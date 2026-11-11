#!/usr/bin/env python3
"""Descubre un árbol de documentos SDD y produce un modelo estructural en JSON.

Uso: python3 sdd_scan.py <directorio> [--json]

Es una librería (`scan(root)`) y también una herramienta de mano. No llama a
ninguna CLI externa: solo lee los Markdown del árbol con la biblioteca estándar.
El modelo es determinista: no lleva fechas ni estado de red, ninguna ruta
derivada es absoluta (`root` es el path recibido, tal cual), los ficheros van
ordenados por `path` y los hallazgos por (path, línea, kind).

Perfiles (convención de lectura, no frontera): `openspec`, `kiro`, `spec-kit` y
`generic`. Se detectan por ruta y por contenido; un fichero sin perfil reconocido
es `generic` y, si tampoco tiene anclas débiles, queda «sin clasificar» con un
motivo. Nunca se descarta en silencio: todo `.md` del árbol aparece en `files`
(salvo el `README.md` de la raíz y las carpetas .git/node_modules y similares).

Modelo (contrato estable):

{
  "root": "<el path recibido, tal cual>",
  "tree_profile": "openspec"|"kiro"|"spec-kit"|"mixed"|"generic",
  "has_non_goals": bool,        # algún fichero declara no-objetivos (nivel 2+)
  "files": [
    {
      "path": "relativo/con/barras.md",
      "role": "proposal|specs|deltas|design|plan|tasks|requirements|research|
               data-model|contracts|quickstart|constitution|decision|followup|
               bugfix|exploration|unknown",
      "phase": "explore|propose|specify|design|tasks|apply|verify|null",
      "profile": "openspec|kiro|spec-kit|generic",
      "title": "primer # o el nombre del fichero",
      "unclassified_reason": "texto"|null,
      "requirements": [
        {
          "name": "...", "text": "...", "line": 12,
          "delta_op": "ADDED|MODIFIED|REMOVED|RENAMED"|null,
          "scenarios": [
            {"name": "...", "line": 14,
             "given": ["..."], "when": ["..."], "then": ["..."]}
          ],
          "acceptance_criteria": [{"id": "1", "text": "...", "line": 16}]
        }
      ],
      "tasks": [
        {"id": "1.1"|null, "text": "...", "line": 8,
         "state": "todo|done|pending"|null, "refs": ["1.2"],
         "parallel": false}
      ],
      "markers": [{"kind": "needs-clarification", "line": 20}],
      "sections": [{"level": 2, "title": "...", "line": 4}]
    }
  ],
  "findings": [{"kind": "...", "path": "...", "line": 12, "detail": "..."}],
  "unknown_files": ["ruta/sin-clasificar.md"]
}

Las líneas son 1-based sobre el fichero original. Los hallazgos de árbol llevan
`line` 0 y, cuando señalan un directorio, `path` acaba en `/`.

Hallazgos: `scenario-three-hashes`, `requirement-without-scenario`,
`ears-without-shall`, `checkbox-pending`, `capability-without-delta-file`,
`modified-without-target`, `vague-requirement`, `prescriptive-requirement`,
`scenario-without-error-case` y `missing-non-goals` (uno solo por árbol).

Fases: proposal→propose, specs/deltas/requirements→specify, design/plan/
research/data-model/contracts→design, tasks→tasks, quickstart→verify,
exploration→explore, constitution/decision/followup→null. Bugfix se trata como
specify (documenta el comportamiento esperado; decisión propia de este parser).
"""
import argparse
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
DELTA_RE = re.compile(r"^##\s+(ADDED|MODIFIED|REMOVED|RENAMED)\s+Requirements\s*:?\s*$", re.I)
REQ_RE = re.compile(r"^###\s+Requirement\s*:\s*(.+?)\s*$", re.I)
KIRO_REQ_RE = re.compile(r"^###\s+Requirement\s+(\d+[A-Za-z0-9.]*)\s*:?\s*(.*)$", re.I)
SCEN4_RE = re.compile(r"^####\s+Scenario\s*:\s*(.*?)\s*$", re.I)
SCEN3_RE = re.compile(r"^###\s+Scenario\s*:\s*(.*?)\s*$", re.I)
AC_RE = re.compile(r"^####\s+Acceptance Criteria\s*$", re.I)
TASK_RE = re.compile(r"^\s*[-*+]\s+\[([ xX~\-/])\]\s+(.+)$")
TASK_ID_RE = re.compile(r"^(?:\d+(?:\.\d+)*|[A-Z]+-?\d+)\b")
PARALLEL_RE = re.compile(r"\[P\]")
REFS_RE = re.compile(r"^[-*+]?\s*_{0,2}Requirements?_{0,2}\s*:\s*(.+?)_*\s*$", re.I)
NUMBERED_RE = re.compile(r"^\s*(\d+)[.)]\s+(.+)$")
NEEDS_CLARIFICATION = "[NEEDS CLARIFICATION"
SPEC_KIT_CONSTITUTION_RE = re.compile(r"^#+\s+Constitution\b", re.I)
SPEC_KIT_SLUG_RE = re.compile(r"^\d{3,}-")

