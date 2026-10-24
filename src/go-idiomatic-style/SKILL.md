---
name: go-idiomatic-style
description: "Escribe y revisa Go idiomático para CLIs y servicios pequeños: formato con gofmt, nombres, paquetes, estructura mínima, funciones, datos, interfaces y dependencias; exige la solución más simple, biblioteca estándar primero, interfaces pequeñas definidas por el consumidor, retornos concretos y flujo con errores primero. Úsala cuando haya que crear código Go nuevo, refactorizar, elegir estructura de paquetes, nombres o dependencias, o revisar estilo y diseño. No la uses para el contrato de una CLI, la estrategia de errores, contextos, concurrencia, pruebas o linting, que tienen sus propias skills."
---

# Estilo y diseño idiomático en Go

Escribe Go que otro lector pueda mantener sin reconstruir la intención. La sencillez no es una preferencia estética: es lo que permite cambiar el código sin miedo y probarlo sin ceremonia.

Esta skill posee el estilo, la estructura y las dependencias. El contrato de la CLI es de `go-cli-ai-first`; los errores, `context` y el ciclo de vida, de `go-errors-and-lifecycle`; las pruebas y la puerta, de `go-testing-and-verification`.

## Invariantes de estilo

1. Ordena las decisiones por claridad, simplicidad, concisión, mantenibilidad y consistencia. La consistencia con el proyecto gana cuando las demás están empatadas.
2. `gofmt` es la fuente de verdad del formato. No alinees a mano, no impongas longitudes de línea y no discutas lo que la herramienta ya decide.
3. Empieza con la estructura mínima. No crees `cmd/`, `internal/` ni `pkg/` por anticipación; añádelos cuando exista una necesidad concreta.
4. La biblioteca estándar es la primera opción. Una dependencia nueva exige una necesidad concreta, revisión de licencia, mantenimiento y superficie de seguridad. No envuelvas una dependencia sin una ventaja clara.
5. No introduzcas abstracciones, interfaces, genéricos, opciones funcionales ni capas «para el futuro». Si no hay dos usos reales o una frontera que probar, no existe.
6. Define las interfaces en el paquete que las consume, pequeñas y orientadas a una necesidad. Devuelve tipos concretos desde los constructores. No definas una interfaz antes de tener un uso real.
7. `main` es cableado. Toda la lógica vive en funciones que reciben sus dependencias por parámetro. `os.Exit` solo se llama en `main`.
8. No uses estado global mutable ni `init()` con efectos. Inyecta reloj, entorno, `stdin`, `stdout`, `stderr` y clientes.
9. No crees paquetes llamados `util`, `common`, `helpers` o `shared`. El nombre del paquete describe lo que aporta.
10. El flujo normal va sin anidar: comprueba errores y casos especiales primero y vuelve pronto. No escribas `else` después de un `return`.
11. Trata los datos según su semántica: asigna siempre el resultado de `append`, inicializa un map antes de escribir, distingue `nil` de vacío cuando la serialización lo distingue y no copies un tipo cuyos métodos viven en `*T`.
12. Declara cerca del uso, con `var` para el valor cero intencional y `:=` para la asignación explícita. Usa nombres de campo en structs y `any` en código nuevo.
13. No ocultes errores con `_`. Si ignoras uno deliberadamente, escribe por qué en la misma línea o justo encima.
14. `panic` solo para invariantes imposibles o fallos de inicialización que impiden arrancar. Nunca cruces una frontera de paquete con un panic.
15. Los comentarios explican el porqué, las invariantes y las decisiones no obvias. Todo lo exportado que forme API pública lleva comentario de documentación.
16. Respeta la convención del proyecto cuando exista. Si el código que rodea usa otra estructura o nombres, no lo reformatees para imponer esta skill.
17. La concurrencia no se introduce aquí. Si hace falta, se diseña con la skill de errores y ciclo de vida, que exige propietario, terminación y espera.

## Procedimiento de estilo

**Paso 1 — Inspeccionar antes de escribir.**
1. Lee `go.mod`, la estructura de paquetes, los tests y el estilo del código vecino.
2. Identifica la convención existente para nombres, errores, configuración y organización. Si hay una regla escrita, prevalece.
3. Localiza el punto de entrada y comprueba si ya existe un patrón `run()` o equivalente.

