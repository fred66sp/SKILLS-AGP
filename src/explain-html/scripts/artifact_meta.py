"""Bloque de procedencia que todo artefacto de explain-html lleva dentro.

El bloque es un comentario HTML con un objeto JSON, al inicio del body:

    <!-- procedencia: {"prompt": "...", "fecha": "AAAA-MM-DD",
         "familia": "informe", "fuentes": ["src/x.py:12"]} -->

Sobrevive a cualquier editor y no se renderiza. Lo comparten
check-artifact.py (lo exige), build-index.py (lee fecha y familia) y
render-quick.py (lo genera).
"""
import json
import re
from datetime import date

# Slugs y etiquetas de las ocho familias de artifact-patterns.md.
FAMILIES = {
    "exploracion": "Exploración comparativa",
    "explicador": "Explicador",
    "informe": "Informe",
    "diagrama": "Diagrama",
    "prototipo": "Prototipo",
    "cuestionario": "Cuestionario",
    "editor": "Editor a medida",
    "presentacion": "Presentación",
}

REQUIRED_FIELDS = ("prompt", "fecha", "familia", "fuentes")

META_RE = re.compile(r"<!--\s*procedencia\s*:\s*(?P<json>\{.*?\})\s*-->", re.DOTALL)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

MISSING = (
    "falta el bloque de procedencia dentro del body. Añade este comentario y "
    'rellénalo: <!-- procedencia: {"prompt": "...", "fecha": "AAAA-MM-DD", '
    '"familia": "informe", "fuentes": ["fichero:línea"]} -->'
)


def find(text: str):
    """Devuelve el match del bloque de procedencia, o None."""
    return META_RE.search(text)


def load(match) -> tuple[dict | None, list[str]]:
    """Valida el bloque encontrado. Devuelve (datos, problemas)."""
    try:
        data = json.loads(match.group("json"))
    except json.JSONDecodeError as exc:
        return None, [
            f"el bloque de procedencia no es JSON válido ({exc.msg}, columna {exc.colno}). "
            "Escribe un objeto JSON con comillas dobles y sin comas finales."
        ]
    if not isinstance(data, dict):
        return None, [
            "el bloque de procedencia debe ser un objeto JSON con los campos "
            f"{', '.join(REQUIRED_FIELDS)}."
        ]

    problems: list[str] = []
    prompt = data.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        problems.append(
            "el campo «prompt» está vacío. Escribe el encargo que originó el "
            "artefacto, en una línea."
        )

    fecha = data.get("fecha")
    valid_date = False
    if isinstance(fecha, str) and DATE_RE.match(fecha):
        try:
            date.fromisoformat(fecha)
            valid_date = True
        except ValueError:
            valid_date = False
    if not valid_date:
        problems.append(
            "el campo «fecha» está vacío o no es una fecha real AAAA-MM-DD. "
            "Usa el día en que se genera el artefacto, por ejemplo 2026-11-08."
        )

    familia = data.get("familia")
    if familia not in FAMILIES:
        problems.append(
            "el campo «familia» está vacío o no es válido. Usa uno de: "
            f"{', '.join(FAMILIES)}."
        )

    fuentes = data.get("fuentes")
    if (
        not isinstance(fuentes, list)
        or not fuentes
        or not all(isinstance(item, str) and item.strip() for item in fuentes)
    ):
        problems.append(
            "el campo «fuentes» está vacío o no es una lista de cadenas no vacías. "
            'Lista de dónde sale el material, por ejemplo ["src/x.py:12", "git log"].'
        )

    return data, problems
