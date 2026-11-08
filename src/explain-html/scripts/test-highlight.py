#!/usr/bin/env python3
"""Pruebas de scripts/highlight.py: determinismo, clases, escape y códigos.

Uso: python3 test-highlight.py
Sale 0 si todo pasa; imprime el caso fallido y sale 1 si no.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("highlight.py")
ALLOWED = {"kw", "str", "com", "num", "fn"}
TOKEN = re.compile(r'class="tok-([a-z]+)"')

SAMPLES = {
    "python": 'def saluda(n):\n    # <comentario>\n    return "hola <b>" if n else 42\n',
    "go": 'func main() {\n\t// <comentario>\n\tfmt.Println("hola <b>", 42)\n}\n',
    "json": '{"ok": true, "n": -12.5, "s": "<b>"}\n',
    "bash": 'if [ -f "x<y" ]; then\n  echo $# # <comentario>\nfi\n',
    "html": '<!-- <comentario> -->\n<p class="x">hola &amp; 42</p>\n',
    "javascript": 'const f = (x) => {\n  // <comentario>\n  return "hola <b>" + x * 42;\n};\n',
    "css": '/* <comentario> */\n:root { --bg: #fafaf9; }\n.a > .b { width: 42px; }\n',
}


def run(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin, capture_output=True, text=True,
    )


def main() -> int:
    failures = 0
    checks: list[tuple[str, bool]] = []

    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        for language, sample in SAMPLES.items():
            first = run(language, stdin=sample)
            second = run(language, stdin=sample)
            checks.extend([
                (f"{language}: código 0", first.returncode == 0),
                (f"{language}: determinista", first.stdout == second.stdout),
                (f"{language}: clases esperadas", set(TOKEN.findall(first.stdout)) <= ALLOWED),
                (f"{language}: escapa HTML", "<b>" not in first.stdout
                 and ("&lt;b&gt;" in first.stdout or "&lt;comentario&gt;" in first.stdout)),
            ])

        target = tmp / "muestra.py"
        target.write_text(SAMPLES["python"], encoding="utf-8")
        from_file = run("python", str(target))
        checks.append(("fichero igual que stdin", from_file.stdout == run("python", stdin=SAMPLES["python"]).stdout))

        keyword = run("python", stdin="def x():\n    return 1\n")
        checks.append(("palabra clave marcada", '<span class="tok-kw">def</span>' in keyword.stdout))

        css = run("--css")
        checks.extend([
            ("--css código 0", css.returncode == 0),
            ("--css trae tokens", ".tok-kw" in css.stdout and ".tok-fn" in css.stdout),
        ])

        unknown = run("cobol", stdin="x")
        checks.extend([
            ("lenguaje desconocido sale 2", unknown.returncode == 2),
            ("lenguaje desconocido lista", "javascript" in unknown.stderr and "css" in unknown.stderr),
        ])

        missing = run("python", str(tmp / "no-existe.py"))
        checks.append(("fichero ausente sale 1", missing.returncode == 1))

        empty = run()
        checks.append(("sin argumentos sale 2", empty.returncode == 2))

    for name, ok in checks:
        if not ok:
            print(f"FALLO «{name}»")
            failures += 1
    if failures:
        print(f"{failures} caso(s) fallidos.")
        return 1
    print(f"OK: {len(checks)} comprobaciones de highlight en {len(SAMPLES)} lenguajes pasan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
