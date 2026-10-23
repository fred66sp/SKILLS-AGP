# gherkin-scenario-review

Skill de revisión de escenarios Gherkin ya escritos, en `src/gherkin-scenario-review/`, y su documentación en
`docs/gherkin-scenario-review/`. Ruta grande: rama corta `feature/gherkin-scenario-review` desde `main`, commits por
unidad revisable, integración en `main` y cualquier `push` pendientes de decisión explícita del usuario.

Fuente principal: `C:\Users\alfredo\Documents\IDEAS\__LIMBO\Cómo escribir buen Gherkin.md` (cuatro reglas de Andy
Knight). Fuentes secundarias de la bóveda: `CURSOS/Curso de Especificaciones/03,06,07`. La mitad de automatización no
existe en la bóveda y se trae de documentación oficial de cada runner, con verificación de comandos en el proyecto
destino.

## Specs

S1. Fuente de referencia obligatoria: «tomando como referencia C:\Users\alfredo\Documents\IDEAS\__LIMBO\Cómo escribir buen Gherkin.md de nuestra bóveda de obsidian». Las cuatro reglas (regla de oro, un escenario un comportamiento, ejemplo único por clase de equivalencia, calidad de lenguaje) son el núcleo del contrato.

S2. La skill «implemente BDD» dentro del alcance decidido: revisión. Verbatim de la opción elegida: «Una sola ruta: leer .feature, pasar las 4 reglas + script, devolver informe. Sin descubrimiento, sin redacción guiada, sin automatización.»

S3. Formato de artefacto único. Verbatim: «Salida única: features/<capacidad>.feature. Delta specs y requisitos SHALL quedan fuera del contrato». La skill no emite `### Requirement:` ni SHALL.

S4. Automatización: verbatim «Agnóstico + un reference por stack». El flujo detecta el stack y carga solo esa referencia; cada referencia sirve para juzgar si un paso es automatizable y si pertenece a hooks o a Gherkin, no para implementar.

S5. Entrega. Verbatim: «SKILL.md + references + script + docs/diagramas … docs/bdd-behavior-specification/: index.html, flujo-de-trabajo.{json,html,delivery.json}, arquitectura.{json,html,delivery.json} + README.md y CHANGELOG.md actualizados + /skill-registry:refresh». La ruta de skill se renombra a `gherkin-scenario-review` (decisión L3); la forma del paquete no cambia.

S6. Reglas de empaquetado del repositorio: `name` coincide exactamente con el directorio padre; dentro de `src/<skill>/` no hay `README.md`, `CHANGELOG.md` ni guía de instalación; `references/` a un solo nivel de profundidad; rutas relativas con barras inclinadas; `SKILL.md` por debajo de 500 líneas; `description` en español, tercera persona, con disparadores negativos y de 1.024 caracteres o menos, validada con `.skills/skill-creator/scripts/validate-metadata.py`.

S7. El script determinista vive en `scripts/check-feature.py`, es stdlib-only (sin dependencias ni red), con el formato de casa: docstring con `Uso:`, salida por stdout legible, mensajes de error autoexplicativos por stderr y códigos de salida `0` sin hallazgos, `1` o `3` con hallazgos, `2` error de uso.

S8. El script acepta palabras clave en inglés (`Given/When/Then/And/But`) y en español (`Dado/Cuando/Entonces/Y/Pero`), encabezado `# language: es`, `Feature`, `Background`, `Scenario`, `Scenario Outline`/`Esquema del escenario`, `Examples`/`Ejemplos`, etiquetas `@`, comentarios `#` y `*` como paso alternativo.

S9. Comprobaciones deterministas exigidas al script, cada hallazgo con la regla que viola y la línea: orden estricto `Dado → Cuando → Entonces` (un `Dado` después de `Cuando`/`Entonces` es violación); presencia de al menos un `Entonces`; más de un par `Cuando`/`Entonces` en un escenario (regla 2); número de pasos de un escenario por encima de 9 (longitud de un dígito, regla 1); vocabulario de interacción de bajo nivel (`clic`, `click`, `botón`, `button`, `teclea`, `escribe`, `wait`, `espera`, `scroll`, `navega a la URL`) (regla 1); `Scenario Outline` con más filas de `Examples` que el umbral declarado y filas que solo difieren en un campo de la misma clase (regla 3); mezcla de primera y tercera persona en los pasos de un mismo escenario (regla 4); paso sin sujeto o sin verbo (regla 4). Los umbrales y patrones que sean heurística se declaran en el propio `--help` del script y en la referencia que los explica.

