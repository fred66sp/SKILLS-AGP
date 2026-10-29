# SKILLS-AGP

Repositorio personal de skills para agentes. Lo versiono para tener el mismo entorno de trabajo en todas mis máquinas.

Cada skill se lee como un contrato. El `SKILL.md` fija qué hace, cuándo se activa y cómo se comprueba; las referencias se abren solo cuando la operación las pide, y nada se da por terminado sin evidencia ejecutada.

La especificación de [agentskills.io](https://agentskills.io/) es la guía y la referencia estricta de este repositorio. La estructura de directorios, los metadatos, la divulgación progresiva y los scripts de cada skill se contrastan contra ella, no contra una convención propia.

## De dónde viene

Este repositorio se inspira y se basa en dos fuentes externas:

- [github.com/agentskills](https://github.com/agentskills), la organización que mantiene la especificación de Agent Skills y sus guías de creación, que son la referencia estricta del párrafo anterior.
- [github.com/mgechev/skills-best-practices](https://github.com/mgechev/skills-best-practices), de donde procede la skill de terceros `skill-creator` —fijada a una revisión en la sección Skills en uso— y el modelo de empaquetado que siguen las skills propias: un `SKILL.md` corto con el procedimiento, `references/` que se cargan justo a tiempo, `assets/` para plantillas y `scripts/` para lo determinista.

## Estructura

| Ruta | Qué contiene |
|---|---|
| `src/<skill>/` | Una skill por carpeta: `SKILL.md` con su versión, `references/`, `assets/`, `scripts/` |
| `docs/` | Catálogo de skills, guías y diagramas del repositorio |
| `.skills/` | Skills de terceros fijadas a una versión, y enrutadores que hacen descubribles a las skills propias |
| `scripts/` | Validación local de estructura, rutas, recibos, versiones y pruebas de los scripts |
| `.github/workflows/` | CI que ejecuta la validación y las pruebas en cada push y pull request |
| `README.md` | Este fichero |
| `CONTRIBUTING.md` | Política de ramas, commits e integración |
| `CHANGELOG.md` | Historial de cambios |
| `BACKLOG.md` | Trabajo pendiente priorizado: qué viene después, con su evidencia y su criterio de aceptación |
| `PRODUCT.md` | Contexto de producto que consume el trabajo de diseño: usuarios, propósito, límites y ausencias declaradas |
| `DESIGN.md` | Sistema visual del catálogo y de las páginas de skill: tokens, tipografía, componentes y reglas |
| `.gitattributes` | Fin de línea del repositorio: todo texto en LF, sin depender de la máquina que clona |
| `opencode.json` | Configuración compartida de OpenCode: los agentes y el modelo de cada uno |

Queda fuera de git por ser estado local de cada máquina: `.atl/`, `.codegraph/`, `.engram/`, `.impeccable/`, `.pi/`, además de los secretos que cubre el `.gitignore`. Sí se versiona `.skills/`, porque contiene las skills de terceros que necesita el entorno de trabajo y los enrutadores de las skills propias de `src/`.

## Skills disponibles

### `git-flow-management`

Clasifica cada operación Git por tamaño y riesgo antes de tocarla. Una tarea pequeña va directa a `main`; una normal o compleja pide rama corta. Los cambios quedan en el stage con su mensaje Conventional Commits en inglés, y el commit, el borrado de una rama ya integrada y cualquier `push` esperan confirmación explícita. Cubre ramas, commits, PR, merges, releases, hotfixes, conflictos y recuperación.

Contrato completo: [`src/git-flow-management/SKILL.md`](src/git-flow-management/SKILL.md).

### `document-management-software`

Trata la documentación como conocimiento que se puede comprobar. Inventaría lo que existe, elige la intervención mínima y clasifica la certeza de cada afirmación antes de escribirla; después demuestra con comprobaciones que lo documentado sigue siendo cierto. Cubre README, PRD, SDD, arquitectura, ADR, API, instalación, operación, runbooks y documentación de features. El script `scripts/doc-inventory.py` detecta enlaces relativos rotos, documentos sin título o sin contenido, encabezados duplicados y referencias vivas escritas como documentación: estado de Git, rutas de una máquina concreta y recuentos de artefactos que caducan.

Contrato completo: [`src/document-management-software/SKILL.md`](src/document-management-software/SKILL.md).

### `document-redactor`

Edita la prosa en castellano sin tocar los hechos. Delimita la operación, fija el registro y congela cifras, citas y enlaces antes de reescribir; luego quita los tics de la escritura de IA por racimos, conserva la cobertura y reconstruye el ritmo. La voz solo entra en los registros que la admiten, y la tipografía española se corrige siempre. Cierra con una rúbrica de seis dimensiones y con `scripts/redactor.py check`, que separa defectos deterministas de señales que exigen criterio y devuelve texto o JSON. Sirve para artículos, guías, README, notas de versión, correos y propuestas; no decide qué documentos debe tener un proyecto ni redacta la estructura de un PRD o un ADR.

Contrato completo: [`src/document-redactor/SKILL.md`](src/document-redactor/SKILL.md).

Precedencia con las demás skills documentales: `document-management-software` decide qué artefactos existen, si siguen siendo ciertos y qué afirmación está respaldada; `prd-cartographer` y `adr-software` poseen la estructura de sus documentos. `document-redactor` posee solo la prosa. Para editar el texto de un PRD o un ADR se aplica primero el contrato de su skill y después el registro y la forma de esta.

### `prd-cartographer`

Convierte una idea, una investigación o un concepto de producto en un PRD verificable, o revisa uno existente sin convertirlo en una especificación técnica. Separa hecho, decisión aprobada, inferencia, hipótesis, propuesta y desconocido. Pide métricas con método de medida, alcance con exclusiones y criterios de aceptación observables, y entrega un estado de preparación explícito en vez de un documento que solo lo parece. Incluye el Universal Idea Model, una plantilla de PRD, una plantilla de cierre y una puerta de calidad.

Contrato completo: [`src/prd-cartographer/SKILL.md`](src/prd-cartographer/SKILL.md).

### `adr-software`

Crea y mantiene Architecture Decision Records con contrato de agente. Antes de escribir decide si la decisión merece un ADR; si lo merece, captura la intención sin interrogar y redacta contexto, decisión, no-goals, alternativas, consecuencias y verificación en plantilla simple o MADR. Una puerta determinista comprueba frontmatter, secciones, marcadores, índice, nombres y sustituciones bidireccionales. Cubre crear, revisar, aceptar, rechazar, deprecar, sustituir e indexar. No diseña la arquitectura ni sustituye al PRD.

Contrato completo: [`src/adr-software/SKILL.md`](src/adr-software/SKILL.md).

### `go-cli-ai-first`

Fija el contrato de una CLI en Go antes de implementarla. El consumidor principal es un agente, así que los comandos y las flags no cambian sin motivo: `stdout` lleva el resultado, `stderr` el diagnóstico y el JSON de éxito o de error tiene un sobre estable. Los códigos de salida son acotados; el modo no interactivo, `--dry-run` y `--yes` cubren la automatización y lo destructivo. Añade idempotencia, salida limitada, cancelación por señal y ayuda como mecanismo de descubrimiento. Incluye una ficha de comando y una referencia con la gramática, el sobre JSON y las reglas de compatibilidad.

Contrato completo: [`src/go-cli-ai-first/SKILL.md`](src/go-cli-ai-first/SKILL.md).

### `go-idiomatic-style`

Escribe y revisa Go idiomático para CLIs y servicios pequeños. `gofmt` manda en el formato; los nombres y los paquetes dicen lo que hacen, la estructura no anticipa capas y las funciones devuelven el error primero. Los datos llevan su semántica explícita, las interfaces son pequeñas y las define quien las consume, y cada dependencia se justifica. La regla de fondo es la solución más simple que mantiene claridad, seguridad y capacidad de evolución. La concurrencia queda en la skill de ciclo de vida.

Contrato completo: [`src/go-idiomatic-style/SKILL.md`](src/go-idiomatic-style/SKILL.md).

### `go-errors-and-lifecycle`

Trata los errores como un contrato. Se clasifican, se envuelven con contexto y se inspeccionan con `errors.Is` y `errors.As`; en una sola frontera se traducen a códigos de salida y a mensajes machine-readable. Cancelación, timeout y fallo interno son cosas distintas y se separan. Cubre `context`, timeouts, señales, concurrencia con propietario, terminación y cierre ordenado sin fugas.

Contrato completo: [`src/go-errors-and-lifecycle/SKILL.md`](src/go-errors-and-lifecycle/SKILL.md).

### `go-testing-and-verification`

Cierra el cambio con evidencia ejecutada. La lógica va en pruebas unitarias y de tabla; los formatos, en golden files deterministas; el binario se prueba de extremo a extremo con `stdout`, `stderr` y código de salida separados. Los casos de error, `--dry-run`, `--yes` y la cancelación también tienen prueba. La puerta `gofmt`, `build`, `test`, `vet`, `race` y `lint` vive en `scripts/verify-go.py`, con salida de texto o JSON, y hay una plantilla de informe.

Contrato completo: [`src/go-testing-and-verification/SKILL.md`](src/go-testing-and-verification/SKILL.md).

Las skills de Go sintetizan tres fuentes: el subagente [`golang-pro`](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/02-language-specialists/golang-pro.md), la colección [`cxuu/golang-skills`](https://github.com/cxuu/golang-skills/tree/main/skills), publicada con licencia Apache 2.0, y el contrato `go-style-contract` v0.2.0. No copian su texto: eligen y reorganizan las decisiones que sostienen una CLI automatizable, separan lo que posee cada skill y añaden el contrato de agente, el mapeo de errores a códigos y la puerta.

| Necesidad de una CLI AI first | Skill | Fuentes que la sostienen |
|---|---|---|
| Contrato máquina estable, seguro y automatizable | `go-cli-ai-first` | `golang-pro` (CLI tools), `go-packages` (flags y `main`), contrato local (estructura y verificación) y criterio propio de agente |
| Código legible, mínimo y mantenible | `go-idiomatic-style` | Contrato local y las skills `go-style-core`, `go-naming`, `go-packages`, `go-declarations`, `go-functions`, `go-control-flow`, `go-data-structures`, `go-interfaces` y `go-defensive` |
| Fallos accionables y terminación limpia | `go-errors-and-lifecycle` | Contrato local y las skills `go-error-handling`, `go-context`, `go-concurrency`, `go-defensive` y `go-logging` |
| Confianza demostrada antes de cerrar | `go-testing-and-verification` | Contrato local y las skills `go-testing`, `go-linting` y `go-code-review` |

Los genéricos, las opciones funcionales, el logging, el rendimiento y la documentación de API no tienen skill propia. No cambian el contrato de una CLI, y sus reglas caben en las cuatro anteriores o esperan a una necesidad medida.

### `typescript-idiomatic-style`

Diseña y escribe TypeScript type-first para librerías, servicios y CLIs. El `tsconfig` es estricto y la API usa uniones discriminadas, tipos branded, type guards y genéricos solo cuando hacen falta; `satisfies` y los objetos const sustituyen al `enum`. Los módulos y los `exports` se declaran, las dependencias se justifican y las project references solo entran con una medición del build. Incluye el contrato de una CLI con citty, `@clack/prompts`, completion perezosa, `stdout` y `stderr` separados, modo no interactivo y empaquetado.

Contrato completo: [`src/typescript-idiomatic-style/SKILL.md`](src/typescript-idiomatic-style/SKILL.md).

### `typescript-testing-and-verification`

Cierra el cambio con evidencia en TypeScript. Toda frontera externa se valida con Zod 4 y los tipos se derivan del esquema; `tsc --noEmit` comprueba el resto. Las pruebas cubren unidad, esquema, integración y la CLI de extremo a extremo, con salida determinista y arranque con variables de entorno inválidas. La puerta `scripts/verify-ts.py` detecta el gestor de paquetes, ejecuta typecheck y, cuando se piden, los scripts `lint`, `test` y `build` del proyecto; devuelve texto o JSON.

Contrato completo: [`src/typescript-testing-and-verification/SKILL.md`](src/typescript-testing-and-verification/SKILL.md).

Las skills de TypeScript sintetizan cuatro fuentes: [`typescript-pro`](https://www.skillsdirectory.com/skills/monoes-typescript-pro), de monoes, publicado con licencia MIT y procedente de [`Jeffallan/claude-skills`](https://github.com/Jeffallan/claude-skills/tree/882ef55e377dbf9a4dbe496bb41ac6ccd0e555cf/skills/typescript-pro); [`typescript-patterns`](https://opencodeskills.dev/skills/code-quality/typescript-patterns/) 1.0.1 y [`zod-validation`](https://opencodeskills.dev/skills/code-quality/zod-validation/) 1.0.0, ambas de OpenCode Skills con licencia MIT declarada; y [`cli-building`](https://www.typingmind.com/skills/damusix-cli-building), de damusix, fijada en la [revisión de damusix](https://github.com/damusix/skills/tree/efa8de4096f167cc896af6b869412def1614ccf0/cli-building), cuya ficha y repositorio no declaran licencia y se usa solo como referencia de decisiones. El texto no se copia: se eligen y reorganizan las reglas que sostienen tipos verificables, una CLI automatizable y una frontera validada; encima van el contrato de agente, el reparto de responsabilidades y la puerta.

| Necesidad | Skill | Fuentes que la sostienen |
|---|---|---|
| Tipos que impiden estados inválidos y una CLI mantenible | `typescript-idiomatic-style` | `typescript-pro`, `typescript-patterns`, `cli-building` y criterio propio de agente |
| Fronteras validadas y confianza demostrada antes de cerrar | `typescript-testing-and-verification` | `zod-validation`, `typescript-patterns`, `cli-building` y criterio propio de agente |

Los frameworks de UI, el rendimiento de build, la estrategia de errores y la publicación tampoco tienen skill propia: no cambian el contrato de tipos ni la verificación, y sus reglas caben en las dos anteriores o esperan a una necesidad medida.

### Precedencia entre las skills de TypeScript

El reparto es claro: el diseño de tipos, los módulos, las dependencias y la forma de la CLI pertenecen a `typescript-idiomatic-style`; la validación en la frontera, las pruebas y la puerta, a `typescript-testing-and-verification`. Si la convención del proyecto choca con la preferencia de estilo, manda la convención, salvo que contradiga el lenguaje o el contrato de la CLI.

- **Proyecto con otro validador:** no se añade Zod. Se mantiene el contrato de validar toda frontera y se usa la herramienta existente.
- **CLI de un solo fichero:** es válida. La estructura `cli/` solo se propone cuando el número de comandos o el tamaño la justifican.
- **Proyecto sin `typecheck`:** la puerta ejecuta la copia local de TypeScript con `--noEmit`; si no existe, declara el bloqueo en lugar de descargar una versión distinta.

### `javascript-idiomatic-style`

Escribe y revisa JavaScript vanilla para navegador y Node. Antes de elegir sintaxis se declara el baseline de cada objetivo, y se prefiere la construcción que rechaza a la que convierte (`===`, `??`, `Number()`). La asincronía se modela con rechazos observados y `AbortSignal`; los módulos se resuelven en ESM y CJS; el DOM se construye con nodos y `textContent`; la CLI de Node usa builtins y `parseArgs`. Un adaptador nombrado es la única pieza que sabe en qué plataforma corre el código: lo demás vive en la intersección de los dos baselines.

Contrato completo: [`src/javascript-idiomatic-style/SKILL.md`](src/javascript-idiomatic-style/SKILL.md).

### `javascript-testing-and-verification`

Demuestra el comportamiento del JavaScript vanilla sin añadir un framework. Elige la capa de prueba más pequeña y escribe los casos con `node:test` y `node:assert/strict`. El DOM y los eventos se prueban en una página de navegador o con el entorno que el proyecto ya tenga; la red, el almacenamiento y el reloj se simulan; el proceso se comprueba con `argv`, `env` y `stdin` controlados. La puerta `scripts/verify-js.py` pasa `node --check` a todos los archivos, ejecuta el script `test` del proyecto o `node --test`, informa de la versión de Node frente a `engines` y devuelve texto o JSON.

Contrato completo: [`src/javascript-testing-and-verification/SKILL.md`](src/javascript-testing-and-verification/SKILL.md).

### Precedencia entre las skills de JavaScript

Por materia: el lenguaje, los módulos, la asincronía, el DOM y el runtime son de `javascript-idiomatic-style`; la elección de capa, los dobles, las pruebas y la puerta, de `javascript-testing-and-verification`. La convención del proyecto manda sobre la preferencia de estilo mientras no contradiga al lenguaje.

- **Proyecto con runner propio:** no se añade otro. Vitest, Jest o `node:test` se usan tal como estén, y la puerta ejecuta el script `test` del proyecto.
- **Código que solo corre en Node:** `node --test` y los builtins cubren el caso sin dependencias; no se añade un entorno DOM que no se usa.
- **Prueba de DOM:** se abre la página de pruebas en un navegador real o se usa el entorno que el proyecto ya tenga; no se añade un DOM simulado para probar un módulo pequeño.

### Precedencia entre JavaScript y TypeScript

Por archivo, no por proyecto: `.ts` y `.tsx` son de las skills de TypeScript, incluida la validación en la frontera y el typecheck; `.js`, `.mjs` y `.cjs` sin tipos son de las skills de JavaScript. Un proyecto TypeScript con ficheros de configuración en `.js` conserva el typecheck como puerta y aplica a esos ficheros el contrato de JavaScript. Las reglas de lenguaje no se duplican: manda la skill del archivo que se está editando.

### `python-idiomatic-style`

Escribe y revisa Python tipado e idiomático para librerías, servicios y CLIs. El intérprete y el empaquetado se declaran en un único `pyproject.toml`. Los valores se modelan con `dataclass(frozen=True, slots=True)`, `Enum`, `TypedDict` y `Protocol`; la API pública se anota y cada `Any` se justifica. Las excepciones llevan causa y contexto, los recursos se cierran con `with`, el estado mutable no se comparte y las dependencias, el layout y el build quedan ordenados. Incluye el contrato de una CLI con `argparse` o Typer: salida separada, códigos acotados, `--dry-run`, confirmación explícita y modo no interactivo.

Contrato completo: [`src/python-idiomatic-style/SKILL.md`](src/python-idiomatic-style/SKILL.md).

### `python-testing-and-verification`

Demuestra el comportamiento de código Python con la capa más pequeña. `unittest` o pytest cubren la lógica, con fixtures y parametrización; `tmp_path`, `monkeypatch` y los dobles de red aíslan el entorno. Cada frontera se valida en runtime y la CLI se prueba como proceso, con `stdout`, `stderr` y código de salida separados. La propiedad solo entra si el proyecto ya usa Hypothesis. La puerta `scripts/verify-python.py` comprueba la sintaxis con `compile()` sin ejecutar código y, cuando se piden, ejecuta `ruff format --check`, `ruff check`, mypy o pyright y las pruebas; informa de la versión de Python frente a `requires-python` y devuelve texto o JSON.

Contrato completo: [`src/python-testing-and-verification/SKILL.md`](src/python-testing-and-verification/SKILL.md).

Las skills de Python se apoyan en referencias públicas: la colección [`wdm0006/python-skills`](https://github.com/wdm0006/python-skills), publicada con licencia MIT y basada en la guía de mcginniscommawill.com; la skill [Python Best Practices](https://mcpmarket.com/es/tools/skills/python-best-practices-2) de cuioss, que fija PEP 8 y los estándares modernos del lenguaje; y la lista [The 10 Best Python AI Skills for Developers](https://aiskill.market/blog/best-python-ai-skills-developers) de AI Skill Market, usada como mapa de temas. Tampoco aquí se copia texto: se eligen las decisiones que sostienen código tipado, un proyecto empaquetado, una CLI automatizable y una verificación ejecutada, y se añaden el contrato de agente, el reparto de responsabilidades y la puerta determinista.

| Necesidad | Skill |
|---|---|
| Lenguaje, tipos, proyecto, empaquetado y CLI | `python-idiomatic-style` |
| Capas de prueba, fronteras, proceso y puerta | `python-testing-and-verification` |

El rendimiento, la publicación en PyPI, los frameworks web y los servidores MCP se quedan fuera por la misma razón: no cambian el contrato del lenguaje ni la verificación, y sus reglas caben en las dos anteriores o esperan a una necesidad medida.

### Precedencia entre las skills de Python

La frontera entre las dos: el lenguaje, los tipos, la estructura, las dependencias, el empaquetado y la CLI son de `python-idiomatic-style`; la validación en runtime, la capa de prueba, los dobles, las pruebas y la puerta, de `python-testing-and-verification`. La convención del proyecto manda sobre la preferencia de estilo mientras no contradiga el lenguaje ni el contrato de la CLI.

- **Proyecto con mesa de pruebas propia:** no se añade otra; pytest, unittest o tox se usan tal como estén, y la puerta ejecuta lo que el proyecto declara.
- **Proyecto sin comprobador de tipos:** la puerta informa de que no está disponible; activar `strict` es una migración aparte con su coste medido.
- **Dato que entra por HTTP, fichero, entorno o cola:** se valida en runtime y se prueba en `python-testing-and-verification`; una anotación no rechaza nada.
- **CLI sin framework:** `argparse` es suficiente; Typer o Click se aceptan si el proyecto ya los tiene o si la CLI justifica la dependencia.

### Precedencia entre las skills de Go

Cada una responde de una parte: el contrato de la CLI es de `go-cli-ai-first`; el estilo, los paquetes y las dependencias, de `go-idiomatic-style`; los errores, `context`, la concurrencia y el cierre, de `go-errors-and-lifecycle`; las pruebas y la puerta, de `go-testing-and-verification`. La convención del proyecto manda sobre la preferencia de estilo mientras no contradiga el contrato de la CLI.

- **CLI mínima:** un `main.go` con el cableado y una función `run` testeable. El contrato de `go-cli-ai-first` se aplica completo y no se crean `cmd/`, `internal/` ni `pkg/` por anticipación.
- **CLI con varios comandos:** `cmd/<binario>/main.go`, `internal/cli` e `internal/app`. La estructura se justifica por el tamaño, no por la plantilla, y el contrato de la CLI no cambia.

### `security-engineering`

Convierte un encargo de seguridad en un análisis acotado y verificable. Primero define activos, adversarios y límites de confianza; después revisa diseño, código y configuración de fuente a sumidero. El endurecimiento de agentes, LLM y MCP cubre mínimo privilegio, separación de instrucciones y datos, aprobaciones ligadas a la acción, memoria validada y límites de coste. Las skills, extensiones y dependencias de terceros se auditan antes de usarlas. Prioriza por explotabilidad e impacto, corrige una causa por cambio con prueba de regresión y cierra con evidencia y riesgo residual. Incluye `scripts/security_scan.py`, un escáner determinista de señales con `--json`, `--min-severity`, supresión y códigos de salida acotados.

Contrato completo: [`src/security-engineering/SKILL.md`](src/security-engineering/SKILL.md).

Documentación: [`docs/security-engineering/index.html`](docs/security-engineering/index.html).

### Precedencia de seguridad

La seguridad posee el modelo de amenazas, la revisión, la auditoría de terceros y el cierre con evidencia. No sustituye a las demás skills: el contrato de la CLI sigue en `go-cli-ai-first`, el estilo y la arquitectura del lenguaje en su skill, las pruebas y sus puertas en la skill de verificación correspondiente, y la documentación en `document-management-software`. Cuando un arreglo de seguridad cambia el comportamiento, se presenta el compromiso y se decide; no se impone.

### `playwright-cli-usage`

Conduce un navegador real desde la terminal cuando la pregunta no se responde sin uno. Antes de abrirlo presenta un briefing de siete líneas —pregunta, origen, sesión, acciones, datos, límites y cierre— y espera un sí explícito; sin esa confirmación solo lee el entorno. Ordena el uso en una escalera: sin navegador, un comando, sesión corta o prueba del proyecto. Usa `find`, `--depth` y `--raw` para no volcar snapshots en el contexto, cierra la sesión y declara artefactos y límites. Incluye `scripts/preflight.py`, que reconoce binario, versión, configuración, artefactos e ignorados sin abrir nada, y `scripts/test-preflight.py`, que cubre binario ausente, versión fallida, configuración, artefactos e ignorados.

Contrato completo: [`src/playwright-cli-usage/SKILL.md`](src/playwright-cli-usage/SKILL.md).

Documentación: [`docs/playwright-cli-usage/index.html`](docs/playwright-cli-usage/index.html).

### Precedencia del navegador

La autorización, la proporcionalidad y la evidencia del navegador son de `playwright-cli-usage`; la referencia de comandos, de la skill oficial que instala el CLI. La suite de regresión y su puerta siguen en la skill de verificación del lenguaje, el juicio visual en `web-interface-visual-design` y el tratamiento de credenciales y datos en `security-engineering`. Descubrir con el navegador no autoriza a sustituir la prueba que conserva el comportamiento.

### `web-interface-visual-design`

Diseña, implementa y revisa la calidad visual de interfaces web sin imponer un framework ni sustituir el sistema de diseño existente. Cubre composición, tipografía, color, responsive, accesibilidad, SVG, iconografía e infografías. Exige inspeccionar el resultado renderizado cuando hay herramientas disponibles y distingue esa evidencia de compilar o validar XML. Reconoce los límites de fidelidad del SVG y no inventa datos para completar una composición.

Contrato completo: [`src/web-interface-visual-design/SKILL.md`](src/web-interface-visual-design/SKILL.md). Sus referencias especializan los recursos visuales y definen escenarios de aceptación manual para interfaz, SVG e infografía, sin añadir una suite de CI.

Documentación: [`docs/web-interface-visual-design/index.html`](docs/web-interface-visual-design/index.html), con diagramas de flujo de trabajo y arquitectura.

La calidad visual pertenece a esta skill; arquitectura, lenguaje, lógica de negocio, seguridad y pruebas funcionales conservan sus contratos especializados. En una revisión sin autorización de cambios, solo informa de hallazgos.

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
| [`.skills/adr-software/SKILL.md`](.skills/adr-software/SKILL.md) | [`src/adr-software/SKILL.md`](src/adr-software/SKILL.md) |
| [`.skills/go-cli-ai-first/SKILL.md`](.skills/go-cli-ai-first/SKILL.md) | [`src/go-cli-ai-first/SKILL.md`](src/go-cli-ai-first/SKILL.md) |
| [`.skills/go-idiomatic-style/SKILL.md`](.skills/go-idiomatic-style/SKILL.md) | [`src/go-idiomatic-style/SKILL.md`](src/go-idiomatic-style/SKILL.md) |
| [`.skills/go-errors-and-lifecycle/SKILL.md`](.skills/go-errors-and-lifecycle/SKILL.md) | [`src/go-errors-and-lifecycle/SKILL.md`](src/go-errors-and-lifecycle/SKILL.md) |
| [`.skills/go-testing-and-verification/SKILL.md`](.skills/go-testing-and-verification/SKILL.md) | [`src/go-testing-and-verification/SKILL.md`](src/go-testing-and-verification/SKILL.md) |
| [`.skills/typescript-idiomatic-style/SKILL.md`](.skills/typescript-idiomatic-style/SKILL.md) | [`src/typescript-idiomatic-style/SKILL.md`](src/typescript-idiomatic-style/SKILL.md) |
| [`.skills/typescript-testing-and-verification/SKILL.md`](.skills/typescript-testing-and-verification/SKILL.md) | [`src/typescript-testing-and-verification/SKILL.md`](src/typescript-testing-and-verification/SKILL.md) |
| [`.skills/python-idiomatic-style/SKILL.md`](.skills/python-idiomatic-style/SKILL.md) | [`src/python-idiomatic-style/SKILL.md`](src/python-idiomatic-style/SKILL.md) |
| [`.skills/python-testing-and-verification/SKILL.md`](.skills/python-testing-and-verification/SKILL.md) | [`src/python-testing-and-verification/SKILL.md`](src/python-testing-and-verification/SKILL.md) |
| [`.skills/web-interface-visual-design/SKILL.md`](.skills/web-interface-visual-design/SKILL.md) | [`src/web-interface-visual-design/SKILL.md`](src/web-interface-visual-design/SKILL.md) |
| [`.skills/security-engineering/SKILL.md`](.skills/security-engineering/SKILL.md) | [`src/security-engineering/SKILL.md`](src/security-engineering/SKILL.md) |
| [`.skills/playwright-cli-usage/SKILL.md`](.skills/playwright-cli-usage/SKILL.md) | [`src/playwright-cli-usage/SKILL.md`](src/playwright-cli-usage/SKILL.md) |

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
python scripts/test-version-skill.py
python src/document-management-software/scripts/test-doc-inventory.py
python src/adr-software/scripts/test-adr.py
python src/go-testing-and-verification/scripts/test-verify-go.py
python src/typescript-testing-and-verification/scripts/test-verify-ts.py
python src/javascript-testing-and-verification/scripts/test-verify-js.py
python src/python-testing-and-verification/scripts/test-verify-python.py
python src/security-engineering/scripts/test-security_scan.py
python src/playwright-cli-usage/scripts/test-preflight.py
```

`check-repo.py` valida metadatos, estructura, enrutadores, enlaces Markdown, recibos de los diagramas, versiones y etiquetas de skills, la página de cada skill en `docs/` con su enlace en el catálogo y su referencia en este README, y sintaxis de los scripts. Las pruebas unitarias se ejecutan aparte para que un fallo indique qué script falló. La CI (`.github/workflows/validate.yml`) ejecuta los mismos comandos en cada push y pull request.

Cada skill declara su versión independiente en `metadata.version`; el procedimiento para incrementarla, validarla, publicarla y recuperarla está en [`CONTRIBUTING.md`](CONTRIBUTING.md#versiones-de-las-skills).

## Documentación

- [`docs/index.html`](docs/index.html): punto de entrada y catálogo: qué hace cada skill, dónde está su contrato, cómo se usa y cómo se verifica el repositorio.
- [`docs/best-practices-create-skills/index.html`](docs/best-practices-create-skills/index.html): guía de buenas prácticas en HTML, con los prompts de validación listos para copiar.
- `docs/best-practices-create-skills/README.md`: fuente Markdown de la guía de buenas prácticas.
- `docs/git-flow-management/index.html`: página principal de la skill `git-flow-management`.
- `docs/git-flow-management/flujo-de-trabajo.html`: diagrama del flujo, del encargo al resultado verificado.
- `docs/git-flow-management/arquitectura.html`: diagrama de las piezas del paquete y sus fronteras.
- `docs/document-management-software/index.html`: página principal de la skill `document-management-software`.
- `docs/document-management-software/flujo-de-trabajo.html`: diagrama del flujo, del encargo al cierre verificado.
- `docs/document-management-software/arquitectura.html`: diagrama del paquete, las puertas de la evidencia y la documentación que escribe.
- `docs/prd-cartographer/index.html`: página principal de la skill `prd-cartographer`.
- `docs/adr-software/index.html`: página principal de la skill `adr-software`.
- `docs/adr-software/flujo-de-trabajo.html`: diagrama del flujo, del encargo al ADR revisado.
- `docs/adr-software/arquitectura.html`: diagrama del paquete, la decisión y el registro.
- `docs/prd-cartographer/flujo-de-trabajo.html`: diagrama del flujo, del encargo al PRD revisado.
- `docs/prd-cartographer/arquitectura.html`: diagrama del paquete, la evidencia y la puerta de calidad.
- `docs/go-cli-ai-first/index.html`: página principal de la skill `go-cli-ai-first`.
- `docs/go-cli-ai-first/flujo-de-trabajo.html`: diagrama del flujo, del encargo a la CLI verificada.
- `docs/go-cli-ai-first/arquitectura.html`: diagrama del paquete, la frontera de la CLI y el programa.
- `docs/go-idiomatic-style/index.html`: página principal de la skill `go-idiomatic-style`.
- `docs/go-idiomatic-style/flujo-de-trabajo.html`: diagrama del flujo, de la inspección al diff revisado.
- `docs/go-idiomatic-style/arquitectura.html`: diagrama del paquete, las reglas de estilo y el proyecto.
- `docs/go-errors-and-lifecycle/index.html`: página principal de la skill `go-errors-and-lifecycle`.
- `docs/go-errors-and-lifecycle/flujo-de-trabajo.html`: diagrama del flujo, del fallo al cierre verificado.
- `docs/go-errors-and-lifecycle/arquitectura.html`: diagrama del paquete, la frontera del error y los recursos.
- `docs/go-testing-and-verification/index.html`: página principal de la skill `go-testing-and-verification`.
- `docs/go-testing-and-verification/flujo-de-trabajo.html`: diagrama del flujo, del cambio a la evidencia ejecutada.
- `docs/go-testing-and-verification/arquitectura.html`: diagrama del paquete, las capas de prueba y la puerta.
- `docs/skill-creator/index.html`: página principal de la skill `skill-creator`.
- `docs/skill-creator/flujo-de-trabajo.html`: diagrama del flujo, del encargo al directorio validado.
- `docs/skill-creator/arquitectura.html`: diagrama del paquete, las puertas de validación y el directorio producido.
- `docs/typescript-idiomatic-style/index.html`: página principal de la skill `typescript-idiomatic-style`.
- `docs/typescript-idiomatic-style/flujo-de-trabajo.html`: diagrama del flujo, de la inspección al diff revisado.
- `docs/typescript-idiomatic-style/arquitectura.html`: diagrama del paquete, el modelo de tipos y el proyecto.
- `docs/javascript-idiomatic-style/index.html`: página principal de la skill `javascript-idiomatic-style`.
- `docs/javascript-idiomatic-style/flujo-de-trabajo.html`: diagrama del flujo, de la inspección al diff revisado.
- `docs/javascript-idiomatic-style/arquitectura.html`: diagrama del paquete, los dos baselines y la intersección compartida.
- `docs/javascript-testing-and-verification/index.html`: página principal de la skill `javascript-testing-and-verification`.
- `docs/javascript-testing-and-verification/flujo-de-trabajo.html`: diagrama del flujo, del riesgo al informe ejecutado.
- `docs/javascript-testing-and-verification/arquitectura.html`: diagrama del paquete, los dos entornos de prueba y la puerta.
- `docs/typescript-testing-and-verification/index.html`: página principal de la skill `typescript-testing-and-verification`.
- `docs/typescript-testing-and-verification/flujo-de-trabajo.html`: diagrama del flujo, del mapa de riesgos al cierre con evidencia.
- `docs/typescript-testing-and-verification/arquitectura.html`: diagrama del paquete, las fronteras validadas y la puerta.
- `docs/python-idiomatic-style/index.html`: página principal de la skill `python-idiomatic-style`.
- `docs/python-idiomatic-style/flujo-de-trabajo.html`: diagrama del flujo, del encargo al diff revisado.
- `docs/python-idiomatic-style/arquitectura.html`: diagrama del paquete, las referencias y el proyecto.
- `docs/python-testing-and-verification/index.html`: página principal de la skill `python-testing-and-verification`.
- `docs/python-testing-and-verification/flujo-de-trabajo.html`: diagrama del flujo, del riesgo al informe ejecutado.
- `docs/python-testing-and-verification/arquitectura.html`: diagrama del paquete, las capas de prueba y la puerta.
- `docs/web-interface-visual-design/index.html`: página de entrada a la skill de diseño visual web.
- `docs/web-interface-visual-design/flujo-de-trabajo.html`: diagrama de la inspección, implementación y verificación visual.
- `docs/web-interface-visual-design/arquitectura.html`: diagrama del contrato, sus referencias y la evidencia renderizada.
- `docs/security-engineering/index.html`: página de entrada a la skill de seguridad, con el alcance, el procedimiento, el paquete y el escáner.
- `docs/security-engineering/flujo-de-trabajo.html`: diagrama del flujo, del encargo al riesgo residual.
- `docs/security-engineering/arquitectura.html`: diagrama del paquete, la superficie revisada y la puerta.
- `docs/playwright-cli-usage/index.html`: página de entrada a la skill del navegador, con la puerta de confirmación, la escalera de uso, el paquete y el reconocimiento del entorno.
- `docs/playwright-cli-usage/flujo-de-trabajo.html`: diagrama del flujo, de la pregunta al cierre con la puerta de confirmación.
- `docs/playwright-cli-usage/arquitectura.html`: diagrama del contrato, las cuatro referencias y la sesión confirmada.

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

Ver [`CONTRIBUTING.md`](CONTRIBUTING.md). `main` es la única rama de larga vida; los cambios van en ramas cortas y se integran con `--no-ff`. Crear un remoto, publicar o hacer `push` es una operación aparte, con su propio plan y su confirmación.
