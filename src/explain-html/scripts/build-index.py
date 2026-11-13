#!/usr/bin/env python3
"""Regenera el índice de `.explanations/` con la lista de artefactos.

Uso: python3 build-index.py [directorio] [--quiet]

`directorio` por defecto es `.explanations` del proyecto actual. El script lee
el `<title>` de cada `.html` de primer nivel, su bloque de procedencia si lo
tiene (fecha, familia y `enlaces` opcionales) y, si no, la fecha de
modificación del fichero. El HTML sale de `assets/plantilla-indice.html`: el
script sustituye sus marcadores por los artefactos, los recuentos, la fecha de
regeneración y el nombre del proyecto en el titular (la carpeta que contiene a
`.explanations`). La plantilla trae búsqueda por título, filtro por familia y por
bucles, vista de lista o tarjetas y paginación de 20; sin JavaScript queda la
lista completa y enlazada. Escribe `index.html` en ese mismo directorio, sin
dependencias y funcional por file://. No toca los artefactos ni nada fuera del
directorio. Se ejecuta tras generar cada artefacto nuevo.
"""
import argparse
import html
import json
import re
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import artifact_meta

TITLE = re.compile(r"<title>\s*(?P<val>[^<]+?)\s*</title>", re.IGNORECASE)
INDEX = "index.html"
TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "plantilla-indice.html"
MARKERS = ("@@PROCEDENCIA@@", "@@FECHA@@", "@@CONTEO@@", "@@PROYECTO@@", "@@CHIPS@@", "@@FILAS@@")

# Color de familia: tiñe el icono, el punto de la etiqueta y el borde de la
# tarjeta. Nunca lleva texto encima, así que no sustituye a un rol de contraste.
FAMILY_COLORS = {
    "exploracion": "#2563eb",
    "explicador": "#0891b2",
    "informe": "#4f46e5",
    "diagrama": "#7c3aed",
    "prototipo": "#0f766e",
    "cuestionario": "#b45309",
    "editor": "#be185d",
    "presentacion": "#c2410c",
    "blindspots": "#b91c1c",
    "entrevista": "#15803d",
    "sdd": "#1e40af",
}

ICONO = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M14 3H7a1 1 0 0 0-1 1v16a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V7z"/>'
    '<path d="M14 3v4h4"/></svg>'
)


