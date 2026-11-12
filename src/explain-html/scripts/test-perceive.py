#!/usr/bin/env python3
"""Pruebas de scripts/perceive.py con un playwright-cli falso, sin navegador real.

Uso: python3 test-perceive.py
Sale 0 si todo pasa; imprime el caso fallido y sale 1 si no.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("perceive.py")
REPO = Path(__file__).resolve().parents[3]
WIDTHS = (390, 768, 1440)

FAKE = '''#!{python}
import json
import os
import sys
from pathlib import Path

args = sys.argv[1:]
log = Path(os.environ["FAKE_LOG"])
state = Path(os.environ["FAKE_STATE"])
log.parent.mkdir(parents=True, exist_ok=True)
with log.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(args, ensure_ascii=False) + "\\n")

positional = [arg for arg in args if not arg.startswith("-")]
command = positional[0] if positional else ""
rest = positional[1:]
width_file = state / "width"

if command == "resize":
    width_file.parent.mkdir(parents=True, exist_ok=True)
    width_file.write_text(rest[0], encoding="utf-8")
    print("- Viewport: {{}}x{{}}".format(rest[0], rest[1]))
elif command == "eval":
    expression = " ".join(rest)
    if "scrollWidth" in expression:
        if os.environ.get("FAKE_EVAL_GARBAGE") == "1":
            print("???")
        else:
            width = width_file.read_text(encoding="utf-8").strip() if width_file.is_file() else ""
            print("true" if width == os.environ.get("FAKE_OVERFLOW_WIDTH") else "false")
    else:
        print("true")
elif command == "screenshot":
    filename = ""
    for arg in args:
        if arg.startswith("--filename="):
            filename = arg.split("=", 1)[1]
    if filename:
        target = Path(filename)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"PNG")
        print("- Screenshot saved to " + filename)
elif command == "console":
    if os.environ.get("FAKE_CONSOLE_ERRORS") == "1":
        print("Total messages: 2 (Errors: 1, Warnings: 1)")
    else:
        print("Total messages: 0 (Errors: 0, Warnings: 0)")
elif command == "open":
    if os.environ.get("FAKE_OPEN_FAIL") == "1":
        print("no browser available", file=sys.stderr)
        sys.exit(1)
    print("- page opened")
else:
    print("- ok")

sys.exit(0)
'''


def write_fake(fake_dir: Path) -> None:
    script = fake_dir / "playwright-cli"
    script.write_text(FAKE.format(python=sys.executable), encoding="utf-8")
    script.chmod(0o755)


def make_env(bin_dir: Path, state: Path, log: Path, **extra: str) -> dict[str, str]:
    env = dict(os.environ)
    env["PATH"] = str(bin_dir)
    env["FAKE_STATE"] = str(state)
    env["FAKE_LOG"] = str(log)
    env.update({key: value for key, value in extra.items() if value is not None})
    return env


def run(env: dict[str, str], *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, env=env,
        cwd=str(cwd) if cwd else None,
    )


def snapshot(root: Path) -> dict[str, object]:
    entries: dict[str, object] = {}
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        relative = str(path.relative_to(root))
        entries[relative] = "dir" if path.is_dir() else path.stat().st_size
    return entries


def main() -> int:
    failures = 0
    checks = 0

    def check(name: str, condition: bool, detail: str = "") -> None:
        nonlocal failures, checks
        checks += 1
        if not condition:
            print(f"FALLO «{name}»: {detail}")
            failures += 1

    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        fake_dir = tmp / "bin"
        empty_dir = tmp / "sin-binario"
        fake_dir.mkdir()
        empty_dir.mkdir()
        write_fake(fake_dir)
        artifact = tmp / "informe-x.html"
        artifact.write_text("<!DOCTYPE html><html lang='es'><body>hola</body></html>", encoding="utf-8")

        # (a) Sin binario: 3 y alternativa manual, sin tocar el artefacto.
        before = artifact.read_text(encoding="utf-8")
        env = make_env(empty_dir, tmp / "state-a", tmp / "log-a.jsonl")
        proc = run(env, str(artifact))
        out = proc.stdout + proc.stderr
        check("sin binario: código 3", proc.returncode == 3, f"código {proc.returncode}\n{out}")
        check("sin binario: alternativa manual", "persona" in out and "navegador" in out, out)
        check("sin binario: artefacto intacto", artifact.read_text(encoding="utf-8") == before, "el artefacto cambió")

        # (a2) El binario existe pero no consigue abrir: 3 y alternativa manual.
        env = make_env(fake_dir, tmp / "state-a2", tmp / "log-a2.jsonl", FAKE_OPEN_FAIL="1")
        proc = run(env, str(artifact))
        out = proc.stdout + proc.stderr
        check("abrir falla: código 3", proc.returncode == 3, f"código {proc.returncode}\n{out}")
        check("abrir falla: alternativa manual", "persona" in out and "navegador" in out, out)

        # (b) --dry-run: 0, imprime los anchos y no ejecuta el binario.
        log_b = tmp / "log-b.jsonl"
        env = make_env(fake_dir, tmp / "state-b", log_b)
        proc = run(env, str(artifact), "--dry-run")
        out = proc.stdout + proc.stderr
        check("dry-run: código 0", proc.returncode == 0, f"código {proc.returncode}\n{out}")
        check("dry-run: imprime los anchos", all(str(width) in out for width in WIDTHS), out)
        check("dry-run: no ejecuta el binario", not log_b.exists(), "el falso registró llamadas")

        # (d) Todo limpio: 0 y capturas claras y oscuras en --out.
        out_dir = tmp / "capturas"
        log_d = tmp / "log-d.jsonl"
        env = make_env(fake_dir, tmp / "state-d", log_d)
        before_tree = snapshot(REPO)
        proc = run(env, str(artifact), "--out", str(out_dir), cwd=REPO)
        after_tree = snapshot(REPO)
        out = proc.stdout + proc.stderr
        check("limpio: código 0", proc.returncode == 0, f"código {proc.returncode}\n{out}")
        for width in WIDTHS:
            for theme in ("claro", "oscuro"):
                shot = out_dir / f"informe-x-{width}-{theme}.png"
                check(f"limpio: captura {theme} a {width}", shot.is_file(), f"falta {shot}\n{out}")
        check("limpio: informe con el directorio", str(out_dir) in out, out)
        check("limpio: el proyecto no cambia", before_tree == after_tree,
              f"añadidos {sorted(set(after_tree) - set(before_tree))} "
              f"borrados {sorted(set(before_tree) - set(after_tree))}")

        # (c) Desborde en un ancho: 1 y el mensaje nombra el ancho.
        log_c = tmp / "log-c.jsonl"
        env = make_env(fake_dir, tmp / "state-c", log_c, FAKE_OVERFLOW_WIDTH="768")
        proc = run(env, str(artifact), "--out", str(tmp / "capturas-c"))
        out = proc.stdout + proc.stderr
        check("desborde: código 1", proc.returncode == 1, f"código {proc.returncode}\n{out}")
        check("desborde: nombra el ancho", "768" in out and "desborde" in out, out)

        # (e) Salida ininteligible: aviso, no fallo duro.
        log_e = tmp / "log-e.jsonl"
        env = make_env(fake_dir, tmp / "state-e", log_e, FAKE_EVAL_GARBAGE="1")
        proc = run(env, str(artifact), "--out", str(tmp / "capturas-e"))
        out = proc.stdout + proc.stderr
        check("ininteligible: código 0", proc.returncode == 0, f"código {proc.returncode}\n{out}")
        check("ininteligible: avisa", "no se entendió" in out and "Aviso" in out, out)

        # Errores de consola también son hallazgo.
        log_f = tmp / "log-f.jsonl"
        env = make_env(fake_dir, tmp / "state-f", log_f, FAKE_CONSOLE_ERRORS="1")
        proc = run(env, str(artifact), "--out", str(tmp / "capturas-f"))
        out = proc.stdout + proc.stderr
        check("consola: código 1", proc.returncode == 1, f"código {proc.returncode}\n{out}")
        check("consola: nombra el error", "consola" in out and "1 error" in out, out)

        # Uso incorrecto: 2.
        env = make_env(fake_dir, tmp / "state-g", tmp / "log-g.jsonl")
        proc = run(env, str(artifact), "--widths", "390,ancho")
        check("uso incorrecto: código 2", proc.returncode == 2, f"código {proc.returncode}")
        proc = run(env, str(tmp / "no-existe.html"))
        check("artefacto ausente: código 2", proc.returncode == 2, f"código {proc.returncode}")

    if failures:
        print(f"{failures} comprobación(es) fallidas de {checks}.")
        return 1
    print(f"OK: {checks} comprobaciones pasan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
