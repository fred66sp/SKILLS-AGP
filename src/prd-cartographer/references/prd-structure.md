# Estructura y criterio del PRD

Léelo en el paso 5 del procedimiento, antes de redactar o reescribir el PRD.

## Estructura mínima

Incluye estas secciones, aunque alguna declare `UNKNOWN`. No elimines una sección porque falte información: declara el hueco.

| # | Sección | Qué debe responder | Criterio de cierre |
|---|---|---|---|
| 1 | Metadatos | Nombre, tipo, versión, estado, propietario y fuentes | Tipo `producto` o `feature`; fuentes inventariadas |
| 2 | Resumen y propósito | Qué es, para quién y por qué ahora | Se entiende sin leer el resto |
| 3 | Universal Idea Model | Objeto, usuarios, acción, resultado y valor | Campos completos o `UNKNOWN` justificado |
| 4 | Problema y evidencia | Entorno, afectados, dinámica, síntomas, causas y estado ideal | Cada causa distingue hecho de hipótesis |
| 5 | Usuarios objetivo y personas | Quién tiene el problema y en qué contexto | Sin nombres, roles ni frustraciones inventados |
| 6 | Objetivos y resultados esperados | Qué cambia para el usuario y para el negocio | Resultados observables, no actividades |
| 7 | Métricas de éxito | Cómo se sabrá si funcionó | Definición, método, fuente, línea base, objetivo, plazo y umbral de fracaso |
| 8 | Alcance de esta versión | Qué entra y qué queda fuera | `In scope` y `Out of scope` explícitos |
| 9 | Épicas, capacidades y user stories | Qué se construye y para qué | Cada historia tiene persona, acción y beneficio |
| 10 | Criterios de aceptación | Cómo se comprueba que está hecho | Observables y verificables, preferiblemente Given/When/Then |
| 11 | Requisitos no funcionales | Qué restricciones de calidad aplican | Solo los justificados por seguridad, privacidad, accesibilidad, rendimiento, disponibilidad, cumplimiento o compatibilidad |
| 12 | Supuestos, restricciones y dependencias | Qué se da por cierto y qué puede fallar | Cada uno con estado y forma de validación |
| 13 | Riesgos y mitigaciones | Qué puede impedir el resultado | Riesgo, probabilidad o impacto cualificado, mitigación y responsable |
| 14 | Preguntas abiertas y decisiones pendientes | Qué falta por decidir | Pregunta exacta, responsable y fecha o condición de respuesta |
| 15 | Plan de validación y revisión | Quién debe validar qué | Producto, diseño, ingeniería, QA y usuarios cuando proceda |
| 16 | Registro de decisiones y changelog | Qué se decidió, cuándo y por qué | Versión, fecha, estado y motivo |
| 17 | Mapa de evidencia y límites | Qué sostiene cada afirmación crítica | Fuente y localización reproducible; límites declarados |

Para un producto nuevo, añade contexto de mercado, propuesta de valor, modelo de negocio, ecosistema de personas, MVP y fases solo si existen fuentes que los sostengan o preséntalos como propuestas. Para una feature, conserva el contexto del producto sin repetirlo innecesariamente.

## Universal Idea Model

Completa la fórmula:

> Un [objeto] para [usuarios] que [hace algo] para [lograr un resultado]. Los usuarios obtienen [valor] cuando [situación].

Si un campo exige inventar, escribe `UNKNOWN` y añade la evidencia que lo desbloquearía. Un modelo incompleto pero honesto es más útil que una frase comercial que nadie puede verificar.

## Problema

El problema se describe antes que la solución. Incluye:

- entorno y contexto donde aparece;
- personas o segmentos afectados y evidencia de que lo están;
- dinámica actual: qué hacen hoy, con qué fricción y qué coste tiene;
- síntomas observables, separados de las causas;
- causas conocidas y causas hipotéticas, con su evidencia;
- estado ideal y qué cambiaría si el problema se resolviera.

No confundas una solución propuesta con una necesidad validada. "Los usuarios quieren un botón de exportar" es una solución; "el cierre mensual exige reconstruir datos a mano" es un problema.

## Personas

Una persona se sustenta en evidencia, no en imaginación. Incluye:

