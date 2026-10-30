# Proceso de una ronda de pruebas

Las cinco fases del método, con sus artefactos y su criterio de salida. El orden es real: saltarse una fase no la elimina, la desplaza al final, donde cuesta más. Las fases A y B pueden durar minutos en una ronda pequeña; eso no las hace opcionales.

## Fase A: Entender y delimitar

**Artefacto:** la necesidad contrastable y el riesgo clasificado.

- Escribe qué debe hacer el sistema y qué cuenta como fallo. Este criterio es la vara de medir de toda la ronda: sin él, ningún resultado puede ser rojo.
- Clasifica el riesgo: impacto de que falle, probabilidad de que falle. De ahí sale el nivel de la escalera.
- Fija el criterio de salida: qué debe estar ejecutado, qué resultado global se admite y qué se documentará como no verificado. Escrito antes, evita que la ronda termine cuando se acaba la paciencia.

**Criterio de salida:** hay necesidad escrita, riesgo clasificado y criterio de salida. Si falta, no se diseñan casos.

## Fase B: Planificar

**Artefacto:** alcance con exclusiones y reparto por niveles y técnicas.

- Elige niveles y técnicas desde el riesgo con las reglas de [test-design](test-design.md). Cada bloque de riesgo queda asignado a un ángulo.
- Escribe las exclusiones con su motivo. Una exclusión escrita es una decisión revisable; una callada es un hueco que nadie asumirá.
- Si la ronda merece informe, crea el documento desde `assets/test-report.md` con resultado pendiente y reserva los ids de casos que tocarán.
- Decide qué entra en la suite del proyecto: todo caso que vaya a repetirse en cada cambio es automatizable; anótalo en lecciones si no puede automatizarse ahora.

**Criterio de salida:** cada riesgo tiene nivel, técnica y prioridad, o su exclusión con motivo.

## Fase C: Diseñar los casos

**Artefacto:** los casos escritos y la puerta de forma en verde.

- Parte de `assets/test-case.md` para cada caso. El resultado esperado se escribe antes de ejecutar; después solo puede escribirse lo observado.
- Un caso declara su ángulo en Notas: partición, límite, columna de decisión o transición que cubre. Sin ángulo, revisa si duplica a otro.
- Pasa cada caso por `python3 scripts/case-check.py <fichero>`. La puerta comprueba forma: secciones, enumerados, pasos numerados, sin placeholders. No comprueba que el diseño sea bueno; eso lo revisa la fase A con el criterio.
- Los datos de prueba se eligen con la misma técnica que el ángulo: representantes reales de cada clase, no ejemplos decorativos.

**Criterio de salida:** todos los casos pasan la puerta y cubren los riesgos de la fase B, con sus exclusiones reflejadas.

## Fase D: Ejecutar y triar

**Artefacto:** casos con estado y evidencia; defectos reportados.

- Ejecuta en orden de prioridad. Actualiza en el propio caso: resultado observado, estado y evidencia. La evidencia es lo que queda tras la ejecución: salida, captura, registro; no la memoria de quien ejecutó.
- Un fallo se reporta reproducible: entorno, pasos, esperado y observado separados. La anatomía del reporte está en [reporting](reporting.md).
- Los bloqueados se declaran con su motivo y se pide lo que falta; no se convierten en fallados ni desaparecen de las métricas.
- Si aparece un defecto fuera del alcance, se registra en Notas del caso y se decide después; perseguirlo ahora es ampliar el alcance sin decisión.
- Un resultado inestable no se promedia ni se reintenta hasta que «pase»: se aísla la causa. La inestabilidad es un hallazgo.

**Criterio de salida:** todos los casos del alcance tienen estado y evidencia, y cada fallo tiene su reporte.

## Fase E: Cerrar e informar

**Artefacto:** el informe completo y las lecciones.

- Rellena el informe: resultado global, cobertura con lo no probado y su motivo, defectos con severidad y prioridad, métricas cuadradas con los estados.
- La sección No verificado se escribe siempre. «Ninguno conocido» es una afirmación; el silencio no lo es.
- Pasa el informe por la puerta: `python3 scripts/case-check.py <informe>`.
- Cierra con lecciones accionables: qué ángulo faltó, qué técnica habría encontrado antes cada defecto, qué se automatiza y qué riesgo queda en vigilancia.

**Criterio de salida:** informe en verde ante la puerta, lecciones escritas y riesgos residuales nombrados.

## Proporcionalidad del proceso

- Ronda pequeña: fases A y B en un párrafo, un humo dirigido, sin plantilla ni informe. La proporcionalidad está en el contrato.
- Ronda media: casos escritos con plantilla y puerta, cierre en conversación con métricas cuadradas.
- Ronda completa: todo lo anterior más informe con plantilla, lecciones y riesgos residuales. El plan formal solo se escribe si alguien lo va a leer.
