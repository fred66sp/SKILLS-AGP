#!/usr/bin/env python3
"""Publica artefactos de explain-html: verifica, indexa y abre en un paso.

Uso: python3 publish.py <ruta.html> [ruta.html ...] [--no-open] [--quiet]

Encadena los tres pasos del contrato: check-artifact.py (autocontención,
título y procedencia), build-index.py (index.html de cada carpeta distinta) y
open-artifact.sh (navegador). Si la verificación falla no escribe índice ni
abre nada. Si falla el índice, no abre. Que no haya navegador no invalida el
artefacto: avisa con la ruta absoluta y termina bien.

Códigos de salida: 0 correcto; 1 verificación o índice fallidos; 2 uso
incorrecto (sin argumentos, ruta inexistente o que no sea .html).
"""
import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
CHECK = SCRIPTS / "check-artifact.py"
BUILD = SCRIPTS / "build-index.py"
OPEN = SCRIPTS / "open-artifact.sh"


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verifica, indexa y abre artefactos de explain-html en un paso"
    )
    parser.add_argument("artefactos", nargs="*", metavar="ruta.html",
                        help="artefactos .html ya generados")
    parser.add_argument("--no-open", action="store_true", help="no abre el navegador")
    parser.add_argument("--quiet", action="store_true", help="no imprime el resumen propio")
    return parser.parse_args(argv)


def collect_paths(raw_paths: list[str]) -> list[Path] | None:
    """Valida las rutas de la línea de órdenes; None si el uso es incorrecto."""
    if not raw_paths:
        print("ERROR: indica al menos un artefacto .html. "
              "Uso: python3 publish.py <ruta.html> [ruta.html ...] [--no-open] [--quiet]",
              file=sys.stderr)
        return None

    paths: list[Path] = []
    for raw in raw_paths:
        path = Path(raw).expanduser()
        if not path.is_file():
            print(f"ERROR: no existe el artefacto «{raw}». Genera el .html antes de publicarlo.",
                  file=sys.stderr)
            return None
        if path.suffix.lower() != ".html":
            print(f"ERROR: «{raw}» no es un .html; los artefactos son un único .html.",
                  file=sys.stderr)
            return None
        paths.append(path.resolve())
    return paths


def open_artifact(path: Path) -> int:
    """Invoca open-artifact.sh y deja pasar su salida; devuelve su código."""
    try:
        proc = subprocess.run(["bash", str(OPEN), str(path)], capture_output=True, text=True)
    except OSError as exc:
        print(f"No se pudo ejecutar {OPEN.name}: {exc}", file=sys.stderr)
        return 1
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return proc.returncode


def main(argv=None) -> int:
    args = parse_args(argv)
    paths = collect_paths(args.artefactos)
    if paths is None:
        return 2

    verified = subprocess.run([sys.executable, str(CHECK), *(str(path) for path in paths)])
    if verified.returncode != 0:
        return 1

    directories = list(dict.fromkeys(path.parent for path in paths))
    for directory in directories:
        built = subprocess.run([sys.executable, str(BUILD), str(directory)])
        if built.returncode != 0:
            return 1

    if not args.no_open:
        if open_artifact(paths[0]) != 0:
            print(f"Aviso: no hay navegador disponible; el artefacto está verificado e indexado. "
                  f"Ábrelo a mano o sírvelo: {paths[0]}", file=sys.stderr)

    if not args.quiet:
        print(f"OK: {len(paths)} artefacto(s) verificados e indexados "
              f"en {len(directories)} carpeta(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
