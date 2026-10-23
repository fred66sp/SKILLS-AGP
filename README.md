# SKILLS-AGP

Repositorio personal de skills para agentes, versionado para tener el mismo entorno de trabajo en todas mis máquinas. Las skills se escriben y se fijan para leerse como contratos: instrucciones verificables, referencias que se cargan solo cuando hacen falta y evidencia obligatoria antes de declarar algo terminado.

La especificación de [agentskills.io](https://agentskills.io/) es la guía y la referencia estricta de este repositorio. La estructura de directorios, los metadatos, la divulgación progresiva y los scripts de cada skill se contrastan contra ella, no contra una convención propia.

## Estructura

| Ruta | Qué contiene |
|---|---|
| `src/<skill>/` | Una skill por carpeta: `SKILL.md`, `references/`, `assets/`, `scripts/` |
| `docs/` | Guías y diagramas del repositorio |
| `tools/` | CLIs compartidas por más de una skill, ejecutadas desde la raíz del repositorio |
| `README.md` | Este fichero |
| `CONTRIBUTING.md` | Política de ramas, commits e integración |
| `CHANGELOG.md` | Historial de cambios |

Queda fuera de git por ser estado local de cada máquina: `.atl/`, `.codegraph/`, `.pi/`, además de los secretos que cubre el `.gitignore`. Sí se versiona `.skills/`, porque contiene las skills de terceros que necesita el entorno de trabajo.

## Skills disponibles

### `git-flow-management`

Convierte cualquier operación Git en un procedimiento proporcionado al tamaño y al riesgo: clasifica la tarea, trabaja directo en `main` cuando es pequeña y propone una rama corta cuando no lo es. Deja los cambios preparados en el stage con su mensaje Conventional Commits en inglés y no ejecuta el commit, el borrado de una rama ya integrada ni ningún `push` sin confirmación explícita. Cubre ramas, commits, PR, merges, releases, hotfixes, conflictos y recuperación.

Contrato completo: [`src/git-flow-management/SKILL.md`](src/git-flow-management/SKILL.md).

### `document-management-software`

Gestiona la documentación de un proyecto de software como conocimiento verificable: inventaría los artefactos existentes, decide la intervención mínima, clasifica la certeza de cada afirmación antes de redactarla y demuestra con comprobaciones que lo documentado sigue siendo cierto. Cubre README, PRD, SDD, arquitectura, ADR, API, instalación, operación, runbooks y documentación de features. Incluye el script `scripts/doc-inventory.py`, que detecta enlaces relativos rotos, documentos sin título, documentos sin contenido y encabezados duplicados.

Contrato completo: [`src/document-management-software/SKILL.md`](src/document-management-software/SKILL.md).

### `gherkin-scenario-review`

Revisa archivos `.feature` ya escritos contra las cuatro reglas de buen Gherkin: legibilidad sin contexto, un comportamiento por escenario, un ejemplo por clase de equivalencia y lenguaje consistente en tercera persona. Es una skill de revisión: no descubre comportamientos, no escribe escenarios ni automatiza, y no devuelve un veredicto de calidad sin la línea que lo sustenta. Separa el hecho medible de la estimación del criterio: seis comprobaciones son deterministas y cinco son candidatos que el revisor confirma o refuta. Usa la CLI compartida `tools/check-feature.py` (solo stdlib, Gherkin en inglés y en español, `# language: es`), con once códigos, umbrales `--max-steps` y `--max-outline-rows`, y salidas `0`, `3` y `2`; una referencia por stack (JS/TS, Python, Java, .NET y Go) para juzgar si un paso es automatizable y a qué capa pertenece; y dos fixtures propios como ejemplo de nivel y evidencia del script.

Contrato completo: [`src/gherkin-scenario-review/SKILL.md`](src/gherkin-scenario-review/SKILL.md).

## Skills en uso

Skills de terceros fijadas a una versión concreta, para que todas las máquinas trabajen con lo mismo. No son de autoría propia: no se editan aquí, se actualizan sustituyéndolas.

### `skill-creator`

Procedimiento para crear skills nuevas con la especificación agentskills.io: estructura de directorios, redacción de instrucciones procedimentales, optimización de metadatos para que la skill se descubra y una lista de comprobación. Incluye plantilla, checklist y un validador de metadatos.

Ruta: [`.skills/skill-creator/SKILL.md`](.skills/skill-creator/SKILL.md). Se usa al crear cualquier skill nueva en `src/`.

Documentación: [`docs/skill-creator/index.html`](docs/skill-creator/index.html).

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
- `docs/skill-creator/index.html` — página principal de la skill `skill-creator`.
- `docs/skill-creator/flujo-de-trabajo.html` — diagrama del flujo, del encargo al directorio validado.
- `docs/skill-creator/arquitectura.html` — diagrama del paquete, las puertas de validación y el directorio producido.
- `docs/gherkin-scenario-review/index.html` — página principal de la skill `gherkin-scenario-review`.
- `docs/gherkin-scenario-review/flujo-de-trabajo.html` — diagrama del flujo, del encargo al informe con veredicto cerrado.
- `docs/gherkin-scenario-review/arquitectura.html` — diagrama del paquete, la frontera con Git y con SDD, y las referencias por stack.

Los diagramas son artefactos de [archify](https://github.com/tt-a1i/archify) 3.2.0. Cada uno tiene su especificación (`*.json`) y su recibo de entrega (`*.delivery.json`) con el `sha256` del HTML y del spec. Para regenerarlos hace falta archify 3.2.0; el comando es el mismo en las cuatro carpetas, cambiando `<skill>` por `git-flow-management`, `skill-creator`, `document-management-software` o `gherkin-scenario-review`:

```bash
node <ruta-a-archify>/archify/bin/archify.mjs deliver workflow \
  docs/<skill>/flujo-de-trabajo.json \
  docs/<skill>/flujo-de-trabajo.html --quality showcase
```

`deliver` reescribe el recibo junto al HTML. La entrega es reproducible byte a byte: el mismo spec devuelve el mismo `sha256`.

## Regla de empaquetado

Dentro de `src/<skill>/` no se crean ficheros de documentación (`README.md`, `CHANGELOG.md`, guías de instalación): el paquete de una skill solo contiene lo que el agente necesita para ejecutarla. La documentación del repositorio vive en `docs/` y en la raíz. Ver [la guía](docs/best-practices-create-skills/README.md).

## Flujo de trabajo

Ver [`CONTRIBUTING.md`](CONTRIBUTING.md). En resumen: `main` como única rama de larga vida, ramas cortas por cambio e integración con `--no-ff`.

## Pendientes conocidos

- El repositorio todavía no tiene remoto.