NON_GOALS_RE = re.compile(
    r"^(?:no[- ]?objetivos?|non[- ]?goals?|out of scope|fuera de alcance)\s*:?\s*$",
    re.I,
)
LABEL_RE = re.compile(r"(?<!\S)(?:\*\*)?(GIVEN|WHEN|THEN|AND)(?:\*\*)?(?=[\s:,\-]|$)")
LABEL_CI_RE = re.compile(r"(?<!\S)(?:\*\*)?(given|when|then|and)(?:\*\*)?(?=[\s:,\-]|$)", re.I)
CI_LABEL_START_RE = re.compile(r"^(?:[-*+]\s+)?(?:given|when|then|and)\b", re.I)
EARS_RE = re.compile(r"\b(?:WHEN|When)\b.*\b(?:THEN|then)\b")
SHALL_RE = re.compile(r"\bSHALL\b")
EARS_ROLES = {"requirements", "specs", "deltas", "bugfix"}
VAGUE_RE = re.compile(
    r"\b(?:modern(?:o|a|os|as)?|fast|r[áa]pid(?:o|a|os|as)?|easy|f[áa]cil(?:es)?"
    r"|robust(?:o|a|os|as)?|scalable|escalable|intuitive|intuitiv(?:o|a|os|as)?"
    r"|seamless|efficient|eficientes?|good|bien|best effort)\b",
    re.I,
)
METRIC_RE = re.compile(
    r"\d+(?:[.,]\d+)?\s*(?:%|ms|s|sec(?:onds?)?|seg(?:undos?)?|min(?:utes?)?|h"
    r"|hours?|d[ií]as?|days?|k|kb|mb|gb|tb|px|rps|qps|users?|usuarios?"
    r"|requests?|peticiones?|items?|elementos?|events?|eventos?|times?|veces|x)\b",
    re.I,
)
CODE_SPAN_RE = re.compile(r"`[^`]+`")
CALL_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\(")
ERROR_SIGNAL_RE = re.compile(
    r"error|fail|invalid|denied|timeout|empty|conflict|retry|fallo"
    r"|inv[áa]lid|denegad|caducad|vac[ií]|reintent",
    re.I,
)
NON_GOALS_HEADING_LEVEL = 2

NAME_ROLES = {
    "proposal.md": "proposal",
    "tasks.md": "tasks",
    "design.md": "design",
    "requirements.md": "requirements",
    "plan.md": "plan",
    "research.md": "research",
    "data-model.md": "data-model",
    "quickstart.md": "quickstart",
    "constitution.md": "constitution",
    "bugfix.md": "bugfix",
    "decision.md": "decision",
    "followup.md": "followup",
    "exploration.md": "exploration",
    "explore.md": "exploration",
}

PHASES = {
    "proposal": "propose",
    "specs": "specify",
    "deltas": "specify",
    "requirements": "specify",
    "design": "design",
    "plan": "design",
    "research": "design",
    "data-model": "design",
    "contracts": "design",
    "tasks": "tasks",
    "quickstart": "verify",
    "exploration": "explore",
    # Decisión propia: un bugfix es una entrada de especificación, no un plan.
    "bugfix": "specify",
    "constitution": None,
    "decision": None,
    "followup": None,
    "unknown": None,
}


def read_lines(path: Path) -> list[str]:
    """Lee UTF-8 tolerante y normaliza CRLF/CR a LF."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    return raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def content_start(lines: list[str]) -> int:
    """Índice de la primera línea tras un bloque de front matter YAML, si lo hay."""
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() in {"---", "..."}:
                return index + 1
    return 0


def scan_headings(lines: list[str], start: int) -> tuple[list[dict], set[int]]:
    """Encabezados fuera de bloques de código, y las líneas que están dentro."""
    headings: list[dict] = []
    code_lines: set[int] = set()
    in_fence = False
    for index in range(start, len(lines)):
        line = lines[index]
        if FENCE_RE.match(line):
            in_fence = not in_fence
            code_lines.add(index)
            continue
        if in_fence:
            code_lines.add(index)
            continue
        match = HEADING_RE.match(line)
        if match:
            headings.append(
                {"level": len(match.group(1)), "title": match.group(2).strip(), "line": index + 1}
            )
    return headings, code_lines


def detect_profile(rel: str, lines: list[str], start: int, code_lines: set[int]) -> str:
    parts = [part.lower() for part in rel.split("/")]
    if "openspec" in parts:
        return "openspec"
    if ".kiro" in parts:
        return "kiro"
    if "specs" in parts and len(parts) >= 3 and SPEC_KIT_SLUG_RE.match(parts[parts.index("specs") + 1]):
        return "spec-kit"
    if parts and SPEC_KIT_SLUG_RE.match(parts[0]) and len(parts) >= 2:
        return "spec-kit"
    if parts[0] == "memory" and parts[-1] == "constitution.md":
        return "spec-kit"
    body = [lines[index] for index in range(start, len(lines)) if index not in code_lines]
    for line in body:
        if DELTA_RE.match(line):
            return "openspec"
    for line in body:
        if AC_RE.match(line) or REFS_RE.match(line.strip()):
            return "kiro"
    for line in body:
        if NEEDS_CLARIFICATION in line.upper() or SPEC_KIT_CONSTITUTION_RE.match(line):
            return "spec-kit"
        if TASK_RE.match(line) and PARALLEL_RE.search(TASK_RE.match(line).group(2)):
            return "spec-kit"
    return "generic"


def role_for(rel: str, has_delta: bool) -> str:
    parts = [part.lower() for part in rel.split("/")]
    name = parts[-1]
    if name == "spec.md":
        return "deltas" if has_delta else "specs"
    if name in NAME_ROLES:
        return NAME_ROLES[name]
    if "contracts" in parts[:-1]:
        return "contracts"
    return "unknown"


def finding(kind: str, path: str, line: int, detail: str) -> dict:
    return {"kind": kind, "path": path, "line": line, "detail": detail}


def label_groups(text: str) -> dict[str, list[str]]:
    """Reparte una línea GIVEN/WHEN/THEN (bullet, negrita o párrafo) por etiqueta."""
    groups: dict[str, list[str]] = {"given": [], "when": [], "then": []}
    matches = list(LABEL_RE.finditer(text))
    if not matches and CI_LABEL_START_RE.match(text.strip()):
        matches = list(LABEL_CI_RE.finditer(text))
    last = None
    for index, match in enumerate(matches):
        key = match.group(1).lower()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        value = text[match.end():end].strip(" \t:,-*;")
        if not value:
            continue
        if key == "and":
            key = last or "then"
        groups[key].append(value)
        last = key
    return groups


def split_task_id(text: str) -> tuple:
    match = TASK_ID_RE.match(text)
    if not match:
        return None, text.strip()
    rest = text[match.end():].strip()
    return match.group(0), rest or text.strip()


def extract_structure(
    lines: list[str], start: int, code_lines: set[int], rel: str, role: str
) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    requirements: list[dict] = []
    tasks: list[dict] = []
    markers: list[dict] = []
    findings: list[dict] = []
    current_delta = None
    current_req = None
    current_scen = None
    in_ac = False
    last_task = None

    for index in range(start, len(lines)):
        raw = lines[index]
        line_no = index + 1
        if index in code_lines:
            continue
        stripped = raw.strip()
        if not stripped:
            continue
        if NEEDS_CLARIFICATION in stripped.upper():
            markers.append({"kind": "needs-clarification", "line": line_no})

        heading = HEADING_RE.match(raw)
        if heading:
            level = len(heading.group(1))
            delta = DELTA_RE.match(raw)
            if delta:
                current_delta = delta.group(1).upper()
                current_req = None
                current_scen = None
                in_ac = False
                continue
            req = REQ_RE.match(raw)
            kiro = None if req else KIRO_REQ_RE.match(raw)
            if req or kiro:
                if req:
                    name = req.group(1).strip()
                else:
                    name = kiro.group(2).strip() or f"Requirement {kiro.group(1)}"
                current_req = {
                    "name": name,
                    "line": line_no,
                    "delta_op": current_delta,
                    "scenarios": [],
                    "acceptance_criteria": [],
                    "_body": [],
                }
                requirements.append(current_req)
                current_scen = None
                in_ac = False
                continue
            scenario = SCEN4_RE.match(raw)
            if scenario is None and SCEN3_RE.match(raw):
                scenario = SCEN3_RE.match(raw)
                findings.append(
                    finding(
                        "scenario-three-hashes",
                        rel,
                        line_no,
                        "«### Scenario:» usa 3 almohadillas; el escenario canónico usa 4.",
                    )
                )
            if scenario is not None:
                if current_req is None:
                    current_scen = None
                else:
                    current_scen = {
                        "name": scenario.group(1).strip() or "Scenario",
                        "line": line_no,
                        "given": [],
                        "when": [],
                        "then": [],
                        "_text": [],
                    }
                    current_req["scenarios"].append(current_scen)
                in_ac = False
                continue
            if AC_RE.match(raw):
                in_ac = True
                current_scen = None
                continue
            if level <= 2:
                current_delta = None
                current_req = None
                current_scen = None
                in_ac = False
            continue

        if role in EARS_ROLES and EARS_RE.search(stripped) and not SHALL_RE.search(stripped):
            findings.append(
                finding(
                    "ears-without-shall",
                    rel,
                    line_no,
                    f"línea EARS sin SHALL: {stripped[:120]}",
                )
            )

        task = TASK_RE.match(raw)
        if task:
            marker, body = task.group(1), task.group(2).strip()
            state = {" ": "todo", "x": "done", "X": "done", "~": "pending"}.get(marker)
            if marker == "~":
                findings.append(
                    finding(
                        "checkbox-pending",
                        rel,
                        line_no,
                        "«- [~]» se trata como tarea pendiente, no como otro estado.",
                    )
                )
            task_id, text = split_task_id(body)
            last_task = {
                "id": task_id,
                "text": text,
                "line": line_no,
                "state": state,
                "refs": [],
                "parallel": bool(PARALLEL_RE.search(body)),
            }
            tasks.append(last_task)
            continue

        refs = REFS_RE.match(stripped)
        if refs and last_task is not None:
            last_task["refs"].extend(
                ref.strip() for ref in refs.group(1).split(",") if ref.strip()
            )
            continue

        if current_scen is not None:
            groups = label_groups(stripped)
            for key in ("given", "when", "then"):
                current_scen[key].extend(groups[key])
            current_scen["_text"].append(stripped)
            continue

        if in_ac and current_req is not None:
            numbered = NUMBERED_RE.match(raw)
            if numbered:
                criterion_id, text = numbered.group(1), numbered.group(2).strip()
            elif stripped[:1] in {"-", "*", "+"}:
                criterion_id = str(len(current_req["acceptance_criteria"]) + 1)
                text = stripped.lstrip("-*+ ").strip()
            else:
                text = ""
                criterion_id = ""
            if text:
                current_req["acceptance_criteria"].append(
                    {"id": criterion_id, "text": text, "line": line_no}
                )
                groups = label_groups(text)
                if groups["given"] or groups["when"] or groups["then"]:
                    scenario = {
                        "name": f"AC {criterion_id}",
                        "line": line_no,
                        "given": groups["given"],
                        "when": groups["when"],
                        "then": groups["then"],
                        "_text": [text],
                    }
                else:
                    scenario = {
                        "name": f"AC {criterion_id}",
                        "line": line_no,
                        "given": [],
                        "when": [],
                        "then": [text],
                        "_text": [text],
                    }
                current_req["scenarios"].append(scenario)
            continue

        if current_req is not None:
            current_req["_body"].append(stripped)

    for req in requirements:
        req["text"] = " ".join(req.pop("_body")).strip()
        for scenario in req["scenarios"]:
            scenario["_all"] = " ".join([scenario["name"], *scenario["_text"]])
        blob = " ".join([req["text"], *(item["text"] for item in req["acceptance_criteria"])])
        if not req["scenarios"] and not req["acceptance_criteria"]:
            findings.append(
                finding(
                    "requirement-without-scenario",
                    rel,
                    req["line"],
                    f"el requisito «{req['name']}» no declara escenario ni criterio de aceptación.",
                )
            )
        vague = VAGUE_RE.search(blob)
        if vague and not METRIC_RE.search(blob):
            findings.append(
                finding(
                    "vague-requirement",
                    rel,
                    req["line"],
                    f"«{vague.group(0)}» sin métrica observable en el requisito «{req['name']}».",
                )
            )
        prescriptive = CODE_SPAN_RE.search(blob) or CALL_RE.search(blob)
        if prescriptive:
            findings.append(
                finding(
                    "prescriptive-requirement",
                    rel,
                    req["line"],
                    f"«{prescriptive.group(0)[:60]}» concreta el CÓMO; eso pertenece al design.",
                )
            )
        if len(req["scenarios"]) == 1 and not ERROR_SIGNAL_RE.search(req["scenarios"][0]["_all"]):
            findings.append(
                finding(
                    "scenario-without-error-case",
                    rel,
                    req["line"],
                    f"el único escenario de «{req['name']}» no cubre ningún caso de fallo.",
                )
            )

    return requirements, tasks, markers, findings


def public_requirement(req: dict) -> dict:
    return {
        "name": req["name"],
        "text": req["text"],
        "line": req["line"],
        "delta_op": req["delta_op"],
        "scenarios": [
            {
                "name": scenario["name"],
                "line": scenario["line"],
                "given": list(scenario["given"]),
                "when": list(scenario["when"]),
                "then": list(scenario["then"]),
            }
            for scenario in req["scenarios"]
        ],
        "acceptance_criteria": [dict(item) for item in req["acceptance_criteria"]],
    }


def unclassified_reason(
    profile: str, requirements: list, tasks: list, markers: list, sections: list
) -> str | None:
    if profile != "generic" or requirements or tasks or markers:
        return None
    if not sections:
        return "sin encabezados Markdown reconocibles."
    return (
        "encabezados sin anclas de requisito («### Requirement»), de escenario "
        "(«#### Scenario») ni de tarea («- [ ]»)."
    )


def analyze(walk_root: Path, path: Path) -> tuple[dict, list[dict]]:
    rel = path.relative_to(walk_root).as_posix()
    lines = read_lines(path)
    start = content_start(lines)
    headings, code_lines = scan_headings(lines, start)
    profile = detect_profile(rel, lines, start, code_lines)
    has_delta = any(
        DELTA_RE.match(lines[index])
        for index in range(start, len(lines))
        if index not in code_lines
    )
    role = role_for(rel, has_delta)
    requirements, tasks, markers, findings = extract_structure(
        lines, start, code_lines, rel, role
    )
    sections = [
        {"level": heading["level"], "title": heading["title"], "line": heading["line"]}
        for heading in headings
    ]
    title = next(
        (heading["title"] for heading in headings if heading["level"] == 1), path.stem
    )
    file_obj = {
        "path": rel,
        "role": role,
        "phase": PHASES.get(role),
        "profile": profile,
        "title": title,
        "unclassified_reason": unclassified_reason(
            profile, requirements, tasks, markers, sections
        ),
        "requirements": [public_requirement(req) for req in requirements],
        "tasks": tasks,
        "markers": markers,
        "sections": sections,
    }
    return file_obj, findings


def discover(walk_root: Path) -> tuple[list[Path], list[str]]:
    md_paths: list[Path] = []
    specs_dirs: list[str] = []
    for path in walk_root.rglob("*"):
        try:
            parts = path.relative_to(walk_root).parts
        except ValueError:
            continue
        if any(part in SKIP_DIRS for part in parts):
            continue
        if path.is_dir():
            if path.name == "specs":
                specs_dirs.append(Path(*parts).as_posix())
            continue
        if path.suffix.lower() != ".md":
            continue
        rel = Path(*parts).as_posix()
        if rel.lower() == "readme.md":
            continue
        md_paths.append(path)
    md_paths.sort(key=lambda item: item.relative_to(walk_root).as_posix())
    specs_dirs.sort()
    return md_paths, specs_dirs


def normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip().casefold()


def capability_findings(walk_root: Path, specs_dirs: list[str]) -> list[dict]:
    findings: list[dict] = []
    for relative in specs_dirs:
        directory = walk_root / relative
        try:
            children = sorted(directory.iterdir())
        except OSError:
            continue
        for child in children:
            if not child.is_dir() or (child / "spec.md").is_file():
                continue
            rel = child.relative_to(walk_root).as_posix()
            findings.append(
                finding(
                    "capability-without-delta-file",
                    f"{rel}/",
                    0,
                    f"la capacidad «{child.name}» no tiene spec.md.",
                )
            )
    return findings


def scan(root) -> dict:
    """Devuelve el modelo estructural del árbol `root` (sin tocar red ni reloj)."""
    root_path = Path(root)
    walk_root = root_path.resolve()
    files: list[dict] = []
    findings: list[dict] = []
    specs_dirs: list[str] = []
    if walk_root.is_dir():
        md_paths, specs_dirs = discover(walk_root)
        for path in md_paths:
            file_obj, file_findings = analyze(walk_root, path)
            files.append(file_obj)
            findings.extend(file_findings)

    detected = sorted({file_obj["profile"] for file_obj in files if file_obj["profile"] != "generic"})
    if not detected:
        tree_profile = "generic"
    elif len(detected) == 1:
        tree_profile = detected[0]
    else:
        tree_profile = "mixed"

    # La regla de capacidad solo tiene sentido dentro de un árbol SDD reconocido;
    # fuera de él, una carpeta llamada «specs» puede ser cualquier cosa.
    if tree_profile != "generic":
        findings.extend(capability_findings(walk_root, specs_dirs))

    base_names = {
        normalize_name(requirement["name"])
        for file_obj in files
        if file_obj["role"] == "specs"
        for requirement in file_obj["requirements"]
        if requirement["delta_op"] is None
    }
    for file_obj in files:
        for requirement in file_obj["requirements"]:
            if requirement["delta_op"] not in {"MODIFIED", "REMOVED", "RENAMED"}:
                continue
            if normalize_name(requirement["name"]) in base_names:
                continue
            findings.append(
                finding(
                    "modified-without-target",
                    file_obj["path"],
                    requirement["line"],
                    f"el delta {requirement['delta_op']} no encuentra «{requirement['name']}» "
                    "entre los requisitos de los specs vigentes.",
                )
            )

    has_non_goals = any(
        section["level"] >= NON_GOALS_HEADING_LEVEL and NON_GOALS_RE.match(section["title"])
        for file_obj in files
        for section in file_obj["sections"]
    )
    if not has_non_goals:
        proposals = [file_obj["path"] for file_obj in files if file_obj["role"] == "proposal"]
        findings.append(
            finding(
                "missing-non-goals",
                proposals[0] if proposals else None,
                0,
                "ningún documento del árbol declara no-objetivos (Non-Goals / Fuera de alcance).",
            )
        )

    findings.sort(key=lambda item: (item["path"] or "", item["line"], item["kind"]))

    return {
        "root": str(root),
        "tree_profile": tree_profile,
        "has_non_goals": has_non_goals,
        "files": files,
        "findings": findings,
        "unknown_files": [
            file_obj["path"]
            for file_obj in files
            if file_obj["unclassified_reason"] is not None
        ],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Descubre un árbol de documentos SDD y produce su modelo estructural"
    )
    parser.add_argument("directorio", help="directorio raíz del árbol de documentos SDD")
    parser.add_argument(
        "--json",
        action="store_true",
        help="emite el modelo en una sola línea (por defecto va indentado)",
    )
    args = parser.parse_args(argv)

    root = Path(args.directorio)
    if not root.is_dir():
        print(f"ERROR: {args.directorio} no es un directorio.", file=sys.stderr)
        return 2

    model = scan(args.directorio)
    print(
        json.dumps(
            model,
            sort_keys=True,
            ensure_ascii=False,
            indent=None if args.json else 2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
