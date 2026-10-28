# Reglas de CLI

Léela en el paso 5, antes de elegir comandos, flags y salida.

## 1. Elección de la herramienta

| Situación | Elección |
|---|---|
| CLI pequeña, sin dependencias | `argparse` |
| El proyecto ya usa Typer o Click | Se conserva esa herramienta |
| Subcomandos, ayuda rica y validación declarativa | Typer o Click, con la dependencia justificada |
| Script de un solo uso | `argparse` o `sys.argv` con validación explícita |

Una CLI no añade Typer para tener colores. El contrato de salida y códigos es el mismo con cualquier parser.

## 2. Contrato de comportamiento

- `--help` y `--version` funcionan sin efectos y sin requerir configuración.
- Los argumentos se validan al entrar; un fallo de uso no deja trabajo a medias.
- `stdout` lleva el resultado; `stderr` lleva diagnóstico, progreso y avisos.
- `--json` es estable y parseable: sin mensajes humanos mezclados, sin trazas.
- Códigos de salida acotados:

| Código | Significado |
|---|---|
| `0` | Éxito |
| `1` | Fallo de la operación |
| `2` | Uso incorrecto o argumentos inválidos |
| `130` | Interrumpido por el usuario (`SIGINT`) |

- Una operación destructiva exige confirmación explícita y `--yes` para el modo no interactivo.
- `--dry-run` describe lo que haría y no muta nada; su salida es válida para un agente.
- La operación es idempotente cuando el dominio lo permite: repetirla no duplica efectos.

## 3. Estructura con `argparse`

```python
import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="herramienta", description="...")
    parser.add_argument("--version", action="version", version="herramienta 1.0.0")
    sub = parser.add_subparsers(dest="command", required=True)

    sync = sub.add_parser("sync", help="sincroniza el índice")
    sync.add_argument("--dry-run", action="store_true")
    sync.add_argument("--yes", action="store_true")
    sync.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run(args)
    except KeyboardInterrupt:
        print("interrumpido", file=sys.stderr)
        return 130
```

`argparse` devuelve `2` en un error de uso. No captures `SystemExit` para cambiarlo sin una razón.

## 4. Salida

```python
def emit(data: dict, as_json: bool) -> None:
    if as_json:
        json.dump(data, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        return
    print(f"{data['accion']}: {data['total']} elementos")
```

- Un resultado legible se escribe con `print` a `stdout`; un diagnóstico, con `print(..., file=sys.stderr)` o `logging`.
- Un aviso en modo `--json` va a `stderr`; nunca dentro del objeto de datos salvo como campo declarado.
- No se imprime una traza al usuario: se captura, se registra en `stderr` con contexto y se devuelve un código.

## 5. Confirmación e interactividad

- Si `--yes` no está y `stdin` no es un TTY, la operación se niega con código `2`; no espera una entrada que nunca llegará.
- La pregunta de confirmación nombra la acción y su alcance, y por defecto es «no».
- `--force` no sustituye a la confirmación; si existe, su efecto se documenta y se limita al caso que lo justifica.
- Una CLI que se usa desde un agente no abre un editor ni un paginador.

## 6. Punto de entrada

```toml
[project.scripts]
herramienta = "paquete.cli:main"
```

- `main()` devuelve un `int`; el `console_scripts` lo usa como código de salida.
- El módulo `paquete/cli.py` no ejecuta trabajo al importarse.
- `python -m paquete` se admite con un `__main__.py` que llama a `main()`.
- La configuración se carga después de parsear los argumentos, para que `--help` no dependa de un fichero ausente.

## 7. Pruebas

La CLI se prueba ejecutando el proceso, no importando `main` y comprobando variables internas. Los argumentos, el entorno y `stdin` se controlan; `stdout`, `stderr` y el código de salida se comprueban por separado. Esa capa pertenece a `python-testing-and-verification`.
