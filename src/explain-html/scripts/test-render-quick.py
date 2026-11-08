#!/usr/bin/env python3
"""Pruebas de scripts/render-quick.py: esquema válido, validación, determinismo y autocontención.

Uso: python3 test-render-quick.py
Sale 0 si todo pasa; imprime el caso fallido y sale 1 si no.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("render-quick.py")
CHECKER = Path(__file__).with_name("check-artifact.py")

VALID = {
    "titulo": "Estado <semana> 45",
    "lead": "Qué cambió y qué falta.",
    "familia": "informe",
    "procedencia": {
        "prompt": "Pásame el estado de la semana",
        "fecha": "2026-11-08",
        "fuentes": ["git log", "src/x.py:12"],
    },
    "secciones": [
        {
            "titulo": "Resumen",
            "bloques": [
                {"tipo": "parrafo", "texto": "Texto con <etiquetas> escapadas."},
                {"tipo": "cifra", "valor": 12, "etiqueta": "tareas abiertas"},
                {"tipo": "lista", "items": ["Uno", "Dos"]},
            ],
        },
        {
            "titulo": "Detalle",
            "bloques": [
                {
                    "tipo": "tabla",
                    "cabeceras": ["Tarea", "Estado"],
                    "filas": [["A", "hecho"], ["B", "en curso"]],
                },
                {"tipo": "nota", "texto": "Una nota al margen."},
            ],
        },
    ],
    "desconocidos": ["El estado del despliegue no consta."],
}


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
    )


def write(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        schema = tmp / "esquema.json"
        write(schema, VALID)
        out = tmp / "artefacto.html"
        first = run(str(schema), str(out))
        second = run(str(schema), str(tmp / "copia.html"))
        html = out.read_text(encoding="utf-8") if out.is_file() else ""
        checks = [
            ("código 0", first.returncode == 0),
            ("salida creada", out.is_file()),
            ("título escapado", "Estado &lt;semana&gt; 45" in html),
            ("texto escapado", "&lt;etiquetas&gt;" in html),
            ("cifra", ">12<" in html),
            ("tabla", "<table>" in html and "<td>B</td>" in html),
            ("nota", 'class="note"' in html),
            ("desconocidos", 'id="desconocidos"' in html),
            ("procedencia", '"familia": "informe"' in html),
            ("determinista", second.returncode == 0 and html == (tmp / "copia.html").read_text(encoding="utf-8")),
        ]
        for name, ok in checks:
            if not ok:
                print(f"FALLO «{name}»\n{first.stdout}{first.stderr}")
                failures += 1

        check = subprocess.run([sys.executable, str(CHECKER), str(out)], capture_output=True, text=True)
        if check.returncode != 0:
            print(f"FALLO «la salida pasa check-artifact»\n{check.stdout}{check.stderr}")
            failures += 1

        bad_block = json.loads(json.dumps(VALID))
        bad_block["secciones"][0]["bloques"].append({"tipo": "video", "texto": "x"})
        write(tmp / "malo.json", bad_block)
        bad_out = tmp / "malo.html"
        result = run(str(tmp / "malo.json"), str(bad_out))
        if result.returncode != 1 or "bloques[3]" not in result.stderr or "tipo" not in result.stderr:
            print(f"FALLO «bloque inválido»: código {result.returncode}\n{result.stdout}{result.stderr}")
            failures += 1
        if bad_out.exists():
            print("FALLO «bloque inválido»: no debe escribir la salida")
            failures += 1

        bad_family = json.loads(json.dumps(VALID))
        bad_family["familia"] = "otra"
        write(tmp / "familia.json", bad_family)
        result = run(str(tmp / "familia.json"), str(tmp / "familia.html"))
        if result.returncode != 1 or "familia" not in result.stderr:
            print(f"FALLO «familia inválida»: código {result.returncode}\n{result.stdout}{result.stderr}")
            failures += 1

        empty = json.loads(json.dumps(VALID))
        empty["procedencia"]["prompt"] = ""
        write(tmp / "vacio.json", empty)
        result = run(str(tmp / "vacio.json"), str(tmp / "vacio.html"))
        if result.returncode != 1 or "prompt" not in result.stderr:
            print(f"FALLO «prompt vacío»: código {result.returncode}\n{result.stdout}{result.stderr}")
            failures += 1

        usage = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        if usage.returncode != 2:
            print(f"FALLO «sin argumentos»: código {usage.returncode}, esperado 2")
            failures += 1

    if failures:
        print(f"{failures} caso(s) fallidos.")
        return 1
    print("OK: render-quick valida, escapa, renderiza determinista y produce HTML autocontenido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
