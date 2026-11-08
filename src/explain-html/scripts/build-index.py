#!/usr/bin/env python3
"""Regenera el índice de `.explanations/` con la lista de artefactos.

Uso: python3 build-index.py [directorio] [--quiet]

`directorio` por defecto es `.explanations` del proyecto actual. El script lee
el `<title>` de cada `.html` de primer nivel, su bloque de procedencia si lo
tiene (fecha y familia) y, si no, la fecha de modificación del fichero.
Escribe `index.html` en ese mismo directorio con enlaces relativos, sin
dependencias y funcional por file://. No toca los artefactos ni nada fuera del
directorio. Se ejecuta tras generar cada artefacto nuevo.
"""
import argparse
import html
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

import artifact_meta

TITLE = re.compile(r"<title>\s*(?P<val>[^<]+?)\s*</title>", re.IGNORECASE)
INDEX = "index.html"

STYLE = """
:root {
  --bg: #fafaf9; --surface: #ffffff; --border: #e2e1de; --text: #1c1b1a;
  --text-dim: #5d5b58; --accent: #0f766e;
}
@media (prefers-color-scheme: dark) {
  :root { --bg: #141413; --surface: #1e1e1d; --border: #333231;
    --text: #ecebea; --text-dim: #9d9b98; --accent: #2dd4bf; }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
  font: 400 1rem/1.6 system-ui, "Segoe UI", sans-serif; }
header { padding: 2.5rem 1.5rem 1.5rem; border-bottom: 1px solid var(--border); }
h1 { font-size: 1.75rem; line-height: 1.25; margin: 0 0 .5rem; text-wrap: balance; }
.lead { color: var(--text-dim); margin: 0; }
main { padding: 1.5rem; max-width: 72rem; }
ul { list-style: none; margin: 0; padding: 0; display: grid; gap: .75rem; }
li { background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; padding: .75rem 1rem; }
li a { color: var(--accent); font-weight: 600; text-decoration: none; }
li a:hover, li a:focus-visible { text-decoration: underline; }
.meta { display: block; color: var(--text-dim); font-size: .875rem; margin-top: .25rem; }
.empty { color: var(--text-dim); }
"""


def artifact_row(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    title = TITLE.search(text)
    name = html.escape(title.group("val").strip()) if title else html.escape(path.stem)

    fecha = fecha_archivo(path)
    familia = ""
    meta = artifact_meta.find(text)
    if meta is not None:
        data, _ = artifact_meta.load(meta)
        if data:
            if isinstance(data.get("fecha"), str) and artifact_meta.DATE_RE.match(data["fecha"]):
                fecha = data["fecha"]
            if data.get("familia") in artifact_meta.FAMILIES:
                familia = artifact_meta.FAMILIES[data["familia"]]
    return {"file": path.name, "title": name, "fecha": fecha, "familia": familia}


def fecha_archivo(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()


def render(rows: list[dict]) -> str:
    hoy = date.today().isoformat()
    if rows:
        items = "\n".join(
            f'  <li><a href="{html.escape(row["file"])}">{row["title"]}</a>'
            f'<span class="meta">{row["fecha"]}'
            f'{" · " + row["familia"] if row["familia"] else ""}</span></li>'
            for row in rows
        )
        body = f'<ul>\n{items}\n</ul>'
        fuentes = [row["file"] for row in rows]
    else:
        body = '<p class="empty">Todavía no hay artefactos en este directorio.</p>'
        fuentes = ["carpeta sin artefactos"]

    meta = {
        "prompt": "Índice generado automáticamente por build-index.py",
        "fecha": hoy,
        "familia": "informe",
        "fuentes": fuentes,
    }
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Artefactos de .explanations</title>
<style>{STYLE}</style>
</head>
<body>
<!-- procedencia: {json_compact(meta)} -->
<header>
  <h1>Artefactos de .explanations</h1>
  <p class="lead">{len(rows)} artefacto(s) · índice regenerado el {hoy}.</p>
</header>
<main>
{body}
</main>
</body>
</html>
"""


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

    paths = sorted(p for p in directory.glob("*.html") if p.is_file() and p.name != INDEX)
    try:
        rows = [artifact_row(path) for path in paths]
    except (OSError, UnicodeDecodeError) as exc:
        print(f"ERROR: no se pudo leer un artefacto: {exc}", file=sys.stderr)
        return 1

    rows.sort(key=lambda row: (row["fecha"], row["title"].lower()), reverse=True)
    target = directory / INDEX
    try:
        target.write_text(render(rows), encoding="utf-8", newline="\n")
    except OSError as exc:
        print(f"ERROR: no se pudo escribir {target}: {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"OK: {target} con {len(rows)} artefacto(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
