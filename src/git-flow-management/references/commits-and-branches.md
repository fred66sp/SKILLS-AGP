# Commits y ramas

Usa esta referencia al crear una rama o preparar un commit, tanto en el modelo por defecto como en un repositorio con política Git Flow declarada.

## Ramas

- Usa minúsculas y palabras separadas por guiones.
- En el modelo por defecto, la base es `main`: `feature/<slug>`, `fix/<slug>`, `docs/<slug>`, `refactor/<slug>` o `chore/<slug>`.
- En un repositorio con Git Flow declarado, respeta la base obligatoria de su tabla: `feature/<id>-<slug>`, `fix/<id>-<slug>`, `hotfix/<id>-<slug>` y `release/<version>`.
- Verifica la base antes de crear la rama:

~~~bash
git merge-base --is-ancestor <base> HEAD
git log -1 --oneline <base>
~~~

Si la base está desactualizada frente a su upstream, informa del estado y propón una actualización de la base como operación separada y confirmada.

## Mensaje de commit

Formato de [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0-beta.2/), con nombre y descripción en inglés:

~~~text
<type>(<scope opcional>): <descripción en imperativo, en inglés>
~~~

Tipos habituales: feat, fix, docs, chore, refactor, test, style, perf, ci, build y revert.

- Un commit representa un cambio lógico coherente, no un archivo ni un paso intermedio.
- Por defecto, una tarea completa cabe en un commit aunque afecte a varios archivos.
- Varios commits solo con una razón clara: separar cambios independientes, facilitar una revisión concreta o conservar una recuperación útil.
- Descripción breve, en imperativo, en inglés y sin punto final.
- Sin firmas de IA ni líneas Co-Authored-By salvo petición expresa.
- Una ruptura se marca con `!` o con un pie `BREAKING CHANGE`.
- El cuerpo del commit puede nombrar la tarea que lo sostiene, por ejemplo `Refs: tk-141`, cuando el proyecto usa un tablero.

## Preparación segura

1. Barrido previo: documentación, `CHANGELOG`, plantillas, referencias cruzadas, diagramas y políticas del repositorio que describan el comportamiento anterior. Se corrige antes, no después.
2. Inspecciona cambios rastreados, no rastreados y ya preparados. Si el índice ya contiene cambios ajenos al plan, detente antes de preparar nada.
3. Separa explícitamente lo que queda fuera del commit.
4. Prepara únicamente rutas enumeradas.
5. Revisa el diff preparado y muéstralo.
6. Presenta el mensaje exacto y las decisiones abiertas; si hay alguna, se pregunta antes de commitear.
7. Ejecuta el commit confirmado y verifica SHA, mensaje y archivos.

## Confirmación

Sin confirmación no hay commit, ni siquiera en una tarea pequeña ni en una tarea con varios commits previstos. Y sin barrido previo no hay confirmación: si el cambio deja algo incoherente —documentación desfasada, política del repositorio en contra, una plantilla que ya no describe el flujo— eso se arregla o se pregunta antes, nunca con un commit de corrección inmediata detrás.

- Puedes presentar las etapas juntas —rama, stage, commit, integración, borrado de rama, push— y recibir una confirmación que las cubra.
- Esa confirmación no se reaprovecha: otro conjunto de archivos, otra rama, un estado distinto o un push nuevo requieren confirmación nueva.
- Si el usuario autoriza los commits coherentes de la tarea actual, no repitas la pregunta por cada uno de los previstos, siempre que el alcance no cambie.
- Antes de ejecutar el commit, revalida rama, `HEAD` y árbol de índice (`git write-tree`). Si cualquiera difiere de lo mostrado, la confirmación queda invalidada.

## Integración y limpieza

1. Integra solo si el usuario lo ha pedido o autorizado.
2. Verifica que el resultado está contenido en el destino.
3. Si la rama ya no se necesita, informa y pide confirmación antes de `git branch -d <rama>`.
4. No borres una rama con trabajo no integrado ni una rama remota sin autorización específica.
