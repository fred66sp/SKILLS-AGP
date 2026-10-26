#!/usr/bin/env python3
"""Herramienta determinista del paquete de ADR.

Uso:
    python3 adr.py new --title "..." [opciones]
    python3 adr.py status <archivo> --status <valor> [opciones]
    python3 adr.py bootstrap [opciones]
    python3 adr.py check --root <raíz> [opciones]

Códigos de salida:
    0  operación correcta, sin hallazgos
    1  la operación falla o la puerta encuentra defectos
    2  error de uso
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_ROOT / "assets"
ADR_DIR_CANDIDATES = ("docs/decisions", "adr", "docs/adr", "docs/adrs", "decisions")
INDEX_NAMES = ("README.md", "index.md")
STATUSES = ("proposed", "accepted", "rejected", "deprecated")
NUMBERED_RE = re.compile(r"^(\d{1,8})-(.+)\.md$")
PLACEHOLDER_RE = re.compile(r"\{[^{}\n]{3,}\}")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
CONTEXT_RE = re.compile(r"^##\s+(Contexto y problema|Contexto|Context and Problem Statement)\s*$", re.I | re.M)
DECISION_RE = re.compile(r"^##\s+(Decisión|Decision|Resultado de la decisión|Decision Outcome)\s*$", re.I | re.M)
CONSEQUENCES_RE = re.compile(r"^###?\s+(Consecuencias|Consequences)\s*$", re.I | re.M)
HEADING_RE = re.compile(r"^#\s+(.+)$", re.M)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SUPERSEDED_RE = re.compile(r"^superseded by\s+\[[^\]]+\]\(([^)]+)\)$", re.I)


class UsageError(Exception):
    """Argumento o estado de entrada inválido."""


class AdrError(Exception):
    """Operación que no se puede completar sobre el repositorio."""


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    dashed = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return dashed or "decision"


def to_posix(path: Path) -> str:
    return path.as_posix()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            data: dict[str, str] = {}
            for line in lines[1:index]:
                if ":" in line and not line[:1].isspace():
                    key, value = line.split(":", 1)
                    data[key.strip()] = value.strip().strip('"').strip("'")
            return data, "\n".join(lines[index + 1 :])
    return {}, text


def fenced_lines(text: str) -> list[str]:
    """Líneas fuera de bloques de código, para no leer marcadores de un ejemplo."""
    kept, fence = [], None
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)[0] * 3
                continue
            kept.append(line)
        elif match and match.group(1).startswith(fence):
            fence = None
    return kept


def md_files(adr_dir: Path) -> list[Path]:
    try:
        return sorted(path for path in adr_dir.iterdir() if path.is_file() and path.suffix == ".md")
    except OSError:
        return []


def adr_files(adr_dir: Path) -> list[Path]:
    return [path for path in md_files(adr_dir) if path.name not in INDEX_NAMES]


def find_adr_dir(root: Path) -> Path | None:
    for name in ADR_DIR_CANDIDATES:
        candidate = root / name
        if candidate.is_dir():
            return candidate
    return None


def detect_strategy(adr_dir: Path) -> str:
    files = adr_files(adr_dir)
    if any(NUMBERED_RE.match(path.name) for path in files):
        return "number"
    return "slug" if files else "number"


def numbering_width(adr_dir: Path) -> int:
    for path in adr_files(adr_dir):
        match = NUMBERED_RE.match(path.name)
        if match:
            return len(match.group(1))
    return 4


def next_number(adr_dir: Path) -> int:
    highest = 0
    for path in adr_files(adr_dir):
        match = NUMBERED_RE.match(path.name)
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


def target_name(adr_dir: Path, strategy: str, title: str) -> str:
    slug = slugify(title)
    if strategy == "number":
        return f"{next_number(adr_dir):0{numbering_width(adr_dir)}d}-{slug}.md"
    candidate, counter = f"{slug}.md", 2
    while (adr_dir / candidate).exists():
        candidate, counter = f"{slug}-{counter}.md", counter + 1
    return candidate


def template_path(name: str) -> Path:
    path = TEMPLATES / f"adr-{name}.md"
    if not path.is_file():
        raise AdrError(f"no existe la plantilla {path}")
    return path


def render_new(raw: str, title: str, status: str, day: str, deciders: str, technical_story: str) -> str:
    lines, out, seen_story = raw.splitlines(), [], False
    for line in lines:
        if re.match(r"^status\s*:", line):
            out.append(f"status: {status}")
        elif re.match(r"^date\s*:", line):
            out.append(f"date: {day}")
        elif re.match(r"^decision-makers\s*:", line):
            out.append(f'decision-makers: "{deciders}"')
            if technical_story and not seen_story:
                out.append(f'technical-story: "{technical_story}"')
                seen_story = True
        elif re.match(r"^(consulted|informed)\s*:", line) and not deciders:
            continue
        elif re.match(r"^#\s+\{", line):
            out.append(f"# {title}")
        else:
            out.append(line)
    return "\n".join(out).rstrip() + "\n"


def choose_index(adr_dir: Path) -> Path:
    for name in INDEX_NAMES:
        candidate = adr_dir / name
        if candidate.is_file():
            return candidate
    return adr_dir / "README.md"


def ensure_index(index_file: Path, adr_dir_label: str) -> None:
    if index_file.exists():
        return
    template = TEMPLATES / "adr-index.md"
    if not template.is_file():
        raise AdrError(f"no existe la plantilla {template}")
    write(index_file, read(template).replace("{ADR_DIR}", adr_dir_label))


def index_entry(title: str, rel_link: str, status: str, day: str) -> str:
    return f"- [{title}]({rel_link}) ({status}, {day})"


def insert_index_entry(index_file: Path, entry: str, rel_link: str) -> bool:
    text = read(index_file)
    if rel_link in text:
        return False
    lines = text.rstrip("\n").splitlines()
    heading = next((i for i, line in enumerate(lines) if re.match(r"^##\s+ADR\s*$", line, re.I)), None)
    if heading is None:
        lines.extend(["", entry])
    else:
        end = len(lines)
        for i in range(heading + 1, len(lines)):
            if re.match(r"^##\s+", lines[i]):
                end = i
                break
        last = next((i for i in range(end - 1, heading, -1) if re.match(r"^[-*]\s+", lines[i])), None)
        lines.insert(last + 1 if last is not None else heading + 1, entry)
    write(index_file, "\n".join(lines) + "\n")
    return True


def create_adr(
    root: Path,
    adr_dir: Path,
    title: str,
    template: str,
    strategy: str,
    status: str,
    deciders: str,
    technical_story: str,
    update_index: bool,
    index_file: Path | None,
    dry_run: bool,
) -> dict:
    if status not in STATUSES:
        raise UsageError(f"estado no admitido al crear: {status}")
    title = title.strip()
    if not title:
        raise UsageError("--title no puede estar vacío")
    if not dry_run:
        adr_dir.mkdir(parents=True, exist_ok=True)
    chosen_strategy = detect_strategy(adr_dir) if strategy == "auto" else strategy
    name = target_name(adr_dir, chosen_strategy, title)
    out = adr_dir / name
    if out.exists():
        raise AdrError(f"el ADR ya existe: {out}")

    index_path, rel_link = None, None
    if update_index:
        index_path = index_file or choose_index(adr_dir)
        try:
            rel_link = to_posix(Path(out).relative_to(index_path.parent))
        except ValueError as exc:
            raise UsageError("--index-file debe quedar dentro del directorio del ADR") from exc

    day = date.today().isoformat()
    rendered = render_new(read(template_path(template)), title, status, day, deciders, technical_story)
    index_changed = False
    if not dry_run:
        write(out, rendered)
        if index_path and rel_link:
            ensure_index(index_path, to_posix(adr_dir.relative_to(root)))
            index_changed = insert_index_entry(index_path, index_entry(title, rel_link, status, day), rel_link)
    return {
        "createdAdrPath": str(out),
        "createdAdrRelPath": to_posix(out.relative_to(root)),
        "title": title,
        "status": status,
        "template": template,
        "strategy": chosen_strategy,
        "date": day,
        "indexPath": str(index_path) if index_path else None,
        "indexUpdated": bool(index_path),
        "indexChanged": index_changed,
        "dryRun": dry_run,
    }


def update_index_status(index_file: Path, adr_name: str, status: str, day: str) -> bool:
    if not index_file.is_file():
        return False
    text = read(index_file)
    pattern = re.compile(r"^([-*]\s+\[[^\]]*\]\([^)]*" + re.escape(adr_name) + r"\))\s*\([^)]*\)\s*$", re.M)
    updated, count = pattern.subn(rf"\1 ({status}, {day})", text)
    if count:
        write(index_file, updated)
    return bool(count)


def set_status(path: Path, status: str, superseded_by: str, day: str) -> dict:
    if not path.is_file():
        raise AdrError(f"no existe el ADR: {path}")
    text = read(path)
    data, _ = frontmatter(text)
    if "status" not in data:
        raise AdrError(f"{path}: no tiene frontmatter con 'status'")
    if status == "superseded":
        if not superseded_by:
            raise UsageError("--status superseded exige --superseded-by")
        target = (path.parent / superseded_by).resolve()
        if not target.is_file():
            raise AdrError(f"--superseded-by no resuelve: {superseded_by}")
        label = "ADR-" + (target.stem.split("-", 1)[0] if NUMBERED_RE.match(target.name) else target.stem)
        value = f"superseded by [{label}]({to_posix(Path(superseded_by))})"
    elif status in STATUSES:
        value = status
    else:
        raise UsageError(f"estado no admitido: {status}")

    lines, out = text.splitlines(), []
    for line in lines:
        if re.match(r"^status\s*:", line):
            out.append(f"status: {value}")
        elif re.match(r"^date\s*:", line):
            out.append(f"date: {day}")
        else:
            out.append(line)
    write(path, "\n".join(out) + "\n")
    index_file = choose_index(path.parent)
    index_changed = update_index_status(index_file, path.name, status, day)
    return {
        "filePath": str(path),
        "fileRelPath": to_posix(path),
        "status": value,
        "date": day,
        "indexChanged": index_changed,
    }


def safe_rel(path: Path, root: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


def finding(code: str, path: Path, message: str) -> dict:
    return {"code": code, "path": to_posix(path), "message": message}


def check_adr(path: Path, root: Path, findings: list[dict]) -> None:
    text = read(path)
    data, body = frontmatter(text)
    rel = safe_rel(path, root)

    if not data:
        findings.append(finding("frontmatter", rel, "falta el frontmatter"))
        return
    status = data.get("status", "")
    if not status:
        findings.append(finding("frontmatter", rel, "falta 'status'"))
    elif status not in STATUSES and not SUPERSEDED_RE.match(status):
        findings.append(finding("frontmatter", rel, f"estado no admitido: '{status}'"))
    day = data.get("date", "")
    if not DATE_RE.match(day):
        findings.append(finding("frontmatter", rel, f"'date' debe ser AAAA-MM-DD, es '{day}'"))
    else:
        try:
            date.fromisoformat(day)
        except ValueError:
            findings.append(finding("frontmatter", rel, f"'date' no es una fecha real: '{day}'"))
    if not data.get("decision-makers", "").strip():
        findings.append(finding("frontmatter", rel, "'decision-makers' está vacío"))

    heading = HEADING_RE.search(body)
    if not heading or re.search(r"\{|\}", heading.group(1)):
        findings.append(finding("estructura", rel, "falta un título H1 concreto"))
    for label, pattern in (("Contexto y problema", CONTEXT_RE), ("Decisión", DECISION_RE), ("Consecuencias", CONSEQUENCES_RE)):
        if not pattern.search(body):
            findings.append(finding("estructura", rel, f"falta la sección '{label}'"))

    for line in fenced_lines(body):
        for match in PLACEHOLDER_RE.findall(line):
            findings.append(finding("plantilla", rel, f"marcador sin sustituir: {match}"))

    superseded = SUPERSEDED_RE.match(status)
    if superseded:
        link = superseded.group(1)
        target = (path.parent / link).resolve()
        if not target.is_file():
            findings.append(finding("supersede", rel, f"el sustituto no existe: {link}"))
        else:
            backlink = re.search(re.escape(path.name), read(target))
            if not backlink:
                findings.append(finding("supersede", rel, f"el sustituto {link} no enlaza de vuelta a {path.name}"))

    numbered = NUMBERED_RE.match(path.name)
    expected = numbered.group(1) if numbered else None
    name_part = path.stem[len(expected) + 1 :] if expected else path.stem
    if name_part != slugify(name_part):
        findings.append(finding("nombres", rel, "el nombre debe ir en minúsculas con guiones y sin acentos"))
    if expected and len(expected) != numbering_width(path.parent):
        findings.append(finding("nombres", rel, f"el número no usa el ancho del directorio ({numbering_width(path.parent)} dígitos)"))


def check_index(adr_dir: Path, root: Path, findings: list[dict]) -> None:
    index_file = next((adr_dir / name for name in INDEX_NAMES if (adr_dir / name).is_file()), None)
    files = adr_files(adr_dir)
    if index_file is None:
        if files:
            findings.append(finding("indice", safe_rel(adr_dir, root), "hay ADR sin índice README.md o index.md"))
        return
    text = read(index_file)
    rel = safe_rel(index_file, root)
    for path in files:
        if path.name not in text:
            findings.append(finding("indice", rel, f"no enlaza {path.name}"))
    for line in fenced_lines(text):
        for target in LINK_RE.findall(line):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if not (index_file.parent / target.split("#", 1)[0]).exists():
                findings.append(finding("indice", rel, f"entrada rota: {target}"))


def check_tree(root: Path, adr_dir: Path | None) -> list[dict]:
    if adr_dir is None:
        return []
    findings: list[dict] = []
    numbers: dict[str, list[str]] = {}
    for path in adr_files(adr_dir):
        check_adr(path, root, findings)
        match = NUMBERED_RE.match(path.name)
        if match:
            numbers.setdefault(match.group(1), []).append(path.name)
    for number, names in numbers.items():
        if len(names) > 1:
            findings.append(finding("nombres", safe_rel(adr_dir, root), f"número {number} repetido: {', '.join(names)}"))
    check_index(adr_dir, root, findings)
    return findings


def emit(payload: dict, as_json: bool, text: str) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(text)


def cmd_new(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if not root.is_dir():
        raise AdrError(f"la raíz no existe: {root}")
    adr_dir = Path(args.dir).resolve() if args.dir else (find_adr_dir(root) or root / "adr")
    if not adr_dir.is_dir() and args.no_create_dir:
        raise AdrError(f"no existe el directorio de ADR: {adr_dir}")
    if adr_dir != root and not adr_dir.is_relative_to(root):
        raise UsageError("--dir debe quedar dentro de --root")
    index_file = None
    if args.index_file:
        index_file = Path(args.index_file)
        index_file = index_file if index_file.is_absolute() else (root / index_file).resolve()
    payload = create_adr(
        root, adr_dir, args.title.strip(), args.template, args.strategy,
        args.status.strip(), args.deciders.strip(), args.technical_story.strip(),
        args.update_index, index_file, args.dry_run,
    )
    payload["ok"] = True
    payload["operation"] = "new"
    emit(payload, args.json, ("[dry-run] " if args.dry_run else "") + payload["createdAdrPath"])
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    payload = set_status(path, args.status.strip(), args.superseded_by, args.date)
    payload.update({"ok": True, "operation": "status"})
    emit(payload, args.json, f"{payload['filePath']}\nstatus: {payload['status']}")
    return 0


def cmd_bootstrap(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if not root.is_dir():
        raise AdrError(f"la raíz no existe: {root}")
    adr_dir = (Path(args.dir) if args.dir else Path("adr"))
    adr_dir = adr_dir if adr_dir.is_absolute() else (root / adr_dir).resolve()
    if adr_dir != root and not adr_dir.is_relative_to(root):
        raise UsageError("--dir debe quedar dentro de --root")
    index_file = adr_dir / "README.md"
    index_existed = index_file.exists()
    if args.first_status not in STATUSES:
        raise UsageError(f"estado no admitido al inicializar: {args.first_status}")
    if args.force_index and adr_files(adr_dir):
        raise UsageError("--force-index no puede sobrescribir el índice de un registro con ADR")
    first = None
    if not args.dry_run:
        adr_dir.mkdir(parents=True, exist_ok=True)
        if not index_existed or args.force_index:
            ensure_index(index_file, to_posix(adr_dir.relative_to(root)))
        if not adr_files(adr_dir):
            strategy = detect_strategy(adr_dir) if args.strategy == "auto" else args.strategy
            out = adr_dir / target_name(adr_dir, strategy, args.first_title)
            day = date.today().isoformat()
            rendered = (
                read(TEMPLATES / "adr-bootstrap.md")
                .replace("{STATUS}", args.first_status)
                .replace("{DATE}", day)
                .replace("{DECIDERS}", args.deciders.strip())
                .replace("{TITLE}", args.first_title.strip())
                .replace("{ADR_DIR}", to_posix(adr_dir.relative_to(root)))
            )
            write(out, rendered)
            rel_link = to_posix(Path(out).relative_to(index_file.parent))
            insert_index_entry(index_file, index_entry(args.first_title.strip(), rel_link, args.first_status, day), rel_link)
            first = {
                "createdAdrPath": str(out),
                "createdAdrRelPath": to_posix(out.relative_to(root)),
                "title": args.first_title.strip(),
                "status": args.first_status,
                "template": "bootstrap",
                "strategy": strategy,
                "date": day,
                "indexPath": str(index_file),
                "indexUpdated": True,
                "indexChanged": True,
                "dryRun": False,
            }
    payload = {
        "ok": True,
        "operation": "bootstrap",
        "adrDir": str(adr_dir),
        "adrDirRelPath": to_posix(adr_dir.relative_to(root)),
        "indexPath": str(index_file),
        "indexExistedBefore": index_existed,
        "indexWritten": (not args.dry_run) and (not index_existed or args.force_index),
        "firstAdr": first,
        "date": date.today().isoformat(),
        "dryRun": args.dry_run,
    }
    emit(payload, args.json, f"ADRs en {adr_dir}\nÍndice: {index_file}" + ("\n[dry-run]" if args.dry_run else ""))
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if not root.is_dir():
        raise AdrError(f"la raíz no existe: {root}")
    adr_dir = Path(args.dir).resolve() if args.dir else find_adr_dir(root)
    if adr_dir is not None and not adr_dir.is_dir():
        findings = [finding("estructura", safe_rel(adr_dir, root), "no existe el directorio de ADR")]
    else:
        findings = check_tree(root, adr_dir)
    payload = {
        "ok": not findings,
        "operation": "check",
        "adrDir": str(adr_dir) if adr_dir else None,
        "findings": findings,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        for item in findings:
            print(f"[{item['code']}] {item['path']}: {item['message']}", file=sys.stderr)
        print(f"{len(findings)} hallazgos en {adr_dir or root}")
    return 1 if findings else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="adr.py", description="Gestión determinista de Architecture Decision Records")
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="crear un ADR desde una plantilla")
    new.add_argument("--title", required=True)
    new.add_argument("--root", default=".")
    new.add_argument("--dir")
    new.add_argument("--template", choices=("simple", "madr"), default="simple")
    new.add_argument("--strategy", choices=("auto", "number", "slug"), default="auto")
    new.add_argument("--status", default="proposed")
    new.add_argument("--deciders", default="")
    new.add_argument("--technical-story", default="")
    new.add_argument("--update-index", action=argparse.BooleanOptionalAction, default=True, help="actualizar el índice (por defecto sí)")
    new.add_argument("--index-file")
    new.add_argument("--no-create-dir", action="store_true")
    new.add_argument("--dry-run", action="store_true")
    new.add_argument("--json", action="store_true")
    new.set_defaults(func=cmd_new)

    status = sub.add_parser("status", help="cambiar el estado de un ADR")
    status.add_argument("path")
    status.add_argument("--status", required=True)
    status.add_argument("--superseded-by", default="")
    status.add_argument("--date", default=date.today().isoformat())
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=cmd_status)

    bootstrap = sub.add_parser("bootstrap", help="crear directorio, índice y primer ADR")
    bootstrap.add_argument("--root", default=".")
    bootstrap.add_argument("--dir")
    bootstrap.add_argument("--first-title", default="Adoptar registros de decisión de arquitectura")
    bootstrap.add_argument("--first-status", default="accepted")
    bootstrap.add_argument("--deciders", default="")
    bootstrap.add_argument("--strategy", choices=("auto", "number", "slug"), default="number")
    bootstrap.add_argument("--force-index", action="store_true")
    bootstrap.add_argument("--dry-run", action="store_true")
    bootstrap.add_argument("--json", action="store_true")
    bootstrap.set_defaults(func=cmd_bootstrap)

    check = sub.add_parser("check", help="puerta determinista del registro")
    check.add_argument("--root", default=".")
    check.add_argument("--dir")
    check.add_argument("--json", action="store_true")
    check.set_defaults(func=cmd_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except UsageError as exc:
        if getattr(args, "json", False):
            print(json.dumps({"ok": False, "operation": args.command, "error": str(exc)}, ensure_ascii=False))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except (AdrError, OSError) as exc:
        if getattr(args, "json", False):
            print(json.dumps({"ok": False, "operation": args.command, "error": str(exc)}, ensure_ascii=False))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
