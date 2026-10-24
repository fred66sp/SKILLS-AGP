# Documentación de la skill skill-creator

Documentación de la skill `skill-creator` en `docs/skill-creator/`, con la misma forma que la de `git-flow-management`: una página principal, dos diagramas archify y sus recibos de entrega.

## Specs

S1. Crear la documentación de la skill `skill-creator` dentro de `docs/skill-creator/`, no dentro del paquete de la skill: el paquete (`src/<skill>/` o `.skills/<skill>/`) solo contiene lo que el agente necesita para ejecutarla.

S2. Mantener la misma forma que la documentación de `git-flow-management`:
- `index.html` redactado a mano, en español, con la misma identidad visual y la misma estructura de página (barra superior, hero, índice lateral, secciones numeradas, tablas, notas, preguntas cortas, tarjetas de diagramas, pie y script de tema/copiado).
- Dos diagramas de archify 3.2.0: flujo de trabajo y arquitectura, cada uno con su especificación `*.json` junto al HTML y su recibo `*.delivery.json`.

S3. Todo lo que la página afirme como regla debe salir del paquete instalado: `.skills/skill-creator/SKILL.md`, `references/checklist.md`, `assets/SKILL.template.md` y `scripts/validate-metadata.py`. Sin criterios añadidos ni interpretaciones libres.

S4. La documentación de regeneración (archify 3.2.0, comandos `deliver` y hashes de los recibos) debe ser exacta y comprobable, como en la documentación existente.

S5. Declarar que <https://agentskills.io/> es la guía y la referencia estricta de este repositorio, allí donde se lee la documentación: `README.md`, `docs/best-practices-create-skills/README.md`, `docs/skill-creator/index.html` y `CHANGELOG.md`.

## Tasks

| ID | Spec | Entrega | Commit | Estado |
|---|---|---|---|---|
| T1 | S1 | Rama `docs/skill-creator`, este documento y espejo en Engram (el guardado en Engram falló: base de datos no disponible) | — | hecho |
| T2 | S2, S3 | `docs/skill-creator/index.html` (1138 líneas, 15 secciones) | `docs: añadir la página de la skill skill-creator` | hecho |
| T3 | S2 | `docs/skill-creator/flujo-de-trabajo.json`, `docs/skill-creator/arquitectura.json` | `docs: añadir los diagramas de skill-creator` | hecho |
| T4 | S2, S4 | `docs/skill-creator/*.html` + `*.delivery.json` (archify 3.2.0, 9/9 comprobaciones cada uno) | `docs: añadir los diagramas de skill-creator` | hecho |

Los SHA que tenía esta tabla dejaron de existir cuando la historia del repositorio se unificó en un commit
inicial; se conservan las materias de commit como evidencia de la unidad de trabajo.
| T5 | S1, S4 | `README.md`, `CHANGELOG.md` | último commit de la rama | hecho |
| T6 | S2, S3, S4 | Verificación: enlaces, hashes, ausencia de recursos externos, salidas reales del validador | ver Log L6 | hecho |
| T7 | S1 | Commits por unidad de trabajo | `docs: añadir la página`, `docs: añadir los diagramas` y el último de la serie | hecho |
| T8 | S5 | Referencia estricta a <https://agentskills.io/> en README, guía, página y changelog | último commit de la rama | hecho |

## Fronteras de entrega

Estrategia: commits secuenciales en la rama `docs/skill-creator` (no hay remoto, así que no hay PR ni cadena de PR). La rebanada de ~400 líneas se aplica a código revisable línea a línea; aquí las dos primeras rebanadas son artefactos indivisibles:

| Rebanada | Contenido | Motivo de la frontera |
|---|---|---|
| A | `index.html` | Una página es una unidad: partirla dejaría la página a medias y sin enlaces válidos |
| B | los dos `*.json` + `*.html` + `*.delivery.json` | Cada diagrama es un artefacto generado: su spec, su HTML y su recibo se entregan y se revisan juntos |
| C | `README.md`, `CHANGELOG.md`, este documento | Solo referencias y registro; no cambia ningún artefacto |

## Log

L1 (petición original, literal): «vamos a crear la documentación de la skill skill-creator en docs/skill-creator igual que la documentación de git-flow-management»

L2 (decisión, herramienta): archify 3.2.0 no está instalado en la máquina. Se clona la etiqueta `v3.2.0` en `.pi/tools/archify`, dentro de la raíz del proyecto y ya cubierto por `.gitignore` (`.pi/`), para no leer ni escribir fuera de la raíz ni añadir una dependencia al repositorio. El HTML y los recibos se generan con esa copia; la ruta no se versiona y no se documenta como requisito del repositorio.

L3 (decisión, verificación): los ejemplos de la página usan salidas reales de `scripts/validate-metadata.py` ejecutado con Python 3.13.9 en esta máquina (código 0 con metadatos válidos; código 1 con nombre inválido y con descripción en primera persona; código 0 sin `--description`; código 1 con descripción de 1.100 caracteres).

