#!/usr/bin/env python3
"""Renderiza un árbol de documentos SDD como artefacto de la familia «sdd».

Uso:
    python3 render-sdd.py <directorio-sdd> --out .explanations/<slug>.html \
        --prompt "…" --date AAAA-MM-DD [--title "…"]

Lee el árbol con `sdd_scan.scan()` (el modelo es su contrato; aquí no se
reinterpreta Markdown para producir fichas ni progreso), extrae el CSS de
`assets/plantilla-sdd.html` y escribe un artefacto autocontenido dentro de
`.explanations/`. Prompt y fecha vienen de flags obligatorios: la misma
entrada produce los mismos bytes.

Secciones: resumen con perfiles y barra de tareas, las siete fases del
pipeline (Explore → Propose → Specify → Design → Tasks → Apply → Verify) más
«Sin fase», fichas de requisito con escenarios GIVEN/WHEN/THEN, matriz de
trazabilidad si hay refs, hallazgos por kind, desconocidos y los ficheros sin
perfil reconocido en modo degradado (secciones y cuerpo tal cual).

Seccionamiento: si la página completa pasaría de MAX_BYTES —el mismo umbral
que vigila check-artifact.py— no se emite un muro; se escribe un índice y una
página por fase (`<slug>-<fase>.html`). El corte es por fase, nunca por
tamaño; una fase que aún se pase se reparte por fichero
(`<slug>-<fase>-<n>.html`) y se avisa por stderr.
"""
import argparse
import html
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import artifact_meta
import sdd_scan

TEMPLATE = Path(__file__).resolve().parents[1] / "assets" / "plantilla-sdd.html"
STYLE_RE = re.compile(r"<style>(?P<css>.*?)</style>", re.DOTALL)

# El umbral de la puerta vive en check-artifact.py (MAX_BYTES). Aquí solo se
# usa para decidir el corte por fase, no para trocear contenido a ciegas.
MAX_BYTES = 100_000

PHASES = ["explore", "propose", "specify", "design", "tasks", "apply", "verify"]
PHASE_LABEL = {
    "explore": "Explore",
    "propose": "Propose",
    "specify": "Specify",
    "design": "Design",
    "tasks": "Tasks",
    "apply": "Apply",
    "verify": "Verify",
    "misc": "Sin fase",
}
MISC = "misc"

SHALL_RE = re.compile(r"\bSHALL\b")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.+)$")
TABLE_SEP_RE = re.compile(r"^\s*:?-{3,}:?\s*$")
FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
STEM_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

DELTA_CLASS = {
    "ADDED": "delta-added",
    "MODIFIED": "delta-modified",
    "REMOVED": "delta-removed",
    "RENAMED": "delta-renamed",
}

FINDING_LABELS = {
    "scenario-three-hashes": "Escenario con tres almohadillas",
    "requirement-without-scenario": "Requisito sin escenario",
    "ears-without-shall": "Línea EARS sin SHALL",
    "checkbox-pending": "Tarea marcada como pendiente",
    "capability-without-delta-file": "Capacidad sin spec.md",
    "modified-without-target": "Delta sin requisito de destino",
    "vague-requirement": "Requisito vago",
    "prescriptive-requirement": "Requisito prescriptivo",
    "scenario-without-error-case": "Escenario sin caso de error",
    "missing-non-goals": "Falta la sección de no-objetivos en el árbol",
}

PREPAINT = """<script>
(function () {
  try {
    var t = localStorage.getItem("explain-html:theme");
    if (!t && window.matchMedia) t = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", t || "light");
  } catch (e) {}
  document.documentElement.classList.add("js");
})();
</script>"""

THEME_JS = """<script>
(function () {
  var root = document.documentElement;
  var toggles = [].slice.call(document.querySelectorAll("[data-theme-toggle]"));
  function label() {
    var dark = root.getAttribute("data-theme") === "dark";
    toggles.forEach(function (toggle) {
      toggle.setAttribute("aria-label", dark ? "Cambiar a tema claro" : "Cambiar a tema oscuro");
    });
  }
  if (toggles.length) {
    label();
    toggles.forEach(function (toggle) {
      toggle.addEventListener("click", function () {
        var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", next);
        try { localStorage.setItem("explain-html:theme", next); } catch (e) {}
        label();
      });
    });
  }
})();
</script>"""


def esc(value) -> str:
    return html.escape(str(value))


def size(text: str) -> int:
    return len(text.encode("utf-8"))


