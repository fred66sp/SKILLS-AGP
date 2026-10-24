---
name: go-cli-ai-first
description: "Diseña, implementa y revisa CLIs en Go pensadas para agentes de IA y para personas: fija un contrato estable de comandos, flags, stdin/stdout/stderr, salida JSON, códigos de salida y errores machine-readable; exige modo no interactivo, `--dry-run`, confirmación explícita para operaciones destructivas, idempotencia, cancelación por señal y salida acotada. Úsala cuando haya que crear una CLI, añadir o cambiar comandos, flags o formato de salida, o auditar si una CLI existente es segura y automatizable. No la uses para diseño de producto, interfaces gráficas, APIs HTTP, arquitectura de microservicios, ni para reglas generales de estilo, errores o pruebas de Go, que tienen sus propias skills."
---

# CLI Go para agentes

El consumidor principal de estas CLIs es un agente que ejecuta comandos, lee stdout y decide el siguiente paso. La interfaz humana importa, pero el contrato máquina manda: si el agente no puede descubrir, ejecutar y verificar una operación sin adivinar, la CLI no está terminada.

Esta skill posee el contrato de la CLI: comandos, flags, flujos, JSON, códigos de salida y seguridad. La estructura y el estilo del código son de `go-idiomatic-style`; los errores, `context`, la concurrencia y el cierre, de `go-errors-and-lifecycle`; las pruebas y la puerta, de `go-testing-and-verification`.

## Invariantes de la CLI para agentes

1. No implementes un comando sin un contrato escrito: nombre, propósito, argumentos, flags, entrada, salida, efectos, idempotencia, seguridad y códigos de salida. Copia `assets/command-spec.md` y rellénalo antes de tocar código.
2. `stdout` transporta solo el resultado. `stderr` transporta diagnóstico, progreso y errores. No mezcles ambos en el mismo flujo.
3. El modo por defecto es no interactivo. No leas de terminal ni esperes confirmación si `stdin` no es un TTY. Una pregunta solo se permite con `--interactive` y un TTY real; en cualquier otro caso, falla con error de uso.
4. Los códigos de salida son parte del contrato y no cambian: `0` éxito, `1` fallo de ejecución, `2` error de uso, `3` cancelado, `4` precondición o conflicto. No inventes códigos por comando.
5. `--json` produce exactamente un documento JSON en `stdout`. En éxito usa `{"ok":true,"command":"...","data":...}`; en fallo usa `{"ok":false,"error":{"code":"...","message":"...","details":...}}`. Los comandos que emiten flujo continuo usan JSON Lines y lo declaran.
6. Los errores son datos: código estable, mensaje accionable y detalles sin secretos. El mismo fallo produce el mismo `code` y el mismo código de salida en texto y en JSON.
7. Lo destructivo es explícito. Todo comando que borra, sobrescribe o publica admite `--dry-run`, muestra el plan antes de actuar y exige `--yes` para ejecutarlo. Un prompt interactivo no sustituye a `--yes`.
8. Los comandos son idempotentes siempre que el dominio lo permita. Repetir la misma operación sobre el mismo estado devuelve éxito con `changed:false`; un conflicto sin `--force` devuelve `4`.
9. La cancelación se propaga. `main` crea un contexto con `signal.NotifyContext`, lo pasa a todas las capas y sale con `3` cuando el usuario interrumpe.
10. La salida está acotada. Los listados aceptan `--limit`; los flujos infinitos exigen `--follow`; ninguna operación imprime indefinidamente sin control del llamador.
11. La ayuda es el mecanismo de descubrimiento. `--help` de la raíz y de cada comando sale con `0` y muestra uso, flags, variables de entorno, ejemplos y códigos de salida. Un comando o flag desconocido sale con `2`.
12. `--version` existe en la raíz y sale con `0`; en modo JSON devuelve versión, commit y versión de Go.
13. No hay color, spinner ni animación cuando `stdout` no es un TTY o cuando `NO_COLOR` está definido. El progreso, si existe, va a `stderr`.
14. Ningún secreto aparece en argumentos, logs, errores ni JSON. Los tokens se leen de entorno, archivo o `stdin`, nunca de un flag visible en el historial.
15. `os.Exit` solo se llama en `main`. Toda la lógica vive en una función `run(ctx, args, stdin, stdout, stderr) int` que se puede probar sin lanzar el proceso.
16. Un cambio de contrato es un cambio incompatible: renombrar o eliminar un comando, flag, campo JSON o código de salida exige versión mayor y una nota de migración. Añadir es compatible; cambiar en silencio, no.

## Procedimiento de la CLI

**Paso 1 — Delimitar la CLI y sus consumidores.**
1. Identifica el binario, el dominio, los consumidores reales (agente, script, persona) y las operaciones que deben existir.
2. Lee `references/cli-contract.md` antes de decidir nombres, flags, salida o códigos.
3. Revisa `go.mod`, la estructura existente y cualquier convención del proyecto. Si ya hay una CLI, inventaría sus comandos y marca qué parte del contrato está implícita.

