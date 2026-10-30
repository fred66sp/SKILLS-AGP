---
name: software-testing
description: "Aplica método de prueba al software: entiende el riesgo, elige qué probar con niveles y técnicas de diseño, ejecuta con evidencia y cierra con un informe honesto que separa lo comprobado de lo no verificado. Se activa al planificar una ronda de pruebas, diseñar casos, fijar prioridades y criterio de salida, triar fallos o escribir informes de pruebas y defectos. No ejecuta la puerta del lenguaje ni sustituye al runner del proyecto, que pertenecen a las skills de verificación por lenguaje; tampoco conduce navegadores (playwright-cli-usage) ni decide calidad visual (web-interface-visual-design)."
metadata:
  version: "0.1.0"
---

# Pruebas de software con método

Probar no es acumular casos: es reducir la incertidumbre sobre un riesgo concreto con la menor cantidad de evidencia suficiente. Este contrato ordena ese trabajo en decisiones: qué probar, con qué ángulo, en qué orden, cuándo parar y qué afirmar al cerrar. Las plantillas fijan la forma y la puerta `case-check.py` la comprueba; la verdad del resultado la sostiene la evidencia, no el documento.

## Responsabilidad y límites

- Posee el método de prueba: el análisis de riesgo, la elección de niveles y técnicas, el diseño de casos, el criterio de salida, el triaje de fallos y el informe. Posee también las plantillas del paquete y la puerta de forma `scripts/case-check.py`.
- No posee la suite ni la puerta del lenguaje. Si el proyecto tiene runner, manda el suyo: esta skill diseña y decide, el runner ejecuta y verifica. La puerta de cada lenguaje es la de su skill de verificación.
- No posee el navegador ni el juicio visual. Una prueba de interfaz usa `playwright-cli-usage` para el render y entrega su evidencia al criterio de `web-interface-visual-design`.
- No posee las pruebas de seguridad. Comprobar una validación funcional no es atacar una superficie: eso es `security-engineering`.
- No posee la corrección del defecto. Reportar no es arreglar: la corrección sigue el flujo del proyecto y, si procede, su skill de verificación la cierra.
- No posee la verdad. Un informe superado afirma lo que la evidencia observada demuestra y nada más; el resto se escribe como no verificado.

## Principios

Siete reglas que limitan lo que la prueba puede afirmar. Cada una con su consecuencia operativa; el desarrollo está en [principles](references/principles.md).

1. La prueba demuestra presencia de defectos, no su ausencia: un resultado verde no certifica que el sistema funciona, solo que los casos escritos pasan.
2. Probarlo todo es imposible: el riesgo decide el conjunto. Prioridad es impacto por probabilidad, no orden alfabético.
3. Antes es más barato: contrastar el criterio de aceptación antes de implementar encuentra más por menos que cualquier ronda tardía.
4. Los defectos se agrupan: donde ya falló o es complejo, vuelve a fallar. Concentra el esfuerzo ahí.
5. La misma prueba repetida deja de encontrar defectos nuevos: si una suite solo crece en líneas y no en ángulos, se ha podrido.
6. El contexto decide el método: una CLI, una API y una interfaz no se prueban igual. La escalera se elige por contexto, no por costumbre.
7. Sin defectos encontrados no es un objetivo: un sistema limpio que no resuelve la necesidad es un fracaso. La prueba contrasta contra la necesidad, no contra sí misma.

## Escalera de proporcionalidad

Elige el nivel más bajo que reduzca la incertidumbre del riesgo y declara el nivel antes de empezar:

| Nivel | Cuándo | Coste |
|---|---|---|
| Revisión sin ejecutar | El criterio es ambiguo o el diseño contradice la necesidad | Mínimo |
| Humo dirigido | Una ruta crítica después de un cambio contenido | Acotado |
| Casos escritos | El riesgo merece evidencia que se repita y se archive | Medio |
| Ronda completa | Cambio grande, código heredado o entrega con criterio formal | Justificado con plan e informe |

- Un humo no necesita plantilla; un caso escrito sí, y pasa por `scripts/case-check.py`.
- Si el caso se repite en cada cambio, su destino es la suite del proyecto, no más ejecuciones manuales.
- Lee [test-design](references/test-design.md) antes de diseñar casos de una ronda con riesgo medio o alto.

## Procedimiento

**Fase A: Entender y delimitar.**
1. Escribe la necesidad que se va a contrastar y qué cuenta como fallo. Sin ese criterio, la prueba no puede fallar y por tanto no puede demostrar nada.
2. Clasifica el riesgo: qué rompe este cambio si falla, a quién y con qué coste. Con el riesgo bajo, la escalera se queda en revisión o humo.
3. Fija el criterio de salida: qué debe estar ejecutado, qué resultado global se admite y qué se documenta como no verificado. Lee [process](references/process.md).

