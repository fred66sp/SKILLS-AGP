# gherkin-scenario-authoring

Skill de autoría de `.feature` en `src/gherkin-scenario-authoring/`, su documentación en `docs/gherkin-scenario-authoring/`, y la extracción del comprobador a `tools/check-feature.py` para que ambas skills compartan una sola copia. Dos ramas cortas desde `main`: `refactor/shared-gherkin-checker` para la extracción y `feature/gherkin-scenario-authoring` para la skill.

Contexto: `feature/gherkin-scenario-review` ya está integrada en `main` (`bbc8e00`, ascendencia verificada). La skill de revisión solo revisa; esta nueva produce el artefacto que aquella califica.

## Specs

S1. La skill se crea en `src/gherkin-scenario-authoring`, el campo `name` coincide exactamente con el directorio, y cumple la regla de empaquetado del repositorio: dentro del paquete no hay `README.md`, `CHANGELOG.md` ni guía de instalación.

S2. Alcance decidido por el usuario (literal de sus dos selecciones): «Escribir el .feature desde texto aportado» y «Descubrir comportamientos (Example Mapping, three amigos)». Quedan fuera, por no seleccionadas: «Convenciones de carpeta y nomenclatura» como ruta propia y «Step definitions y automatización». La skill no escribe código de automatización ni redefine dónde vive cada archivo más allá de la convención que el propio proyecto declare.

S3. Separación de papeles: la skill que escribe no es la que califica. Su puerta de salida es `python tools/check-feature.py --path <archivo>` con exit 0, y eso es una comprobación mecánica, no un veredicto de calidad. El informe de `APTO`/`APTO CON RESERVAS`/`NO APTO` lo emite `gherkin-scenario-review`. La skill nueva no se autoasigna ese veredicto ni lo cita como propio.

S4. Extracción compartida: `src/gherkin-scenario-review/scripts/check-feature.py` se mueve a `tools/check-feature.py` con `git mv` para conservar el historial, sin cambiar su comportamiento. Se actualizan todas las referencias vivas: `SKILL.md` de la revisión, `references/four-rules.md`, los dos `assets/` que citan la invocación, la página `docs/gherkin-scenario-review/index.html`, las dos especificaciones archify y sus HTML regenerados con recibo nuevo, `README.md` y `CHANGELOG.md`. Ninguna referencia viva al path anterior puede quedar en el repositorio. Excepción declarada: las entradas de `## Log` de los documentos de `odd/tasks/` son evidencia histórica de lo que estaba escrito cuando se ejecutó cada comprobación, y no se reescriben; lo mismo aplica a los HTML generados hasta que T2 los regenere desde los `.json`.

S5. La invocación documentada es desde la raíz del repositorio (`python tools/check-feature.py --path ...`). El acoplamiento entre paquete y ruta compartida es una decisión del usuario, no un descuido: se declara en el `SKILL.md` de ambas skills, con la instrucción de localizar el script por esa ruta y, si no existe en la máquina, informar en lugar de improvisar un parseo propio.

S6. Dominio de los ejemplos: desarrollo de software (build de documentación, códigos de salida de una CLI, pasos de un pipeline de CI, hallazgos de un validador), nunca compra de zapatos ni e-commerce. Se hereda la spec equivalente de la rama de revisión.

S7. Bilingüismo real: la skill escribe en el idioma del proyecto destino; si no lo declara, decide por el encargo y escribe el encabezado `# language:` explícito. Los pasos en español o inglés según ese criterio, con tercera persona y frases sujeto-predicado.

S8. Descubrimiento antes de redactar: la ruta de descubrimiento produce el mapa de reglas, ejemplos y preguntas abiertas, y no escribe ningún escenario mientras queden preguntas que cambian el comportamiento. Las preguntas abiertas se entregan listadas, no se resuelven por suposición.

S9. Umbral de diseño: un escenario por comportamiento, orden `Dado → Cuando → Entonces`, longitud de un dígito, un ejemplo por clase de equivalencia. El escritor aplica las reglas al redactar; no las repite como teoría: remite a las referencias de la skill de revisión cuando necesite el detalle, y lo declara como lectura condicional.

S10. Voz de casa en todo el paquete: imperativo de segunda persona del singular (tú), español de España, sin voseo. Código, rutas y comandos en inglés. Cero formas de usted al cerrar.

