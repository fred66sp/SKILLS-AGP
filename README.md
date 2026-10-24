# SKILLS-AGP

Repositorio personal de skills para agentes, versionado para tener el mismo entorno de trabajo en todas mis máquinas. Las skills se escriben y se fijan para leerse como contratos: instrucciones verificables, referencias que se cargan solo cuando hacen falta y evidencia obligatoria antes de declarar algo terminado.

La especificación de [agentskills.io](https://agentskills.io/) es la guía y la referencia estricta de este repositorio. La estructura de directorios, los metadatos, la divulgación progresiva y los scripts de cada skill se contrastan contra ella, no contra una convención propia.

## De dónde viene

Este repositorio se inspira y se basa en dos fuentes externas:

- [github.com/agentskills](https://github.com/agentskills), la organización que mantiene la especificación de Agent Skills y sus guías de creación, que son la referencia estricta del párrafo anterior.
- [github.com/mgechev/skills-best-practices](https://github.com/mgechev/skills-best-practices), de donde procede la skill de terceros `skill-creator` —fijada a una revisión en la sección Skills en uso— y el modelo de empaquetado que siguen las skills propias: un `SKILL.md` corto con el procedimiento, `references/` que se cargan justo a tiempo, `assets/` para plantillas y `scripts/` para lo determinista.

## Estructura

| Ruta | Qué contiene |
|---|---|
| `src/<skill>/` | Una skill por carpeta: `SKILL.md`, `references/`, `assets/`, `scripts/` |
| `docs/` | Guías y diagramas del repositorio |
| `.skills/` | Skills de terceros fijadas a una versión, y enrutadores que hacen descubribles a las skills propias |
| `README.md` | Este fichero |
| `CONTRIBUTING.md` | Política de ramas, commits e integración |
| `CHANGELOG.md` | Historial de cambios |

Queda fuera de git por ser estado local de cada máquina: `.atl/`, `.codegraph/`, `.pi/`, además de los secretos que cubre el `.gitignore`. Sí se versiona `.skills/`, porque contiene las skills de terceros que necesita el entorno de trabajo y los enrutadores de las skills propias de `src/`.

## Skills disponibles

### `git-flow-management`

Convierte cualquier operación Git en un procedimiento proporcionado al tamaño y al riesgo: clasifica la tarea, trabaja directo en `main` cuando es pequeña y propone una rama corta cuando no lo es. Deja los cambios preparados en el stage con su mensaje Conventional Commits en inglés y no ejecuta el commit, el borrado de una rama ya integrada ni ningún `push` sin confirmación explícita. Cubre ramas, commits, PR, merges, releases, hotfixes, conflictos y recuperación.

Contrato completo: [`src/git-flow-management/SKILL.md`](src/git-flow-management/SKILL.md).

### `document-management-software`

Gestiona la documentación de un proyecto de software como conocimiento verificable: inventaría los artefactos existentes, decide la intervención mínima, clasifica la certeza de cada afirmación antes de redactarla y demuestra con comprobaciones que lo documentado sigue siendo cierto. Cubre README, PRD, SDD, arquitectura, ADR, API, instalación, operación, runbooks y documentación de features. Incluye el script `scripts/doc-inventory.py`, que detecta enlaces relativos rotos, documentos sin título, documentos sin contenido, encabezados duplicados y referencias vivas escritas como documentación: estado de Git, rutas de una máquina concreta y recuentos de artefactos que caducan.

Contrato completo: [`src/document-management-software/SKILL.md`](src/document-management-software/SKILL.md).

### `prd-cartographer`

Convierte una idea, una investigación o un concepto de producto en un PRD verificable, o revisa uno existente sin convertirlo en una especificación técnica. Separa hecho, decisión aprobada, inferencia, hipótesis, propuesta y desconocido; exige métricas con método de medida, alcance con exclusiones y criterios de aceptación observables; y entrega un estado de preparación explícito en lugar de un documento aparentemente completo. Incluye el Universal Idea Model, una plantilla de PRD, una plantilla de cierre y una puerta de calidad.

Contrato completo: [`src/prd-cartographer/SKILL.md`](src/prd-cartographer/SKILL.md).

## Skills en uso

Skills de terceros fijadas a una versión concreta, para que todas las máquinas trabajen con lo mismo. No son de autoría propia: no se editan aquí, se actualizan sustituyéndolas.

### `skill-creator`

Procedimiento para crear skills nuevas con la especificación agentskills.io: estructura de directorios, redacción de instrucciones procedimentales, optimización de metadatos para que la skill se descubra y una lista de comprobación. Incluye plantilla, checklist y un validador de metadatos.

Ruta: [`.skills/skill-creator/SKILL.md`](.skills/skill-creator/SKILL.md). Se usa al crear cualquier skill nueva en `src/`.

Procedencia: [`mgechev/skills-best-practices`](https://github.com/mgechev/skills-best-practices/tree/main/skill), directorio `skill/`, fijada en el commit [`a0bfa56`](https://github.com/mgechev/skills-best-practices/commit/a0bfa56bbcd676383f6ca57bb7e344d0856bc38e) del 2026-07-27. La copia es idéntica byte a byte a esa revisión. Actualizarla es sustituir el directorio por otra revisión y cambiar aquí el commit fijado; la fijación se comprueba con `git diff` contra esa revisión, no leyendo esta página.

Documentación: [`docs/skill-creator/index.html`](docs/skill-creator/index.html).

## Enrutadores de skills propias

`.skills/` no solo guarda terceros: cada skill propia que quiera ser descubrible por el agente tiene ahí un enrutador. Un enrutador es un `SKILL.md` mínimo con dos cosas: la metadatos de disparo (nombre igual al de la carpeta y descripción con los disparadores) y una instrucción para leer el contrato completo en `src/<skill>/SKILL.md` antes de trabajar. No copia invariantes, ni tablas, ni procedimientos: si enrutador y paquete difieren, manda el paquete.

| Enrutador | Fuente canónica |
|---|---|
| [`.skills/document-management-software/SKILL.md`](.skills/document-management-software/SKILL.md) | [`src/document-management-software/SKILL.md`](src/document-management-software/SKILL.md) |
| [`.skills/git-flow-management/SKILL.md`](.skills/git-flow-management/SKILL.md) | [`src/git-flow-management/SKILL.md`](src/git-flow-management/SKILL.md) |
| [`.skills/prd-cartographer/SKILL.md`](.skills/prd-cartographer/SKILL.md) | [`src/prd-cartographer/SKILL.md`](src/prd-cartographer/SKILL.md) |

La carpeta se registra como origen de skills en `.pi/settings.json` con `"skills": ["../.skills"]`. Como `.pi/` es estado local de cada máquina, ese registro se vuelve a escribir al clonar el repositorio en otra; sin él, `.skills/` no se descubre. Registrar la carpeta hace descubribles también a las skills de terceros que ya contiene.

## Cómo se usa una skill

1. Lee el `SKILL.md` de la skill como contrato, hasta el final.
2. Abre las `references/` solo cuando la operación concreta lo pida: cada una declara en su primera línea cuándo aplica.
3. Ejecuta los scripts de `scripts/` en lugar de reescribir su lógica.
4. No des una tarea por terminada sin la evidencia que el propio `SKILL.md` exige.

## Documentación

- `docs/best-practices-create-skills/README.md` — guía de buenas prácticas para crear skills.
- `docs/git-flow-management/index.html` — página principal de la skill `git-flow-management`.
- `docs/git-flow-management/flujo-de-trabajo.html` — diagrama del flujo, del encargo al resultado verificado.
- `docs/git-flow-management/arquitectura.html` — diagrama de las piezas del paquete y sus fronteras.
- `docs/document-management-software/index.html` — página principal de la skill `document-management-software`.
- `docs/document-management-software/flujo-de-trabajo.html` — diagrama del flujo, del encargo al cierre verificado.
- `docs/document-management-software/arquitectura.html` — diagrama del paquete, las puertas de la evidencia y la documentación que escribe.
- `docs/prd-cartographer/index.html` — página principal de la skill `prd-cartographer`.
- `docs/prd-cartographer/flujo-de-trabajo.html` — diagrama del flujo, del encargo al PRD revisado.
- `docs/prd-cartographer/arquitectura.html` — diagrama del paquete, la evidencia y la puerta de calidad.
- `docs/skill-creator/index.html` — página principal de la skill `skill-creator`.
- `docs/skill-creator/flujo-de-trabajo.html` — diagrama del flujo, del encargo al directorio validado.
- `docs/skill-creator/arquitectura.html` — diagrama del paquete, las puertas de validación y el directorio producido.

Los diagramas son artefactos de [archify](https://github.com/tt-a1i/archify) 3.2.0. Cada uno tiene su especificación (`*.json`) y su recibo de entrega (`*.delivery.json`) con el `sha256` del HTML y del spec. Para regenerarlos hace falta archify 3.2.0; el comando es el mismo en todas las carpetas de `docs/<skill>/`. El binario se invoca con la ruta de la copia local, instalada fuera del repositorio:

```bash
node <ruta-a-archify>/archify/bin/archify.mjs deliver workflow \
  docs/<skill>/flujo-de-trabajo.json \
  docs/<skill>/flujo-de-trabajo.html --quality showcase
```

`deliver` reescribe el recibo junto al HTML. La entrega es reproducible byte a byte: el mismo spec devuelve el mismo `sha256`.

La comprobación de esa reproducibilidad tiene dos partes, y la herramienta solo hace una. `archify check <html> --require-provenance` verifica el HTML contra su recibo; no compara el spec que el recibo dice haber leído con el spec que está en el repositorio. La segunda parte es manual: comparar el `sha256` y los `bytes` de `specification` con el hash real del `.json`, y los de `artifact` con el del `.html`. Sin esa segunda parte se cuelan recibos válidos sobre un spec que ya no es el guardado: basta con que el hash se calcule sobre una copia con CRLF mientras el repositorio guarda LF para que el recibo registre otros `bytes` bajo el mismo nombre. Antes de `deliver`, el spec debe estar en LF; se comprueba contando retornos de carro, y el resultado debe ser 0.

## Regla de empaquetado

Dentro de `src/<skill>/` no se crean ficheros de documentación (`README.md`, `CHANGELOG.md`, guías de instalación): el paquete de una skill solo contiene lo que el agente necesita para ejecutarla. La documentación del repositorio vive en `docs/` y en la raíz. Ver [la guía](docs/best-practices-create-skills/README.md).

## Flujo de trabajo

Ver [`CONTRIBUTING.md`](CONTRIBUTING.md). En resumen: `main` como única rama de larga vida, ramas cortas por cambio e integración con `--no-ff`. Crear un remoto, publicar o hacer `push` es una operación aparte, con su propio plan y su confirmación.
