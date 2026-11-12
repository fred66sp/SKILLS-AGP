#!/usr/bin/env python3
"""Verificación perceptiva medible de un artefacto HTML de explain-html.

Uso:
    python3 perceive.py <ruta.html> [--widths 390,768,1440] [--out DIR]
                        [--session NAME] [--dry-run]

Abre el artefacto por file:// con playwright-cli, recorre cada ancho, mide el
desborde horizontal, captura el artefacto en tema claro y oscuro y recoge los
errores de consola. Por defecto las capturas van a un directorio temporal
propio; --out permite elegir otro, y entonces el script escribe donde le digas.
La CLI corre con una sesión sin perfil persistente y un cwd temporal para no
dejar estado en el proyecto. Si una medición no se entiende, el informe lo dice
y no afirma que el artefacto esté limpio: mide y entrega evidencia, la calidad
visual la juzga la persona.

Códigos de salida:
    0  sin desborde horizontal ni errores de consola
    1  hay desborde horizontal o errores de consola
    2  uso incorrecto
    3  no hay playwright-cli o no se pudo abrir el navegador
"""
import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BINARY = "playwright-cli"
DEFAULT_WIDTHS = "390,768,1440"
VIEWPORT_HEIGHT = 900
TIMEOUT = 120

OVERFLOW_EXPR = (
    "() => document.documentElement.scrollWidth > document.documentElement.clientWidth"
)
LIGHT_EXPR = (
    "() => { localStorage.setItem('explain-html:theme', 'light');"
    " document.documentElement.setAttribute('data-theme', 'light'); return true; }"
)
DARK_EXPR = (
    "() => { localStorage.setItem('explain-html:theme', 'dark');"
    " document.documentElement.setAttribute('data-theme', 'dark'); return true; }"
)
CONSOLE_ERRORS = re.compile(r"Errors:\s*(\d+)", re.IGNORECASE)
CONSOLE_ERROR_LINE = re.compile(r"\berror\b", re.IGNORECASE)
SLUG_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")

MANUAL = (
    "Abre el artefacto con un navegador y pide a la persona que lo revise a "
    "390, 768 y 1440 px, en tema claro y oscuro."
)


def parse_widths(raw: str) -> list[int]:
    widths: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            width = int(part)
        except ValueError:
            raise ValueError(f"ancho no numérico: «{part}»") from None
        if not 200 <= width <= 4000:
            raise ValueError(f"ancho fuera de rango (200-4000): {width}")
        widths.append(width)
    if not widths:
        raise ValueError("no hay ningún ancho que probar")
    return widths


def slugify(stem: str) -> str:
    slug = SLUG_UNSAFE.sub("-", stem).strip("-")
    return slug or "artefacto"


def build_plan(binary: str, session: str, url: str, widths: list[int],
               out: Path, slug: str) -> list[tuple[str, list[str], int | None]]:
    cli = [binary, f"-s={session}"]
    plan: list[tuple[str, list[str], int | None]] = [
        ("abrir el artefacto", cli + ["open", url], None),
    ]
    for width in widths:
        name = f"{slug}-{width}"
        plan.extend([
            ("preparar el ancho", cli + ["resize", str(width), str(VIEWPORT_HEIGHT)], width),
            ("forzar tema claro", cli + ["--raw", "eval", LIGHT_EXPR], width),
            ("medir desborde", cli + ["--raw", "eval", OVERFLOW_EXPR], width),
            ("capturar en claro", cli + ["screenshot", f"--filename={out / (name + '-claro.png')}"], width),
            ("forzar tema oscuro", cli + ["--raw", "eval", DARK_EXPR], width),
            ("capturar en oscuro", cli + ["screenshot", f"--filename={out / (name + '-oscuro.png')}"], width),
        ])
    plan.extend([
        ("recoger errores de consola", cli + ["console", "error", "--all"], None),
        ("cerrar la sesión", cli + ["close"], None),
    ])
    return plan


def print_plan(plan: list[tuple[str, list[str], int | None]]) -> None:
    for purpose, argv, _ in plan:
        print(f"# {purpose}")
        print(shlex.join(argv))
    print(f"# {MANUAL}")


def call(argv: list[str], workdir: Path) -> tuple[subprocess.CompletedProcess | None, str]:
    try:
        return subprocess.run(
            argv, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=TIMEOUT, cwd=str(workdir),
        ), ""
    except subprocess.TimeoutExpired:
        return None, f"timeout de {TIMEOUT} s"
    except OSError as exc:
        return None, str(exc)


def response_text(proc: subprocess.CompletedProcess) -> str:
    return (proc.stdout or "") + (proc.stderr or "")


def parse_bool(text: str) -> bool | None:
    value = text.strip().strip('"').strip("'").lower()
    if value in ("true", "1", "yes"):
        return True
    if value in ("false", "0", "no"):
        return False
    return None


