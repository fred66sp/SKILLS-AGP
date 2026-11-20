# Protocolos de ACM

Se lee al ejecutar cualquiera de los siete protocolos. `SKILL.md` resume qué hace
cada uno y cuándo; aquí está la secuencia de operaciones, los criterios de captura
y la reconciliación de errores. Las formas exactas de los comandos y sus flags se
consultan en la skill `db-ai`; este fichero solo nombra operaciones (`cat`, `find`,
`grep`, `touch`, `write`, `batch`) y campos.

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
- Escribe solo después de abrir la sesión de ACM: la clave foránea lo exige y un
  `touch` huérfano devuelve `E_CONSTRAINT`.

## 1. Inicio de sesión y recuperación de contexto

Objetivo: saber dónde quedó el proyecto y qué reglas rigen antes de actuar.

1. Comprueba el alias con `mounts` y confirma que `cat` de `meta` responde. Lee
   `project_key` con `find` por `name` y compáralo con el esperado del proyecto.
   Si no coincide, detente: la base no es de este proyecto.
2. Abre la sesión de ACM con `touch` en `/mem/sessions`: `id`, `agent_id`,
   `source`, `goal`, `status='open'`, `started_at`, `created_at` y `updated_at`.
   La recuperación de solo lectura puede ocurrir antes; la primera escritura de
   conocimiento, no.
3. Preferencias aplicables: pide por `pref_key` conocido —una invocación por
   clave que rija la tarea, como máximo tres en la reanudación— con
   `status='active'` y límite 2. Si aún no conoces las claves, pide una página
   mínima (`status='active'`, límite 3), elige las aplicables y, si `truncated`
   avisa de recorte, pide por clave las que falten. No pidas todas las activas.
   Con más de tres claves, pide ahora las que rijan la acción inmediata y el
   resto después. Aplica cada valor o declara el conflicto con la instrucción de
   la persona.
4. Checkpoint vigente. Acota el alcance antes de buscar: `find` ordena por PK
   ascendente y no garantiza el más reciente en la primera página (C-ACM-03).
   - Sesión conocida (handoff o reanudación de una sesión concreta): `find` en
     `/mem/checkpoints` por `session_id` y `status='active'`, con límite corto
     (5). El UUIDv7 mayor de esa página es el vigente; dos activas para la misma
     sesión son una anomalía y van al protocolo 7.
   - Continuidad del proyecto sin sesión conocida: `find` en `/mem/sessions` por
     `started_at` dentro de una ventana acotada (por defecto, los últimos 14
     días) y límite corto (50). Si la respuesta trae `truncated`, la página no
     contiene la más reciente: acorta el corte y repite; no uses el cursor para
     recorrer páginas. Con la ventana entera en memoria, ordena localmente por
     UUIDv7 mayor (recencia) y toma la primera sesión con checkpoint activo.
     Busca después su checkpoint por `session_id`, como en el caso anterior.
   Exige la continuidad del mismo agente solo cuando la persona o el encargo lo
   pidan: añade `agent_id` a los filtros de sesión y checkpoint y, si no hay
   checkpoint de ese agente, decláralo en vez de adoptar el de otro en silencio.
   Ninguno de los dos casos recorre páginas: si la sesión buscada queda fuera de
   la ventana, amplía el corte y repite el `find` de sesiones.
   Lee objetivo, estado, próximos pasos, ficheros y preguntas abiertas. Si no
   hay checkpoint, el historial de la sesión anterior es el siguiente recurso.
5. Decisiones de la tarea: `find` en `/mem/observations` por `kind='decision'`,
   `status='active'` y el `topic_key` de la tarea en curso, con límite 5. No
   pidas «todas las decisiones activas». Sin `topic_key` conocido, pide una
   página mínima (límite 3) y declara el recorte de `truncated`: ese caso es un
   aviso, no una recuperación completa.
6. Observaciones abiertas: `find` por `status='needs_review'` y revisa las
   `open_questions` del checkpoint.
7. Para cuando la pregunta esté respondida. Lee el detalle con `cat` solo si la
   fila localizada no basta; no exportes tablas.

Límite de contexto: apunta a seis invocaciones o menos para reanudar
(M-ACM-01) y no acumules filas completas. El checkpoint vigente cuesta uno o
dos `find` acotados (por `session_id`, o sesiones y luego checkpoint); nunca uno
sin filtro. El historial de la sesión no forma parte del guion por defecto: se
pide después, solo si no hay checkpoint o si la pregunta lo exige. `find`
devuelve filas enteras y no hay proyección: el control está en el filtro, el
límite y el tamaño del texto.

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
5. Genera UUIDv7 y `content_hash`, y ejecuta `touch` en la tabla que
   corresponda. Verifica con `cat`. Si `touch` devuelve `E_CONSTRAINT` por hash,
   aplica la deduplicación exacta del protocolo 4; no reintentes la inserción.
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
4. Recencia: dentro de una ventana acotada, el UUIDv7 mayor es el más reciente.
   No esperes orden descendente ni recuentos baratos. Para el checkpoint vigente
   pide por `session_id` (protocolo 1.4) en vez de ordenar la tabla.
