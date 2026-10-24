#!/usr/bin/env python3
"""Puerta de verificación de un módulo Go.

Uso:
    python scripts/verify-go.py [--root <directorio>] [--race] [--lint]
                                [--timeout <segundos>] [--json]

Ejecuta gofmt -l, go build, go test, go vet y, opcionalmente, go test -race y
golangci-lint. Devuelve código 0 si todo lo ejecutado pasa, 1 si alguna
comprobación falla y 2 si la raíz o una herramienta obligatoria no existe.

La salida de texto muestra una línea por comprobación. --json devuelve un
documento con el detalle y el código de salida de cada comando.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_TIMEOUT = 600


def executable(name, go_exe):
    found = shutil.which(name)
    if found:
        return found

    suffix = ".exe" if os.name == "nt" else ""
    sibling = Path(go_exe).parent / (name + suffix)
    if sibling.exists():
        return str(sibling)

    return None


def run(command, cwd, timeout):
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        return None, f"timed out after {timeout}s\n{output}".strip()

    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, output.strip()


def check_gofmt(command, cwd, timeout):
    code, output = run(command, cwd, timeout)
    if code != 0:
        return "failed", code, output or "gofmt failed"
    if output:
        return "failed", code, "unformatted files:\n" + output
    return "passed", code, ""


def check_command(command, cwd, timeout):
    code, output = run(command, cwd, timeout)
    if code == 0:
        return "passed", code, output
    return "failed", code, output or f"exit code {code}"


def main():
    parser = argparse.ArgumentParser(description="Ejecuta la puerta de verificación de un módulo Go")
    parser.add_argument("--root", default=".", help="Raíz del módulo (por defecto: .)")
    parser.add_argument("--race", action="store_true", help="Ejecuta go test -race ./...")
    parser.add_argument("--lint", action="store_true", help="Ejecuta golangci-lint run ./...")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout por comando en segundos")
    parser.add_argument("--json", action="store_true", help="Salida JSON")
    args = parser.parse_args()

    if args.timeout <= 0:
        print("error: --timeout must be greater than zero", file=sys.stderr)
        return 2

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: root is not a directory: {root}", file=sys.stderr)
        return 2

    go_exe = shutil.which("go")
    if not go_exe:
        print("error: go is not available in PATH", file=sys.stderr)
        return 2

    gofmt_exe = executable("gofmt", go_exe)
    if not gofmt_exe:
        print("error: gofmt is not available", file=sys.stderr)
        return 2

    checks = []
    gofmt_result = check_gofmt([gofmt_exe, "-l", "."], root, args.timeout)
    checks.append(("gofmt", " ".join([gofmt_exe, "-l", "."]), *gofmt_result))

    commands = [
        ("build", [go_exe, "build", "./..."]),
        ("test", [go_exe, "test", "./..."]),
        ("vet", [go_exe, "vet", "./..."]),
    ]
    if args.race:
        commands.append(("race", [go_exe, "test", "-race", "./..."]))

    lint_missing = False
    if args.lint:
        lint_exe = executable("golangci-lint", go_exe)
        if lint_exe:
            commands.append(("lint", [lint_exe, "run", "./..."]))
        else:
            lint_missing = True

    for name, command in commands:
        result = check_command(command, root, args.timeout)
        checks.append((name, " ".join(command), *result))

    if lint_missing:
        checks.append(("lint", "golangci-lint run ./...", "failed", None, "golangci-lint is not available"))

    results = []
    for name, command, status, code, output in checks:
        results.append(
            {
                "name": name,
                "command": command,
                "status": status,
                "exit_code": code,
                "output": output,
            }
        )

    ok = all(item["status"] == "passed" for item in results)

    if args.json:
        print(json.dumps({"ok": ok, "root": str(root), "checks": results}, indent=2, ensure_ascii=False))
    else:
        print(f"Puerta Go: {root}")
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
