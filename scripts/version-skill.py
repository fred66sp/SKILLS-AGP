#!/usr/bin/env python3
"""Consulta y prepara la versión independiente de una skill.

Uso:
    python scripts/version-skill.py list
    python scripts/version-skill.py show <skill>
    python scripts/version-skill.py bump <skill> <patch|minor|major> [--dry-run]

No ejecuta `git commit`, `git tag` ni `git push`: solo actualiza
`metadata.version` de `src/<skill>/SKILL.md`.
"""

import argparse
import sys
from pathlib import Path

import skill_versions


def git_tags(root):
    return skill_versions.git_tags(root)


def status(root, name, tags):
    path = Path(root) / "src" / name / "SKILL.md"
    declared = skill_versions.read_version(skill_versions.read_text(path))
    if tags is None:
        return declared, [], "desconocido (Git no disponible)"
    by_skill, _ = skill_versions.skill_tags(tags)
    published = sorted(by_skill.get(name, []), key=skill_versions.version_key)
    if not skill_versions.is_version(declared or ""):
        return declared, published, "versión no válida"
    return declared, published, skill_versions.published_status(declared, published)


def command_list(root):
    tags = git_tags(root)
    for name in skill_versions.skill_names(root):
        declared, published, state = status(root, name, tags)
        latest = published[-1] if published else "-"
        print(f"{name:<40} {declared or '-':<10} {latest:<10} {state}")
    return 0


def command_show(root, name):
    if name not in skill_versions.skill_names(root):
        print(f"ERROR: no existe la skill '{name}' en src/", file=sys.stderr)
        return 1
    declared, published, state = status(root, name, git_tags(root))
    print(f"skill: {name}")
    print(f"declarada: {declared or '(falta)'}")
    print(f"publicadas: {', '.join(published) if published else '(ninguna)'}")
    print(f"estado: {state}")
    return 0


def command_bump(root, name, part, dry_run):
    tags = git_tags(root)
    path, current, new = skill_versions.plan_bump(root, name, part, tags)
    print(f"{name}: {current} -> {new} ({part})")
    print(f"etiqueta a crear tras integrar: {name}/v{new}")
    if dry_run:
        print(f"sin escribir {path} (--dry-run)")
        return 0
    current, new, _ = skill_versions.apply_bump(root, name, part, tags)
    print(f"actualizada metadata.version en {path}")
    return 0


def main(argv=None):
    root_default = str(Path(__file__).resolve().parents[1])
    parser = argparse.ArgumentParser(description="Versiones independientes de las skills")
    parser.add_argument("--root", default=root_default, help="Raíz del repositorio")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("list", help="Lista las skills y su versión")

    show = commands.add_parser("show", help="Muestra la versión de una skill")
    show.add_argument("skill")

    bump = commands.add_parser("bump", help="Prepara el siguiente incremento de versión")
    bump.add_argument("skill")
    bump.add_argument("part", choices=skill_versions.PARTS)
    bump.add_argument("--dry-run", action="store_true", help="Previsualiza sin escribir")

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

    if skill_versions.is_shallow(root):
        print(
            "AVISO: clon superficial; las etiquetas publicadas pueden estar incompletas",
            file=sys.stderr,
        )

    try:
        if args.command == "list":
            return command_list(root)
        if args.command == "show":
            return command_show(root, args.skill)
        return command_bump(root, args.skill, args.part, args.dry_run)
    except skill_versions.VersionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
