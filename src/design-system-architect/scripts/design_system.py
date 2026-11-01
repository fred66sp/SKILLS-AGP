#!/usr/bin/env python3
"""Herramienta determinista del paquete design-system-architect.

Uso:
    python3 design_system.py discover <raíz> [--json]
    python3 design_system.py check <contrato> [--catalog <directorio>] [--json]
    python3 design_system.py gate <contrato> --baseline <anterior> [--approvals <archivo>] [--json]
    python3 design_system.py catalog <contrato> --out <directorio> [--json]

Códigos de salida:
    0  PASS: todas las comprobaciones ejecutadas han pasado
    1  FAIL: hay al menos un incumplimiento demostrado
    2  UNKNOWN: no se pudo ejecutar una comprobación necesaria
    3  error de uso o de entrada/salida

El contrato es un esquema propio (design-system.v1). Los tokens siguen un
subconjunto declarado de DTCG 2025.10: $value, $type, grupos, herencia de tipo,
alias con {ruta}, $root y $deprecated. No implementa $extends, JSON Pointer,
tipos compuestos con validación profunda ni todas las reglas de la especificación.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable

SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSETS = SKILL_ROOT / "assets"

SCHEMA = "design-system.v1"
CATALOG_SCHEMA = "design-system.catalog.v1"
ADAPTER_SCHEMA = "design-system.adapter.v1"
APPROVAL_SCHEMA = "design-system.approvals.v1"

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"
EXIT_PASS, EXIT_FAIL, EXIT_UNKNOWN, EXIT_USAGE = 0, 1, 2, 3

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
TOKEN_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
MODE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REF_RE = re.compile(r"\{([^{}\s]+)\}")
EXACT_REF_RE = re.compile(r"^\{([^{}\s]+)\}$")
DIMENSION_RE = re.compile(
    r"^-?\d+(?:\.\d+)?(?:px|rem|em|%|vw|vh|vmin|vmax|ch|ex|mm|cm|in|pt|pc)$"
)
DURATION_RE = re.compile(r"^-?\d+(?:\.\d+)?(?:ms|s)$")
CSS_VAR_RE = re.compile(r"--([A-Za-z0-9_-]+)\s*:\s*([^;{}]+);")

TOKEN_TYPES = {
    "color",
    "dimension",
    "fontFamily",
    "fontWeight",
    "duration",
    "cubicBezier",
    "number",
    "string",
    "shadow",
    "border",
    "typography",
    "gradient",
    "transition",
    "strokeStyle",
}
COMPOSITE_TYPES = {"shadow", "border", "typography", "gradient", "transition", "strokeStyle"}
PROPERTY_TYPES = {
    "backgroundColor": "color",
    "background": "color",
    "textColor": "color",
    "foreground": "color",
    "borderColor": "color",
    "rounded": "dimension",
    "radius": "dimension",
    "padding": "dimension",
    "size": "dimension",
    "height": "dimension",
    "width": "dimension",
    "borderWidth": "dimension",
    "gap": "dimension",
    "typography": "typography",
    "shadow": "shadow",
    "opacity": "number",
}
DIMENSION_UNITS = {"px", "rem", "em", "%", "vw", "vh", "vmin", "vmax", "ch", "ex", "mm", "cm", "in", "pt", "pc"}
DURATION_UNITS = {"ms", "s"}
COLOR_SPACES = {
    "srgb",
    "display-p3",
    "a98-rgb",
    "prophoto-rgb",
    "rec2020",
    "xyz-d50",
    "xyz-d65",
    "lab",
    "lch",
    "oklab",
    "oklch",
}
STATUSES = {"bootstrap", "refine", "locked"}
SOURCE_KINDS = {"observed", "documented", "inferred", "unknown"}
ALLOWED_TOP_LEVEL = {
    "$schema",
    "schema",
    "name",
    "version",
    "status",
    "identity",
    "tokenSources",
    "tokens",
    "themes",
    "components",
    "patterns",
    "accessibility",
    "governance",
    "constraints",
    "decisions",
    "catalog",
    "implementation",
    "adapters",
    "sources",
    "omitted",
    "provenance",
}
SKIP_DIRS = {
    ".git",
    ".opencode",
    ".pi",
    ".codegraph",
    ".atl",
    ".engram",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    "vendor",
    "archify",
}
DISCOVERY_CSS_LIMIT = 200
DISCOVERY_COMPONENT_LIMIT = 120
DISCOVERY_JSON_LIMIT = 800
DISCOVERY_TOKEN_SAMPLE = 12
DUPLICATE_LIMIT = 25
CLASS_ATTR_RE = re.compile(r"class\s*=\s*[\"']([^\"']*)[\"']", re.IGNORECASE)
CLASS_SELECTOR_RE = re.compile(r"\.(-?[A-Za-z_][A-Za-z0-9_-]*)")
REFERENCE_RE = re.compile(
    r"""(?:href|src)\s*=\s*["']([^"']+)["']|@import\s+(?:url\(\s*)?["']([^"']+)["']""",
    re.IGNORECASE,
)
BRAND_PACK_KEYS = {
    "brand",
    "color",
    "colors",
    "colour",
    "colours",
    "palette",
    "radius",
    "rounded",
    "shadow",
    "shadows",
    "spacing",
    "typography",
}
CATALOG_MODES = {"generated", "external"}
GOVERNANCE_MODES = {"solo", "approvals"}


class UsageError(Exception):
    """Argumento o entrada que impide ejecutar la herramienta."""


class ContractError(Exception):
    """Contrato ilegible o con una forma que impide continuar."""


class Parser(argparse.ArgumentParser):
    """ArgumentParser con el código de uso propio de la herramienta."""

    def error(self, message: str) -> None:  # noqa: D401 - mensaje de argparse
        self.print_usage(sys.stderr)
        print(f"ERROR: {message}", file=sys.stderr)
        raise SystemExit(EXIT_USAGE)


class Report:
    """Resultado de una ejecución: comprobaciones y avisos."""

    def __init__(self) -> None:
        self.checks: list[dict[str, str]] = []
        self.warnings: list[str] = []

    def add(self, check_id: str, status: str, detail: str = "") -> None:
        self.checks.append({"id": check_id, "status": status, "detail": detail})

    def result(self) -> str:
        statuses = {check["status"] for check in self.checks}
        if FAIL in statuses:
            return FAIL
        if UNKNOWN in statuses:
            return UNKNOWN
        return PASS


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def read_asset(name: str) -> str:
    path = ASSETS / name
    if not path.is_file():
        raise UsageError(f"falta el recurso del paquete: {path}")
    return read_text(path)


def load_json(path: Path) -> Any:
    if not path.is_file():
        raise UsageError(f"no existe el archivo: {path}")
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ContractError(f"{path}: JSON inválido ({exc})") from exc
    except OSError as exc:
        raise UsageError(f"no se puede leer {path}: {exc}") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def relpath(path: Path, base: Path) -> str:
    return os.path.relpath(path, base).replace(os.sep, "/")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def dedupe(items: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(items))


def iter_refs(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        for match in REF_RE.finditer(value):
            yield match.group(1)
    elif isinstance(value, dict):
        for child in value.values():
            yield from iter_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_refs(child)


def exact_ref(value: Any) -> str | None:
    if isinstance(value, str):
        match = EXACT_REF_RE.match(value.strip())
        if match:
            return match.group(1)
    return None


def css_name(path: str) -> str:
    return "--ds-" + path.replace("$", "").replace(".", "-")


def kebab(value: str) -> str:
    value = re.sub(r"(?<!^)(?=[A-Z])", "-", value)
    return re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-").lower()


def matches(pattern: str, path: str) -> bool:
    if pattern.endswith(".*"):
        return path.startswith(pattern[:-2] + ".")
    return path == pattern or path.startswith(pattern + ".")


def flatten(value: Any, prefix: str = "") -> dict[str, str]:
    result: dict[str, str] = {}
    if isinstance(value, dict):
        if not value:
            result[prefix] = canonical(value)
            return result
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(child, dict):
                result.update(flatten(child, path))
            else:
                result[path] = canonical(child)
    else:
        result[prefix] = canonical(value)
    return result


# ---------------------------------------------------------------------------
# Tokens: lectura, estructura y tipos
# ---------------------------------------------------------------------------


def collect_tokens(
    document: dict[str, Any],
    errors: list[str],
    source: str,
    prefix: str = "",
    inherited_type: str | None = None,
    depth: int = 0,
    inherited_deprecated: Any = False,
) -> dict[str, dict[str, Any]]:
    if depth > 20:
        errors.append(f"{source}: anidamiento de grupos mayor que 20 en '{prefix or 'raíz'}'")
        return {}
    if not isinstance(document, dict):
        errors.append(f"{source}: el documento de tokens no es un objeto")
        return {}

    tokens: dict[str, dict[str, Any]] = {}
    document_deprecated = document.get("$deprecated", inherited_deprecated)
    for key, value in document.items():
        if key == "$root":
            path = f"{prefix}.$root" if prefix else "$root"
            if not isinstance(value, dict) or "$value" not in value:
                errors.append(f"{source}: '$root' en '{prefix or 'raíz'}' no es un token")
                continue
            register_token(tokens, errors, source, path, value, inherited_type, document_deprecated)
            continue
        if key.startswith("$"):
            if key in {"$type", "$description", "$extensions", "$deprecated"}:
                continue
            errors.append(f"{source}: clave reservada no soportada '{key}' en '{prefix or 'raíz'}'")
            continue
        if not TOKEN_NAME_RE.match(key):
            errors.append(f"{source}: nombre inválido '{key}' en '{prefix or 'raíz'}'")
            continue
        path = f"{prefix}.{key}" if prefix else key
        if not isinstance(value, dict):
            errors.append(f"{source}: '{path}' no es un token ni un grupo")
            continue
        if "$extends" in value:
            errors.append(f"{source}: '{path}' usa $extends, no soportado por este validador")
            continue
        if "$ref" in value:
            errors.append(f"{source}: '{path}' usa $ref (JSON Pointer), no soportado; usa {{ruta}}")
            continue
        if "$value" in value:
            extra = [k for k in value if k not in {"$value", "$type", "$description", "$extensions", "$deprecated"}]
            if extra:
                errors.append(f"{source}: '{path}' mezcla $value con hijos: {', '.join(sorted(extra))}")
            register_token(tokens, errors, source, path, value, inherited_type, document_deprecated)
            continue
        group_type = value.get("$type", inherited_type)
        if group_type is not None and not isinstance(group_type, str):
            errors.append(f"{source}: '$type' de '{path}' no es una cadena")
            group_type = None
        group_deprecated = value.get("$deprecated", document_deprecated)
        tokens.update(
            collect_tokens(
                value,
                errors,
                source,
                path,
                group_type,
                depth + 1,
                group_deprecated,
            )
        )
    return tokens


def register_token(
    tokens: dict[str, dict[str, Any]],
    errors: list[str],
    source: str,
    path: str,
    node: dict[str, Any],
    inherited_type: str | None,
    inherited_deprecated: Any = False,
) -> None:
    token_type = node.get("$type", inherited_type)
    if token_type is not None and not isinstance(token_type, str):
        errors.append(f"{source}: '$type' de '{path}' no es una cadena")
        token_type = None
    tokens[path] = {
        "path": path,
        "value": node.get("$value"),
        "type": token_type,
        "node": node,
        "source": source,
        "deprecated": node.get("$deprecated", inherited_deprecated),
    }


def validate_token_type(token: dict[str, Any]) -> str | None:
    token_type = token["type"]
    value = token["value"]
    path = token["path"]

    if token_type is None:
        return f"token '{path}': tipo indeterminable; declara $type en el token o en su grupo"
    if token_type not in TOKEN_TYPES:
        return f"token '{path}': $type '{token_type}' no reconocido"
    if value is None:
        return f"token '{path}': $value nulo"
    if isinstance(value, str) and REF_RE.search(value):
        return None

    if token_type == "color":
        if isinstance(value, str):
            if not value.strip():
                return f"token '{path}': color vacío"
            return None
        if not isinstance(value, dict):
            return f"token '{path}': color debe ser un objeto DTCG o una cadena CSS"
        if "colorSpace" in value:
            space = value.get("colorSpace")
            if not isinstance(space, str) or space not in COLOR_SPACES:
                return f"token '{path}': colorSpace no reconocido"
            components = value.get("components")
            if not isinstance(components, list) or not 3 <= len(components) <= 4:
                return f"token '{path}': components debe tener 3 o 4 números"
            if not all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in components):
                return f"token '{path}': components debe contener números"
        elif "hex" not in value:
            return f"token '{path}': color sin colorSpace/components ni hex"
        if "hex" in value:
            if not isinstance(value["hex"], str) or not re.match(r"^#[0-9A-Fa-f]{3,8}$", value["hex"]):
                return f"token '{path}': hex inválido"
        return None

    if token_type == "dimension":
        if isinstance(value, str):
            return None if DIMENSION_RE.match(value) else f"token '{path}': dimensión inválida"
        if not isinstance(value, dict):
            return f"token '{path}': dimensión debe ser un objeto o una cadena con unidad"
        if not isinstance(value.get("value"), (int, float)) or isinstance(value.get("value"), bool):
            return f"token '{path}': dimensión sin valor numérico"
        if value.get("unit") not in DIMENSION_UNITS:
            return f"token '{path}': unidad de dimensión no reconocida"
        return None

    if token_type == "duration":
        if isinstance(value, str):
            return None if DURATION_RE.match(value) else f"token '{path}': duración inválida"
        if not isinstance(value, dict):
            return f"token '{path}': duración debe ser un objeto o una cadena con unidad"
        if not isinstance(value.get("value"), (int, float)) or isinstance(value.get("value"), bool):
            return f"token '{path}': duración sin valor numérico"
        if value.get("unit") not in DURATION_UNITS:
            return f"token '{path}': unidad de duración no reconocida"
        return None

    if token_type == "fontFamily":
        if isinstance(value, str):
            return None
        if isinstance(value, list) and value and all(isinstance(item, str) for item in value):
            return None
        return f"token '{path}': fontFamily debe ser una cadena o una lista de cadenas"

    if token_type == "fontWeight":
        if isinstance(value, (int, float)) and not isinstance(value, bool) and 1 <= value <= 1000:
            return None
        if isinstance(value, str) and value in {"normal", "bold", "bolder", "lighter", "100", "200", "300", "400", "500", "600", "700", "800", "900"}:
            return None
        return f"token '{path}': fontWeight inválido"

    if token_type == "number":
        return None if isinstance(value, (int, float)) and not isinstance(value, bool) else f"token '{path}': number inválido"

    if token_type == "cubicBezier":
        if isinstance(value, list) and len(value) == 4 and all(
            isinstance(item, (int, float)) and not isinstance(item, bool) for item in value
        ):
            return None
        return f"token '{path}': cubicBezier debe tener cuatro números"

    if token_type == "string":
        return None if isinstance(value, str) else f"token '{path}': string inválido"

    if token_type in COMPOSITE_TYPES:
        if isinstance(value, (dict, list, str)):
            return None
        return f"token '{path}': {token_type} debe ser un objeto, lista o cadena"

    return f"token '{path}': tipo '{token_type}' sin validador"


def load_tokens(
    contract: dict[str, Any], contract_path: Path
) -> tuple[dict[str, dict[str, Any]], list[tuple[str, Path]], list[str]]:
    errors: list[str] = []
    tokens: dict[str, dict[str, Any]] = {}
    inputs: list[tuple[str, Path]] = [("contract", contract_path.resolve())]

    sources = contract.get("tokenSources", [])
    if sources is not None and not isinstance(sources, list):
        errors.append("tokenSources debe ser una lista de rutas")
        sources = []
    for raw in sources or []:
        if not isinstance(raw, str) or not raw.strip():
            errors.append("tokenSources contiene una ruta vacía o inválida")
            continue
        if Path(raw).is_absolute():
            errors.append(f"tokenSources debe ser relativo al contrato: {raw}")
            continue
        source_path = (contract_path.parent / raw).resolve()
        if not source_path.is_file():
            errors.append(f"fuente de tokens no encontrada: {raw}")
            continue
        inputs.append(("token-source", source_path))
        try:
            document = json.loads(read_text(source_path))
        except json.JSONDecodeError as exc:
            errors.append(f"fuente de tokens ilegible {raw}: {exc}")
            continue
        found = collect_tokens(document, errors, raw)
        for path, token in found.items():
            if path in tokens:
                errors.append(f"token duplicado '{path}' en {raw}")
            else:
                tokens[path] = token

    inline = contract.get("tokens")
    if inline is not None:
        if not isinstance(inline, dict):
            errors.append("tokens debe ser un objeto")
        else:
            found = collect_tokens(inline, errors, "tokens")
            for path, token in found.items():
                if path in tokens:
                    errors.append(f"token duplicado '{path}' entre tokens y tokenSources")
                else:
                    tokens[path] = token

    if not tokens and not errors:
        errors.append("el contrato no declara tokens ni tokenSources")

    for path in list(tokens):
        infer_token_type(path, tokens)

    return tokens, inputs, errors


def check_token_references(tokens: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []

    for path, token in tokens.items():
        for ref in iter_refs(token["value"]):
            if ref not in tokens:
                errors.append(f"token '{path}': referencia inexistente '{{{ref}}}'")
            elif tokens[ref]["deprecated"]:
                errors.append(f"token '{path}': referencia al token obsoleto '{{{ref}}}'")

    for path, token in tokens.items():
        target = exact_ref(token["value"])
        if not target:
            continue
        seen: list[str] = []
        current = path
        while True:
            if current in seen:
                cycle = " -> ".join(seen + [current])
                errors.append(f"token '{path}': ciclo de referencias: {cycle}")
                break
            seen.append(current)
            if len(seen) > 10:
                errors.append(f"token '{path}': cadena de referencias mayor que 10")
                break
            current_token = tokens.get(current)
            if current_token is None:
                break
            next_ref = exact_ref(current_token["value"])
            if not next_ref:
                break
            current = next_ref
        final_token = tokens.get(current)
        if (
            final_token is not None
            and token["type"]
            and final_token["type"]
            and token["type"] != final_token["type"]
        ):
            errors.append(
                f"token '{path}': tipo '{token['type']}' no coincide con "
                f"'{final_token['type']}' de '{{{current}}}'"
            )

    return dedupe(errors)


def resolved_type(path: str, tokens: dict[str, dict[str, Any]]) -> str | None:
    seen: set[str] = set()
    while path in tokens and path not in seen:
        seen.add(path)
        token = tokens[path]
        target = exact_ref(token["value"])
        if not target:
            return token["type"]
        path = target
    return tokens.get(path, {}).get("type") if path in tokens else None


def infer_token_type(
    path: str, tokens: dict[str, dict[str, Any]], stack: tuple[str, ...] = ()
) -> str | None:
    token = tokens.get(path)
    if token is None:
        return None
    if token["type"] is not None:
        return token["type"]
    if path in stack:
        return None
    target = exact_ref(token["value"])
    if not target:
        return None
    inferred = infer_token_type(target, tokens, stack + (path,))
    if inferred is not None:
        token["type"] = inferred
    return inferred


def check_value_refs(value: Any, context: str, tokens: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    for ref in iter_refs(value):
        if ref not in tokens:
            errors.append(f"{context}: referencia inexistente '{{{ref}}}'")
        elif tokens[ref]["deprecated"]:
            errors.append(f"{context}: referencia al token obsoleto '{{{ref}}}'")
    return errors


# ---------------------------------------------------------------------------
# Estructura del contrato
# ---------------------------------------------------------------------------


def check_structure(contract: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in sorted(set(contract) - ALLOWED_TOP_LEVEL):
        warnings.append(f"clave superior desconocida: {key}")

    if contract.get("schema") != SCHEMA:
        errors.append(f"schema debe ser '{SCHEMA}'")
    if not isinstance(contract.get("name"), str) or not contract["name"].strip():
        errors.append("name debe ser una cadena no vacía")
    if not isinstance(contract.get("version"), str) or not SEMVER_RE.match(contract["version"]):
        errors.append("version debe ser SemVer MAJOR.MINOR.PATCH")
    if "status" in contract and contract["status"] not in STATUSES:
        errors.append("status debe ser bootstrap, refine o locked")

    identity = contract.get("identity")
    if not isinstance(identity, dict):
        errors.append("identity debe ser un objeto")
    else:
        principles = identity.get("principles")
        if not isinstance(principles, list) or not principles or not all(
            isinstance(item, str) and item.strip() for item in principles
        ):
            errors.append("identity.principles debe ser una lista no vacía de cadenas")
        if "purpose" in identity and not isinstance(identity["purpose"], str):
            errors.append("identity.purpose debe ser una cadena")

    governance = contract.get("governance")
    if not isinstance(governance, dict):
        errors.append("governance debe ser un objeto")
    else:
        mode = governance.get("mode", "solo")
        if mode not in GOVERNANCE_MODES:
            errors.append("governance.mode debe ser solo o approvals")
        for field in ("protected", "configurable"):
            value = governance.get(field, [])
            if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
                errors.append(f"governance.{field} debe ser una lista de rutas")
        exceptions = governance.get("exceptions", [])
        if not isinstance(exceptions, list):
            errors.append("governance.exceptions debe ser una lista")
        else:
            for index, exception in enumerate(exceptions):
                if not isinstance(exception, dict):
                    errors.append(f"governance.exceptions[{index}] debe ser un objeto")
                    continue
                for field in ("path", "reason"):
                    if not isinstance(exception.get(field), str) or not exception[field].strip():
                        errors.append(f"governance.exceptions[{index}].{field} debe ser una cadena no vacía")
                if not (exception.get("approved_by") or exception.get("approval")):
                    errors.append(
                        f"governance.exceptions[{index}] debe declarar approved_by o approval"
                    )

    if "tokens" not in contract and "tokenSources" not in contract:
        errors.append("el contrato debe declarar tokens o tokenSources")
    if "tokens" in contract and not isinstance(contract["tokens"], dict):
        errors.append("tokens debe ser un objeto")
    if "tokenSources" in contract and not isinstance(contract["tokenSources"], list):
        errors.append("tokenSources debe ser una lista")

    themes = contract.get("themes")
    if themes is not None:
        if not isinstance(themes, dict):
            errors.append("themes debe ser un objeto")
        else:
            default = themes.get("default")
            if default is not None and (not isinstance(default, str) or not MODE_NAME_RE.match(default)):
                errors.append("themes.default debe ser un identificador de modo")
            modes = themes.get("modes")
            if modes is not None:
                if not isinstance(modes, dict):
                    errors.append("themes.modes debe ser un objeto")
                else:
                    for mode, overrides in modes.items():
                        if not isinstance(mode, str) or not MODE_NAME_RE.match(mode):
                            errors.append(f"themes.modes: modo inválido '{mode}'")
                        if not isinstance(overrides, dict):
                            errors.append(f"themes.modes.{mode} debe ser un objeto")

    components = contract.get("components")
    if components is not None and not isinstance(components, dict):
        errors.append("components debe ser un objeto")
    patterns = contract.get("patterns")
    if patterns is not None and not isinstance(patterns, dict):
        errors.append("patterns debe ser un objeto")

    accessibility = contract.get("accessibility")
    if accessibility is not None and not isinstance(accessibility, dict):
        errors.append("accessibility debe ser un objeto")

    constraints = contract.get("constraints")
    if constraints is not None:
        if not isinstance(constraints, dict):
            errors.append("constraints debe ser un objeto")
        else:
            for field in ("always", "never"):
                value = constraints.get(field, [])
                if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                    errors.append(f"constraints.{field} debe ser una lista de cadenas")

    decisions = contract.get("decisions")
    if decisions is not None and not isinstance(decisions, list):
        errors.append("decisions debe ser una lista")

    catalog = contract.get("catalog")
    if catalog is not None:
        if isinstance(catalog, str):
            if not catalog.strip():
                errors.append("catalog no puede ser una ruta vacía")
        elif isinstance(catalog, dict):
            if not isinstance(catalog.get("path"), str) or not catalog["path"].strip():
                errors.append("catalog.path debe ser una ruta no vacía")
            mode = catalog.get("mode", "generated")
            if mode not in CATALOG_MODES:
                errors.append("catalog.mode debe ser generated o external")
            elif mode == "external":
                sources = catalog.get("sources")
                if not isinstance(sources, list) or not all(
                    isinstance(item, str) and item.strip() for item in sources
                ) or not sources:
                    errors.append("un catálogo external debe declarar catalog.sources con la implementación que consume")
                if "entry" in catalog and (
                    not isinstance(catalog["entry"], str) or not catalog["entry"].strip()
                ):
                    errors.append("catalog.entry debe ser una ruta no vacía")
                fingerprint = catalog.get("fingerprint")
                if fingerprint is not None and (
                    not isinstance(fingerprint, dict)
                    or not all(isinstance(value, str) for value in fingerprint.values())
                ):
                    errors.append("catalog.fingerprint debe ser un objeto ruta → sha256")
        else:
            errors.append("catalog debe ser una ruta o un objeto con path")

    implementation = contract.get("implementation")
    if implementation is not None:
        if not isinstance(implementation, dict):
            errors.append("implementation debe ser un objeto")
        else:
            styles = implementation.get("styles")
            if not isinstance(styles, list) or not all(
                isinstance(item, str) and item.strip() for item in styles
            ) or not styles:
                errors.append("implementation.styles debe ser una lista no vacía de rutas CSS")

    adapters = contract.get("adapters")
    if adapters is not None:
        if not isinstance(adapters, list):
            errors.append("adapters debe ser una lista")
        else:
            for index, adapter in enumerate(adapters):
                if not isinstance(adapter, dict):
                    errors.append(f"adapters[{index}] debe ser un objeto")
                    continue
                for field in ("name", "report"):
                    if not isinstance(adapter.get(field), str) or not adapter[field].strip():
                        errors.append(f"adapters[{index}].{field} debe ser una cadena no vacía")

    sources = contract.get("sources")
    if sources is not None:
        if not isinstance(sources, list):
            errors.append("sources debe ser una lista")
        else:
            for index, source in enumerate(sources):
                if not isinstance(source, dict):
                    errors.append(f"sources[{index}] debe ser un objeto")
                    continue
                if not isinstance(source.get("path"), str) or not source["path"].strip():
                    errors.append(f"sources[{index}].path debe ser una cadena no vacía")
                if source.get("kind") not in SOURCE_KINDS:
                    errors.append(f"sources[{index}].kind debe ser observed, documented, inferred o unknown")

    omitted = contract.get("omitted")
    if omitted is not None and not isinstance(omitted, list):
        errors.append("omitted debe ser una lista")

    return errors, warnings


def check_components(contract: dict[str, Any], tokens: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    components = contract.get("components")
    if components is None:
        return errors
    if not isinstance(components, dict):
        return ["components debe ser un objeto"]

    for name, component in components.items():
        context = f"components.{name}"
        if not isinstance(component, dict):
            errors.append(f"{context} debe ser un objeto")
            continue
        variants = component.get("variants")
        if variants is not None and not isinstance(variants, dict):
            errors.append(f"{context}.variants debe ser un objeto")
            variants = None
        if variants:
            when = component.get("when")
            when_not = component.get("when_not")
            has_rule = (isinstance(when, list) and bool(when)) or (
                isinstance(when_not, list) and bool(when_not)
            )
            if not has_rule:
                errors.append(f"{context}: con variantes debe declarar when o when_not")
            for variant_name, bag in variants.items():
                if not isinstance(bag, dict):
                    errors.append(f"{context}.variants.{variant_name} debe ser un objeto")
                    continue
                errors.extend(
                    check_value_refs(bag, f"{context}.variants.{variant_name}", tokens)
                )
                for property_name, value in bag.items():
                    expected = PROPERTY_TYPES.get(property_name)
                    target = exact_ref(value)
                    if not expected or not target:
                        continue
                    actual = resolved_type(target, tokens)
                    if actual is not None and actual != expected:
                        errors.append(
                            f"{context}.variants.{variant_name}.{property_name}: "
                            f"esperaba {expected}, referencia a {actual} '{{{target}}}'"
                        )
        for field in ("when", "when_not", "states"):
            value = component.get(field)
            if value is not None and (
                not isinstance(value, list) or not all(isinstance(item, str) for item in value)
            ):
                errors.append(f"{context}.{field} debe ser una lista de cadenas")
        if "example" in component and not isinstance(component["example"], str):
            errors.append(f"{context}.example debe ser una cadena HTML")
        if "description" in component and not isinstance(component["description"], str):
            errors.append(f"{context}.description debe ser una cadena")

    return dedupe(errors)


def check_themes(contract: dict[str, Any], tokens: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    themes = contract.get("themes")
    if not isinstance(themes, dict):
        return errors
    modes = themes.get("modes")
    if not isinstance(modes, dict):
        return errors
    for mode, overrides in modes.items():
        if not isinstance(overrides, dict):
            continue
        for path, value in overrides.items():
            if path not in tokens:
                errors.append(f"themes.modes.{mode}: token inexistente '{path}'")
                continue
            token = tokens[path]
            target = exact_ref(value)
            if target:
                actual = resolved_type(target, tokens)
                if actual is not None and token["type"] is not None and actual != token["type"]:
                    errors.append(
                        f"themes.modes.{mode}.{path}: esperaba {token['type']}, "
                        f"referencia a {actual} '{{{target}}}'"
                    )
            else:
                error = validate_token_type(
                    {
                        "path": f"themes.modes.{mode}.{path}",
                        "type": token["type"],
                        "value": value,
                    }
                )
                if error:
                    errors.append(error.replace("token '", "override '"))
            errors.extend(check_value_refs(value, f"themes.modes.{mode}.{path}", tokens))
    return dedupe(errors)


# ---------------------------------------------------------------------------
# Puerta de cambios protegidos y aprobaciones externas
# ---------------------------------------------------------------------------


def load_approvals(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    try:
        data = json.loads(read_text(path))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"no se puede leer el archivo de aprobaciones: {exc}"]
    if not isinstance(data, dict) or data.get("schema") != APPROVAL_SCHEMA:
        return [], [f"el archivo de aprobaciones no declara schema '{APPROVAL_SCHEMA}'"]
    approvals = data.get("approvals")
    if not isinstance(approvals, list) or not approvals:
        return [], ["el archivo de aprobaciones no contiene entradas"]

    valid: list[dict[str, Any]] = []
    for index, approval in enumerate(approvals):
        if not isinstance(approval, dict):
            errors.append(f"approvals[{index}] no es un objeto")
            continue
        missing = [
            field
            for field in ("id", "path", "approved_by", "approved_at", "source", "reason")
            if not isinstance(approval.get(field), str) or not approval[field].strip()
        ]
        if missing:
            errors.append(f"approvals[{index}] carece de {', '.join(missing)}")
            continue
        if not DATE_RE.match(approval["approved_at"]):
            errors.append(f"approvals[{index}].approved_at no es una fecha AAAA-MM-DD")
            continue
        valid.append(approval)
    if errors:
        return [], errors
    return valid, []


def check_protected_changes(
    contract: dict[str, Any],
    baseline: dict[str, Any],
    approvals_path: Path | None,
) -> tuple[str, str]:
    governance = contract.get("governance")
    protected = governance.get("protected", []) if isinstance(governance, dict) else []
    mode = governance.get("mode", "solo") if isinstance(governance, dict) else "solo"
    if not isinstance(protected, list) or not protected:
        return UNKNOWN, "el contrato no declara rutas protegidas; no hay nada que comparar"
    protected = [pattern for pattern in protected if isinstance(pattern, str) and pattern]
    if not protected:
        return UNKNOWN, "el contrato no declara rutas protegidas válidas"

    old = flatten(baseline)
    new = flatten(contract)
    changed: list[tuple[str, str | None, str | None]] = []
    unmatched: list[str] = []
    for pattern in protected:
        matched = False
        for path in sorted(set(old) | set(new)):
            if matches(pattern, path):
                matched = True
                if old.get(path) != new.get(path):
                    changed.append((path, old.get(path), new.get(path)))
        if not matched:
            unmatched.append(pattern)

    suffix = ""
    if unmatched:
        suffix = "; rutas protegidas sin coincidencias: " + ", ".join(unmatched)

    if not changed:
        return PASS, "ninguna ruta protegida ha cambiado" + suffix

    if approvals_path is None:
        if mode != "approvals":
            return UNKNOWN, (
                "governance.mode es solo: la revisión es el commit y la confirmación de la persona; "
                "el validador no puede comprobarla. Rutas cambiadas: "
                + ", ".join(path for path, _, _ in changed)
                + suffix
            )
        return FAIL, "cambios protegidos sin archivo de aprobaciones: " + ", ".join(
            path for path, _, _ in changed
        ) + suffix

    approvals, approval_errors = load_approvals(approvals_path)
    if approval_errors:
        return UNKNOWN, "no se puede comprobar la aprobación: " + "; ".join(approval_errors) + suffix

    unapproved: list[str] = []
    for path, _, _ in changed:
        if not any(matches(approval["path"], path) for approval in approvals):
            unapproved.append(path)
    if unapproved:
        return FAIL, "cambios protegidos sin aprobación externa: " + ", ".join(unapproved) + suffix

    used = [
        approval["id"]
        for approval in approvals
        if any(matches(approval["path"], path) for path, _, _ in changed)
    ]
    return PASS, "cambios protegidos cubiertos por: " + ", ".join(used) + suffix


# ---------------------------------------------------------------------------
# Consistencia del catálogo y conformidad de componentes
# ---------------------------------------------------------------------------


def catalog_target(contract: dict[str, Any], contract_path: Path, override: str | None) -> Path | None:
    if override:
        target = Path(override)
    else:
        catalog = contract.get("catalog")
        if isinstance(catalog, str):
            target = Path(catalog)
        elif isinstance(catalog, dict) and isinstance(catalog.get("path"), str):
            target = Path(catalog["path"])
        else:
            return None
    if not target.is_absolute():
        target = contract_path.parent / target
    return target


def catalog_mode(contract: dict[str, Any]) -> str:
    catalog = contract.get("catalog")
    if isinstance(catalog, dict) and isinstance(catalog.get("mode"), str):
        return catalog["mode"]
    return "generated"


def implementation_styles(contract: dict[str, Any]) -> list[str]:
    implementation = contract.get("implementation")
    if isinstance(implementation, dict):
        styles = implementation.get("styles")
        if isinstance(styles, list):
            return [item for item in styles if isinstance(item, str) and item.strip()]
    if catalog_mode(contract) == "external":
        catalog = contract.get("catalog")
        sources = catalog.get("sources") if isinstance(catalog, dict) else None
        if isinstance(sources, list):
            return [item for item in sources if isinstance(item, str) and item.strip()]
    return []


def check_catalog(
    contract: dict[str, Any],
    contract_path: Path,
    token_inputs: list[tuple[str, Path]],
    override: str | None,
) -> tuple[str, str] | None:
    catalog_dir = catalog_target(contract, contract_path, override)
    if catalog_dir is None:
        return None
    if catalog_mode(contract) == "external":
        return check_external_catalog(contract, contract_path, catalog_dir)

    manifest_path = catalog_dir / "catalog.json"
    if not manifest_path.is_file():
        return UNKNOWN, f"catálogo declarado pero no generado: {manifest_path}"

    try:
        manifest = json.loads(read_text(manifest_path))
    except (OSError, json.JSONDecodeError) as exc:
        return UNKNOWN, f"manifiesto del catálogo ilegible: {exc}"
    if not isinstance(manifest, dict) or manifest.get("schema") != CATALOG_SCHEMA:
        return FAIL, f"manifiesto del catálogo con schema distinto de '{CATALOG_SCHEMA}'"

    current_inputs = [(kind, sha256_file(path)) for kind, path in token_inputs]
    current_inputs.extend(
        ("skill-template", sha256_file(ASSETS / name))
        for name in ("catalog.html", "catalog.css")
    )
    current_inputs = sorted(current_inputs)
    recorded_inputs = []
    for item in manifest.get("inputs", []):
        if not isinstance(item, dict):
            return FAIL, "manifiesto del catálogo con entradas inválidas"
        kind = item.get("kind")
        digest = item.get("sha256")
        if not isinstance(kind, str) or not isinstance(digest, str):
            return FAIL, "manifiesto del catálogo con entradas inválidas"
        recorded_inputs.append((kind, digest))
    if current_inputs != sorted(recorded_inputs):
        return FAIL, "el catálogo no coincide con las entradas efectivas actuales"

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        return FAIL, "el manifiesto del catálogo no declara artefactos"
    for artifact in artifacts:
        if not isinstance(artifact, dict) or not isinstance(artifact.get("path"), str):
            return FAIL, "el manifiesto del catálogo contiene un artefacto inválido"
        path = catalog_dir / artifact["path"]
        if not path.is_file():
            return FAIL, f"falta el artefacto '{artifact['path']}'"
        if sha256_file(path) != artifact.get("sha256"):
            return FAIL, f"el artefacto '{artifact['path']}' no coincide con el manifiesto"
    return PASS, f"catálogo sincronizado con {len(current_inputs)} entrada(s)"


def check_external_catalog(
    contract: dict[str, Any], contract_path: Path, catalog_dir: Path
) -> tuple[str, str]:
    if not catalog_dir.is_dir():
        return FAIL, f"catálogo externo declarado pero ausente: {catalog_dir}"
    catalog = contract.get("catalog")
    entry = "index.html"
    if isinstance(catalog, dict) and isinstance(catalog.get("entry"), str):
        entry = catalog["entry"]
    entry_path = catalog_dir / entry
    if not entry_path.is_file():
        return FAIL, f"falta la entrada del catálogo externo: {entry_path}"

    sources = implementation_styles(contract)
    missing = [rel for rel in sources if not (contract_path.parent / rel).is_file()]
    if missing:
        return FAIL, "fuentes de implementación ausentes: " + ", ".join(missing)

    fingerprint = catalog.get("fingerprint") if isinstance(catalog, dict) else None
    if isinstance(fingerprint, dict):
        for rel, digest in fingerprint.items():
            path = contract_path.parent / rel
            if not path.is_file():
                return FAIL, f"falta el archivo con huella declarada: {rel}"
            if sha256_file(path) != digest:
                return FAIL, f"la huella de '{rel}' no coincide con la declarada"
    return PASS, f"catálogo externo verificado: {entry} y {len(sources)} fuente(s) de implementación"


def css_classes(text: str) -> set[str]:
    return {match.group(1) for match in CLASS_SELECTOR_RE.finditer(text)}


def referenced_paths(text: str) -> set[str]:
    found = set()
    for match in REFERENCE_RE.finditer(text):
        value = (match.group(1) or match.group(2) or "").strip()
        if value:
            found.add(value)
    return found


def example_classes(contract: dict[str, Any]) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    components = contract.get("components")
    if not isinstance(components, dict):
        return found
    for name, component in components.items():
        if not isinstance(component, dict) or not isinstance(component.get("example"), str):
            continue
        for attribute in CLASS_ATTR_RE.finditer(component["example"]):
            found.extend((name, token) for token in attribute.group(1).split())
    return found


def check_implementation_fidelity(
    contract: dict[str, Any], contract_path: Path
) -> tuple[str, str] | None:
    if contract.get("catalog") is None and contract.get("implementation") is None:
        return None
    styles = implementation_styles(contract)
    if not styles:
        return UNKNOWN, "no hay implementación declarada; la fidelidad del catálogo no se puede comprobar"

    texts: list[str] = []
    for rel in styles:
        path = contract_path.parent / rel
        if not path.is_file():
            return FAIL, f"falta la fuente de implementación '{rel}'"
        texts.append(read_text(path))
    classes = set().union(*(css_classes(text) for text in texts))

    missing = sorted(
        {f"{name}:{token}" for name, token in example_classes(contract) if token not in classes}
    )
    if missing:
        return FAIL, "muestras con clases ausentes del CSS del producto: " + ", ".join(missing[:12])

    catalog_dir = catalog_target(contract, contract_path, None)
    if catalog_mode(contract) == "external" and catalog_dir is not None:
        catalog = contract.get("catalog")
        entry = "index.html"
        if isinstance(catalog, dict) and isinstance(catalog.get("entry"), str):
            entry = catalog["entry"]
        entry_path = catalog_dir / entry
        if entry_path.is_file():
            references = referenced_paths(read_text(entry_path))
            imported = any(
                any(ref.endswith(rel) or ref.endswith(Path(rel).name) for ref in references)
                for rel in styles
            )
            if not imported:
                return FAIL, f"el catálogo externo no importa la implementación declarada: {entry}"
        layer = []
        for path in sorted(catalog_dir.rglob("*.css")):
            if relpath(path, contract_path.parent) in styles:
                continue
            own = sorted(name for name in css_classes(read_text(path)) if name.startswith("ds-"))
            if own:
                layer.append(f"{relpath(path, contract_path.parent)} ({len(own)} clase(s) ds-*)")
        if layer:
            return FAIL, "el catálogo externo declara una capa propia de componentes: " + "; ".join(layer)
    return PASS, f"{len(classes)} clase(s) de implementación; las muestras están acopladas"


def check_adapters(contract: dict[str, Any], contract_path: Path) -> tuple[str, str] | None:
    adapters = contract.get("adapters")
    if adapters is None:
        return None
    if not isinstance(adapters, list) or not adapters:
        return UNKNOWN, "adapters está vacío o no es una lista"
    components = contract.get("components")
    if not isinstance(components, dict) or not components:
        return UNKNOWN, "no hay componentes declarados que comprobar"

    statuses: list[str] = []
    details: list[str] = []
    for index, adapter in enumerate(adapters):
        if not isinstance(adapter, dict) or not isinstance(adapter.get("name"), str) or not isinstance(adapter.get("report"), str):
            statuses.append(UNKNOWN)
            details.append(f"adapters[{index}] inválido")
            continue
        report_path = contract_path.parent / adapter["report"]
        if not report_path.is_file():
            statuses.append(UNKNOWN)
            details.append(f"{adapter['name']}: informe ausente")
            continue
        try:
            report = json.loads(read_text(report_path))
        except (OSError, json.JSONDecodeError) as exc:
            statuses.append(UNKNOWN)
            details.append(f"{adapter['name']}: informe ilegible ({exc})")
            continue
        if not isinstance(report, dict) or report.get("schema") != ADAPTER_SCHEMA:
            statuses.append(UNKNOWN)
            details.append(f"{adapter['name']}: schema distinto de '{ADAPTER_SCHEMA}'")
            continue
        entries = {
            entry["name"]: entry
            for entry in report.get("components", [])
            if isinstance(entry, dict) and isinstance(entry.get("name"), str)
        }
        for name in components:
            entry = entries.get(name)
            if entry is None:
                statuses.append(UNKNOWN)
                details.append(f"{adapter['name']}/{name}: sin resultado")
                continue
            status = str(entry.get("status", "")).upper()
            evidence = entry.get("evidence")
            has_evidence = isinstance(evidence, str) and bool(evidence.strip())
            if status == FAIL:
                statuses.append(FAIL)
                suffix = "" if has_evidence else " (sin evidencia)"
                details.append(f"{adapter['name']}/{name}: FAIL{suffix}")
            elif status == PASS:
                if not has_evidence:
                    statuses.append(UNKNOWN)
                    details.append(f"{adapter['name']}/{name}: PASS sin evidencia")
                else:
                    statuses.append(PASS)
                    details.append(f"{adapter['name']}/{name}: PASS")
            else:
                statuses.append(UNKNOWN)
                details.append(f"{adapter['name']}/{name}: resultado no concluyente")

    if FAIL in statuses:
        return FAIL, "; ".join(details)
    if UNKNOWN in statuses:
        return UNKNOWN, "; ".join(details)
    return PASS, "; ".join(details)


# ---------------------------------------------------------------------------
# Catálogo: valores, HTML y manifiesto
# ---------------------------------------------------------------------------


def resolve_display(path: str, tokens: dict[str, dict[str, Any]], stack: tuple[str, ...] = ()) -> str:
    token = tokens.get(path)
    if token is None:
        return f"{{{path}}}"
    if path in stack:
        return f"ciclo: {path}"
    value = token["value"]
    target = exact_ref(value)
    if target:
        return resolve_display(target, tokens, stack + (path,))
    return display_value(value)


def display_with_refs(value: Any, tokens: dict[str, dict[str, Any]]) -> str:
    if isinstance(value, str):
        target = exact_ref(value)
        if target:
            return f"{{{target}}} → {resolve_display(target, tokens)}"
        return value
    return display_value(value)


def display_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, dict):
        if "hex" in value and isinstance(value["hex"], str):
            return value["hex"]
        if "value" in value and "unit" in value:
            return f"{value['value']}{value['unit']}"
        if "colorSpace" in value and "components" in value:
            components = " ".join(str(item) for item in value["components"])
            alpha = f" / {value['alpha']}" if "alpha" in value else ""
            return f"color({value['colorSpace']} {components}{alpha})"
        if "fontFamily" in value:
            parts = [
                str(value[field])
                for field in ("fontFamily", "fontSize", "fontWeight", "lineHeight")
                if field in value
            ]
            return " · ".join(parts)
    return canonical(value)


def human_value(value: Any) -> str:
    if isinstance(value, bool):
        return "sí" if value else "no"
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, dict):
        return "; ".join(f"{key}: {human_value(child)}" for key, child in value.items())
    if isinstance(value, list):
        return ", ".join(human_value(child) for child in value)
    return str(value)


def css_value(value: Any) -> str | None:
    if isinstance(value, str):
        return replace_refs(value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, list):
        if len(value) == 4 and all(
            isinstance(item, (int, float)) and not isinstance(item, bool) for item in value
        ):
            return "cubic-bezier(" + ", ".join(str(item) for item in value) + ")"
        if value and all(isinstance(item, str) for item in value):
            return ", ".join(value)
        return None
    if isinstance(value, dict):
        if "hex" in value and isinstance(value["hex"], str):
            return value["hex"]
        if "value" in value and "unit" in value:
            return f"{value['value']}{value['unit']}"
        if "colorSpace" in value and "components" in value:
            components = " ".join(str(item) for item in value["components"])
            alpha = f" / {value['alpha']}" if "alpha" in value else ""
            return f"color({value['colorSpace']} {components}{alpha})"
    return None


def replace_refs(value: str) -> str:
    return REF_RE.sub(lambda match: f"var({css_name(match.group(1))})", value)


def emit_token_css(path: str, token: dict[str, Any]) -> list[str]:
    base = css_name(path)
    value = token["value"]
    token_type = token["type"]
    if token_type == "typography" and isinstance(value, dict) and not exact_ref(value):
        lines = []
        for field, field_value in value.items():
            css = css_value(field_value)
            if css is not None:
                lines.append(f"  {base}-{kebab(field)}: {css};")
        return lines
    css = css_value(value)
    if css is None:
        return [f"  /* {path}: valor compuesto sin representación CSS directa */"]
    return [f"  {base}: {css};"]


def build_tokens_css(contract: dict[str, Any], tokens: dict[str, dict[str, Any]]) -> str:
    lines = [
        "/* Generado por design-system-architect. No editar a mano. */",
        ":root {",
    ]
    for path in sorted(tokens):
        lines.extend(emit_token_css(path, tokens[path]))

    themes = contract.get("themes")
    modes = themes.get("modes") if isinstance(themes, dict) else None
    default_mode = themes.get("default") if isinstance(themes, dict) else None
    if isinstance(modes, dict) and default_mode in modes and isinstance(modes[default_mode], dict):
        for path, value in sorted(modes[default_mode].items()):
            css = css_value(value)
            if css is not None:
                lines.append(f"  {css_name(path)}: {css};")
    lines.append("}")

    if isinstance(modes, dict):
        for mode, overrides in sorted(modes.items()):
            if mode == default_mode or not isinstance(overrides, dict) or not overrides:
                continue
            lines.append("")
            lines.append(f'[data-theme="{mode}"] {{')
            for path, value in sorted(overrides.items()):
                css = css_value(value)
                if css is not None:
                    lines.append(f"  {css_name(path)}: {css};")
            lines.append("}")
    lines.append("")
    return "\n".join(lines)


def render_sample(path: str, token: dict[str, Any]) -> str:
    token_type = token["type"]
    variable = css_name(path)
    if token_type == "color":
        return (
            f'<span class="swatch" style="background: var({variable})" '
            f'aria-hidden="true"></span>'
        )
    if token_type == "dimension":
        if any(part in path.lower() for part in ("radius", "rounded", "radio")):
            return f'<span class="radius" style="border-radius: var({variable})" aria-hidden="true"></span>'
        return f'<span class="bar" style="width: var({variable})" aria-hidden="true"></span>'
    if token_type == "typography":
        return (
            f'<span class="type-sample" style="font-family: var({variable}-font-family); '
            f"font-size: var({variable}-font-size, 1rem); "
            f'font-weight: var({variable}-font-weight, 400)">Aa</span>'
        )
    if token_type in {"shadow", "elevation"}:
        return f'<span class="elevation" style="box-shadow: var({variable})" aria-hidden="true"></span>'
    if token_type in {"duration", "cubicBezier", "motion"}:
        return f'<span class="mono">{esc(display_value(token["value"]))}</span>'
    return f'<span class="mono">{esc(display_value(token["value"]))}</span>'


def group_tokens(tokens: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for path in sorted(tokens):
        group = path.split(".", 1)[0]
        groups.setdefault(group, []).append(path)
    return groups


def section(title: str, section_id: str, body: str) -> str:
    return (
        f'<section class="section" id="{esc(section_id)}">'
        f"<h2>{esc(title)}</h2>{body}</section>"
    )


def render_catalog(
    contract: dict[str, Any],
    tokens: dict[str, dict[str, Any]],
    contract_path: Path,
    input_hash: str,
    tokens_css: str,
) -> str:
    template = read_asset("catalog.html")
    nav: list[str] = []
    sections: list[str] = []

    identity = contract.get("identity") if isinstance(contract.get("identity"), dict) else {}
    identity_body = []
    if identity.get("purpose"):
        identity_body.append(f"<p>{esc(identity['purpose'])}</p>")
    principles = identity.get("principles") if isinstance(identity.get("principles"), list) else []
    if principles:
        identity_body.append("<ul>" + "".join(f"<li>{esc(item)}</li>" for item in principles) + "</ul>")
    if identity_body:
        nav.append('<a href="#identidad">Identidad</a>')
        sections.append(section("Identidad y principios", "identidad", "".join(identity_body)))

    accessibility = contract.get("accessibility") if isinstance(contract.get("accessibility"), dict) else {}
    if accessibility:
        rows = "".join(
            f"<tr><th>{esc(key)}</th><td>{esc(human_value(value))}</td></tr>"
            for key, value in sorted(accessibility.items())
        )
        nav.append('<a href="#accesibilidad">Accesibilidad</a>')
        sections.append(
            section(
                "Accesibilidad",
                "accesibilidad",
                f'<table class="table"><tbody>{rows}</tbody></table>',
            )
        )

    themes = contract.get("themes") if isinstance(contract.get("themes"), dict) else {}
    modes = themes.get("modes") if isinstance(themes.get("modes"), dict) else {}
    if modes:
        names = ", ".join(sorted(modes))
        nav.append('<a href="#temas">Temas</a>')
        sections.append(
            section(
                "Temas y modos",
                "temas",
                f"<p>Modo por defecto: <code>{esc(themes.get('default', 'sin declarar'))}</code>. "
                f"Modos declarados: <code>{esc(names)}</code>.</p>",
            )
        )

    for group, paths in group_tokens(tokens).items():
        section_id = f"tokens-{kebab(group)}"
        nav.append(f'<a href="#{esc(section_id)}">{esc(group)}</a>')
        rows = []
        for path in paths:
            token = tokens[path]
            rows.append(
                "<tr>"
                f'<td><code>{esc(path)}</code></td>'
                f'<td><code>{esc(token["type"] or "sin tipo")}</code></td>'
                f'<td>{render_sample(path, token)}</td>'
                f'<td><code>{esc(display_with_refs(token["value"], tokens))}</code></td>'
                "</tr>"
            )
        sections.append(
            section(
                f"Tokens: {group}",
                section_id,
                '<div class="table-wrap"><table class="table">'
                "<thead><tr><th>Token</th><th>Tipo</th><th>Muestra</th><th>Valor</th></tr></thead>"
                f"<tbody>{''.join(rows)}</tbody></table></div>",
            )
        )

    components = contract.get("components") if isinstance(contract.get("components"), dict) else {}
    if components:
        nav.append('<a href="#componentes">Componentes</a>')
        cards = []
        for name, component in sorted(components.items()):
            if not isinstance(component, dict):
                continue
            body = [f"<h3>{esc(name)}</h3>"]
            if component.get("description"):
                body.append(f"<p>{esc(component['description'])}</p>")
            for field, label in (("when", "Cuándo"), ("when_not", "Cuándo no")):
                values = component.get(field)
                if isinstance(values, list) and values:
                    body.append(
                        f"<h4>{esc(label)}</h4><ul>"
                        + "".join(f"<li>{esc(item)}</li>" for item in values)
                        + "</ul>"
                    )
            states = component.get("states")
            if isinstance(states, list) and states:
                body.append(
                    "<p><strong>Estados:</strong> "
                    + ", ".join(f"<code>{esc(state)}</code>" for state in states)
                    + "</p>"
                )
            variants = component.get("variants")
            if isinstance(variants, dict) and variants:
                rows = []
                for variant_name, bag in sorted(variants.items()):
                    if not isinstance(bag, dict):
                        continue
                    properties = "<br>".join(
                        f"<code>{esc(key)}</code>: <code>{esc(display_with_refs(value, tokens))}</code>"
                        for key, value in sorted(bag.items())
                    )
                    rows.append(f"<tr><td><code>{esc(variant_name)}</code></td><td>{properties}</td></tr>")
                body.append(
                    '<div class="table-wrap"><table class="table">'
                    "<thead><tr><th>Variante</th><th>Tokens</th></tr></thead>"
                    f"<tbody>{''.join(rows)}</tbody></table></div>"
                )
            example = component.get("example")
            if isinstance(example, str) and example.strip():
                iframe_css = tokens_css.replace("</", "<\\/") + (
                    "\nbody{margin:0;padding:16px;background:var(--ds-color-surface,var(--ds-color-background,#ffffff));"
                    "color:var(--ds-color-text,var(--ds-color-foreground,#0f172a));}"
                )
                srcdoc = f"<style>{iframe_css}</style>{example}"
                body.append(
                    f'<iframe class="preview" sandbox loading="lazy" '
                    f'title="Ejemplo de {esc(name)}" srcdoc="{esc(srcdoc)}"></iframe>'
                )
                body.append(
                    '<details><summary>Código del ejemplo</summary>'
                    f"<pre><code>{esc(example)}</code></pre></details>"
                )
            cards.append(f'<article class="component">{"".join(body)}</article>')
        sections.append(
            section("Componentes", "componentes", '<div class="grid">' + "".join(cards) + "</div>")
        )

    constraints = contract.get("constraints") if isinstance(contract.get("constraints"), dict) else {}
    if constraints.get("always") or constraints.get("never"):
        nav.append('<a href="#restricciones">Restricciones</a>')
        body = []
        for field, label in (("always", "Siempre"), ("never", "Nunca")):
            values = constraints.get(field)
            if isinstance(values, list) and values:
                body.append(
                    f"<h3>{esc(label)}</h3><ul>"
                    + "".join(f"<li>{esc(item)}</li>" for item in values)
                    + "</ul>"
                )
        sections.append(section("Restricciones", "restricciones", "".join(body)))

    decisions = contract.get("decisions")
    if isinstance(decisions, list) and decisions:
        nav.append('<a href="#decisiones">Decisiones</a>')
        rows = []
        for decision in decisions:
            if not isinstance(decision, dict):
                continue
            rows.append(
                "<tr>"
                f"<td><code>{esc(decision.get('id', ''))}</code></td>"
                f"<td>{esc(decision.get('decision', ''))}</td>"
                f"<td>{esc(decision.get('rationale', ''))}</td>"
                "</tr>"
            )
        sections.append(
            section(
                "Decisiones",
                "decisiones",
                '<div class="table-wrap"><table class="table">'
                "<thead><tr><th>ID</th><th>Decisión</th><th>Razón</th></tr></thead>"
                f"<tbody>{''.join(rows)}</tbody></table></div>",
            )
        )

    governance = contract.get("governance") if isinstance(contract.get("governance"), dict) else {}
    if governance:
        nav.append('<a href="#gobernanza">Gobernanza</a>')
        body = []
        for field, label in (("protected", "Propiedades protegidas"), ("configurable", "Parámetros configurables")):
            values = governance.get(field)
            if isinstance(values, list) and values:
                body.append(
                    f"<h3>{esc(label)}</h3><ul>"
                    + "".join(f"<li><code>{esc(item)}</code></li>" for item in values)
                    + "</ul>"
                )
        exceptions = governance.get("exceptions")
        if isinstance(exceptions, list) and exceptions:
            body.append("<h3>Excepciones declaradas</h3><ul>")
            for exception in exceptions:
                if isinstance(exception, dict):
                    body.append(
                        f"<li><code>{esc(exception.get('path', ''))}</code>: "
                        f"{esc(exception.get('reason', ''))} "
                        f"(declarada por {esc(exception.get('approved_by', 'sin declarar'))})</li>"
                    )
            body.append("</ul>")
        sections.append(section("Gobernanza", "gobernanza", "".join(body)))

    patterns = contract.get("patterns") if isinstance(contract.get("patterns"), dict) else {}
    if patterns:
        nav.append('<a href="#patrones">Patrones</a>')
        cards = []
        for name, pattern in sorted(patterns.items()):
            if not isinstance(pattern, dict):
                continue
            body = [f"<h3>{esc(name)}</h3>"]
            if pattern.get("description"):
                body.append(f"<p>{esc(pattern['description'])}</p>")
            for field, label in (("when", "Cuándo"), ("rules", "Reglas")):
                values = pattern.get(field)
                if isinstance(values, list) and values:
                    body.append(
                        f"<h4>{esc(label)}</h4><ul>"
                        + "".join(f"<li>{esc(item)}</li>" for item in values)
                        + "</ul>"
                    )
            cards.append(f'<article class="component">{"".join(body)}</article>')
        sections.append(section("Patrones", "patrones", '<div class="grid">' + "".join(cards) + "</div>"))

    sources = contract.get("sources")
    if isinstance(sources, list) and sources:
        nav.append('<a href="#evidencia">Evidencia</a>')
        rows = []
        for source in sources:
            if not isinstance(source, dict):
                continue
            rows.append(
                "<tr>"
                f"<td><code>{esc(source.get('path', ''))}</code></td>"
                f"<td>{esc(source.get('kind', ''))}</td>"
                f"<td>{esc(source.get('note', ''))}</td>"
                "</tr>"
            )
        sections.append(
            section(
                "Evidencia del descubrimiento",
                "evidencia",
                '<div class="table-wrap"><table class="table">'
                "<thead><tr><th>Fuente</th><th>Tipo</th><th>Nota</th></tr></thead>"
                f"<tbody>{''.join(rows)}</tbody></table></div>",
            )
        )

    omitted = contract.get("omitted")
    if isinstance(omitted, list) and omitted:
        nav.append('<a href="#omitido">Omitido</a>')
        sections.append(
            section(
                "Omitido a propósito",
                "omitido",
                "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in omitted) + "</ul>",
            )
        )

    if not sections:
        sections.append(
            section(
                "Contrato mínimo",
                "contrato",
                "<p>El contrato no declara secciones que mostrar. Revisa su contenido.</p>",
            )
        )

    page = (
        template.replace("{{NAME}}", esc(contract.get("name", "sin nombre")))
        .replace("{{VERSION}}", esc(contract.get("version", "")))
        .replace("{{STATUS}}", esc(contract.get("status", "sin estado")))
        .replace("{{CONTRACT}}", esc(contract_path.name))
        .replace("{{NAV}}", "".join(nav))
        .replace("{{SECTIONS}}", "".join(sections))
        .replace("{{HASH}}", esc(input_hash))
    )
    return page


# ---------------------------------------------------------------------------
# Descubrimiento de un proyecto existente (solo lectura)
# ---------------------------------------------------------------------------


def iter_files(root: Path, suffix: str, limit: int = 500) -> Iterable[Path]:
    count = 0
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        for name in sorted(files):
            if name.endswith(suffix):
                yield Path(current) / name
                count += 1
                if count >= limit:
                    return


def is_generated_artifact(path: Path) -> bool:
    manifest = path.parent / "catalog.json"
    if not manifest.is_file():
        return False
    try:
        document = json.loads(read_text(manifest))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(document, dict) and document.get("schema") == CATALOG_SCHEMA


def discover_project(root: Path) -> dict[str, Any]:
    facts: list[dict[str, Any]] = []
    unknown: list[dict[str, str]] = []

    def add(path: Path | str, kind: str, what: str, detail: Any = None) -> None:
        entry: dict[str, Any] = {
            "path": str(path).replace(os.sep, "/"),
            "kind": kind,
            "what": what,
        }
        if detail is not None:
            entry["detail"] = detail
        facts.append(entry)

    contract_candidates = ["design-system.json", "docs/design-system.json", "DESIGN.md", "docs/DESIGN.md", "docs/design.md"]
    contract_found = False
    for rel in contract_candidates:
        path = root / rel
        if path.is_file():
            if path.suffix.lower() == ".md":
                detail = None
                try:
                    headings = re.findall(r"^#{1,3}\s+(.+)$", read_text(path), re.M)
                    if headings:
                        detail = {"headings": headings[:10]}
                except OSError:
                    pass
                add(rel, "documented", "documento de diseño", detail)
            else:
                add(rel, "observed", "contrato del sistema")
            contract_found = True
    for path in sorted(root.glob("*.design")):
        if path.is_file():
            add(path.name, "observed", "contrato .design")
            contract_found = True
    for rel in (
        "tailwind.config.js",
        "tailwind.config.ts",
        "tailwind.config.mjs",
        "tailwind.config.cjs",
        "components.json",
        ".storybook",
    ):
        if (root / rel).exists():
            add(rel, "observed", "configuración de interfaz")

    value_sites: dict[str, set[str]] = {}
    seen_json: set[Path] = set()

    def record_color_values(document: Any, site: str) -> None:
        stack = [document]
        while stack:
            current = stack.pop()
            if isinstance(current, dict):
                stack.extend(current.values())
            elif isinstance(current, list):
                stack.extend(current)
            elif isinstance(current, str):
                value = current.strip().lower()
                if len(value) > 3 and value.startswith(("#", "rgb", "hsl", "oklch")):
                    value_sites.setdefault(value, set()).add(site)

    candidates: list[Path] = []
    for pattern in ("*.tokens.json", "tokens/*.json", "tokens.json", "design-tokens.json", "src/tokens/*.json"):
        candidates.extend(path for path in root.glob(pattern) if path.is_file())
    for path in iter_files(root, ".json", DISCOVERY_JSON_LIMIT):
        if re.search(r"(token|brand|palette|colou?r|theme|design|catalog)", path.name.lower()):
            candidates.append(path)

    token_found = False
    brand_packs: list[str] = []
    for path in sorted(set(candidates)):
        if path in seen_json:
            continue
        seen_json.add(path)
        rel = relpath(path, root)
        try:
            document = json.loads(read_text(path))
        except (OSError, json.JSONDecodeError) as exc:
            add(rel, "observed", f"archivo de tokens ilegible: {exc}")
            continue
        if isinstance(document, dict) and document.get("schema") in {
            SCHEMA,
            CATALOG_SCHEMA,
            ADAPTER_SCHEMA,
            APPROVAL_SCHEMA,
        }:
            if document.get("schema") == CATALOG_SCHEMA:
                add(rel, "observed", "catálogo generado existente", {"role": "generated"})
            continue
        errors: list[str] = []
        tokens = collect_tokens(document, errors, str(path)) if isinstance(document, dict) else {}
        if tokens:
            token_found = True
            add(
                rel,
                "observed",
                f"{len(tokens)} token(s) DTCG",
                {"sample": sorted(tokens)[:DISCOVERY_TOKEN_SAMPLE]},
            )
            record_color_values(document, rel)
        elif isinstance(document, dict) and BRAND_PACK_KEYS & {str(key).lower() for key in document}:
            brand_packs.append(rel)
            add(
                rel,
                "observed",
                "pack de marca sin DTCG (brand-pack)",
                {"keys": sorted(str(key) for key in document)[:8]},
            )
            record_color_values(document, rel)
        else:
            add(rel, "observed", "JSON sin tokens DTCG reconocibles")

    css_found = False
    for index, path in enumerate(iter_files(root, ".css", DISCOVERY_CSS_LIMIT)):
        try:
            text = read_text(path)
        except OSError:
            continue
        variables = [match for match in CSS_VAR_RE.finditer(text)]
        if variables:
            css_found = True
            rel = relpath(path, root)
            role = "generated" if is_generated_artifact(path) else "source"
            add(
                rel,
                "observed",
                f"{len(variables)} variable(s) CSS",
                {"role": role, "sample": sorted({match.group(1) for match in variables})[:DISCOVERY_TOKEN_SAMPLE]},
            )
            for match in variables:
                value = match.group(2).strip().lower()
                if len(value) > 3:
                    value_sites.setdefault(value, set()).add(f"{rel}#--{match.group(1)}")
        if index >= DISCOVERY_CSS_LIMIT:
            break

    component_dirs = ["components", "src/components", "ui", "src/ui", "app/components"]
    component_files: list[str] = []
    for rel in component_dirs:
        directory = root / rel
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".tsx", ".jsx", ".vue", ".svelte", ".html", ".css"}:
                component_files.append(relpath(path, root))
                if len(component_files) >= DISCOVERY_COMPONENT_LIMIT:
                    break
        if len(component_files) >= DISCOVERY_COMPONENT_LIMIT:
            break
    if component_files:
        add(
            "components",
            "observed",
            f"{len(component_files)} archivo(s) de componentes",
            {"sample": component_files[:DISCOVERY_TOKEN_SAMPLE]},
        )

    package_path = root / "package.json"
    if package_path.is_file():
        try:
            package = json.loads(read_text(package_path))
            dependencies = {}
            for field in ("dependencies", "devDependencies"):
                if isinstance(package.get(field), dict):
                    dependencies.update(package[field])
            ui_packages = sorted(
                name
                for name in dependencies
                if name in {
                    "react",
                    "vue",
                    "svelte",
                    "tailwindcss",
                    "@mui/material",
                    "bootstrap",
                    "@chakra-ui/react",
                    "styled-components",
                    "sass",
                }
            )
            if ui_packages:
                add("package.json", "observed", "dependencias de interfaz", {"packages": ui_packages})
        except (OSError, json.JSONDecodeError):
            add("package.json", "observed", "package.json ilegible")

    duplicates = [
        {"value": value, "count": len(sites), "sites": sorted(sites)[:8]}
        for value, sites in value_sites.items()
        if len({site.split("#")[0] for site in sites}) > 1
    ]
    duplicates.sort(key=lambda item: (-item["count"], item["value"]))
    duplicates = duplicates[:DUPLICATE_LIMIT]

    if token_found and not contract_found:
        add(
            ".",
            "inferred",
            "posible sistema de tokens sin contrato canónico",
            "Confirmar la fuente y proponer un contrato antes de escribir.",
        )
    if brand_packs and not token_found:
        add(
            brand_packs[0],
            "inferred",
            "pack de marca probablemente canónico fuera de DTCG",
            "Confirmar si es la fuente o un artefacto de marca antes de convertirlo en tokens DTCG.",
        )
    if component_files and not (root / "design-system.json").is_file():
        add(
            "components",
            "inferred",
            "posible inventario de componentes sin contrato",
            "Confirmar variantes, estados y reglas de uso; no deducirlos del nombre del archivo.",
        )
    if css_found and token_found:
        add(
            ".",
            "inferred",
            "posible duplicidad entre variables CSS y tokens",
            "Confirmar cuál es la fuente canónica antes de copiar valores.",
        )
    if duplicates:
        add(
            ".",
            "inferred",
            f"{len(duplicates)} valor(es) repetido(s) en más de un sitio",
            "Distinguir la fuente del artefacto generado antes de declarar tokens; ver 'duplicates'.",
        )
    if css_found and not token_found:
        add(
            ".",
            "inferred",
            "posible conjunto de tokens en variables CSS",
            "Confirmar nombres, tipos y temas antes de convertirlo en contrato.",
        )
    if contract_found and (root / "DESIGN.md").is_file():
        add(
            "DESIGN.md",
            "inferred",
            "documento de diseño que puede describir decisiones consolidadas",
            "Leerlo como evidencia documentada; no reescribirlo sin autorización.",
        )

    if not any(fact["kind"] in {"observed", "documented"} for fact in facts):
        unknown.append({"what": "sistema visual", "reason": "no se encontró evidencia en el proyecto"})
    if not token_found and not brand_packs:
        unknown.append(
            {
                "what": "tokens",
                "reason": "no se encontraron tokens DTCG ni packs de marca reconocibles",
            }
        )
    if not component_files:
        unknown.append({"what": "componentes", "reason": "no se encontraron directorios de componentes reconocibles"})
    if not any(fact.get("path", "").endswith(".md") for fact in facts):
        unknown.append({"what": "identidad y principios", "reason": "no se encontró documento de diseño o producto"})
    motion = False
    for path in iter_files(root, ".css", DISCOVERY_CSS_LIMIT):
        try:
            if "prefers-reduced-motion" in read_text(path):
                motion = True
                break
        except OSError:
            continue
    if not motion:
        unknown.append({"what": "movimiento y accesibilidad", "reason": "no se encontró evidencia de reduced motion"})

    return {
        "root": str(root.resolve()),
        "mode": "read-only",
        "facts": facts,
        "duplicates": duplicates,
        "unknown": unknown,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def static_report(
    contract: dict[str, Any], contract_path: Path
) -> tuple[Report, dict[str, dict[str, Any]], list[tuple[str, Path]]]:
    report = Report()
    structure_errors, warnings = check_structure(contract)
    report.warnings.extend(warnings)
    report.add("contract-structure", FAIL if structure_errors else PASS, "; ".join(structure_errors))

    tokens, token_inputs, token_errors = load_tokens(contract, contract_path)
    for token in tokens.values():
        error = validate_token_type(token)
        if error:
            token_errors.append(error)
    report.add("token-syntax", FAIL if token_errors else PASS, "; ".join(dedupe(token_errors)))

    reference_errors = check_token_references(tokens)
    reference_errors.extend(check_themes(contract, tokens))
    report.add("token-references", FAIL if reference_errors else PASS, "; ".join(dedupe(reference_errors)))

    component_errors = check_components(contract, tokens)
    report.add("component-contract", FAIL if component_errors else PASS, "; ".join(component_errors))

    if any(token["type"] in COMPOSITE_TYPES for token in tokens.values()):
        report.warnings.append(
            "hay tipos compuestos: se aceptan sin validación profunda; no se afirma conformidad DTCG completa"
        )
    return report, tokens, token_inputs


def print_report(
    report: Report,
    as_json: bool,
    contract_path: Path | None = None,
    inputs: list[tuple[str, Path]] | None = None,
) -> None:
    result = report.result()
    if as_json:
        payload: dict[str, Any] = {
            "result": result,
            "checks": report.checks,
            "warnings": report.warnings,
        }
        if contract_path is not None:
            payload["contract"] = str(contract_path)
        if inputs is not None:
            payload["inputs"] = [
                {"kind": kind, "path": str(path), "sha256": sha256_file(path)} for kind, path in inputs
            ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    for check in report.checks:
        detail = f": {check['detail']}" if check["detail"] else ""
        print(f"{check['status']} {check['id']}{detail}")
    for warning in report.warnings:
        print(f"WARN {warning}")
    print(f"RESULT: {result}")


def command_check(args: argparse.Namespace) -> int:
    contract_path = Path(args.contract)
    contract = load_json(contract_path)
    if not isinstance(contract, dict):
        raise ContractError("el contrato debe ser un objeto JSON")
    report, tokens, token_inputs = static_report(contract, contract_path)
    governance = contract.get("governance")
    if isinstance(governance, dict) and governance.get("protected"):
        report.warnings.append(
            "check no evalúa cambios protegidos; usa gate con --baseline para esa compuerta"
        )

    catalog = check_catalog(contract, contract_path, token_inputs, args.catalog)
    if catalog is not None:
        report.add("catalog-consistency", catalog[0], catalog[1])
    fidelity = check_implementation_fidelity(contract, contract_path)
    if fidelity is not None:
        report.add("implementation-fidelity", fidelity[0], fidelity[1])
    adapters = check_adapters(contract, contract_path)
    if adapters is not None:
        report.add("component-conformance", adapters[0], adapters[1])

    print_report(report, args.json, contract_path, token_inputs)
    return {PASS: EXIT_PASS, FAIL: EXIT_FAIL, UNKNOWN: EXIT_UNKNOWN}[report.result()]


def command_gate(args: argparse.Namespace) -> int:
    contract_path = Path(args.contract)
    contract = load_json(contract_path)
    if not isinstance(contract, dict):
        raise ContractError("el contrato debe ser un objeto JSON")
    report, tokens, token_inputs = static_report(contract, contract_path)

    catalog = check_catalog(contract, contract_path, token_inputs, args.catalog)
    if catalog is not None:
        report.add("catalog-consistency", catalog[0], catalog[1])
    fidelity = check_implementation_fidelity(contract, contract_path)
    if fidelity is not None:
        report.add("implementation-fidelity", fidelity[0], fidelity[1])
    adapters = check_adapters(contract, contract_path)
    if adapters is not None:
        report.add("component-conformance", adapters[0], adapters[1])

    if not args.baseline:
        report.add("protected-changes", UNKNOWN, "falta --baseline; no se puede comparar")
    else:
        baseline_path = Path(args.baseline)
        if not baseline_path.is_file():
            report.add("protected-changes", UNKNOWN, f"no existe el baseline: {baseline_path}")
        else:
            try:
                baseline = json.loads(read_text(baseline_path))
            except (OSError, json.JSONDecodeError) as exc:
                report.add("protected-changes", UNKNOWN, f"baseline ilegible: {exc}")
            else:
                if not isinstance(baseline, dict):
                    report.add("protected-changes", UNKNOWN, "el baseline no es un objeto")
                else:
                    status, detail = check_protected_changes(
                        contract,
                        baseline,
                        Path(args.approvals) if args.approvals else None,
                    )
                    report.add("protected-changes", status, detail)

    print_report(report, args.json, contract_path, token_inputs)
    return {PASS: EXIT_PASS, FAIL: EXIT_FAIL, UNKNOWN: EXIT_UNKNOWN}[report.result()]


def command_catalog(args: argparse.Namespace) -> int:
    contract_path = Path(args.contract)
    contract = load_json(contract_path)
    if not isinstance(contract, dict):
        raise ContractError("el contrato debe ser un objeto JSON")
    if catalog_mode(contract) == "external":
        raise UsageError(
            "catalog.mode es external: el catálogo se mantiene a mano y consume la implementación; "
            "no se genera un tokens.css paralelo"
        )
    report, tokens, token_inputs = static_report(contract, contract_path)
    if report.result() == FAIL:
        print_report(report, args.json, contract_path, token_inputs)
        return EXIT_FAIL

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    tokens_css = build_tokens_css(contract, tokens)
    all_inputs = list(token_inputs) + [
        ("skill-template", ASSETS / "catalog.html"),
        ("skill-template", ASSETS / "catalog.css"),
    ]
    combined_hash = hashlib.sha256(
        "".join(f"{kind}:{sha256_file(path)}\n" for kind, path in all_inputs).encode("utf-8")
    ).hexdigest()
    page = render_catalog(contract, tokens, contract_path, combined_hash, tokens_css)
    catalog_css = read_asset("catalog.css")

    write_text(out_dir / "tokens.css", tokens_css)
    write_text(out_dir / "catalog.css", catalog_css)
    write_text(out_dir / "index.html", page)

    inputs = []
    for kind, path in all_inputs:
        if kind == "skill-template":
            label = f"skill:assets/{path.name}"
        elif kind == "contract":
            label = contract_path.name
        else:
            label = relpath(path, contract_path.parent)
        inputs.append(
            {
                "kind": kind,
                "path": label,
                "sha256": sha256_file(path),
            }
        )
    artifacts = []
    for name in ("index.html", "tokens.css", "catalog.css"):
        path = out_dir / name
        artifacts.append(
            {"path": name, "sha256": sha256_file(path), "bytes": path.stat().st_size}
        )
    manifest = {"schema": CATALOG_SCHEMA, "inputs": inputs, "artifacts": artifacts}
    write_text(out_dir / "catalog.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    declared = catalog_target(contract, contract_path, None)
    if declared is not None and declared.resolve() != out_dir.resolve():
        report.warnings.append(f"el contrato declara catalog en {declared}; se generó en {out_dir}")

    if args.json:
        print(
            json.dumps(
                {
                    "result": PASS,
                    "out": str(out_dir),
                    "artifacts": [artifact["path"] for artifact in artifacts],
                    "inputs": inputs,
                    "warnings": report.warnings,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"PASS catalog: {out_dir}")
        for artifact in artifacts:
            print(f"  {artifact['path']} ({artifact['bytes']} bytes)")
        for warning in report.warnings:
            print(f"WARN {warning}")
    return EXIT_PASS


def command_discover(args: argparse.Namespace) -> int:
    root = Path(args.root)
    if not root.is_dir():
        raise UsageError(f"la raíz no es un directorio: {root}")
    inventory = discover_project(root)
    if args.json:
        print(json.dumps(inventory, ensure_ascii=False, indent=2))
        return EXIT_PASS
    labels = {
        "observed": "OBSERVADO",
        "documented": "DOCUMENTADO",
        "inferred": "INFERIDO",
        "unknown": "DESCONOCIDO",
    }
    for fact in inventory["facts"]:
        detail = ""
        if "detail" in fact:
            detail = f" ({fact['detail']})" if isinstance(fact["detail"], str) else f" ({canonical(fact['detail'])})"
        print(f"{labels.get(fact['kind'], fact['kind'])} {fact['path']}: {fact['what']}{detail}")
    for item in inventory.get("duplicates", []):
        print(f"DUPLICADO {item['value']} en {item['count']} sitios: " + ", ".join(item["sites"]))
    for item in inventory["unknown"]:
        print(f"DESCONOCIDO {item['what']}: {item['reason']}")
    print("MODO: solo lectura; no se escribió ningún archivo")
    return EXIT_PASS


def build_parser() -> argparse.ArgumentParser:
    parser = Parser(description="Valida y documenta un contrato de sistema de diseño")
    subparsers = parser.add_subparsers(dest="command", required=True)

    discover = subparsers.add_parser("discover", help="Inventaría un proyecto existente sin escribirlo")
    discover.add_argument("root")
    discover.add_argument("--json", action="store_true")
    discover.set_defaults(func=command_discover)

    check = subparsers.add_parser("check", help="Comprueba la integridad del contrato")
    check.add_argument("contract")
    check.add_argument("--catalog", help="Directorio del catálogo; sustituye al declarado")
    check.add_argument("--json", action="store_true")
    check.set_defaults(func=command_check)

    gate = subparsers.add_parser("gate", help="Compara contra un baseline y exige aprobación externa")
    gate.add_argument("contract")
    gate.add_argument("--baseline")
    gate.add_argument("--approvals")
    gate.add_argument("--catalog", help="Directorio del catálogo; sustituye al declarado")
    gate.add_argument("--json", action="store_true")
    gate.set_defaults(func=command_gate)

    catalog = subparsers.add_parser("catalog", help="Genera el catálogo estático desde el contrato")
    catalog.add_argument("contract")
    catalog.add_argument("--out", required=True)
    catalog.add_argument("--json", action="store_true")
    catalog.set_defaults(func=command_catalog)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except UsageError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except ContractError as exc:
        print(f"FAIL contract-structure: {exc}", file=sys.stderr)
        return EXIT_FAIL
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
