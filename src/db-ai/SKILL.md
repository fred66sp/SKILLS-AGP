---
name: db-ai
description: "Explora, consulta y modifica bases de datos SQLite con la CLI db-ai, que expone tablas, filas y campos como un sistema de archivos y evita generar SQL. Úsala cuando un agente necesite descubrir qué bases hay montadas, inspeccionar tablas y columnas, leer o buscar filas, exportar resultados o escribir con permisos, ETags, dry-run y transacciones. Cubre el descubrimiento progresivo con mounts, ls, tree, stat y describe; la lectura con cat, find, grep y export; y la escritura con touch, write, cp, mv, rm y batch, incluidos cursores, sesiones y códigos de error. No la uses para desarrollar, modificar o depurar la herramienta db-ai, ni para escribir SQL directo, ORMs, migraciones de esquema o administración de motores; tampoco para PostgreSQL u otros motores fuera del MVP. Prefiere la CLI propia del dominio cuando exista y aplique reglas de negocio."
metadata:
  version: "0.1.0"
---

# Operación de bases de datos con db-ai

`db-ai` presenta una base SQLite como un sistema de archivos: monta un fichero en un alias y navega tablas, filas y campos con rutas. El agente consume esa semántica; nunca genera SQL. Esta skill enseña a operar la CLI con autonomía, seguridad y el mínimo contexto posible.

## Alcance y límites

- Posee la conducción de `db-ai`: descubrir, leer, buscar, escribir en una fila y ejecutar lotes transaccionales.
- No posee el desarrollo de la herramienta. Para cambiar `db-ai` se trabaja en su repositorio y con sus propias reglas, no con esta skill.
- No posee SQL, ORMs, migraciones de esquema ni administración del motor. `db-ai` no acepta SQL libre y esta skill no lo inventa.
- No posee las reglas de negocio. Si el dominio ya ofrece una CLI con validaciones propias, se prefiere esa CLI; `db-ai` es el acceso genérico por semántica de filesystem.

## Modelo mental

1. Una ruta absoluta tiene la forma `/alias/tabla/clave/campo`. Los segmentos de identidad se escapan; una clave textual `a/b` viaja como `a%2Fb`. Los detalles de identidad están en [comandos](references/comandos.md).
2. Toda invocación devuelve **un único objeto JSON versionado** en stdout —`export --format jsonl` es la excepción: emite una fila por línea—: `{"version":1,"ok":true,"data":...,"meta":{...}}` o `{"version":1,"ok":false,"error":{"code":"E_...","message":"..."}}`. `--json` se acepta pero no cambia nada.
3. `error.code` es la fuente de verdad del fallo; el código de salida solo lo agrupa.
4. Sin `--session`, las rutas relativas se rechazan. Las sesiones solo sirven para `cd` y `pwd`; el resto de comandos es stateless.
5. `mount` y `umount` los ejecuta el operador por convención. Un agente no los usa para abrirse acceso.

## Regla de oro

Descubre antes de leer, lee antes de escribir y verifica después de escribir. Detente en cuanto la pregunta esté respondida: cada comando y cada fila consumen contexto.

## Procedimiento

### Fase 1: Descubrir con el mínimo de pasos

1. Ejecuta `db-ai mounts` para saber qué alias existen, con qué fichero y en qué modo (`ro` o `rw`).
2. Lista solo el nivel que necesitas: `db-ai ls /` para los alias y `db-ai ls /alias` para las tablas del montaje.
3. Si necesitas la forma del árbol, usa `db-ai tree /alias --depth 2`. La profundidad máxima es 4; no abuses de ella.
4. Antes de tocar una tabla, ejecuta `db-ai describe /alias/tabla`: devuelve columnas, claves y capacidades, incluidas las limitaciones que `db-ai` conoce.
5. Usa `db-ai stat PATH` para confirmar qué es una ruta antes de leerla o escribirla.
6. Para cuando sepas la tabla, sus columnas y la clave o el filtro que responde la pregunta. No explores ramas que no vas a usar.

### Fase 2: Leer y buscar

