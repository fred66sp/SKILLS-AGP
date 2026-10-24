# Contrato de errores

## 1. Clasificación

| Clase | Quién actúa | Tratamiento | Código de salida |
|---|---|---|---|
| Uso incorrecto | El llamador corrige la invocación | Error de validación con la flag o el argumento exacto | `2` |
| Operación fallida | El llamador reintenta, informa o aborta | Error envuelto con contexto de la operación | `1` |
| Conflicto de estado | El llamador decide sobrescribir o cambiar el plan | Error tipado con el estado observado y el esperado | `4` |
| Cancelación | El llamador decidió parar | `context.Canceled` o error de cancelación | `3` |
| Defecto de programación | Nadie en producción | `panic` en el punto imposible o error interno | `1` |

- No uses la misma clase para un fallo de red y una flag mal escrita. El agente necesita distinguir «me equivoqué al llamar» de «la operación falló».
- Una condición que el llamador debe poder comprobar es parte del contrato público y se documenta.

## 2. Estrategia

| ¿El llamador necesita identificar la condición? | ¿El mensaje es fijo? | Herramienta |
|---|---|---|
| No | Sí | `errors.New("mensaje")` |
| No | No | `fmt.Errorf("mensaje: %v", valor)` |
| Sí | Sí | Centinela: `var ErrFoo = errors.New("foo")` |
| Sí | No | Tipo propio que implementa `error` |

- Por defecto, envuelve con `%w` y coloca el verbo al final: `fmt.Errorf("read config %q: %w", path, err)`.
- Un centinela se nombra `ErrXxx`; un tipo de error, `XxxError`.
- Un tipo de error implementa `Error() string` y, si envuelve, `Unwrap() error`. Si agrupa varios, `Unwrap() []error` o `errors.Join`.
- No devuelvas un tipo concreto desde una función exportada. Devuelve `error`.

## 3. Envoltura

- Añade contexto que el llamador no tenga: operación, recurso, identificador, número de intento.
- No repitas el contexto de la capa inferior: `read config: open /x: no such file` es aceptable; `read config: error reading config: open /x: ...` no.
- Usa `%q` para valores de texto que puedan contener espacios, saltos de línea o caracteres de control.
- Usa `%w` cuando la causa deba seguir siendo inspeccionable. Usa `%v` solo en una frontera donde no quieras exponer el interior.
- No uses `%w` con varios errores en el mismo `fmt.Errorf`; usa `errors.Join` si necesitas agrupar.
- No incluyas secretos, tokens, cabeceras de autorización, cadenas de conexión ni rutas internas en el mensaje que cruza la frontera.

## 4. Inspección

```go
if errors.Is(err, ErrNotFound) {
    // condición estable
}

var conflict *ConflictError
if errors.As(err, &conflict) {
    // datos estructurados
}
```

- `errors.Is` recorre la cadena de `Unwrap`. No compares `err == ErrX`, porque una capa intermedia puede haber envuelto el error.
- `errors.As` recibe un puntero al tipo destino: `var target *ConflictError; errors.As(err, &target)`.
- No compares `err.Error()` con una cadena, ni siquiera en tests. Si el texto importa, es una decisión de presentación, no de lógica.
- Un error de cancelación se comprueba con `errors.Is(err, context.Canceled)` o `errors.Is(err, context.DeadlineExceeded)`.

## 5. Frontera de la CLI

El mapeo ocurre en un único punto, cerca de `main`:

```go
type exitError struct {
    code    string
    message string
    details map[string]any
    status  int
}

func (e *exitError) Error() string { return e.message }
func (e *exitError) Unwrap() error { return e.cause }
```

| Condición | `code` | `status` |
|---|---|---|
| Flag o argumento inválido | `invalid_argument` | `2` |
| Entrada malformada | `invalid_input` | `2` |
| Recurso no encontrado | `not_found` | `1` |
| Conflicto sin `--force` | `conflict` | `4` |
| Falta `--yes` | `confirmation_required` | `4` |
| Timeout | `timeout` | `1` |
| Cancelación | `cancelled` | `3` |
| Fallo interno | `internal` | `1` |

- El `code` es estable y en `snake_case`. El mensaje puede cambiar; el código no.
- En modo JSON, el error se escribe en `stdout` con el sobre del contrato de la CLI. En modo texto, una línea accionable en `stderr`.
- Los detalles completos solo con `--debug`, siempre redactados. Una traza nunca sustituye a un mensaje accionable.
- Un fallo parcial por lotes devuelve `1` y detalla los elementos fallidos en `details`; no devuelve `0` con un aviso.

## 6. Patrones

- **Handle once.** Si devuelves el error, no lo registres además en la misma capa. El registro pertenece a la frontera.
- **Guard clauses.** Comprueba el error inmediatamente y vuelve; deja el camino feliz sin indentar.
- **No log-and-return.** Duplica el mensaje, ensucia la salida y confunde al consumidor.
- **No errores en banda.** `-1`, `""`, `0` o `nil` como señal de fallo se sustituyen por `(T, error)` o `(T, bool)`.
- **No panics de biblioteca.** Un panic cruza la frontera y mata al consumidor. Convierte en error salvo un invariante imposible.
- **Recover con límite.** Si recuperas, hazlo en un límite conocido, convierte a error y no continues como si nada.
- **Errores de cierre.** Al cerrar varios recursos, conserva el primer error y no ocultes los siguientes; `errors.Join` es útil.

## 7. Lista rápida de errores

- [ ] Cada error tiene una clase y un tratamiento decidido.
- [ ] Los errores esperados son centinelas o tipos documentados.
- [ ] Las funciones exportadas devuelven `error`.
- [ ] La envoltura añade contexto y conserva la causa con `%w`.
- [ ] La inspección usa `errors.Is`/`errors.As`.
- [ ] El mapeo a código de salida y JSON vive en un solo punto.
- [ ] No hay secretos ni rutas internas en el mensaje público.
- [ ] Ningún error se descarta sin justificación escrita.
- [ ] La cancelación y el timeout se distinguen.
- [ ] Los tests comprueban semántica, no textos.
