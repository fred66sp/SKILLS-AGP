---
name: gherkin-scenario-authoring
description: "Descubre comportamientos y escribe archivos .feature de Gherkin bajo las cuatro reglas de calidad de BDD: un comportamiento por escenario, orden Dado/Cuando/Entonces, un ejemplo por clase de equivalencia y tercera persona con frases sujeto-predicado. Produce el mapa de reglas, ejemplos y preguntas abiertas antes de redactar el primer escenario y no entrega el archivo mientras el comprobador compartido `tools/check-feature.py` no sale con código 0. Úsala cuando el agente deba convertir una historia de usuario, un criterio de aceptación, prosa de comportamiento o una discusión de equipo en escenarios Gherkin, o cuando necesite Example Mapping y three amigos para acotar qué se especifica antes de escribir. No la uses para auditar `.feature` ya escritos (eso lo hace la skill gherkin-scenario-review), ni para redactar step definitions, instalar runners o automatizar pruebas, ni para escribir requisitos SHALL o delta specs de SDD, ni para decidir arquitectura de pruebas o cobertura de una suite."
---

# Escritura de escenarios Gherkin

Descubre el comportamiento y escríbelo como `.feature`. El artefacto vale tres: requerimiento, criterio de aceptación y caso de prueba. Por eso la salida se mide con la misma comprobación que leerá quien revise: si el archivo no pasa el comprobador, no está terminado.

Esta skill produce; no califica. Su puerta es mecánica (exit 0 del comprobador). El veredicto de calidad —`APTO`, `APTO CON RESERVAS`, `NO APTO`— lo emite `gherkin-scenario-review`, y esta skill no se lo atribuye a sí misma.

## Invariantes obligatorias

1. No se redacta ningún escenario mientras quede una pregunta abierta que pueda cambiar el comportamiento. Las preguntas se entregan listadas y sin resolver; no se cierran por suposición.
2. Un escenario, un comportamiento. Si el borrador tiene dos ciclos acción-verificación, se divide antes de escribir, y cada parte se sitúa con su propio `Dado`, aunque empiece en mitad de la acción.
3. El producto es `.feature`. No se emiten `### Requirement:`, ni `SHALL`, ni delta specs: ese territorio es de las skills de especificación.
4. Puerta de salida obligatoria: `python tools/check-feature.py --path <archivo.feature>` desde la raíz del repositorio, con exit 0. Sin exit 0 no se entrega el archivo, se entrega el fallo con sus líneas.
5. Exit 0 no es calidad. Es la comprobación mecánica de estructura, orden y longitud; la legibilidad y la independencia del comportamiento las juzga la skill de revisión.
6. El comprobador es una CLI compartida del repositorio, no una pieza de este paquete: se busca por esa ruta y desde la raíz. Si `tools/check-feature.py` no existe, se informa la ruta que falta y se para; no se escribe un parseo propio.
7. Los ejemplos del archivo modelan desarrollo de software (compilación de documentación, códigos de salida de una CLI, pasos de un pipeline de CI, hallazgos de un validador). Nunca e-commerce ni compra de zapatos.
8. El idioma se declara: encabezado `# language:` explícito, `es` o `en` según el proyecto destino o el encargo. Los pasos van en tercera persona con frases sujeto-predicado que se entiendan sueltas.
9. Un `.feature` existente no se reescribe por reflejo. Si el encargo es ampliar, se preservan los escenarios que no atañen al comportamiento nuevo y se muestran en el diff los que cambiaron y por qué.
10. No se escribe código de automatización: ni step definitions, ni configuración de runners, ni hooks. Es una tercera skill, no una ampliación de esta.

## Procedimiento

### Paso 1 — Clasificar el encargo

1. Decide la ruta: descubrir, escribir, o ambas. Con una historia de usuario sin ejemplos concretos, la ruta empieza en descubrir; con ejemplos ya acordados, empieza en escribir.
2. Registra la entrada disponible: historia, criterio de aceptación, prosa de comportamiento, defecto real o spec existente.
3. Aplica la invariante 10 y la 3. Si el encargo pide automatizar o redactar requisitos SHALL, declara el fuera de alcance y sigue solo con lo escribible.
4. Si no hay suficiente material para identificar un comportamiento, pregunta una vez, con la laguna concreta. No preguntes por convenciones de nombres ni por la ruta de la carpeta: usa la que declare el proyecto y, si no declara, propón una y dilo.

