# Protocolos de ACM

Se lee al ejecutar cualquiera de los siete protocolos. `SKILL.md` resume qué hace
cada uno y cuándo; aquí está la secuencia de operaciones, los criterios de captura
y la reconciliación de errores. Las formas exactas de los comandos y sus flags se
consultan en la skill `db-ai`; este fichero solo nombra operaciones (`cat`, `find`,
`grep`, `upsert`, `touch`, `write`, `batch`) y campos.

## Convenciones comunes

- Cada fila tiene un `id` UUIDv7 textual que genera el productor; la base no lo
  inventa. Las marcas temporales son ISO-8601 en UTC.
- El `content_hash` se calcula antes de `touch` con el algoritmo de DESIGN §5.2:
  normalización NFC, array JSON canónico de los campos semánticos y SHA-256 con
  prefijo `sha256:`. El esquema garantiza formato y unicidad, no el algoritmo.
  Usa el helper canónico `tools/content-hash.py` del ejemplo en lugar de
  reimplementarlo: todos los productores deben calcularlo igual.
- `files` y `open_questions` son arrays JSON; las rutas son relativas al
  repositorio, nunca absolutas de la máquina.
- La sesión de ACM es una fila de `/mem/sessions`, no la sesión de db-ai que solo
  resuelve `cd` y `pwd`. No uses esa sesión para la memoria.
- Escribe solo después de abrir la sesión de ACM: la clave foránea lo exige. Sin
  sesión, un `upsert` de observación devuelve `E_CONSTRAINT`.

## 1. Inicio de sesión y recuperación de contexto

Objetivo: saber dónde quedó el proyecto y qué reglas rigen antes de actuar.

1. Comprueba el alias con `mounts` y confirma que `cat` de `meta` responde. Lee
   `project_key` con `find` por `name` y compáralo con el esperado del proyecto.
   Si no coincide, detente: la base no es de este proyecto.
2. Abre la sesión de ACM con `upsert` en `/mem/sessions`: `id`, `agent_id`,
   `source`, `goal`, `status='open'`, `started_at`, `created_at` y `updated_at`.
   Crear no lleva `--if-match`; actualizar una sesión existente, siempre con
   `--if-match` del ETag leído. La recuperación de solo lectura puede ocurrir
   antes; la primera escritura de conocimiento, no.
3. Recuperación en frío, con guion determinista de cuatro `find` y un paso de
   decisión (presupuesto medido sobre el fixture de 10.240 observaciones:
   ≈1.900 tokens estimados, por debajo de los 2.000 del contrato):
   1. `find /mem/sessions --order "started_at:desc" --limit 5 --fields "id,status"`.
      Elige la sesión del proyecto; añade el filtro `agent_id` solo si el encargo
      exige el mismo agente. El orden lo aplica db-ai, no la skill. Lee el
      `summary` de la sesión elegida con `cat` solo si el checkpoint no basta.
   2. `find /mem/checkpoints --where "session_id=<id>" --where "status=active" --order "created_at:desc" --limit 1 --fields "state,next_steps"`.
      Dos activas para la misma sesión son una anomalía del protocolo 7.
   3. `find /mem/observations --where "session_id=<id>" --order "created_at:desc" --fields "kind,topic_key,title" --limit 5`.
      Decisiones y contexto reciente; el detalle va con `cat` solo si se actúa.
   4. `find /mem/preferences --where "source=human" --where "status=active" --fields "pref_key,value" --limit 20`.
      En frío se recuperan las preferencias de la persona; las del agente
      (`source=agent`) o importadas se piden por `pref_key` cuando el paso las
      necesite. Aplica cada valor o declara el conflicto con la instrucción de
      la persona.
   5. Solo si hay una contradicción sin resolver: un `find` acotado por el
      `topic_key` o el `pref_key` en duda.
   6. Siguiente paso: `next_steps` del checkpoint. Lee el detalle con `cat` solo
      si la fila proyectada no basta.
4. Sesión conocida (handoff): salta el paso 3.1 y entra por `session_id` en
   checkpoints (3.2) y observaciones (3.3). El historial completo de la sesión
   no forma parte del guion: se pide después, solo si no hay checkpoint o si la
   pregunta lo exige.
