#!/usr/bin/env python3
"""Pruebas de scripts/tokens-from-project.py: DESIGN.md, DTCG, alias y errores.

Uso: python3 test-tokens-from-project.py
Sale 0 si todo pasa; imprime el caso fallido y sale 1 si no.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("tokens-from-project.py")

DESIGN = """# Sistema del proyecto

Tokens normativos:

```css
:root {
  --bg: #f8fafc;
  --text: #0f172a;
  --accent: #0f766e;
}
```

La prosa no se lee.
"""


def run(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin, capture_output=True, text=True,
    )


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        design = tmp / "DESIGN.md"
        design.write_text(DESIGN, encoding="utf-8")

        first = run(str(design))
        second = run(str(design))
        checks = [
            ("código 0", first.returncode == 0),
            ("bloque :root", first.stdout.startswith(":root {") and first.stdout.rstrip().endswith("}")),
            ("token de fondo", "--bg: #f8fafc;" in first.stdout),
            ("token de acento", "--accent: #0f766e;" in first.stdout),
            ("determinista", first.stdout == second.stdout),
        ]

        empty = tmp / "SIN-TOKENS.md"
        empty.write_text("# Sin tokens\n\nSolo prosa.\n", encoding="utf-8")
        result = run(str(empty))
        checks.append(("sin tokens sale 1", result.returncode == 1))
        checks.append(("sin tokens avisa", "no hay custom properties" in result.stderr))

        contract = {
            "schema": "design-system.v1",
            "tokens": {
                "color": {
                    "$type": "color",
                    "brand": {"$value": "#0f766e"},
                },
                "space": {"sm": {"$value": "4px"}},
                "accent": {"$value": "{color.brand}"},
                "shadow": {"card": {"$value": {"color": "#000", "blur": "8px"}}},
            },
        }
        json_path = tmp / "design-system.json"
        json_path.write_text(json.dumps(contract), encoding="utf-8")
        result = run(str(json_path))
        checks.extend([
            ("JSON código 0", result.returncode == 0),
            ("ruta DTCG", "--color-brand: #0f766e;" in result.stdout),
            ("dimensión", "--space-sm: 4px;" in result.stdout),
            ("alias como var", "--accent: var(--color-brand);" in result.stdout),
            ("compuesto se salta", "el token «shadow-card»" in result.stderr
             and "shadow-card" not in result.stdout),
        ])

        broken = tmp / "roto.json"
        broken.write_text("{no es json}", encoding="utf-8")
        result = run(str(broken))
        checks.append(("JSON roto sale 1", result.returncode == 1))
        checks.append(("JSON roto explica", "JSON válido" in result.stderr))

        result = run(str(tmp / "no-existe.md"))
        checks.append(("fichero ausente sale 1", result.returncode == 1))
        checks.append(("fichero ausente explica", "no se pudo leer" in result.stderr))

        result = run()
        checks.append(("sin argumentos sale 2", result.returncode == 2))

        for name, ok in checks:
            if not ok:
                print(f"FALLO «{name}»")
                failures += 1

    if failures:
        print(f"{failures} caso(s) fallidos.")
        return 1
    print(f"OK: {len(checks)} comprobaciones de tokens del proyecto pasan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
