#!/usr/bin/env python3
"""Comprueba la forma de un texto en castellano: tipografía y tics de escritura de IA.

Uso:
    python scripts/redactor.py check <fichero|-> [--json] [--strict]

Comprueba, fuera del frontmatter y de los bloques de código:
- defectos deterministas de tipografía española: comillas curvas, raya con
  espacios al estilo inglés, doble guion, falta de ¿ o ¡, emojis en el cuerpo;
- señales de escritura de IA que exigen criterio: paralelismo negativo,
  evitación de la cópula, muletillas, conclusiones genéricas, signposting,
  artefactos de chat, léxico sobreusado, gerundio de consecuencia, rangos
  falsos, listas con etiqueta en negrita, title case, raya sobreusada,
  ritmo uniforme y conectores formulaicos en párrafos consecutivos.

No valida el significado, los hechos ni la calidad del argumento.

Códigos de salida:
    0  sin hallazgos, o solo avisos sin --strict
    1  hay hallazgos que incumplen el umbral
    2  error de uso o de lectura
"""

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

FENCE_RE = re.compile(r"^\s*(```+|~~~+)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
URL_RE = re.compile(r"https?://\S+")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")
PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n")
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]+|[^.!?]+$")

# (identificador, severidad, expresión, mensaje)
RULES = [
    ("T01", "error", re.compile(r"[\u201c\u201d\u2018\u2019]"),
     "comillas curvas: usa «latinas» o \"rectas\""),
    ("T02", "error", re.compile(r"\s\u2014\s"),
     "raya con espacios: en castellano va pegada al texto —así—"),
    ("T03", "error", re.compile(r"(?<=\s)--(?=\s)"),
     "doble guion: usa la raya — para el inciso"),
    ("T06", "error", re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]"),
     "emoji en el cuerpo del texto"),
    ("P08", "aviso", re.compile(
        r"\bse erige como\b|\bse posiciona como\b|\bse configura como\b"
        r"|\bconstituye (?:un|una|el|la|los|las)\b", re.IGNORECASE),
     "evitación de la cópula: prueba con «es» o «tiene»"),
    ("P09", "aviso", re.compile(
        r"\bno (?:solo|solamente|únicamente)\b[^.\n]{0,120}?\bsino\b", re.IGNORECASE),
     "paralelismo negativo: di directamente la segunda mitad"),
    ("P12", "aviso", re.compile(r"\bdesde\b[^.\n]{1,40}\bhasta\b", re.IGNORECASE),
     "rango: comprueba que los extremos están en una escala real"),
    ("P16", "aviso", re.compile(r"^\s*[-*]\s+\*\*[^*\n]+\*\*", re.MULTILINE),
     "lista con etiqueta en negrita: valora prosa o lista paralela"),
    ("P07", "aviso", re.compile(
        r"\bun sinfín de\b|\buna miríada de\b|\bun abanico de\b|\buna amplia gama de\b"
        r"|\bprofundizar en\b|\badentrarse en\b|\bsumergirse en\b|\bfomentar\b"
        r"|\bpotenciar\b|\boptimizar\b|\bmaximizar\b|\bholístic[oa]s?\b"
        r"|\bsinérgic[oa]s?\b|\bdisruptiv[oa]s?\b|\bvanguardistas?\b"
        r"|\ben aras de\b|\bde la mano de\b|\bponer de manifiesto\b", re.IGNORECASE),
     "léxico sobreusado: comprueba el racimo y busca el verbo concreto"),
    ("P20", "aviso", re.compile(
        r"¡claro!|¡por supuesto!|espero que (?:esto )?te sirva"
        r"|si necesitas algo más|aquí tienes (?:un|una|el|la)\b", re.IGNORECASE),
     "artefacto de chat: empieza por la primera afirmación útil"),
    ("P22", "aviso", re.compile(
        r",\s*(?:logrando|garantizando|permitiendo|consiguiendo|poniendo de manifiesto"
        r"|reflejando|destacando|simbolizando)\b", re.IGNORECASE),
     "gerundio de consecuencia: punto y frase nueva"),
    ("P24", "aviso", re.compile(
        r"\bcabe (?:destacar|señalar|mencionar|resaltar|indicar)\b"
        r"|\bes importante (?:señalar|tener en cuenta|recordar|destacar)\b"
        r"|\ben el mundo actual\b|\ben la era digital\b|\ben el panorama actual\b"
        r"|\ba día de hoy\b|\bcon esto en mente\b|\bdicho esto\b"
        r"|\ben última instancia\b", re.IGNORECASE),
     "muletilla o fórmula de relleno: suprímela y deja la afirmación"),
    ("P26", "aviso", re.compile(
        r"\ben (?:resumen|conclusión|definitiva|síntesis)\b"
        r"|\bel futuro es prometedor\b|\btiempos apasionantes\b", re.IGNORECASE),
     "conclusión genérica: termina con un dato o una consecuencia"),
    ("P27", "aviso", re.compile(
        r"\bvamos a (?:sumergirnos|adentrarnos|ver|explorar)\b"
        r"|\ba continuación,? (?:veremos|vemos|analizamos)\b|\bsin más dilación\b"
        r"|\bveamos a continuación\b", re.IGNORECASE),
     "signposting: anuncia en lugar de hacer"),
    ("P29", "aviso", re.compile(
        r"\bla verdadera pregunta es\b|\ben el fondo\b"
        r"|\blo que de verdad importa\b|\bel quid de la cuestión\b", re.IGNORECASE),
     "tropo de autoridad: haz la pregunta o la afirmación directamente"),
]

