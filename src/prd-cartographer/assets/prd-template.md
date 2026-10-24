# PRD: <nombre>

> Copia esta estructura y sustituye cada marcador por contenido concreto. Si un campo no puede completarse con evidencia, escribe `UNKNOWN` y añade la pregunta que lo desbloquea en la sección 14. No dejes marcadores `<...>` en la entrega.

## 1. Metadatos

| Campo | Valor |
|---|---|
| Nombre | <nombre del producto o feature> |
| Tipo | <producto \| feature> |
| Versión | <versión del documento> |
| Estado | <borrador \| en revisión \| aprobado \| obsoleto> |
| Propietario | <persona o rol responsable> |
| Fecha | <fecha de esta versión> |
| Fuentes | <lista de fuentes inventariadas> |

## 2. Resumen y propósito

<Qué es, para quién y por qué ahora. Debe entenderse sin leer el resto.>

## 3. Universal Idea Model

> Un <objeto> para <usuarios> que <hace algo> para <lograr un resultado>. Los usuarios obtienen <valor> cuando <situación>.

Campos `UNKNOWN` y evidencia que los desbloquearía: <...>

## 4. Problema y evidencia

### Entorno y contexto

<Dónde aparece el problema y bajo qué condiciones.>

### Personas afectadas

<Quién lo sufre y qué evidencia lo sostiene.>

### Dinámica actual

<Qué hacen hoy, con qué fricción y qué coste tiene.>

### Síntomas observables

- <síntoma, con fuente>

### Causas conocidas

- <causa, con grado de certeza y fuente>

### Hipótesis causales

- <hipótesis, con prueba que la validaría>

### Estado ideal

<Qué cambiaría si el problema se resolviera.>

## 5. Usuarios objetivo y personas

| Persona o segmento | Contexto | Necesidad | Evidencia | Qué la diferencia |
|---|---|---|---|---|
| <persona> | <contexto> | <necesidad> | <fuente> | <diferencia que cambia una decisión> |

## 6. Objetivos y resultados esperados

### Objetivos

- <objetivo>

### Resultados esperados

- <resultado observable para el usuario o el negocio>

## 7. Métricas de éxito

| Métrica | Definición | Método | Fuente | Línea base | Objetivo | Plazo | Umbral de fracaso |
|---|---|---|---|---|---|---|---|
| <métrica> | <fórmula o criterio> | <cómo se calcula> | <sistema o informe> | <valor o UNKNOWN> | <valor> | <periodo> | <valor o condición> |

## 8. Alcance de esta versión

### In scope

- <lo que entrega esta versión>

### Out of scope

- <lo que queda fuera y, si sorprende, por qué>

## 9. Épicas, capacidades y user stories

### Épica: <nombre>

<Resultado que persigue.>

- Como <persona>, quiero <acción>, para <beneficio>.
  - Trazabilidad: <objetivo, problema, persona o riesgo>
  - Prioridad: <alta \| media \| baja, con motivo>
  - Criterios de aceptación: <referencia a la sección 10>

## 10. Criterios de aceptación

### <Historia o capacidad>

- Dado <contexto>, cuando <acción>, entonces <resultado observable>.
- Dado <contexto>, cuando <acción>, entonces <resultado observable>.

## 11. Requisitos no funcionales

| Requisito | Restricción | Motivo | Verificación |
|---|---|---|---|
| <seguridad \| privacidad \| accesibilidad \| rendimiento \| disponibilidad \| cumplimiento \| compatibilidad> | <valor o regla> | <por qué aplica> | <cómo se comprueba> |

## 12. Supuestos, restricciones y dependencias

| Elemento | Tipo | Enunciado | Grado | Impacto si es falso | Validación o mitigación |
|---|---|---|---|---|---|
| <elemento> | <supuesto \| restricción \| dependencia> | <enunciado> | <hecho \| decisión \| inferencia \| hipótesis \| UNKNOWN> | <impacto> | <cómo se valida> |

## 13. Riesgos y mitigaciones

| Riesgo | Efecto sobre el resultado | Probabilidad o impacto | Mitigación | Responsable |
|---|---|---|---|---|
| <riesgo> | <efecto> | <cualificación> | <acción> | <persona o rol> |

## 14. Preguntas abiertas y decisiones pendientes

| Pregunta o decisión | Por qué importa | Responsable | Condición de respuesta |
|---|---|---|---|
| <pregunta> | <decisión que bloquea> | <persona o rol> | <fecha o evidencia necesaria> |

## 15. Plan de validación y revisión

| Área | Qué debe validar | Evidencia o acción | Responsable |
|---|---|---|---|
| Producto | <problema, prioridad y alcance> | <revisión, dato o decisión> | <persona o rol> |
| Diseño | <experiencia y accesibilidad> | <prueba o revisión> | <persona o rol> |
| Ingeniería | <viabilidad y dependencias> | <análisis o prototipo> | <persona o rol> |
| QA | <criterios de aceptación> | <plan de prueba> | <persona o rol> |
| Usuarios | <necesidad y valor> | <entrevista, prueba o dato> | <persona o rol> |

## 16. Registro de decisiones y changelog

| Fecha | Versión | Decisión o cambio | Estado | Responsable | Motivo |
|---|---|---|---|---|---|
| <fecha> | <versión> | <decisión> | <propuesta \| aprobada \| descartada> | <persona o rol> | <motivo> |

Condiciones que obligan a revisar este PRD: <cambio de evidencia, de alcance, de métrica, de dependencia o de decisión>.

## 17. Mapa de evidencia y límites

| Afirmación crítica | Grado | Fuente | Localización | Límite |
|---|---|---|---|---|
| <afirmación> | <hecho \| decisión \| inferencia \| hipótesis \| parcial \| UNKNOWN> | <documento, entrevista, dato> | <sección, página o consulta> | <qué no cubre> |

### Límites de la verificación

- <qué se revisó y qué no>
- <fuente no accesible o no versionada>
