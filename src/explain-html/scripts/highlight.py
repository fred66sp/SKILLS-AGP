#!/usr/bin/env python3
"""Resaltador determinista y mínimo para los lenguajes del proyecto.

Uso:
    python3 highlight.py <lenguaje> [fichero]   # fichero o stdin -> HTML
    python3 highlight.py --css                  # bloque CSS de los tokens

Lenguajes: go, python, json, bash, html, javascript, css. La salida es un
fragmento HTML con `<span class="tok-...">` para palabra clave (kw), cadena
(str), comentario (com), número (num) y función (fn). Todo el texto se escapa:
un `<` del código se convierte en `&lt;`. Misma entrada, misma salida, sin
dependencias ni reloj.

Para un artefacto que muestra código:

1. Pega el fragmento dentro de `<pre><code>…</code></pre>`.
2. Pega una sola vez el bloque de `--css` en el `<style>` del artefacto.
3. Ejecuta `check-artifact.py`: el CSS va en línea, así que la autocontención
   se mantiene.
"""
import argparse
import html
import re
import sys
from pathlib import Path

# Cadena de Python: prefijo opcional y comillas simples, dobles o triples.
PY_STRING = (
    r'(?:[rRbBuUfF]{0,2})(?:'
    '"""' r'(?:\\.|[^\\])*?' '"""'
    r"|'''(?:\\.|[^\\])*?'''"
    r'|"(?:\\.|[^"\\\n])*"'
    r"|'(?:\\.|[^'\\\n])*'"
    r")"
)

# Cada regla: (clase, expresión). El orden es la prioridad: un comentario gana
# a una cadena y una cadena gana a lo que haya dentro; la alternancia se evalúa
# de izquierda a derecha.
RULES: dict[str, list[tuple[str, str]]] = {
    "python": [
        ("com", r"#[^\n]*"),
        ("str", PY_STRING),
        ("kw", r"\b(?:and|as|assert|async|await|break|class|continue|def|del|elif|else|except|False|finally|for|from|global|if|import|in|is|lambda|None|nonlocal|not|or|pass|raise|return|True|try|while|with|yield|match|case)\b"),
        ("num", r"\b(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\b"),
        ("fn", r"\b[A-Za-z_]\w*(?=\s*\()"),
    ],
    "go": [
        ("com", r"//[^\n]*|/\*.*?\*/"),
        ("str", r'`[^`]*`|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'',),
        ("kw", r"\b(?:break|case|chan|const|continue|default|defer|else|fallthrough|for|func|go|goto|if|import|interface|map|package|range|return|select|struct|switch|type|var|true|false|nil|iota)\b"),
        ("num", r"\b(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?)\b"),
        ("fn", r"\b[A-Za-z_]\w*(?=\s*\()"),
    ],
    "json": [
        ("str", r'"(?:\\.|[^"\\\n])*"'),
        ("kw", r"\b(?:true|false|null)\b"),
        ("num", r"-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b"),
    ],
    "bash": [
        ("com", r"#[^\n]*"),
        ("str", r"'[^']*'|\"(?:\\.|[^\"\\])*\""),
        ("kw", r"\b(?:if|then|else|elif|fi|for|while|until|do|done|case|esac|function|in|select|time|export|local|readonly|declare|return|exit|set|unset|shift|source|alias)\b"),
        ("num", r"\b\d+\b"),
        ("fn", r"\b[A-Za-z_][\w-]*(?=\s*\()"),
    ],
    "html": [
        ("com", r"<!--.*?-->"),
        ("str", r'"[^"]*"|\'[^\']*\''),
        ("kw", r"</?[A-Za-z][\w:-]*"),
        ("num", r"\b\d+(?:\.\d+)?\b"),
    ],
    "javascript": [
        ("com", r"//[^\n]*|/\*.*?\*/"),
        ("str", r"`(?:\\.|[^`\\])*`|\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*'"),
        ("kw", r"\b(?:async|await|break|case|catch|class|const|continue|debugger|default|delete|do|else|export|extends|false|finally|for|function|if|import|in|instanceof|let|new|null|of|return|static|super|switch|this|throw|true|try|typeof|undefined|var|void|while|with|yield)\b"),
        ("num", r"\b(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?)\b"),
        ("fn", r"\b[A-Za-z_$][\w$]*(?=\s*\()"),
    ],
    "css": [
        ("com", r"/\*.*?\*/"),
        ("str", r'"[^"]*"|\'[^\']*\''),
        ("kw", r"@[\w-]+|!important\b"),
        ("num", r"#[0-9a-fA-F]{3,8}\b|\b\d+(?:\.\d+)?(?:[a-z%]+)?\b"),
        ("fn", r"[A-Za-z-]+(?=\s*:)"),
    ],
}

TOKEN_STYLE = """
.tok-kw { color: #7c3aed; font-weight: 600; }
.tok-str { color: #15803d; }
.tok-com { color: #5d5b58; font-style: italic; }
.tok-num { color: #b45309; }
.tok-fn { color: #0f766e; }
@media (prefers-color-scheme: dark) {
  .tok-kw { color: #c4b5fd; }
  .tok-str { color: #86efac; }
  .tok-com { color: #9d9b98; }
  .tok-num { color: #fcd34d; }
  .tok-fn { color: #5eead4; }
}
"""

COMPILED = {
    language: (
        re.compile(
            "|".join(f"(?P<t{index}>{pattern})" for index, (_, pattern) in enumerate(rules)),
            re.DOTALL,
        ),
        [kind for kind, _ in rules],
    )
    for language, rules in RULES.items()
}


def highlight(text: str, language: str) -> str:
    regex, kinds = COMPILED[language]
    output: list[str] = []
    last = 0
    for match in regex.finditer(text):
        output.append(html.escape(text[last:match.start()], quote=False))
        kind = kinds[int(match.lastgroup[1:])]
        output.append(
            f'<span class="tok-{kind}">{html.escape(match.group(0), quote=False)}</span>'
        )
        last = match.end()
    output.append(html.escape(text[last:], quote=False))
    return "".join(output)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Resaltado determinista de código para artefactos explain-html"
    )
    parser.add_argument("lenguaje", nargs="?", help="go, python, json, bash, html, javascript, css")
    parser.add_argument("fichero", nargs="?", help="fichero a resaltar; sin él lee stdin")
    parser.add_argument("--css", action="store_true", help="imprime el bloque CSS de los tokens")
    args = parser.parse_args(argv)

    if args.css:
        print(TOKEN_STYLE.strip())
        return 0
    if not args.lenguaje:
        parser.print_usage(sys.stderr)
        return 2
    if args.lenguaje not in RULES:
        print(
            f"ERROR: lenguaje desconocido «{args.lenguaje}». Usa uno de: "
            f"{', '.join(RULES)}.",
            file=sys.stderr,
        )
        return 2

    try:
        text = Path(args.fichero).read_text(encoding="utf-8") if args.fichero else sys.stdin.read()
    except OSError as exc:
        print(f"ERROR: no se pudo leer {args.fichero}: {exc}", file=sys.stderr)
        return 1
    except UnicodeDecodeError as exc:
        print(f"ERROR: {args.fichero} no es texto UTF-8 ({exc}).", file=sys.stderr)
        return 1

    sys.stdout.write(highlight(text, args.lenguaje))
    if not text.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
