#!/usr/bin/env python3
"""Comprueba si playwright-cli está listo en un espacio de trabajo, sin abrir un navegador.

Uso:
    python3 preflight.py [--root <directorio>] [--binary <ruta|nombre>] [--json]

No instala nada, no abre sesiones y no escribe en el proyecto. Reconoce el
entorno para que el briefing de confirmación no prometa lo que no existe.

Códigos de salida:
    0  playwright-cli disponible y ejecutable
    1  no disponible o no ejecutable
    2  error de uso o raíz inexistente
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ARTIFACTS = (".playwright-cli", "test-results", "playwright-report")
CONFIG = Path(".playwright") / "cli.config.json"


def resolve_binary(name):
    if os.sep in name or (os.altsep and os.altsep in name):
        path = Path(name).expanduser()
        return path if path.is_file() else None
    found = shutil.which(name)
    return Path(found) if found else None


def read_version(binary, timeout):
    try:
        result = subprocess.run(
            [str(binary), "--version"],
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
        )
    except subprocess.TimeoutExpired:
        return None, "timeout al ejecutar --version"
    except OSError as exc:
        return None, f"no se pudo ejecutar: {exc}"
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "sin salida"
        return None, f"--version devolvió {result.returncode}: {detail[:200]}"
    line = (result.stdout.strip().splitlines() or [""])[0]
    if not line:
        return None, "--version no imprimió versión"
    return line, None


def ignored_patterns(gitignore):
    """Devuelve los nombres ignorados. Heurística de línea simple, no un parser de Git."""
    names = set()
    if not gitignore.is_file():
        return names
    for line in gitignore.read_text(encoding="utf-8", errors="replace").splitlines():
        entry = line.strip()
        if not entry or entry.startswith(("#", "!")):
            continue
        entry = entry.rstrip("/").lstrip("/")
        if entry in ARTIFACTS:
            names.add(entry)
    return names


def inspect_artifact(root, name):
    path = root / name
    if not path.is_dir():
        return None
    files = 0
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            files += 1
            try:
                total += item.stat().st_size
            except OSError:
                pass
    return {"path": name, "files": files, "bytes": total}


def check_environment(root, binary="playwright-cli", timeout=15):
    root = Path(root).expanduser()
    report = {
        "root": str(root),
        "binary": {"name": binary, "path": None, "version": None},
        "ready": False,
        "workspace_config": (root / CONFIG).is_file(),
        "global_config": (Path.home() / ".playwright" / "cli.config.json").is_file(),
        "artifacts": [item for item in (inspect_artifact(root, name) for name in ARTIFACTS) if item],
        "gitignore": {"present": (root / ".gitignore").is_file(), "ignored": [], "missing": []},
        "notes": [],
    }

    path = resolve_binary(binary)
    if path is None:
        report["notes"].append(f"no se encontró '{binary}' en PATH")
    else:
        report["binary"]["path"] = str(path)
        version, problem = read_version(path, timeout)
        if problem:
            report["notes"].append(problem)
        else:
            report["binary"]["version"] = version
            report["ready"] = True

    ignored = ignored_patterns(root / ".gitignore")
    present = [item["path"] for item in report["artifacts"]]
    report["gitignore"]["ignored"] = sorted(ignored)
    report["gitignore"]["missing"] = sorted(name for name in present if name not in ignored)
    return report


def print_text(report):
    binary = report["binary"]
    if binary["version"]:
        print(f"playwright-cli: ok · {binary['version']} · {binary['path']}")
    elif binary["path"]:
        print(f"playwright-cli: no ejecutable · {binary['path']}")
    else:
        print("playwright-cli: ausente")

    print("config: "
          f"workspace {'sí' if report['workspace_config'] else 'no'} · "
          f"global {'sí' if report['global_config'] else 'no'}")

    if report["artifacts"]:
        detail = ", ".join(
            f"{item['path']} ({item['files']} fichero{'s' if item['files'] != 1 else ''})"
            for item in report["artifacts"]
        )
        print(f"artefactos: {detail}")
    else:
        print("artefactos: ninguno")

    if not report["gitignore"]["present"]:
        print("gitignore: no hay .gitignore en la raíz")
    elif report["gitignore"]["missing"]:
        print(f"gitignore: falta ignorar {', '.join(report['gitignore']['missing'])}")
    else:
        print("gitignore: artefactos cubiertos")

    for note in report["notes"]:
        print(f"nota: {note}")
    print("conclusión: listo" if report["ready"] else "conclusión: bloqueado")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Reconoce playwright-cli sin abrir un navegador")
    parser.add_argument("--root", default=".", help="Espacio de trabajo a inspeccionar")
    parser.add_argument("--binary", default="playwright-cli", help="Ruta o nombre del ejecutable")
    parser.add_argument("--timeout", type=int, default=15, help="Segundos para --version")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    args = parser.parse_args(argv)

    root = Path(args.root).expanduser()
    if not root.is_dir():
        print(f"ERROR: la raíz no es un directorio: {root}", file=sys.stderr)
        return 2

    report = check_environment(root, args.binary, args.timeout)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text(report)
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
