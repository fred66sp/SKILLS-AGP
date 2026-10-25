---
name: git-flow-management
description: "Gestiona y verifica operaciones Git con ceremonia proporcional al tamaño y al riesgo: permite el commit directo en main en tareas pequeñas y exige rama corta en las normales o complejas, conservando la política que el repositorio declare. Deja siempre los cambios preparados en el stage con un mensaje Conventional Commits en inglés y pide confirmación explícita antes de commitear, antes de borrar una rama ya integrada y antes de cualquier push. Úsala siempre que el agente vaya a realizar o planificar cualquier operación Git: ramas, commits, integraciones, releases, hotfixes, conflictos, publicación y recuperación. No la uses para operaciones ajenas a Git ni para migrar una política de ramas sin encargo explícito."
metadata:
  version: "1.0.0"
---

# Gestión de Git con ceremonia proporcional

Gestiona Git como un procedimiento verificable, no como una intención. Clasifica la tarea por tamaño y riesgo, aplica la ceremonia mínima que mantiene el resultado fiable, presenta lo que vas a ejecutar, espera confirmación y demuestra el resultado con comandos de solo lectura.

La seguridad no debe convertir cada cambio en un trámite pesado. Una corrección de texto no merece el mismo procedimiento que una migración.

## Invariantes obligatorias

1. Esta skill es obligatoria para cualquier operación Git. No continúes un flujo ignorando sus comprobaciones porque el usuario haya dicho «haz Git Flow», «haz un commit» o «sube los cambios».
2. No declares que se ha aplicado Git Flow, se ha integrado una rama, se ha publicado un cambio o se ha terminado una release sin verificarlo con comandos de solo lectura y mostrar el resultado.
3. La política Git documentada del repositorio prevalece sobre cualquier modelo genérico. Si el repositorio no declara política, aplica el modelo por defecto de esta skill: `main` como línea estable y ramas cortas de trabajo cuando la tarea lo justifique.
4. Ningún commit se ejecuta sin confirmación explícita. Deja los cambios preparados en el stage, propón el mensaje exacto y pide confirmación antes de crear nada.
5. No pidas confirmación con decisiones abiertas. Antes de commitear, comprueba que nada de lo que has encontrado va a obligar a tocar esos mismos ficheros después: hallazgos, huecos de alcance, documentación desincronizada, plantillas o políticas del repositorio incoherentes con el cambio. Lo que necesite una decisión del usuario se pregunta **antes** del commit; lo que puedas resolver con evidencia se resuelve **antes** del commit. Un commit que obliga a un commit de corrección inmediata es un fallo de preparación, no un paso más del trabajo.
6. La confirmación no es global ni reutilizable. Cubre únicamente las etapas que enumera y el estado concreto que has mostrado. Una rama distinta, un conjunto de archivos distinto, un conflicto, un push nuevo o una discrepancia invalidan la confirmación. Antes de ejecutar el commit, revalida rama, `HEAD` y árbol de índice (`git write-tree`); si alguno cambió, detente y pide una confirmación nueva.
7. Puedes presentar varias etapas en un mismo plan y recibir una sola confirmación conjunta, pero nunca aprovechar una confirmación previa para una etapa que no estaba en ella.
8. No amplíes el alcance. No uses add global, no incluyas cambios ajenos, no incluyas no rastreados ni hagas amend salvo que el plan aprobado lo nombre expresamente. Si el índice ya contiene cambios preparados, detente antes de `git add` salvo que coincidan exactamente con el alcance enumerado.
9. No uses reset destructivo, clean, restauración desde otra revisión, borrado forzado de ramas, push forzado, borrado de etiquetas o ramas remotas, ni reescritura de historia salvo autorización específica para ese comando. Lee [recuperación y operaciones peligrosas](references/recovery-and-dangerous-operations.md).
10. `develop`, cuando existe, es una rama protegida: nunca prepares trabajo normal sobre ella. `main` admite trabajo directo solo en tareas pequeñas y de riesgo contenido, siempre con stage revisado y confirmación posterior. En una tarea normal o compleja desde `main`, propón una rama corta de trabajo antes de modificar archivos.
11. Cualquier operación remota —push, fetch para integrar, pull o creación de referencias remotas— requiere confirmación propia, aunque el commit ya esté hecho y confirmado.
12. Ante conflicto, estado inesperado, error o resultado distinto del plan, detente. No improvises una resolución; inspecciona y prepara un nuevo plan.

