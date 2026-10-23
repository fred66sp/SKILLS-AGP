---
name: git-flow-management
description: "Gestiona y verifica flujos de trabajo de Git seguros: impone la política Git Flow requerida en repositorios nuevos, conserva y verifica el flujo existente en repositorios ya establecidos, y cubre ramas, commits, PR, merges, releases, hotfixes, conflictos y recuperación. Úsala siempre que el agente vaya a realizar o planificar cualquier operación Git. Exige una aprobación explícita para cada plan concreto de operación persistente; no da por completado ningún paso de Git Flow sin haber verificado la ascendencia de ramas, los destinos de integración y el estado resultante. No la uses para operaciones ajenas a Git, ni para migrar a Git Flow un repositorio que ya declara otra política de ramas sin un encargo explícito de migración."
---

# Gestión de Git y Git Flow

Gestiona Git como un procedimiento verificable, no como una intención. Inspecciona, detecta la política aplicable, construye un plan concreto, solicita una confirmación, ejecuta únicamente lo aprobado y prueba que el resultado cumple el flujo.

## Invariantes obligatorias

1. Esta skill es obligatoria para cualquier operación Git. No continúes un flujo ignorando sus comprobaciones porque el usuario haya dicho “haz Git Flow”, “haz un commit” o “sube los cambios”.
2. No declares que se ha aplicado Git Flow, se ha integrado una rama, se ha publicado un cambio o se ha terminado una release sin verificarlo con comandos de solo lectura y mostrar el resultado.
3. La política Git documentada del repositorio prevalece sobre el Git Flow genérico. Para un proyecto nuevo, aplica Git Flow por defecto; para uno existente, detecta y respeta su política documentada o su práctica verificable, sin relajar nunca las protecciones genéricas contra operaciones destructivas ni migrarlo sin encargo explícito.
4. No ejecutes ningún cambio persistente sin una única confirmación explícita del plan exacto. Incluye add, commit, creación o borrado de rama, merge, rebase, cherry-pick, tag, push, fetch --prune y cambios remotos.
5. La confirmación no es global ni reutilizable. Una rama distinta, un conjunto de archivos distinto, un conflicto, un nuevo push o una discrepancia invalidan el plan.
6. No amplíes el alcance. No uses add global, no incluyas cambios ajenos, no incluyas no rastreados ni hagas amend salvo que el plan aprobado lo nombre expresamente.
7. No uses reset destructivo, clean, restauración desde otra revisión, borrado forzado de ramas, push forzado, borrado de etiquetas o ramas remotas, ni reescritura de historia salvo autorización específica para ese comando. Lee [recuperación y operaciones peligrosas](references/recovery-and-dangerous-operations.md).
8. Main y develop son ramas protegidas. Nunca prepares, confirmes ni ejecutes trabajo normal, commits de funcionalidad, correcciones o cambios de documentación mientras la rama actual sea main o develop, salvo una excepción directa a main documentada y plenamente probada conforme a la guardia. En otro caso, detente y propone crear la rama de trabajo correcta desde su base obligatoria.
9. Solo permite cambios en main o develop mediante una integración verificada de una rama permitida: feature o fix hacia develop; release o hotfix hacia main y después hacia develop; o las ramas y destinos que defina una política documentada. La excepción de bootstrap solo sirve para el commit inicial y la creación de develop.
10. Ante conflicto, estado inesperado, error o resultado diferente al plan, detente. No improvises una resolución; inspecciona y prepara un nuevo plan.

## Inspección obligatoria

La inspección es de solo lectura y no requiere confirmación. Antes de proponer una operación persistente, ejecuta y comunica al menos:

~~~bash
git rev-parse --show-toplevel
git status --short --branch
git branch --show-current
git branch -a -vv
git remote -v
git log --graph --oneline --decorate --all -n 30
~~~

Lee la documentación de contribución y de flujo si existe. Consulta [detección de política](references/workflow-detection.md) si hay dudas. Para operaciones acotadas —crear una rama, preparar archivos, revisar el diff preparado— lee [operaciones normales](references/normal-operations.md).

Clasifica el repositorio:

- Nuevo: todavía no tiene una política de ramas. Aplica Git Flow por defecto.
- Git Flow existente: hay evidencia documental o práctica verificable de main/master, develop y ramas de trabajo asociadas.
- Git Flow documentado, pendiente de evidencia operativa: existe una guía de flujo aplicable, pero el historial aún no demuestra una feature, release o hotfix completados. Trata la guía como política obligatoria para el siguiente trabajo, pero no declares que Git Flow ya está demostrado en la práctica.
- Git Flow local ligero documentado: ramas cortas `feature/*`, `fix/*`, `docs/*`, `refactor/*` o `chore/*` desde main; sin develop, release ni hotfix por defecto; integración no fast-forward en main.
- Política existente distinta: conserva su modelo; no inventes develop, Issues, PR, SemVer, etiquetas ni reglas de merge.
- Política desconocida: informa de la evidencia y pide decisión antes de una operación persistente.

