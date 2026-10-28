# Reglas de lenguaje

Léela en los pasos 2 y 3 del procedimiento, cuando una decisión de sintaxis, datos, errores, recursos o asincronía no sea evidente.

## 1. Intérprete y compatibilidad

| Decisión | Regla | Motivo |
|---|---|---|
| Versión mínima | Se declara en `requires-python` y se repite en CI | Una sintaxis nueva sin mínimo declarado rompe instalaciones que el paquete dice soportar |
| `match` | Solo si el mínimo es 3.10 o superior | `case` es sintaxis, no una función disponible |
| `X \| Y` | Solo si el mínimo es 3.10 o superior | `types.UnionType` no existe antes |
| `Self` | `typing_extensions` si el mínimo es anterior a 3.11 | Evita duplicar el tipo del llamante |
| `tomllib` | Solo con 3.11 o superior; antes, una dependencia justificada | La biblioteca estándar cambia por versión |
| `except*` | Solo con 3.11 y un diseño que agrupe errores | No es un sustituto de `except` |

`sys.version_info` no se comprueba en runtime para decidir sintaxis: si el fichero se parsea, la sintaxis ya se aceptó o falló.

## 2. Estructura de un módulo

- Un módulo, una responsabilidad. Si el nombre necesita «and», probablemente sean dos.
- Orden: docstring, `__all__` si la API pública lo necesita, imports, constantes, tipos, funciones, clases. Las funciones públicas antes que las privadas.
- Los imports se agrupan en estándar, terceros y locales, separados por una línea. Sin `import *` fuera de un `__init__` deliberado.
- Un import pesado o con efecto de arranque se mueve dentro de la función solo con una razón medida; si no, se paga al importar.
- Sin estado global mutable. Una constante es `Final`; una caché global se sustituye por `functools.lru_cache` o se inyecta.
- `if __name__ == "__main__":` llama a `main()` y devuelve su código con `sys.exit(main())`.

## 3. Nombres

| Elemento | Convención | Nota |
|---|---|---|
| Módulo y paquete | `snake_case`, corto | Sin guiones: no son importables |
| Función y variable | `snake_case` | Un verbo para la función, un sustantivo para el valor |
| Clase y excepción | `PascalCase`; la excepción termina en `Error` | `ValueError`, no `ValueProblem` |
| Constante | `UPPER_SNAKE_CASE` con `Final` | El tipo va en la anotación |
| Privado | Prefijo `_` | Es una convención, no una garantía |
| Booleano | `is_`, `has_`, `can_` | `activo` obliga a adivinar qué significa `True` |

Un nombre de una letra solo vale para un índice, una coordenada o un genérico documentado.

## 4. Funciones

- Guardas primero; retorno temprano. El camino feliz no va indentado.
- Parámetros: máximo cuatro posicionales; a partir de ahí, keyword-only (`*`). Un booleano posicional se prohíbe: `f(True, False)` no se lee.
- Valor por defecto inmutable en la firma; si es mutable, `None` y construcción dentro.
- No mutar parámetros salvo que el nombre lo declare (`rellenar_en_sitio`, `actualizar`). Un parámetro mutado sin decirlo es un efecto invisible.
- Una función que puede fallar documenta sus excepciones en la docstring y usa la más específica que exista.
- Los generadores se documentan como tales; si se recorren dos veces, no son generadores.
- `functools.partial` para fijar argumentos, no `lambda` que repite una llamada con menos nombres.

## 5. Datos y modelos

| Necesidad | Elección | Por qué |
|---|---|---|
| Valor con campos y sin identidad | `@dataclass(frozen=True, slots=True)` | Igualdad por valor, inmutable, sin `__dict__` |
| Valor con validación al construir | `@dataclass` con `__post_init__` y `object.__setattr__` | Falla en la frontera, no tres capas después |
| Conjunto cerrado de opciones | `enum.StrEnum` (3.11) o `Enum` | Un `Literal` para strings externos, `Enum` para lógica |
| Diccionario con forma fija | `TypedDict` | El tipo describe un JSON, no lo valida |
| Contrato que implementa el consumidor | `Protocol` | Sin herencia forzada ni clase base vacía |
| Secuencia de tamaño fijo | `tuple[T, ...]` o un `NamedTuple` | Una tupla anónima de cuatro elementos no es un tipo |
| Cantidad monetaria | `Decimal` o entero de céntimos | `float` no representa decimales |