## Clasificación proporcional

Clasifica sin interrumpir al usuario cuando la clasificación no cambie una decisión importante. Ante la duda razonable, trátala como la categoría superior.

| Tamaño | Ejemplos | Rama | Commit | Verificación |
|---|---|---|---|---|
| Pequeña | Texto, documentación, configuración o corrección localizada; diff pequeño y reversible | No obligatoria. Trabajo directo en `main` permitido | Un commit coherente | Revisar el diff y ejecutar una comprobación localizada si existe |
| Normal | Funcionalidad completa, corrección de varios archivos, cambio coordinado | Rama corta recomendada si estás en `main` | Un commit coherente; varios solo con una razón | Validación principal del proyecto |
| Compleja | Cambio incompatible, migración, reestructuración amplia, riesgo de recuperación | Rama específica obligatoria | Varios commits por unidad funcional cuando aporten recuperación o revisión | Validación principal más comprobaciones de los puntos críticos |

Señales de que la tarea no es pequeña: toca código ejecutable en varios módulos, cambia datos, contratos públicos, seguridad o concurrencia, o no sabrías deshacerla con una lectura del diff.

## Inspección proporcional

La inspección es de solo lectura y no requiere confirmación. Al empezar, comprueba el estado y no lo repitas tras cada paso:

~~~bash
git status --short --branch
~~~

Esa comprobación basta para una tarea pequeña. Amplía la inspección antes de proponer una operación persistente de una tarea normal o compleja:

~~~bash
git branch --show-current
git branch -a -vv
git remote -v
git log --graph --oneline --decorate --all -n 30
~~~

Lee la documentación de contribución y de flujo si existe; prevalece sobre esta skill. Consulta [detección de política](references/workflow-detection.md) si hay dudas. Para operaciones acotadas —crear una rama, preparar archivos, revisar el diff preparado— lee [operaciones normales](references/normal-operations.md).

Debes conservar los cambios previos del usuario: no los sobrescribas ni los mezcles en silencio. Si afectan a los archivos que vas a tocar, dilo antes de continuar. No actualices `main` desde un remoto por iniciativa propia.

## Clasificación del repositorio

- Modelo por defecto: `main` como única rama de larga vida, ramas cortas `feature/*`, `fix/*`, `docs/*`, `refactor/*` o `chore/*` cuando la tarea no es pequeña.
- Política Git Flow declarada: existe evidencia documental o práctica verificable de `main`, `develop` y ramas de trabajo asociadas. Aplica la tabla condicional de más abajo.
- Git Flow documentado, pendiente de evidencia operativa: la guía es obligatoria para el siguiente trabajo, pero no declares que Git Flow está demostrado en la práctica.
- Política existente distinta: conserva su modelo; no inventes `develop`, Issues, PR, SemVer, etiquetas ni reglas de merge.
- Política desconocida: informa de la evidencia y pide decisión antes de una operación persistente.

## Modelo por defecto: `main` y ramas cortas

- `main` contiene lo que está listo para usarse y no se abandona por reflejo.
- Las ramas de trabajo se crean desde `main` y viven lo mínimo.
- Sin `develop`, `release/*` ni `hotfix/*` por defecto.
- La integración en `main` se decide aparte del trabajo: nunca fusiones por iniciativa propia.
- La estrategia de integración es la que mantenga el historial claro para ese repositorio; si la política documentada fija `--no-ff`, respétala.

## Política Git Flow, solo si el repositorio la declara

| Tipo | Base obligatoria | Destino obligatorio | Propósito |
|---|---|---|---|
| main | — | — | Código listo para producción; releases etiquetadas |
| develop | main | — | Integración de la siguiente versión |
| feature/<id>-<slug> | develop | develop | Nueva funcionalidad |
| fix/<id>-<slug> | develop | develop | Corrección no productiva |
| release/<version> | develop | main y después develop | Preparación de release |
| hotfix/<id>-<slug> | main | main y después develop | Corrección urgente de producción |