5. Si una respuesta trae `truncated`, el límite dejó fuera filas: acota con
   `--where` o sube el `--limit` solo del paso afectado; no recorras el cursor.

Presupuesto: objetivo ≤2 000 tokens estimados para el guion en frío (M-ACM-01).
La proyección (`--fields`) recorta el ancho de cada fila y el orden lo aplica
db-ai; la clave del registro se emite siempre, aunque no se pida. Los errores
esperables son `E_USAGE` (precondición o parámetro: columna inexistente o
repetida en `--fields`, actualización sin `--if-match`) y `E_CONFLICT` (ETag
obsoleto: releer y reintentar). Sin FTS ni búsqueda difusa: filtros, orden,
proyección y límites deterministas.

## 2. Captura de conocimiento durante el trabajo

Captura cuando el conocimiento sea durable, reutilizable y no obvio. No captures
actividad.

| Se captura | No se captura |
|---|---|
| descubrimientos, patrones, correcciones, arquitectura y aprendizajes | conversaciones, prompts o salidas de herramientas completas |
| decisiones con justificación y alternativas | cada paso rutinario o cada invocación |
| preferencias operativas con motivo | secretos, credenciales o datos personales |
| checkpoints con estado y próximos pasos | especulación presentada como hecho |

1. Elige `kind`: `discovery`, `pattern`, `bugfix`, `architecture`, `learning` o
   `decision`. Una decisión exige `topic_key` y `rationale` no vacío.
2. Elige `confidence`: `confirmed`, `inference`, `hypothesis`, `proposal` o
   `unknown`. No presentes una hipótesis como hecho.
3. `topic_key` sigue `familia/descripcion`, minúsculas y kebab-case, dos niveles
   como máximo; por ejemplo `storage/db-per-project` o `commit/approval`.
4. El título debe contener los términos con los que alguien lo buscará después.
   Sin FTS ni ranking, la recuperabilidad se gana en la captura (hallazgo R1 de
   ACM-03): un título genérico es una fila perdida.
5. Genera UUIDv7 y `content_hash`, y ejecuta `upsert` en la tabla que
   corresponda: sin `--if-match` para una captura nueva, con el ETag leído para
   corregir una existente. Verifica con `cat` cuando el resultado no baste. Si el
   `content_hash` ya existe, aplica el protocolo 4.1 en vez de insistir.
6. Las preferencias pueden nacer de una persona sin sesión: `session_id` nulo y
   `source='human'` son válidos y explícitos.

## 3. Recuperación selectiva

1. Por identidad: `cat` de la ruta `/mem/<tabla>/<uuid>`, o de un campo concreto
   si solo necesitas ese valor.
2. Por columnas: `find` con filtros de `kind`, `status`, `topic_key`,
   `session_id`, `agent_id` o `pref_key`. Páginas cortas: 10 a 20 filas para una
   pregunta; 50 para el historial completo de una sesión.
3. Por texto: `grep` con un término distintivo y límite corto. Es subcadena
   literal y sensible a mayúsculas; después lee el campo con `cat`.
4. Recencia: `--order "created_at:desc"` (o `started_at`) con `--limit` corto; el
   orden y el desempate por PK los aplica db-ai, no la skill. Para el checkpoint
   vigente pide por `session_id` (protocolo 1.3) en vez de ordenar la tabla.
   Recuento: `--count` en `find` y `grep` cuando solo haga falta cardinalidad;
   es incompatible con `--cursor`.
5. Si el término no aparece, reformula con las palabras que usaría quien
   capturó; no pidas la tabla completa. Un fallo de recuperación es una señal
   sobre la captura, no una invitación a exportar.