def artifact_row(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    title = TITLE.search(text)
    name = html.escape(title.group("val").strip()) if title else html.escape(path.stem)

    fecha = fecha_archivo(path)
    slug = ""
    enlaces: list[str] = []
    meta = artifact_meta.find(text)
    if meta is not None:
        data, _ = artifact_meta.load(meta)
        if data:
            if isinstance(data.get("fecha"), str) and artifact_meta.DATE_RE.match(data["fecha"]):
                fecha = data["fecha"]
            if data.get("familia") in artifact_meta.FAMILIES:
                slug = data["familia"]
            declared = data.get(artifact_meta.LINK_FIELD)
            if isinstance(declared, list):
                enlaces = [item for item in declared
                           if isinstance(item, str) and artifact_meta.LINK_RE.match(item)]
    return {"file": path.name, "title": name, "fecha": fecha, "slug": slug,
            "familia": artifact_meta.FAMILIES.get(slug, ""), "enlaces": enlaces}


def fecha_archivo(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()


def fecha_visible(iso: str) -> str:
    """AAAA-MM-DD (dato y orden) a DD-MM-YYYY (lo que se lee)."""
    return f"{iso[8:10]}-{iso[5:7]}-{iso[0:4]}"


def links_line(enlaces: list[str]) -> str:
    """Relación declarada por el artefacto, como enlaces relativos hermanos."""
    if not enlaces:
        return ""
    items = ", ".join(
        f'<a href="{html.escape(link)}">{html.escape(link)}</a>' for link in enlaces
    )
    return f'<span class="bucle">Enlaza: {items}</span>'


def chip(slug: str, label: str, count: int, active: bool) -> str:
    pressed = "true" if active else "false"
    return (f'<button class="chip" type="button" data-filtro-familia="{slug}" '
            f'aria-pressed="{pressed}">{html.escape(label)} '
            f'<span class="n">{count}</span></button>')


def chips(rows: list[dict]) -> str:
    """Filtro de familia: «Todas» y las familias presentes, con su recuento."""
    counts = Counter(row["slug"] for row in rows if row["slug"])
    parts = [chip("", "Todas", len(rows), True)]
    parts.extend(
        chip(slug, label, counts[slug], False)
        for slug, label in artifact_meta.FAMILIES.items() if slug in counts
    )
    return "      " + "\n      ".join(parts)


def fila(row: dict) -> str:
    """Un artefacto, una sola vez: la vista de lista y la de tarjetas lo comparten."""
    total = len(row["enlaces"])
    bucle = ' data-bucle="%d"' % total if total else ""
    color = FAMILY_COLORS.get(row["slug"], "var(--accent)")
    familia = f'<span class="tag">{row["familia"]}</span>' if row["familia"] else ""
    return (
        f'    <li class="artefacto" data-titulo="{row["title"]}" '
        f'data-familia="{row["slug"]}" data-fecha="{row["fecha"]}"{bucle} '
        f'style="--familia:{color}">'
        f'<span class="ico">{ICONO}</span>'
        f'<a class="t" href="{html.escape(row["file"])}">{row["title"]}</a>'
        f'<span class="cab">{familia}<span class="fecha">'
        f'<time datetime="{row["fecha"]}">{fecha_visible(row["fecha"])}</time>'
        f'</span></span>'
        f'{links_line(row["enlaces"])}</li>'
    )


def render(rows: list[dict], plantilla: str, hoy: str, proyecto: str) -> str:
    faltan = [marker for marker in MARKERS if marker not in plantilla]
    if faltan:
        raise ValueError(
            f"{TEMPLATE}: faltan los marcadores {', '.join(faltan)}. "
            "Restaura la plantilla del índice o usa la del repositorio."
        )

    if rows:
        filas = "\n".join(fila(row) for row in rows)
        fuentes = [row["file"] for row in rows]
    else:
        filas = '    <li class="vacio">Todavía no hay artefactos en este directorio.</li>'
        fuentes = ["carpeta sin artefactos"]

    conteo = f"{len(rows)} artefacto" + ("" if len(rows) == 1 else "s")
    meta = {
        "prompt": "Índice generado automáticamente por build-index.py",
        "fecha": hoy,
        "familia": "informe",
        "fuentes": fuentes,
    }
    return (
        plantilla
        .replace("@@PROCEDENCIA@@", json_compact(meta))
        .replace("@@FECHA@@", fecha_visible(hoy))
        .replace("@@CONTEO@@", conteo)
        .replace("@@PROYECTO@@", html.escape(proyecto))
        .replace("@@CHIPS@@", chips(rows))
        .replace("@@FILAS@@", filas)
    )


def json_compact(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(", ", ": "))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Regenera .explanations/index.html con los artefactos de la carpeta"
    )
    parser.add_argument("directorio", nargs="?", default=".explanations",
                        help="carpeta de artefactos (por defecto .explanations)")
    parser.add_argument("--quiet", action="store_true", help="no imprime el resumen")
    args = parser.parse_args(argv)

    directory = Path(args.directorio)
    if not directory.is_dir():
        print(f"ERROR: no es un directorio: {directory}. Pasa la carpeta .explanations del proyecto.",
              file=sys.stderr)
        return 2

    try:
        plantilla = TEMPLATE.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: no se pudo leer la plantilla del índice {TEMPLATE}: {exc}", file=sys.stderr)
        return 1

    paths = sorted(p for p in directory.glob("*.html") if p.is_file() and p.name != INDEX)
    try:
        rows = [artifact_row(path) for path in paths]
    except (OSError, UnicodeDecodeError) as exc:
        print(f"ERROR: no se pudo leer un artefacto: {exc}", file=sys.stderr)
        return 1

    rows.sort(key=lambda row: (row["fecha"], row["title"].lower()), reverse=True)
    proyecto = directory.resolve().parent.name or "el proyecto"
    try:
        text = render(rows, plantilla, date.today().isoformat(), proyecto)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    target = directory / INDEX
    try:
        target.write_text(text, encoding="utf-8", newline="\n")
    except OSError as exc:
        print(f"ERROR: no se pudo escribir {target}: {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"OK: {target} con {len(rows)} artefacto(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