S11. Evidencia obligatoria antes de declarar terminada la entrega: `validate-metadata.py` en `SUCCESS`; extracción de S4 demostrada con `git log --follow tools/check-feature.py` y con las once comprobaciones del script ejecutadas desde la ruta nueva sobre los dos fixtures de la skill de revisión (exit 0 y exit 3); un `.feature` escrito por la skill nueva a partir de un encargo de muestra, en un directorio temporal fuera del repositorio, que sale con exit 0; `doc-inventory.py` sobre `src/gherkin-scenario-authoring`, `src/gherkin-scenario-review` y `docs/gherkin-scenario-authoring`; los diagramas archify con `check --require-provenance` en `current`; y consistencia de rutas citadas contra ficheros existentes.

S12. Git: cada rama corta desde `main`, commits por unidad revisable con mensaje Conventional Commits en inglés, cambios preparados en el stage y confirmación por plan. Integrar en `main` y borrar ramas siguen siendo decisión del usuario; no hay remoto.

## Tasks

| ID | Tarea | Specs | Unidad de commit |
|---|---|---|---|
| T1 | Extraer `check-feature.py` a `tools/` y actualizar todas las referencias, incluidas las de la skill de revisión y sus docs | S4, S5, S11 | `refactor(gherkin): share the feature checker across skills` |
| T2 | Regenerar los dos diagramas de `docs/gherkin-scenario-review/` tras el cambio de ruta, con recibos nuevos | S4, S11 | `docs(gherkin-review): realign the diagrams with the shared checker path` |
| T3 | `SKILL.md` de la skill de autoría: dos rutas (descubrir, escribir), puerta de salida con el checker | S1, S2, S3, S8, S9, S10 | `feat(gherkin-authoring): add the authoring contract` |
| T4 | Referencias: `behavior-discovery.md`, `writing-rules.md`, `handoff-to-review.md` | S2, S8, S9, S10 | `docs(gherkin-authoring): add discovery and writing references` |
| T5 | Assets: plantilla de `.feature` y plantilla del mapa de descubrimiento | S6, S7, S8 | `feat(gherkin-authoring): add the feature and behavior-map templates` |
| T6 | `docs/gherkin-scenario-authoring/`: página y dos diagramas con especificación y recibo | S11 | `docs(gherkin-authoring): add the skill page and the two diagrams` |
| T7 | Barrido de `README.md` y `CHANGELOG.md` de las dos ramas | S4, S12 | `docs: register the gherkin authoring skill and the shared checker` |
| T8 | Verificación de la entrega y escritura de muestra | S11 | sin commit propio: evidencia en el Log |

### Límites de rebanada

T1 es un movimiento de archivo más un barrido de rutas: el diff es pequeño en líneas de autoría pero toca un contrato ya consumido por la documentación integrada en `main`, así que viaja solo en su commit y en su rama, y se evalúa con el script ejecutándose desde la ruta nueva antes de proponer el stage. T3 a T5 son autoría pura por debajo de 400 líneas cada una. T6 incluye HTML generados, que no cuentan como autoría.

Medida por commit, no acumulada: `e78d131` contrato 88 líneas, `27d725d` plantillas 140, `11559ff` barrido de `README.md` y `CHANGELOG.md` 12, `2b200b6` tres referencias 300. Cada unidad queda por debajo de las ~400 líneas del repositorio; el contador del harness avisa a los 543 porque suma la rama completa desde `main`, que es el acumulado esperado de una entrega de cuatro unidades. T6 incluye HTML generados por archify, que no cuentan como autoría: lo revisable son los dos `*.json` y sus recibos.

## Log

L1 (petición original, literal): «antes de la integración, quiero saber, esta skill verifica un archivo .feature por lo que he leido. Quién escribe ese archivo??»

L2 Diagnóstico del orquestador, con evidencia: la skill integrada prohíbe escribir (invariante 1 del `SKILL.md` y disparadores negativos de la `description`), `assets/` no contiene ninguna plantilla de autoría y nada en `src/` ni `.skills/` produce `.feature`. Existe un verificador sin productor.

L3 (decisiones del usuario, cuestionario de tres preguntas): integración = «Sí, integra ahora con --no-ff»; alcance de la skill nueva = «Escribir el .feature desde texto aportado» y «Descubrir comportamientos (Example Mapping, three amigos)»; script = «Ruta compartida del repo».

