---
name: go-errors-and-lifecycle
description: "Diseña el contrato de errores y el ciclo de vida de un programa Go: clasifica errores, los envuelve con contexto, los inspecciona con errors.Is y errors.As, los traduce a códigos de salida y mensajes machine-readable, y propaga context, cancelación, timeouts, señales y cierre ordenado; exige que toda goroutine tenga propietario, terminación, propagación y espera. Úsala cuando haya que definir o revisar errores, mapearlos a códigos de salida, añadir context o cancelación, manejar señales, introducir concurrencia o cerrar un proceso con limpieza. No la uses para el contrato de la CLI, estilo general ni pruebas, que tienen sus propias skills."
---

# Errores y ciclo de vida en Go

Un error no es un texto: es un valor con significado, un contrato entre capas y una decisión sobre qué puede hacer el llamador. Un proceso no termina cuando `main` retorna: termina cuando sus goroutines, conexiones y archivos han cerrado en el orden correcto.

## Invariantes de errores y ciclo de vida

1. Clasifica antes de escribir: error esperado de operación, error de uso, conflicto de estado, cancelación o defecto de programación. Cada clase tiene un tratamiento distinto.
2. Un error se maneja una sola vez: se devuelve con contexto o se registra en la frontera, nunca ambas cosas.
3. Envuelve con `%w` cuando el llamador pueda necesitar inspeccionar la causa. Usa `%v` solo en una frontera de confianza donde no debas exponer el interior. `%w` va al final del formato.
4. El mensaje describe la operación que falló, no la emoción ni la consecuencia: `read config %q`, no `failed to load configuration`. Minúscula inicial y sin punto final salvo nombres propios o acrónimos.
5. Inspecciona con `errors.Is` y `errors.As`. Comparar textos de error es un defecto, incluso en tests.
6. Las funciones exportadas devuelven `error`, nunca un tipo concreto de error. Un `nil` de tipo concreto dentro de una interfaz deja de ser `nil`.
7. No uses errores en banda: nada de `-1`, `""` o `nil` como señal. Devuelve `(T, bool)` o `(T, error)`.
8. `panic` solo para invariantes imposibles o inicialización que no puede continuar. No cruces una frontera de paquete con un panic; si recuperas, hazlo en un límite conocido y conviértelo en error.
9. El mapeo de error a código de salida y a sobre JSON vive en un solo punto, cerca de `main`. El dominio no conoce códigos de proceso.
10. `context.Context` es el primer parámetro de toda función que hace I/O, espera o trabajo cancelable. No se guarda en un struct, no se usa para parámetros opcionales y no se sustituye por un tipo propio.
11. Deriva contextos con timeout o deadline en la frontera que corresponda y llama `defer cancel()` inmediatamente.
12. Toda goroutine tiene propietario, condición de terminación, forma de propagar error o resultado, política de cancelación y forma de esperarla. Si no puedes explicar cómo termina, no la crees.
13. Prefiere funciones síncronas; que el llamador añada concurrencia. Usa `errgroup` para tareas relacionadas con cancelación y errores, `WaitGroup` solo para esperar, canales para transferir propiedad y mutex para proteger estado compartido.
14. Nada de goroutines en `init()`. No dejes timers, tickers, conexiones ni goroutines activas después de que su propietario termine.
15. Las operaciones externas terminan por éxito, error, cancelación, timeout o cierre del propietario. Si falta una de esas salidas, el diseño está incompleto.
16. `main` instala la señal con `signal.NotifyContext`, propaga el contexto y ejecuta un cierre ordenado: dejar de aceptar trabajo, cancelar, esperar con límite, cerrar recursos y salir.

## Procedimiento de errores y ciclo de vida

**Paso 1 — Inventariar fallos y fronteras.**
1. Enumera las operaciones que pueden fallar y quién puede actuar sobre cada fallo: usuario, agente, reintento, operador o nadie.
2. Identifica las fronteras: dominio, CLI, red, disco, proceso. En cada frontera decide qué se envuelve, qué se registra y qué se oculta.
3. Lee `references/error-contract.md` antes de definir la taxonomía.

**Paso 2 — Definir la taxonomía.**
1. Usa errores centinela (`var ErrX = errors.New(...)`) para condiciones estables que el llamador compara con `errors.Is`.
2. Usa un tipo de error para datos estructurados que el llamador inspecciona con `errors.As`.
3. Usa errores opacos para fallos que solo necesitan contexto de depuración.
4. Asigna un `code` estable a cada condición que cruce la frontera de la CLI y mapéalo a `1`, `2`, `3` o `4` según el contrato de la CLI.