**Paso 2 — Escribir el contrato.**
1. Copia `assets/command-spec.md` a un documento de trabajo y rellena una ficha por comando.
2. Define para cada comando: entrada, salida de éxito, error posible, efecto sobre el estado, idempotencia, modo `--dry-run` y requisito de `--yes`.
3. Fija el esquema JSON de éxito y de error. Si hay varios comandos, comparte el sobre y especializa solo `data`.
4. Identifica los cambios incompatibles y decide versión y migración antes de implementar.

**Paso 3 — Elegir la estructura.**
1. Empieza por la estructura mínima que mantenga `main` como cableado y la lógica en una función `run` testeable. Cuántos paquetes hacen falta lo decide `go-idiomatic-style`.
2. Cuando la CLI tenga varios comandos o el paquete único deje de ser legible, separa `cmd/<binario>/main.go` (cableado), `internal/cli` (parseo, ayuda, formato y mapeo de errores) e `internal/app` (casos de uso). No crees esas capas antes de que exista la necesidad.
3. Inyecta `stdin`, `stdout`, `stderr`, reloj y entorno como dependencias. No uses `os.Stdout` ni `time.Now` dentro de la lógica de negocio.

**Paso 4 — Implementar la superficie.**
1. Implementa la ayuda raíz y la de cada comando antes que la lógica. Un comando sin ayuda no está listo.
2. Usa `flag.NewFlagSet` con `flag.ContinueOnError` y una salida propia; no dejes que la biblioteca escriba la ayuda ni llame a `os.Exit`.
3. Acepta `--flag` y `-flag`; documenta la forma canónica. Los nombres de flag usan kebab-case.
4. Implementa un renderizador de texto y otro JSON sobre el mismo resultado tipado. No construyas el JSON a mano en cada comando.
5. Implementa el sobre de error y el mapeo a código de salida en un único punto.

**Paso 5 — Añadir seguridad e idempotencia.**
1. Implementa `--dry-run`: calcula el plan, muéstralo por `stdout` y no muta nada.
2. Implementa la confirmación: sin `--yes`, una operación destructiva muestra el plan y sale con `4`; con `--yes`, ejecuta.
3. Escribe archivos con temporal en el mismo directorio, `fsync` y `rename` atómico. Nunca dejes un archivo a medias.
4. Devuelve `changed` en el resultado. Si el estado ya es el deseado, no reescribas y no falles.
5. Limita listados y flujos; rechaza `--limit` negativo o cero cuando no tenga sentido.

**Paso 6 — Resolver el ciclo de vida.**
Aplica `go-errors-and-lifecycle`. En la CLI:

1. `main` crea el contexto con `signal.NotifyContext`, lo propaga a las operaciones y sale con `3` al cancelar.
2. Trata `EPIPE` como una salida normal: si el consumidor cierra la tubería, termina con `0` sin ruido.

**Paso 7 — Probar el contrato, no solo la lógica.**
Aplica las capas de `go-testing-and-verification`. En la CLI cubre además:

1. La superficie con pruebas de extremo a extremo que ejecutan el binario y comprueban por separado `stdout`, `stderr` y código de salida.
2. Ayuda, versión, comando desconocido, flag desconocido, JSON válido, `--dry-run`, falta de `--yes`, cancelación y `EPIPE`.
3. Golden files para la salida estable, normalizando rutas, tiempos y mensajes del sistema.

**Paso 8 — Cerrar con evidencia.**
1. Ejecuta la puerta de `go-testing-and-verification` y adjunta su resultado.
2. Rellena el bloque de resultado. Ningún comando del contrato queda sin verificar o declarado como no disponible.

## Errores y paradas de la CLI

- Si el consumidor necesita una operación que no se puede expresar sin estado interactivo, rediseña el comando como `plan` + `apply`; no añadas un prompt como única vía.
- Si un comando destructivo no puede mostrar su plan antes de ejecutar, no lo implementes: falta una fase de previsualización.
- Si el proyecto usa una biblioteca de CLI con convenciones propias, respeta sus nombres y códigos, pero conserva las invariantes de flujo, seguridad y JSON.
- Si el esquema JSON ya existe y no se puede cambiar, adáptate a él y documenta las diferencias; no impongas el sobre de esta skill sobre un contrato publicado.
- Si no hay TTY y el comando necesita una decisión, devuelve `2` con la flag exacta que falta. No leas `stdin` a ciegas.
- Si la cancelación deja trabajo parcial, declara si la operación es atómica o reanudable. No prometas atomicidad que el código no garantiza.

## Resultado de la CLI

Cierra siempre con este bloque:

```text
Estado: completado | parcial | bloqueado
Contrato: <ruta del command spec>
Comandos: <lista de comandos cubiertos>
Comprobaciones: <gofmt, build, test, vet, race, smoke de ayuda/versión/JSON/exit codes>
Cambios de contrato: <ninguno | lista con versión y migración>
No verificado: <lista, o "ninguno">
```

## Referencias de la CLI

- [cli-contract](references/cli-contract.md) — gramática de comandos, flags, flujos, códigos de salida, sobre JSON, ayuda, seguridad y compatibilidad. Léela en el paso 1 y consúltala en los pasos 2, 4 y 5.
- [command-spec](assets/command-spec.md) — ficha por comando. Cópiala en el paso 2.
