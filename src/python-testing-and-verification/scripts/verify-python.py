#!/usr/bin/env python3
"""Puerta de verificación de un proyecto Python.

Uso:
    python scripts/verify-python.py [--root <directorio>] [--format] [--lint]
                                    [--types] [--test] [--timeout <segundos>]
                                    [--json]

Comprueba siempre la sintaxis de los `.py` del proyecto con `compile()`, sin
ejecutar el código, excluyendo entornos virtuales, caches y directorios de
build. Con `--format` ejecuta `ruff format --check`; con `--lint`, `ruff
check`; con `--types`, `mypy .`; con `--test`, `pytest` si está instalado o,
en su defecto, `python -m unittest discover` cuando hay archivos de prueba.
Informa de la versión de Python detectada frente a `requires-python` sin
convertir la diferencia en un fallo.

Devuelve código 0 si todo lo ejecutado pasa, 1 si alguna comprobación falla y
2 si la raíz no es un directorio, una opción es inválida o falta una herramienta
pedida.

No descarga dependencias ni instala entornos: usa el intérprete que ejecuta el
script y las herramientas disponibles en él o en PATH. Las comprobaciones que
ejecutan código del proyecto (`pytest`, `unittest`) deben correr solo sobre
proyectos confiables o en un contenedor sin privilegios.
"""

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

DEFAULT_TIMEOUT = 600
EXCLUDED_DIRS = {
    ".git", ".hg", ".svn", ".tox", ".nox", ".venv", "venv", "env", ".env",
    "__pycache__", "build", "dist", "site-packages", "node_modules",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".coverage",
}
TEST_PREFIXES = ("test_",)
TEST_SUFFIXES = ("_test.py",)
REQUIRES_RE = re.compile(r"^\s*>=\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?\s*$")


def find_module(name):
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def read_requires_python(root):
    path = root / "pyproject.toml"
    if not path.is_file():
        return None, None
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return None, f"cannot read pyproject.toml: {exc}"
    project = data.get("project")
    if not isinstance(project, dict):
        return None, None
    value = project.get("requires-python")
    return (value if isinstance(value, str) and value.strip() else None), None


def find_sources(root):
    found = []
    for path in sorted(root.rglob("*.py")):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS or part.startswith(".") for part in relative.parts[:-1]):
            continue
        if path.is_file():
            found.append(path)
    return found


def find_tests(root):
    return [
        path for path in find_sources(root)
        if path.name.startswith(TEST_PREFIXES) or path.name.endswith(TEST_SUFFIXES)
    ]


def check_syntax(files, root):
    failures = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except UnicodeDecodeError as exc:
            failures.append((relative, f"no es texto UTF-8: {exc}"))
        except SyntaxError as exc:
            location = f"{exc.lineno}:{exc.offset}" if exc.lineno else "?"
            failures.append((relative, f"{location}: {exc.msg}"))
        except OSError as exc:
            failures.append((relative, f"no se puede leer: {exc}"))
    return failures


def run(command, cwd, timeout):
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", "replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", "replace")
        return None, f"timed out after {timeout}s\n{stdout}{stderr}".strip()
    except OSError as exc:
        return None, f"could not run {command[0]}: {exc}"

    return completed.returncode, ((completed.stdout or "") + (completed.stderr or "")).strip()