- Un `dict` solo se usa cuando las claves son datos, no cuando son campos conocidos.
- `collections.Counter`, `defaultdict` y `deque` se prefieren a reconstruirlos con bucles.
- `frozenset` para conjuntos inmutables que se comparten.

## 6. Excepciones

- La jerarquía del paquete deriva de `Exception`; nunca de `BaseException`.
- Cada causa tiene su clase cuando el consumidor debe distinguirla. Si nunca se captura por tipo, una sola clase basta.
- Al envolver: `raise MiError("contexto") from exc`. Sin `from`, la causa se pierde o se presenta como error durante el manejo.
- `except Exception` sin `raise` exige una razón escrita; `except Exception: pass` no se acepta.
- No se usa una excepción para control de flujo normal.
- Una excepción de dominio no transporta una traza de la base de datos ni un secreto en el mensaje.
- `warnings.warn` para una deprecación, no una excepción; la advertencia se puede silenciar y la excepción no.

## 7. Recursos y contexto

- `with` para ficheros, sockets, locks, transacciones, directorios temporales y variables de entorno.
- Un `try/finally` manual solo cuando el recurso no tiene protocolo de contexto; entonces se envuelve en un `@contextmanager`.
- `contextlib.suppress` para una excepción esperada y nombrada; no para tapar un bloque.
- `ExitStack` cuando el número de recursos es dinámico.
- No dejar un fichero abierto por no cerrarlo: `Path.read_text()` y `Path.write_text()` cierran por ti.

## 8. Texto, rutas y fechas

- `pathlib.Path` para rutas; `/` para componer. `os.path` solo en código que ya lo usa.
- Codificación explícita al leer o escribir: `encoding="utf-8"`. `errors="strict"` por defecto; un reemplazo se declara.
- `datetime.now(timezone.utc)` y comparaciones entre fechas con zona. `datetime.utcnow()` devuelve una fecha sin zona y se prohíbe.
- Una fecha de negocio se guarda como fecha (`date`) si no tiene hora; una duración, como `timedelta`.
- `Decimal` con `quantize` y una política de redondeo declarada; el contexto por defecto no es una decisión de negocio.
- `re` compilado cuando el patrón se repite o es complejo; un patrón con grupos nombrados se lee mejor.

## 9. Asincronía

- `async` solo cuando hay E/S concurrente real. Un cálculo puro no gana nada por ser `async`.
- No se llama a una función bloqueante dentro del bucle de eventos: se usa `asyncio.to_thread` o el cliente asíncrono.
- `asyncio.TaskGroup` (3.11) para varios hijos con cancelación conjunta; antes, `gather` con manejo explícito de excepciones.
- Una tarea se espera o se cancela; una tarea huérfana pierde la excepción.
- `asyncio.timeout` para plazos. No se usa `wait_for` con un timeout que el propio cliente ya aplica.
- La cancelación se propaga: no se captura `CancelledError` para continuar.
- Un lock no se mantiene durante una espera de red.

## 10. Logging y salida

- `logging.getLogger(__name__)` por módulo; nada de `print` para diagnóstico.
- El programa configura el logging una vez, en el punto de entrada. Una librería no llama a `basicConfig`.
- Los mensajes usan parámetros (`logger.info("x=%s", x)`), no f-strings que se evalúan siempre.
- Los niveles significan algo: `ERROR` para una operación que falló, `WARNING` para algo corregible, `INFO` para el recorrido normal, `DEBUG` para diagnóstico.
- `stdout` es el resultado que otro programa consume; `stderr` es diagnóstico y progreso. Un `--json` no mezcla avisos en `stdout`.
