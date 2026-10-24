---
name: prd-cartographer
description: "Produce y revisa Product Requirements Documents (PRD) verificables y trazables: separa evidencia, decisiones, inferencias, hipótesis y desconocidos; exige métricas medibles, alcance con exclusiones y criterios de aceptación observables; y declara un estado de preparación explícito en lugar de un documento aparentemente completo. Úsala cuando haya que transformar una idea, una investigación, un concepto de producto o un encargo ambiguo en un PRD para producto, diseño, ingeniería y QA, o revisar y auditar un PRD existente. No la uses para diseño técnico, arquitectura de software, especificación de implementación, documentación técnica general, contenido comercial ni material de marketing."
---

# PRD Cartographer

Produce un PRD que explique qué se construye, para quién, qué problema resuelve y cómo se medirá el resultado. No redactes una especificación técnica: la implementación pertenece a la arquitectura o al diseño técnico.

El documento debe servir para decidir y poder auditarse después. La claridad prevalece sobre la extensión, y un hueco declarado vale más que una afirmación inventada.

## Invariantes del PRD

1. No escribas antes de delimitar la operación —crear, revisar o auditar—, el tipo de producto, la audiencia y las fuentes disponibles.
2. No conviertas una afirmación plausible en un hecho. Toda afirmación material lleva un grado de certeza y, cuando condiciona una decisión, una fuente con localización reproducible.
3. El PRD describe producto: necesidades, comportamientos y resultados. No prescribe colores, píxeles, componentes, tablas de base de datos ni algoritmos salvo que sean una restricción explícita.
4. Si el problema no está entendido o la oportunidad no está validada, no fabriques un PRD concluyente. Entrega un diagnóstico de preparación y el documento de descubrimiento que falta.
5. Una métrica sin definición, método de medida, fuente, línea base, objetivo y plazo no es una métrica: es una intención.
6. Una persona sin evidencia no es una persona: es una hipótesis que debe marcarse como tal.
7. Cada requisito se vincula a una persona, un objetivo, un problema o un riesgo. Un requisito huérfano se elimina o se justifica.
8. `In scope` y `Out of scope` son explícitos. Sin exclusiones, el alcance no está definido.
9. Las contradicciones entre fuentes se exponen y se piden decisiones. No se resuelven con una redacción ambigua.
10. No presentes el PRD como aprobado. Si el usuario no ha aprobado una decisión, el agente la marca como `Propuesta`.
11. No declares terminado un PRD sin ejecutar la puerta de calidad y mostrar su resultado. Un PRD que no supera la puerta se entrega como `PARCIAL` o `NO LISTO`, nunca como listo.

## Procedimiento del PRD

**Paso 1 — Delimitar el encargo.**
1. Identifica la operación: crear un PRD, revisar uno existente o auditar su preparación sin modificarlo.
2. Identifica el tipo: `producto` nuevo o `feature` sobre un producto existente. Para una feature, conserva el contexto del producto y no lo repitas sin necesidad.
3. Identifica la audiencia y la decisión que habilita el PRD: inversión, priorización, diseño, desarrollo, validación o lanzamiento.
4. Si faltan el problema, el usuario o la fuente de una decisión crítica, formula una sola pregunta concreta y detente. No interrogues para rellenar una plantilla.

**Paso 2 — Inventariar las fuentes.**
1. Enumera las fuentes realmente disponibles: archivos, texto aportado, repositorio, entrevistas, datos, analítica, enlaces y decisiones previas.
2. Registra para cada una: tipo, procedencia, fecha visible, alcance y limitación. Si una fecha no es visible, escribe `UNKNOWN`.
3. Extrae afirmaciones atómicas. No mezcles hechos, opiniones, objetivos y propuestas en una sola frase.
4. Lee `references/evidence-and-claims.md` cuando una afirmación no esté directamente sustentada o cuando dos fuentes puedan discrepar.

**Paso 3 — Decidir si procede un PRD.**
1. Comprueba si existe descubrimiento suficiente: problema delimitado, usuarios identificados con evidencia, oportunidad o necesidad sustentada y resultado esperado comprensible.
2. Si no lo hay, entrega un diagnóstico de preparación con `Estado: NO LISTO` y redacta el `Problem Statement` o `Product Concept` que falta. No presentes ese documento como PRD.
3. Si hay evidencia parcial, redacta el PRD como `PARCIAL` y marca cada hueco crítico con `UNKNOWN`, `Hipótesis` o `Parcial`.
4. Formula el **Universal Idea Model**: `Un [objeto] para [usuarios] que [hace algo] para [lograr un resultado]. Los usuarios obtienen [valor] cuando [situación].` Si un campo no puede completarse sin inventar, escribe `UNKNOWN` y explica qué evidencia lo desbloquearía.

**Paso 4 — Fijar problema y concepto.**
1. Describe el problema antes que la solución: entorno, personas afectadas, dinámica, estado actual, síntomas, causas conocidas y estado ideal.
2. Distingue causa demostrada de hipótesis causal. Una correlación no demuestra una causa.
3. Describe el concepto: contexto, usuarios y necesidades, experiencia o factor de forma, estrategia y monetización solo si aplica.
4. Registra preguntas abiertas y riesgos del concepto antes de convertirlo en requisitos.