def version_tuple(text):
    match = re.search(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", text or "")
    if not match:
        return None
    return tuple(int(part) if part else 0 for part in match.groups())


def plan(root, ruff, want_format, want_lint, want_types, want_test):
    checks = []

    if want_format:
        if ruff:
            checks.append(("format", [ruff, "format", "--check", "."], None))
        else:
            checks.append(("format", ["ruff", "format", "--check", "."], "ruff is not available in PATH"))

    if want_lint:
        if ruff:
            checks.append(("lint", [ruff, "check", "."], None))
        else:
            checks.append(("lint", ["ruff", "check", "."], "ruff is not available in PATH"))

    if want_types:
        if find_module("mypy"):
            checks.append(("types", [sys.executable, "-m", "mypy", "."], None))
        elif shutil.which("pyright"):
            checks.append(("types", [shutil.which("pyright")], None))
        else:
            checks.append((
                "types",
                [sys.executable, "-m", "mypy", "."],
                "mypy is not installed in this interpreter and pyright is not in PATH",
            ))

    if want_test:
        if find_module("pytest"):
            checks.append(("test", [sys.executable, "-m", "pytest"], None))
        elif find_tests(root):
            start = "tests" if (root / "tests").is_dir() else "."
            checks.append(("test", [sys.executable, "-m", "unittest", "discover", "-s", start], None))
        else:
            checks.append((
                "test",
                [sys.executable, "-m", "unittest", "discover"],
                "pytest is not installed and no test_*.py file was found",
            ))
    return checks


def evaluate(checks, root, timeout):
    results = []
    for name, command, missing in checks:
        if missing:
            results.append({
                "name": name,
                "command": " ".join(command),
                "status": "failed",
                "exit_code": None,
                "output": missing,
            })
            continue
        code, output = run(command, root, timeout)
        results.append({
            "name": name,
            "command": " ".join(Path(part).name if part == sys.executable else part for part in command),
            "status": "passed" if code == 0 else "failed",
            "exit_code": code,
            "output": output,
        })
    return results


def check_requires(declared, current):
    match = REQUIRES_RE.match(declared or "")
    if not match or not current:
        return None
    minimum = tuple(int(part) if part else 0 for part in match.groups())
    if current < minimum:
        return (
            f"python {'.'.join(map(str, current))} is below requires-python \"{declared}\""
        )
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Ejecuta la puerta de verificación de un proyecto Python")
    parser.add_argument("--root", default=".", help="Raíz del proyecto (por defecto: .)")
    parser.add_argument("--format", action="store_true", help="Ejecuta ruff format --check")
    parser.add_argument("--lint", action="store_true", help="Ejecuta ruff check")
    parser.add_argument("--types", action="store_true", help="Ejecuta mypy o pyright")
    parser.add_argument("--test", action="store_true", help="Ejecuta pytest o unittest discover")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout por comando en segundos")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    args = parser.parse_args(argv)

    if args.timeout <= 0:
        print("error: --timeout must be greater than zero", file=sys.stderr)
        return 2

    try:
        root = Path(args.root).resolve()
        is_directory = root.is_dir()
    except OSError as exc:
        print(f"error: cannot read root {args.root}: {exc}", file=sys.stderr)
        return 2
    if not is_directory:
        print(f"error: root is not a directory: {root}", file=sys.stderr)
        return 2

    detected = tuple(sys.version_info[:3])
    declared, error = read_requires_python(root)
    if error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    notes = []
    files = find_sources(root)
    failures = check_syntax(files, root)
    syntax_result = {
        "name": "syntax",
        "command": f"compile() ({len(files)} file{'s' if len(files) != 1 else ''})",
        "status": "passed" if not failures else "failed",
        "exit_code": 0 if not failures else 1,
        "output": "\n".join(f"{relative}: {output}" for relative, output in failures).strip(),
    }
    if not files:
        notes.append("no .py file was found")

    results = [syntax_result]
    try:
        plans = plan(
            root, shutil.which("ruff"), args.format, args.lint, args.types, args.test,
        )
        results.extend(evaluate(plans, root, args.timeout))
    except OSError as exc:
        print(f"error: cannot inspect the project: {exc}", file=sys.stderr)
        return 2

    warning = check_requires(declared, detected)
    if warning:
        notes.append(warning)
    if declared and not REQUIRES_RE.match(declared):
        notes.append(f"requires-python \"{declared}\" is not checked by this gate")

    ok = all(item["status"] == "passed" for item in results)

    if args.json:
        print(json.dumps({
            "ok": ok,
            "root": str(root),
            "python": ".".join(map(str, detected)),
            "requires_python": declared,
            "notes": notes,
            "checks": results,
        }, indent=2, ensure_ascii=False))
    else:
        print(f"Puerta Python: {root}")
        python_text = ".".join(map(str, detected))
        if declared:
            python_text += f" (requires-python: {declared})"
        print(f"Python: {python_text}")
        for item in results:
            print(f"{item['status'].upper():6} {item['name']}")
            if item["status"] != "passed" and item["output"]:
                for line in item["output"].splitlines():
                    print(f"       {line}")
        for note in notes:
            print(f"NOTA   {note}")
        print()
        print("Resultado: " + ("PASS" if ok else "FAIL"))

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
