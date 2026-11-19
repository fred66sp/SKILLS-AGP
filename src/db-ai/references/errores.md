# Errores y recuperación

Se lee al recibir un `error.code` distinto de OK o al planificar una recuperación. La tabla corta y la regla de cierre están en `SKILL.md`; aquí se detalla qué significa cada código y qué acción evita pérdida de datos.

## Regla general

`error.code` es la fuente de verdad. El código de salida solo agrupa códigos y nunca identifica el error por sí solo. La salida de error es un único objeto JSON en stdout:

```json
{"version":1,"ok":false,"error":{"code":"E_...","message":"..."}}
```

Los diagnósticos van a stderr. No interpretes el mensaje como permiso para probar variantes: corrige la causa.

## Tabla

| Exit | Código | Significado | Acción correcta |
|---|---|---|---|
| 0 | `OK` | Éxito. | Leer `data`. Si hubo mutación, verificar con una lectura. |
| 2 | `E_USAGE` | Sintaxis, flag o valor inválido. | Corregir la forma; un flag desconocido no se sustituye por otro. |
| 3 | `E_NOT_FOUND` | El recurso no existe o no es navegable. | Reconfirmar con `mounts`, `ls` o `stat`. |
| 3 | `E_STALE_SESSION` | El cwd de la sesión ya no es válido (por ejemplo, alias desmontado). | Reabrir contexto con `cd` o dejar de usar la sesión para esa ruta. |
| 4 | `E_DENIED` | La política o el modo de acceso deniegan la operación. | Detenerse y reportar operación y prefijo. No escalar privilegios. |
| 5 | `E_CONFLICT` | ETag o destino en conflicto. | Releer, revisar el ETag o el destino y decidir de nuevo. |
| 6 | `E_CONSTRAINT` | Una restricción del motor impidió la operación. | Respetar la restricción; no buscar un rodeo ni desactivar nada. |
| 7 | `E_BUSY` | Contención de la base. | Reducir alcance y reintentar una vez tras observar. |
| 7 | `E_TIMEOUT` | Se agotó `--timeout`. | Reducir alcance o acotar la consulta; no subir el plazo a ciegas. |
| 8 | `E_UNSUPPORTED` | Capacidad no soportada en el MVP. | Cambiar de estrategia; no forcejear la capacidad. |
| 8 | `E_LIMIT` | Presupuesto excedido (por ejemplo, `--limit` > 1000). | Reducir `--limit`, `--depth` o el tamaño de la respuesta. |
| 9 | `E_INTERNAL` | Fallo interno. | Detenerse, reportar y no repetir la mutación. |
| 10 | `E_COMMIT_UNKNOWN` | El resultado del commit es incierto. | Reconciliar leyendo la base antes de reintentar o informar. |

## E_COMMIT_UNKNOWN

El commit pudo aplicarse o no. No hay forma de saberlo por el código de salida.

1. No repitas la mutación.
2. Relee la fila o consulta el rango con `cat`, `find` o `export`.
3. Compara lo observado con la intención: si el cambio está aplicado, trata la operación como completada y verifica el ETag; si no lo está, decide si reintentar con el ETag vigente.
4. Si no puedes determinar el estado, informa de la incertidumbre y del recurso afectado. No declares éxito ni fracaso.

## Recuperación por familia

- `E_CONFLICT`: el ETag representa contenido, no una versión monotónica. Relee y decide con el estado actual; el mismo ETag no vuelve a funcionar.
- `E_DENIED`: la política compara prefijos por segmentos. Comprueba la operación exacta y la ruta; no intentes una ruta equivalente ni otro montaje para esquivarla.
- `E_LIMIT`: reduce `--limit` (máximo 1000), la profundidad de `tree` (máximo 4) o el número de operaciones del lote (máximo 100).
- `E_CONSTRAINT`: una FK, UNIQUE u otra restricción del motor rechazó el cambio. Ajusta los datos o detente; no desactives restricciones.
- `E_BUSY` / `E_TIMEOUT`: acota la operación. Un reintento único tras observar el estado es aceptable; la repetición a ciegas no.
- `E_NOT_FOUND`: confirma que el alias sigue montado y que la clave existe. Una tabla sin PK estable puede no ser navegable por clave.
- `E_STALE_SESSION`: el cwd quedó inválido. Vuelve a fijarlo con `cd` o usa rutas absolutas.

## Lo que nunca se hace

- Reintentar una mutación tras `E_COMMIT_UNKNOWN` sin leer.
- Reutilizar un ETag tras un cambio o un `E_CONFLICT`.
- Tratar `--apply` como permiso.
- Convertir un `E_DENIED` en una búsqueda de otro camino de acceso.
- Ocultar un error no resuelto en el informe de cierre.