S10. El informe usa la [plantilla de informe](assets/review-report-template.md) con veredicto por escenario y estado final del archivo en un vocabulario cerrado: `APTO`, `APTO CON RESERVAS`, `NO APTO`. Cada hallazgo cita regla, número de línea y una reescritura propuesta; ningún hallazgo se declara sin la evidencia de línea que lo sustenta.

S11. Evidencia obligatoria antes de declarar terminada la entrega: `validate-metadata.py` en `SUCCESS`; `check-feature.py` ejecutado sobre los dos fixtures del paquete (uno `APTO`, otro con violaciones conocidas) mostrando salida y códigos; prueba del script en orden RED → GREEN; `doc-inventory.py` sobre `src/gherkin-scenario-review` y sobre `docs/gherkin-scenario-review` con enlaces resueltos; los dos diagramas `archify` validados con `provenance: current`; y la simulación de ejecución de la skill contra un encargo de revisión realista, sin huecos donde el agente tenga que adivinar.

S12. Ningún commit se ejecuta sin confirmación explítica, siguiendo `src/git-flow-management/SKILL.md` y `CONTRIBUTING.md`: cambios preparados en el stage, mensaje Conventional Commits en inglés, barrido previo de `README.md`, `CHANGELOG.md`, registro de skills y referencias cruzadas antes de pedir la confirmación.

## Tasks

| ID | Tarea | Specs | Unidad de commit |
|---|---|---|---|
| T1 | Contrato: `SKILL.md` con clasificación del encargo, flujo con puertas e invariantes | S1, S2, S3, S6 | `feat(gherkin-review): añadir el contrato de revisión de escenarios` |
| T2 | Referencias de las cuatro reglas: calidad, estructura y orden, clases de equivalencia, lenguaje y punto de vista | S1, S9, S10 | `docs(gherkin-review): añadir las referencias de las cuatro reglas` |
| T3 | `scripts/check-feature.py` con sus fixtures y su prueba RED → GREEN | S7, S8, S9, S11 | `feat(gherkin-review): añadir el script determinista de comprobación` |
| T4 | Referencias por stack (JS/TS, Python, Java, .NET, Go) con detección de stack y verificación de comandos | S4, S11 | `feat(gherkin-review): añadir las referencias por stack` |
| T5 | Plantillas `assets/`: informe de revisión y checklist de las cuatro reglas | S10 | `feat(gherkin-review): añadir plantilla de informe y checklist` |
| T6 | `docs/gherkin-scenario-review/`: especificaciones archify, dos diagramas entregados y página principal | S5, S11 | `docs(gherkin-review): añadir página y diagramas de la skill` |
| T7 | Barrido de `README.md`, `CHANGELOG.md` y registro de skills | S5, S12 | `docs: registrar la skill de revisión de escenarios Gherkin` |
| T8 | Verificación de la entrega y simulación de ejecución | S11 | sin commit propio: evidencia en el Log |

### Límites de rebanada

T1 a T5 son autoría pura y cada uno se mantiene por debajo de las ~400 líneas del repositorio. T4 puede pasarlas si los cinco `references/` por stack crecen: en ese caso se parte en `T4a` JS/TS + Python + detección y `T4b` Java + .NET + Go, con un commit por mitad. T6 incluye HTML generados por archify, que no cuentan como autoría: lo revisable son los `*.json` y sus recibos.

## Log

L1 (petición original, literal): «tomando como referencia C:\Users\alfredo\Documents\IDEAS\__LIMBO\Cómo escribir buen Gherkin.md de nuestra bóveda de obsidian. Quiero hacer una skill que implemente BDD. Puedes analizar otros documentos de la bóveda, hay mucha información. Prepara un plan primero, antes de implementar.»

L2 (decisiones del usuario, cuestionario de 4 preguntas): alcance = «Solo revisión de escenarios ya escritos»; formato = «Solo archivos .feature»; stacks = «Agnóstico + un reference por stack»; entrega = «SKILL.md + references + script + docs/diagramas».

L3 Decisión de interpretación: el nombre `bdd-behavior-specification` se descarta porque el alcance elegido es solo revisión; la skill se nombra `gherkin-scenario-review` y su `description` lleva los disparadores BDD, Gherkin y `.feature` por delante para que se dispare desde el lenguaje BDD.

