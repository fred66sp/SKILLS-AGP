#!/usr/bin/env python3
"""Comprobación determinista de archivos `.feature` contra las reglas de buen Gherkin.

Uso:
    python3 scripts/check-feature.py --path <archivo.feature> [--json]
                                     [--max-steps N] [--max-outline-rows N]

Salida por stdout: un hallazgo por línea con su código, si es determinista o candidato,
la posición `archivo:linea`, la evidencia del paso y el mensaje para autocorregirse. Al
final, un resumen por archivo con el recuento de deterministas y candidatos.

Códigos deterministas (hecho medible, suficiente para `NO APTO` cuando la regla 2 o la
estructura lo indican): `step-order`, `missing-then`, `multiple-action-outcome`,
`too-many-steps`, `outline-missing-placeholder`, `unparseable-block`.

Candidatos (heurística: el revisor los confirma o los refuta antes de escribirlos en el
informe): `low-level-vocab`, `person-mixed`, `no-subject-verb`, `redundant-examples`,
`business-intent-given`.

Umbrales por defecto: `--max-steps 9` (longitud de un solo dígito, contando los pasos de
`Background`) y `--max-outline-rows 5` (filas de un `Scenario Outline`).

Códigos de salida:
    0  archivo sin hallazgos
    3  al menos un hallazgo (determinista o candidato)
    2  error de uso: falta `--path`, la ruta no existe, no es un archivo o el idioma
       declarado en `# language:` no se soporta
"""

import argparse
import json
import re
import sys

KEYWORDS = {
    "en": {
        "feature": ["Feature"],
        "background": ["Background"],
        "outline": ["Scenario Outline"],
        "scenario": ["Scenario"],
        "examples": ["Examples", "Scenarios"],
        "given": ["Given"],
        "when": ["When"],
        "then": ["Then"],
        "conj": ["And", "But", "*"],
    },
    "es": {
        "feature": ["Característica", "Funcionalidad"],
        "background": ["Antecedentes"],
        "outline": ["Esquema del escenario", "Esquema de escenario", "Esquema"],
        "scenario": ["Escenario"],
        "examples": ["Ejemplos"],
        "given": ["Dado", "Dada", "Dados", "Dadas"],
        "when": ["Cuando"],
        "then": ["Entonces"],
        "conj": ["Y", "E pero", "Pero", "*"],
    },
}
SUPPORTED_LANGS = {"en", "es"}

# Cada bloque `keyword` se empareja con la lista de palabras que lo abren. El orden de
# búsqueda es por longitud descendente, para que `Scenario Outline` no se lea como `Scenario`.
MATCHERS = {}
for _lang, _types in KEYWORDS.items():
    for _type, _words in _types.items():
        for _word in _words:
            MATCHERS.setdefault(_word.lower(), []).append((_type, _lang))

STEP_TYPES = {"given", "when", "then", "conj"}
BLOCK_TYPES = {"feature", "background", "scenario", "outline", "examples"}

if hasattr(sys.stdout, "reconfigure"):
    # Windows arrive con cp1252 y los mensajes en español saldrían inservibles.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (ValueError, OSError):
        pass

LANG_RE = re.compile(r"^\s*#\s*language\s*:\s*([A-Za-z-]+)\s*$")
TAG_RE = re.compile(r"^\s*(@\S*)")
TABLE_RE = re.compile(r"^\s*\|(.*)\|\s*$")
PLACEHOLDER_RE = re.compile(r"<([^<>]+)>")
CONJ_TEXT_RE = re.compile(r"^(?:que|that)\s+", re.IGNORECASE)