def chrome() -> str:
    return """<a class="skip" href="#contenido">Saltar al contenido</a>
<header class="top">
  <div class="shell top-in">
    <a class="brand" href="#contenido" aria-label="Artefacto explain-html">
      <span class="mark" aria-hidden="true"><svg viewBox="0 0 32 32" role="presentation"><rect width="32" height="32" rx="8" fill="#4f46e5"/><rect x="7" y="9" width="18" height="14" rx="2" fill="none" stroke="#ffffff" stroke-width="2"/><path d="M7 13h18" stroke="#ffffff" stroke-width="2"/><path d="M12 19l3 3 5-5" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
      <span class="brand-text"><strong>explain-html</strong><small>sdd · artefacto</small></span>
    </a>
    <nav class="top-nav" aria-label="Navegación">
      <button class="theme" type="button" data-theme-toggle aria-label="Cambiar a tema oscuro" title="Cambiar tema">
        <svg class="i-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg><svg class="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
      </button>
    </nav>
  </div>
</header>"""


def hero(title: str, lead: str, chips: str, fecha: str) -> str:
    return f"""<section class="hero grid" id="portada">
  <div class="shell">
    <p class="eyebrow"><span class="dot"></span>sdd · {esc(fecha)}</p>
    <h1>{esc(title)}</h1>
    <p class="lead">{esc(lead)}</p>
    <div class="meta-row">
      {chips}
    </div>
  </div>
</section>"""