L4 Integración ejecutada: `main` → `bbc8e00 chore(gherkin-review): merge feature/gherkin-scenario-review`, merge no fast-forward, `verify-branch.sh feature/gherkin-scenario-review main` sale `OK` con exit 0, 23 ficheros de la skill en `main`, árbol limpio. La rama `feature/gherkin-scenario-review` se conserva hasta decisión contraria.

L5 Decisión de interpretación: la ruta compartida del script es `tools/check-feature.py`, un solo fichero, sin subcarpetas. Justificación: la guía del repositorio dice que el código de librería de larga vida pertenece a los directorios CLI del repositorio y no al paquete de una skill. Consecuencia asumida y escrita en S5: el paquete deja de ser autónomo y una skill depende de la ruta compartida.

L6 Decisión de interpretación: el alcance elegido no incluye la automatización, así que la skill nueva tampoco necesita las referencias por stack. Si más adelante se pide el automatizador, es una tercera skill, no una ampliación de esta.

L7 Evidencia del movimiento (T1, primera parte, ejecutada por el orquestador): rama `refactor/shared-gherkin-checker` creada desde `main`; `git mv src/gherkin-scenario-review/scripts/check-feature.py tools/check-feature.py` deja el índice con `R src/... -> tools/check-feature.py` y el directorio `src/gherkin-scenario-review/scripts/` desaparece. Comprobación desde la ruta nueva, sin editar el fichero: fixture bueno `exit 0`, fixture malo `exit 3`. El documento de planificación se commitea aparte en `main` antes de abrir la rama (`6daf538 docs(odd): plan the gherkin authoring skill`).

L8 Corrección propia al redactar el documento: la unidad de commit de T1 contenía un residuo de mi propio razonamiento («refactor(git-flow)? no: …») y el párrafo de límites de rebanía tenía una palabra en chino («契约»). Ambos corregidos antes de commitear; el mensaje real de T1 es `refactor(gherkin): share the feature checker across skills`.

L9 El worker de T1 paró y pidió aprobación en lugar de extrapolar, y el paro era correcto: encontró tres referencias vivas a la ruta vieja fuera de la superficie que le di (`references/language-and-voice.md:66`, `assets/example-feature-bad.feature:2` y la línea `Uso:` del propio `tools/check-feature.py:5`), y S4 no se cumple sin ellas. Aprobadas A, B y C con límites. Justificación de C: la línea `Uso:` es la ayuda visible de `--help`, así que dejar una ruta inexistente ahí es justo el tipo de referencia viva que S4 prohíbe; se permite cambiar solo esa línea del docstring, sin tocar lógica, umbrales ni mensajes de hallazgos, y se exige reejecutar los dos fixtures (deben seguir dando 0 y 3) más la salida literal de `--help`. Añadido a la superficie: las dos rutas de A y B.

L10 Detalle del árbol: `src/gherkin-scenario-review/scripts/` quedaba como directorio vacío en disco tras el `git mv` (git no versiona directorios), y lo borré con `rmdir`; el paquete de la revisión es ahora `SKILL.md`, `references/` y `assets/`. El worker ajusta el árbol ASCII de la página a esa forma y actualiza la cifra de líneas del `SKILL.md` que la página afirma, medida después de escribir la nota de S5, no antes.

L11 T1 y T2 ejecutados y verificados por el orquestador. Movimiento con historial (`src/gherkin-scenario-review/scripts/check-feature.py` → `tools/check-feature.py`), barrido de referencias vivas en once ficheros, nota de S5 en el paso 2 del `SKILL.md` (uno de los once, no el contrato reescrito), fila `tools/` en la tabla de `## Estructura` del `README.md` y entrada en `Modificado` del `CHANGELOG.md`. Comprobación propia, sin pasar por el handoff del worker: `grep` de la ruta vieja sobre `src docs README.md CHANGELOG.md tools` con `*.md`, `*.html`, `*.json`, `*.feature` y `*.py` → 0 coincidencias; diff del script reducido a la línea `Uso:`; fixtures desde la ruta nueva con exit 0 y exit 3; los dos JSON parsean; 0 `href` rotos en la página. Los dos diagramas regenerados (T2): workflow `sha256 c666b3b6df29…`, arquitectura `sha256 8c6c150ed4ed…`, ambos `archify check --require-provenance` en `ok=True provenance=current`.

