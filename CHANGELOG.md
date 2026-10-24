# Changelog

Todos los cambios relevantes de este repositorio se documentan aquí.

El formato sigue [Keep a Changelog 1.1.0](https://keepachangelog.com/es-ES/1.1.0/) y el versionado sigue [Semantic Versioning 2.0.0](https://semver.org/lang/es/). Todavía no hay versiones publicadas: no existe ninguna etiqueta.

## [Unreleased]

### Añadido

- Skill `skill-creator` fijada en `.skills/`, la de terceros que se usa al crear skills nuevas: procedimiento, plantilla, lista de comprobación y validador de metadatos.
- Skill `git-flow-management`: gestión y verificación de operaciones Git con ceremonia proporcional al tamaño y al riesgo, guardia de ramas, plantillas de plan y de resultado, y el script `scripts/verify-branch.sh` para comprobar ascendencia y contención entre referencias.
- Skill `document-management-software`: gestión documental de un proyecto de software como conocimiento verificable, con inventario y responsabilidad por artefacto, grados de certeza por afirmación, reglas de redacción, auditoría de solo lectura, plantillas de plan e informe, y el script `scripts/doc-inventory.py` para detectar enlaces relativos rotos, documentos sin título, documentos sin contenido y encabezados duplicados.
- Skill `gherkin-scenario-authoring`: descubrimiento y escritura de archivos `.feature` — mapa de reglas, ejemplos y preguntas abiertas antes del primer escenario, referencias con las cuatro reglas convertidas en decisiones de redacción, plantilla de `.feature` que sale con código 0 del propio comprobador, plantilla del mapa con el vocabulario cerrado `MAPA LISTO | MAPA INCOMPLETO`, y la puerta mecánica de `tools/check-feature.py` sin atribuirse el veredicto de calidad, que sigue siendo de `gherkin-scenario-review`.
- Skill `gherkin-scenario-review`: revisión de archivos `.feature` contra las cuatro reglas de buen Gherkin, con puerta de alcance, veredicto cerrado por escenario (`APTO`, `APTO CON RESERVAS`, `NO APTO`), separación explícita entre hechos medibles y estimaciones del criterio, informe con reescritura propuesta por hallazgo, detección de stack con una referencia por stack (JS/TS, Python, Java, .NET y Go), plantillas de informe y de lista de comprobación, y el script `tools/check-feature.py` con once comprobaciones (seis deterministas y cinco candidatos), Gherkin en inglés y en español, umbrales `--max-steps` y `--max-outline-rows` y salidas `0`, `3` y `2`.
- Guía de buenas prácticas para crear skills, en `docs/best-practices-create-skills/README.md`.
- Documentación de la skill en `docs/git-flow-management/`: página principal, diagrama de flujo de trabajo y diagrama de arquitectura, cada uno con su especificación y su recibo de entrega.
- Documentación de la skill `skill-creator` en `docs/skill-creator/`: página principal, diagrama de flujo de trabajo y diagrama de arquitectura, cada uno con su especificación y su recibo de entrega.
- Documentación de la skill `document-management-software` en `docs/document-management-software/`: página principal, diagrama de flujo de trabajo y diagrama de arquitectura, cada uno con su especificación y su recibo de entrega.
- Documentación de la skill `gherkin-scenario-review` en `docs/gherkin-scenario-review/`: página principal con la tabla de los once códigos, diagrama del flujo (puerta de alcance, exit code del script, pasos por regla y confirmación o refutación de candidatos) y diagrama de arquitectura (paquete, frontera con `git-flow-management` y con SDD, y las referencias por stack), cada uno con su especificación y su recibo de entrega.
- Documentación de la skill `gherkin-scenario-authoring` en `docs/gherkin-scenario-authoring/`: página principal con las dos rutas del contrato, la tabla de los once códigos repartidos entre lo que se evita al escribir y lo que se resuelve en el paso 4, y el comprobador compartido; diagrama del flujo (puerta de alcance, mapa con su estado, parada por pregunta bloqueante, salida 0 / 3 / 2 y el bucle que vuelve al descubrimiento) y diagrama de arquitectura (paquete, CLI compartida fuera del paquete, y fronteras con la revisora, con el SDD y con el archivo producido), cada uno con su especificación y su recibo de entrega.
- Referencia normativa del repositorio: la especificación de [agentskills.io](https://agentskills.io/) como guía y referencia estricta, enlazada desde el `README.md`, la guía de buenas prácticas y la documentación de la skill `skill-creator`.
- Política de flujo del repositorio en `CONTRIBUTING.md`.
- `README.md` con la descripción del repositorio y su estructura.

### Modificado

- Comprobador de `.feature`: deja de vivir dentro del paquete de la skill de revisión y pasa a `tools/check-feature.py`, una sola copia compartida que invocan las dos skills de Gherkin, `gherkin-scenario-review` y `gherkin-scenario-authoring`, siempre desde la raíz del repositorio con `python tools/check-feature.py --path <archivo.feature>`. El comportamiento del script no cambia; lo que cambia es su propiedad: pasa de ser una pieza del paquete a ser una CLI compartida del repositorio. Se actualizan todas las referencias del paquete, de la documentación y de los diagramas.

- Skill `git-flow-management`: el flujo pasa a ser proporcional al tamaño y al riesgo de la tarea. Las tareas pequeñas admiten commit directo en `main`; las normales y complejas proponen rama corta. Todo commit se deja preparado en el stage con su mensaje Conventional Commits en inglés y se ejecuta solo tras confirmación explícita. El borrado de una rama ya integrada y cualquier `push` requieren su propia confirmación, y una confirmación no se reaprovecha para trabajo posterior. Git Flow deja de ser el modelo por defecto: se aplica solo si el repositorio lo declara.
- Skill `git-flow-management`: prohibido commitear con cabos sueltos. Antes de pedir la confirmación se hace un barrido de documentación, `CHANGELOG`, plantillas, referencias y políticas del repositorio; lo que requiera una decisión del usuario se pregunta antes del commit y entra en ese mismo commit. Un commit que obliga a un commit de corrección inmediata se informa como fallo de preparación, no como decisión pendiente.
- `CONTRIBUTING.md`: la excepción directa a `main` se sustituye por la regla de tamaño de la skill, con el barrido previo y la confirmación del commit como condiciones en todos los casos.

### Corregido

- Corregido el nombre de la carpeta de documentación de la skill, que tenía una errata. Los dos diagramas se re-entregaron para que sus recibos registren la ruta correcta.
- Recibos de los dos diagramas de `git-flow-management`: registraban el hash de una copia con CRLF del spec (8.067 y 6.072 bytes) frente a un spec guardado con LF (7.743 y 5.812), así que el recibo no correspondía a nada reproducible después de un checkout. Reentregados con `deliver` desde el árbol principal: el contenido de los dos HTML no cambió y los cuatro hashes del recibo casan con el disco. Añadida al `README.md` la segunda parte de la comprobación de reproducibilidad, la que `archify check --require-provenance` no hace.