6. Contexto de reanudación con presupuesto cerrado y guion acotado por defecto
   (protocolo 1.3):
   - Sesiones: `--order "started_at:desc" --limit 5 --fields "id,status"`.
   - Checkpoint: por `session_id`; uno o dos `find`.
   - Decisiones: solo las de la sesión, `--order "created_at:desc"` y `--fields`
     con los campos mínimos; la clave del registro viaja siempre.
   - Preferencias: activas del humano en frío (`source=human`) y por `pref_key`
     las del agente cuando el paso las pida, con `--fields "pref_key,value"`.
   El historial de la sesión no forma parte del guion: se pide si no hay
   checkpoint o si la pregunta lo exige. Nada de `find` sin filtro ni `cat`
   redundante. Las cinco invocaciones en frío apuntan a ≤2 000 tokens
   estimados; la re-medición con db-ai 0.4.0 está pendiente y se declara su
   resultado cuando se haga. Si el guion se pasa, se acota antes de crecer:
   menos `--fields`, `--limit` menor o un rango de fechas.

## 4. Actualización y consolidación

### 4.1 Misma captura repetida

`UNIQUE(content_hash)` impide la segunda fila. Con `upsert` la repetición es una
actualización explícita, no un `E_CONSTRAINT` que haya que perseguir:

1. Registro nuevo: `upsert <tabla> --data '<json>'` sin `--if-match`. Devuelve
   `{"result":"created",...}`.
2. Registro existente: lee la fila y su ETag, y repite con `--if-match`. Una
   actualización sin `--if-match` es `E_USAGE`; un ETag obsoleto es
   `E_CONFLICT` (relee y reintenta). Devuelve `{"result":"updated",...}`.
3. En `observations`, la repetición suma `duplicate_count` y refresca
   `last_seen_at`. En `checkpoints` y `preferences` es un no-op: no la ejecutes.
4. `--dry-run` calcula el resultado sin efectos si quieres previsualizar el
   `created`/`updated` y el ETag antes de aplicarlo.
5. Verifica con `cat` solo si el resultado no basta.

### 4.2 Sustitución

Sustituye una decisión, un checkpoint o una preferencia con un solo `batch`:

1. Busca y lee la fila activa anterior; guarda su ETag.
2. Prepara dos operaciones: `upsert` de la fila nueva y actualización de la
   anterior (`upsert --if-match` o `write` con ese ETag) con `status='superseded'`,
   `superseded_by` igual al id nuevo y `updated_at`.
3. Ordena el lote: inserción primero, actualización después. La actualización
   apunta a una fila preexistente; no encadenes sobre una fila creada en el mismo
   lote.
4. Ejecuta el lote; si una operación falla, revierte entero.
5. Verifica que queda exactamente una activa para el tema, la sesión o la clave.

El ETag de la fila anterior serializa la escritura: dos agentes que sustituyan la
misma fila compiten por él y el segundo recibe `E_CONFLICT`. Si no existía fila
activa, dos primeras capturas concurrentes pueden dejar dos activas: verifica
después y reconcilia según el protocolo 7.

### 4.3 Duplicado semántico

No hay detección automática. Compara por `topic_key`, `kind` y texto.

- Si es la misma decisión con otras palabras, no crees una segunda activa.
- Si no puedes decidir, marca la existente `needs_review` con `upsert --if-match`
  y deja la duda en `rationale` o `body`. Si cambias texto semántico, recalcula
  `content_hash` en la misma operación.
- Nunca fusiones ni borres por iniciativa propia: la fusión es una decisión
  humana.

### 4.4 Estados

`active` es vigente. `superseded` exige `superseded_by` y es terminal. `obsolete`
es conocimiento invalidado sin reemplazo y también es terminal. `needs_review` es
dudoso, conflictivo o vencido, y vuelve a `active`, `superseded` u `obsolete`
cuando se resuelve. Una fila terminal no se reactiva: si el conocimiento vuelve,
se captura una fila nueva con UUID nuevo.

## 5. Creación de checkpoints

Un checkpoint captura el estado de reanudación de una sesión.

1. Cuándo: al cerrar la sesión, al alcanzar un hito, antes de una compactación o
   de un traspaso, y al abandonar el trabajo.
2. Contenido: `goal`, `state`, `next_steps`, `files` y `open_questions`.
   `next_steps` no puede estar vacío; deja primero la acción concreta que sigue.
3. Si la sesión ya tiene un checkpoint activo, sustitúyelo con el `batch` del
   protocolo 4.2. Solo uno queda activo por sesión.
