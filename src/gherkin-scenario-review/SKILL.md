---
name: gherkin-scenario-review
description: "Revisa archivos .feature de Gherkin contra las cuatro reglas de calidad de BDD — legibilidad sin contexto, un comportamiento por escenario, un ejemplo por clase de equivalencia y lenguaje consistente en tercera persona — con un script determinista que mide orden de pasos, pares Cuando/Entonces duplicados, longitud, mezcla de punto de vista y filas redundantes de Examples, y devuelve un informe con veredicto APTO, APTO CON RESERVAS o NO APTO. Úsala cuando el agente deba auditar, revisar o validar escenarios Gherkin ya escritos, archivos .feature de Cucumber, SpecFlow, Reqnroll, behave o pytest-bdd, o cuando detecte un muro de texto, un escenario con varios comportamientos, un Scenario Outline con filas de más o pasos que filtran detalles de automatización. No la uses para descubrir comportamientos, escribir escenarios desde una historia de usuario, redactar step definitions ni automatizar pruebas, escribir requisitos SHALL o delta specs de SDD, ni auditar suites de tests unitarios."
---

# Revisión de escenarios Gherkin

Revisa un `.feature` ya escrito y decide si cumple las cuatro reglas de buen Gherkin. La salida es un informe con evidencia por línea, no una reescritura del archivo: el producto de BDD es el mismo artefacto que sirve de requerimiento, criterio de aceptación y caso de prueba, así que la revisión tiene que decir con precisión qué regla falla, dónde y cómo se vería la versión correcta.

No opina de estrategia, de cobertura de negocio ni de código de automatización. Se limita al artefacto de comportamiento.

## Invariantes obligatorias

1. Esta skill solo revisa texto Gherkin que ya existe: un archivo `.feature` o un bloque de escenarios aportado en el encargo. Si el encargo pide descubrir comportamientos, escribir escenarios desde una historia de usuario o implementar la automatización, se declara el fuera de alcance y se revisa únicamente lo que ya esté escrito.
2. El archivo del usuario no se modifica. Cada hallazgo lleva una reescritura propuesta dentro del informe; aplicar esa reescritura es un encargo aparte.
3. Ninguna revisión de memoria. Se ejecuta `scripts/check-feature.py` sobre cada archivo y se leen las referencias aplicables antes de emitir un veredicto. La regla se cita por nombre y por número.
4. Se separa hecho de estimación. Lo que mide el script es un hecho reproducible; lo que juzga el criterio sobre legibilidad, equivalencia o independencia de un comportamiento es estimación. Un hallazgo de estimación no se redacta como violación determinista, y un `APTO` nunca se apoya solo en estimaciones.
5. Cada hallazgo cita regla, archivo, número de línea y evidencia literal del paso. Sin línea citada no hay hallazgo.
6. Un escenario con más de un comportamiento es el hallazgo de mayor prioridad. No se propone dividirlo sin nombrar qué comportamiento queda en cada parte y qué `Dado` nuevo lo situaría.
7. El vocabulario del veredicto es cerrado: `APTO`, `APTO CON RESERVAS`, `NO APTO`. No existen «se ve bien», «podría mejorarse» ni porcentajes de calidad.
8. No se inventan comandos de runner. Un comando de automatización sale solo de la referencia de stack correspondiente; si la referencia no lo documenta, se omite el comando y se declara que el parseo no está verificado por el runner.
9. Ante un archivo que no es Gherkin, o un bloque sin pasos, no se asigna veredicto: se informa `FUERA DE ALCANCE` con el motivo.
10. La revisión no declara que un escenario pasa, falla o está automatizado. Solo declara su calidad como especificación.

## Procedimiento

### Paso 1 — Delimitar el encargo

1. Enumera los archivos o bloques `.feature` a revisar y el idioma de las palabras clave (`Given/When/Then`, `Dado/Cuando/Entonces`, o `# language:` declarado).
2. Aplica la invariante 1. Si el encargo es escribir, descubrir o automatizar, para y di qué parte del encargo sí es revisable.
3. Registra si el proyecto declara un stack y un runner. Con stack declarado, reserva el paso 7; sin stack declarado, el paso 7 se limita a señalar que la automatizabilidad no está verificada.

### Paso 2 — Comprobación determinista

Ejecuta el script por archivo y conserva stdout, stderr y el código de salida:

~~~bash
python scripts/check-feature.py --path features/documentation-build.feature
~~~

1. Con `--json` cuando el informe necesite volcar los hallazgos sin reescribirlos a mano.
2. El código `2` significa uso inválido: corrige la invocación antes de seguir. No sustituyas el script por un parseo improvisado.
3. Los candidatos que el script marca como heurística (`person-mixed`, `low-level-vocab`, `redundant-examples`, `no-subject-verb`) entran al informe solo después de confirmarlos en los pasos 4 a 6. Un candidato refutado se declara refutado con su motivo.

### Paso 3 — Regla 2: un escenario, un comportamiento

Lee [references/four-rules.md](references/four-rules.md) y [references/structure-and-order.md](references/structure-and-order.md).

1. Busca pares `Cuando`/`Entonces` duplicados, `Cuando` después del primer `Entonces` y cambios de actor o de objeto dentro del mismo escenario.
2. Comprueba si el título del escenario anuncia todo lo que el cuerpo hace.
3. Para cada escenario con más de un comportamiento, escribe las dos reescrituras propuestas, cada una con su `Dado` situacional: un escenario puede empezar en mitad de la acción, no hace falta volver al login o a la portada.

