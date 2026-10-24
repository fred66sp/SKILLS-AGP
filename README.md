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
| `scripts/` | Validación local de estructura, rutas, recibos y pruebas de los scripts |
| `.github/workflows/` | CI que ejecuta la validación y las pruebas en cada push y pull request |
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

### `go-cli-ai-first`

Fija el contrato de una CLI en Go antes de implementarla, con el agente como consumidor principal: comandos y flags estables, `stdout` para el resultado y `stderr` para el diagnóstico, salida JSON con sobre de éxito y de error, códigos de salida acotados, modo no interactivo, `--dry-run`, `--yes` para operaciones destructivas, idempotencia, salida limitada, cancelación por señal y ayuda como mecanismo de descubrimiento. Incluye una ficha de comando y una referencia con la gramática, el sobre JSON y las reglas de compatibilidad.

Contrato completo: [`src/go-cli-ai-first/SKILL.md`](src/go-cli-ai-first/SKILL.md).

### `go-idiomatic-style`

Escribe y revisa Go idiomático para CLIs y servicios pequeños: formato con `gofmt`, nombres y paquetes claros, estructura mínima sin capas anticipadas, funciones con errores primero, datos con semántica explícita, interfaces pequeñas definidas por el consumidor y dependencias justificadas. La regla es la solución más simple que mantiene claridad, seguridad y capacidad de evolución; la concurrencia se delega a la skill de ciclo de vida.

Contrato completo: [`src/go-idiomatic-style/SKILL.md`](src/go-idiomatic-style/SKILL.md).

### `go-errors-and-lifecycle`

Convierte los errores en un contrato: los clasifica, los envuelve con contexto, los inspecciona con `errors.Is` y `errors.As`, los traduce a códigos de salida y a mensajes machine-readable en una sola frontera, y separa cancelación de timeout y de fallo interno. Cubre `context`, timeouts, señales, concurrencia con propietario y terminación, y cierre ordenado sin fugas.

Contrato completo: [`src/go-errors-and-lifecycle/SKILL.md`](src/go-errors-and-lifecycle/SKILL.md).

### `go-testing-and-verification`

Cierra el cambio con evidencia: pruebas unitarias y de tabla para lógica, golden files deterministas para formatos, pruebas de extremo a extremo del binario con `stdout`, `stderr` y código de salida separados, y casos de error, `--dry-run`, `--yes` y cancelación. Incluye la puerta `gofmt`, `build`, `test`, `vet`, `race` y `lint` en `scripts/verify-go.py`, con salida de texto o JSON, y una plantilla de informe.

Contrato completo: [`src/go-testing-and-verification/SKILL.md`](src/go-testing-and-verification/SKILL.md).