**Paso 2 — Fijar el mapa de paquetes.**
1. Escribe una frase por paquete con su responsabilidad. Si una frase necesita dos responsabilidades, el paquete está mal dividido.
2. Mantén el dominio separado del parseo de flags y de la presentación. Una CLI pequeña puede vivir en un solo paquete; cuando el binario y la lógica dejen de caber con claridad, separa `cmd/<binario>` e `internal/<dominio>`. No añadas más capas.
3. Comprueba que no hay ciclos ni paquetes comodín. Si aparece un `util`, asígnalo a un paquete con nombre de dominio.

**Paso 3 — Nombrar.**
1. Paquetes: minúsculas, sin guiones bajos, normalmente una palabra, sin repetir el nombre del símbolo que contienen.
2. Exportados en PascalCase, no exportados en camelCase; acrónimos con su caso: `ID`, `URL`, `HTTP`.
3. Receptores de una o dos letras, coherentes en todos los métodos del tipo; nunca `this` o `self`.
4. Constantes en MixedCaps, nunca `ALL_CAPS`. Nombra por función, no por valor.
5. La longitud del nombre crece con el ámbito. `i` en un bucle, `pendingOrders` en una función larga.
6. No repitas el contexto: `widget.New()`, no `widget.NewWidget()`.

**Paso 4 — Diseñar funciones, datos e interfaces.**
1. Una función, una responsabilidad comprensible. Si necesita un comentario para explicar qué hace, probablemente hace demasiado.
2. Prefiere firmas simples; si un booleano posicional no se entiende, usa un tipo con nombre o un comentario `/* name */`.
3. Define la interfaz en el consumidor y solo con los métodos que usa. Si el productor necesita devolver algo, devuelve el tipo concreto.
4. Elige puntero o valor por semántica: mutación, ausencia con `nil`, tamaño o identidad. No lo justifiques por «stack» o «heap».
5. Inicializa structs con nombres de campo; omite los ceros. Usa `&T{}` en lugar de `new(T)`.
6. Usa `errors.Is` y `errors.As` para errores; el diseño de errores pertenece a la skill de errores y ciclo de vida.

**Paso 5 — Implementar.**
1. Escribe primero el camino normal y los guard clauses; deja el caso feliz sin indentación.
2. Mantén las funciones cortas por responsabilidad, no por un número arbitrario de líneas.
3. Si necesitas `init()`, demuestra que es determinista, sin I/O, sin entorno y sin orden entre paquetes. Si no, usa una función explícita.
4. Si añades una dependencia, escribe en el diff por qué la biblioteca estándar no basta.

**Paso 6 — Formatear y compilar.**
1. Ejecuta `go fmt ./...` y `go vet ./...`.
2. Ejecuta `go build ./...`; un cambio de estilo que rompe la compilación no es un cambio de estilo.
3. Si el proyecto tiene `golangci-lint` configurado, ejecútalo. No lo añadas solo para cumplir esta skill.

**Paso 7 — Revisar el diff.**
1. Comprueba que no has introducido abstracciones, opciones, paquetes o dependencias que nadie pidió.
2. Comprueba que no has reformateado código ajeno ni mezclado una refactorización con un cambio de comportamiento.
3. Cierra con el bloque de resultado.

## Errores y paradas de estilo

- Si el proyecto ya tiene una estructura distinta, no la migres dentro de un cambio funcional. Propón la migración aparte.
- Si una abstracción existente es incorrecta pero sustituirla amplía el cambio, termina la tarea actual y registra la deuda; no la escondas en el mismo diff.
- Si `gofmt` y la convención del proyecto discrepan, gana `gofmt`. La convención no puede contradecir el lenguaje.
- Si una dependencia parece necesaria pero no se puede revisar su licencia o mantenimiento, no la añadas: declara el bloqueo.
- Si el código necesita concurrencia para cumplir el requisito, no la improvises aquí; pasa a la skill de errores y ciclo de vida.
- Si el usuario pide una abstracción genérica sin casos de uso, entrega la versión concreta y explica en una línea qué la haría merecer la abstracción.

## Resultado de estilo

```text
Estado: completado | parcial | bloqueado
Paquetes tocados: <lista con su responsabilidad>
Decisiones de diseño: <interfaces, dependencias, estructura>
Comprobaciones: <gofmt, go build, go vet, lint si existe>
Deuda declarada: <lista, o "ninguna">
No verificado: <lista, o "ninguno">
```

## Referencias de estilo

- [style-rules](references/style-rules.md) — tablas de decisión para formato, nombres, paquetes, estructura, funciones, datos, interfaces y dependencias. Léela en los pasos 2 a 4 cuando una regla no sea evidente.
