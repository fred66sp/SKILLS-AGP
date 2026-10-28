# Reglas de tipos

Léela en el paso 3, cuando una anotación, una unión o una supresión no sea evidente. El comprobador manda: estas tablas explican qué escribir para que lo acepte sin `# type: ignore` nuevo.

## 1. Configuración de partida

Un `pyproject.toml` con mypy:

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_unreachable = true
```

Con pyright, `typeCheckingMode = "strict"` en `pyrightconfig.json` o en `[tool.pyright]`. Un proyecto que no tenga ninguna de las dos configuraciones no se migra dentro de un cambio funcional.

## 2. Anotaciones

| Decisión | Regla |
|---|---|
| API pública | Parámetros y retorno anotados siempre |
| Función local | Se infiere; se anota si la inferencia no es obvia o el retorno es una unión |
| Variable local | Se infiere; se anota cuando el valor inicial no representa el tipo final (`total: int = 0`) |
| Constante de módulo | `Final[T]` o `Final` con valor literal |
| Atributo de instancia | Se anota en la clase o en `__init__`, no en ambos |
| `__init__` | Retorno `None` |
| `*args` / `**kwargs` | `*args: int`, `**kwargs: str`; si la forma es fija, un `TypedDict` con `Unpack` |
| Callable | `Callable[[int, str], bool]`; para keyword, un `Protocol` con `__call__` |

`list[int]` y `dict[str, int]` (builtins genéricos) requieren 3.9; `X | None` requiere 3.10. `Optional[X]` solo se usa si el proyecto es anterior.

## 3. `Any`, `object` y `Unknown`

| Situación | Qué se escribe | Motivo |
|---|---|---|
| Dato externo sin validar | `object` y estrechar | `Any` apaga el comprobador y se propaga |
| JSON ya parseado | `dict[str, object]` o `TypedDict` | La forma se documenta; el valor se valida en runtime |
| Biblioteca sin tipos | Un adaptador con `Any` interno y una firma tipada hacia fuera | El `Any` no cruza el módulo |
| Supresión | `# type: ignore[código]  # razón` | Sin código y sin razón no se acepta |
| Conversión comprobada | `cast(T, x)` tras una comprobación real | `cast` no comprueba nada |

## 4. Uniones y estados

- Una unión de dos estados se documenta con un campo literal cuando la forma lo permite: `Literal["ok"]` y `Literal["error"]`. Un `tuple[bool, str | None]` es el mismo estado sin nombres.
- La comprobación exhaustiva se hace con `assert_never` de `typing` en la rama final; añadir una variante rompe la comprobación.
- `isinstance` estrecha uniones de clases; para uniones de diccionarios, un `TypeGuard` o una validación en runtime.
- El estrechamiento no cruza una llamada a función: si el comprobador no puede demostrar la invariante, se comprueba con un guard y se documenta.

## 5. Estructuras

| Necesidad | Tipo |
|---|---|
| Registro con campos | `@dataclass(frozen=True, slots=True)` |
| Diccionario externo | `TypedDict` con `total=False` solo si todas las claves son opcionales |
| Contrato del consumidor | `Protocol` con los métodos mínimos |
| Variante cerrada | `Enum` o `Literal` |
| Genérico con dos usos reales | `TypeVar` o PEP 695 (`class Pila[T]`) si el mínimo es 3.12 |
| Genérico con límite | `TypeVar("T", bound=Base)`; `constrained` solo con dos o más tipos concretos |
| Retorno que depende de la entrada | `overload` en el `.pyi` o en el módulo, con una implementación que acepte la unión |

Un `Protocol` no se hereda para reutilizar código; para eso está una clase base. Un `dataclass` no se usa como formulario de validación: no comprueba tipos en runtime.

## 6. Funciones especiales

- `TypeGuard[T]` cuando el guard solo estrecha en la rama verdadera; `TypeIs[T]` (3.13) cuando estrecha en ambas.
- `Self` para un método que devuelve el tipo del llamante; en versiones anteriores, un `TypeVar` con `bound`.
- `Never` para una función que no retorna; `NoReturn` es su alias histórico.
- `@final` en un método que no debe sobrescribirse y en una clase cerrada.
- `@override` (3.12) o `typing_extensions.override` antes, para que renombrar el método base rompa la compilación.

## 7. Cuándo no anotar

- Un `lambda` no se anota; si la firma importa, se escribe una función.
- Un decorador que devuelve el mismo callable conserva el tipo con `ParamSpec`; sin él, la firma se pierde.
- Un `dict` de configuración interno no necesita un `TypedDict` si nunca cruza una frontera.
- Un test no necesita anotaciones salvo que las exija la configuración.

## 8. Errores frecuentes del comprobador

| Mensaje | Causa real | Corrección |
|---|---|---|
| `Item "None" of ... has no attribute` | El valor puede ser `None` y no se comprobó | Guarda antes de usar, o modela el estado |
| `Incompatible default for argument` | Valor por defecto de otro tipo | Cambia el defecto, no el tipo |
| `Missing return statement` | Rama sin retorno | Añade el retorno o `raise` |
| `Need type annotation` | Contenedor vacío | Anota la variable |
| `Cannot determine type of ...` | Atributo asignado solo en una rama | Inicialízalo en `__init__` |
| `Argument has incompatible type` | Unión sin estrechar | Estrecha con `isinstance` o un guard |

Un error del comprobador no se silencia para cerrar el cambio: se corrige el tipo o se declara el bloqueo.
