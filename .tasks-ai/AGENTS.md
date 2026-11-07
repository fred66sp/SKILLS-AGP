# Gestor de tareas del proyecto

Este proyecto guarda sus tareas con el gestor local que vive en esta carpeta.

## Qué hay aquí

| Elemento | Qué es |
|---|---|
| `tasks.db` | Las tareas y las decisiones del proyecto |
| `settings.json` | El prefijo de las referencias, la base y los ajustes de la interfaz |
| `AGENTS.md` | Estas instrucciones |
| `CONTRATO_ETIQUETAS.md` | El contrato de las etiquetas: clases, asignación y gestión del catálogo |

## Cómo se usa

Desde cualquier punto del proyecto:

```bash
tasks-ai create --title "Preparar el análisis"   # crea una tarea y devuelve su JSON
tasks-ai create --title "Revisar el análisis" --parent sk-1  # crea una subtarea de sk-1
tasks-ai show sk-1                               # devuelve la tarea en JSON, con sus hijas, sus bloqueantes, sus dependientes y sus comentarios
tasks-ai update sk-1 --priority 1                # cambia los campos que se piden y devuelve la tarea
tasks-ai update sk-1 --tags "docs,urgente"       # pone la lista entera de etiquetas de sk-1: una lista vacía la deja sin ninguna
tasks-ai tags                                    # devuelve el catálogo de etiquetas con el uso de cada una
tasks-ai tag create --name "docs" --color blue   # crea una etiqueta; el color que falta es blue
tasks-ai tag edit docs --name "documentacion"    # cambia de la etiqueta lo que se pide y nada más; renombrar no toca ninguna tarea
tasks-ai tag delete docs                         # borra la etiqueta con sus asignaciones y avisa de las tareas que la usaban
tasks-ai adr create --title "Adoptar SQLite" --deciders "Ana"  # crea una decisión durable y devuelve su número
tasks-ai adr edit 1 --status accepted            # cambia lo que se pide y devuelve el ADR; el cuerpo se congela al salir de proposed
tasks-ai adr list                                # devuelve los ADR del proyecto, sin sus cuerpos
tasks-ai adr show ADR-001                        # devuelve el ADR entero, con su cuerpo por secciones
tasks-ai adr import --dir docs/decisions         # guarda los ADR de un directorio que aún no estén, sin duplicar
tasks-ai adr export --dir docs/decisions         # escribe la exportación generada de los ADR y su índice
tasks-ai close sk-1 --reason done                # cierra la tarea con su motivo y devuelve la tarea
tasks-ai reopen sk-1                             # reabre la tarea cerrada y devuelve la tarea
tasks-ai block sk-2 sk-1                         # deja sk-2 bloqueada por sk-1 y devuelve sk-2
tasks-ai unblock sk-2 sk-1                       # retira el bloqueo entre sk-2 y sk-1 y devuelve sk-2
tasks-ai comment sk-1 --body "..."               # añade un comentario a sk-1 y devuelve la tarea
tasks-ai comment list sk-1                       # devuelve los comentarios de sk-1, del primero al último, cada uno con su identidad
tasks-ai comment edit sk-1 1 --body "..."        # cambia el cuerpo del comentario 1 de sk-1: conserva su identidad y su fecha
tasks-ai serve                                   # arranca la API HTTP en la dirección y el puerto del settings y anuncia los cambios por un canal abierto
```

El motivo de cierre es obligatorio y debe ser uno de: `done`, `duplicate`, `absorbed`,
`stale` o `superseded`. Cerrar una tarea con subtareas abiertas se rechaza sin escribir
nada, cerrar una subtarea no cierra su padre, y una tarea ya cerrada no se cierra otra
vez ni una abierta se reabre.

## Cuándo se usa qué

El tablero es el único registro del trabajo. Cada momento del ciclo tiene su operación, y
se hace cuando toca, no al final:

| Momento | Operación |
|---|---|
| Abrir el trabajo | `tasks-ai create --title "..."`; la tarea nace `open` |
| Abrir el trabajo de una épica | `tasks-ai update <ref> --status in_progress` en la épica cuando empieza su primera hija; su cierre espera a que cierren todas |
| Empezar el trabajo | `tasks-ai update <ref> --status in_progress` |
| Surgir un avance, una decisión o un bloqueo | `tasks-ai comment <ref> --body "..."` en ese momento |
| Dejar el trabajo a medias | `tasks-ai update <ref> --status open` |
| Terminar | informe a la persona y `tasks-ai close <ref> --reason done`, con su revisión o su pedido expreso |
| Dejar de necesitarla sin hacerla | `tasks-ai close <ref> --reason duplicate`, `absorbed`, `stale` o `superseded` |

El tablero no habla de Git: el estado de Git solo vive en Git.

El estado bloqueado se calcula y no se guarda: una tarea aparece bloqueada mientras
tenga algún bloqueante que no esté `done`, y deja de estarlo al cerrar al bloqueante o
al retirar el bloqueo. Una referencia que no resuelve se rechaza y una tarea no puede
bloquearse por sí misma. Los comentarios se pueden añadir y editar por su identidad
dentro de la tarea; su cuerpo es obligatorio y no hay operación de borrado.

Las etiquetas se gestionan por su nombre en el catálogo de `tags`; toda tarea lleva desde
que nace un tipo y un estructural (`task` o `epic`), y el vocabulario con el que nace el
proyecto y las reglas para asignarlo están en
[`CONTRATO_ETIQUETAS.md`](CONTRATO_ETIQUETAS.md). El color, si se da,
debe ser uno de la paleta que la propia ayuda del comando enumera (`tasks-ai tag create
--help`); un color que falte es `blue` y un color desconocido se rechaza. Renombrar una
etiqueta cambia el nombre que muestran las tareas sin tocar su fila guardada, y borrar
una retira sus asignaciones avisando de las tareas que la usaban.

Las decisiones durables del proyecto viven en la misma base, cada una con su número y su
referencia `ADR-NNN`. Se escriben con `adr`, no editando el markdown: `docs/decisions/`
es una exportación generada desde la base y `adr export --check` dice si hay deriva. El
cuerpo se congela al salir de `proposed`; después solo se admiten añadidos fechados en
«Más información», y un cambio de decisión se publica como un ADR nuevo que sustituye al
anterior.

Toda operación responde en JSON por la salida estándar, y los avisos y errores van por
la salida de error con la forma `{"error": "..."}`. `serve` no es una operación: no
devuelve JSON, habla por la salida de error y se detiene con Ctrl+C o con SIGTERM.

## Las referencias

Cada tarea tiene un número interno, que es su identidad, que es único en el proyecto y
que no se reutiliza. La referencia visible se compone con el prefijo del proyecto y ese
número: `sk-1`. Se escribe sin distinguir mayúsculas y admite espacios alrededor.
