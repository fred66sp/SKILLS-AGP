#!/usr/bin/env python3
"""Puerta de forma de casos de prueba e informes de la skill software-testing.

Comprueba que un documento con la forma de caso de prueba o de informe de
pruebas tenga las secciones exigidas, los enumerados correctos y sin
placeholders. Valida forma, no verdad: un documento que pasa no demuestra que
la prueba esté bien diseñada ni que la evidencia sea real.

Uso:
    python3 case-check.py <fichero> [--tipo caso|informe] [--json]

Códigos de salida:
    0  sin defectos (los avisos W* no bloquean)
    1  al menos un defecto (E*)
    2  error de uso: fichero inexistente, tipo imposible o indetectable
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CASE_SECTIONS = [
    "objetivo",
    "entorno",
    "precondiciones",
    "pasos",
    "resultado esperado",
    "resultado observado",
    "estado",
    "evidencia",
]

REPORT_SECTIONS = [
    "alcance",
    "resultado global",
    "cobertura",
    "defectos",
    "no verificado",
    "riesgos residuales",
    "métricas",
    "lecciones",
]

CASE_STATES = {"pendiente", "superado", "superada", "fallado", "fallada", "bloqueado", "bloqueada"}
CASE_STATES_CANON = {"superada": "superado", "fallada": "fallado", "bloqueada": "bloqueado"}
REPORT_RESULTS = {"pendiente", "aprobado", "aprobado con reservas", "suspendido"}

PLACEHOLDER_WORDS = {"todo", "tbd", "fixme", "xxx"}

EVIDENCE_PENDING = "sin ejecutar"


class Finding:
    def __init__(self, code: str, line: int, message: str):
        self.code = code
        self.line = line
        self.message = message

    def as_dict(self) -> dict:
        return {"codigo": self.code, "linea": self.line, "mensaje": self.message}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).lower()


def parse_frontmatter(lines: list[str]) -> tuple[dict[str, str], int]:
    """Devuelve (claves, línea de cierre o -1 si el bloque --- está roto)."""
    if not lines or lines[0].strip() != "---":
        return {}, 0
    values: dict[str, str] = {}
    for index in range(1, len(lines)):
        stripped = lines[index].strip()
        if stripped == "---":
            return values, index + 1
        if not stripped or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        values[key.strip().lower()] = value.strip()
    return {}, -1


def detect_type(text: str, lines: list[str], forced: str | None) -> tuple[str | None, str | None]:
    if forced is not None:
        return forced, None
    frontmatter, _ = parse_frontmatter(lines)
    declared = frontmatter.get("tipo", "").lower()
    if declared in {"caso", "informe"}:
        return declared, None
    for line in lines:
        if line.startswith("# ") and not line.startswith("## "):
            heading = normalize(line)
            if "caso de prueba" in heading:
                return "caso", None
            if "informe de pruebas" in heading:
                return "informe", None
            break
    return None, "No se pudo detectar el tipo de documento: falta el campo 'tipo' en el frontmatter o un título que empiece por 'Caso de prueba' o 'Informe de pruebas'."


def split_sections(lines: list[str], body_start: int) -> dict[str, dict]:
    """Devuelve {título normalizado: {"line": nº H2, "body": [líneas]}}."""
    sections: dict[str, dict] = {}
    current: dict | None = None
    for number in range(body_start, len(lines) + 1):
        line = lines[number - 1] if number <= len(lines) else ""
        heading = None
        if line.startswith("## "):
            heading = normalize(line[3:])
        elif line.startswith("# "):
            heading = ""
        if heading is not None:
            if heading:
                current = {"line": number, "body": []}
                sections.setdefault(heading, current)
            else:
                current = None
            continue
        if current is not None:
            current["body"].append(line)
    return sections


def section_text(section: dict) -> str:
    return "\n".join(section["body"]).strip()


def outside_code_fences(lines: list[str]) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    inside = False
    for number, line in enumerate(lines, start=1):
        if line.lstrip().startswith("```"):
            inside = not inside
            continue
        if not inside:
            result.append((number, line))
    return result


def check_placeholders(lines: list[str], defects: list[Finding]) -> None:
    for number, line in outside_code_fences(lines):
        content = line.strip()
        if not content:
            continue
        lowered = content.lower()
        for word in PLACEHOLDER_WORDS:
            if re.search(rf"\b{word}\b", lowered):
                defects.append(Finding("E05", number, f"placeholder '{word.upper()}' en el texto"))
                break
        else:
            if content == "...":
                defects.append(Finding("E05", number, "línea '...' en lugar de contenido"))
            elif "pendiente de redactar" in lowered:
                defects.append(Finding("E05", number, "placeholder 'pendiente de redactar'"))
            elif re.search(r"(?<!- )\[\s*\]", content):
                defects.append(Finding("E05", number, "corchete vacío sin rellenar"))


def check_case(sections: dict[str, dict], defects: list[Finding], warnings: list[Finding]) -> None:
    for name in CASE_SECTIONS:
        if name not in sections:
            defects.append(Finding("E01", sections_line(sections), f"falta la sección '## {name.capitalize()}'"))
    if "pasos" in sections:
        steps = section_text(sections["pasos"])
        if not re.search(r"(?m)^\d+\.\s", steps):
            defects.append(Finding("E04", sections["pasos"]["line"], "la sección Pasos no tiene pasos numerados"))
    state = first_content(sections.get("estado"))
    state_canon = CASE_STATES_CANON.get(state, state)
    if state:
        if state not in CASE_STATES:
            defects.append(Finding("E02", sections["estado"]["line"], f"estado '{state}' fuera del enumerado pendiente|superado|fallado|bloqueado"))
        elif state_canon in {"superado", "fallado"}:
            evidence = normalize(first_content(sections.get("evidencia")))
            if not evidence or evidence == EVIDENCE_PENDING:
                defects.append(Finding("E03", sections["estado"]["line"], "un caso superado o fallado exige evidencia observada"))
        else:
            warnings.append(Finding("W01", sections["estado"]["line"], f"caso con estado '{state_canon}': no ejecutado"))


def sections_line(sections: dict[str, dict]) -> int:
    for section in sections.values():
        return section["line"]
    return 1


def first_content(section: dict | None) -> str:
    if not section:
        return ""
    for line in section["body"]:
        if line.strip():
            return line.strip()
    return ""


def check_report(sections: dict[str, dict], defects: list[Finding], warnings: list[Finding]) -> None:
    for name in REPORT_SECTIONS:
        if name not in sections:
            defects.append(Finding("E01", sections_line(sections), f"falta la sección '## {name.capitalize()}'"))
    if "resultado global" in sections:
        result = normalize(first_content(sections["resultado global"]))
        if result and result not in REPORT_RESULTS:
            defects.append(Finding("E06", sections["resultado global"]["line"], f"resultado global '{result}' fuera del enumerado pendiente|aprobado|aprobado con reservas|suspendido"))
    if "cobertura" in sections:
        coverage = normalize(section_text(sections["cobertura"]))
        if coverage and "no probad" not in coverage:
            defects.append(Finding("E07", sections["cobertura"]["line"], "la Cobertura no declara lo no probado y su motivo"))
    if "métricas" in sections:
        check_metrics(sections["métricas"], defects, warnings)


def check_metrics(section: dict, defects: list[Finding], warnings: list[Finding]) -> None:
    text = section_text(section).lower()
    executed = re.search(r"casos\s+ejecutados:\s*(\d+)\s+de\s+\d+", text)
    passed = re.search(r"casos\s+superados:\s*(\d+)", text)
    failed = re.search(r"casos\s+fallados:\s*(\d+)", text)
    blocked = re.search(r"casos\s+bloqueados:\s*(\d+)", text)
    counts = [executed, passed, failed, blocked]
    if all(counts):
        total = int(executed.group(1))
        accounted = int(passed.group(1)) + int(failed.group(1)) + int(blocked.group(1))
        if accounted != total:
            defects.append(Finding("E08", section["line"], f"métricas incoherentes: {passed.group(1)}+{failed.group(1)}+{blocked.group(1)} != {total} ejecutados"))
    else:
        warnings.append(Finding("W02", section["line"], "métricas incompletas o sin enteros; no se puede comprobar la coherencia"))


def run_check(path: Path, forced: str | None) -> tuple[int, str | None, dict | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        return 2, f"No se pudo leer '{path}': {error}", None

    lines = text.splitlines()
    frontmatter, end = parse_frontmatter(lines)
    if end == -1:
        return 2, "Frontmatter roto: el bloque '---' inicial no se cierra.", None

    doc_type, error = detect_type(text, lines[end:], forced)
    if doc_type is None:
        return 2, error, None

    body_start = end + 1 if end else 1
    sections = split_sections(lines, body_start)

    defects: list[Finding] = []
    warnings: list[Finding] = []
    check_placeholders(lines[body_start - 1:], defects)
    if doc_type == "caso":
        check_case(sections, defects, warnings)
    else:
        check_report(sections, defects, warnings)

    report = {
        "fichero": str(path),
        "tipo": doc_type,
        "defectos": [finding.as_dict() for finding in defects],
        "avisos": [finding.as_dict() for finding in warnings],
    }
    exit_code = 1 if defects else 0
    return exit_code, None, report


def render_text(report: dict) -> str:
    file = report["fichero"]
    lines: list[str] = []
    for kind, label in (("defectos", "error"), ("avisos", "aviso")):
        for finding in report[kind]:
            lines.append(f"{finding['codigo']} {file}:{finding['linea']} [{label}] {finding['mensaje']}")
    if not report["defectos"]:
        count = len(report["avisos"])
        suffix = f"; {count} {'aviso' if count == 1 else 'avisos'}" if count else "; sin avisos"
        lines.append(f"OK {file} ({report['tipo']}{suffix})")
    else:
        lines.append(f"{len(report['defectos'])} defectos, {len(report['avisos'])} avisos en {file}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Puerta de forma de casos de prueba e informes de la skill software-testing.")
    parser.add_argument("file", help="documento a comprobar (Markdown)")
    parser.add_argument("--tipo", choices=("caso", "informe"), default=None, help="fuerza el tipo en lugar de autodetectarlo")
    parser.add_argument("--json", action="store_true", help="salida JSON en lugar de texto")
    args = parser.parse_args(argv)

    path = Path(args.file)
    if not path.is_file():
        print(f"error de uso: '{args.file}' no existe o no es un fichero", file=sys.stderr)
        return 2

    exit_code, error, report = run_check(path, args.tipo)
    if error is not None:
        print(f"error de uso: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
