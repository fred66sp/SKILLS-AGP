# Changelog

Todos los cambios relevantes de este repositorio se documentan aquí.

El formato sigue [Keep a Changelog 1.1.0](https://keepachangelog.com/es-ES/1.1.0/) y el versionado sigue [Semantic Versioning 2.0.0](https://semver.org/lang/es/). Todavía no hay versiones publicadas: no existe ninguna etiqueta.

## [Unreleased]

### Añadido

- Skill `skill-creator` fijada en `.skills/`, la de terceros que se usa al crear skills nuevas: procedimiento, plantilla, lista de comprobación y validador de metadatos.
- Skill `git-flow-management`: gestión y verificación de operaciones Git con ceremonia proporcional al tamaño y al riesgo, guardia de ramas, plantillas de plan y de resultado, y el script `scripts/verify-branch.sh` para comprobar ascendencia y contención entre referencias.
- Skill `document-management-software`: gestión documental de un proyecto de software como conocimiento verificable, con inventario y responsabilidad por artefacto, grados de certeza por afirmación, reglas de redacción, auditoría de solo lectura, plantillas de plan e informe, y el script `scripts/doc-inventory.py` para detectar enlaces relativos rotos, documentos sin título, documentos sin contenido y encabezados duplicados.
- Guía de buenas prácticas para crear skills, en `docs/best-practices-create-skills/README.md`.
- Enrutadores de las skills propias en `.skills/document-management-software/` y `.skills/git-flow-management/`: un `SKILL.md` mínimo con los metadatos de disparo y la instrucción de leer el contrato completo en `src/<skill>/SKILL.md`. No duplican invariantes ni procedimientos; la fuente canónica sigue siendo el paquete. El registro del origen de skills vive en `.pi/settings.json`, que es estado local de cada máquina.
- Documentación de la skill en `docs/git-flow-management/`: página principal, diagrama de flujo de trabajo y diagrama de arquitectura, cada uno con su especificación y su recibo de entrega.
- Documentación de la skill `skill-creator` en `docs/skill-creator/`: página principal, diagrama de flujo de trabajo y diagrama de arquitectura, cada uno con su especificación y su recibo de entrega.
- Documentación de la skill `document-management-software` en `docs/document-management-software/`: página principal, diagrama de flujo de trabajo y diagrama de arquitectura, cada uno con su especificación y su recibo de entrega.
- Referencia normativa del repositorio: la especificación de [agentskills.io](https://agentskills.io/) como guía y referencia estricta, enlazada desde el `README.md`, la guía de buenas prácticas y la documentación de la skill `skill-creator`.
- Política de flujo del repositorio en `CONTRIBUTING.md`.
- `README.md` con la descripción del repositorio y su estructura.

### Modificado


- Skill `git-flow-management`: el flujo pasa a ser proporcional al tamaño y al riesgo de la tarea. Las tareas pequeñas admiten commit directo en `main`; las normales y complejas proponen rama corta. Todo commit se deja preparado en el stage con su mensaje Conventional Commits en inglés y se ejecuta solo tras confirmación explícita. El borrado de una rama ya integrada y cualquier `push` requieren su propia confirmación, y una confirmación no se reaprovecha para trabajo posterior. Git Flow deja de ser el modelo por defecto: se aplica solo si el repositorio lo declara.
- Skill `git-flow-management`: prohibido commitear con cabos sueltos. Antes de pedir la confirmación se hace un barrido de documentación, `CHANGELOG`, plantillas, referencias y políticas del repositorio; lo que requiera una decisión del usuario se pregunta antes del commit y entra en ese mismo commit. Un commit que obliga a un commit de corrección inmediata se informa como fallo de preparación, no como decisión pendiente.
- `CONTRIBUTING.md`: la excepción directa a `main` se sustituye por la regla de tamaño de la skill, con el barrido previo y la confirmación del commit como condiciones en todos los casos.
- Skill `document-management-software`: las reglas de redacción de `references/authoring-rules.md` y la auditoría y el cierre de `references/audit-checklist.md` incorporan que el estado de la entrega no se documenta: ramas, commits, hashes y narraciones de corrección viven en Git y en el registro de trabajo, no en un documento de usuario. El registro de trabajo sí los conserva, porque es evidencia del encargo.
- `README.md`: la sección de documentación de los diagramas deja de contar el incidente de los recibos con sus cifras y deja de enumerar las carpetas que tienen diagramas, porque esa lista caducaba con la quinta skill; describe el modo de fallo en presente e indica la ruta local de la copia de archify.
- Páginas de skill en `docs/`: fuera las reglas CSS huérfanas de las tres páginas (`document-management-software`, `git-flow-management` y `skill-creator`). Se van ~9,9 KB de estilos que ya no describían ningún elemento del marcado: los badges de severidad sin uso, los bloques de estado de entrega, la rejilla de roles, `sr-only`, las listas `plain` y los comandos `cmd`/`sig`, incluidas sus apariciones dentro de `@media`, que se retira el bloque cuando queda vacío. El marcado no cambia y las clases que crean los scripts de la página (`copy`, `copied`, `active`) siguen con su regla.
- Documentación de la skill `skill-creator`: `docs/skill-creator/index.html` pasa de 15 secciones y 68.289 bytes a siete secciones en presente, sin el bloque que prometía completitud ni la sección de registro de entrega. La tabla de salidas del validador queda contrastada con el script: 0 con metadatos válidos, 1 con `NAME ERROR`, `DESCRIPTION ERROR` o `STYLE WARNING`, y éxito también cuando no llega `--description`. Se declaran dos incoherencias internas del paquete de terceros que no se corrigen porque no se edita: el `SKILL.md` nombra `STYLE ERROR` donde el script imprime `STYLE WARNING`, y la lista de carpetas de paso 2 no coincide con la de la checklist. La guía `docs/best-practices-create-skills/README.md` queda marcada como artefacto del repositorio.
- Documentación de la skill `git-flow-management`: `docs/git-flow-management/index.html` pasa de 17 secciones que copian las doce invariantes y las tablas de las referencias a siete secciones en presente que resumen y remiten al paquete. Fuera la promesa de que «todo lo que hay aquí sale de la propia skill» y fuera el estado de la entrega; la página, los diagramas y sus recibos quedan marcados como convenio de este repositorio.
- Documentación de la skill `document-management-software`: `docs/document-management-software/index.html` pasa de 14 secciones que duplican el paquete y narran la entrega, a 7 secciones en presente para quien llega por primera vez, con las preguntas cortas que ayudan a entender el alcance. Las reglas dejan de copiarse y se remite a `SKILL.md` y a las `references/` (una sola fuente canónica por afirmación); la evidencia de la entrega y sus hallazgos quedan en `odd/tasks/document-management-software.md`; y lo que es convención de este repositorio —la página, los diagramas de archify y sus recibos— va marcado como tal.

### Eliminado

- Skills `gherkin-scenario-review` y `gherkin-scenario-authoring`: los paquetes `src/gherkin-scenario-review/` y `src/gherkin-scenario-authoring/`, su documentación en `docs/` (página principal, los dos diagramas con sus especificaciones y sus recibos de entrega) y la CLI compartida `tools/check-feature.py`, que era la única ocupante de esa carpeta. El repositorio se queda con `git-flow-management`, `document-management-software` y la skill de terceros `skill-creator`.

### Corregido

- Corregido el nombre de la carpeta de documentación de la skill, que tenía una errata. Los dos diagramas se re-entregaron para que sus recibos registren la ruta correcta.
- Recibos de los dos diagramas de `git-flow-management`: registraban el hash de una copia con CRLF del spec (8.067 y 6.072 bytes) frente a un spec guardado con LF (7.743 y 5.812), así que el recibo no correspondía a nada reproducible después de un checkout. Reentregados con `deliver` desde el árbol principal: el contenido de los dos HTML no cambió y los cuatro hashes del recibo casan con el disco. Añadida al `README.md` la segunda parte de la comprobación de reproducibilidad, la que `archify check --require-provenance` no hace.
