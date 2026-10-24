# Contrato de CLI para agentes

## 1. Gramática

La forma canónica es:

```text
<binario> <comando> [<subcomando>] [flags] [argumentos]
```

- El verbo describe la acción: `get`, `list`, `create`, `update`, `delete`, `run`, `check`.
- Un subcomando solo existe si el dominio tiene una jerarquía real. No inventes niveles para imitar a otras herramientas.
- Los argumentos posicionales son datos, no opciones. Si un valor puede cambiar el comportamiento, es un flag.
- `--` termina la lista de flags; todo lo que sigue es posicional, incluidos valores que empiezan por `-`.
- Un argumento desconocido es error de uso, nunca se ignora.

## 2. Flags

- Nombres en kebab-case: `--output-file`, no `--outputFile`, `--output_file` ni `--OutputFile`.
- Forma canónica con dos guiones; acepta también uno si el parser lo permite sin ambigüedad.
- Un flag tiene un solo significado en toda la CLI. No reutilices `--force` para cosas distintas.
- Los booleanos no llevan valor: `--json`, no `--json=true`.
- Los valores sensibles no se pasan por flag. Usa entorno, archivo con permisos restringidos o `stdin`.
- `--help` y `--version` existen en la raíz y en cada comando; `-h` es alias de `--help` cuando no colisiona.
- La precedencia es: flag > variable de entorno > archivo de configuración > valor por defecto. Si dos fuentes discrepan y la elección importa, dilo en `stderr` o falla; no elijas en silencio.
- Toda variable de entorno usa un prefijo estable del binario y aparece en la ayuda.

## 3. Entrada

- `stdin` se lee solo cuando el comando lo declara: `--input -`, un comando de filtro o una operación que documenta entrada por tubería.
- Si el comando espera datos y `stdin` es un TTY sin `--input`, falla con `2` y explica cómo pasar la entrada.
- Acepta JSON y texto solo si ambos están documentados. Valida el esquema antes de usarlo; un JSON inválido es error de uso (`2`), no de ejecución (`1`).
- Los tamaños máximos se declaran y se aplican. No cargues un flujo infinito en memoria.

## 4. Salida

| Flujo | Contenido | Nunca |
|---|---|---|
| `stdout` | Resultado, JSON de éxito, plan de `--dry-run` | Logs, progreso, avisos, prompts |
| `stderr` | Errores, diagnóstico, progreso, ayuda cuando corresponde | Resultado consumible |
| Código de salida | Resultado de la operación | Detalles que solo estén en el texto |

- En modo texto, imprime el resultado de forma estable y legible. Una tabla es aceptable si las columnas y el orden no cambian entre ejecuciones equivalentes.
- En modo JSON, imprime un único documento y nada más. No antepongas banners, avisos ni líneas de progreso.
- Para flujos continuos (`--follow`), usa JSON Lines: un objeto por línea, sin pretty-print, con `flush` tras cada objeto.
- No dependas del ancho de terminal para construir JSON. El texto puede adaptarse; el contrato no.
- Si `stdout` no es un TTY, no hay color, spinner, barra de progreso ni animación. `NO_COLOR` desactiva el color aunque haya TTY.
- El progreso va a `stderr` y se puede desactivar con `--quiet`. `--quiet` no silencia errores.

## 5. Códigos de salida

| Código | Significado | Ejemplos |
|---|---|---|
| `0` | Éxito, incluido «sin cambios» | `changed:false`, `--dry-run` correcto |
| `1` | Fallo de ejecución | Error de red, disco, dependencia, estado inesperado |
| `2` | Error de uso | Flag desconocido, argumento inválido, JSON malformado, falta `--input` |
| `3` | Cancelado | SIGINT, SIGTERM, contexto cancelado por el llamador |
| `4` | Precondición o conflicto | Falta `--yes`, recurso existente sin `--force`, estado incompatible |

- No uses `1` para errores de uso: impide que un agente distinga «lo llamé mal» de «la operación falló».
- No uses `0` para un fallo parcial. Si una operación por lotes termina con fallos, devuelve `1` y detalla en el JSON qué elementos fallaron.
- `EPIPE` al escribir en `stdout` es una salida normal: termina con `0` sin imprimir un error.
- La ayuda y la versión salen con `0`; un comando o flag desconocido, con `2`.

