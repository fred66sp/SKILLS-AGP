#!/usr/bin/env python3
"""Inventario determinista de documentación Markdown de un proyecto.

Uso:
    python3 scripts/doc-inventory.py --root <directorio> [--glob "*.md"] [--json]
                                     [--exclude-dir <nombre>]...

Salida por stdout: tabla con ruta relativa, líneas, título H1 y número de enlaces
relativos de cada documento, seguida de los hallazgos detectados:
enlaces relativos rotos, documentos sin H1, documentos sin contenido,
encabezados H2 repetidos entre documentos (señal de duplicación) y estado de la
entrega escrito como documentación.

La clase de estado de la entrega solo mira la prosa: omite los bloques de código
(``` y ~~~), las citas entre comillas anguladas (el ejemplo que la propia regla
enumera no es un hallazgo) y los documentos que son registro de trabajo, que por
convención llevan un encabezado H2 llamado `Log`.

Códigos de salida:
    0  inventario completo sin hallazgos
    3  inventario completo con hallazgos
    2  error de uso: la ruta no existe, no es un directorio o el patrón no es válido
"""

import argparse
import fnmatch
import json
import os
import re
import sys
import unicodedata
from urllib.parse import unquote

DEFAULT_EXCLUDES = (
    ".git", "node_modules", "vendor", "dist", "build", "target",
    "__pycache__", ".venv", "venv", ".next", ".nuxt", ".output",
)

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
QUOTED_RE = re.compile(r"«[^»]*»")
NARRATION_RE = re.compile(
    r"\bse corrigió\b|\bquedó reportado\b|\bantes dec[íi]a\b|"
    r"\bpasa de\b|\bdejó de\b",
    re.IGNORECASE,
)
RECOUNT_RE = re.compile(r"\b\d[\d.]*\s?(?:bytes|KB|MB|secciones)\b")


def prose_lines(text):
    """Devuelve (número de línea, texto) fuera del frontmatter y de los bloques de código."""
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() in ("---", "..."):
                start = index + 1
                break
    kept, open_fence = [], None
    for index in range(start, len(lines)):
        line = lines[index]
        match = FENCE_RE.match(line)
        if open_fence is None:
            if match:
                open_fence = match.group(1)[0] * 3
                continue
            kept.append((index + 1, line))
        elif match and match.group(1).startswith(open_fence):
            open_fence = None
    return kept


def normalize(value):
    text = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"\s+", " ", text).strip()


def analyze(path, root):
    with open(path, encoding="utf-8", errors="replace") as handle:
        raw = handle.read()
    prose = prose_lines(raw)
    lines = [line for _, line in prose]
    title, headings, links = None, [], []
    for line in lines:
        heading = HEADING_RE.match(line)
        if heading:
            level, text = len(heading.group(1)), heading.group(2).strip()
            if level == 1 and title is None:
                title = text
            elif level == 2:
                headings.append(text)
            continue
        for target in LINK_RE.findall(INLINE_CODE_RE.sub("", line)):
            links.append(resolve(target, path, root))
    has_content = any(line.strip() for line in lines)
    delivery = []
    if "log" not in {normalize(heading) for heading in headings}:
        for number, line in prose:
            plain = QUOTED_RE.sub("", line)
            for family, pattern in (("narracion", NARRATION_RE), ("recuento", RECOUNT_RE)):
                found = pattern.search(plain)
                if found:
                    delivery.append({
                        "line": number,
                        "family": family,
                        "matched": found.group(0),
                        "excerpt": plain.strip()[:80],
                    })
    return {
        "path": os.path.relpath(path, root).replace(os.sep, "/"),
        "delivery": delivery,
        "lines": raw.count("\n") + (0 if raw.endswith("\n") or not raw else 1),
        "title": title,
        "headings": headings,
        "links": [target for target, _, _ in links],
        "broken": [(target, resolved) for target, resolved, exists in links if not exists],
        "has_content": has_content,
    }


