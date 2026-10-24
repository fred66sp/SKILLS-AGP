# Evidencia y certeza de las afirmaciones

Léelo en el paso 2 del procedimiento, cuando una afirmación no esté sustentada directamente por una fuente visible o cuando dos fuentes puedan discrepar.

## Grados de certeza de la afirmación

Clasifica cada afirmación material antes de redactarla. La etiqueta se imprime cuando afecta a una decisión, a un riesgo, a la implementación o a la comprensión del producto.

| Grado | Significado | Cómo se redacta | Acción obligatoria |
|---|---|---|---|
| Hecho confirmado | Una fuente disponible lo sustenta directamente | Afirmación directa, sin matices | Citar fuente y localización en el mapa de evidencia |
| Decisión aprobada | Una persona con autoridad la adoptó y consta el alcance | "Se decidió…" con responsable y fecha visibles | Registrarla en el registro de decisiones |
| Inferencia | Conclusión razonada a partir de hechos, no declarada | "Se infiere de…", "Los datos sugieren…" | Explicar el razonamiento y qué falta para confirmarla |
| Hipótesis | Supuesto pendiente de validación | "Hipótesis:…" | Definir la prueba o evidencia que la valida o refuta |
| Propuesta | Decisión sugerida por el agente, no aprobada | "Propuesta:…" | Separarla de lo aprobado y pedir decisión |
| Parcial | La evidencia cubre solo una parte de la afirmación | "La evidencia cubre X; no cubre Y" | Acotar la afirmación a lo sustentado |
| UNKNOWN / No verificable | No hay evidencia suficiente | "No determinado en este alcance" | Enumerarlo como pendiente con la pregunta que lo desbloquea |

Regla de oro: una inferencia cómoda redactada como hecho es el defecto más caro de un PRD, porque nadie la vuelve a comprobar antes de construir.

## Comparación de fuentes

Cuando dos fuentes traten la misma afirmación, clasifica la relación antes de elegir una:

| Clasificación | Cuándo se usa |
|---|---|
| SE SOSTIENE | La fuente aporta evidencia suficiente y coherente para la afirmación en el alcance revisado |
| NO SE SOSTIENE | La fuente contradice la afirmación o no aporta la evidencia que se le atribuye |
| SUPERADA | Existe sustitución, revisión, anulación o incompatibilidad explícita de una fuente anterior |
| COPIA DERIVADA | La fuente repite otra sin aportar evidencia independiente |
| NO VERIFICABLE | No se puede acceder a la fuente, a su versión o a su contexto |

No uses `SUPERADA` solo porque una fuente sea más reciente. La fecha no sustituye a una decisión de reemplazo.

## Qué confirma cada fuente

| Fuente | Qué confirma | Qué no confirma |
|---|---|---|
| Entrevistas y observación | Necesidades declaradas, lenguaje del usuario, contexto de uso | Frecuencia, magnitud ni causa del problema |
| Analítica y datos de producto | Comportamiento medido en la población y periodo observados | Motivación, intención ni demanda no observada |
| Documentos de producto y decisiones | Intención declarada, alcance aprobado, restricciones | Que lo declarado esté implementado o siga vigente |
| Repositorio, prototipos y demos | Comportamiento existente y restricciones técnicas visibles | Valor para el usuario ni prioridad de negocio |
| Investigación de mercado | Prácticas del mercado y alternativas existentes | Demanda concreta en los usuarios objetivo |
| Documentación externa oficial | Comportamiento de una dependencia en la versión consultada | Cómo la usa o configura este producto |
| Decisión explícita del usuario | Requisito, prioridad o política adoptada | Detalles que la decisión no cubre |

Contrasta siempre la evidencia de problema con la de solución. Una funcionalidad existente no demuestra que el problema esté resuelto, y una encuesta de intención no demuestra uso.

## Contradicciones

1. Determina qué fuente tiene responsabilidad sobre la afirmación concreta. Una entrevista describe necesidad; la analítica describe comportamiento; una decisión describe intención. No compiten si se sitúan en secciones distintas.
2. Si dos fuentes reclaman la misma responsabilidad, no redactes un término medio. Expón ambas, identifica cada una y pide decisión.
3. Si la contradicción afecta al alcance, a una métrica o a una persona, el PRD no puede declararse `LISTO`.
4. Si la contradicción es entre una fuente y una decisión aprobada, prevalece la decisión para la intención y la fuente para el estado observado. Deja constancia de la discrepancia.

## Redacción de afirmaciones no sustentadas

Mal: "Los usuarios necesitan exportar en PDF porque lo piden en todas las entrevistas."

Bien: "En las entrevistas revisadas, tres participantes mencionan la exportación como fricción. No se determinó su frecuencia ni si es prioritaria frente a otras necesidades: `Hipótesis`."

Mal: "La funcionalidad aumentará la retención un 20 %."

Bien: "Propuesta de métrica: retención a 30 días. Línea base y método de medida `UNKNOWN`; sin ellos, el objetivo del 20 % no es verificable."

## Límites de la verificación del PRD

- Un alcance acotado produce certeza acotada. Declara qué se revisó y qué no.
- Una fuente sin fecha ni versión identificable no sustenta una afirmación sobre el estado actual.
- La ausencia de evidencia no es evidencia de ausencia: no declares una carencia sin haber buscado en las fuentes donde debería estar.
- No atribuyas a una fuente una conclusión que la fuente no formula, aunque la conclusión parezca razonable.
