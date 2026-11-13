#!/usr/bin/env python3
"""Pruebas de scripts/publish.py: encadena verificación, índice y apertura.

Uso: python3 test-publish.py
Sale 0 si todo pasa; imprime el caso fallido y sale 1 si no.

Los casos usan solo directorios temporales: publicar sobre `.explanations/` del
repositorio regeneraría índices reales.
"""
import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("publish.py")

META = (
    '<!-- procedencia: {"prompt": "prueba de publicación", "fecha": "2026-11-12", '
    '"familia": "informe", "fuentes": ["test-publish.py"]} -->'
)
BAD_META = '<!-- procedencia: {"prompt": "", "fecha": "", "familia": "", "fuentes": []} -->'


def artifact(title: str, meta: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>{title}</title>
<style>p {{ color: #1c1b1a; background: #ffffff; }}</style></head>
<body>
{meta}
<p>contenido</p>
</body></html>
"""


def run(*args: str, path_value: str | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if path_value is not None:
        env["PATH"] = path_value
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, env=env,
    )


def no_open_attempt(result: subprocess.CompletedProcess) -> bool:
    output = result.stdout + result.stderr
    return not any(mark in output for mark in ("Abierto en el navegador", "Abre a mano esta ruta"))


def load_publish():
    """Importa publish.py para sustituir su abridor sin depender del entorno."""
    spec = importlib.util.spec_from_file_location("publish_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    failures = 0

    def check(name: str, ok: bool, result: subprocess.CompletedProcess | None = None) -> None:
        nonlocal failures
        if not ok:
            extra = f"\n{result.stdout}{result.stderr}" if result else ""
            print(f"FALLO «{name}»{extra}")
            failures += 1

    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        one = root / "uno"
        two = root / "dos"
        one.mkdir()
        two.mkdir()
        (one / "bien.html").write_text(artifact("Artefacto verificado", META), encoding="utf-8")
        (two / "otro.html").write_text(artifact("Segundo artefacto", META), encoding="utf-8")

        # 1. Artefacto válido: sale 0 e indexa cada carpeta distinta.
        valid = run(str(one / "bien.html"), str(two / "otro.html"), "--no-open")
        first_index = one / "index.html"
        second_index = two / "index.html"
        first_text = first_index.read_text(encoding="utf-8") if first_index.is_file() else ""
        check("válido sale 0", valid.returncode == 0, valid)
        check("válido crea índice", first_index.is_file(), valid)
        check("índice con título", "Artefacto verificado" in first_text, valid)
        check("índice por carpeta", second_index.is_file(), valid)

        # 2. Marcador en el título: sale 1, sin índice y sin intentar abrir.
        broken = root / "roto"
        broken.mkdir()
        (broken / "roto.html").write_text(
            artifact("ASUNTO DEL ARTEFACTO semanal", BAD_META), encoding="utf-8"
        )
        invalid = run(str(broken / "roto.html"), "--no-open")
        check("inválido sale 1", invalid.returncode == 1, invalid)
        check("inválido no crea índice", not (broken / "index.html").is_file(), invalid)
        check("inválido no abre", no_open_attempt(invalid), invalid)

        # 3. --no-open con PATH vacío: no se lanza wslview ni xdg-open.
        quiet_open = root / "solo"
        quiet_open.mkdir()
        (quiet_open / "solo.html").write_text(artifact("Sin apertura", META), encoding="utf-8")
        no_open = run(str(quiet_open / "solo.html"), "--no-open", path_value="")
        check("--no-open sale 0", no_open.returncode == 0, no_open)
        check("--no-open indexa", (quiet_open / "index.html").is_file(), no_open)
        check("--no-open no abre", no_open_attempt(no_open), no_open)

        # --quiet calla el resumen propio pero no la salida ajena.
        quiet = run(str(quiet_open / "solo.html"), "--no-open", "--quiet", path_value="")
        check("--quiet sale 0", quiet.returncode == 0, quiet)
        check("--quiet sin resumen", "verificados e indexados" not in quiet.stdout, quiet)

        # 4. Sin --no-open y sin bash en PATH: avisa, indexa y sale 0 igualmente.
        no_browser = root / "sin-bash"
        no_browser.mkdir()
        (no_browser / "aviso.html").write_text(artifact("Sin bash", META), encoding="utf-8")
        warned = run(str(no_browser / "aviso.html"), path_value="")
        check("sin bash sale 0", warned.returncode == 0, warned)
        check("sin bash avisa", "no hay navegador" in (warned.stdout + warned.stderr), warned)
        check("sin bash indexa", (no_browser / "index.html").is_file(), warned)

        # 5. El abridor existe pero no encuentra navegador: aviso, índice y salida 0.
        opener = root / "sin-navegador.sh"
        opener.write_text(
            "#!/usr/bin/env bash\necho 'No hay navegador disponible en este entorno.' >&2\nexit 1\n",
            encoding="utf-8",
        )
        module = load_publish()
        module.OPEN = opener
        no_opener = root / "abridor"
        no_opener.mkdir()
        (no_opener / "aviso.html").write_text(artifact("Sin abridor", META), encoding="utf-8")
        captured_out, captured_err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(captured_out), contextlib.redirect_stderr(captured_err):
            code = module.main([str(no_opener / "aviso.html")])
        text = captured_out.getvalue() + captured_err.getvalue()
        check("sin abridor: código 0", code == 0, None)
        check("sin abridor: avisa", "no hay navegador" in text.lower(), None)
        check("sin abridor: indexa", (no_opener / "index.html").is_file(), None)

        # 6. Uso incorrecto.
        missing = run(str(root / "no-existe.html"), "--no-open")
        check("ruta inexistente sale 2", missing.returncode == 2, missing)
        no_args = run()
        check("sin argumentos sale 2", no_args.returncode == 2, no_args)
        (one / "notas.txt").write_text("no es un artefacto", encoding="utf-8")
        not_html = run(str(one / "notas.txt"), "--no-open")
        check("extensión no html sale 2", not_html.returncode == 2, not_html)

    if failures:
        print(f"{failures} caso(s) fallidos.")
        return 1
    print("OK: publish verifica, indexa y abre sin salirse del contrato.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