CONNECTORS = (
    "además", "asimismo", "por consiguiente", "no obstante", "sin embargo",
    "por otro lado", "en definitiva", "por último", "en primer lugar",
)
CONNECTOR_RE = re.compile(
    r"^\s*(?:" + "|".join(re.escape(c) for c in CONNECTORS) + r")\b[,\s]", re.IGNORECASE
)
DASH_RE = re.compile(r"\u2014")


def prose_without_code(text):
    """Devuelve las líneas de prosa con código, frontmatter y URLs enmascarados."""
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() in ("---", "..."):
                start = index + 1
                break
    out, fence = [], None
    for index, line in enumerate(lines):
        match = FENCE_RE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)[0] * 3
                out.append("")
                continue
            masked = INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), line)
            masked = URL_RE.sub(lambda m: " " * len(m.group(0)), masked)
            out.append(masked)
        else:
            if match and match.group(1).startswith(fence):
                fence = None
            out.append("")
    return out[start:], start


def check_line_rules(lines, findings):
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        for rule_id, severity, regex, message in RULES:
            match = regex.search(line)
            if match:
                findings.append({
                    "line": number, "rule": rule_id, "severity": severity,
                    "message": message, "excerpt": match.group(0).strip(),
                })

        if missing_opening(line, "?", "¿"):
            findings.append({
                "line": number, "rule": "T04", "severity": "error",
                "message": "falta el signo de apertura ¿",
                "excerpt": line.strip()[:80],
            })
        if missing_opening(line, "!", "¡"):
            findings.append({
                "line": number, "rule": "T05", "severity": "error",
                "message": "falta el signo de apertura ¡",
                "excerpt": line.strip()[:80],
            })


def missing_opening(line, closing, opening):
    """Hay un cierre al que no precede ninguna apertura en la misma línea."""
    for index, char in enumerate(line):
        if char != closing:
            continue
        if closing == "!" and index and line[index - 1] in "[(":
            continue  # imagen o enlace de Markdown
        if opening not in line[:index]:
            return True
    return False


