#!/usr/bin/env python3
"""Pruebas de scripts/lifecycle.py: poda por versión, dry-run, N por defecto y seguridad.

Uso: python3 test-lifecycle.py
Sale 0 si todo pasa; imprime el caso fallido y sale 1 si no.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("lifecycle.py")


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
    )


def touch(path: Path) -> None:
    path.write_text("x", encoding="utf-8")


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw) / "explanations"
        tmp.mkdir()
        for number in range(1, 6):
            touch(tmp / f"estado-v{number}.html")
        touch(tmp / "otro-v1.html")
        touch(tmp / "suelto.html")
        touch(tmp / "index.html")
        (tmp / "carpeta-v1.html").mkdir()

        dry = run(str(tmp), "--keep", "2", "--dry-run")
        quedan = all((tmp / f"estado-v{number}.html").is_file() for number in range(1, 6))
        if dry.returncode != 0 or "estado-v1.html" not in dry.stdout or "estado-v3.html" not in dry.stdout:
            print(f"FALLO «dry-run lista las antiguas»\n{dry.stdout}{dry.stderr}")
            failures += 1
        if "estado-v4.html" in dry.stdout or not quedan:
            print(f"FALLO «dry-run no toca nada»\n{dry.stdout}{dry.stderr}")
            failures += 1

        real = run(str(tmp), "--keep", "2")
        expected_gone = [f"estado-v{number}.html" for number in (1, 2, 3)]
        expected_kept = [f"estado-v{number}.html" for number in (4, 5)] + [
            "otro-v1.html", "suelto.html", "index.html",
        ]
        if real.returncode != 0:
            print(f"FALLO «poda real»: código {real.returncode}\n{real.stdout}{real.stderr}")
            failures += 1
        for name in expected_gone:
            if (tmp / name).exists():
                print(f"FALLO «debería haberse borrado {name}»")
                failures += 1
        for name in expected_kept:
            if not (tmp / name).is_file():
                print(f"FALLO «no debía tocarse {name}»")
                failures += 1
        if not (tmp / "carpeta-v1.html").is_dir():
            print("FALLO «no debe tocar una carpeta con nombre versionado»")
            failures += 1

        for number in range(1, 5):
            touch(tmp / f"otro-v{number}.html")
        default = run(str(tmp))
        if default.returncode != 0 or (tmp / "otro-v1.html").exists() or not (tmp / "otro-v3.html").is_file():
            print(f"FALLO «N por defecto es 3»\n{default.stdout}{default.stderr}")
            failures += 1

        zero = run(str(tmp), "--keep", "0")
        if zero.returncode != 2 or not (tmp / "estado-v5.html").is_file():
            print(f"FALLO «--keep 0 se rechaza sin borrar»\n{zero.stdout}{zero.stderr}")
            failures += 1

        missing = run(str(tmp / "no-existe"))
        if missing.returncode != 2:
            print(f"FALLO «directorio inexistente»: código {missing.returncode}, esperado 2")
            failures += 1

    if failures:
        print(f"{failures} caso(s) fallidos.")
        return 1
    print("OK: lifecycle poda por versión, respeta dry-run, N y el resto de ficheros.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