Las skills de Go sintetizan tres fuentes: el subagente [`golang-pro`](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/02-language-specialists/golang-pro.md), la colección [`cxuu/golang-skills`](https://github.com/cxuu/golang-skills/tree/main/skills), publicada con licencia Apache 2.0, y el contrato `go-style-contract` v0.2.0. No copian su texto: seleccionan y reorganizan las decisiones que sostienen una CLI automatizable, separan lo que cada skill posee y añaden el contrato de agente, el mapeo de errores a códigos de salida y la puerta de verificación.

| Necesidad de una CLI AI first | Skill | Fuentes que la sostienen |
|---|---|---|
| Contrato máquina estable, seguro y automatizable | `go-cli-ai-first` | `golang-pro` (CLI tools), `go-packages` (flags y `main`), contrato local (estructura y verificación) y criterio propio de agente |
| Código legible, mínimo y mantenible | `go-idiomatic-style` | Contrato local y las skills `go-style-core`, `go-naming`, `go-packages`, `go-declarations`, `go-functions`, `go-control-flow`, `go-data-structures`, `go-interfaces` y `go-defensive` |
| Fallos accionables y terminación limpia | `go-errors-and-lifecycle` | Contrato local y las skills `go-error-handling`, `go-context`, `go-concurrency`, `go-defensive` y `go-logging` |
| Confianza demostrada antes de cerrar | `go-testing-and-verification` | Contrato local y las skills `go-testing`, `go-linting` y `go-code-review` |

Quedan fuera como skills separadas los genéricos, las opciones funcionales, el logging, el rendimiento y la documentación de API: no cambian el contrato de una CLI y sus reglas esenciales viven dentro de las cuatro anteriores o se posponen hasta que exista una necesidad medida.

### Precedencia entre las skills de Go

Cada skill posee una materia y las demás la referencian: el contrato de la CLI es de `go-cli-ai-first`; el estilo, la estructura de paquetes y las dependencias son de `go-idiomatic-style`; los errores, `context`, la concurrencia y el cierre son de `go-errors-and-lifecycle`; las pruebas y la puerta son de `go-testing-and-verification`. La convención del proyecto donde se trabaja gana sobre la preferencia de estilo cuando no contradice el contrato de la CLI.

- **CLI mínima:** un `main.go` con el cableado y una función `run` testeable. El contrato de `go-cli-ai-first` se aplica completo y no se crean `cmd/`, `internal/` ni `pkg/` por anticipación.
- **CLI con varios comandos:** `cmd/<binario>/main.go`, `internal/cli` e `internal/app`. La estructura se justifica por el tamaño, no por la plantilla, y el contrato de la CLI no cambia.

## Skills en uso

Skills de terceros fijadas a una versión concreta, para que todas las máquinas trabajen con lo mismo. No son de autoría propia: no se editan aquí, se actualizan sustituyéndolas.

### `skill-creator`

Procedimiento para crear skills nuevas con la especificación agentskills.io: estructura de directorios, redacción de instrucciones procedimentales, optimización de metadatos para que la skill se descubra y una lista de comprobación. Incluye plantilla, checklist y un validador de metadatos.

Ruta: [`.skills/skill-creator/SKILL.md`](.skills/skill-creator/SKILL.md). Se usa al crear cualquier skill nueva en `src/`.

Procedencia: [`mgechev/skills-best-practices`](https://github.com/mgechev/skills-best-practices/tree/main/skill), directorio `skill/`, fijada en el commit [`a0bfa56`](https://github.com/mgechev/skills-best-practices/commit/a0bfa56bbcd676383f6ca57bb7e344d0856bc38e) del 2026-07-27. La copia es idéntica byte a byte a esa revisión. Actualizarla es sustituir el directorio por otra revisión y cambiar aquí el commit fijado; la fijación se comprueba con `git diff` contra esa revisión, no leyendo esta página.

Documentación: [`docs/skill-creator/index.html`](docs/skill-creator/index.html).

## Enrutadores de skills propias

`.skills/` no solo guarda terceros: cada skill propia que quiera ser descubrible por el agente tiene ahí un enrutador. Un enrutador es un `SKILL.md` mínimo con dos cosas: los metadatos de disparo (nombre igual al de la carpeta y descripción con los disparadores) y una instrucción para leer el contrato completo en `../../src/<skill>/SKILL.md` antes de trabajar. La ruta es relativa a la carpeta del enrutador, porque Pi resuelve las rutas relativas contra el directorio del `SKILL.md`, no contra el directorio de trabajo. No copia invariantes, ni tablas, ni procedimientos: si enrutador y paquete difieren, manda el paquete.

| Enrutador | Fuente canónica |
|---|---|
| [`.skills/document-management-software/SKILL.md`](.skills/document-management-software/SKILL.md) | [`src/document-management-software/SKILL.md`](src/document-management-software/SKILL.md) |
| [`.skills/git-flow-management/SKILL.md`](.skills/git-flow-management/SKILL.md) | [`src/git-flow-management/SKILL.md`](src/git-flow-management/SKILL.md) |
| [`.skills/prd-cartographer/SKILL.md`](.skills/prd-cartographer/SKILL.md) | [`src/prd-cartographer/SKILL.md`](src/prd-cartographer/SKILL.md) |
| [`.skills/go-cli-ai-first/SKILL.md`](.skills/go-cli-ai-first/SKILL.md) | [`src/go-cli-ai-first/SKILL.md`](src/go-cli-ai-first/SKILL.md) |
| [`.skills/go-idiomatic-style/SKILL.md`](.skills/go-idiomatic-style/SKILL.md) | [`src/go-idiomatic-style/SKILL.md`](src/go-idiomatic-style/SKILL.md) |
| [`.skills/go-errors-and-lifecycle/SKILL.md`](.skills/go-errors-and-lifecycle/SKILL.md) | [`src/go-errors-and-lifecycle/SKILL.md`](src/go-errors-and-lifecycle/SKILL.md) |
| [`.skills/go-testing-and-verification/SKILL.md`](.skills/go-testing-and-verification/SKILL.md) | [`src/go-testing-and-verification/SKILL.md`](src/go-testing-and-verification/SKILL.md) |

`python scripts/check-repo.py` comprueba que cada enrutador resuelve su contrato desde su propio directorio, que el nombre del enrutador y el del contrato coinciden y que no hay enrutadores huérfanos ni skills canónicas sin enrutador.

La carpeta se registra como origen de skills en `.pi/settings.json` con `"skills": ["../.skills"]`; la ruta es relativa a `.pi/`, no al directorio de trabajo. Como `.pi/` es estado local de cada máquina, al clonar el repositorio en otra hay que volver a crear `.pi/settings.json` con esa clave (y las demás preferencias locales); sin ella, `.skills/` no se descubre. La clave mínima es:

```json
{
  "skills": ["../.skills"]
}
```

Registrar la carpeta hace descubribles también a las skills de terceros que ya contiene.

## Cómo se usa una skill

1. Lee el `SKILL.md` de la skill como contrato, hasta el final.
2. Abre las `references/` solo cuando la operación concreta lo pida: cada una declara en su primera línea cuándo aplica.
3. Ejecuta los scripts de `scripts/` en lugar de reescribir su lógica.
4. No des una tarea por terminada sin la evidencia que el propio `SKILL.md` exige.

## Validación

La misma comprobación que ejecuta la CI se ejecuta en local:

```bash
python scripts/check-repo.py
python scripts/test-check-repo.py
python src/document-management-software/scripts/test-doc-inventory.py
python src/go-testing-and-verification/scripts/test-verify-go.py
```

`check-repo.py` valida metadatos, estructura, enrutadores, enlaces Markdown, recibos de los diagramas y sintaxis de los scripts. Las pruebas unitarias se ejecutan aparte para que un fallo indique qué script falló. La CI (`.github/workflows/validate.yml`) ejecuta los mismos comandos en cada push y pull request.

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
- `docs/go-cli-ai-first/index.html` — página principal de la skill `go-cli-ai-first`.
- `docs/go-cli-ai-first/flujo-de-trabajo.html` — diagrama del flujo, del encargo a la CLI verificada.
- `docs/go-cli-ai-first/arquitectura.html` — diagrama del paquete, la frontera de la CLI y el programa.
- `docs/go-idiomatic-style/index.html` — página principal de la skill `go-idiomatic-style`.
- `docs/go-idiomatic-style/flujo-de-trabajo.html` — diagrama del flujo, de la inspección al diff revisado.
- `docs/go-idiomatic-style/arquitectura.html` — diagrama del paquete, las reglas de estilo y el proyecto.
- `docs/go-errors-and-lifecycle/index.html` — página principal de la skill `go-errors-and-lifecycle`.
- `docs/go-errors-and-lifecycle/flujo-de-trabajo.html` — diagrama del flujo, del fallo al cierre verificado.
- `docs/go-errors-and-lifecycle/arquitectura.html` — diagrama del paquete, la frontera del error y los recursos.
- `docs/go-testing-and-verification/index.html` — página principal de la skill `go-testing-and-verification`.
- `docs/go-testing-and-verification/flujo-de-trabajo.html` — diagrama del flujo, del cambio a la evidencia ejecutada.
- `docs/go-testing-and-verification/arquitectura.html` — diagrama del paquete, las capas de prueba y la puerta.
- `docs/skill-creator/index.html` — página principal de la skill `skill-creator`.
- `docs/skill-creator/flujo-de-trabajo.html` — diagrama del flujo, del encargo al directorio validado.
- `docs/skill-creator/arquitectura.html` — diagrama del paquete, las puertas de validación y el directorio producido.

Los diagramas son artefactos de [archify](https://github.com/tt-a1i/archify) 3.2.0. Cada uno tiene su especificación (`*.json`) y su recibo de entrega (`*.delivery.json`) con el `sha256` del HTML y del spec. Para regenerarlos hace falta archify 3.2.0 y el checkout local en `archify/`, ignorado por Git, con los ajustes de ancho descritos en `archify/LOCAL-PATCH.md`; el comando es el mismo en todas las carpetas de `docs/<skill>/`:

```bash
node archify/archify/bin/archify.mjs deliver workflow \
  docs/<skill>/flujo-de-trabajo.json \
  docs/<skill>/flujo-de-trabajo.html --quality showcase
```

`deliver` reescribe el recibo junto al HTML. Con ese checkout, la entrega es reproducible byte a byte: el mismo spec devuelve el mismo `sha256`.

La comprobación de esa reproducibilidad tiene dos niveles. `archify check <html> --require-provenance` verifica el HTML contra su recibo. `python scripts/check-repo.py` compara el `sha256` y los `bytes` de `specification` con el `.json` y los de `artifact` con el `.html`, y exige que el spec esté en LF. El segundo nivel no necesita Archify y detecta el recibo válido sobre un spec que ya no es el guardado: basta con que el hash se calcule sobre una copia con CRLF mientras el repositorio guarda LF para que el recibo registre otros `bytes` bajo el mismo nombre. Antes de `deliver`, el spec debe estar en LF; se comprueba contando retornos de carro, y el resultado debe ser 0.

Regenera solo el diagrama cuyo `.json` haya cambiado; los demás HTML y recibos no se tocan. Un cambio de texto en una página `index.html` no obliga a regenerar diagramas. Si no se dispone del checkout local de Archify, la verificación de recibos sigue siendo posible; la regeneración, no.

## Regla de empaquetado

Dentro de `src/<skill>/` no se crean ficheros de documentación (`README.md`, `CHANGELOG.md`, guías de instalación): el paquete de una skill solo contiene lo que el agente necesita para ejecutarla. La documentación del repositorio vive en `docs/` y en la raíz. Ver [la guía](docs/best-practices-create-skills/README.md).

## Flujo de trabajo

Ver [`CONTRIBUTING.md`](CONTRIBUTING.md). En resumen: `main` como única rama de larga vida, ramas cortas por cambio e integración con `--no-ff`. Crear un remoto, publicar o hacer `push` es una operación aparte, con su propio plan y su confirmación.
