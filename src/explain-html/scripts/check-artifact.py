#!/usr/bin/env python3
"""Verifica la autocontención de un artefacto HTML de explain-html.

Uso: python3 check-artifact.py <ruta.html> [ruta.html ...]

Un artefacto es autocontenido cuando funciona igual abierto por file:// que
servido: todo CSS, JS y SVG en línea, toda imagen como data: URI o SVG
incrustado, sin CDN, sin fuentes remotas y sin ficheros compañeros. El script
comprueba eso, que el artefacto tenga título, que su bloque de procedencia
—prompt, fecha, familia y fuentes— esté completo y que el HTML esté bien
formado (etiquetas balanceadas y html/head/body sin anidar).

Además emite avisos, que no impiden la entrega: pares texto/fondo del :root
por debajo de WCAG AA 4.5:1 y ficheros de más de 100000 bytes. No valida la
calidad del contenido ni la accesibilidad completa: eso es criterio del agente.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

import artifact_meta

# src= y href= de recursos cargados: cualquier valor que no sea inline o
# ancla interno rompe la autocontención. Los <a href> de texto sí pueden
# enlazar a páginas externas: son contenido, no recursos.
LOADING_TAGS = re.compile(
    r"<(?P<tag>script|link|img|source|track|iframe|embed|object|use|image)\b[^>]*?>",
    re.IGNORECASE,
)
SRC_HREF = re.compile(r'''\b(?:src|href)\s*=\s*["'](?P<val>[^"']*)["']''', re.IGNORECASE)
CSS_URL = re.compile(r'''url\(\s*["']?(?P<val>[^"')]+)["']?\s*\)''', re.IGNORECASE)
CSS_IMPORT = re.compile(r'''@import\s+(?:url\(\s*)?["']?(?P<val>[^"'();\s]+)''', re.IGNORECASE)
TITLE = re.compile(r"<title>\s*(?P<val>[^<]+?)\s*</title>", re.IGNORECASE)

INLINE_OK = re.compile(r"^(data:|#|$)", re.IGNORECASE)

# Elementos sin cierre y elementos cuyo cierre es opcional en HTML: no se
# exige balancearlos, solo que no haya anidamiento cruzado con los anteriores.
VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}
OPTIONAL_CLOSE = {
    "p", "li", "dt", "dd", "tr", "td", "th", "thead", "tbody", "tfoot",
    "option", "optgroup", "rt", "rp", "colgroup",
}

ROOT_BLOCK = re.compile(r":root(?:\s*\[[^\]]*\])?\s*\{(?P<body>[^}]*)\}", re.IGNORECASE)
COLOR_PROP = re.compile(
    r"--(?P<name>[A-Za-z0-9_-]+)\s*:\s*(?P<value>#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?)\b\s*;?"
)
FOREGROUND_ROLES = {"text", "text-dim", "muted", "fg", "ink", "accent", "ok", "warn", "err"}
BACKGROUND_ROLES = {"bg", "surface", "sunken", "background"}
MIN_CONTRAST = 4.5
MAX_BYTES = 100_000


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


class StructureChecker(HTMLParser):
    """Pila de etiquetas para detectar HTML mal formado, sin dependencias."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, int]] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in VOID_ELEMENTS:
            return
        if tag in ("html", "head", "body") and any(name == tag for name, _ in self.stack):
            self.errors.append(
                f"línea {self.getpos()[0]}: se anida <{tag}> dentro de otro <{tag}>"
            )
            return
        self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in ("html", "head", "body"):
            self.errors.append(
                f"línea {self.getpos()[0]}: <{tag}/> no puede cerrarse en su apertura"
            )

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        line = self.getpos()[0]
        if tag in VOID_ELEMENTS:
            self.errors.append(f"línea {line}: </{tag}> cierra un elemento vacío")
            return
        positions = [index for index, (name, _) in enumerate(self.stack) if name == tag]
        if not positions:
            self.errors.append(f"línea {line}: </{tag}> aparece sin su apertura")
            return
        index = positions[-1]
        between = self.stack[index + 1:]
        if any(name not in OPTIONAL_CLOSE for name, _ in between):
            name, opened = between[-1]
            self.errors.append(
                f"línea {line}: </{tag}> llega con <{name}> abierto en la línea "
                f"{opened}; cierra <{name}> antes"
            )
        del self.stack[index:]

    def unclosed(self) -> list[tuple[str, int]]:
        return [(name, line) for name, line in self.stack if name not in OPTIONAL_CLOSE]


def luminance(value: str) -> float | None:
    """Luminancia relativa de #rgb o #rrggbb; None si el valor no es un color."""
    digits = value.lstrip("#")
    if len(digits) == 3:
        digits = "".join(ch * 2 for ch in digits)
    if len(digits) != 6:
        return None
    try:
        channels = [int(digits[index:index + 2], 16) / 255 for index in (0, 2, 4)]
    except ValueError:
        return None

    def linear(channel: float) -> float:
        return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(channel) for channel in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(first: str, second: str) -> float | None:
    first_lum, second_lum = luminance(first), luminance(second)
    if first_lum is None or second_lum is None:
        return None
    high, low = max(first_lum, second_lum), min(first_lum, second_lum)
    return (high + 0.05) / (low + 0.05)


def has_role(name: str, roles: set[str]) -> bool:
    return name in roles or any(name.endswith("-" + role) for role in roles)


