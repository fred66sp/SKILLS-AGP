#!/usr/bin/env python3
"""Renderiza un artefacto rutinario desde un JSON compacto y validado.

Uso: python3 render-quick.py <esquema.json> <salida.html>

Es el atajo de explain-html para artefactos que solo combinan texto: no
sustituye la generación a medida. Si el JSON no valida, imprime los problemas
y sale 1; el contrato indica entonces caer a la generación normal.

Esquema (todas las claves de cada objeto están acotadas; una clave
desconocida es un error):

{
  "titulo": "Estado de la semana 45",              // obligatorio
  "lead": "Una línea con la pregunta y la fecha.", // opcional
  "familia": "informe",                            // obligatorio, un slug
  "procedencia": {                                 // obligatorio
    "prompt": "Pásame el estado de la semana",     // obligatorio
    "fecha": "2026-11-08",                         // obligatorio, AAAA-MM-DD
    "fuentes": ["git log", "src/x.py:12"]          // obligatorio, no vacío
  },
  "secciones": [                                   // obligatorio, no vacío
    {
      "titulo": "Resumen",                         // obligatorio
      "bloques": [                                 // obligatorio, no vacío
        {"tipo": "parrafo", "texto": "..."},
        {"tipo": "lista", "items": ["...", "..."]},
        {"tipo": "tabla", "cabeceras": ["A", "B"],
         "filas": [["a1", "b1"], ["a2", "b2"]]},
        {"tipo": "cifra", "valor": "12", "etiqueta": "tareas abiertas"},
        {"tipo": "nota", "texto": "..."}
      ]
    }
  ],
  "desconocidos": ["Lo que el material no permitió verificar"] // opcional
}

Familias: exploracion, explicador, informe, diagrama, prototipo,
cuestionario, editor, presentacion. La salida es determinista: el mismo JSON
produce el mismo HTML, y la fecha sale del propio JSON, no del reloj.
"""
import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

import artifact_meta

TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "plantilla-artefacto.html"
STYLE_RE = re.compile(r"<style>(?P<css>.*?)</style>", re.DOTALL)

EXTRA_STYLE = """
.grid-kpi { display: grid; grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr)); gap: .75rem; margin: 1.5rem 0; }
.kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1rem; }
.kpi strong { display: block; font-size: 1.75rem; line-height: 1.2; color: var(--accent); }
.kpi span { color: var(--text-dim); font-size: .875rem; }
.note { background: var(--surface); border-left: 3px solid var(--accent); padding: .75rem 1rem; margin: 1.5rem 0; }
.note p { margin: 0; }
.table-wrap { overflow-x: auto; }
"""

TOP_KEYS = {"titulo", "lead", "familia", "procedencia", "secciones", "desconocidos"}
META_KEYS = {"prompt", "fecha", "fuentes"}
SECTION_KEYS = {"titulo", "bloques"}
BLOCK_KEYS = {
    "parrafo": {"tipo", "texto"},
    "lista": {"tipo", "items"},
    "tabla": {"tipo", "cabeceras", "filas"},
    "cifra": {"tipo", "valor", "etiqueta"},
    "nota": {"tipo", "texto"},
}


