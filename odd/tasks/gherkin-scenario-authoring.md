# gherkin-scenario-authoring

Skill de autoría de `.feature` en `src/gherkin-scenario-authoring/`, su documentación en `docs/gherkin-scenario-authoring/`, y la extracción del comprobador a `tools/check-feature.py` para que ambas skills compartan una sola copia. Dos ramas cortas desde `main`: `refactor/shared-gherkin-checker` para la extracción y `feature/gherkin-scenario-authoring` para la skill.

Contexto: `feature/gherkin-scenario-review` ya está integrada en `main` (`bbc8e00`, ascendencia verificada). La skill de revisión solo revisa; esta nueva produce el artefacto que aquella califica.

## Specs

S1. La skill se crea en `src/gherkin-scenario-authoring`, el campo `name` coincide exactamente con el directorio, y cumple la regla de empaquetado del repositorio: dentro del paquete no hay `README.md`, `CHANGELOG.md` ni guía de instalación.

S2. Alcance decidido por el usuario (literal de sus dos selecciones): «Escribir el .feature desde texto aportado» y «Descubrir comportamientos (Example Mapping, three amigos)». Quedan fuera, por no seleccionadas: «Convenciones de carpeta y nomenclatura» como ruta propia y «Step definitions y automatización». La skill no escribe código de automatización ni redefine dónde vive cada archivo más allá de la convención que el propio proyecto declare.

S3. Separación de papeles: la skill que escribe no es la que califica. Su puerta de salida es `python tools/check-feature.py --path <archivo>` con exit 0, y eso es una comprobación mecánica, no un veredicto de calidad. El informe de `APTO`/`APTO CON RESERVAS`/`NO APTO` lo emite `gherkin-scenario-review`. La skill nueva no se autoasigna ese veredicto ni lo cita como propio.

S4. Extracción compartida: `src/gherkin-scenario-review/scripts/check-feature.py` se mueve a `tools/check-feature.py` con `git mv` para conservar el historial, sin cambiar su comportamiento. Se actualizan todas las referencias: `SKILL.md` de la revisión, `references/four-rules.md`, `assets/checklist-four-rules.md`, la página `docs/gherkin-scenario-review/index.html`, las dos especificaciones archify y sus HTML regenerados con recibo nuevo, `README.md` y `CHANGELOG.md`. Ninguna referencia vieja al path anterior puede quedar en el repositorio.

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

## Log

L1 (petición original, literal): «antes de la integración, quiero saber, esta skill verifica un archivo .feature por lo que he leido. Quién escribe ese archivo??»

L2 Diagnóstico del orquestador, con evidencia: la skill integrada prohíbe escribir (invariante 1 del `SKILL.md` y disparadores negativos de la `description`), `assets/` no contiene ninguna plantilla de autoría y nada en `src/` ni `.skills/` produce `.feature`. Existe un verificador sin productor.

L3 (decisiones del usuario, cuestionario de tres preguntas): integración = «Sí, integra ahora con --no-ff»; alcance de la skill nueva = «Escribir el .feature desde texto aportado» y «Descubrir comportamientos (Example Mapping, three amigos)»; script = «Ruta compartida del repo».

L4 Integración ejecutada: `main` → `bbc8e00 chore(gherkin-review): merge feature/gherkin-scenario-review`, merge no fast-forward, `verify-branch.sh feature/gherkin-scenario-review main` sale `OK` con exit 0, 23 ficheros de la skill en `main`, árbol limpio. La rama `feature/gherkin-scenario-review` se conserva hasta decisión contraria.

L5 Decisión de interpretación: la ruta compartida del script es `tools/check-feature.py`, un solo fichero, sin subcarpetas. Justificación: la guía del repositorio dice que el código de librería de larga vida pertenece a los directorios CLI del repositorio y no al paquete de una skill. Consecuencia asumida y escrita en S5: el paquete deja de ser autónomo y una skill depende de la ruta compartida.

L6 Decisión de interpretación: el alcance elegido no incluye la automatización, así que la skill nueva tampoco necesita las referencias por stack. Si más adelante se pide el automatizador, es una tercera skill, no una ampliación de esta.
