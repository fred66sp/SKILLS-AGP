# Changelog

Todos los cambios relevantes de este repositorio se documentan aquí.

El formato sigue [Keep a Changelog 1.1.0](https://keepachangelog.com/es-ES/1.1.0/) y el versionado sigue [Semantic Versioning 2.0.0](https://semver.org/lang/es/). Todavía no hay versiones publicadas: no existe ninguna etiqueta.

## [Unreleased]

### Añadido

- Skill `skill-creator` fijada en `.skills/`, la de terceros que se usa al crear skills nuevas: procedimiento, plantilla, lista de comprobación y validador de metadatos.
- Skill `git-flow-management`: gestión y verificación de operaciones Git con ceremonia proporcional al tamaño y al riesgo, guardia de ramas, plantillas de plan y de resultado, y el script `scripts/verify-branch.sh` para comprobar ascendencia y contención entre referencias.
- Skill `document-management-software`: gestión documental de un proyecto de software como conocimiento verificable, con inventario y responsabilidad por artefacto, grados de certeza por afirmación, reglas de redacción, auditoría de solo lectura, plantillas de plan e informe, y el script `scripts/doc-inventory.py` para detectar enlaces relativos rotos, documentos sin título, documentos sin contenido y encabezados duplicados.
- Guía de buenas prácticas para crear skills, en `docs/best-practices-create-skills/README.md`.
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

### Corregido

- Corregido el nombre de la carpeta de documentación de la skill, que tenía una errata. Los dos diagramas se re-entregaron para que sus recibos registren la ruta correcta.
