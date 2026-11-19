# Escritura, ETags y lotes

Se lee antes de la primera mutación o al preparar un `batch`. Desarrolla la fase 3 de `SKILL.md`; no repite el flujo de descubrimiento ni la tabla de errores.

## Puerta previa

1. `db-ai mounts` debe mostrar el alias en modo `rw`. En `ro`, toda escritura es `E_DENIED`.
2. El modo `rw` no basta: la política del montaje debe autorizar la operación (`ops`) sobre el prefijo de la ruta (`prefix`), comparado por segmentos. La política la edita el operador en `$XDG_CONFIG_HOME/db-ai/config.json` (fallback `~/.config/db-ai`): si una ruta te devuelve `E_DENIED`, pide su autorización; no la edites tú.
3. Lee la fila objetivo y guarda su `etag`. Sin ese dato no puedes usar la precondición que exigen `write`, `cp`, `mv` y `rm`.
4. Si la operación es destructiva o cambia identidad, planifica con `--dry-run` primero.

## Operaciones

| Comando | Qué hace | Precondición |
|---|---|---|
| `touch PATH --data JSON\|-` | Inserta una fila con las columnas indicadas y devuelve la clave efectiva. | Ninguna; no inventa valores obligatorios omitidos. |
| `write ROW_OR_FIELD --data JSON\|- --if-match ETAG` | Actualiza un campo o varios campos de una fila. Un registro recibe un mapa parcial, no un reemplazo. | `--if-match` con el ETag actual. |
| `cp ROW DEST_ROW --if-match ETAG` | Copia los campos ordinarios de una fila a una clave destino explícita dentro de la misma tabla. | `--if-match` con el ETag de la fila **origen**. |
| `mv ROW DEST_ROW --if-match ETAG --apply` | Renombra una PK simple. | ETag actual y `--apply`. |
| `rm ROW --if-match ETAG --apply` | Borra una fila. No es recursivo. | ETag actual y `--apply`. |
| `batch --data JSON\|-` | Ejecuta varias mutaciones en una transacción. | Las precondiciones de cada operación. |

Reglas de identidad y forma:

- `write` no cambia PK ni columnas generadas.
- `cp` no copia columnas generadas ni relaciones; una restricción UNIQUE puede impedir la copia.
- `mv` solo opera sobre PK simple, no generada, con destino inexistente, y deniega referencias entrantes. No mueve entre tablas.
- `rm` bloquea si existen referencias entrantes con efecto indirecto. No hay borrado recursivo ni `--force`.
- No se crean tablas, columnas ni índices. Eso pertenece al esquema y queda fuera de `db-ai`.
- `db-ai` rechaza triggers de escritura sobre la tabla objetivo y claves foráneas con cascada o `SET NULL`/`DEFAULT` en la operación afectada. No intentes desactivar restricciones.

## Dry-run y confirmación

- `--dry-run` está disponible en `touch`, `write`, `cp`, `mv`, `rm` y `batch`.
- Solo planifica y consulta: no ejecuta la mutación, no dispara triggers y no promete superar restricciones. El plan no es una autorización futura.
- `--apply` es obligatorio únicamente en `mv` y `rm`.
- `--apply` es confirmación no interactiva de una operación destructiva, no permiso. La política sigue mandando.
- `--dry-run` y `--apply` son incompatibles en la misma invocación.

## ETag

1. Formato `sha256:<hex>`; sale en `cat` de una fila y en las filas de `find` y `export`.
2. Cubre tabla, clave, versión de esquema y valores tipados completos. Representa contenido, no una versión monotónica: no detecta ABA.
3. `--if-match` se compara dentro de la transacción. Un valor viejo devuelve `E_CONFLICT`.
4. Tras cualquier cambio, relee la fila para obtener el ETag vigente. No reutilices el anterior.
5. Una operación que exige leer la fila completa se deniega si el actor no tiene acceso completo a esa fila.

## Batch

`--data` recibe un array de operaciones explícitas. Cada elemento es un envoltorio `{op, path, ...args}` con los mismos argumentos de la operación individual:

```json
[
  {"op":"write","path":"/work/tasks/TK-001/status","data":{"kind":"text","data":"done"},"if_match":"sha256:..."},
  {"op":"touch","path":"/work/tasks","data":{"id":{"kind":"text","data":"TK-002"}}}
]
```

Límites y semántica:

1. Máximo 100 operaciones, como valor por defecto y como máximo.
2. Un solo montaje y una sola transacción. No hay atomicidad entre bases.
3. Si una operación falla, se revierte todo el lote.
4. Cada operación cumple sus propios permisos y precondiciones.
5. No hay referencias dinámicas a resultados previos. El `if_match` describe el estado **previo** al lote: una operación no puede encadenarse sobre una fila creada o modificada en el mismo lote. Si lo intentas, el lote devuelve `E_CONFLICT` y revierte; divídelo en dos invocaciones.
6. `--dry-run` planifica el lote completo con las mismas reglas.

## Secuencia de una mutación

1. Comprobar montaje y política.
2. Leer la fila y guardar el ETag.
3. Planificar con `--dry-run`.
4. Ejecutar con `--if-match` y, si aplica, `--apply`.
5. Releer la fila y comprobar el resultado y el ETag nuevo.
6. Informar de la clave afectada, el resultado y cualquier error no resuelto.

Si el resultado es `E_COMMIT_UNKNOWN`, no reintentes a ciegas: reconcilia leyendo la base con `cat`, `find` o `export` y decide con lo observado.