LOW_LEVEL_TERMS = [
    "click", "clic", "clica", "pulse", "pinchar", "botón", "button", "teclea", "escribe",
    "typed", "type ", "wait", "espera", "scroll", "navega a", "navegar a", "http://",
    "https://", "checkbox", "casilla", "dropdown", "desplegable",
]
FIRST_PERSON_RE = re.compile(r"(?<![\w-])(I|my|me|yo|mí|mi)(?![\w-])", re.IGNORECASE)
# Solo cuentan los actores nombrados: `the home page is visible` es impersonal y no rompe
# el punto de vista; `the user opens the page` sí convive mal con un paso en primera persona.
THIRD_PERSON_RE = re.compile(
    r"(?<![\w-])(?:the|un|una|el|la|los|las)\s+"
    r"(developer|maintainer|engineer|reviewer|user|users|shopper|customer|buyer|visitor|"
    r"administrator|admin|clerk|operator|system|pipeline|compiler|validator|runner|build|"
    r"desarrollador|desarrolladora|mantenedor|mantenedora|ingeniero|ingeniera|revisor|revisora|"
    r"usuario|usuaria|compradora|comprador|cliente|visitante|dependienta|dependiente|"
    r"administradora|administrador|operadora|operador|sistema|pipeline|compilador|compiladora|"
    r"validador|validadora|ejecutor|ejecutora)\b",
    re.IGNORECASE,
)
INTENT_RE = re.compile(
    r"(?<![\w-])(quiero|necesito|deseo|we want|i want|i need)(?![\w-])", re.IGNORECASE
)


def classify(text):
    """Devuelve (tipo, idioma, resto_del_texto) para una línea, o None si no es palabra clave.

    Los bloques llevan dos puntos (`Feature:`, `Scenario Outline:`, `Examples:`); los pasos
    no (`Given ...`, `Dado que ...`, `Y ...`). La palabra clave debe ir seguida de dos
    puntos, de espacio o del final de línea, para que `Y` no casque con `Yo` y `But` no
    casque con `button`. Se usa la coincidencia más larga, así `Scenario Outline` no se
    lee como `Scenario`.
    """
    stripped = text.strip()
    if not stripped:
        return None
    lowered = stripped.lower()
    candidates = []
    for key, entries in MATCHERS.items():
        if not lowered.startswith(key):
            continue
        rest = stripped[len(key):]
        if rest and rest[0] not in (":", " "):
            continue
        block_form = rest.startswith(":")
        remainder = rest.lstrip(": ").strip()
        for entry in entries:
            is_block = entry[0] in BLOCK_TYPES
            if block_form == is_block:
                candidates.append((len(key) + (1 if block_form else 0), entry, remainder))
    if not candidates:
        return None
    candidates.sort(key=lambda item: -item[0])
    _, (kind, lang), remainder = candidates[0]
    return kind, lang, remainder


def normalize_step(text):
    """Quita el `que`/`that` de relleno que dejan las palabras clave compuestas."""
    return CONJ_TEXT_RE.sub("", text, count=1).strip()