1. Si conoces la clave, lee la fila con `db-ai cat /alias/tabla/clave`; si solo necesitas un valor, lee el campo con `db-ai cat /alias/tabla/clave/campo`.
2. Si buscas por condiciones, usa `db-ai find /alias/tabla --where 'columna=valor'`. Los operadores son `=`, `!=`, `<`, `<=`, `>`, `>=`, `is-null` y `not-null`; varios `--where` se combinan con AND. No hay SQL ni expresiones libres.
3. Si buscas texto, usa `db-ai grep /alias/tabla TEXTO`. Es una subcadena literal, sensible a mayúsculas, sobre columnas de texto autorizadas; no es búsqueda semántica ni FTS.
4. Acota siempre con `--limit`. Una página razonable empieza en 20 o 50 filas; el máximo duro es 1000 y superarlo devuelve `E_LIMIT`.
5. Si `meta.next_cursor` aparece, pide la página siguiente con `--cursor TOKEN`. Repite hasta que no haya cursor o hasta responder la pregunta. El cursor no es una foto del conjunto: los datos pueden cambiar entre páginas, y una tabla sin orden total solo ofrece la primera página.
6. Para volumen, usa `db-ai export /alias/tabla --where ... --format jsonl`. Exporta por stdout y no escribe ficheros; captura solo lo necesario y evita volcar la tabla entera en la conversación.
7. Lee [comandos](references/comandos.md) si dudas de la forma exacta de un comando, sus flags o la forma de la salida.

### Fase 3: Escribir

1. Comprueba el modo del montaje con `db-ai mounts`. `ro` es el defecto: toda escritura devuelve `E_DENIED`. `--mode rw` exige una política explícita, y `rw` por sí solo no concede escritura.
2. Lee la fila objetivo con `db-ai cat` y guarda su `etag`. El ETag representa el contenido actual; no es un número de versión.
3. Planifica primero con `--dry-run` en `touch`, `write`, `cp`, `mv`, `rm` o `batch`. El plan no ejecuta la mutación ni garantiza superar restricciones, pero revela permisos y conflictos antes de tocar datos.
4. Ejecuta la mutación con su precondición: `--if-match ETAG` en `write`, `cp`, `mv` y `rm`; en `cp`, el ETag es el de la fila **origen**. `touch` no lleva ETag porque crea una fila nueva.
5. `--apply` es obligatorio solo en `mv` y `rm`, y es confirmación no interactiva, no permiso. `--dry-run` y `--apply` son incompatibles en la misma invocación.
6. Para varias mutaciones, usa `db-ai batch --data -` o `--data JSON`: máximo 100 operaciones, un solo montaje, una transacción y reversión total si una falla. Cada elemento es `{op, path, ...args}`. El `if_match` de cada operación describe el estado **previo** al lote: no encadenes una operación sobre una fila creada o modificada en el mismo lote; divídelo en dos invocaciones.
7. No cambies campos de identidad con `write`, no muevas filas entre tablas, no crees tablas, no borres de forma recursiva y no busques `--force`. Nada de eso existe.
8. Tras escribir, vuelve a leer la fila y comprueba el resultado y el ETag nuevo. No declares éxito por el código de salida.
9. Lee [escritura](references/escritura.md) antes de la primera mutación o de preparar un lote.

### Fase 4: Cerrar

1. Verifica con `cat`, `find` o `export` lo que acabas de cambiar; incluye el ETag cuando el encargo lo necesite.
2. Separa lo observado de lo no comprobado. Si el commit quedó incierto, no lo presentes como éxito: reconcilia leyendo la base.
3. Informa del alias, la tabla, las filas afectadas y los errores no resueltos. No repitas una escritura para «asegurarte».

## Permisos

1. Montaje `ro` por defecto. `mount --mode rw` exige política explícita o devuelve `E_DENIED`.
2. La política autoriza por lista `allow` de operaciones (`ops`) sobre prefijos de ruta (`prefix`). La comparación es por segmentos, nunca por prefijo de cadena.
3. La escritura es deny-by-default: `rw` no concede escritura por sí solo. Si la política no incluye la operación sobre ese prefijo, la respuesta es `E_DENIED`.
4. Un filtro sobre una columna prohibida se rechaza. No intentes inferir su contenido por otros comandos ni por mensajes de error.
5. `--apply` no amplía permisos. Si la política deniega, la operación se detiene.
6. Ante `E_DENIED`, no escales privilegios ni cambies de montaje por iniciativa propia. Informa de qué operación y qué prefijo faltan.

## ETags

1. Formato `sha256:<hex>`. Se obtiene de `cat` de una fila y se exige en `write`, `cp` (origen), `mv` y `rm`.
2. Representa el contenido, no una versión monotónica: no detecta el ciclo ABA. Tras cada cambio, vuelve a leer para obtener el ETag vigente.
3. Un ETag viejo devuelve `E_CONFLICT`. Relee la fila, decide con el estado actual y no reintentes con el mismo ETag.
4. En `batch`, cada `if_match` se compara con el estado previo al lote. Si una operación necesita el resultado de otra anterior, usa dos invocaciones.

## Errores

`error.code` manda. Estas son las familias y la primera acción correcta:

