#!/usr/bin/env python3
"""Pruebas de scripts/build-index.py: lista, fechas, familia, enlaces y controles.

Uso: python3 test-build-index.py
Sale 0 si todo pasa; imprime el caso fallido y sale 1 si no.
"""
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SCRIPT = SCRIPTS / "build-index.py"
CHECKER = SCRIPTS / "check-artifact.py"


def artifact(title: str, meta: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>{title}</title></head>
<body>
{meta}
<p>contenido</p>
</body></html>
"""


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
    )


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw) / "explanations"
        tmp.mkdir()

        viejo = time.mktime((2026, 2, 3, 12, 0, 0, 0, 0, -1))
        (tmp / "b-sin-meta.html").write_text(artifact("Exploración sin metadatos", ""), encoding="utf-8")
        os.utime(tmp / "b-sin-meta.html", (viejo, viejo))
        (tmp / "a-con-meta.html").write_text(
            artifact("Estado verificado", '<!-- procedencia: {"prompt": "p", "fecha": "2026-01-02", '
                     '"familia": "informe", "fuentes": ["git log"]} -->'),
            encoding="utf-8",
        )
        (tmp / "c-encadenado.html").write_text(
            artifact("Plan enlazado", '<!-- procedencia: {"prompt": "p", "fecha": "2026-01-01", '
                     '"familia": "exploracion", "fuentes": ["conversación"], '
                     '"enlaces": ["a-con-meta.html", "b-sin-meta.html"]} -->'),
            encoding="utf-8",
        )
        (tmp / "notas.txt").write_text("no es un artefacto", encoding="utf-8")

        result = run(str(tmp))
        index = tmp / "index.html"
        text = index.read_text(encoding="utf-8") if index.is_file() else ""
        links_block = text.split('<span class="bucle">', 1)[-1].split("</span>", 1)[0]
        checks = [
            ("código 0", result.returncode == 0),
            ("index creado", index.is_file()),
            ("título con metadatos", "Estado verificado" in text),
            ("título sin metadatos", "Exploración sin metadatos" in text),
            ("familia legible", "Informe" in text),
            ("fecha de metadatos", "02-01-2026" in text),
            ("fecha de fichero", "03-02-2026" in text),
            ("fecha ordenable", 'data-fecha="2026-01-02"' in text
             and '<time datetime="2026-01-02">02-01-2026</time>' in text),
            ("título con el proyecto", "El catálogo de explain-html" in text),
            ("enlace relativo", 'href="a-con-meta.html"' in text),
            ("relación visible", "Enlaza:" in text),
            ("enlaces del bucle", 'href="a-con-meta.html"' in links_block
             and 'href="b-sin-meta.html"' in links_block),
            ("ignora no-html", "notas.txt" not in text),
            ("no se lista a sí mismo", 'href="index.html"' not in text),
            ("orden por fecha reciente", text.find("Exploración sin metadatos") < text.find("Estado verificado")),
            ("datos para el filtro", 'data-familia="informe"' in text
             and 'data-titulo="Estado verificado"' in text),
            ("un solo miembro del bucle", text.count('data-bucle="') == 1),
            ("chips de familia", 'data-filtro-familia="informe"' in text
             and 'data-filtro-familia="exploracion"' in text),
            ("recuento en el chip", '>Todas <span class="n">3</span>' in text),
            ("filtro por fecha", 'data-filtro-fecha="hoy"' in text
             and 'data-filtro-fecha="semana"' in text
             and 'data-filtro-fecha="mes"' in text
             and 'data-filtro-fecha="anio"' in text),
            ("paginación disponible", 'id="paginador"' in text),
            ("sin marcadores sueltos", "@@" not in text),
        ]
        for name, ok in checks:
            if not ok:
                print(f"FALLO «{name}»\n{result.stdout}{result.stderr}")
                failures += 1

        check = subprocess.run([sys.executable, str(CHECKER), str(index)], capture_output=True, text=True)
        if check.returncode != 0:
            print(f"FALLO «el índice pasa check-artifact»\n{check.stdout}{check.stderr}")
            failures += 1

        again = run(str(tmp))
        text = index.read_text(encoding="utf-8")
        if again.returncode != 0 or text.count('class="artefacto"') != 3:
            print(f"FALLO «regenerar no duplica entradas»\n{again.stdout}{again.stderr}")
            failures += 1

        vacia = Path(raw) / "vacia"
        vacia.mkdir()
        empty = run(str(vacia))
        empty_index = vacia / "index.html"
        empty_text = empty_index.read_text(encoding="utf-8") if empty_index.is_file() else ""
        empty_check = subprocess.run(
            [sys.executable, str(CHECKER), str(empty_index)], capture_output=True, text=True
        )
        if (empty.returncode != 0 or "Todavía no hay artefactos" not in empty_text
                or empty_check.returncode != 0):
            print(f"FALLO «carpeta sin artefactos»\n{empty.stdout}{empty.stderr}"
                  f"{empty_check.stdout}{empty_check.stderr}")
            failures += 1

        missing = run(str(tmp / "no-existe"))
        if missing.returncode != 2:
            print(f"FALLO «directorio inexistente»: código {missing.returncode}, esperado 2")
            failures += 1

    if failures:
        print(f"{failures} caso(s) fallidos.")
        return 1
    print("OK: build-index lista, fecha, enlaza, filtra y regenera sin duplicar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
