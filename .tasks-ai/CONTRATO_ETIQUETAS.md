# Contrato de etiquetas del tablero

Guía de cómo gestionar correctamente el catálogo de etiquetas del gestor de tareas y de
cómo asignarlas a las tareas. Lo modifica el proyecto, no la instalación, y su verdad
viva —qué etiquetas existen hoy y cuánto se usan— es siempre `tasks-ai tags`: este
documento dice las reglas, no inventaria el catálogo.

## 1. Las clases y su convivencia

Las etiquetas conviven en una tarea: un tipo, los estructurales que su forma dicte y los
ámbitos que hagan falta. Son tres clases y cada una con su regla.

### 1.1 Tipo — obligatorio y único

Responde «de qué clase de trabajo es esta tarea». Toda tarea lleva exactamente uno:

| Etiqueta | Qué trabajo declara |
|---|---|
| `feat` | Capacidad o integración nueva |
| `fix` | Corrección de un defecto |
| `docs` | Documentación, ADR, contrato o informe |
| `refactor` | Reorganización sin cambio de comportamiento |
| `test` | Pruebas, guardas y verificaciones |
| `style` | Presentación visual |
| `chore` | Instalación, configuración y tareas administrativas |
| `improvement` | Mejora de lectura o de uso |

Los siete primeros son los nombres de Conventional Commits, pensados para commits y
adoptados aquí como vocabulario común. `improvement` es la extensión propia del proyecto.
Solo se estrena o se retira un tipo cambiando este contrato: no se estrena creándolo a
mano en el catálogo.

### 1.2 Estructurales — los dicta la forma de la tarea

No son una elección de tema: los dicta la forma de la tarea, y los escribe quien escribe
la tarea. El producto no añade ni retira ninguna:

- `ODD`: el trabajo que nace del registro ODD.
- `epic`: una tarea con subtareas.
- `task`: una tarea sin subtareas.

`epic` y `task` describen la forma de la tarea y no su nivel: una épica puede colgar de
otra tarea y una tarea puede estar en el primer nivel. Una tarea con padre no nace con
`task` por estarlo, y dejar de tener padre no se la quita; `epic` tampoco aparece sola
al llegarle subtareas, ni se retira al cerrarlas. La forma la marca la persona, igual
que el tipo, y por eso una tarea que se queda sin la etiqueta que le toca es un descuido
de quien la escribió, no algo que el producto corrija.

No se usan para otra cosa y no se crean de nuevo: si faltan en el catálogo, es señal de
que algo los retiró por error.

### 1.3 Ámbito — opcional y repetible

Marca la parte del producto a la que la tarea apunta y **convive con el tipo**: una
tarea lleva su tipo y además los ámbitos que hagan falta (`cli`, `i18n`, `web`, `api`).
Reglas de nomenclatura:

- En minúsculas, una palabra, sin espacios ni guiones.
- Sin sinónimos de un ámbito que ya exista: si `cli` cubre el sentido, no se crea
  `commandline`.
- Nombra una parte del producto, no un proyecto entero ni una persona.

## 2. Asignación correcta a una tarea

La asignación se hace con la lista entera: `tasks-ai update <ref> --tags "a,b,c"` pone
esa lista completa, así que siempre se parte de las etiquetas actuales y se añade o
retira sobre ellas, nunca se escribe la lista nueva de memoria. Al crear se usa
`tasks-ai create --tags "a,b,c"`, que deja la tarea con esa lista desde el primer
momento.

1. La tarea lleva **su tipo** desde que se crea —con `--tags` en la creación, o después
   con `update`—, y no cambia salvo que el trabajo cambie de naturaleza.
2. Los **estructurales** los pone quien crea la tarea y, cuando su forma cambia, se
   ponen y se retiran a mano: el producto no los ajusta solo.
3. Los **ámbitos** se añaden cuando la tarea apunta a una parte concreta del producto y
   se retiran cuando dejan de describirla.
4. Antes de asignar una etiqueta que no existe, vale la regla del catálogo (§3): si hace
   falta crearla, se crea con su descripción y luego se asigna.

## 3. Gestión del catálogo

El catálogo no crece sin criterio ni se conserva sin uso:

1. **Antes de crear, se lee el catálogo** (`tasks-ai tags`): si una etiqueta existente
   cubre el sentido, se usa esa y no se crea nada.
2. **Toda etiqueta nueva se crea con descripción**
   (`tasks-ai tag create --name ... --description ...`): una etiqueta sin descripción no
   es contrato, es ruido. Un ámbito sin descripción no dice para qué sirve y acabará
   duplicado.
3. **Una etiqueta sin asignaciones se borra** (`tasks-ai tag delete`): el catálogo no es
   un archivo histórico, es el vocabulario vivo del tablero. Borrarla retira sus
   asignaciones y avisa de las tareas que la usaban.
4. **Renombrar** (`tasks-ai tag edit`) cambia el nombre que muestran las tareas sin
   tocar su fila guardada; se usa para corregir nombres, no para cambiar de clase.
5. **El tipo no se improvisa**: si ninguna etiqueta de tipo encaja con un trabajo, el
   hueco es de este contrato, no del catálogo; se propone el cambio aquí y se decide
   antes de crear nada.

## 4. Cómo se cambia este contrato

Un cambio de clases, de tipos o de reglas se propone en el tablero como tarea de
documentación (`docs`), se decide con el usuario y se escribe aquí antes de usar la
etiqueta nueva. Después de cambiarlo, el catálogo se ajusta en la misma unidad de
trabajo: lo que este documento permite, `tasks-ai tags` lo muestra; lo que prohíbe, el
catálogo no lo conserva.