def text_value(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(data) -> list[str]:
    problems: list[str] = []
    if not isinstance(data, dict):
        return ["el JSON debe ser un objeto con las claves titulo, familia, procedencia y secciones."]

    for key in sorted(set(data) - TOP_KEYS):
        problems.append(f"clave desconocida «{key}»; las admitidas son: {', '.join(sorted(TOP_KEYS))}.")
    if not text_value(data.get("titulo")):
        problems.append("«titulo» vacío: escribe el asunto concreto del artefacto.")
    if "lead" in data and not text_value(data["lead"]):
        problems.append("«lead» vacío: escríbelo en una línea o elimínalo.")
    if data.get("familia") not in artifact_meta.FAMILIES:
        problems.append(
            "«familia» vacía o no válida; usa uno de: "
            f"{', '.join(artifact_meta.FAMILIES)}."
        )

    meta = data.get("procedencia")
    if not isinstance(meta, dict):
        problems.append("«procedencia» ausente: incluye prompt, fecha y fuentes.")
    else:
        for key in sorted(set(meta) - META_KEYS):
            problems.append(
                f"procedencia: clave desconocida «{key}»; las admitidas son: "
                f"{', '.join(sorted(META_KEYS))}."
            )
        if not text_value(meta.get("prompt")):
            problems.append("procedencia.prompt vacío: escribe el encargo que originó el artefacto.")
        fecha = meta.get("fecha")
        try:
            valid_date = isinstance(fecha, str) and bool(artifact_meta.DATE_RE.match(fecha)) and bool(date.fromisoformat(fecha))
        except ValueError:
            valid_date = False
        if not valid_date:
            problems.append("procedencia.fecha vacía o no válida: usa AAAA-MM-DD, por ejemplo 2026-11-08.")
        fuentes = meta.get("fuentes")
        if (
            not isinstance(fuentes, list)
            or not fuentes
            or not all(text_value(item) for item in fuentes)
        ):
            problems.append("procedencia.fuentes vacía: lista al menos una fuente, por ejemplo [\"git log\"].")

    sections = data.get("secciones")
    if not isinstance(sections, list) or not sections:
        problems.append("«secciones» vacía: incluye al menos una sección con bloques.")
    else:
        for index, section in enumerate(sections):
            problems.extend(validate_section(section, f"secciones[{index}]"))

    if "desconocidos" in data:
        unknown = data["desconocidos"]
        if not isinstance(unknown, list) or not unknown or not all(text_value(item) for item in unknown):
            problems.append("«desconocidos» vacío: escríbelo como lista de cadenas no vacías o elimínalo.")
    return problems


def validate_section(section, path: str) -> list[str]:
    problems: list[str] = []
    if not isinstance(section, dict):
        return [f"{path}: debe ser un objeto con titulo y bloques."]
    for key in sorted(set(section) - SECTION_KEYS):
        problems.append(f"{path}: clave desconocida «{key}»; las admitidas son: titulo, bloques.")
    if not text_value(section.get("titulo")):
        problems.append(f"{path}.titulo vacío: escribe el título de la sección.")
    blocks = section.get("bloques")
    if not isinstance(blocks, list) or not blocks:
        problems.append(f"{path}.bloques vacío: incluye al menos un bloque.")
        return problems
    for index, block in enumerate(blocks):
        problems.extend(validate_block(block, f"{path}.bloques[{index}]"))
    return problems


def validate_block(block, path: str) -> list[str]:
    if not isinstance(block, dict):
        return [f"{path}: debe ser un objeto con «tipo» y sus campos."]
    kind = block.get("tipo")
    if kind not in BLOCK_KEYS:
        return [
            f"{path}: «tipo» desconocido ({kind!r}); usa uno de: "
            f"{', '.join(BLOCK_KEYS)}."
        ]
    problems = [
        f"{path}: clave desconocida «{key}» para el bloque {kind}; las admitidas son: "
        f"{', '.join(sorted(BLOCK_KEYS[kind]))}."
        for key in sorted(set(block) - BLOCK_KEYS[kind])
    ]
    if kind in ("parrafo", "nota"):
        if not text_value(block.get("texto")):
            problems.append(f"{path}.texto vacío: escribe el texto del bloque {kind}.")
    elif kind == "lista":
        items = block.get("items")
        if not isinstance(items, list) or not items or not all(text_value(item) for item in items):
            problems.append(f"{path}.items vacío: lista al menos un elemento de texto.")
    elif kind == "cifra":
        value = block.get("valor")
        if isinstance(value, bool) or not isinstance(value, (str, int, float)) or not str(value).strip():
            problems.append(f"{path}.valor vacío: escribe el número o el texto de la cifra.")
        if not text_value(block.get("etiqueta")):
            problems.append(f"{path}.etiqueta vacía: explica qué mide la cifra.")
    elif kind == "tabla":
        headers = block.get("cabeceras")
        valid_headers = (
            isinstance(headers, list) and bool(headers)
            and all(text_value(item) for item in headers)
        )
        if not valid_headers:
            problems.append(f"{path}.cabeceras vacía: lista al menos un encabezado de texto.")
        rows = block.get("filas")
        if not isinstance(rows, list) or not rows:
            problems.append(f"{path}.filas vacía: incluye al menos una fila.")
        elif valid_headers:
            for index, row in enumerate(rows):
                if not isinstance(row, list) or len(row) != len(headers):
                    problems.append(
                        f"{path}.filas[{index}]: debe tener {len(headers)} celdas, "
                        f"como cabeceras."
                    )
                elif not all(text_value(cell) for cell in row):
                    problems.append(f"{path}.filas[{index}]: cada celda debe ser texto no vacío.")
    return problems


def esc(value) -> str:
    return html.escape(str(value))


def render_block(block) -> str:
    kind = block["tipo"]
    if kind in ("parrafo", "nota"):
        body = f"<p>{esc(block['texto'])}</p>"
        return body if kind == "parrafo" else f'<div class="note" role="note">{body}</div>'
    if kind == "lista":
        items = "\n".join(f"      <li>{esc(item)}</li>" for item in block["items"])
        return f"    <ul>\n{items}\n    </ul>"
    if kind == "cifra":
        return (
            '    <div class="grid-kpi"><div class="kpi">'
            f"<strong>{esc(block['valor'])}</strong><span>{esc(block['etiqueta'])}</span>"
            "</div></div>"
        )
    headers = "".join(f"<th>{esc(item)}</th>" for item in block["cabeceras"])
    rows = "\n".join(
        "        <tr>" + "".join(f"<td>{esc(cell)}</td>" for cell in row) + "</tr>"
        for row in block["filas"]
    )
    return (
        '    <div class="table-wrap"><table>\n'
        f"      <thead><tr>{headers}</tr></thead>\n"
        f"      <tbody>\n{rows}\n      </tbody>\n"
        "    </table></div>"
    )


def render(data: dict, css: str) -> str:
    meta = {
        "prompt": data["procedencia"]["prompt"],
        "fecha": data["procedencia"]["fecha"],
        "familia": data["familia"],
        "fuentes": data["procedencia"]["fuentes"],
    }
    lead = f'\n  <p class="lead">{esc(data["lead"])}</p>' if data.get("lead") else ""
    sections = []
    for index, section in enumerate(data["secciones"], start=1):
        blocks = "\n".join(render_block(block) for block in section["bloques"])
        sections.append(
            f'  <section id="seccion-{index}">\n'
            f"    <h2>{esc(section['titulo'])}</h2>\n{blocks}\n"
            "  </section>"
        )
    if data.get("desconocidos"):
        items = "\n".join(f"      <li>{esc(item)}</li>" for item in data["desconocidos"])
        sections.append(
            '  <section id="desconocidos">\n'
            "    <h2>Desconocidos</h2>\n"
            f"    <ul>\n{items}\n    </ul>\n"
            "  </section>"
        )
    metadata = json.dumps(meta, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(data["titulo"])}</title>
<style>{css}{EXTRA_STYLE}</style>
</head>
<body>
<!-- procedencia: {metadata} -->
<header>
  <h1>{esc(data["titulo"])}</h1>{lead}
</header>
<main>
{chr(10).join(sections)}
</main>
</body>
</html>
"""


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Renderiza un artefacto explain-html rutinario desde un JSON compacto"
    )
    parser.add_argument("esquema", help="fichero JSON con el esquema del artefacto")
    parser.add_argument("salida", help="ruta del .html de salida")
    args = parser.parse_args(argv)

    try:
        data = json.loads(Path(args.esquema).read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"ERROR: no se pudo leer {args.esquema}: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERROR: {args.esquema} no es JSON válido ({exc.msg}, línea {exc.lineno}).",
              file=sys.stderr)
        return 1

    problems = validate(data)
    if problems:
        print("El JSON no valida; corrige o cae a la generación a medida normal:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    try:
        css = STYLE_RE.search(TEMPLATE.read_text(encoding="utf-8")).group("css")
    except (OSError, AttributeError) as exc:
        print(f"ERROR: no se pudo leer el estilo de {TEMPLATE}: {exc}", file=sys.stderr)
        return 2

    target = Path(args.salida)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(data, css), encoding="utf-8", newline="\n")
    except OSError as exc:
        print(f"ERROR: no se pudo escribir {target}: {exc}", file=sys.stderr)
        return 1

    print(f"OK: {target} desde {args.esquema}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