L4 Decisión de interpretación: las referencias por stack no contradicen el alcance «sin automatización». Sirven para juzgar automatizabilidad y para decidir si un detalle de bajo nivel pertenece a hooks o a Gherkin, no para escribir step definitions.

L5 Evidencia de reconocimiento: bóveda indexada en Miyo (`IDEAS` 529/529, listo) y explorada con `miyo search` + `grep`. Lo que la bóveda cubre: las cuatro reglas, anti-patrones, formato, escalera de verificación y estilo de casa para skills que producen especificaciones. Lo que no cubre en absoluto: step definitions, page objects, CLI de runners, hooks implementados, reportes, CI para escenarios.

L6 Conflicto entre notas de la bóveda, resuelto por el alcance: `CURSOS/Curso de Especificaciones/03` escribe GWT en bullets Markdown dentro de la spec, `06` muestra un `.feature` real y la nota de Gherkin trabaja con `.feature`. Se resuelve con S3 (`.feature` solo). `RECURSOS/Skills/prd-cartografo` trata GWT como opcional; queda fuera porque la skill solo opina sobre `.feature` que ya existen. El choque TDD (`uncle-bob-agentes-ia-fundamentos-software.md` contra `CURSOS/Curso completo de Gentle-AI/08`) no se toca: esta skill no impone disciplina de test-first, solo revisa artefactos de comportamiento.

L7 En curso: falta por confirmar del usuario — nombre `gherkin-scenario-review` y el visto bueno para empezar T1.

L8 (autorización, literal): «adelante». Se lee como confirmación conjunta de las etapas enumeradas en el plan: crear la rama desde `main`, escribir T1 a T8 y preparar los commits por unidad revisable. No autoriza integrar en `main` ni `push`.

L9 Corrección del nombre: el `name` del frontmatter y el directorio son `gherkin-scenario-review`; S5 conserva la forma de paquete y las rutas de `docs/` con ese nombre.

L10 Códigos de salida fijados para `scripts/check-feature.py`: `0` sin hallazgos, `3` con hallazgos (deterministas o candidatos), `2` error de uso o idioma no soportado. Trece códigos: seis deterministas (`step-order`, `missing-then`, `multiple-action-outcome`, `too-many-steps`, `outline-missing-placeholder`, `unparseable-block`) y cinco candidatos (`low-level-vocab`, `person-mixed`, `no-subject-verb`, `redundant-examples`, `business-intent-given`), más `--max-steps 9` y `--max-outline-rows 5`.

L11 Evidencia T3 (RED → GREEN): RED observado con parser y solo `missing-then` y `step-order` implementadas → el fixture malo devolvía 3 hallazgos y exit 3, y el parser no veía ningún bloque porque las palabras clave de bloque llevan dos puntos (`Scenario:`) y `classify` no los trataba. GREEN: sobre `assets/example-feature-bad.feature`, 21 hallazgos (10 deterministas, 11 candidatos), exit 3, disparando los 13 códigos previstos; sobre `assets/example-feature-good.feature`, 0 hallazgos, exit 0. Además: ruta inexistente → exit 2; `# language: de` → exit 2 con mensaje; `--json` devuelve 21 objetos con las claves `rule`, `deterministic`, `file`, `line`, `evidence`, `message`; `--max-steps 3` y `--max-outline-rows 1` cambian los hallazgos del fixture bueno como se espera; la rama de variación de una sola columna se comprobó con un fixture temporal fuera del repositorio (`mktemp -d`), no commiteada.

L12 Hallazgo de entorno al corregir: un `\b` escrito como `"\b"` dentro del JSON de la herramienta de edición llegó al fichero como carácter de retroceso (0x08), así que `THIRD_PERSON_RE` nunca casaba y `person-mixed` no disparaba. Corregido con `\u0008` en el oldText y `\\b` en el newText. Nota para la casa: en los argumentos JSON de `edit`/`write`, las secuencias de escape de regex se escriben con doble barra.

L13 Defecto de escritura observado: sustituir el byte 0x08 con `python` (`open(...,'wb')`, `io.open`, con `flush` y `os.fsync`) no persistía en el disco (`changed: False` releyendo el fichero); la misma sustitución con la herramienta `edit` sí persistió. Para correcciones de este fichero se usa `edit`, no `python`. 
