#!/usr/bin/env python3
"""Puerta de verificación de un proyecto TypeScript.

Uso:
    python scripts/verify-ts.py [--root <directorio>] [--test] [--lint] [--build]
                                [--timeout <segundos>] [--json]

Ejecuta el typecheck (script `typecheck` del proyecto o `tsc --noEmit` con la
copia local de TypeScript) y, si se piden, los scripts `lint`, `test` y `build`
de package.json. Devuelve código 0 si todo lo ejecutado pasa, 1 si alguna
comprobación falla y 2 si la raíz, package.json o el gestor de paquetes no
existe.

Detecta el gestor por el campo `packageManager` y, si falta, por el lockfile.
No descarga dependencias: si no hay script `typecheck`, exige una copia local
de TypeScript en node_modules. La salida de texto muestra una línea por
comprobación; --json devuelve el detalle y el código de salida de cada comando.
"""

import argparse
import json
import os
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


def read_package(root):
    path = root / "package.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"package.json does not exist in {root}"
    except OSError as exc:
        return None, f"cannot read {path}: {exc}"
    except json.JSONDecodeError as exc:
        return None, f"cannot parse {path}: {exc}"
    if not isinstance(data, dict):
        return None, f"{path} must contain a JSON object"
    return data, None


def detect_package_manager(root, package):
    declared = package.get("packageManager")
    if isinstance(declared, str) and declared.strip():
        name = declared.split("@", 1)[0].strip()
        if name in SUPPORTED_MANAGERS:
            return name, None
        return None, (
            f"unsupported packageManager '{declared}'; "
            f"expected one of {', '.join(SUPPORTED_MANAGERS)}"
        )

    found = [(filename, manager) for filename, manager in LOCKFILES if (root / filename).is_file()]
    managers = sorted({manager for _, manager in found})
    if len(managers) > 1:
        names = ", ".join(filename for filename, _ in found)
        return None, f"multiple lockfiles ({names}); keep one package manager"
    if managers:
        return managers[0], None
    return "npm", None


def script_command(manager_exe, script):
    return [manager_exe, "run", script]


def find_tsc(root):
    candidate = root / "node_modules" / "typescript" / "bin" / "tsc"
    return candidate if candidate.is_file() else None


def plan(package, manager_exe, root, want_lint, want_test, want_build):
    scripts = package.get("scripts")
    scripts = scripts if isinstance(scripts, dict) else {}

    checks = []
    if "typecheck" in scripts:
        checks.append(("typecheck", script_command(manager_exe, "typecheck"), None))
    else:
        tsc = find_tsc(root)
        node = shutil.which("node")
        if tsc and node:
            checks.append(("typecheck", [node, str(tsc), "--noEmit"], None))
        elif tsc:
            checks.append((
                "typecheck",
                ["node", str(tsc), "--noEmit"],
                "node is not available in PATH",
            ))
        else:
            checks.append((
                "typecheck",
                ["tsc", "--noEmit"],
                'typescript is not installed locally and package.json has no "typecheck" script',
            ))

    for name, wanted in (("lint", want_lint), ("test", want_test), ("build", want_build)):
        if not wanted:
            continue
        if name in scripts:
            checks.append((name, script_command(manager_exe, name), None))
        else:
            checks.append((
                name,
                script_command(manager_exe, name),
                f'package.json has no "{name}" script',
            ))
    return checks


def run(command, cwd, timeout):
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
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
        if code == 0:
            status = "passed"
        else:
            status = "failed"
        results.append({
            "name": name,
            "command": display,
            "status": status,
            "exit_code": code,
            "output": output,
        })
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description="Ejecuta la puerta de verificación de un proyecto TypeScript")
    parser.add_argument("--root", default=".", help="Raíz del proyecto (por defecto: .)")
    parser.add_argument("--test", action="store_true", help="Ejecuta el script test de package.json")
    parser.add_argument("--lint", action="store_true", help="Ejecuta el script lint de package.json")
    parser.add_argument("--build", action="store_true", help="Ejecuta el script build de package.json")
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

    package, error = read_package(root)
    if error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    manager, error = detect_package_manager(root, package)
    if error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    manager_exe = shutil.which(manager)
    if not manager_exe:
        print(f"error: {manager} is not available in PATH", file=sys.stderr)
        return 2

    checks = plan(package, manager_exe, root, args.lint, args.test, args.build)
    results = evaluate(checks, root, args.timeout)
    ok = all(item["status"] == "passed" for item in results)

    if args.json:
        print(json.dumps({
            "ok": ok,
            "root": str(root),
            "package_manager": manager,
            "checks": results,
        }, indent=2, ensure_ascii=False))
    else:
        print(f"Puerta TypeScript: {root}")
        print(f"Gestor: {manager}")
        for item in results:
            print(f"{item['status'].upper():6} {item['name']}")
            if item["status"] != "passed" and item["output"]:
                for line in item["output"].splitlines():
                    print(f"       {line}")
        print()
        print("Resultado: " + ("PASS" if ok else "FAIL"))

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