L4 (incidencia, delegación): el trabajador `gentle-ai-worker` no arranca en este entorno (`spawn pi ENOENT`), así que la página se redactó en línea en la sesión principal.

L5 (corrección, diagramas): el primer spec de arquitectura no pasó `archify validate`: tres componentes caían dentro de marcos de frontera sin pertenecer a ellos y una etiqueta no tenía hueco suficiente. Se reubicaron los componentes en dos clústeres compactos y se dio más separación a las conexiones etiquetadas. Segundo intento: `ok architecture (9 artifact checks; 0 errors, 0 warnings)`.

L6 (verificación, evidencia): sobre el árbol de trabajo y sobre el commit — 0 enlaces rotos desde `index.html`, `README.md` y `CHANGELOG.md`; 0 recursos externos (`http`, `https`, `data:` de red, `@import`, tipografías remotas); 0 ids duplicados; 15 secciones y 15 entradas de índice; 0 errores de anidado HTML; 19 ítems de checklist y 5 bloques, que son las cifras que afirma la página; los `sha256` de los cuatro recibos coinciden con los blobs del commit (spec y artefacto); carga en navegador sin errores de consola y con el conmutador de tema funcionando (`#6d28d9` en claro, fondo `#0a0f1c` en oscuro).

L7 (corrección, saltos de línea): la primera escritura de `arquitectura.json` salió con CRLF y el recibo registraba el hash del fichero con CRLF, distinto del blob normalizado a LF. Se reescribió el spec con LF y se re-entregó el diagrama: el HTML resultó idéntico byte a byte (`sha256 071b29d0367e`) y los cuatro recibos quedaron `current` contra el commit.

L8 (decisión, alcance): no se toca `.gitignore` por los artefactos de verificación; la captura de pantalla y el directorio del navegador se borraron tras comprobar la página. `odd/tasks/` se versiona porque forma parte del seguimiento del trabajo.

L9 (cambio de requisito, literal): «añade donde sea necesario que este repositorio tiene como guía y referencia extricta de https://agentskills.io/»

L10 (ejecución, S5): la referencia se declara en cuatro sitios, que son donde se lee la documentación: el `README.md` (párrafo de cabecera con el alcance de la norma), la guía de buenas prácticas (línea «Referencia estricta» antes de la documentación externa), la página de la skill (sección 1 y tarjeta de `SKILL.md`, con enlace) y el `CHANGELOG.md`. En la página es un enlace saliente: no añade ninguna carga de recurso externo, así que la afirmación de «página estática» del pie sigue siendo cierta. No se tocan los diagramas ni sus recibos; los cuatro `sha256` siguen coincidiendo con los blobs del commit.

L11 (defecto reportado, literal): «en el index.html de skill-creator, el bloque "Cuándo aplica	Cuándo no" le falta margen supieror y eso hace que se vea pegado. Añade el margen necesario. No hace falta que lo compruebes en el navegador, me lo dices y yo lo compruebo.»

L12 (causa y corrección, S2): la tabla de la sección 1 es un `.table-wrap` inmediatamente después de la rejilla `.flow`. El sistema de diseño solo separaba `.grid + .grid`, `.grid + .note`, `.grid + h3` y `.table-wrap + …`; ni `.flow` ni `.table-wrap` tienen margen propio, y un `div` no trae margen del navegador, así que el hueco era 0. Se añade `.flow + .table-wrap, .grid + .table-wrap { margin-top: 24px; }`: el mismo aire que ya usan las rejillas entre sí. En la página de `git-flow-management` el bloque equivalente va seguido de un `.note`, que sí trae `margin: 16px 0`, y por eso allí no aparece el defecto. Comprobación estática hecha (regla presente, adyacencia real, sin regla competidora, llaves del CSS balanceadas); la comprobación visual la hace la persona.

L13 (cambio de herramienta, ruta): la copia de archify se mueve de `.pi/tools/archify` a `.pi/vendor/archify`. Motivo: Pi trata `<proyecto>/.pi/tools/` como directorio obsoleto de custom tools y, si contiene cualquier entrada no oculta, muestra un aviso de migración en cada arranque y se queda esperando una pulsación. El aviso no dependía de que archify fuera un custom tool: lo dispara la mera presencia de la carpeta (pi `dist/migrations.js`, `checkDeprecatedExtensionDirs`, que solo mira `hooks/` y `tools/` de `.pi/` y de `~/.pi/agent/`). Se conserva la decisión de L2 —copia dentro de la raíz, ignorada por git, ruta no versionada—: `.pi/vendor/` no la mira nadie más y sigue cubierto por `.gitignore`. `tools/check-feature.py` en la raíz del proyecto no tiene nada que ver: Pi no escanea esa ruta. Comprobado tras el movimiento: 0 avisos con la misma réplica de la comprobación, y `archify validate architecture docs/document-management-software/arquitectura.json --json` → `ok: true`, exit 0, desde la ruta nueva.
