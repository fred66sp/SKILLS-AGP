#!/usr/bin/env python3
"""Pruebas de scripts/check-artifact.py: autocontención, título, procedencia y códigos de salida.

Uso: python3 test-check-artifact.py
Sale 0 si todo pasa; imprime el caso fallido y sale 1 si no.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import artifact_meta

CHECKER = Path(__file__).with_name("check-artifact.py")
ASSETS = Path(__file__).resolve().parents[1] / "assets"

GOOD_META = (
    '<!-- procedencia: {"prompt": "estado semanal", "fecha": "2026-11-08", '
    '"familia": "informe", "fuentes": ["git log"]} -->'
)
EMPTY_META = '<!-- procedencia: {"prompt": "", "fecha": "", "familia": "", "fuentes": []} -->'

BASE = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>{title}</title>{extra}
<style>p {{ background: url({url}) }}</style></head>
<body>
{meta}
<p>hola</p><script>var a = 1;</script></body></html>
"""


def run(tmp: Path, name: str, content: str | None) -> tuple[int, str]:
    target = tmp / name
    if content is not None:
        target.write_text(content, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(CHECKER), str(target)],
        capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    cases: list[tuple[str, str | None, int, list[str]]] = [
        ("autocontenido con título y procedencia", BASE.format(title="Estado semana 45", extra="", url="data:image/png;base64,AAA", meta=GOOD_META), 0, []),
        ("con script por CDN", BASE.format(title="Estado", extra='<script src="https://cdn.jsdelivr.net/x.js"></script>', url="#", meta=GOOD_META), 1, ["cdn.jsdelivr.net"]),
        ("con hoja externa", BASE.format(title="Estado", extra='<link rel="stylesheet" href="temas.css">', url="#", meta=GOOD_META), 1, ["temas.css"]),
        ("con url() remota en CSS", BASE.format(title="Estado", extra="", url="https://fonts.googleapis.com/f.css", meta=GOOD_META), 1, ["fonts.googleapis.com"]),
        ("con imagen por URL", BASE.format(title="Estado", extra='<img src="https://example.com/f.png" alt="">', url="#", meta=GOOD_META), 1, ["example.com"]),
        ("sin título", BASE.format(title="", extra="", url="#", meta=GOOD_META).replace("<title></title>", ""), 1, ["falta <title>"]),
        ("título sin personalizar", BASE.format(title="ASUNTO DEL ARTEFACTO", extra="", url="#", meta=GOOD_META), 1, ["marcador"]),
        ("procedencia ausente", BASE.format(title="Estado", extra="", url="#", meta=""), 1, ["falta el bloque de procedencia"]),
        ("procedencia con campos vacíos", BASE.format(title="Estado", extra="", url="#", meta=EMPTY_META), 1, ["vacío", "prompt", "fecha", "familia", "fuentes"]),
        ("procedencia con JSON roto", BASE.format(title="Estado", extra="", url="#", meta="<!-- procedencia: {prompt: x} -->"), 1, ["JSON válido"]),
        ("procedencia con familia inválida", BASE.format(title="Estado", extra="", url="#", meta='<!-- procedencia: {"prompt": "x", "fecha": "2026-11-08", "familia": "otra", "fuentes": ["y"]} -->'), 1, ["familia"]),
    ]
    failures = 0
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        for name, content, expected_code, needles in cases:
            code, out = run(tmp, name.replace(" ", "-") + ".html", content)
            if code != expected_code:
                print(f"FALLO «{name}»: código {code}, esperado {expected_code}\n{out}")
                failures += 1
                continue
            missing = [n for n in needles if n not in out]
            if missing:
                print(f"FALLO «{name}»: el mensaje no menciona {missing}\n{out}")
                failures += 1
        code, out = run(tmp, "inexistente.html", None)
        if code != 1 or "no existe" not in out:
            print(f"FALLO «fichero inexistente»: código {code}\n{out}")
            failures += 1
        # Sin argumentos: la invocación vacía sale 2 con la ayuda por stderr.
        proc = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True)
        if proc.returncode != 2:
            print(f"FALLO «sin argumentos»: código {proc.returncode}, esperado 2")
            failures += 1

    # Las nueve plantillas (base y una por familia) traen el bloque vacío listo
    # para rellenar; si falta una, el contrato no se puede cumplir copiándola.
    templates = [ASSETS / "plantilla-artefacto.html"] + [
        ASSETS / f"plantilla-{slug}.html" for slug in artifact_meta.FAMILIES
    ]
    for template in templates:
        if not template.is_file():
            print(f"FALLO «plantilla»: no existe {template}")
            failures += 1
            continue
        text = template.read_text(encoding="utf-8")
        if '{"prompt": "", "fecha": "", "familia": "", "fuentes": []}' not in text:
            print(f"FALLO «plantilla»: {template.name} no trae el bloque de procedencia vacío")
            failures += 1
        if "ASUNTO DEL ARTEFACTO" not in text:
            print(f"FALLO «plantilla»: {template.name} no marca el título a sustituir")
            failures += 1

    if failures:
        print(f"{failures} caso(s) fallidos.")
        return 1
    print(f"OK: {len(cases) + 2} casos y {len(templates)} plantillas pasan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