### Paso 2 — Descubrir el comportamiento

Lee [references/behavior-discovery.md](references/behavior-discovery.md) y rellena [assets/behavior-map-template.md](assets/behavior-map-template.md).

1. Escribe la regla del negocio, no la funcionalidad: qué hace el sistema y por qué importa.
2. Por cada regla, al menos un ejemplo concreto con datos reales del dominio del proyecto.
3. Lista las preguntas abiertas. Cada pregunta que admite dos resultados posibles distintos bloquea el paso 3.
4. Reduce: si dos ejemplos comprueban lo mismo, son la misma clase de equivalencia y sobra uno.

### Paso 3 — Redactar los escenarios

Lee [references/writing-rules.md](references/writing-rules.md) y copia la forma de [assets/feature-template.feature](assets/feature-template.feature).

1. Un escenario por comportamiento, con el `Dado` que lo sitúa.
2. Orden estricto `Dado → Cuando → Entonces`; `Y` solo encadenado dentro del mismo tipo de paso.
3. Longitud de un dígito contando `Antecedentes`. Si te pasas, sube de nivel: el detalle mecánico no pertenece al Gherkin.
4. `Esquema del escenario` solo cuando las filas sean clases de equivalencia distintas. Dos filas de la misma clase es un error, no cobertura.
5. Si un paso no se entiende fuera del escenario, reescríbelo con sujeto y predicado completos.

### Paso 4 — Comprobar antes de entregar

~~~bash
python tools/check-feature.py --path features/compilacion-de-documentacion.feature
~~~

1. Con `--json` si necesitas volcar los hallazgos sin reescribirlos.
2. Violación de estructura, orden o longitud: se corrige la redacción. Si la corrección cambia lo que se especifica, se vuelve al paso 2 y se declara.
3. Candidato heurístico (`low-level-vocab`, `person-mixed`, `no-subject-verb`, `redundant-examples`, `business-intent-given`): se resuelve antes de entregar; el comprobador no lo exige, la invariante 8 y el paso 3 sí.
4. Repite hasta exit 0. Dos iteraciones sin progreso son señal de que el comportamiento está mal descubierto: se vuelve al paso 2 en lugar de retocar palabras.

### Paso 5 — Entregar

Lee [references/handoff-to-review.md](references/handoff-to-review.md) y cierra con su forma de entrega.

1. Qué se escribió: rutas de `.feature` y número de escenarios por archivo.
2. Qué se descubrió: el mapa de reglas, ejemplos y preguntas, incluidas las preguntas abiertas que siguen sin responder.
3. Qué se comprobó: el comando del paso 4, su salida y su exit code.
4. Qué queda fuera: la calificación del artefacto pertenece a `gherkin-scenario-review`; la automatización, a otra skill.

## Gestión de errores

- Falta `tools/check-feature.py`: se informa la ruta esperada y se para. No se entrega sin comprobar, ni se simula la comprobación.
- El encargo aporta una historia sin criterios verificables: se descubre primero (paso 2) y se pregunta la laguna concreta; no se inventan reglas de negocio.
- El proyecto destino ya tiene un `.feature` para la misma funcionalidad: se revisa el solapamiento y se propone ampliar o dividir, mostrando lo que se preservaría.
- El comprobador sale 2: es error de uso o idioma no soportado; se corrige la invocación o el encabezado `# language:`, no el escenario.
- Dos reglas del negocio contradicen la historia: se para y se reportan las dos, con la línea del encargo. No se elige una en silencio.

## Referencias

- [references/behavior-discovery.md](references/behavior-discovery.md) — cómo se descubre: regla, ejemplo, pregunta, y cuándo el mapa está listo. Léelo en el paso 2.
- [references/writing-rules.md](references/writing-rules.md) — las cuatro reglas aplicadas al escribir, con pares MAL/BIEN de dominio software. Léelo en el paso 3.
- [references/handoff-to-review.md](references/handoff-to-review.md) — qué se entrega, qué se deja de declarar y cómo se lee el exit 0. Léelo en el paso 5.
- [assets/feature-template.feature](assets/feature-template.feature) — forma del archivo: encabezado, `# language:`, historia de usuario en la documentación, un escenario y un esquema.
- [assets/behavior-map-template.md](assets/behavior-map-template.md) — forma del mapa de descubrimiento.
- `tools/check-feature.py` — CLI compartida del repositorio. Su salida es la puerta del paso 4; su comportamiento no se reimplementa aquí.
