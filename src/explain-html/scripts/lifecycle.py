#!/usr/bin/env python3
"""Poda las versiones antiguas de los artefactos versionados de `.explanations/`.

Uso: python3 lifecycle.py [directorio] [--keep N] [--dry-run]

Un artefacto versionado se llama `<slug>-v<N>.html` (por ejemplo
`estado-semana-45-v3.html`). Para cada slug, el script conserva las N versiones
de número más alto —la vigente incluida— y borra las anteriores. N vale 3 por
defecto. `--dry-run` lista lo que borraría sin tocar nada.

Límites de seguridad: solo mira el primer nivel del directorio indicado (por
defecto `.explanations`), solo ficheros que casan con el patrón versionado y
nunca borra la versión vigente ni deja que N sea menor que 1. No toca el resto
de artefactos ni nada fuera de esa carpeta.
"""
import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

VERSIONED = re.compile(r"^(?P<base>.+)-v(?P<number>[0-9]+)\.html$", re.IGNORECASE)
DEFAULT_KEEP = 3


def candidates(directory: Path, keep: int) -> list[Path]:
    groups: dict[str, list[tuple[int, Path]]] = defaultdict(list)
    for path in directory.iterdir():
        if not path.is_file():
            continue
        match = VERSIONED.match(path.name)
        if match:
            groups[match.group("base")].append((int(match.group("number")), path))

    obsolete: list[Path] = []
    for versions in groups.values():
        versions.sort(key=lambda item: item[0])
        obsolete.extend(path for _, path in versions[:-keep])
    return sorted(obsolete, key=lambda path: path.name.lower())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Conserva las últimas N versiones de cada artefacto versionado"
    )
    parser.add_argument("directorio", nargs="?", default=".explanations",
                        help="carpeta de artefactos (por defecto .explanations)")
    parser.add_argument("--keep", type=int, default=DEFAULT_KEEP,
                        help=f"versiones a conservar por artefacto (por defecto {DEFAULT_KEEP})")
    parser.add_argument("--dry-run", action="store_true",
                        help="lista lo que borraría sin borrar nada")
    args = parser.parse_args(argv)

    if args.keep < 1:
        print("ERROR: --keep debe ser 1 o más; con 0 se perdería la versión vigente.",
              file=sys.stderr)
        return 2

    directory = Path(args.directorio)
    if not directory.is_dir():
        print(f"ERROR: no es un directorio: {directory}. Pasa la carpeta .explanations del proyecto.",
              file=sys.stderr)
        return 2

    obsolete = candidates(directory, args.keep)
    if not obsolete:
        print(f"OK: nada que podar en {directory} (se conservan hasta {args.keep} versiones por artefacto).")
        return 0

    action = "borraría" if args.dry_run else "borrado"
    for path in obsolete:
        if not args.dry_run:
            try:
                path.unlink()
            except OSError as exc:
                print(f"ERROR: no se pudo borrar {path}: {exc}", file=sys.stderr)
                return 1
        print(f"{action}: {path.name}")

    suffix = " (dry-run: no se ha tocado nada)" if args.dry_run else ""
    print(f"OK: {len(obsolete)} versión(es) antigua(s){suffix}.")
    if not args.dry_run:
        print(f"Regenera el índice con build-index.py {directory} tras la poda.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
