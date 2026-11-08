#!/usr/bin/env python3
"""Extrae los tokens del proyecto destino y emite un bloque :root copiable.

Uso: python3 tokens-from-project.py <DESIGN.md|design-system.json>

Lee el sistema visual que el proyecto ya declara y escribe por stdout un bloque
`:root { ... }` con custom properties, para pegarlo en el `<style>` del
artefacto. Los valores se copian, no se enlazan: el artefacto sigue siendo
autocontenido y `check-artifact.py` no ve ningún recurso externo.

- `DESIGN.md`: lee los bloques cercados ```css (o sin lenguaje que contengan
  `--`) y extrae las parejas `--nombre: valor;`. No lee el frontmatter.
- `design-system.json`: recorre `tokens` en formato DTCG y convierte cada
  `$value` de cadena en `--ruta-del-token`. Un alias `{color.brand}` se emite
  como `var(--color-brand)`. Un valor compuesto (objeto) se salta con aviso.

Precedencia al integrar el bloque: intención de la persona, sistema del
proyecto, defaults de la plantilla. Si el sistema no declara tokens legibles,
el script sale 1 y el artefacto usa los de la plantilla, declarándolo.
"""
import argparse
import json
import re
import sys
from pathlib import Path

FENCE = re.compile(r"```(?P<lang>[A-Za-z0-9_-]*)[ \t]*\n(?P<body>.*?)```", re.DOTALL)
PROPERTY = re.compile(r"(?P<name>--[A-Za-z0-9_-]+)\s*:\s*(?P<value>[^;{}\n]+);?")
ALIAS = re.compile(r"^\{(?P<ref>[^{}]+)\}$")


def from_markdown(text: str) -> tuple[dict[str, str], list[str]]:
    tokens: dict[str, str] = {}
    warnings: list[str] = []
    for fence in FENCE.finditer(text):
        language = fence.group("lang").lower()
        body = fence.group("body")
        if language not in ("", "css") or "--" not in body:
            continue
        for prop in PROPERTY.finditer(body):
            name = prop.group("name")
            value = prop.group("value").strip()
            if value:
                tokens[name] = value
    if not tokens:
        warnings.append(
            "no hay custom properties en bloques ```css. Añade un bloque con "
            "`:root { --bg: #...; }` al DESIGN.md o pasa design-system.json."
        )
    return tokens, warnings


def from_json(data) -> tuple[dict[str, str], list[str]]:
    tokens: dict[str, str] = {}
    warnings: list[str] = []

    def walk(node, path: list[str]) -> None:
        if not isinstance(node, dict):
            return
        if "$value" in node:
            name = "-".join(part for part in path if part != "$root")
            if not name:
                warnings.append("token sin nombre de ruta; se salta.")
                return
            value = node["$value"]
            if isinstance(value, str) and value.strip():
                tokens[f"--{name}"] = normalize(value.strip())
            else:
                warnings.append(
                    f"el token «{name}» tiene un $value compuesto o vacío; "
                    "se salta. Emite su valor como cadena CSS si lo quieres copiar."
                )
            return
        for key, child in node.items():
            if key.startswith("$"):
                continue
            walk(child, path + [key])

    root = data.get("tokens") if isinstance(data, dict) else None
    if not isinstance(root, dict):
        warnings.append(
            "el JSON no declara un objeto «tokens» (formato design-system.v1 "
            "con tokens DTCG). Pasa el contrato del sistema, no otro JSON."
        )
        return tokens, warnings
    walk(root, [])
    if not tokens:
        warnings.append("no se encontró ningún token con $value de cadena.")
    return tokens, warnings


def normalize(value: str) -> str:
    alias = ALIAS.match(value)
    if alias:
        return f"var(--{alias.group('ref').strip().replace('.', '-')})"
    return value


def render(tokens: dict[str, str]) -> str:
    lines = "\n".join(f"  {name}: {value};" for name, value in tokens.items())
    return f":root {{\n{lines}\n}}\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Emite el bloque :root con los tokens del proyecto destino"
    )
    parser.add_argument("origen", help="DESIGN.md o design-system.json del proyecto")
    args = parser.parse_args(argv)

    path = Path(args.origen)
    try:
        if path.suffix.lower() == ".json":
            tokens, warnings = from_json(json.loads(path.read_text(encoding="utf-8")))
        else:
            tokens, warnings = from_markdown(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"ERROR: no se pudo leer {path}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(
            f"ERROR: {path} no es JSON válido ({exc.msg}, línea {exc.lineno}).",
            file=sys.stderr,
        )
        return 1

    for warning in warnings:
        print(f"AVISO: {warning}", file=sys.stderr)
    if not tokens:
        return 1

    sys.stdout.write(render(tokens))
    return 0


if __name__ == "__main__":
    sys.exit(main())
