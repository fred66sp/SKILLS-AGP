#!/usr/bin/env python3
"""Puerta de verificación de un proyecto JavaScript.

Uso:
    python scripts/verify-js.py [--root <directorio>] [--syntax] [--test] [--lint]
                                [--timeout <segundos>] [--json]

Comprueba siempre la sintaxis con `node --check` sobre los `.js`, `.mjs` y
`.cjs` del proyecto, excluyendo directorios de dependencias y de build. Con
`--test` ejecuta el script `test` de package.json o, si no existe, `node --test`
cuando hay archivos de prueba. Con `--lint` ejecuta el script `lint` si existe.
Informa de la versión de node detectada frente a `engines.node` sin convertir la
diferencia en un fallo.

Devuelve código 0 si todo lo ejecutado pasa, 1 si alguna comprobación falla y 2
si la raíz no es un directorio, falta node, falta package.json cuando se piden
pruebas o el proyecto no existe.

No descarga dependencias y no sustituye el runner del proyecto: si hay script
`test`, se usa ese. La comprobación de sintaxis no ejecuta el código.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_TIMEOUT = 600
SUPPORTED_MANAGERS = ("npm", "pnpm", "yarn", "bun")
LOCKFILES = (
    ("pnpm-lock.yaml", "pnpm"),
    ("yarn.lock", "yarn"),
    ("bun.lockb", "bun"),
    ("bun.lock", "bun"),
    ("package-lock.json", "npm"),
    ("npm-shrinkwrap.json", "npm"),
)
EXCLUDED_DIRS = {
    ".git", "node_modules", "dist", "build", "coverage", "vendor",
    "tmp", ".cache", ".venv", "venv", ".next", ".output",
}
SOURCE_SUFFIXES = (".js", ".mjs", ".cjs")
TEST_PATTERNS = (".test.js", ".test.mjs", ".test.cjs", "-test.js", "-test.mjs", "-test.cjs")
MODULE_HINT = re.compile(
    r"Cannot use import statement outside a module|Unexpected token 'export'|"
    r"Cannot use 'import\.meta' outside a module"
)


def read_package(root):
    path = root / "package.json"
    if not path.exists():
        return None, None
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except OSError as exc:
        return None, f"cannot read package.json: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"package.json is not valid JSON: {exc}"


def detect_package_manager(root, package):
    declared = (package or {}).get("packageManager")
    if isinstance(declared, str) and declared:
        name = declared.split("@", 1)[0].strip()
        if name in SUPPORTED_MANAGERS:
            return name, None
        return None, f"unsupported package manager: {name}"
    for filename, manager in LOCKFILES:
        if (root / filename).exists():
            return manager, None
    return "npm", None


def find_sources(root):
    found = []
    for path in sorted(root.rglob("*")):
        if path.suffix not in SOURCE_SUFFIXES:
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS or part.startswith(".") for part in relative.parts[:-1]):
            continue
        if path.name.endswith(".min.js"):
            continue
        if path.is_file():
            found.append(path)
    return found


def find_tests(root):
    return [path for path in find_sources(root) if path.name.endswith(TEST_PATTERNS)]


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
        output = stdout + stderr
        return None, f"timed out after {timeout}s\n{output}".strip()
    except OSError as exc:
        return None, f"could not run {command[0]}: {exc}"

    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, output.strip()


def version_tuple(text):
    match = re.search(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", text or "")
    if not match:
        return None
    parts = [int(part) if part else 0 for part in match.groups()]
    return tuple(parts)


def declared_node(package):
    engines = (package or {}).get("engines")
    if not isinstance(engines, dict):
        return None
    node = engines.get("node")
    return node if isinstance(node, str) and node.strip() else None


def supports_detect_module(node_exe):
    code, _ = run([node_exe, "--experimental-detect-module", "--version"], None, 10)
    return code == 0


def check_syntax(node_exe, files, root, timeout):
    """Devuelve (fallos, notas). Un fallo es (ruta relativa, salida)."""
    failures, notes = [], []
    retry = None
    for path in files:
        relative = path.relative_to(root).as_posix()
        code, output = run([node_exe, "--check", str(path)], root, timeout)
        if code != 0 and path.suffix == ".js" and MODULE_HINT.search(output):
            if retry is None:
                retry = supports_detect_module(node_exe)
            if retry:
                retry_code, retry_output = run(
                    [node_exe, "--experimental-detect-module", "--check", str(path)], root, timeout
                )
                if retry_code == 0:
                    notes.append(
                        f"{relative}: ESM in .js detected; the runtime is older than Node 22.7 "
                        "and needs --experimental-detect-module or \"type\": \"module\""
                    )
                    continue
                code, output = retry_code, retry_output
        if code != 0:
            failures.append((relative, output))
    return failures, notes


def plan(package, manager_exe, node_exe, root, want_test, want_lint):
    scripts = (package or {}).get("scripts")
    scripts = scripts if isinstance(scripts, dict) else {}
    checks = []

    if want_test:
        if "test" in scripts:
            checks.append(("test", [manager_exe, "run", "test"], None))
        else:
            tests = find_tests(root)
            if tests:
                checks.append(("test", [node_exe, "--test"], None))
            else:
                checks.append((
                    "test",
                    [node_exe, "--test"],
                    'package.json has no "test" script and no *test* file was found',
                ))
    if want_lint:
        if "lint" in scripts:
            checks.append(("lint", [manager_exe, "run", "lint"], None))
        else:
            checks.append((
                "lint",
                [manager_exe, "run", "lint"],
                'package.json has no "lint" script',
            ))
    return checks


def evaluate(checks, root, timeout):
    results = []
    for name, command, missing in checks:
        display = " ".join(command)
        if missing:
            results.append({
                "name": name,
                "command": display,
                "status": "failed",
                "exit_code": None,
                "output": missing,
            })
            continue
        code, output = run(command, root, timeout)
        results.append({
            "name": name,
            "command": display,
            "status": "passed" if code == 0 else "failed",
            "exit_code": code,
            "output": output,
        })
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description="Ejecuta la puerta de verificación de un proyecto JavaScript")
    parser.add_argument("--root", default=".", help="Raíz del proyecto (por defecto: .)")
    parser.add_argument("--syntax", action="store_true", help="Comprueba la sintaxis (siempre activo)")
    parser.add_argument("--test", action="store_true", help="Ejecuta el script test o node --test")
    parser.add_argument("--lint", action="store_true", help="Ejecuta el script lint de package.json")
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

    node_exe = shutil.which("node")
    if not node_exe:
        print("error: node is not available in PATH", file=sys.stderr)
        return 2

    package, error = read_package(root)
    if error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    if package is None and (args.test or args.lint):
        print(f"error: package.json does not exist in {root}", file=sys.stderr)
        return 2

    manager, error = detect_package_manager(root, package)
    if error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    manager_exe = shutil.which(manager)
    if (args.test or args.lint) and not manager_exe:
        print(f"error: {manager} is not available in PATH", file=sys.stderr)
        return 2

    detected = version_tuple(run([node_exe, "--version"], None, args.timeout)[1])
    declared = declared_node(package)

    notes = []
    files = find_sources(root)
    failures, syntax_notes = check_syntax(node_exe, files, root, args.timeout)
    notes.extend(syntax_notes)
    syntax_result = {
        "name": "syntax",
        "command": f"node --check ({len(files)} file{'s' if len(files) != 1 else ''})",
        "status": "passed" if not failures else "failed",
        "exit_code": 0 if not failures else 1,
        "output": "\n".join(f"{relative}: {output}" for relative, output in failures).strip(),
    }
    if not files:
        notes.append("no .js, .mjs or .cjs file was found")

    results = [syntax_result]
    results.extend(evaluate(plan(package, manager_exe, node_exe, root, args.test, args.lint), root, args.timeout))

    minimum = version_tuple(declared or "")
    if declared and detected and minimum and detected < minimum:
        notes.append(f"node {'.'.join(map(str, detected))} is below engines.node \"{declared}\"")

    ok = all(item["status"] == "passed" for item in results)

    if args.json:
        print(json.dumps({
            "ok": ok,
            "root": str(root),
            "node": ".".join(map(str, detected)) if detected else None,
            "node_declared": declared,
            "package_manager": manager,
            "notes": notes,
            "checks": results,
        }, indent=2, ensure_ascii=False))
    else:
        print(f"Puerta JavaScript: {root}")
        node_text = ".".join(map(str, detected)) if detected else "desconocido"
        if declared:
            node_text += f" (engines: {declared})"
        print(f"Node: {node_text}")
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