5. Si el término no aparece, reformula con las palabras que usaría quien
   capturó; no pidas la tabla completa. Un fallo de recuperación es una señal
   sobre la captura, no una invitación a exportar.
6. Contexto de reanudación con presupuesto cerrado y guion acotado por defecto:
   - Sesiones: ventana acotada del protocolo 1.4 o `session_id` conocido.
   - Checkpoint: por `session_id` y `status='active'`; uno o dos `find`.
   - Decisiones: solo las activas del `topic_key` de la tarea en curso, límite
     5. Sin `topic_key`, página mínima (límite 3) con aviso de recorte.
   - Preferencias: solo las claves aplicables, por `pref_key` y
     `status='active'`, límite 2 por clave y como máximo tres claves; sin
     claves, página mínima (límite 3).
   El historial de la sesión no forma parte del guion: se pide si no hay
   checkpoint o si la pregunta lo exige. Nada de `find` sin filtro ni `cat`
   redundante. Con `session_id` conocido y dos claves aplicables son cuatro
   `find`; en frío, la ventana añade el quinto. La re-medición sobre la base de
   10 000 observaciones está en
   `scenarios/evidence/evidence-benchmark.md`, «Re-medición M-ACM-03»: el guion
   acotado con sesión conocida cumple los 2 000 tokens; en frío la ventana de
   sesiones lo desborda porque `find` devuelve filas enteras (C-ACM-03). El
   objetivo no se toca: se declara el resultado. El detalle se pide después,
   solo del elemento que vayas a usar.

## 4. Actualización y consolidación

### 4.1 Duplicado exacto

`UNIQUE(content_hash)` impide la segunda fila; la segunda captura devuelve
`E_CONSTRAINT`.

1. No repitas el `touch`.
2. Busca la fila existente por `content_hash`.
3. En `observations`, actualiza `duplicate_count` y `last_seen_at` con `write` y
   ETag vigente. En `checkpoints` y `preferences`, el duplicado es un no-op.
4. Verifica con `cat`.

### 4.2 Sustitución

Sustituye una decisión, un checkpoint o una preferencia con un solo `batch`:

1. Busca y lee la fila activa anterior; guarda su ETag.
2. Prepara dos operaciones: `touch` de la fila nueva y `write` de la anterior con
   `status='superseded'`, `superseded_by` igual al id nuevo y `updated_at`.
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
- Si no puedes decidir, marca la existente `needs_review` con `write` y deja la
  duda en `rationale` o `body`. Si cambias texto semántico, recalcula
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
2. Con `write`, fija `status='closed'`, `ended_at`, `summary` y `updated_at`.
   Limítate a esos campos: no reescribas procedencia (`agent_id`, `source`,
   `started_at`, `created_at`).
3. Si el trabajo se abandona, usa `status='abandoned'` y deja un checkpoint que
   explique el estado.
4. Verifica con `cat` y confirma que el checkpoint deja un siguiente paso
   identificable.

### 6.2 Reanudación

1. Ejecuta el protocolo 1 con el checkpoint como pieza central y el guion
   acotado de §3.6: por `session_id` si la sesión es conocida; si no, por la
   sesión más reciente de la ventana (protocolo 1.4). Decisiones solo del
   `topic_key` de la tarea en curso y preferencias solo por `pref_key`
   aplicable. No pidas la tabla de checkpoints sin filtro.
2. La continuidad es del proyecto por defecto, entre sesiones y agentes: un
   checkpoint de otra sesión u otro agente es válido y la procedencia queda
   registrada. Si el encargo exige el mismo agente, filtra por `agent_id` y, sin
   checkpoint suyo, decláralo.
3. Continúa desde `next_steps`; no repitas los hallazgos ya capturados.
4. Revisa la cola `needs_review` antes de dar por vigente una decisión dudosa.
5. Límite residual: un checkpoint activo huérfano de una sesión anterior a la
   ventana solo aparece ampliando el corte. Es convención de la skill, no
   garantía del motor: `find` no tiene orden descendente (C-ACM-03) y la tabla
   no se recorre entera.

## 7. Resolución de conflictos y recuerdos contradictorios

| Situación | Acción |
|---|---|
| `E_CONFLICT` | Relee la fila, obtén el ETag nuevo y decide con el estado actual. No reutilices el ETag viejo. |
| `E_COMMIT_UNKNOWN` | No reintentes a ciegas. Lee por `id` (en un `touch`) o por `content_hash`/`session_id` (en un `write` o `batch`). Si el cambio está, verifica y cierra; si no está, confirma la ausencia y reintenta con el mismo `id`; si no puedes concluir, informa la incertidumbre. |
| `E_DENIED` | Detente. Reporta la operación y el prefijo; no escales privilegios, no cambies de montaje ni busques una ruta equivalente. |
| `E_CONSTRAINT` | Distingue la causa: duplicado exacto (recupera por hash), sesión inexistente (ábrela antes), `CHECK` de decisión (falta `topic_key` o `rationale`) o enlace de sustitución incoherente. Corrige los datos; no desactives restricciones. |
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
