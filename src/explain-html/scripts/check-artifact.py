#!/usr/bin/env python3
"""Verifica la autocontención de un artefacto HTML de explain-html.

Uso: python3 check-artifact.py <ruta.html> [ruta.html ...]

Un artefacto es autocontenido cuando funciona igual abierto por file:// que
servido: todo CSS, JS y SVG en línea, toda imagen como data: URI o SVG
incrustado, sin CDN, sin fuentes remotas y sin ficheros compañeros. El script
comprueba eso, que el artefacto tenga título y que su bloque de procedencia
—prompt, fecha, familia y fuentes— esté completo; no valida la calidad del
contenido ni la accesibilidad, que son criterio del agente, no del script.
"""
import re
import sys
from pathlib import Path

import artifact_meta

# src= y href= de recursos cargados: cualquier valor que no sea inline o
# ancla interno rompe la autocontención. Los <a href> de texto sí pueden
# enlazar a páginas externas: son contenido, no recursos.
LOADING_TAGS = re.compile(
    r"<(?P<tag>script|link|img|source|track|iframe|embed|object|use|image)\b[^>]*?>",
    re.IGNORECASE,
)
SRC_HREF = re.compile(r'''\b(?:src|href)\s*=\s*["'](?P<val>[^"']*)["']''', re.IGNORECASE)
CSS_URL = re.compile(r'''url\(\s*["']?(?P<val>[^"')]+)["']?\s*\)''', re.IGNORECASE)
CSS_IMPORT = re.compile(r'''@import\s+(?:url\(\s*)?["']?(?P<val>[^"'();\s]+)''', re.IGNORECASE)
TITLE = re.compile(r"<title>\s*(?P<val>[^<]+?)\s*</title>", re.IGNORECASE)

INLINE_OK = re.compile(r"^(data:|#|$)", re.IGNORECASE)


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def check_artifact(path: Path) -> list[str]:
    errors = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"{path}: el fichero no existe. Genera el artefacto antes de verificarlo."]
    except UnicodeDecodeError as exc:
        return [f"{path}: no es texto UTF-8 ({exc}); un HTML de texto plano no debería fallar aquí."]

    if path.suffix.lower() != ".html":
        errors.append(f"{path}: la extensión no es .html; los artefactos son un único .html.")

    title = TITLE.search(text)
    if not title:
        errors.append(f"{path}: falta <title>. Un artefacto sin título no se encuentra ni se nombra en el cierre.")
    elif "ASUNTO DEL ARTEFACTO" in title.group("val"):
        errors.append(f"{path}: <title> conserva el marcador de la plantilla; pon el asunto concreto.")

    meta = artifact_meta.find(text)
    if meta is None:
        errors.append(f"{path}: {artifact_meta.MISSING}")
    else:
        _, problems = artifact_meta.load(meta)
        for problem in problems:
            errors.append(f"{path}:{line_of(text, meta.start())}: {problem}")

    for tag in LOADING_TAGS.finditer(text):
        tag_text = tag.group(0)
        tag_name = tag.group("tag").lower()
        for attr in SRC_HREF.finditer(tag_text):
            value = attr.group("val").strip()
            if INLINE_OK.match(value):
                continue
            errors.append(
                f"{path}:{line_of(text, tag.start())}: <{tag_name}> carga «{value}», que no va en línea. "
                f"Incrusta el recurso (CSS/JS en línea, imagen data: o SVG) o elimínalo."
            )

    for rule in (CSS_URL, CSS_IMPORT):
        for match in rule.finditer(text):
            value = match.group("val").strip()
            if INLINE_OK.match(value):
                continue
            errors.append(
                f"{path}:{line_of(text, match.start())}: CSS carga «{value}» con {match.group(0).split('(')[0].strip()}. "
                f"Incrusta el recurso en el propio fichero o elimínalo."
            )

    return errors


def main() -> int:
    args = sys.argv[1:]
    if not args or any(a in ("-h", "--help") for a in args):
        print(__doc__.strip())
        return 0 if args else 2

    all_errors: list[str] = []
    checked = 0
    for raw in args:
        path = Path(raw)
        errors = check_artifact(path)
        checked += 1 if not any("no existe" in e for e in errors) else 0
        all_errors.extend(errors)

    if all_errors:
        print("El artefacto no pasa la verificación; corrige antes de abrirlo en el navegador:")
        for error in all_errors:
            print(f"  - {error}")
        return 1

    print(f"OK: {checked} artefacto(s) autocontenido(s), con título y procedencia completa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
