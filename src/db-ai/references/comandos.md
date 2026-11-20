# Comandos y salida de db-ai

Se lee cuando el agente necesita la forma exacta de un comando, sus flags, la interpretación de la salida, los cursores o las sesiones. El flujo y las reglas de decisión están en `SKILL.md`; este fichero no las repite.

## Formas exactas

```text
db-ai mount FILE /ALIAS [--mode ro|rw]
db-ai umount /ALIAS
db-ai mounts
db-ai ls [PATH] [--limit N] [--cursor TOKEN]
db-ai tree [PATH] [--depth N] [--limit N]
db-ai stat PATH
db-ai describe PATH
db-ai cat PATH
db-ai --session ID cd PATH
db-ai --session ID pwd
db-ai find PATH [--where EXPR]... [--order SPEC] [--fields LIST] [--count] [--limit N] [--cursor TOKEN]
db-ai grep PATH TEXT [--fields LIST] [--count] [--limit N] [--cursor TOKEN]
db-ai touch PATH --data JSON|-
db-ai write ROW_OR_FIELD --data JSON|- --if-match ETAG
db-ai upsert TABLE --data JSON|- [--if-match ETAG] [--dry-run]
db-ai cp ROW DEST_ROW --if-match ETAG
db-ai mv ROW DEST_ROW --if-match ETAG --apply
db-ai rm ROW --if-match ETAG --apply
db-ai batch --data JSON|-
db-ai export PATH [--where EXPR]... [--format json|jsonl] [--limit N] [--cursor TOKEN]
```

`describe`, `find`, `grep`, `touch` y `export` reciben una ruta VFS (`/alias/tabla`), no un nombre de tabla suelto.

## Flags globales

| Flag | Uso |
|---|---|
| `--session ID` | Resuelve rutas relativas. Obligatorio en `cd` y `pwd`; el resto es stateless. El ID es ASCII `[A-Za-z0-9._-]+`. |
| `--timeout N` | Segundos, de 1 a 60. Defecto 5. |
| `--actor NAME` | Etiqueta informativa; no es identidad autenticada. |
| `--request-id ID` | Identificador de la petición; se genera si falta y aparece en `meta.request_id`. |
| `--json` | Aceptado por compatibilidad; no-op. La salida ya es JSON. |
| `--help` | Ayuda. No abre bases. |

Flags de comando: `--mode`, `--limit`, `--cursor`, `--depth`, `--where`, `--order`, `--fields`, `--count`, `--data`, `--if-match`, `--format`, `--dry-run`, `--apply`. Un flag desconocido o fuera de su comando es `E_USAGE`.

## Salida

Éxito:

```json
{"version":1,"ok":true,"data":{},"meta":{"truncated":false,"next_cursor":"...","request_id":"..."}}
```

Error:

```json
{"version":1,"ok":false,"error":{"code":"E_...","message":"..."}}
```

- `cat` de una fila, `find` y `export` comparten la forma `{path, fields, etag}`. Con `--fields`, `fields` contiene solo las columnas pedidas más la clave (en orden de catálogo); el `etag` sigue siendo el de la fila completa.
- `find --count` y `grep --count` emiten `{"count":N}` sin filas: el total del conjunto filtrado, no el de la página (`--limit` no lo acota; `--count` es incompatible con `--cursor`). `grep --count` cuenta filas, no coincidencias por columna.
- `upsert` emite `{result: "created"|"updated", applied: true|false, path, etag}`; `applied:false` y sin `etag` es la simulación `--dry-run`.
- `cat` de un campo emite el envoltorio tipado `{kind, data}`.
- `stat` emite `{type, path, columns|keys}`.
- `grep` emite la fila, la columna y la posición de la coincidencia.
- `describe` emite las columnas, las claves y las capacidades, con las limitaciones detectadas.
- `--format jsonl` (solo `export`) emite una fila por línea; un fallo a mitad de flujo deja stdout parcial y código distinto de cero.

## Rutas e identidad

1. Ruta absoluta: `/alias/tabla/clave/campo`.
2. Segmentos con escape porcentual UTF-8; también `/`, `%` y el segmento entero `.` o `..`. Una clave textual `a/b` se escribe `a%2Fb`.
3. Cadena vacía de clave: marcador `~e`. `~` literal: `%7E`. Entero: decimal canónico.
4. Claves compuestas: `~k` seguido de base64url sin padding del array JSON canónico de envoltorios tipados, en orden de PK, por ejemplo `[{"kind":"text","data":"a"},{"kind":"integer","data":"42"}]`.
5. Vistas, tablas virtuales y claves sin PK estable quedan fuera del MVP navegable. Una tabla sin orden total solo ofrece la primera página de `find`, `grep` o `export`.

## Filtros, orden y búsqueda

- Operadores de `--where`: `=`, `!=`, `<`, `<=`, `>`, `>=`, `is-null`, `not-null`.
- Varios `--where` se combinan con AND.
- El valor se interpreta primero como JSON y, si no lo es, como texto literal: `1` es entero, `"1"` es texto, `null`/`true`/`false` son literales JSON.
- `--order "col:asc,col2:desc"` ordena en el servidor; la dirección por defecto es `asc`. El desempate es el resto de la clave, así que el orden es total y los cursores recorren sin omisiones ni duplicados. Los nulos se ordenan al final en ambas direcciones. Sin `--order`, el orden es el interno (clave ascendente). Columna o dirección inválida: `E_USAGE`. Sin SQL libre.
- `--fields "col1,col2"` proyecta en la salida de `find` y `cat` de fila: columnas del catálogo, sin espacios; columna desconocida, repetida o vacía: `E_USAGE`. La clave se emite siempre. El pedido es del volumen de salida, no de SQLite: la fila llega completa y el ETag no cambia.
- `grep` busca una subcadena literal en columnas TEXT autorizadas con comparación sensible a mayúsculas; no hay FTS ni expresiones regulares.
- Un filtro sobre una columna prohibida se rechaza con `E_DENIED`; no se filtra en cliente para esquivarlo. Proyectar con `--fields` no amplía acceso: el permiso es de la tabla.

## Paginación

1. `--limit` va de 1 a 1000. Superarlo devuelve `E_LIMIT`.
2. La página siguiente se pide con `--cursor` y el valor de `meta.next_cursor`.
3. El cursor es keyset y firmado; no es una foto del conjunto. Los datos pueden cambiar entre páginas.
4. Sin `meta.next_cursor`, no hay más páginas.
5. `export` acepta los mismos filtros y cursores que `find`, y escribe en stdout: no crea ficheros por sí mismo.

## Sesiones

- Solo `cd` y `pwd` usan sesión; ambas exigen `--session`.
- `cd` valida que el destino sea un contenedor y que el actor tenga permiso.
- `pwd` revalida el cwd; un alias desmontado devuelve `E_STALE_SESSION`.
- No hay sesión global: cada agente usa la suya.

## Lo que no existe

No hay SQL libre ni lenguaje natural, ni `mkdir` (no se crean tablas), ni `mv` entre tablas, ni `rm` recursivo, ni `--force`, ni shell interactivo, ni FUSE, ni servidor, ni PostgreSQL en el MVP. `export --format jsonl` no es un flag `--jsonl`. No se editan campos de identidad. Las claves de catálogo se citan, nunca se interpolan como SQL.