| Exit | Código | Qué hacer |
|---|---|---|
| 0 | OK | Leer `data`; si había mutación, verificar antes de cerrar. |
| 2 | `E_USAGE` | Corregir la forma del comando o el valor del flag; no reintentar igual. |
| 3 | `E_NOT_FOUND`, `E_STALE_SESSION` | Reconfirmar la ruta o la sesión con `ls`, `stat` o `mounts`. |
| 4 | `E_DENIED` | Detenerse y reportar la operación y el prefijo no autorizados. |
| 5 | `E_CONFLICT` | Releer, revisar el ETag o el destino y decidir de nuevo. |
| 6 | `E_CONSTRAINT` | Respetar la restricción del motor; no buscar un rodeo. |
| 7 | `E_BUSY`, `E_TIMEOUT` | Reducir alcance o reintentar una vez tras observar; no subir el timeout a ciegas. |
| 8 | `E_UNSUPPORTED`, `E_LIMIT` | Reducir `--limit`, la profundidad o el alcance; no forzar la capacidad. |
| 9 | `E_INTERNAL` | Detenerse y reportar; no repetir la mutación. |
| 10 | `E_COMMIT_UNKNOWN` | Reconciliar leyendo la base antes de cualquier reintento. |

Regla de `E_COMMIT_UNKNOWN`: el commit pudo aplicarse. Relee la fila o consulta el lote con `cat`, `find` o `export`; decide según lo que veas y solo entonces reintenta o informa. Reintentar a ciegas puede duplicar o pisar datos.

Lee [errores](references/errores.md) cuando recibas un `error.code` distinto de OK, o antes de diseñar una recuperación.

## Autonomía y contexto mínimo

Elige el comando más pequeño que responda la pregunta:

| Pregunta | Comando | Coste |
|---|---|---|
| ¿Qué bases hay? | `mounts` | Una línea por montaje |
| ¿Qué tablas hay? | `ls /alias` | Una línea por tabla |
| ¿Qué forma tiene? | `tree --depth 2` | Acotado por profundidad |
| ¿Qué columnas y capacidades? | `describe /alias/tabla` | Acotado a la tabla |
| ¿Qué es esta ruta? | `stat PATH` | Una ruta |
| ¿Qué contiene esta fila? | `cat /alias/tabla/clave` | Una fila |
| ¿Qué filas cumplen? | `find ... --limit 20` | Una página |
| ¿Dónde aparece un texto? | `grep ... --limit 20` | Una página |
| ¿Necesito muchas filas? | `export --format jsonl` | Flujo de stdout |

1. Emite un comando por paso y lee su JSON antes del siguiente.
2. No pidas la tabla completa para responder una pregunta de una fila.
3. No repitas una lectura que ya tienes; reutiliza el `etag` y los datos observados.
4. Usa `--session` solo para `cd` y `pwd`. Cada agente usa su propio identificador; no hay sesión global.
5. Si un comando falla, el mensaje ya describe la causa. No encadenes variantes del mismo comando para adivinar.

## Prioridad de la CLI de dominio

Si el dominio tiene una CLI propia que conoce sus reglas de negocio, se prefiere esa CLI para las operaciones de negocio. `db-ai` es el acceso genérico por semántica de filesystem: sirve para explorar, consultar, exportar y para cambios que la CLI de dominio no cubra, siempre con los permisos, ETags y transacciones de este contrato. No reimplementes en `db-ai` una validación que la CLI de dominio ya garantiza.

## Documentación canónica

Esta skill enseña la operación. Los fundamentos, la identidad, las capacidades y el contrato detallado viven en el proyecto fuente:

- `/home/desarrollo/PROJECTS/database-virtual-filesystem/docs/PRD.md`
- `/home/desarrollo/PROJECTS/database-virtual-filesystem/docs/DESIGN.md` (§3 formas de los comandos; §8-9 mutaciones, estado y sesiones)

No copies esas fuentes en el trabajo. Consúltalas solo cuando necesites un detalle de contrato que esta skill no cubra. Si la CLI real y esta skill difieren, manda la CLI y se corrige la skill.

## Referencias

| Fichero | Cuándo se lee |
|---|---|
| [comandos](references/comandos.md) | Antes de usar un comando cuya forma o flags no recuerdes, o al interpretar la salida, los cursores o las sesiones. |
| [escritura](references/escritura.md) | Antes de la primera mutación o al preparar un `batch`. |
| [errores](references/errores.md) | Al recibir un `error.code` distinto de OK o al planificar una recuperación. |

## Antes de cerrar

1. La pregunta está respondida con datos leídos, no supuestos.
2. Toda mutación tuvo permiso, ETag correcto y verificación posterior.
3. Los errores no resueltos y lo no verificado están declarados.
4. No se ha inventado ningún comando, flag ni capacidad fuera de [comandos](references/comandos.md).