4. No lleva `review_after`: su vigencia la marca el checkpoint posterior, no el
   tiempo.

## 6. Cierre y reanudación de sesiones

### 6.1 Cierre

1. Lee la sesión y guarda su ETag vigente.
2. Con `upsert --if-match` del ETag leído (o `write` con el mismo ETag), fija
   `status='closed'`, `ended_at`, `summary` y `updated_at`. Sin ETag no hay
   actualización: `E_USAGE`. Limítate a esos campos: no reescribas procedencia
   (`agent_id`, `source`, `started_at`, `created_at`).
3. Si el trabajo se abandona, usa `status='abandoned'` y deja un checkpoint que
   explique el estado.
4. Verifica con `cat` y confirma que el checkpoint deja un siguiente paso
   identificable.

### 6.2 Reanudación

1. Ejecuta el protocolo 1 con el checkpoint como pieza central y el guion
   acotado de §3.6: por `session_id` si la sesión es conocida; si no, por la
   sesión más reciente (`--order "started_at:desc"`, protocolo 1.3). Decisiones
   solo de la sesión y preferencias solo activas. No pidas la tabla de
   checkpoints sin filtro.
2. La continuidad es del proyecto por defecto, entre sesiones y agentes: un
   checkpoint de otra sesión u otro agente es válido y la procedencia queda
   registrada. Si el encargo exige el mismo agente, filtra por `agent_id` y, sin
   checkpoint suyo, decláralo.
3. Continúa desde `next_steps`; no repitas los hallazgos ya capturados.
4. Revisa la cola `needs_review` antes de dar por vigente una decisión dudosa.
5. Límite residual: el guion mira las cinco sesiones más recientes. Un
   checkpoint activo huérfano de una sesión más antigua solo aparece subiendo ese
   `--limit`; sigue siendo convención de la skill, no garantía del motor.

## 7. Resolución de conflictos y recuerdos contradictorios

| Situación | Acción |
|---|---|
| `E_USAGE` | Falta una precondición o un parámetro no es válido: columna inexistente o repetida en `--fields`, actualización sin `--if-match`, `--count` junto a `--cursor`. Corrige la invocación; no la reintentes igual. |
| `E_CONFLICT` | Relee la fila, obtén el ETag nuevo y decide con el estado actual. No reutilices el ETag viejo. |
| `E_COMMIT_UNKNOWN` | No reintentes a ciegas. Lee por `id` (en un `upsert`) o por `content_hash`/`session_id` (en un `write` o `batch`). Si el cambio está, verifica y cierra; si no está, confirma la ausencia y reintenta con el mismo `id`; si no puedes concluir, informa la incertidumbre. |
| `E_DENIED` | Detente. Reporta la operación y el prefijo; no escales privilegios, no cambies de montaje ni busques una ruta equivalente. |
| `E_CONSTRAINT` | Distingue la causa: duplicado exacto (protocolo 4.1), sesión inexistente (ábrela antes), `CHECK` de decisión (falta `topic_key` o `rationale`) o enlace de sustitución incoherente. Corrige los datos; no desactives restricciones. |
| `E_BUSY` o `E_TIMEOUT` | Reduce el alcance y reintenta una vez tras observar; no subas plazos a ciegas. |

Recuerdos contradictorios:

1. Dos filas activas para el mismo `topic_key`, sesión o `pref_key`: no borres
   ninguna. Marca ambas `needs_review`, informa a la persona y registra la
   reconciliación como una observación cuando ella decida.
2. Contradicción de contenido: prioriza `confirmed` sobre `inference`,
   `hypothesis` o `proposal`. Mismo grado de certeza no resuelve el conflicto: la
   fila más reciente es una pista, no autoridad.
3. `review_after` vencido: informa la fecha y propón `needs_review`. No escribas
   durante la lectura; la decisión es de la persona (convención adoptada, PRD
   §14).
4. La memoria nunca manda sobre una instrucción explícita de la persona. Si una
   preferencia guardada contradice lo que pide ahora, aplica lo que pide y deja
   constancia de la contradicción para revisar la preferencia.