Usa feature/<slug> o fix/<slug> si no existe sistema de incidencias. No inventes un identificador. No presupongas que está instalada la extensión git-flow: usa Git normal.

Para esta política: crea develop desde el commit inicial de main; crea cada rama de trabajo desde su base obligatoria y verifica la relación antes de trabajar; integra en ramas protegidas mediante PR cuando exista un mecanismo de revisión configurado; conserva el back-merge de toda release y hotfix hacia develop.

Lee [operaciones Git Flow verificables](references/git-flow-operations.md) para cada tipo de rama. Lee [releases y versionado](references/releases-and-versioning.md) solo al preparar una release o hotfix.

## Protocolo de commit

Ningún commit se ejecuta sin confirmación previa, y ninguna confirmación se pide con cabos sueltos. El orden es siempre este:

1. Barrido previo. Antes de preparar nada, revisa si este cambio deja algo incoherente a su alrededor: documentación que describe el comportamiento anterior, `CHANGELOG`, plantillas, referencias cruzadas, diagramas o políticas del repositorio que contradicen lo nuevo. Lo que puedas corregir con evidencia, corrígelo ahora; lo que necesite una decisión del usuario, pregúntalo ahora.

2. Prepara únicamente las rutas que el plan enumera:

~~~bash
 git add -- src/module.ts tests/module.test.ts
 git diff --cached
~~~

3. Redacta el mensaje según [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0-beta.2/), con nombre y descripción en inglés:

~~~text
<tipo>(<ámbito opcional>): <descripción breve en imperativo, en inglés>
~~~

4. Presenta antes de commitear: archivos preparados, mensaje exacto, validación realizada, cuántos commits propones, y **las decisiones abiertas**. Si esa lista no está vacía, no es una nota al pie: es una pregunta que se responde antes de commitear, y su respuesta entra en este mismo commit cuando cambie estos ficheros.
5. Pide confirmación explícita para ese commit o para los commits coherentes de la tarea actual.
6. Ejecuta exactamente el mensaje confirmado con `git commit -m` o, si el mensaje requiere un archivo, con `git commit -F <archivo>` en UTF-8 sin BOM.
7. Verifica y muestra SHA, mensaje y archivos del commit.

Si tras revisar el diff preparado descubres que el alcance debe cambiar, vuelve al paso 2 y pide una confirmación nueva. Un mensaje confirmado no se reescribe por conveniencia.

### Cierre sin cabos sueltos

Un cambio está listo para commitear cuando no queda nada que puedas resolver con la información disponible y nada que el usuario tenga que decidir para que el resultado sea coherente. En concreto:

- no dejes para después la sincronización de la documentación que describe lo que acabas de cambiar;
- no dejes para después una política del repositorio que contradice la regla nueva;
- no presentes como «pendiente de tu decisión» algo que podías haber preguntado antes de escribir;
- si el commit ya está hecho y aparece un cabo suelto, nómbralo como fallo de preparación y propón la reparación; no lo presentes como una decisión pendiente del usuario.

Un bloqueo externo real —una persona, un permiso, un dato que solo el usuario tiene— se declara **antes** del commit, con el estado del árbol preparado y sin commitear, para que no haya que completarlo después.

Detalle de convenciones, preparación segura y cierre en [commits y ramas](references/commits-and-branches.md).

## Etapas agrupadas y confirmación conjunta

Puedes proponer varias etapas en un solo plan —crear la rama, preparar archivos, commitear, integrar, borrar la rama, publicar— y recibir una única confirmación que las cubra todas.

- La confirmación enumera las etapas que autoriza. Lo que no enumere sigue sin autorizar.
- La autorización no se hereda a trabajo posterior, a otro conjunto de archivos ni a otro push.
- Si una etapa del plan falla o el estado cambia, las etapas restantes quedan sin autorizar y requieren un plan nuevo.

## Push y borrado de ramas

