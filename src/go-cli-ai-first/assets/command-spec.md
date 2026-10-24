# Ficha de comando

Copia esta ficha por cada comando antes de implementarlo. Si un campo no se puede rellenar, el comando no está especificado.

## Identidad

- **Binario:**
- **Comando:** `<verbo> [<subcomando>]`
- **Propósito:** una frase.
- **Consumidores:** agente, script, persona.
- **Cambio de contrato:** compatible | incompatible (versión y migración).

## Entrada

| Elemento | Tipo | Obligatorio | Por defecto | Validación |
|---|---|---|---|---|
| argumento | | | | |
| `--flag` | | | | |
| variable de entorno | | | | |
| `stdin` | | | | |

## Salida

- **Éxito en texto:**
- **Éxito en JSON (`data`):**
- **Campos estables:**
- **Flujo continuo:** no | JSON Lines con `--follow`
- **Límite:** `--limit` / máximo de elementos.

## Errores

| `code` | Código de salida | Cuándo | `details` |
|---|---|---|---|
| | | | |

## Efectos y seguridad

- **Estado que lee:**
- **Estado que modifica:**
- **Idempotencia:** misma entrada y mismo estado → `changed:true|false`.
- **`--dry-run`:** qué plan muestra y qué no modifica.
- **`--yes`:** qué operación lo exige.
- **Escritura atómica:** sí | no aplica.
- **Secretos:** qué se redacta.

## Ciclo de vida

- **Contexto:** operaciones cancelables.
- **Timeout:** dónde se aplica.
- **Cierre:** recursos y orden.
- **Señales:** salida con `3`.

## Pruebas mínimas

- [ ] Éxito en texto.
- [ ] Éxito en JSON válido.
- [ ] Error de uso (`2`).
- [ ] Error de ejecución (`1`).
- [ ] Precondición sin `--yes` (`4`).
- [ ] `--dry-run` no muta.
- [ ] Cancelación (`3`).
- [ ] `EPIPE` sin ruido.