- rol o contexto relevante para el problema;
- necesidad o trabajo que intenta completar;
- comportamiento observado o declarado, con su fuente;
- restricciones que condicionan la solución;
- qué la diferencia de otro segmento, cuando esa diferencia cambia una decisión.

No inventes nombres, edades, cargos, frustraciones ni citas. Si la evidencia solo cubre un segmento, no generalices al resto.

## Objetivos, resultados y métricas

Distingue:

- **objetivo**: el cambio que se persigue;
- **resultado**: lo que el usuario o el negocio podrá observar;
- **salida**: lo que el equipo entrega.

Una métrica de éxito necesita, como mínimo:

| Campo | Contenido |
|---|---|
| Nombre | Qué se mide, sin ambigüedad |
| Definición | Fórmula o criterio exacto |
| Método | Cómo se recoge y calcula |
| Fuente | Sistema, informe o instrumento |
| Línea base | Valor actual; si falta, `UNKNOWN` |
| Objetivo | Valor esperado y dirección del cambio |
| Plazo | Periodo de evaluación |
| Umbral de fracaso | Valor o condición que obliga a reevaluar |

Incluye al menos un resultado de usuario y, cuando proceda, uno de negocio. No escribas una métrica que no pueda medirse con la instrumentación disponible o prevista.

## Alcance

`In scope` enumera lo que esta versión entrega. `Out of scope` enumera lo que queda fuera y, cuando la exclusión pueda sorprender, su motivo. Las exclusiones no pueden contradecir los objetivos de la versión.

No uses "fase 2" como cajón para todo lo difícil sin definir qué condición la desbloquea.

## Épicas, capacidades y user stories

Agrupa el trabajo en épicas o capacidades con resultado propio. Cada user story sigue el formato:

> Como [persona], quiero [acción], para [beneficio].

El beneficio no puede ser una operación de interfaz. "Quiero un desplegable para elegir el informe" no es un beneficio; "quiero comparar periodos sin reconstruir los datos a mano" sí lo es.

Cada historia debe poder rastrearse hasta una persona, un objetivo, un problema o un riesgo. Si no se puede, elimínala o justifica su existencia.

## Criterios de aceptación

Escribe criterios observables y comprobables. Cuando encaje, usa Given/When/Then:

> Dado [contexto], cuando [acción], entonces [resultado observable].

Evita "funciona correctamente", "es intuitivo" o "carga rápido" sin definición. Si el criterio depende de un valor, indica el valor y su fuente.

## Requisitos no funcionales

Añade solo los justificados. Para cada uno, indica la restricción, su motivo y cómo se verificará. No conviertas una preferencia de implementación en requisito de producto.

## Supuestos, restricciones y dependencias

Cada uno lleva:

- enunciado;
- grado de certeza;
- impacto si es falso;
- forma de validación o mitigación;
- responsable y fecha o condición, cuando se conozcan.

Una dependencia no verificada no se presenta como disponible.

## Trazabilidad

Mantén una tabla que conecte las afirmaciones críticas con su evidencia:

| Afirmación crítica | Grado | Fuente | Localización | Límite |
|---|---|---|---|---|
| <afirmación> | <hecho \| decisión \| inferencia \| hipótesis \| parcial \| UNKNOWN> | <documento, entrevista, dato> | <sección, página o consulta> | <qué no cubre> |

La tabla puede vivir como anexo. Lo que no puede faltar es que una afirmación crítica sin trazabilidad quede visible como hueco.

## Registro de decisiones

Registra cada decisión relevante con fecha, estado, responsable y motivo. Incluye las decisiones descartadas cuando su contexto evite repetir una discusión. No conviertas cada detalle en una decisión.

## Criterios de redacción

- Describe necesidades, comportamientos y resultados; no prescribas interfaz, datos ni algoritmos salvo restricción explícita.
- Cada requisito debe ser comprensible, necesario, no ambiguo, comprobable y vinculado a una historia, objetivo o riesgo.
- No escribas métricas sin método de medición, personas sin evidencia ni dependencias sin confirmar.
- Separa siempre `hecho`, `decisión aprobada`, `propuesta`, `hipótesis` y `desconocido` en tablas o etiquetas visibles.
- No uses citas, enlaces, páginas, símbolos ni localizaciones que no hayas podido comprobar.
- Responde en español de España y no uses voseo.
- Elimina cualquier sección que solo contenga generalidades. Un hueco declarado es preferible a relleno.
