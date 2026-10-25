#!/usr/bin/env python3
"""Versión declarada y publicada de cada skill canónica.

La versión vive en `metadata.version` del frontmatter de `src/<skill>/SKILL.md`
y se publica con la etiqueta `<skill>/v<MAJOR.MINOR.PATCH>`.
"""

import os
import re
import subprocess
from pathlib import Path

VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
TAG_RE = re.compile(r"^([a-z0-9]+(?:-[a-z0-9]+)*)/v(.+)$")
PARTS = ("patch", "minor", "major")


class VersionError(Exception):
    """Error de uso o de estado que impide versionar."""


def is_version(value):
    return bool(VERSION_RE.fullmatch(value.strip()))


def read_text(path):
    """Lee sin normalizar saltos de línea para poder preservarlos al escribir."""
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def version_key(value):
    return tuple(int(part) for part in value.split("."))


def next_version(value, part):
    if part not in PARTS:
        raise VersionError(f"incremento desconocido '{part}': usa {', '.join(PARTS)}")
    major, minor, patch = version_key(value)
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def _frontmatter_range(lines):
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() in ("---", "..."):
            return 1, index
    return None


def _version_location(lines):
    bounds = _frontmatter_range(lines)
    if bounds is None:
        return None
    start, end = bounds
    for index in range(start, end):
        if lines[index].rstrip() == "metadata:":
            for inner in range(index + 1, end):
                line = lines[inner]
                if not line.strip():
                    continue
                if not line[:1].isspace():
                    break
                match = re.match(r"^([ \t]+)version:([ \t]*)(.*)$", line)
                if match:
                    indent, spacing, raw = match.groups()
                    quote = raw[:1] if raw[:1] in ("'", '"') else ""
                    return inner, indent, spacing, quote
    return None


def read_version(text):
    location = _version_location(text.splitlines())
    if location is None:
        return None
    line = text.splitlines()[location[0]]
    value = line.split(":", 1)[1].strip()
    if len(value) >= 2 and value[0] in ("'", '"') and value[-1] == value[0]:
        value = value[1:-1]
    return value


def replace_version(text, version):
    lines = text.splitlines(keepends=True)
    location = _version_location([line.rstrip("\r\n") for line in lines])
    if location is None:
        raise VersionError("falta metadata.version en el frontmatter")
    index, indent, spacing, quote = location
    ending = lines[index][len(lines[index].rstrip("\r\n")):]
    value = f"{quote}{version}{quote}" if quote else version
    lines[index] = f"{indent}version:{spacing}{value}{ending}"
    updated = "".join(lines)
    if read_version(updated) != version:
        raise VersionError("no se pudo actualizar metadata.version")
    return updated


def skill_names(root):
    src = Path(root) / "src"
    if not src.is_dir():
        return []
    return sorted(
        path.name for path in src.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def git_tags(root):
    """Etiquetas del repositorio, o None si Git no está disponible o falla."""
    try:
        result = subprocess.run(
            ["git", "tag", "--list"], cwd=str(root), capture_output=True,
            text=True, encoding="utf-8", errors="replace",
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def is_shallow(root):
    """True si el clon es superficial; None si no se puede determinar."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-shallow-repository"], cwd=str(root),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() == "true"


def skill_tags(tags):
    """Devuelve ({skill: [versiones]}, [(etiqueta, problema)]) para las etiquetas del convenio."""
    by_skill, problems = {}, []
    for tag in tags:
        match = TAG_RE.match(tag)
        if not match:
            continue
        name, version = match.groups()
        if not VERSION_RE.fullmatch(version):
            problems.append((tag, f"versión '{version}' no es SemVer MAJOR.MINOR.PATCH"))
            continue
        by_skill.setdefault(name, []).append(version)
    return by_skill, problems


def published_status(declared, versions):
    """'publicada', 'en desarrollo' o 'inconsistente' para una versión declarada."""
    if not versions:
        return "sin publicar"
    latest = max(versions, key=version_key)
    if declared == latest:
        return "publicada"
    if is_version(declared) and version_key(declared) > version_key(latest):
        return "en desarrollo"
    return "inconsistente"


def plan_bump(root, name, part, tags):
    """Calcula el incremento sin escribir. Devuelve (ruta, anterior, nueva)."""
    path = Path(root) / "src" / name / "SKILL.md"
    if not path.is_file():
        raise VersionError(f"no existe la skill '{name}' en src/")
    text = read_text(path)
    current = read_version(text)
    if current is None:
        raise VersionError(f"{path}: falta metadata.version")
    if not is_version(current):
        raise VersionError(f"{path}: la versión '{current}' no es SemVer MAJOR.MINOR.PATCH")
    if tags is None:
        raise VersionError(
            "no se pueden comprobar las etiquetas: Git no disponible; "
            "se aborta para no publicar dos veces la misma versión"
        )
    if is_shallow(root):
        raise VersionError(
            "clon superficial: las etiquetas publicadas pueden estar incompletas; "
            "usa `fetch-depth: 0` o un clon completo antes de versionar"
        )

    by_skill, problems = skill_tags(tags)
    for tag, problem in problems:
        if tag.startswith(f"{name}/v"):
            raise VersionError(f"etiqueta '{tag}': {problem}")

    published = by_skill.get(name, [])
    new = next_version(current, part)
    if new in published:
        raise VersionError(
            f"la etiqueta '{name}/v{new}' ya existe; elige otro incremento"
        )
    if published and version_key(new) <= max(version_key(item) for item in published):
        raise VersionError(
            f"la versión {new} no supera la última publicada "
            f"({max(published, key=version_key)}); no se permite reducir"
        )
    return path, current, new


def apply_bump(root, name, part, tags):
    """Actualiza solo `metadata.version` de forma atómica. Devuelve (anterior, nueva, ruta)."""
    path, current, new = plan_bump(root, name, part, tags)
    text = read_text(path)
    updated = replace_version(text, new)
    temporary = path.with_name(path.name + ".version-tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            handle.write(updated)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return current, new, path