def contrast_warnings(path: Path, text: str) -> list[str]:
    """Avisa de pares texto/fondo del :root por debajo de WCAG AA."""
    warnings: list[str] = []
    for block in ROOT_BLOCK.finditer(text):
        properties = {
            prop.group("name"): prop.group("value")
            for prop in COLOR_PROP.finditer(block.group("body"))
        }
        foregrounds = {name: value for name, value in properties.items()
                       if has_role(name, FOREGROUND_ROLES)}
        backgrounds = {name: value for name, value in properties.items()
                       if has_role(name, BACKGROUND_ROLES)}
        line = line_of(text, block.start())
        for fg_name, fg_value in foregrounds.items():
            for bg_name, bg_value in backgrounds.items():
                ratio = contrast_ratio(fg_value, bg_value)
                if ratio is not None and ratio < MIN_CONTRAST:
                    warnings.append(
                        f"{path}:{line}: --{fg_name} sobre --{bg_name} da "
                        f"{ratio:.1f}:1, por debajo de WCAG AA ({MIN_CONTRAST}:1). "
                        "Sube el contraste del texto o del fondo en ese :root."
                    )
    return warnings


def structure_errors(path: Path, text: str) -> list[str]:
    checker = StructureChecker()
    try:
        checker.feed(text)
        checker.close()
    except Exception as exc:  # html.parser es tolerante; si falla, se informa.
        return [f"{path}: no se pudo analizar el HTML ({exc}); revisa que las etiquetas no estén cortadas."]
    errors = [f"{path}: HTML mal formado: {message}. Corrige el balance de etiquetas."
              for message in checker.errors]
    for tag, line in checker.unclosed():
        errors.append(
            f"{path}:{line}: no se cierra <{tag}>; añade su etiqueta de cierre o elimínalo."
        )
    return errors


def check_artifact(path: Path) -> tuple[list[str], list[str]]:
    """Devuelve (errores, avisos): los errores impiden la entrega, los avisos no."""
    errors: list[str] = []
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"{path}: el fichero no existe. Genera el artefacto antes de verificarlo."], warnings
    except UnicodeDecodeError as exc:
        return [f"{path}: no es texto UTF-8 ({exc}); un HTML de texto plano no debería fallar aquí."], warnings

    if path.suffix.lower() != ".html":
        errors.append(f"{path}: la extensión no es .html; los artefactos son un único .html.")

    title = TITLE.search(text)
    if not title:
        errors.append(f"{path}: falta <title>. Un artefacto sin título no se encuentra ni se nombra en el cierre.")
    elif "ASUNTO DEL ARTEFACTO" in title.group("val"):
        errors.append(f"{path}: <title> conserva el marcador de la plantilla; pon el asunto concreto.")

    meta = artifact_meta.find(text)
    if meta is None:
        errors.append(f"{path}: {artifact_meta.MISSING}")
    else:
        _, problems = artifact_meta.load(meta)
        for problem in problems:
            errors.append(f"{path}:{line_of(text, meta.start())}: {problem}")

    for tag in LOADING_TAGS.finditer(text):
        tag_text = tag.group(0)
        tag_name = tag.group("tag").lower()
        for attr in SRC_HREF.finditer(tag_text):
            value = attr.group("val").strip()
            if INLINE_OK.match(value):
                continue
            errors.append(
                f"{path}:{line_of(text, tag.start())}: <{tag_name}> carga «{value}», que no va en línea. "
                f"Incrusta el recurso (CSS/JS en línea, imagen data: o SVG) o elimínalo."
            )

    for rule in (CSS_URL, CSS_IMPORT):
        for match in rule.finditer(text):
            value = match.group("val").strip()
            if INLINE_OK.match(value):
                continue
            errors.append(
                f"{path}:{line_of(text, match.start())}: CSS carga «{value}» con {match.group(0).split('(')[0].strip()}. "
                f"Incrusta el recurso en el propio fichero o elimínalo."
            )

    errors.extend(structure_errors(path, text))
    warnings.extend(contrast_warnings(path, text))

    size = len(text.encode("utf-8"))
    if size > MAX_BYTES:
        warnings.append(
            f"{path}: ocupa {size} bytes, por encima de {MAX_BYTES}. El artefacto se "
            "descontrola: mueve el detalle a un artefacto enlazado o recorta contenido; "
            "no comprimas el CSS."
        )

    return errors, warnings


def main() -> int:
    args = sys.argv[1:]
    if not args or any(a in ("-h", "--help") for a in args):
        print(__doc__.strip())
        return 0 if args else 2

    all_errors: list[str] = []
    all_warnings: list[str] = []
    checked = 0
    for raw in args:
        path = Path(raw)
        errors, warnings = check_artifact(path)
        checked += 1 if not any("no existe" in error for error in errors) else 0
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    if all_warnings:
        print("Avisos (no impiden la entrega, pero revísalos):", file=sys.stderr)
        for warning in all_warnings:
            print(f"  - {warning}", file=sys.stderr)

    if all_errors:
        print("El artefacto no pasa la verificación; corrige antes de abrirlo en el navegador:")
        for error in all_errors:
            print(f"  - {error}")
        return 1

    print(f"OK: {checked} artefacto(s) autocontenido(s), bien formado(s), con título y procedencia completa.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