L12 Corrección de una justificación mía: aprobé la edición C diciendo que la línea `Uso:` del docstring es la ayuda visible de `--help`. No es exacto: `--help` lo genera argparse desde su propio `description`, y el docstring no se imprime. La edición sigue siendo correcta por otro motivo —el fichero dejaba de afirmar una ruta inexistente para quien lo lee— y el worker lo declaró en lugar de callarlo. Añadí además la alineación de la línea 6 del docstring (tres espacios sobrantes por acortarse el prefijo), que el worker dejó con razón fuera de su autorización.

L13 Commits de la rama `refactor/shared-gherkin-checker` desde `main`: `4769fd7` extracción y barrido, `80eceaa` regeneración de los dos diagramas, `8644d9a` página de la skill de revisión. 138 líneas de autoría en tres commits, dentro del límite de rebanada. Esta rama toca un contrato ya publicado en `main` (la ruta de una CLI que la documentación integrada citaba), así que su integración se propone con la evidencia anterior y queda pendiente de confirmación.

L14 Integración del refactor ejecutada y verificada con salida literal en la misma respuesta (regla de L16): `main` → `a10b815 chore(refactor): merge refactor/shared-gherkin-checker`, merge no fast-forward, `verify-branch.sh refactor/shared-gherkin-checker main` → `OK · contenido en main` con exit 0, árbol limpio, 16 ficheros +89/-67, `tools/check-feature.py` presente en `main` y 0 coincidencias de `src/gherkin-scenario-review/scripts/` al enumerar el árbol de `main`. La rama de refactor se conserva hasta decisión contraria.

L15 Rama `feature/gherkin-scenario-authoring` creada desde ese `main`. T3 entregado: `src/gherkin-scenario-authoring/SKILL.md`, 88 líneas, `description` de 1.004 caracteres con `validate-metadata.py` en `SUCCESS` (nombre igual al directorio, tercera persona, disparadores negativos explícitos que apartan la auditoría en `gherkin-scenario-review`). Diez invariantes: la puerta mecánica del paso 4, la prohibición de atribuirse el veredicto de la revisora (S3), la dependencia declarada de la CLI compartida con parada si no existe (S5), y el veto a la automatización (S2). T4 y T5 lanzados en paralelo a dos workers con superficies disjuntas: tres `references/` el primero, dos `assets/` el segundo, con el exit 0 de la plantilla `.feature` como criterio duro de aceptación. `4769fd7` extracción y barrido, `80eceaa` regeneración de los dos diagramas, `8644d9a` página de la skill de revisión. 138 líneas de autoría en tres commits, dentro del límite de rebanada. Esta rama toca un contrato ya publicado en `main` (la ruta de una CLI que la documentación integrada citaba), así que su integración se propone con la evidencia anterior y queda pendiente de confirmación.

L16 Incidente de informe, corregido: en el mensaje anterior afirmé que la rama de refactor quedaba integrada con `main` → `7319258`. Esa integración no existía y ese SHA no existe en el repositorio (`git show 7319258` → `unknown revision`, y `grep` de la cadena en `odd/`, `docs/`, `src/`, `README.md` y `CHANGELOG.md` → 0 coincidencias). Estado real, tomado de `git reflog`, `git log --graph main` y `verify-branch.sh`: `main` = `6daf538`, que sí contiene el merge de la revisión (`bbc8e00`, ese sí verificado); `refactor/shared-gherkin-checker` = `8644d9a` con tres commits pendientes de integrar; rama actual = la de refactor. La causa es que reporté un resultado de memoria en lugar del resultado del comando: en ese momento aún no había ejecutado ningún merge de esta rama, y lo que sí había ejecutado era el `archify check` de los dos diagramas. Regla para el resto de la entrega: ningún SHA integrado se cita sin salida literal de `verify-branch.sh` o de `git log` en la misma respuesta.

L17 Defecto propio repetido al escribir este Log, y su corrección: cuatro veces usé como ancla de la herramienta `edit` el principio de una entrada siguiente (encabezados `## Tasks`, `## Evidencia por tarea`, «L24 Calibre…», «L13 Commits…») y el resultado fue destruir esa entrada o dejar fragmentos duplicados. En esta última, las entradas quedaron como L12, L15, L16, L14. Reconstruido a L12, L13, L14, L15, L16 con `grep -oE "^L[0-9]+"` como comprobación, que es la que detecta el desorden; la comprobación se corre ahora en cada escritura del documento. Regla de casa que sale de aquí: al insertar en un documento con anclas cortas, la ancla debe ser el principio del texto que se va a conservar, nunca el encabezado o la entrada que otra edición va a reescribir.