def parse_console_errors(text: str) -> int | None:
    """Devuelve el número de errores, o None si la respuesta no se entiende."""
    if not text.strip():
        return 0
    match = CONSOLE_ERRORS.search(text)
    if match:
        return int(match.group(1))
    lines = [line for line in text.splitlines()
             if CONSOLE_ERROR_LINE.search(line) and "errors:" not in line.lower()]
    if lines:
        return len(lines)
    if text.strip():
        return None
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verifica capturas, desborde horizontal y consola de un artefacto HTML",
    )
    parser.add_argument("artifact", help="Ruta del artefacto .html")
    parser.add_argument("--widths", default=DEFAULT_WIDTHS, help="Anchos separados por comas")
    parser.add_argument("--out", help="Directorio de capturas (por defecto, uno temporal)")
    parser.add_argument("--session", help="Nombre de la sesión de playwright-cli")
    parser.add_argument("--dry-run", action="store_true",
                        help="Imprime los comandos y sale sin abrir navegador")
    args = parser.parse_args(argv)

    artifact = Path(args.artifact).expanduser()
    if not artifact.is_file():
        print(f"ERROR: no existe el artefacto: {artifact}", file=sys.stderr)
        return 2
    try:
        widths = parse_widths(args.widths)
    except ValueError as exc:
        print(f"ERROR: --widths no es válido: {exc}", file=sys.stderr)
        return 2

    out = Path(args.out).expanduser().resolve() if args.out else None
    session = args.session or f"perceive-{os.getpid()}"
    slug = slugify(artifact.stem)
    url = artifact.resolve().as_uri()
    binary = shutil.which(BINARY)

    if args.dry_run:
        planned = out or Path(tempfile.gettempdir()) / "explain-html-perceive-<aleatorio>"
        if out is None:
            print("# --out: directorio temporal aleatorio; se crea al ejecutar")
        print_plan(build_plan(binary or BINARY, session, url, widths, planned, slug))
        return 0

    if binary is None:
        print(f"No se encontró {BINARY} en PATH.", file=sys.stderr)
        print(MANUAL, file=sys.stderr)
        return 3

    if out is None:
        out = Path(tempfile.mkdtemp(prefix="explain-html-perceive-"))
    out.mkdir(parents=True, exist_ok=True)
    plan = build_plan(binary, session, url, widths, out, slug)
    # cwd propio para la CLI: sus artefactos de sesión no caen en el proyecto.
    workdir = Path(tempfile.mkdtemp(prefix="explain-html-perceive-cli-"))
    warnings: list[str] = []
    incomplete: list[str] = []
    overflows: list[int] = []
    console_errors = 0
    shots: list[Path] = []
    opened = False
    closed = False

    try:
        for purpose, cmd, width in plan:
            proc, problem = call(cmd, workdir)
            if problem:
                if purpose == "abrir el artefacto":
                    print(f"No se pudo abrir el navegador: {problem}", file=sys.stderr)
                    print(MANUAL, file=sys.stderr)
                    return 3
                warnings.append(f"{purpose}: {problem}")
                continue
            text = response_text(proc)
            if purpose == "abrir el artefacto":
                if proc.returncode != 0:
                    detail = text.strip().splitlines()[:2]
                    print("No se pudo abrir el navegador: " + " / ".join(detail), file=sys.stderr)
                    print(MANUAL, file=sys.stderr)
                    return 3
                opened = True
                continue
            if purpose == "cerrar la sesión":
                closed = True
            if proc.returncode != 0:
                detail = text.strip().splitlines()[:1]
                warnings.append(
                    f"{purpose} devolvió {proc.returncode}" + (f": {detail[0]}" if detail else "")
                )
                incomplete.append(f"{purpose}" + (f" a {width} px" if width else ""))
                continue
            if purpose == "medir desborde":
                value = parse_bool(proc.stdout or "")
                if value is None:
                    warnings.append(
                        f"no se entendió la respuesta de desborde a {width} px; "
                        "no se marca el artefacto como fallido"
                    )
                    incomplete.append(f"desborde a {width} px")
                elif value:
                    overflows.append(width)
            elif purpose.startswith("capturar"):
                match = re.search(r"--filename=(.+)$", " ".join(cmd))
                if match:
                    shot = Path(match.group(1))
                    if shot.is_file():
                        shots.append(shot)
                    else:
                        warnings.append(f"no se creó la captura {shot}")
                        incomplete.append(f"{purpose} a {width} px")
            elif purpose == "recoger errores de consola":
                count = parse_console_errors(text)
                if count is None:
                    warnings.append(
                        "no se entendió la salida de consola; revísala a mano "
                        "(el artefacto no se marca como fallido)"
                    )
                    incomplete.append("errores de consola")
                else:
                    console_errors = count
    finally:
        if opened and not closed:
            call([binary, f"-s={session}", "close"], workdir)
        shutil.rmtree(workdir, ignore_errors=True)

    for warning in warnings:
        print(f"Aviso: {warning}", file=sys.stderr)

    print(f"Verificación perceptiva: {artifact}")
    if shots:
        print(f"Capturas en {out}:")
        for shot in shots:
            print(f"  - {shot}")
    else:
        print(f"Sin capturas en {out}: revisa los avisos antes de dar la revisión por hecha.")

    findings: list[str] = []
    for width in overflows:
        findings.append(f"desborde horizontal a {width} px")
    if console_errors:
        findings.append(f"{console_errors} error(es) de consola")
    if findings:
        print("Hallazgos:")
        for finding in findings:
            print(f"  - {finding}")
        return 1

    if incomplete:
        print("Medición incompleta: " + ", ".join(incomplete) + ".")
        print("Revisa las capturas a mano; no des la revisión perceptiva por hecha.")
        return 0

    print("Sin desborde horizontal ni errores de consola.")
    print("Revisa las capturas: el script mide, la calidad visual la juzgas tú.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
