#!/usr/bin/env python3
"""Valida la estructura, los metadatos, las rutas y los recibos del repositorio.

Uso:
    python scripts/check-repo.py [--root <directorio>]

Comprueba:
- frontmatter de cada skill: nombre igual a la carpeta, formato válido y
  descripción de 1 a 1024 caracteres;
- que cada skill de `src/` tenga su enrutador en `.skills/` y que cada
  enrutador resuelva su contrato desde su propio directorio;
- que los enlaces Markdown relativos del repositorio resuelvan;
- que los recibos de `docs/` coincidan con el `sha256` y los bytes reales de
  su especificación y su HTML, y que la especificación esté en LF;
- que cada skill canónica declare una versión SemVer en `metadata.version` y
  que no contradiga sus etiquetas `<skill>/v<versión>` publicadas;
- que los scripts Python compilen y los scripts de shell tengan sintaxis
  válida cuando `bash` está disponible.

Códigos de salida:
    0  todo correcto
    1  se ha detectado al menos un defecto
    2  error de uso
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

import skill_versions

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*([^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
FENCE_RE = re.compile(r"^\s*(```+|~~~+)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
ROUTER_MARKER = "Enrutador de la skill"
SKILL_REF_RE = re.compile(r"`([^`\n]*\bsrc/[a-z0-9-]+/SKILL\.md)`")
SKILL_DIR_REF_RE = re.compile(r"`([^`\n]*\bsrc/[a-z0-9-]+/)`")
EXCLUDED_DIRS = {
    ".git", ".opencode", ".atl", ".pi", ".codegraph", ".worktrees",
    "archify", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
}


def read(path):
    return path.read_text(encoding="utf-8")


def frontmatter(path, errors):
    text = read(path)
    if not text.startswith("---"):
        errors.append(f"[metadatos] {path}: falta el frontmatter")
        return {}, text

    end = text.find("\n---", 3)
    if end < 0:
        errors.append(f"[metadatos] {path}: el frontmatter no se cierra")
        return {}, text

    data, key = {}, None
    for line in text[3:end].splitlines():
        if not line.strip():
            continue
        if line[:1] in (" ", "\t") and key:
            data[key] = data[key] + " " + line.strip()
        elif ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip('"')
    return data, text[end + 4:]


def check_metadata(skill_md, expected_name, errors):
    data, _ = frontmatter(skill_md, errors)
    name = data.get("name", "")
    description = data.get("description", "")

    if name != expected_name:
        errors.append(
            f"[metadatos] {skill_md}: name='{name}' no coincide con la carpeta '{expected_name}'"
        )
    if not NAME_RE.match(name):
        errors.append(
            f"[metadatos] {skill_md}: name='{name}' no es minúsculas, números y guiones simples"
        )
    if not 1 <= len(description) <= 1024:
        errors.append(
            f"[metadatos] {skill_md}: description tiene {len(description)} caracteres, debe tener entre 1 y 1024"
        )


def check_version(skill_md, errors):
    version = skill_versions.read_version(read(skill_md))
    if version is None:
        errors.append(f"[versiones] {skill_md}: falta metadata.version")
    elif not skill_versions.is_version(version):
        errors.append(
            f"[versiones] {skill_md}: versión '{version}' no es SemVer MAJOR.MINOR.PATCH"
        )


def check_published_versions(root, src_names, errors, notes):
    tags = skill_versions.git_tags(root)
    if tags is None:
        notes.append(
            "[versiones] Git no disponible: no se pudieron comprobar las etiquetas publicadas"
        )
        return
    if skill_versions.is_shallow(root):
        notes.append(
            "[versiones] clon superficial: las etiquetas publicadas pueden estar "
            "incompletas; usa `fetch-depth: 0`"
        )

    by_skill, problems = skill_versions.skill_tags(tags)
    for tag, problem in problems:
        errors.append(f"[versiones] etiqueta '{tag}': {problem}")
    for name in sorted(by_skill):
        if name not in src_names:
            errors.append(
                f"[versiones] etiqueta '{name}/v...': la skill '{name}' no existe en src/"
            )
        elif len(by_skill[name]) != len(set(by_skill[name])):
            errors.append(f"[versiones] {name}: etiqueta duplicada para la misma versión")

    for name in src_names:
        skill_md = root / "src" / name / "SKILL.md"
        if not skill_md.is_file():
            continue
        declared = skill_versions.read_version(read(skill_md))
        if not skill_versions.is_version(declared or ""):
            continue
        published = by_skill.get(name, [])
        if not published:
            continue
        latest = max(published, key=skill_versions.version_key)
        if skill_versions.version_key(declared) < skill_versions.version_key(latest):
            errors.append(
                f"[versiones] {skill_md}: la versión declarada {declared} es menor "
                f"que la publicada {latest} ({name}/v{latest})"
            )


def prose_lines(text):
    """Devuelve (número de línea, texto) fuera del frontmatter y de los bloques de código."""
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() in ("---", "..."):
                start = index + 1
                break
    kept, fence = [], None
    for index in range(start, len(lines)):
        line = lines[index]
        match = FENCE_RE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)[0] * 3
                continue
            kept.append((index + 1, line))
        elif match and match.group(1).startswith(fence):
            fence = None
    return kept


def check_links(root, errors):
    for path in sorted(root.rglob("*.md")):
        if any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
            continue
        text = read(path)
        for number, line in prose_lines(text):
            for target in LINK_RE.findall(INLINE_CODE_RE.sub("", line)):
                if not target or target.startswith(("#", "//")) or SCHEME_RE.match(target):
                    continue
                cleaned = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not cleaned:
                    continue
                if cleaned.startswith("/"):
                    resolved = root / cleaned.lstrip("/")
                else:
                    resolved = path.parent / cleaned
                if not resolved.exists():
                    errors.append(
                        f"[enlaces] {path}:{number}: no resuelve '{target}'"
                    )


def check_router(router_md, name, canonical_md, errors):
    _, text = frontmatter(router_md, errors)
    refs = set(SKILL_REF_RE.findall(text)) | set(SKILL_DIR_REF_RE.findall(text))
    required = f"../../src/{name}/SKILL.md"
    if required not in refs:
        errors.append(
            f"[enrutadores] {router_md}: falta la referencia `{required}`"
        )

    for raw in sorted(refs):
        if raw.startswith("/") or SCHEME_RE.match(raw):
            errors.append(f"[enrutadores] {router_md}: la ruta '{raw}' no es relativa")
            continue
        resolved = (router_md.parent / raw).resolve()
        expected = canonical_md.resolve() if raw.endswith("/SKILL.md") else canonical_md.parent.resolve()
        if not resolved.exists():
            errors.append(
                f"[enrutadores] {router_md}: '{raw}' no resuelve desde la carpeta del enrutador"
            )
        elif resolved != expected:
            errors.append(
                f"[enrutadores] {router_md}: '{raw}' no apunta al contrato '{canonical_md}'"
            )


def check_skills(root, errors, notes):
    src_root, skills_root = root / "src", root / ".skills"
    src_names = sorted(path.name for path in src_root.iterdir() if path.is_dir()) if src_root.is_dir() else []
    router_names = sorted(path.name for path in skills_root.iterdir() if path.is_dir()) if skills_root.is_dir() else []

    for name in src_names:
        skill_md = src_root / name / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"[estructura] {src_root / name}: falta SKILL.md")
            continue
        check_metadata(skill_md, name, errors)
        check_version(skill_md, errors)
        for human in ("README.md", "CHANGELOG.md", "INSTALLATION.md"):
            if (src_root / name / human).exists():
                errors.append(f"[estructura] {src_root / name / human}: documento humano dentro del paquete")
        router_md = skills_root / name / "SKILL.md"
        if not router_md.is_file():
            errors.append(f"[enrutadores] {skills_root / name}: falta el enrutador de '{name}'")

    for name in router_names:
        router_md = skills_root / name / "SKILL.md"
        if not router_md.is_file():
            errors.append(f"[estructura] {skills_root / name}: falta SKILL.md")
            continue
        canonical_md = src_root / name / "SKILL.md"
        _, text = frontmatter(router_md, errors)
        is_router = ROUTER_MARKER in text
        if canonical_md.is_file():
            if not is_router:
                errors.append(f"[enrutadores] {router_md}: falta el marcador de enrutador")
                continue
            check_metadata(router_md, name, errors)
            check_router(router_md, name, canonical_md, errors)
        elif is_router:
            errors.append(
                f"[enrutadores] {router_md}: enrutador huérfano, no existe {canonical_md}"
            )
        else:
            check_metadata(router_md, name, errors)

    check_published_versions(root, src_names, errors, notes)


def check_receipts(root, errors):
    docs = root / "docs"
    if not docs.is_dir():
        return

    for spec in sorted(docs.glob("*/*.json")):
        if spec.name.endswith(".delivery.json"):
            continue
        receipt = spec.with_name(spec.stem + ".delivery.json")
        if not receipt.is_file():
            errors.append(f"[recibos] {spec}: falta {receipt.name}")

    for html in sorted(docs.glob("*/*.html")):
        if html.name == "index.html":
            continue
        receipt = html.with_name(html.stem + ".delivery.json")
        if not receipt.is_file():
            errors.append(f"[recibos] {html}: falta {receipt.name}")

    for receipt in sorted(docs.glob("*/*.delivery.json")):
        try:
            data = json.loads(read(receipt))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"[recibos] {receipt}: no se puede leer ({exc})")
            continue
        if data.get("schemaVersion") != 1:
            errors.append(f"[recibos] {receipt}: schemaVersion distinto de 1")
        spec = receipt.with_name(receipt.name[: -len(".delivery.json")] + ".json")
        html = receipt.with_name(receipt.name[: -len(".delivery.json")] + ".html")
        for kind, path in (("specification", spec), ("artifact", html)):
            if not path.is_file():
                errors.append(f"[recibos] {receipt}: no existe {path}")
                continue
            raw = path.read_bytes()
            actual = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
            if data.get(kind) != actual:
                errors.append(
                    f"[recibos] {receipt}: {kind} no coincide con {path.name} "
                    f"(registro {data.get(kind)}, real {actual})"
                )
        if spec.is_file() and b"\r" in spec.read_bytes():
            errors.append(f"[recibos] {receipt}: {spec.name} tiene CR; el spec debe estar en LF")


def check_scripts(root, errors, notes):
    for path in sorted(root.rglob("*.py")):
        if any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
            continue
        try:
            compile(read(path), str(path), "exec")
        except (OSError, SyntaxError) as exc:
            errors.append(f"[python] {path}: {exc}")

    bash = shutil.which("bash")
    if not bash:
        notes.append("[shell] bash no disponible: sintaxis de los .sh no comprobada")
        return
    for path in sorted(root.rglob("*.sh")):
        if any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
            continue
        result = subprocess.run(
            [bash, "-n", path.name], cwd=str(path.parent), capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        if result.returncode != 0:
            errors.append(f"[shell] {path}: {result.stderr.strip() or 'sintaxis inválida'}")


def validate(root):
    root = Path(root).resolve()
    errors, notes = [], []
    check_skills(root, errors, notes)
    check_links(root, errors)
    check_receipts(root, errors)
    check_scripts(root, errors, notes)
    return errors, notes


def main(argv=None):
    parser = argparse.ArgumentParser(description="Valida estructura, rutas y recibos del repositorio")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]), help="Raíz del repositorio")
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"ERROR: la raíz no es un directorio: {root}", file=sys.stderr)
        return 2
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    errors, notes = validate(root)
    for note in notes:
        print(note)
    for error in errors:
        print(error, file=sys.stderr)
    print(f"\n{len(errors)} errores en {root}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