**Fase B: Planificar.**
1. Elige niveles y técnicas por partición de riesgo, no por volumen. Las técnicas están en [test-design](references/test-design.md).
2. Declara el alcance con exclusiones: qué queda fuera y por qué. Una exclusión escrita es una decisión; una callada es un hueco.
3. Si la ronda merece informe, reserva el número y crea el documento desde `assets/test-report.md` con resultado pendiente.

**Fase C: Diseñar los casos.**
1. Diseña cada caso desde una técnica: partición de equivalencia, valores límite, tabla de decisión o transición de estados. Un caso sin ángulo declarado es un caso que solo repite otro.
2. Parte de `assets/test-case.md`. El resultado esperado se escribe antes de ejecutar; lo que se escribe después es una crónica, no una prueba.
3. Pasa cada caso por `python3 scripts/case-check.py <fichero>` y corrige los defectos de forma. La puerta comprueba forma, no verdad.

**Fase D: Ejecutar y triar.**
1. Ejecuta en orden de prioridad y actualiza resultado observado, estado y evidencia en el propio caso. Un paso que no deja rastro no es evidencia.
2. Un fallo solo se reporta reproducible: registra entorno, pasos y diferencia entre lo esperado y lo observado. Lee [reporting](references/reporting.md) antes de escribir el defecto.
3. Si aparece un defecto fuera del alcance de la ronda, se registra en notas y se sigue el caso en curso; perseguirlo es ampliar el alcance sin decisión.
4. Un resultado que baila entre ejecuciones no se promedia: se aísla la causa antes de contar la métrica.

**Fase E: Cerrar e informar.**
1. Rellena el informe desde `assets/test-report.md`: resultado global, cobertura con lo no probado, defectos con severidad y prioridad, métricas coherentes.
2. Pasa el informe por `scripts/case-check.py`. La sección No verificado se escribe siempre, aunque sea «ninguno conocido».
3. Cierra con lecciones accionables: qué ángulo faltó y qué se automatiza. La ronda que no deja lecciones se repetirá igual.

## Evidencia y cierre

- El estado del caso y la evidencia van juntos: superado o fallado sin evidencia observada es un defecto de forma que `case-check.py` rechaza con `E03`.
- Un caso superado demuestra que ese caso pasa con esos datos en ese entorno; no demuestra que la feature funcione ni que el resto del sistema siga en pie.
- La severidad mide el daño del defecto; la prioridad mide su urgencia. No son la misma columna y no siempre coinciden.
- Las métricas del informe se cuadran con los estados: superados más fallados más bloqueados igual a ejecutados. La puerta lo comprueba con `E08`.
- Si algo no se pudo comprobar, se escribe en No verificado con el motivo. No se sustituye por «parece que funciona».

## Errores y paradas

- **No reproducible:** anota entorno, frecuencia y lo que falta para reproducir. Si depende del entorno, es un defecto del entorno y se reporta como tal, no se archiva como fantasma.
- **Bloqueado por datos o permisos:** se detiene, se declara bloqueado con el motivo y se pide lo que falta. No se inventan datos de producción.
- **Flaky:** se aísla la causa —tiempo, orden, dependencia externa— antes de contar la métrica. La inestabilidad es información, no ruido que limpiar con reintentos.
- **Criterio de salida alcanzado:** se para, aunque queden ideas. El presupuesto manda; las ideas restantes se anotan en lecciones.
- **Riesgo no cubierto por ninguna técnica:** se dice en el informe y queda en riesgos residuales. No se disfraza de cobertura.

## Precedencia

- La suite y la puerta del lenguaje del proyecto mandan sobre la ejecución: `go-testing-and-verification`, `typescript-testing-and-verification`, `javascript-testing-and-verification` y `python-testing-and-verification`. Esta skill posee el método y el diseño; esas skills, el binario y el cierre del lenguaje.
- `playwright-cli-usage` posee la conducción del navegador que una prueba de interfaz necesite. Aquí se decide qué observar; allí, cómo abrirlo y cerrarlo.
- `web-interface-visual-design` posee el juicio visual. La evidencia de render que produce una prueba la evalúa ese contrato, no este.
- `security-engineering` posee las pruebas de seguridad. Aquí no se ataca una superficie: se comprueba la necesidad declarada.
- `document-redactor` posee la prosa del informe si se va a publicar. Las plantillas fijan la forma; la redacción, el registro y el ritmo.
