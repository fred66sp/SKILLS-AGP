# Puerta de calidad del PRD

Aplica esta lista antes de considerar un PRD suficientemente preparado para revisión humana. No sustituye la lectura del documento: comprueba que lo afirmado se sostiene.

## Evidencia y trazabilidad

- [ ] Todas las fuentes realmente utilizadas están inventariadas con procedencia, fecha visible y alcance.
- [ ] Cada afirmación crítica tiene fuente y localización reproducible.
- [ ] Se distingue evidencia primaria de resumen, copia derivada o inferencia.
- [ ] Las afirmaciones sin apoyo están marcadas `UNKNOWN`, `Parcial`, `Hipótesis` o `Propuesta`.
- [ ] No se ha atribuido autoridad, vigencia ni corrección a una fuente solo por existir o por ser más reciente.
- [ ] Los conflictos entre fuentes están expuestos, no resueltos en silencio.
- [ ] Las decisiones del agente no aprobadas están marcadas `Propuesta`.
- [ ] El mapa de evidencia declara qué no se pudo verificar.

## Pensamiento de producto

- [ ] El problema está descrito antes que la solución.
- [ ] Se identifica quién está afectado, en qué contexto y con qué necesidad.
- [ ] El concepto puede expresarse con el Universal Idea Model o se explican los campos `UNKNOWN`.
- [ ] El PRD responde qué, para quién, por qué y cómo se sabrá si funcionó.
- [ ] No se ha confundido una solución propuesta con una necesidad validada.
- [ ] La propuesta de valor no depende de una categoría genérica ni de un adjetivo no comprobable.

## Usuarios y personas

- [ ] Cada persona se sustenta en evidencia y declara su fuente.
- [ ] No se han inventado nombres, roles, edades, frustraciones, citas ni comportamientos.
- [ ] Los segmentos se diferencian solo cuando la diferencia cambia una decisión.
- [ ] Las necesidades descritas son del usuario, no de la organización que las imagina.

## Objetivos y métricas

- [ ] Cada métrica tiene definición, método, fuente, línea base, objetivo y plazo, o declara exactamente lo que falta.
- [ ] Hay al menos un resultado de usuario y, cuando proceda, uno de negocio.
- [ ] Existe umbral de fracaso o condición de reevaluación.
- [ ] La instrumentación necesaria existe o está incluida en el alcance.
- [ ] Ningún objetivo se ha expresado como actividad o entrega.

## Requisitos y alcance

- [ ] Cada funcionalidad relevante está vinculada a una persona, objetivo, problema o riesgo.
- [ ] Las user stories expresan beneficio, no solo una operación de interfaz.
- [ ] Los criterios de aceptación son observables y comprobables.
- [ ] `In scope` y `Out of scope` son explícitos y coherentes con los objetivos.
- [ ] No se han introducido detalles de implementación sin una restricción que los justifique.
- [ ] Los requisitos no funcionales están justificados y tienen forma de verificación.

## Supuestos, dependencias y riesgos

- [ ] Cada supuesto, dependencia y riesgo tiene estado y una forma concreta de validación o mitigación.
- [ ] Ninguna dependencia no verificada se presenta como disponible.
- [ ] Los riesgos incluyen su efecto sobre el resultado, no solo una etiqueta.
- [ ] Las preguntas abiertas identifican responsable y condición de respuesta cuando se conocen.

## Coherencia final

- [ ] No hay contradicciones entre problema, personas, objetivos, funcionalidades y métricas.
- [ ] Las exclusiones no contradicen los objetivos de la versión.
- [ ] El documento contiene versión, estado, propietario, changelog y decisiones pendientes.
- [ ] Un lector ajeno puede explicar qué se construye, para quién y cómo se medirá el éxito.
- [ ] El PRD no se presenta como aprobado si no lo está.
- [ ] Las validaciones humanas pendientes están asignadas y son visibles.

## Veredicto de la puerta

- **LISTO PARA REVISIÓN**: no quedan fallos críticos; puede haber validaciones humanas pendientes, pero ninguna afirmación crítica está inventada ni ninguna métrica es inmedible.
- **PARCIAL**: puede circular como borrador, pero contiene `UNKNOWN`, hipótesis críticas o dependencias sin confirmar que impiden decidir.
- **NO LISTO**: falta comprender el problema, existe una contradicción crítica, se estaría inventando evidencia o el documento no permite saber qué se construye y para quién.

## Falsos positivos

No marques `LISTO PARA REVISIÓN` para complacer al usuario. La puerta no mide lo completo que parece el documento, sino lo que se puede sostener. Un PRD corto con huecos declarados supera a uno extenso con afirmaciones sin fuente.

No marques `NO LISTO` por la sola ausencia de una línea base si el resto del PRD es coherente y el hueco está declarado con su plan de medición. En ese caso, el veredicto correcto es `PARCIAL`.
