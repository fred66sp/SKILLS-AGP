# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Autor (usuario principal).** Desarrollador que trabaja solo, en varias máquinas y sistemas —Linux y Windows con WSL— y quiere el mismo entorno de skills en todas. Usa los agentes de código a diario; el repositorio es su taller, no un producto comercial.
- **Agentes de código.** Consumidores de primera clase: descubren cada skill, leen su `SKILL.md` como contrato y ejecutan sus scripts. Para ellos la forma del repositorio importa tanto como su prosa.
- **Otros desarrolladores.** Llegan al catálogo y a las guías para entender el método y reutilizar ideas. Confirmado como audiencia; su permiso de reutilización no está decidido (ver más abajo).

El trabajo principal del autor es mantener skills fiables y verificables; el de quien lee la documentación es entender cómo se construye y se comprueba una skill, no recorrer un escaparate.

## Product Purpose

Repositorio personal de skills para agentes: cada skill enseña a un agente a hacer una tarea concreta con un contrato que incluye cuándo se activa y cómo se comprueba. Existe para que el mismo entorno de trabajo funcione en cualquier máquina y para que la documentación no se separe de lo que existe. El éxito es que una skill se pueda leer como contrato, que el repositorio se comporte igual en cualquier máquina y que nada se dé por terminado sin evidencia ejecutada.

## Positioning

**Contrato verificable, no documento plausible.** Cada `SKILL.md` fija qué hace la skill, cuándo se activa y cómo se comprueba; el repositorio cierra con puertas deterministas (`check-repo.py`, suites propias y CI). Un repositorio vecino puede copiar la prosa, pero no la evidencia ejecutada que la sostiene sin construir la misma disciplina. Esta afirmación debe sobrevivir a cualquier rediseño.

## Operating Context

- Se trabaja con OpenCode y sus agentes; las skills se descubren por enrutadores, no copiándolas al directorio global de cada máquina.
- Cada skill vive en `src/<skill>/`: `SKILL.md` con versión, `references/` de carga justo a tiempo, `assets/` y `scripts/` deterministas.
- Las skills de terceros se fijan a una revisión en `.skills/`, junto a los enrutadores de las propias.
- La puerta local es `python scripts/check-repo.py` más diez suites de `scripts/` y `src/*/scripts/`; la CI (`.github/workflows/validate.yml`) ejecuta lo mismo en cada push y pull request.
- La documentación es HTML estático en `docs/`: catálogo, una página por skill y diagramas. No hay build ni servidor de aplicación.
- El idioma de la documentación es castellano; los nombres de fichero y de directorio, inglés. Los ficheros de texto usan LF.
- El repositorio se versiona en git; el trabajo pendiente vive en `BACKLOG.md` y las decisiones de integración en `CONTRIBUTING.md`.

## Capabilities and Constraints

- 19 skills propias en `src/`, cada una con versión independiente en `metadata.version`, más `skill-creator` de terceros fijado en `.skills/`.
- Especificación de referencia: [agentskills.io](https://agentskills.io/), aplicada de forma estricta a estructura, metadatos y divulgación progresiva.
- La validación es determinista y local; un fallo debe indicar qué script falló.
- El sitio de documentación no descarga dependencias, tipografías ni scripts de terceros: HTML, CSS y JavaScript propios.
- La CI actual corre en `ubuntu-latest` con Python 3.12; la paridad con Windows es trabajo pendiente (`PBI-03`), no una garantía presente.
- **Decisión abierta:** no hay fichero `LICENSE`. Otros desarrolladores pueden leer el repositorio, pero la reutilización y redistribución no están autorizadas explícitamente. No inventar una licencia ni afirmar permisos.
- **Decisión abierta:** el alcance de publicación para terceros (solo lectura o reutilización) no está fijado.

## Brand Commitments

- Nombre: **SKILLS-AGP**, en mayúsculas.
- Voz: castellano directo, técnico y sin tics de escritura de IA; frases cortas, afirmaciones comprobables, nada de promesas de marketing.
- Identidad visual existente: verde de verificación (teal) como acento principal y azul como segundo acento; tema claro y oscuro; iconografía propia por familia de skill.
- Sin tipografías descargadas: se usan pilas del sistema.
- La cita de fuentes externas es explícita y con licencia; el texto de terceros no se copia.

## Evidence on Hand

- `README.md`: catálogo completo de skills, procedencia de cada familia, uso, validación y documentación.
- `CONTRIBUTING.md`: ramas, commits, versiones y publicación.
- `CHANGELOG.md`: historial de cambios por versión.
- `BACKLOG.md`: trabajo pendiente priorizado con evidencia y criterio de aceptación.
- `docs/index.html` y `docs/<skill>/index.html`: catálogo, páginas y diagramas con recibo.
- `src/*/SKILL.md` y sus `scripts/`: los contratos y sus puertas.
- `.opencode/context.md`: bitácora de misiones del repositorio.
- **Ausencias que no se deben rellenar:** no hay testimonios, clientes, métricas de uso, benchmarks ni casos de éxito. No hay LICENSE. No hay datos de adopción por terceros.

## Product Principles

1. **La evidencia manda.** Una afirmación sin comprobación ejecutada no cierra una tarea.
2. **La documentación es parte del producto.** Si el catálogo, el README o una página divergen de lo que existe, es un fallo, no una deuda estética.
3. **Igual en cualquier máquina.** Lo que funciona en una sesión debe funcionar en un clon limpio y en otro sistema.
4. **Divulgación progresiva.** El contrato se lee entero; las referencias se abren solo cuando la operación las pide.
5. **Mínimo que sostiene el contrato.** No se añade una skill, una dependencia ni una capa sin una necesidad medida.

## Accessibility & Inclusion

Sin estándar de accesibilidad confirmado como requisito de producto. La hoja de estilos declara contraste AA en tema claro y ofrece tema oscuro; trátese como compromiso de implementación existente, no como requisito confirmado.
