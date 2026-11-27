# Gestor de tareas del proyecto

Este proyecto guarda sus tareas con el gestor local que vive en esta carpeta.

## Qué hay aquí

| Elemento | Qué es |
|---|---|
| `tasks.db` | Las tareas y las decisiones del proyecto |
| `settings.json` | El prefijo de las referencias, la base y los ajustes de la interfaz |
| `AGENTS.md` | Estas instrucciones |
| `CONTRATO_ETIQUETAS.md` | El contrato de las etiquetas: clases, asignación y gestión del catálogo |

## Cómo habla el agente con el producto

La única superficie de interacción del agente es el subcomando `tasks-ai aif`: lee una
petición JSON por la entrada estándar, escribe exactamente una respuesta JSON por la
salida estándar y deja los diagnósticos en la salida de error. El código de salida sale
del campo `result` de la respuesta: 0 ejecutada o descubrimiento, 2 `input_needed` o
`invalid`, 3 `unknown_operation`, `unsupported_version` o `malformed_request`, 4 `denied`
y 1 `failed`.

```bash
echo '{"aif":"0.2"}' | tasks-ai aif    # descubrimiento
```

- Cuando no sepas qué pedir, manda una petición sin `operation` conocida: el producto
  responde con `discovery` y el vocabulario. No memorices ni reproduzcas esa lista
  después; el producto es autodescriptivo.
- Para recuperar el trabajo del proyecto, pide el tablero con `tasks_board`.
- Una respuesta reparable —`invalid` o `input_needed`— se corrige con el campo que marca
  el error y se reenvía la petición completa.

El resto de la ayuda de los comandos está en su `--help` y en la documentación del
producto.

## Cuándo se usa qué

El tablero es el único registro del trabajo. Cada momento del ciclo tiene su operación, y
se hace cuando toca, no al final:

| Momento | Operación |
|---|---|
| Abrir el trabajo | Crea la tarea; nace `open`. Un encargo sustancial nace con objetivo, alcance y criterios de aceptación en su descripción; un cambio pequeño, con un título claro |
| Abrir el trabajo de una épica | Pon la épica en curso cuando empieza su primera hija; su cierre espera a que cierren todas |
| Empezar el trabajo | Pon la tarea en curso |
| Surgir un avance, una decisión o un bloqueo | Añade un comentario en ese momento |
| Dejar el trabajo a medias | Devuelve la tarea a pendiente, con un comentario que señale el siguiente paso |
| Terminar | Informa a la persona y cierra la tarea con el motivo `done`, con su revisión o su pedido expreso |
| Dejar de necesitarla sin hacerla | Cierra con `duplicate`, `absorbed`, `stale` o `superseded` |

El motivo de cierre es obligatorio y debe ser uno de: `done`, `duplicate`, `absorbed`,
`stale` o `superseded`. Cerrar una tarea con subtareas abiertas se rechaza sin escribir
nada, cerrar una subtarea no cierra su padre, y una tarea ya cerrada no se cierra otra
vez ni una abierta se reabre.

El tablero no habla de Git: el estado de Git solo vive en Git. El texto de una tarea, de
sus notas y de un comentario no nombra a Git ni el estado de la tarea o de la entrega:
solo nombra el trabajo.

El estado bloqueado se calcula y no se guarda: una tarea aparece bloqueada mientras
tenga algún bloqueante que no esté `done`, y deja de estarlo al cerrar al bloqueante o
al retirar el bloqueo. Una referencia que no resuelve se rechaza y una tarea no puede
bloquearse por sí misma. Los comentarios se pueden añadir y editar por su identidad
dentro de la tarea; su cuerpo es obligatorio y no hay operación de borrado.

Las etiquetas se gestionan por su nombre en el catálogo; toda tarea lleva desde que nace
un tipo y un estructural (`task` o `epic`), y el vocabulario con el que nace el proyecto y
las reglas para asignarlo están en [`CONTRATO_ETIQUETAS.md`](CONTRATO_ETIQUETAS.md).
Renombrar una etiqueta cambia el nombre que muestran las tareas sin tocar su fila
guardada, y borrar una retira sus asignaciones avisando de las tareas que la usaban.

Las decisiones durables del proyecto viven en la misma base, cada una con su número y su
referencia `ADR-NNN`. Se escriben con `adr`, no editando el markdown: `docs/decisions/`
es una exportación generada desde la base y `adr export --check` dice si hay deriva. El
cuerpo se congela al salir de `proposed`; después solo se admiten añadidos fechados en
«Más información», y un cambio de decisión se publica como un ADR nuevo que sustituye al
anterior.

## Las referencias

Cada tarea tiene un número interno, que es su identidad, que es único en el proyecto y
que no se reutiliza. La referencia visible se compone con el prefijo del proyecto y ese
número: `sk-1`. Se escribe sin distinguir mayúsculas y admite espacios alrededor.