**Paso 3 — Implementar el flujo.**
1. Comprueba cada error inmediatamente. No lo asignes a `_` sin una razón escrita.
2. Añade contexto que el llamador no tenga: operación, recurso, identificador. No repitas el mensaje de la capa inferior.
3. Si la anotación no aporta nada, devuelve `err` tal cual.
4. Mantén el error original accesible con `%w`; no lo reconstruyas con `fmt.Errorf("%s", err)`.

**Paso 4 — Traducir en la frontera.**
1. Mapea el error a un `code`, un mensaje accionable y un código de salida en un único punto.
2. No incluyas rutas internas, tokens, cabeceras ni trazas en el mensaje público. Los detalles completos van a `--debug` y a `stderr`, redactados.
3. En modo JSON, produce el sobre de error del contrato de la CLI. En modo texto, escribe una línea accionable en `stderr`.
4. Un fallo parcial por lotes devuelve `1` y detalla qué elementos fallaron; no lo conviertas en éxito.

**Paso 5 — Propagar context y cancelación.**
1. Pasa `ctx` a todas las operaciones de I/O y espera.
2. Deriva timeouts en la frontera responsable; no pongas el mismo timeout en todas las capas.
3. Comprueba `ctx.Err()` al recibir una cancelación y devuélvela envuelta o tal cual según la frontera.
4. Distingue cancelación del usuario de timeout: no son el mismo `code` ni el mismo mensaje.

**Paso 6 — Justificar la concurrencia.**
1. Si no hay trabajo independiente, espera solapable o necesidad de capacidad, no introduzcas goroutines.
2. Para cada goroutine, escribe en el diseño: quién la posee, cómo termina, cómo reporta y cómo se espera.
3. Usa `errgroup.WithContext` cuando varias tareas relacionadas deban cancelarse entre sí. Usa `sync.WaitGroup` solo si no hay errores que propagar.
4. Canales sin buffer o de tamaño uno salvo justificación. No cierres un canal desde el receptor ni uno que otro productor pueda usar.

**Paso 7 — Cerrar el proceso.**
1. Instala `signal.NotifyContext(ctx, os.Interrupt, syscall.SIGTERM)` en `main` y llama `stop` al salir.
2. Ante la primera señal, deja de aceptar trabajo, cancela el contexto y espera a las tareas en curso con un deadline.
3. Cierra recursos en orden inverso a su apertura y propaga el primer error de cierre.
4. Sal con `3` si la cancelación fue por señal; con `1` si el cierre falló por otra causa.
5. Un segundo SIGINT puede forzar la salida; si existe, documéntalo.

**Paso 8 — Verificar y cerrar.**
1. Prueba los caminos de error con `errors.Is`/`errors.As`, no con textos.
2. Prueba la cancelación: el contexto se cancela, la operación retorna pronto y no quedan goroutines.
3. Ejecuta `go test ./...`, `go vet ./...` y `go test -race ./...` si hay concurrencia.
4. Rellena el bloque de resultado.

## Errores y paradas del ciclo de vida

- Si un error no se puede mapear a una decisión del llamador, no inventes un `code`: probablemente es un error interno y debe salir como `1` con mensaje genérico.
- Si la cancelación deja estado parcial y la operación no es atómica, declara cómo se reanuda o cómo se limpia. No prometas atomicidad.
- Si una goroutine no puede terminar por diseño, no la lances; usa una operación síncrona o un límite explícito.
- Si el proyecto ya tiene un envelope de errores, respétalo y mapea a él; no impongas el de esta skill sobre un contrato publicado.
- Si el cierre ordenado no cabe en el plazo, no bloquees indefinidamente: cancela, registra qué no se pudo cerrar y sal con el código que corresponda.
- Si detectas un panic recuperado que oculta un defecto de programación, no lo conviertas en error de operación: corrígelo o decláralo.

## Resultado del ciclo de vida

```text
Estado: completado | parcial | bloqueado
Taxonomía: <centinelas, tipos y códigos>
Frontera CLI: <dónde se mapea y qué envelope usa>
Contexto: <timeouts y puntos de cancelación>
Concurrencia: <propietarios, terminación y espera, o "no aplica">
Cierre: <orden y límite>
Comprobaciones: <go test, go vet, go test -race>
No verificado: <lista, o "ninguno">
```

## Referencias de errores y ciclo de vida

- [error-contract](references/error-contract.md) — taxonomía, envoltura, inspección, mensajes, mapeo a códigos y ejemplos. Léela en los pasos 1 a 4.
- [lifecycle](references/lifecycle.md) — context, goroutines, errgroup, canales, mutex, señales y cierre ordenado. Léela en los pasos 5 a 7.