def read_lines(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        return handle.read().splitlines()


def declared_language(lines):
    for line in lines:
        if not line.strip():
            continue
        match = LANG_RE.match(line)
        if not match:
            return None
        code = match.group(1).lower().split("-")[0]
        return code
    return None


def split_table_row(line):
    match = TABLE_RE.match(line)
    if not match:
        return None
    return [cell.strip() for cell in match.group(1).split("|")]


def parse(path):
    """Analiza un `.feature` y devuelve (bloques, error_de_parseo)."""
    lines = read_lines(path)
    lang = declared_language(lines)
    if lang is not None and lang not in SUPPORTED_LANGS:
        return None, (
            f"idioma declarado `# language: {lang}` no soportado; solo se soportan "
            f"'en' y 'es' — quite el encabezado o revise el archivo con ese idioma configurado"
        )

    blocks = []
    current = None
    feature = None
    in_docstring = False
    pending_tags = []
    examples_state = None

    for index, raw in enumerate(lines, start=1):
        text = raw.strip()
        if not text:
            in_docstring = False
            continue
        if LANG_RE.match(raw):
            continue
        if TAG_RE.match(raw) and not text.startswith("#"):
            pending_tags.append(text)
            continue
        if text.startswith("#"):
            continue

        table = TABLE_RE.match(raw)
        if table and examples_state is not None:
            examples_state["rows"].append({"cells": split_table_row(raw), "line": index})
            continue
        if table and examples_state is None:
            blocks.append({
                "kind": "orphan-table", "line": index, "name": text, "steps": [],
                "tags": [], "examples": None,
            })
            continue

        classified = classify(raw)
        if classified and classified[0] in BLOCK_TYPES:
            kind, _lang, rest = classified
            if kind == "feature":
                feature = {"kind": "feature", "line": index, "name": rest, "steps": [],
                           "tags": pending_tags, "examples": None}
                blocks.append(feature)
                pending_tags = []
                in_docstring = True
                current = None
                continue
            if kind == "examples":
                if current is not None and current["kind"] in ("outline", "scenario"):
                    examples_state = {"header": None, "rows": [], "line": index}
                    current["examples_state"] = examples_state
                    current["examples_line"] = index
                in_docstring = False
                continue
            current = {
                "kind": "background" if kind == "background" else
                        ("outline" if kind == "outline" else "scenario"),
                "line": index,
                "name": rest,
                "steps": [],
                "tags": pending_tags,
                "examples": None,
                "examples_state": None,
                "examples_line": None,
            }
            pending_tags = []
            examples_state = None
            blocks.append(current)
            continue

        if classified and classified[0] in STEP_TYPES:
            if current is None:
                blocks.append({"kind": "orphan-step", "line": index, "name": text,
                               "steps": [], "tags": [], "examples": None})
                continue
            step_kind, _lang, rest = classified
            resolved = step_kind
            if step_kind == "conj" and current["steps"]:
                resolved = current["steps"][-1]["type"]
            elif step_kind == "conj":
                resolved = None
            current["steps"].append({"type": resolved, "raw": step_kind, "text": normalize_step(rest),
                                      "source": text, "line": index})
            in_docstring = False
            continue

        if current is None and feature is not None and in_docstring:
            continue
        if current is None:
            continue

    # Cerrar tablas de ejemplos: la primera fila es la cabecera.
    for block in blocks:
        state = block.get("examples_state")
        if not state:
            continue
        rows = state["rows"]
        if rows:
            block["examples"] = {
                "header": rows[0]["cells"],
                "header_line": rows[0]["line"],
                "rows": rows[1:],
                "line": state["line"],
                "rows_without_header": rows,
            }
        else:
            block["examples"] = {"header": [], "header_line": state["line"], "rows": [],
                                 "line": state["line"], "rows_without_header": []}

    return blocks, None


# --- Comprobaciones -------------------------------------------------------------

def check_missing_then(blocks, _limits):
    findings = []
    for block in blocks:
        if block["kind"] not in ("scenario", "outline") or not block["steps"]:
            continue
        types = {step["type"] for step in block["steps"]}
        if "then" not in types:
            findings.append({
                "rule": "missing-then", "deterministic": True, "line": block["line"],
                "evidence": f"{describe(block)}: {block['name']}",
                "regla": 1,
                "message": "el escenario no tiene ningún `Entonces`/`Then`: sin aserción no hay "
                           "criterio de aceptación ni forma de verificar el comportamiento",
            })
    return findings


def check_step_order(blocks, _limits):
    findings = []
    for block in blocks:
        if block["kind"] not in ("scenario", "outline"):
            continue
        seen_action = None
        for step in block["steps"]:
            if step["type"] in ("when", "then"):
                if seen_action is None:
                    seen_action = step
            elif step["type"] == "given" and seen_action is not None:
                findings.append({
                    "rule": "step-order", "deterministic": True, "line": step["line"],
                    "evidence": step["source"],
                    "regla": 1,
                    "message": "`Dado`/`Given` después de la acción (primera acción en la línea "
                               f"{seen_action['line']}): el orden debe ser setup → acción → verificación; "
                               "conviértalo en estado inicial antes del `Cuando` o divida el escenario",
                })
    return findings


def background_of(blocks):
    for block in blocks:
        if block["kind"] == "background":
            return block
    return None


def compressed_types(block):
    """Agrupa pasos consecutivos del mismo tipo: [(tipo, [pasos])] en orden de aparición."""
    groups = []
    for step in block["steps"]:
        if groups and groups[-1][0] == step["type"]:
            groups[-1][1].append(step)
        else:
            groups.append((step["type"], [step]))
    return groups


def term_matches(term, text):
    lowered = text.lower()
    needle = term.lower()
    if " " in needle or "://" in needle or needle.endswith("-"):
        return needle in lowered
    return re.search(r"(?<!\w)" + re.escape(needle) + r"(?!\w)", lowered) is not None


def check_unparseable(blocks, _limits):
    findings = []
    if not any(block["kind"] == "feature" for block in blocks):
        findings.append({
            "rule": "unparseable-block", "deterministic": True, "line": 1, "regla": 0,
            "evidence": "(sin encabezado de funcionalidad)",
            "message": "el archivo no declara `Feature:` ni `Característica:`: no hay artefacto de "
                       "comportamiento que revisar; confirme que el encargo apunta a un `.feature`",
        })
    for block in blocks:
        if block["kind"] == "orphan-step":
            findings.append({
                "rule": "unparseable-block", "deterministic": True, "line": block["line"], "regla": 0,
                "evidence": block["name"],
                "message": "paso fuera de cualquier `Scenario`: un paso solo existe dentro de un "
                           "escenario, de un esquema o de `Background`",
            })
        elif block["kind"] == "orphan-table":
            findings.append({
                "rule": "unparseable-block", "deterministic": True, "line": block["line"], "regla": 0,
                "evidence": block["name"],
                "message": "tabla fuera de un bloque `Examples`/`Ejemplos`: no hay filas que "
                           "sustituir en los pasos",
            })
        elif block["kind"] in ("scenario", "outline") and not block["name"]:
            findings.append({
                "rule": "unparseable-block", "deterministic": True, "line": block["line"], "regla": 0,
                "evidence": describe(block) + ": (sin título)",
                "message": "escenario sin título: el título es lo que se lee en el informe de "
                           "pruebas y en el triaje de un fallo",
            })
    return findings


def check_multiple_action(blocks, _limits):
    """Regla 2: dos ciclos acción-verificación en un escenario son dos comportamientos."""
    findings = []
    for block in blocks:
        if block["kind"] not in ("scenario", "outline"):
            continue
        groups = compressed_types(block)
        cycles = [index for index, (kind, _) in enumerate(groups)
                  if kind == "when" and any(later == "then" for later, _ in groups[index + 1:])]
        if len(cycles) > 1:
            step = groups[cycles[1]][1][0]
            findings.append({
                "rule": "multiple-action-outcome", "deterministic": True, "line": step["line"],
                "regla": 2, "evidence": step["source"],
                "message": f"segunda acción con su verificación en `{block['name']}`: son dos "
                           "comportamientos. Divida el escenario y sitúe el segundo con su propio "
                           "`Dado`, aunque empiece en mitad de la acción",
            })
    return findings


def check_too_many_steps(blocks, limits):
    background = background_of(blocks)
    background_steps = len(background["steps"]) if background else 0
    findings = []
    for block in blocks:
        if block["kind"] not in ("scenario", "outline"):
            continue
        total = len(block["steps"]) + background_steps
        if total > limits["max_steps"]:
            findings.append({
                "rule": "too-many-steps", "deterministic": True, "line": block["line"], "regla": 1,
                "evidence": f"{describe(block)}: {block['name']}",
                "message": f"{total} pasos efectivos ({len(block['steps'])} del escenario más "
                           f"{background_steps} de `Background`), el máximo declarado es "
                           f"{limits['max_steps']}: suba de nivel y deje el detalle en la "
                           "automatización, o divida comportamientos",
            })
    return findings


def check_outlines(blocks, _limits):
    findings = []
    for block in blocks:
        if block["kind"] != "outline":
            continue
        placeholders = set()
        for step in block["steps"]:
            placeholders.update(PLACEHOLDER_RE.findall(step["text"]))
        examples = block.get("examples")
        if examples is None:
            findings.append({
                "rule": "outline-missing-placeholder", "deterministic": True, "line": block["line"],
                "regla": 0, "evidence": f"Scenario Outline: {block['name']}",
                "message": "esquema sin tabla `Examples`/`Ejemplos`: no hay datos que sustituir, "
                           "así que no genera pruebas",
            })
            continue
        header = examples["header"]
        for placeholder in sorted(placeholders - set(header)):
            findings.append({
                "rule": "outline-missing-placeholder", "deterministic": True, "line": block["line"],
                "regla": 0, "evidence": f"<{placeholder}>",
                "message": f"el paso usa <{placeholder}> pero `Examples` no tiene esa columna: "
                           "la sustitución quedará sin valor",
            })
        for column in header:
            if column not in placeholders:
                findings.append({
                    "rule": "outline-missing-placeholder", "deterministic": True,
                    "line": examples["header_line"], "regla": 0, "evidence": f"| {column} |",
                    "message": f"la columna `{column}` no la consume ningún `<placeholder>` del "
                               "esquema: fila de datos que no llega a la prueba",
                })
        for row in examples["rows"]:
            if len(row["cells"]) != len(header):
                findings.append({
                    "rule": "outline-missing-placeholder", "deterministic": True, "line": row["line"],
                    "regla": 0, "evidence": "| " + " | ".join(row["cells"]) + " |",
                    "message": f"fila con {len(row['cells'])} columnas frente a {len(header)} de la "
                               "cabecera: la tabla está mal formada",
                })
    return findings


def check_redundant_examples(blocks, limits):
    findings = []
    for block in blocks:
        if block["kind"] != "outline" or not block.get("examples"):
            continue
        examples = block["examples"]
        rows, header = examples["rows"], examples["header"]
        if len(rows) > limits["max_outline_rows"]:
            findings.append({
                "rule": "redundant-examples", "deterministic": False, "line": examples["header_line"],
                "regla": 3, "evidence": f"{len(rows)} filas en `Examples`",
                "message": f"{len(rows)} filas superan el umbral de {limits['max_outline_rows']}: "
                           "confirme si de verdad hay esa cantidad de clases de equivalencia; cada "
                           "fila es una prueba que se ejecuta",
            })
        varying = []
        for index, column in enumerate(header):
            values = {row["cells"][index] for row in rows if len(row["cells"]) > index}
            if len(values) > 1:
                varying.append(column)
        if len(rows) >= 3 and len(varying) == 1:
            findings.append({
                "rule": "redundant-examples", "deterministic": False, "line": examples["header_line"],
                "regla": 3, "evidence": f"todas las filas difieren solo en `{varying[0]}`",
                "message": "las filas cambian únicamente una columna: compruebe si son la misma "
                           "clase de equivalencia repetida; si lo son, deje un ejemplo",
            })
    return findings


def check_low_level_vocab(blocks, _limits):
    findings = []
    for block in blocks:
        if block["kind"] == "feature":
            continue
        for step in block["steps"]:
            matched = [term for term in LOW_LEVEL_TERMS if term_matches(term, step["text"])]
            if matched:
                findings.append({
                    "rule": "low-level-vocab", "deterministic": False, "line": step["line"], "regla": 1,
                    "evidence": step["source"],
                    "message": "el paso describe el cómo (" + ", ".join(sorted(set(matched))) +
                               "): suba al qué quiere el usuario; el detalle mecánico vive en los "
                               "hooks y en la automatización",
                })
    return findings


def check_person_mixed(blocks, _limits):
    findings = []
    for block in blocks:
        if block["kind"] not in ("scenario", "outline"):
            continue
        first = [step for step in block["steps"] if FIRST_PERSON_RE.search(step["text"])]
        third = [step for step in block["steps"] if THIRD_PERSON_RE.search(step["text"])]
        if first and third:
            findings.append({
                "rule": "person-mixed", "deterministic": False, "line": block["line"], "regla": 4,
                "evidence": f"primera persona en la línea {first[0]['line']}, tercera en la "
                            f"línea {third[0]['line']}",
                "message": "el escenario mezcla `yo` con actores en tercera persona: elija tercera "
                           "persona y reescriba los pasos, que además podrán reutilizarse sueltos",
            })
    return findings


def check_no_subject_verb(blocks, _limits):
    findings = []
    for block in blocks:
        if block["kind"] == "feature":
            continue
        for step in block["steps"]:
            if len(step["text"].split()) < 3:
                findings.append({
                    "rule": "no-subject-verb", "deterministic": False, "line": step["line"], "regla": 4,
                    "evidence": step["source"],
                    "message": "el paso no tiene sujeto y predicado legibles: fuera de su "
                               "escenario no se sabría qué verificar con él; reescríbalo como frase "
                               "completa",
                })
    return findings


def check_business_intent(blocks, _limits):
    findings = []
    for block in blocks:
        for step in block["steps"]:
            if step["type"] == "given" and INTENT_RE.search(step["text"]):
                findings.append({
                    "rule": "business-intent-given", "deterministic": False, "line": step["line"],
                    "regla": 1, "evidence": step["source"],
                    "message": "un `Dado` declara estado inicial, no una intención de negocio: la "
                               "propuesta de valor va en la historia de usuario bajo `Feature`",
                })
    return findings


CHECKS = [
    check_unparseable,
    check_missing_then,
    check_step_order,
    check_multiple_action,
    check_too_many_steps,
    check_outlines,
    check_redundant_examples,
    check_low_level_vocab,
    check_person_mixed,
    check_no_subject_verb,
    check_business_intent,
]


def describe(block):
    if block["kind"] == "outline":
        return "Scenario Outline"
    return "Background" if block["kind"] == "background" else "Scenario"


def format_finding(finding, path):
    mark = "D" if finding["deterministic"] else "C"
    evidence = finding["evidence"]
    if len(evidence) > 64:
        evidence = evidence[:61] + "..."
    return (f"[{mark}] regla {finding['regla'] if finding['regla'] else '-'} "
            f"{finding['rule']:28} {path}:{finding['line']:<4} \"{evidence}\" "
            f"→ {finding['message']}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="check-feature.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Revisa un `.feature` contra las cuatro reglas de buen Gherkin.\n\n"
            "Deterministas (hecho medible): step-order, missing-then, multiple-action-outcome,\n"
            "too-many-steps, outline-missing-placeholder, unparseable-block.\n"
            "Candidatos heurísticos (el revisor confirma o refuta antes de escribirlos en el\n"
            "informe): low-level-vocab, person-mixed, no-subject-verb, redundant-examples,\n"
            "business-intent-given.\n\n"
            "Umbrales por defecto: --max-steps 9 y --max-outline-rows 5. Use --json para volcar\n"
            "los hallazgos al informe sin reescribirlos a mano."
        ),
    )
    parser.add_argument("--path", required=True, help="archivo .feature a revisar")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="emite los hallazgos como array JSON en stdout")
    parser.add_argument("--max-steps", type=int, default=9,
                        help="máximo de pasos efectivos por escenario (por defecto 9)")
    parser.add_argument("--max-outline-rows", type=int, default=5,
                        help="máximo de filas de Examples antes de señalar redundancia "
                             "(por defecto 5)")
    args = parser.parse_args(argv)

    import os

    if not os.path.exists(args.path):
        print(f"check-feature.py: la ruta no existe: {args.path}", file=sys.stderr)
        return 2
    if not os.path.isfile(args.path):
        print(f"check-feature.py: la ruta no es un archivo: {args.path}", file=sys.stderr)
        return 2

    try:
        blocks, parse_error = parse(args.path)
    except (OSError, UnicodeDecodeError) as error:
        print(f"check-feature.py: no se pudo leer {args.path}: {error}", file=sys.stderr)
        return 2

    if parse_error:
        print(f"check-feature.py: {parse_error}", file=sys.stderr)
        return 2

    findings = []
    limits = {"max_steps": args.max_steps, "max_outline_rows": args.max_outline_rows}
    for check in CHECKS:
        findings.extend(check(blocks, limits))
    findings.sort(key=lambda item: (item["line"], item["rule"]))

    if args.as_json:
        payload = [{key: value for key, value in finding.items() if key != "regla"}
                   for finding in findings]
        for finding in payload:
            finding["file"] = args.path.replace("\\", "/")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if not findings:
            print(f"{args.path}: sin hallazgos")
        else:
            print(f"hallazgos en {args.path}:")
            for finding in findings:
                print("  " + format_finding(finding, args.path.replace("\\", "/")))
        deterministic = sum(1 for finding in findings if finding["deterministic"])
        candidates = len(findings) - deterministic
        print(f"resumen: {args.path} — {len(findings)} hallazgos "
              f"({deterministic} deterministas, {candidates} candidatos)")

    return 3 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