## Política Git Flow por defecto para proyectos nuevos

| Tipo | Base obligatoria | Destino obligatorio | Propósito |
|---|---|---|---|
| main | — | — | Código listo para producción; releases etiquetadas |
| develop | main | — | Integración de la siguiente versión |
| feature/<id>-<slug> | develop | develop | Nueva funcionalidad |
| fix/<id>-<slug> | develop | develop | Corrección no productiva |
| release/<version> | develop | main y después develop | Preparación de release |
| hotfix/<id>-<slug> | main | main y después develop | Corrección urgente de producción |

Usa feature/<slug> o fix/<slug> si no existe sistema de incidencias. No inventes un identificador. No presupongas que está instalada la extensión git-flow: usa Git normal.

Para esta política:

- crea develop desde el commit inicial de main;
- crea cada rama de trabajo desde su base obligatoria y verifica la relación antes de trabajar;
- usa commits atómicos y Conventional Commits, según [commits y ramas](references/commits-and-branches.md);
- integra en ramas protegidas mediante PR cuando exista un mecanismo de revisión configurado; no hagas un merge local directo como sustituto sin explicarlo;
- usa merge no fast-forward al integrar en main o develop, salvo política documentada distinta;
- no hagas squash ni rebase de una rama compartida o publicada salvo regla documentada y aprobación explícita;
- conserva el back-merge de toda release y hotfix hacia develop.

Lee [operaciones Git Flow verificables](references/git-flow-operations.md) para cada tipo de rama. Lee [releases y versionado](references/releases-and-versioning.md) solo al preparar una release o hotfix.

## Plan, confirmación y ejecución

Tras inspeccionar, rellena la [plantilla de plan](assets/plan-template.md) y preséntala antes de cualquier cambio persistente. No improvises el formato: esos campos son los que el usuario necesita para decidir.

Después de la confirmación, ejecuta solo el plan. Antes de cada comando remoto incluido, revalida que el estado no haya cambiado. Si cambió, detente y solicita un nuevo plan.

## Guardia de rama protegida

Antes de preparar archivos o proponer un commit, comprueba la rama actual.

- Si es main y la operación es trabajo normal, comprueba primero si el repositorio documenta una excepción directa, estrecha y explícita. Permite un commit directo solo tras probar que cada ruta disponible y el diff completo cumplen todas las condiciones documentadas de trivialidad, aislamiento y reversibilidad, validar proporcionalmente el cambio y obtener una confirmación exacta posterior a la revisión para ese commit. Si la excepción falta, es ambigua o alguna condición no se cumple, bloquea el plan y exige una rama de trabajo permitida.
- Si es develop y la operación es trabajo normal, bloquea el plan. Informa de la rama protegida y propone únicamente crear feature, fix, release o hotfix desde la base correcta.
- Si es main o develop y la operación es una integración, verifica primero origen permitido, destino permitido y evidencia de revisión cuando exista.
- Si la rama actual no es una rama permitida para el tipo de trabajo, no intentes arreglarlo con checkout, rebase o merge por iniciativa propia: explica la discrepancia y prepara un plan separado.

Lee [guardia de ramas protegidas](references/protected-branch-guard.md) en cualquier operación que empiece en main o develop.

## Verificación de cierre

Después de ejecutar, no digas “hecho” hasta comprobar y mostrar:

1. estado de rama y árbol de trabajo;
2. SHA, mensaje y archivos del commit cuando exista;
3. ramas, relaciones de ascendencia e integración previstas; `scripts/verify-branch.sh <ancestro> <descendiente> [remoto]` comprueba la contención y sale con 0 si se cumple, 1 si no y 2 si el uso es inválido;
4. remoto, referencias o etiquetas publicadas cuando aplique;
5. validación acordada;
6. lista de comprobación aplicable en [verificación de flujo](references/flow-verification.md).

Si falla una comprobación de una operación que ya se ha iniciado, el resultado es INCOMPLETO o NO VERIFICADO, no “terminado”. Explica qué condición falta y no pases a la siguiente fase.

## Auditoría sin operación

Si el encargo solo inspecciona documentación, ramas e historial, no uses INCOMPLETO para describir un ciclo Git Flow que aún no se ha iniciado. Separa:

- Política: DOCUMENTADA | NO DOCUMENTADA | CONTRADICTORIA.
- Estructura: PREPARADA | PARCIAL | AUSENTE.
- Evidencia operativa: DEMOSTRADA | PENDIENTE DE PRIMER CICLO | INSUFICIENTE.
- Incumplimiento activo: SÍ | NO | NO VERIFICABLE.

Para un repositorio con main y develop en el mismo commit inicial, política documental clara y sin ramas auxiliares históricas, informa:

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