def page(title: str, css: str, meta: dict, hero_html: str, main: str, footer: str) -> str:
    metadata = json.dumps(meta, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="es" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%234f46e5'/%3E%3Crect x='7' y='9' width='18' height='14' rx='2' fill='none' stroke='%23ffffff' stroke-width='2'/%3E%3Cpath d='M7 13h18' stroke='%23ffffff' stroke-width='2'/%3E%3Cpath d='M12 19l3 3 5-5' fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
{PREPAINT}
<title>{esc(title)}</title>
<style>{css}</style>
</head>
<body class="inner">
<!-- procedencia: {metadata} -->
{chrome()}
{hero_html}
<main class="shell inner" id="contenido">
{main}
</main>
<footer class="foot">
  <div class="shell foot-in">
    <span><code>familia · sdd</code> · artefacto explain-html</span>
    <span>{footer}</span>
  </div>
</footer>
{THEME_JS}
</body>
</html>
"""


def section_head(number: int, title: str) -> str:
    return f'<div class="section-head"><span class="num">{number}</span><h2>{esc(title)}</h2></div>'


def meta_for(prompt: str, fecha: str, fuentes: list, enlaces=None) -> dict:
    meta = {"prompt": prompt, "fecha": fecha, "familia": "sdd", "fuentes": fuentes}
    if enlaces:
        meta["enlaces"] = enlaces
    return meta


def task_stats(model: dict) -> dict:
    tasks = [task for item in model["files"] for task in item["tasks"]]
    done = sum(1 for task in tasks if task["state"] == "done")
    pending = sum(1 for task in tasks if task["state"] in {"todo", "pending", None})
    parallel = sum(1 for task in tasks if task["parallel"])
    return {"total": len(tasks), "done": done, "pending": pending, "parallel": parallel}


def phase_of(item: dict) -> str:
    # Un fichero sin perfil reconocido siempre va a «Sin fase»: su ficha real
    # depende del perfil, y en modo degradado no se inventa.
    if item["unclassified_reason"] is not None:
        return MISC
    return item["phase"] or MISC


def bucket_files(model: dict) -> dict:
    buckets = {phase: [] for phase in [*PHASES, MISC]}
    for item in model["files"]:
        buckets[phase_of(item)].append(item)
    return buckets


def chips_html(model: dict) -> str:
    files = model["files"]
    counts = Counter(item["profile"] for item in files)
    chips = [f'<span class="tag tag-accent">árbol · {esc(model["tree_profile"])}</span>']
    for profile in sorted(counts):
        chips.append(f'<span class="tag">{esc(profile)} · {counts[profile]}</span>')
    unclassified = len(model["unknown_files"])
    if unclassified:
        chips.append(
            f'<span class="tag tag-warn">{unclassified} de {len(files)} ficheros '
            "sin perfil reconocido</span>"
        )
    return "\n      ".join(chips)


def progress_html(stats: dict) -> str:
    total = stats["total"]
    if not total:
        return ""
    percent = round(100 * stats["done"] / total)
    return f"""<div class="progress">
      <p class="progress-head"><strong>{stats["done"]} de {total}</strong> tareas hechas
        <span>· {stats["pending"]} pendientes</span>
        <span>· {stats["parallel"]} marcadas [P] como paralelizables</span></p>
      <div class="bar" role="progressbar" aria-valuenow="{stats["done"]}" aria-valuemin="0" aria-valuemax="{total}" aria-label="Tareas completadas del árbol"><span class="fill" style="width:{percent}%"></span></div>
      <p class="progress-note">Estado de las tareas declaradas en el árbol; una tarea «pending» no se cuenta como hecha.</p>
    </div>"""


def requirement_html(req: dict) -> str:
    delta = req.get("delta_op")
    badge = ""
    if delta:
        css_class = DELTA_CLASS.get(delta, "delta-renamed")
        badge = f'<span class="delta {css_class}">{esc(delta)}</span>'
    text = f"<p>{SHALL_RE.sub('<strong class=\"shall\">SHALL</strong>', esc(req['text']))}</p>" if req["text"] else ""
    scenarios = "".join(scenario_html(scenario) for scenario in req["scenarios"])
    criteria = ""
    if req["acceptance_criteria"]:
        items = "".join(
            f"<li>{esc(item['text'])}</li>" for item in req["acceptance_criteria"]
        )
        criteria = (
            '<div class="ac"><p class="ac-title">Criterios de aceptación</p>'
            f"<ol>{items}</ol></div>"
        )
    return (
        '<article class="req">'
        f'<h5 class="req-name">{esc(req["name"])}{badge}</h5>'
        f"{text}{scenarios}{criteria}"
        "</article>"
    )


def scenario_html(scenario: dict) -> str:
    roles = ""
    for key in ("given", "when", "then"):
        values = scenario.get(key) or []
        if not values:
            continue
        items = "".join(f"<li>{esc(value)}</li>" for value in values)
        roles += (
            f'<div class="sc-role sc-{key}"><span class="lbl">{key.upper()}</span>'
            f"<ul>{items}</ul></div>"
        )
    return (
        '<div class="scenario">'
        f'<p class="sc-name">Escenario: {esc(scenario["name"])}</p>'
        f"{roles}</div>"
    )


def task_html(task: dict) -> str:
    state = task["state"] or "pending"
    mark = {"done": "✓", "todo": "○", "pending": "~"}.get(state, "○")
    parallel = ' <span class="tag tag-warn">[P]</span>' if task["parallel"] else ""
    refs = (
        f' <span class="refs">→ requisitos {esc(", ".join(task["refs"]))}</span>'
        if task["refs"]
        else ""
    )
    return (
        f'<li class="task task-{esc(state)}"><span class="box" aria-hidden="true">{mark}</span>'
        f'<span class="task-text">{esc(task["text"])}</span>{parallel}{refs}</li>'
    )


def markdown_blocks(path: Path) -> list:
    """Convierte un Markdown seco en bloques HTML: párrafos, listas y tablas.

    No interpreta el perfil ni inventa fichas: solo transcribe el cuerpo de un
    fichero sin perfil reconocido, con encabezados como los declara el modelo.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ['<p class="muted">No se pudo leer el fichero desde el árbol.</p>']
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    index = 0
    if lines and lines[0].strip() == "---":
        for position in range(1, len(lines)):
            if lines[position].strip() in {"---", "..."}:
                index = position + 1
                break

    blocks: list = []
    paragraph: list = []
    items: list = []
    rows: list = []
    code: list = []
    in_code = False

    def flush() -> None:
        nonlocal paragraph, items, rows
        if paragraph:
            blocks.append(f"<p>{esc(' '.join(paragraph))}</p>")
            paragraph = []
        if items:
            lis = "".join(f"<li>{esc(item)}</li>" for item in items)
            blocks.append(f'<ul class="md-list">{lis}</ul>')
            items = []
        if rows:
            header = "".join(f"<th>{esc(cell)}</th>" for cell in rows[0])
            body = "".join(
                "<tr>" + "".join(f"<td>{esc(cell)}</td>" for cell in row) + "</tr>"
                for row in rows[1:]
            )
            blocks.append(
                '<div class="table-wrap"><table>'
                f"<thead><tr>{header}</tr></thead><tbody>{body}</tbody>"
                "</table></div>"
            )
            rows = []

    for line in lines[index:]:
        if FENCE_RE.match(line):
            flush()
            if in_code:
                blocks.append(f"<pre><code>{esc(chr(10).join(code))}</code></pre>")
                code = []
            in_code = not in_code
            continue
        if in_code:
            code.append(line)
            continue
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        heading = HEADING_RE.match(line)
        if heading:
            flush()
            level = min(len(heading.group(1)) + 2, 6)
            blocks.append(f"<h{level}>{esc(heading.group(2))}</h{level}>")
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            if paragraph or items:
                flush()
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if all(TABLE_SEP_RE.match(cell) for cell in cells if cell):
                continue
            rows.append(cells)
            continue
        item = LIST_RE.match(line)
        if item:
            if paragraph or rows:
                flush()
            items.append(item.group(1).strip())
            continue
        paragraph.append(stripped)
    if in_code and code:
        blocks.append(f"<pre><code>{esc(chr(10).join(code))}</code></pre>")
    flush()
    if not blocks:
        return ['<p class="muted">El fichero no tiene cuerpo que transcribir.</p>']
    return blocks


def file_pieces(item: dict, root: Path, budget: int) -> list:
    """Devuelve las tarjetas HTML del fichero, troceadas si no caben en `budget`."""
    tags = [
        f'<span class="tag">{esc(item["role"])}</span>',
        f'<span class="tag">{esc(item["phase"] or "sin fase")}</span>',
        f'<span class="tag">{esc(item["profile"])}</span>',
    ]
    if item["markers"]:
        tags.append(
            f'<span class="tag tag-warn">necesita aclaración · {len(item["markers"])}</span>'
        )

    blocks: list = []
    if item["unclassified_reason"]:
        blocks.append(
            '<div class="note note-warn"><p><strong>Sin perfil reconocido:</strong> '
            f"{esc(item['unclassified_reason'])}. Se muestra el documento tal cual, "
            "sin fichas ni progreso.</p></div>"
        )
        blocks.extend(
            f'<div class="md-body">{block}</div>' for block in markdown_blocks(root / item["path"])
        )
    for req in item["requirements"]:
        blocks.append(requirement_html(req))
    for start in range(0, len(item["tasks"]), 60):
        chunk = item["tasks"][start:start + 60]
        items = "".join(task_html(task) for task in chunk)
        blocks.append(f'<ul class="tasks">{items}</ul>')

    groups: list = []
    current: list = []
    current_size = 0
    for block in blocks:
        if current and current_size + len(block) > budget:
            groups.append(current)
            current = []
            current_size = 0
        current.append(block)
        current_size += len(block)
    if current:
        groups.append(current)
    if not groups:
        groups = [[]]

    pieces = []
    for position, group in enumerate(groups):
        title = esc(item["title"])
        if position:
            title += " <small>(continúa)</small>"
        head = (
            '<header class="file-head"><div class="file-title">'
            f'<h4>{title}</h4><p class="path"><code>{esc(item["path"])}</code></p>'
            f'</div><div class="chips">{"".join(tags)}</div></header>'
        )
        pieces.append(f'<article class="file-card">{head}{"".join(group)}</article>')
    return pieces


def phase_cards(bucket: list, root: Path, budget: int) -> list:
    pieces: list = []
    for item in bucket:
        pieces.extend(file_pieces(item, root, budget))
    return pieces


def profile_chips(model: dict) -> str:
    files = model["files"]
    if not files:
        return '<p class="muted">El árbol no contiene ningún Markdown que renderizar.</p>'
    return chips_html(model)


def traceability_html(model: dict) -> str:
    rows = []
    for item in model["files"]:
        for task in item["tasks"]:
            if not task["refs"]:
                continue
            rows.append((item, task))
    if not rows:
        return ""
    body = "".join(
        "<tr>"
        f"<td>{esc(task['id'] + ' · ' if task['id'] else '')}{esc(task['text'])}</td>"
        f"<td><code>{esc(', '.join(task['refs']))}</code></td>"
        f"<td><code>{esc(item['path'])}:{task['line']}</code></td>"
        "</tr>"
        for item, task in rows
    )
    return (
        '<div class="table-wrap"><table>'
        "<thead><tr><th>Tarea</th><th>Requisitos referenciados</th><th>Fuente</th></tr></thead>"
        f"<tbody>{body}</tbody></table></div>"
    )


def finding_place(item: dict) -> str:
    path = item["path"]
    line = item["line"]
    if line:
        return f'<code>{esc(path)}:{line}</code>'
    if path:
        return f'<code>{esc(path)}</code> <span class="tree-level">· a nivel de árbol</span>'
    return '<span class="tree-level">a nivel de árbol</span>'


def finding_groups(model: dict) -> dict:
    groups: dict = {}
    for entry in model["findings"]:
        groups.setdefault(entry["kind"], []).append(entry)
    return groups


def finding_blocks(model: dict, chunk_size: int = 80) -> list:
    """Un <details> por kind; un kind enorme se reparte en tandas con su recuento."""
    blocks = []
    groups = finding_groups(model)
    for kind in sorted(groups):
        label = FINDING_LABELS.get(kind, "Hallazgo sin etiqueta conocida")
        entries = groups[kind]
        for start in range(0, len(entries), chunk_size):
            chunk = entries[start:start + chunk_size]
            continues = " <small>(continúa)</small>" if start else ""
            items = "".join(
                f"<li>{finding_place(entry)} · {esc(entry['detail'])}</li>"
                for entry in chunk
            )
            blocks.append(
                f'<details class="finding-group" open><summary>{esc(label)}{continues} '
                f'<code>{esc(kind)}</code> <span class="count">{len(entries)}</span></summary>'
                f'<ul class="tight">{items}</ul></details>'
            )
    return blocks


def findings_html(model: dict, number: int) -> str:
    groups = finding_groups(model)
    head = section_head(number, "Hallazgos")
    if not groups:
        return (
            f'<section class="section" id="hallazgos">{head}'
            '<p class="muted">El escáner no produjo hallazgos estructurales.</p></section>'
        )
    counts = "".join(
        f'<span class="tag">{esc(kind)} · {len(groups[kind])}</span>'
        for kind in sorted(groups)
    )
    return (
        f'<section class="section" id="hallazgos">{head}'
        f'<div class="chips">{counts}</div>'
        f'{"".join(finding_blocks(model))}</section>'
    )


def unknown_items(model: dict) -> list:
    items = []
    for item in model["files"]:
        if item["unclassified_reason"] is not None:
            items.append(
                f'<li><code>{esc(item["path"])}</code> — sin perfil reconocido: '
                f'{esc(item["unclassified_reason"])}</li>'
            )
    for item in model["files"]:
        for marker in item["markers"]:
            items.append(
                f'<li><code>{esc(item["path"])}:{marker["line"]}</code> — necesita '
                "aclaración: el documento marca NEEDS CLARIFICATION y queda sin resolver.</li>"
            )
    return items


def unknown_blocks(model: dict, chunk_size: int = 60) -> list:
    items = unknown_items(model)
    if not items:
        return []
    blocks = ['<h3 class="phase-title">Desconocidos</h3>']
    for start in range(0, len(items), chunk_size):
        blocks.append(f'<ul class="tight">{"".join(items[start:start + chunk_size])}</ul>')
    return blocks


def unknowns_html(model: dict, number: int) -> str:
    items = unknown_items(model)
    head = section_head(number, "Desconocidos")
    if not items:
        return (
            f'<section class="section" id="desconocidos">{head}'
            '<p class="muted">Ninguno detectado: todos los ficheros tienen perfil '
            "reconocido y no quedan marcadores de aclaración.</p></section>"
        )
    return (
        f'<section class="section" id="desconocidos">{head}'
        f'<ul class="tight">{"".join(items)}</ul></section>'
    )


def findings_counts_html(model: dict, number: int, detail_name: str | None) -> str:
    """Recuento por kind para el índice seccionado; el detalle vive en su hermana."""
    groups = finding_groups(model)
    head = section_head(number, "Hallazgos")
    if not groups:
        body = '<p class="muted">El escáner no produjo hallazgos estructurales.</p>'
    else:
        counts = "".join(
            f'<span class="tag">{esc(kind)} · {len(groups[kind])}</span>'
            for kind in sorted(groups)
        )
        body = (
            f'<div class="chips">{counts}</div>'
            '<p class="sub">Recuento por kind; el detalle —fichero, línea y motivo— '
            "está en la página de hallazgos.</p>"
        )
    link = (
        f'<p><a href="{esc(detail_name)}">Ver el detalle de hallazgos y desconocidos</a></p>'
        if detail_name
        else ""
    )
    return f'<section class="section" id="hallazgos">{head}{body}{link}</section>'


def unknowns_counts_html(model: dict, number: int, detail_name: str | None) -> str:
    unclassified = sum(
        1 for item in model["files"] if item["unclassified_reason"] is not None
    )
    markers = sum(len(item["markers"]) for item in model["files"])
    head = section_head(number, "Desconocidos")
    body = (
        f'<p class="sub">{unclassified} fichero(s) sin perfil reconocido · '
        f"{markers} marcador(es) de aclaración.</p>"
    )
    if not unclassified and not markers:
        body = '<p class="muted">Ninguno detectado.</p>'
    link = (
        f'<p><a href="{esc(detail_name)}">Ver el detalle de hallazgos y desconocidos</a></p>'
        if detail_name
        else ""
    )
    return f'<section class="section" id="desconocidos">{head}{body}{link}</section>'


def resumen_html(model: dict, stats: dict, number: int) -> str:
    files = model["files"]
    used_phases = sum(1 for phase in PHASES if any(phase_of(item) == phase for item in files))
    kpis = (
        f'<div class="kpis">'
        f'<div class="kpi"><strong>{len(files)}</strong><span>Documentos leídos</span></div>'
        f'<div class="kpi"><strong>{used_phases}</strong><span>Fases con contenido</span></div>'
        f'<div class="kpi"><strong>{stats["total"]}</strong><span>Tareas declaradas</span></div>'
        f'<div class="kpi"><strong>{len(model["findings"])}</strong><span>Hallazgos</span></div>'
        "</div>"
    )
    return (
        f'<section class="section" id="resumen">{section_head(number, "Resumen")}'
        f"{kpis}{progress_html(stats)}{profile_chips(model)}</section>"
    )


def pipeline_anchors(buckets: dict) -> str:
    links = []
    for phase in [*PHASES, MISC]:
        count = len(buckets.get(phase, []))
        links.append(
            f'<li><a href="#fase-{phase}"><span class="n">{count}</span>'
            f"{esc(PHASE_LABEL[phase])}</a></li>"
        )
    return f'<ul class="pipeline">{"".join(links)}</ul>'


def phases_single_html(model: dict, buckets: dict, root: Path, number: int, budget: int) -> str:
    parts = [
        f'<section class="section" id="fases">{section_head(number, "Fases del pipeline")}'
        '<p class="sub">La navegación es fija: las siete fases del pipeline más «Sin fase». '
        "Una fase sin ficheros se muestra vacía, no se oculta.</p>"
        f"{pipeline_anchors(buckets)}"
    ]
    for phase in [*PHASES, MISC]:
        bucket = buckets.get(phase, [])
        label = PHASE_LABEL[phase]
        cards = "".join(phase_cards(bucket, root, budget))
        if not cards:
            cards = '<p class="phase-empty">Sin ficheros en esta fase.</p>'
        parts.append(
            f'<section class="phase" id="fase-{phase}">'
            f'<h3 class="phase-title">{esc(label)} <span class="count">{len(bucket)}</span></h3>'
            f"{cards}</section>"
        )
    parts.append("</section>")
    return "\n".join(parts)


def phase_links_index(pages: list, number: int) -> str:
    rows = []
    by_phase: dict = {}
    for phase, name, count in pages:
        by_phase.setdefault(phase, []).append((name, count))
    for phase in [*PHASES, MISC]:
        entries = by_phase.get(phase)
        if not entries:
            rows.append(
                f'<li class="phase-link"><span class="phase-label">{esc(PHASE_LABEL[phase])}</span>'
                '<span class="phase-empty">Sin ficheros en esta fase.</span></li>'
            )
            continue
        links = " ".join(
            f'<a href="{esc(name)}">{esc(name)}</a> <span class="count">{count} fichas</span>'
            for name, count in entries
        )
        rows.append(
            f'<li class="phase-link"><span class="phase-label">{esc(PHASE_LABEL[phase])}</span>'
            f"{links}</li>"
        )
    return (
        f'<section class="section" id="fases">{section_head(number, "Fases del pipeline")}'
        '<p class="sub">El árbol supera el umbral de una página: cada fase vive en su '
        "página hermana y este índice conserva el resumen, los hallazgos y los desconocidos.</p>"
        f'<ul class="phase-links">{"".join(rows)}</ul></section>'
    )


def page_nav(index_name: str, current: str, enlaces: list) -> str:
    links = [f'<a href="{esc(index_name)}">Índice</a>']
    for name in enlaces:
        if name in {index_name, current}:
            continue
        links.append(f'<a href="{esc(name)}">{esc(name)}</a>')
    return f'<nav class="page-nav" aria-label="Páginas del artefacto">{"".join(links)}</nav>'


def paginate(pieces: list, limit: int) -> list:
    pages: list = []
    current: list = []
    current_size = 0
    for piece in pieces:
        if current and current_size + size(piece) > limit:
            pages.append(current)
            current = []
            current_size = 0
        current.append(piece)
        current_size += size(piece)
    if current:
        pages.append(current)
    return pages


def build_single(model, root, title, css, meta, fecha, stats, buckets, budget):
    chars = []
    number = 1
    chars.append(resumen_html(model, stats, number))
    number += 1
    chars.append(phases_single_html(model, buckets, root, number, budget))
    number += 1
    traceability = traceability_html(model)
    if traceability:
        chars.append(
            f'<section class="section" id="trazabilidad">'
            f'{section_head(number, "Trazabilidad")}'
            '<p class="sub">Tareas que declaran los requisitos que implementan.</p>'
            f"{traceability}</section>"
        )
        number += 1
    chars.append(findings_html(model, number))
    number += 1
    chars.append(unknowns_html(model, number))
    lead = (
        f"{len(model['files'])} documentos · perfil del árbol «{model['tree_profile']}» · "
        f"{stats['total']} tareas · {len(model['findings'])} hallazgos."
    )
    footer = f"{len(model['files'])} documentos · árbol {esc(model['tree_profile'])}"
    hero_html = hero(title, lead, chips_html(model), fecha)
    return page(title, css, meta, hero_html, "\n".join(chars), footer)


def build_split(model, root, out, title, css, base_meta, fecha, stats, buckets, budget):
    """Construye el índice y las páginas por fase; devuelve [(ruta, html)] y avisos."""
    warnings: list = []
    # Holgura: se mide una página vacía con el mismo chrome, hero y CSS; el
    # margen cubre la cabecera de fase y la navegación entre hermanas.
    probe = page(title, css, base_meta, hero(title, "", chips_html(model), fecha), "", "")
    limit = max(20_000, MAX_BYTES - size(probe) - 4_000)

    phase_pages: list = []
    for phase in [*PHASES, MISC]:
        pieces = phase_cards(buckets.get(phase, []), root, budget)
        if not pieces:
            continue
        chunks = paginate(pieces, limit)
        phase_pages.append((phase, chunks))
        if len(chunks) > 1:
            warnings.append(
                f"AVISO: la fase «{PHASE_LABEL[phase]}» supera {MAX_BYTES} bytes; "
                f"se reparte en {len(chunks)} páginas por fichero."
            )

    stem = out.stem
    named: list = []  # (phase, name, chunk)
    for phase, chunks in phase_pages:
        for position, chunk in enumerate(chunks, start=1):
            if len(chunks) == 1:
                name = f"{stem}-{phase}.html"
            else:
                name = f"{stem}-{phase}-{position}.html"
            named.append((phase, name, chunk))

    # El detalle de hallazgos y desconocidos va a su propia hermana: el índice
    # se queda con el recuento por kind para no crecer con el árbol.
    detail_blocks = finding_blocks(model) + unknown_blocks(model)
    detail_chunks = paginate(detail_blocks, limit) if detail_blocks else []
    detail_names: list = []
    for position in range(1, len(detail_chunks) + 1):
        if len(detail_chunks) == 1:
            detail_names.append(f"{stem}-hallazgos.html")
        else:
            detail_names.append(f"{stem}-hallazgos-{position}.html")
    if len(detail_chunks) > 1:
        warnings.append(
            f"AVISO: los hallazgos y desconocidos superan {MAX_BYTES} bytes; "
            f"se reparten en {len(detail_chunks)} páginas por kind."
        )
    detail_link = detail_names[0] if detail_names else None

    all_names = [out.name] + [name for _, name, _ in named] + detail_names

    def enlaces_for(current: str) -> list:
        return sorted(name for name in all_names if name != current)

    pages: list = []
    links_summary = [(phase, name, len(chunk)) for phase, name, chunk in named]
    index_chars = [
        resumen_html(model, stats, 1),
        phase_links_index(links_summary, 2),
        findings_counts_html(model, 3, detail_link),
        unknowns_counts_html(model, 4, detail_link),
    ]
    index_lead = (
        f"Índice de {len(named) + len(detail_names)} páginas hermanas · "
        f"{len(model['files'])} documentos · {stats['total']} tareas · "
        f"{len(model['findings'])} hallazgos."
    )
    index_meta = dict(base_meta)
    index_meta["enlaces"] = enlaces_for(out.name)
    index_hero = hero(title, index_lead, chips_html(model), fecha)
    index_footer = f"índice · {len(named) + len(detail_names)} páginas hermanas"
    pages.append(
        (
            out,
            page(
                title,
                css,
                index_meta,
                index_hero,
                "\n".join(index_chars),
                index_footer,
            ),
        )
    )

    for phase, name, chunk in named:
        label = PHASE_LABEL[phase]
        page_title = f"{title} · {label}"
        lead = (
            f"{label} · {len(buckets.get(phase, []))} documentos en esta fase · "
            f"árbol {model['tree_profile']}."
        )
        meta = dict(base_meta)
        meta["enlaces"] = enlaces_for(name)
        hero_html = hero(page_title, lead, chips_html(model), fecha)
        main = (
            page_nav(out.name, name, enlaces_for(name))
            + f'<section class="section" id="fase-{phase}">'
            + section_head(1, label)
            + "".join(chunk)
            + "</section>"
        )
        pages.append(
            (
                out.parent / name,
                page(page_title, css, meta, hero_html, main, f"{label} · {len(chunk)} fichas"),
            )
        )

    for position, chunk in enumerate(detail_chunks, start=1):
        name = detail_names[position - 1]
        page_title = f"{title} · Hallazgos y desconocidos"
        if len(detail_chunks) > 1:
            page_title += f" ({position}/{len(detail_chunks)})"
        lead = (
            f"{len(model['findings'])} hallazgos · {len(unknown_items(model))} "
            f"desconocidos · parte {position} de {len(detail_chunks)}."
        )
        meta = dict(base_meta)
        meta["enlaces"] = enlaces_for(name)
        hero_html = hero(page_title, lead, chips_html(model), fecha)
        main = (
            page_nav(out.name, name, enlaces_for(name))
            + '<section class="section" id="hallazgos">'
            + section_head(1, "Hallazgos y desconocidos")
            + "".join(chunk)
            + "</section>"
        )
        pages.append(
            (
                out.parent / name,
                page(page_title, css, meta, hero_html, main, "hallazgos y desconocidos"),
            )
        )
    return pages, warnings


def read_css() -> str:
    text = TEMPLATE.read_text(encoding="utf-8")
    match = STYLE_RE.search(text)
    if match is None:
        raise ValueError("la plantilla no tiene un bloque <style>")
    return match.group("css")


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 2


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Renderiza un árbol de documentos SDD como artefacto explain-html"
    )
    parser.add_argument("directorio", help="directorio raíz del árbol de documentos SDD")
    parser.add_argument("--out", required=True, help="ruta del .html dentro de .explanations/")
    parser.add_argument("--prompt", required=True, help="encargo que originó el artefacto")
    parser.add_argument("--date", required=True, dest="fecha", help="fecha del artefacto, AAAA-MM-DD")
    parser.add_argument("--title", default=None, help="título visible; por defecto, el del directorio")
    args = parser.parse_args(argv)

    root = Path(args.directorio)
    if not root.is_dir():
        return fail(f"{args.directorio} no es un directorio.")
    if not args.prompt.strip():
        return fail("--prompt vacío: escribe el encargo que originó el artefacto.")
    if not artifact_meta.DATE_RE.match(args.fecha or ""):
        return fail("--date vacía o no válida: usa AAAA-MM-DD, por ejemplo 2026-11-08.")
    try:
        date.fromisoformat(args.fecha)
    except ValueError:
        return fail("--date no es una fecha real: usa AAAA-MM-DD, por ejemplo 2026-11-08.")

    out = Path(args.out)
    if out.suffix.lower() != ".html":
        return fail("--out debe terminar en .html.")
    if out.name.lower() == "index.html":
        return fail("--out no puede ser index.html: ese fichero lo mantiene build-index.py.")
    resolved = out.resolve()
    if ".explanations" not in resolved.parts:
        return fail(
            f"--out ({resolved}) queda fuera de un directorio .explanations/. "
            "Los artefactos solo se escriben ahí."
        )

    try:
        css = read_css()
    except (OSError, ValueError) as exc:
        return fail(f"no se pudo leer el estilo de {TEMPLATE}: {exc}")

    model = sdd_scan.scan(args.directorio)
    title = args.title or f"Especificación SDD: {root.resolve().name}"
    fuentes = [item["path"] for item in model["files"]] or [str(model["root"])]
    base_meta = meta_for(args.prompt, args.fecha, fuentes)
    stats = task_stats(model)
    buckets = bucket_files(model)
    budget = max(10_000, MAX_BYTES // 2)

    single = build_single(model, root, title, css, base_meta, args.fecha, stats, buckets, budget)
    if size(single) <= MAX_BYTES:
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(single, encoding="utf-8", newline="\n")
        except OSError as exc:
            return fail(f"no se pudo escribir {out}: {exc}")
        print(f"OK: {out} (1 página, {size(single)} bytes) desde {args.directorio}.")
        return 0

    if not STEM_RE.match(out.stem):
        return fail(
            f"el nombre «{out.stem}» no sirve para las páginas hermanas "
            "(solo letras, números, punto, guion y guion bajo)."
        )

    pages, warnings = build_split(
        model, root, out, title, css, base_meta, args.fecha, stats, buckets, budget
    )
    for path, text in pages:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
        except OSError as exc:
            return fail(f"no se pudo escribir {path}: {exc}")
        if size(text) > MAX_BYTES:
            warnings.append(
                f"AVISO: {path.name} sigue por encima de {MAX_BYTES} bytes "
                f"({size(text)}); una sola ficha no se puede cortar sin perder información."
            )
    for warning in warnings:
        print(warning, file=sys.stderr)
    print(
        f"OK: índice en {out} y {len(pages) - 1} página(s) por fase desde {args.directorio}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