**Paso 5 — Redactar el PRD.**
1. Copia la estructura de `assets/prd-template.md` y sustituye cada marcador por contenido concreto. Lee `references/prd-structure.md` para el criterio de cada sección.
2. Escribe en español de España, en imperativo y tercera persona, sin voseo.
3. Redacta cada requisito de forma comprensible, necesaria, no ambigua, comprobable y vinculada a una historia, objetivo o riesgo.
4. Expresa user stories como `Como [persona], quiero [acción], para [beneficio]`. El beneficio no puede ser una operación de interfaz.
5. Escribe criterios de aceptación observables, preferiblemente en formato Given/When/Then.
6. Separa en tablas o etiquetas visibles `hecho`, `decisión aprobada`, `propuesta`, `hipótesis` y `desconocido`.
7. Añade requisitos no funcionales solo cuando estén justificados por seguridad, privacidad, accesibilidad, rendimiento, disponibilidad, cumplimiento o compatibilidad.

**Paso 6 — Revisar coherencia y calidad.**
1. Busca contradicciones entre problema, usuarios, objetivos, funcionalidades, métricas, alcance y dependencias.
2. Comprueba que cada funcionalidad tiene persona, objetivo o problema; que cada métrica tiene método; que cada exclusión no contradice los objetivos; y que ninguna dependencia no verificada se presenta como disponible.
3. Lee `references/quality-gate.md` y ejecuta todas sus comprobaciones. No abuses del veredicto `LISTO PARA REVISIÓN`.
4. Si una afirmación no se sostiene, baja su grado o retírala. No la maquilles con lenguaje seguro.

**Paso 7 — Planificar validación y mantenimiento.**
1. Define qué debe revisar producto, diseño, ingeniería, QA y usuarios reales. Asigna cada validación a una evidencia o acción concreta.
2. Incluye versión, fecha, estado, propietario, historial de cambios y condiciones que obligan a revisar el PRD.
3. Trata el PRD como documento vivo: debe reflejar lo que el equipo cree actualmente, no lo que creía al aprobarse.

**Paso 8 — Cerrar con evidencia.**
1. Copia la estructura de `assets/delivery-template.md` y rellena cada campo con evidencia.
2. Enumera las fuentes inventariadas, las afirmaciones críticas con su trazabilidad, las contradicciones, los `UNKNOWN` y las decisiones pendientes.
3. Declara el resultado de la puerta de calidad y las validaciones humanas que faltan.
4. Si un campo no puede rellenarse con evidencia, ese campo es el hallazgo.

## Errores y paradas del PRD

- Si el usuario pide un PRD completo pero solo aporta una idea sin usuarios, problema ni datos, entrega el diagnóstico de preparación y el `Problem Statement`. No rellenes el PRD con categorías genéricas.
- Si dos fuentes discrepan, expón ambas y pide decisión. No elijas la más reciente sin evidencia de sustitución, revisión o anulación explícita.
- Si una fuente externa no se puede consultar en la versión usada por el producto, no le atribuyas comportamiento: declara la limitación.
- Si el encargo mezcla producto y solución técnica, separa el requisito de producto y deja la decisión técnica como dependencia o pregunta abierta.
- Si detectas una contradicción crítica que impide decidir, el veredicto es `NO LISTO` aunque el resto del documento esté completo.
- Si el usuario aprueba una propuesta durante el trabajo, conviértela en `Decisión aprobada` y registra quién la aprobó y con qué alcance.

## Resultado del PRD

Cierra siempre con este bloque, rellenado con evidencia y sin adjetivos:

```text
Estado de preparación: <LISTO | PARCIAL | NO LISTO>
Documento entregado: <PRD completo | diagnóstico de preparación | revisión de PRD existente>
Fuentes inventariadas: <lista con procedencia y alcance, o "ninguna">
Afirmaciones críticas y trazabilidad: <tabla o referencia al anexo>
Contradicciones y UNKNOWN: <lista, o "ninguno">
Decisiones pendientes: <lista con la pregunta exacta que las desbloquea, o "ninguna">
Validaciones necesarias: <producto, diseño, ingeniería, QA, usuarios>
Veredicto de la puerta de calidad: <LISTO PARA REVISIÓN | PARCIAL | NO LISTO>
```

No presentes el PRD como aprobado. Si el usuario no ha dado aprobación, marca las decisiones del agente como `Propuesta`.

## Referencias del paquete de PRD

- [evidence-and-claims](references/evidence-and-claims.md) — grados de certeza, comparación de fuentes y límites de la verificación. Léelo en el paso 2 y cuando una afirmación crítica no esté sustentada.
- [prd-structure](references/prd-structure.md) — criterio de cada sección, métricas, personas, requisitos y criterios de aceptación. Léelo en el paso 5.
- [quality-gate](references/quality-gate.md) — comprobaciones previas a declarar un PRD preparado para revisión. Léelo en el paso 6.
- [prd-template](assets/prd-template.md) — estructura mínima del PRD. Cópiala en el paso 5.
- [delivery-template](assets/delivery-template.md) — formato de cierre. Cópialo en el paso 8.