def resolve(target, source, root):
    """Resuelve un enlace relativo. Devuelve (original, ruta resuelta, existe)."""
    if not target or target.startswith("#") or target.startswith("//") or SCHEME_RE.match(target):
        return (target, None, True)
    path = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not path:
        return (target, None, True)
    if path.startswith("/"):
        resolved = os.path.join(root, path.lstrip("/"))
    else:
        resolved = os.path.join(os.path.dirname(source), path)
    return (target, os.path.normpath(resolved), os.path.exists(os.path.normpath(resolved)))


def collect(root, pattern, excludes):
    pattern = pattern.lower()
    documents = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            name for name in dirnames if name.lower() not in excludes
        )
        for name in sorted(filenames):
            if fnmatch.fnmatch(name.lower(), pattern):
                documents.append(os.path.join(dirpath, name))
    return documents


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Inventario determinista de documentación Markdown.",
        add_help=True,
    )
    parser.add_argument("--root", required=True, help="Directorio raíz a inventariar.")
    parser.add_argument("--glob", default="*.md", help="Patrón de nombre de archivo. Por defecto: *.md")
    parser.add_argument("--json", action="store_true", help="Salida JSON en lugar de tabla Markdown.")
    parser.add_argument(
        "--exclude-dir", action="append", default=None,
        help="Directorio a excluir, repetible. Sustituye a la lista por defecto.",
    )
    args = parser.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"ERROR: la ruta no existe o no es un directorio: {args.root}", file=sys.stderr)
        return 2
    if "/" in args.glob or "\\" in args.glob:
        print("ERROR: --glob acepta solo un patrón de nombre de archivo, sin separadores de ruta.", file=sys.stderr)
        return 2

    excludes = {item.lower() for item in (args.exclude_dir or DEFAULT_EXCLUDES)}
    results = [analyze(path, root) for path in collect(root, args.glob, excludes)]

    h2_index = {}
    for document in results:
        for heading in set(normalize(item) for item in document["headings"]):
            h2_index.setdefault(heading, set()).add(document["path"])
    duplicates = {key: sorted(value) for key, value in h2_index.items() if len(value) > 1}

    findings = {
        "broken_links": [
            {"document": document["path"], "target": target, "resolved": resolved}
            for document in results for target, resolved in document["broken"]
        ],
        "missing_h1": [document["path"] for document in results if document["title"] is None],
        "empty_documents": [document["path"] for document in results if not document["has_content"]],
        "duplicate_h2": duplicates,
        "delivery_state": [
            {"document": document["path"], **item}
            for document in results for item in document["delivery"]
        ],
        "documents_reviewed": len(results),
    }

    has_findings = bool(
        findings["broken_links"] or findings["missing_h1"]
        or findings["empty_documents"] or findings["duplicate_h2"]
        or findings["delivery_state"]
    )

    if args.json:
        payload = {
            "root": root.replace(os.sep, "/"),
            "glob": args.glob,
            "documents": [
                {key: document[key] for key in ("path", "lines", "title", "links", "delivery")}
                for document in results
            ],
            "findings": findings,
            "exit_code": 3 if has_findings else 0,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 3 if has_findings else 0

    if not results:
        print(f"Sin documentos que coincidan con '{args.glob}' en {root}.")
        return 0

    print(f"Inventario de {len(results)} documentos en {root.replace(os.sep, '/')}\n")
    print("| Documento | Líneas | Título H1 | Enlaces relativos |")
    print("|---|---|---|---|")
    for document in results:
        print(f"| {document['path']} | {document['lines']} | {document['title'] or '—'} | {len(document['links'])} |")

    print("\nHallazgos")
    if not has_findings:
        print("Ninguno.")
        return 0
    for item in findings["broken_links"]:
        print(f"- enlace roto: {item['document']} -> {item['target']}")
    for path in findings["missing_h1"]:
        print(f"- sin H1: {path}")
    for path in findings["empty_documents"]:
        print(f"- sin contenido: {path}")
    for heading, paths in sorted(duplicates.items()):
        print(f"- encabezado repetido: \"{heading}\" en {', '.join(paths)}")
    for item in findings["delivery_state"]:
        print(
            f"- estado de la entrega: {item['document']}:{item['line']} · {item['family']} · "
            f"[{item['matched']}] {item['excerpt']}"
        )
    return 3


if __name__ == "__main__":
    sys.exit(main())