def check_heading_case(lines, findings):
    for number, line in enumerate(lines, start=1):
        match = HEADING_RE.match(line)
        if not match:
            continue
        words = [w for w in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", match.group(1))]
        if len(words) < 3:
            continue
        inner = words[1:]
        capitalized = [
            w for w in inner
            if w[0].isupper() and w[1:].islower()
        ]
        if len(capitalized) >= 2:
            findings.append({
                "line": number, "rule": "P17", "severity": "aviso",
                "message": "posible title case en el titular: mayúscula solo en la primera palabra",
                "excerpt": match.group(1).strip()[:80],
            })


def check_dash_density(lines, findings):
    text = "\n".join(lines)
    words = len(re.findall(r"\w+", text))
    dashes = len(DASH_RE.findall(text))
    if dashes > 3 and dashes > max(3, words // 100):
        for number, line in enumerate(lines, start=1):
            if DASH_RE.search(line):
                findings.append({
                    "line": number, "rule": "P14", "severity": "aviso",
                    "message": f"raya sobreusada: {dashes} en unas {words} palabras",
                    "excerpt": line.strip()[:80],
                })
                break


def check_paragraphs(lines, findings):
    text = "\n".join(lines)
    paragraphs, offset = [], 0
    for raw in PARAGRAPH_SPLIT_RE.split(text):
        start = text.count("\n", 0, offset) + 1
        offset += len(raw) + 2
        body = raw.strip()
        if body:
            paragraphs.append((start, body))

    run, previous = 0, None
    for start, body in paragraphs:
        first = body.splitlines()[0]
        if HEADING_RE.match(first):
            previous = None
            continue
        connector = CONNECTOR_RE.match(first)
        key = connector.group(0).strip().lower() if connector else None
        if key and key == previous:
            run += 1
        else:
            run = 1 if key else 0
        previous = key
        if run == 3:
            findings.append({
                "line": start, "rule": "P33", "severity": "aviso",
                "message": f"conector formulaico «{key}» en párrafos consecutivos",
                "excerpt": first.strip()[:80],
            })

        sentences = [s.strip() for s in SENTENCE_RE.findall(body) if len(s.split()) > 1]
        if len(sentences) >= 4:
            lengths = [len(s.split()) for s in sentences]
            if statistics.pstdev(lengths) < 3.0:
                findings.append({
                    "line": start, "rule": "P32", "severity": "aviso",
                    "message": "ritmo uniforme: varía la longitud de frase",
                    "excerpt": f"{len(sentences)} frases de {min(lengths)}–{max(lengths)} palabras",
                })


def check(text):
    lines, _ = prose_without_code(text)
    findings = []
    check_line_rules(lines, findings)
    check_heading_case(lines, findings)
    check_dash_density(lines, findings)
    check_paragraphs(lines, findings)
    findings.sort(key=lambda f: (f["line"], f["rule"]))
    return findings, stats(lines)


def stats(lines):
    text = "\n".join(lines)
    words = len(re.findall(r"\w+", text))
    sentences = len([s for s in SENTENCE_RE.findall(text) if len(s.split()) > 1])
    paragraphs = len([p for p in PARAGRAPH_SPLIT_RE.split(text) if p.strip()])
    return {"words": words, "sentences": sentences, "paragraphs": paragraphs}


def report(path, findings, summary, as_json):
    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = len(findings) - errors
    if as_json:
        print(json.dumps({
            "file": str(path), "findings": findings,
            "counts": {"errors": errors, "warnings": warnings},
            "stats": summary,
        }, ensure_ascii=False, indent=2))
        return
    print(f"{path}: {len(findings)} {'hallazgo' if len(findings) == 1 else 'hallazgos'} "
          f"({errors} {'error' if errors == 1 else 'errores'}, "
          f"{warnings} {'aviso' if warnings == 1 else 'avisos'})")
    print(f"  {summary['words']} palabras, {summary['sentences']} frases, "
          f"{summary['paragraphs']} párrafos")
    for finding in findings:
        print(f"  {finding['severity']:<6} L{finding['line']:<4} {finding['rule']}  "
              f"{finding['message']}  «{finding['excerpt']}»")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Comprueba tipografía española y tics de escritura de IA",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser("check", help="analiza un fichero o la entrada estándar")
    check_parser.add_argument("path", help="fichero de texto, o - para la entrada estándar")
    check_parser.add_argument("--json", action="store_true", help="salida JSON")
    check_parser.add_argument(
        "--strict", action="store_true", help="los avisos también hacen fallar la puerta",
    )
    args = parser.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    if args.path == "-":
        text, name = sys.stdin.read(), "<stdin>"
    else:
        name = args.path
        try:
            text = Path(args.path).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: no se puede leer {args.path}: {exc}", file=sys.stderr)
            return 2

    try:
        findings, summary = check(text)
    except Exception as exc:  # noqa: BLE001 - la puerta nunca debe caer con una traza
        print(f"ERROR: fallo al analizar {name}: {exc}", file=sys.stderr)
        return 2

    report(name, findings, summary, args.json)
    failing = [f for f in findings if args.strict or f["severity"] == "error"]
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