### Paso 4 — Regla 1: legible, conciso, sin muro de texto

Con los dos ficheros del paso 3 ya leídos:

1. Descarta escenarios que no sean especificación (`Dado` que declara una intención de negocio en lugar de un estado inicial).
2. Mide la longitud de cada escenario contando pasos, incluidos los de `Background`.
3. Marca los pasos que comunican el cómo en lugar del qué: clics, esperas, navego a la URL, tecleo, botón concreto.
4. Verifica el orden estricto `Dado → Cuando → Entonces` y que cada palabra clave esté en su tipo de paso.

### Paso 5 — Regla 3: un ejemplo por clase de equivalencia

Lee [references/equivalence-classes.md](references/equivalence-classes.md).

1. En cada `Scenario Outline`, agrupa las filas de `Examples` por lo que el escenario verifica de verdad.
2. Estima el coste de ejecución de las filas redundantes cuando el escenario sea de UI.
3. Señala las tablas que se han hinchado añadiendo columnas que no cambian el comportamiento.

### Paso 6 — Regla 4: lenguaje y punto de vista

Lee [references/language-and-voice.md](references/language-and-voice.md).

1. Decide el punto de vista dominante del archivo y marca los pasos que lo rompen.
2. Marca los pasos sin sujeto o sin verbo, y los que no se entienden fuera del contexto de su escenario.
3. Escribe la reescritura como frase sujeto-predicado completa.

### Paso 7 — Automatizabilidad y stack

Solo con stack declarado en el paso 1: lee [references/stack-detection.md](references/stack-detection.md) y después la referencia del stack detectado (`references/stack-javascript.md`, `references/stack-python.md`, `references/stack-java.md`, `references/stack-dotnet.md` o `references/stack-go.md`), una sola.

1. Comprueba con esa referencia si los detalles de bajo nivel señalados en el paso 4 pertenecen a hooks del runner.
2. Declara si los pasos son definibles como `step definitions` con el estilo de coincidencia de ese stack.
3. Si la referencia documenta un comando de parseo o de dry-run y el proyecto lo tiene instalado, ejecútalo como evidencia de parseo. Sin evidencia de ejecución, la automatizabilidad queda declarada como no verificada.

### Paso 8 — Informe y cierre

1. Rellena [assets/review-report-template.md](assets/review-report-template.md) con un veredicto por escenario y el veredicto de archivo.
2. Pasa [assets/checklist-four-rules.md](assets/checklist-four-rules.md) y copia su resultado en el informe.
3. No entregues el informe sin el código de salida del script y sin la cita de línea de cada hallazgo.

## Gestión de errores

- El script no reconoce las palabras clave del archivo: revisa con los dos conjuntos (inglés y español), dilo en el informe y marca el parseo como pendiente de `# language:`.
- `Examples` mal formada o con número de columnas distinto al de los placeholders: hallazgo estructural, `NO APTO` para ese escenario, sin adivinar filas.
- Escenario sin `Entonces`: no hay verificación, así que no hay criterio de aceptación. `NO APTO`.
- El encargo aporta solo prosa o una historia de usuario: `FUERA DE ALCANCE`, sin veredicto.
- Dos archivos del mismo proyecto definen pasos equivalentes con redacción distinta: se informa como riesgo de reutilización de pasos, citando ambos archivos.

## Resultado de la revisión

El informe cierra con:

1. veredicto por escenario con su veredicto de archivo;
2. recuento de violaciones deterministas confirmadas por el script y de estimaciones confirmadas por el criterio;
3. los candidatos refutados, con el motivo;
4. lo que no se pudo verificar y por qué.

`NO APTO` si hay al menos una violación determinista de regla 2, un escenario sin `Entonces`, un orden de pasos imposible o un bloque no parseable. `APTO CON RESERVAS` si no hay violaciones deterministas de esas y existen hallazgos de estimación, o violaciones menores de lenguaje. `APTO` si no queda ningún hallazgo con impacto después de refutar candidatos.

## Referencias

- [references/four-rules.md](references/four-rules.md) — las cuatro reglas como comprobaciones, con ejemplos MAL y BIEN. Léela en el paso 3.
- [references/structure-and-order.md](references/structure-and-order.md) — orden de pasos, longitud, cronología, qué pertenece a hooks. Léela en los pasos 3 y 4.
- [references/equivalence-classes.md](references/equivalence-classes.md) — clases de equivalencia y `Scenario Outline`. Léela en el paso 5.
- [references/language-and-voice.md](references/language-and-voice.md) — punto de vista, frase sujeto-predicado, paso legible suelto. Léela en el paso 6.
- [references/stack-detection.md](references/stack-detection.md) — cómo se decide el stack y qué referencia cargar. Léela en el paso 7.
- `references/stack-<stack>.md` — palabras clave, estilo de coincidencia de pasos, sitio de los hooks, filtrado por etiquetas y el comando de parseo o dry-run verificado con su fuente; cuando la documentación del runner no documenta ninguno, la referencia lo declara con la línea de fallback y la automatizabilidad se reporta como no verificada. Solo la del stack detectado.
- [assets/review-report-template.md](assets/review-report-template.md) — forma obligatoria del informe.
- [assets/checklist-four-rules.md](assets/checklist-four-rules.md) — lista de las cuatro preguntas por escenario.
- `assets/example-feature-good.feature` y `assets/example-feature-bad.feature` — referencia del nivel esperado y fixture del script.
