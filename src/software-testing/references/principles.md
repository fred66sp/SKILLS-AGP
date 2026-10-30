# Principios de la prueba

Desarrollo operativo de los siete principios del contrato. Cada principio lleva su consecuencia en el trabajo diario y la señal que avisa de que se está violando. No son decoración: cuando dos decisiones chocan, estos principios deciden.

## 1. La prueba demuestra presencia de defectos, no su ausencia

Un resultado verde dice que los casos escritos pasan. No dice que los que no se escribieron no existen.

- Consecuencia: el cierre nunca afirma «funciona»; afirma «estos riesgos quedaron cubiertos por esta evidencia». El resto va a No verificado.
- Señal de violación: un informe que concluye «sin defectos» en vez de «sin defectos encontrados por esta ronda».

## 2. Probarlo todo es imposible

Ni siquiera una función de dos enteros admite todas las entradas. El conjunto de casos es siempre una elección.

- Consecuencia: la prioridad se calcula como impacto por probabilidad, y el alcance se escribe con exclusiones. La pregunta útil no es «¿qué puedo probar?» sino «¿qué fallo pagaré más caro por no haber visto?».
- Señal de violación: casos ordenados por módulo o por alfabético; un plan que promete «cobertura completa» sin definir de qué.

## 3. Antes es más barato

El coste de un defecto crece con la fase en que se descubre: en el criterio se corrige hablando, en la ronda tardía se paga con retrabajo.

- Consecuencia: contrastar criterios de aceptación y contratos antes de implementar es trabajo de prueba, aunque no ejecute nada. Es el nivel más barato de la escalera.
- Señal de violación: una ronda que empieza con casos sin haber revisado si la necesidad y el diseño se contradicen.

## 4. Los defectos se agrupan

Los fallos no se reparten en uniforme: se concentran en módulos complejos, recién tocados o mal entendidos.

- Consecuencia: el historial decide el esfuerzo. Un módulo con defectos abiertos o cambios recientes merece más ángulos que uno estable.
- Señal de violación: repartir el presupuesto de casos a partes iguales entre todo el sistema.

## 5. La misma prueba repetida deja de encontrar defectos nuevos

Como el pesticida, una suite que solo repite sus ángulos elimina los defectos que ya sabe buscar y deja pasar el resto.

- Consecuencia: cada ronda añade algún ángulo nuevo: otro dato límite, otra combinación, otro orden. La revisión de la suite es parte de la ronda.
- Señal de violación: una suite que crece en líneas y no en ángulos; rondas consecutivas con casos idénticos y cero hallazgos, celebrados como calidad.

## 6. El contexto decide el método

Una CLI, una API, un servicio con estado y una interfaz no comparten riesgo ni coste de observación. Las técnicas se eligen por contexto.

- Consecuencia: la escalera y las técnicas se justifican con el contexto del proyecto. Lo que es humo en una CLI es ronda completa en una migración de datos.
- Señal de violación: aplicar la misma plantilla de ronda a todo, o exigir automatización donde solo cabe observación manual.

## 7. Sin defectos encontrados no es el objetivo

Un sistema sin fallos encontrados que no resuelve la necesidad es un fracaso pulcro. La prueba contrasta contra la necesidad, no contra sí misma.

- Consecuencia: cada caso remite al riesgo que cubre, y el riesgo remite a la necesidad. Si un caso no sabe explicar a qué necesidad sirve, sobra.
- Señal de violación: métricas de casos ejecutados sin métricas de riesgos cubiertos; ruedas de fortuna verdes.