- Cualquier `push`, incluido el de una rama nueva, requiere confirmación previa específica y revalidación del estado justo antes de ejecutarlo.
- Tras integrar una rama de trabajo en `main`, si ya no hace falta, informa del nombre, del estado integrado y del comando propuesto, y pide confirmación antes de borrarla. Prefiere `git branch -d`, que se niega a borrar trabajo no integrado.
- No borres una rama con trabajo no integrado, ni local ni remota, sin autorización específica.

## Guardia de rama

Antes de preparar archivos o proponer un commit, comprueba la rama actual y el tamaño de la tarea.

- Rama actual `main`, tarea pequeña: permite preparar y commitear directamente, con el protocolo de commit y su confirmación. No requiere excepción documentada.
- Rama actual `main`, tarea normal o compleja: propón una rama corta desde `main` y pide confirmación para crearla antes de modificar archivos.
- Rama actual `develop`: bloquea el trabajo normal. Propón feature, fix, release o hotfix desde la base correcta.
- Rama actual `main` o `develop` y operación de integración: verifica origen permitido, destino permitido y evidencia de revisión cuando exista.
- Rama actual distinta de las permitidas para ese tipo de trabajo: no lo arregles con checkout, rebase o merge por iniciativa propia; explica la discrepancia y prepara un plan separado.

Lee [guardia de ramas](references/protected-branch-guard.md) en cualquier operación que empiece en `main` o `develop`.

## Plan y confirmación

Tras inspeccionar y clasificar, rellena la [plantilla de plan](assets/plan-template.md) y preséntala antes de cualquier cambio persistente. No improvises el formato: esos campos son los que el usuario necesita para decidir.

Después de la confirmación, ejecuta solo el plan. Antes de cada comando remoto incluido, revalida que el estado no haya cambiado. Si cambió, detente y solicita un nuevo plan.

## Verificación de cierre

Después de ejecutar, no digas «hecho» hasta comprobar y mostrar lo que corresponda al tamaño de la tarea:

1. estado de rama y árbol de trabajo;
2. SHA, mensaje y archivos del commit cuando exista;
3. ramas, relaciones de ascendencia e integración previstas, cuando haya integración; `scripts/verify-branch.sh <ancestro> <descendiente> [remoto]` comprueba la contención y sale con 0 si se cumple, 1 si no y 2 si el uso es inválido;
4. remoto, referencias o etiquetas publicadas cuando aplique;
5. validación acordada;
6. lista de comprobación aplicable en [verificación de flujo](references/flow-verification.md).

Para una tarea pequeña, los puntos 1, 2 y 5 suelen ser suficientes. Si falla una comprobación de una operación ya iniciada, el resultado es INCOMPLETO o NO VERIFICADO, no «terminado».

## Auditoría sin operación

Si el encargo solo inspecciona documentación, ramas e historial, no uses INCOMPLETO para describir un ciclo que aún no se ha iniciado. Separa:

- Política: DOCUMENTADA | NO DOCUMENTADA | CONTRADICTORIA.
- Estructura: PREPARADA | PARCIAL | AUSENTE.
- Evidencia operativa: DEMOSTRADA | PENDIENTE DE PRIMER CICLO | INSUFICIENTE.
- Incumplimiento activo: SÍ | NO | NO VERIFICABLE.

Para un repositorio con política documental clara, `main` estable y sin ramas auxiliares históricas, informa:

~~~text
Política: DOCUMENTADA
Estructura: PREPARADA
Evidencia operativa: PENDIENTE DE PRIMER CICLO
Incumplimiento activo: NO EVIDENCIADO
~~~

No confundas una falta de historial con una ejecución incompleta o un incumplimiento.

## Conflictos e integración

Antes de proponer merge, rebase o cherry-pick, lee [integración y conflictos](references/integration-and-conflicts.md). Muestra origen, destino, commits, posibilidad de fast-forward, riesgo de conflicto y efecto sobre la historia.

Ante conflicto, informa de archivos afectados y ofrece resolver, abortar o pausar. Una resolución es un plan nuevo y requiere confirmación.

## Resultado final

Cierra siempre con la [plantilla de resultado](assets/result-template.md). Si un campo no se puede rellenar con evidencia, ese es el hallazgo.