## 6. Sobre JSON

Éxito:

```json
{
  "ok": true,
  "command": "project.list",
  "data": {
    "items": [],
    "changed": false
  }
}
```

Error:

```json
{
  "ok": false,
  "command": "project.delete",
  "error": {
    "code": "confirmation_required",
    "message": "project.delete requires --yes in non-interactive mode",
    "details": {
      "flag": "--yes"
    }
  }
}
```

Reglas:

- `ok` es siempre booleano y siempre está presente.
- `command` es el nombre estable del comando, no la línea de invocación.
- `code` es un identificador en `snake_case`, estable y documentado. No cambia con el idioma ni con el mensaje.
- `message` es una frase accionable en inglés o en el idioma del proyecto, pero no se usa para decidir: para decidir se usa `code` y el código de salida.
- `details` es un objeto; puede omitirse si no aporta. Nunca incluye secretos, rutas de una máquina concreta ni trazas internas.
- El sobre no cambia entre comandos. Solo cambia `data`.
- Un fallo en modo JSON sigue escribiendo exactamente un documento en `stdout`; el diagnóstico adicional va a `stderr`.

## 7. Ayuda

Cada ayuda incluye, en este orden:

1. Una línea de propósito.
2. Uso: `<binario> <comando> [flags] [argumentos]`.
3. Argumentos posicionales.
4. Flags, con tipo y valor por defecto.
5. Variables de entorno.
6. Ejemplos ejecutables, incluido el modo JSON y `--dry-run` si aplica.
7. Códigos de salida específicos del comando, si añaden información.

La ayuda se escribe en `stdout` cuando se pide con `--help` y sale con `0`. Cuando se muestra por un error de uso, el mensaje breve va a `stderr` y sale con `2`.

## 8. Seguridad e idempotencia

- **Plan y ejecución.** Una operación destructiva se expresa como `plan` + `apply` o como `--dry-run` + `--yes`. El plan enumera qué se crea, modifica o elimina; no ejecuta.
- **Confirmación.** `--yes` es la única confirmación válida en modo no interactivo. Un prompt solo se añade con `--interactive` y TTY.
- **Escritura atómica.** Crea un temporal en el mismo directorio, escribe, sincroniza y renombra. Si el proceso muere, no deja un archivo parcial.
- **Idempotencia.** Define la unidad de estado. Si el estado deseado ya existe, devuelve `0` con `changed:false`. Si existe con otro contenido y no hay `--force`, devuelve `4`.
- **Borrado.** Nunca borres por defecto ni interpretes una ruta vacía, `.` o `/` como objetivo. Valida y normaliza antes.
- **Secretos.** Redacta tokens, cabeceras de autorización y cadenas de conexión en logs y errores. No imprimas el valor de una variable sensible ni siquiera en `--debug`.
- **Rutas.** Respeta la ruta que da el usuario; no la sustituyas por una ruta de la máquina del agente. Si necesitas una ruta temporal, usa el directorio temporal del sistema y límpiala.

## 9. Cancelación y errores de frontera

- `main` crea `ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)` y llama `defer stop()`.
- Pasa `ctx` a cada operación de I/O. Las operaciones que no puedan cancelarse se declaran como tales.
- Al recibir una señal, deja de aceptar trabajo, espera a las tareas en curso con un límite y cierra recursos. Después sale con `3`.
- Un segundo SIGINT puede forzar la salida; si lo implementas, documéntalo y no imprimas una traza.
- El mapeo de error a código de salida y a sobre JSON ocurre en un solo lugar, cerca de `main`, nunca dentro del dominio.
- Un error interno devuelve `1` y un mensaje genérico; los detalles completos solo con `--debug` y siempre sin secretos.

## 10. Compatibilidad

- Añadir un comando, un flag opcional o un campo nuevo en `data` es compatible.
- Renombrar o eliminar un comando, flag, valor de `code` o código de salida es incompatible: exige versión mayor y nota de migración.
- Cambiar el tipo de un campo JSON o su significado es incompatible aunque el nombre no cambie.
- Un flag obsoleto se conserva con aviso en `stderr` durante al menos una versión menor antes de eliminarse.
- El contrato publicado (ayuda, JSON, códigos) es la fuente de verdad. Si el código y la ayuda discrepan, el defecto es del código.
