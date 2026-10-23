# Evidencia y certeza de las afirmaciones

Léelo en el paso 3 del procedimiento, cuando una afirmación material no esté sustentada directamente por una fuente visible.

## Grados de certeza

Clasifica cada afirmación material antes de redactarla. La clasificación no se imprime en todos los documentos: se hace visible cuando afecta a una decisión, a un riesgo, a la implementación o a la comprensión.

| Grado | Significado | Cómo se redacta | Acción obligatoria |
|---|---|---|---|
| CONFIRMADO | Una fuente disponible lo sustenta directamente | Afirmación directa, sin matices | Citar la fuente en la verificación de cierre |
| INFERENCIA | Conclusión razonable derivada de evidencia, no declarada | "Se infiere de…", "La implementación sugiere…" | Señalar qué la sustenta y qué falta para confirmarla |
| PROPUESTA | Diseño o recomendación no adoptada | "Se propone…", "Queda abierto…" | Separarla del estado actual en una sección propia |
| UNKNOWN | No hay evidencia suficiente | "No determinado en este alcance" | Enumerarla como pendiente con la pregunta que la desbloquea |
| CONTRADICCIÓN | Dos fuentes con responsabilidad sobre lo mismo sostienen cosas incompatibles | "La fuente A afirma X; la fuente B afirma Y" | No elegir por cuenta propia: reportar y pedir decisión |
| OBSOLETO | Hay evidencia de que la descripción ya no representa el estado actual | Eliminar o marcar como histórico con su motivo | Comprobar antes que no sea la única representación del conocimiento |

Regla de oro: una inferencia cómoda redactada como hecho es el defecto más caro de la documentación, porque nadie la vuelve a comprobar.

## Verificación por tipo de fuente

| Fuente | Qué confirma | Qué no confirma |
|---|---|---|
| Código | Comportamiento implementado, nombres, rutas, valores por defecto | Intención del producto ni comportamiento deseado |
| Tests | Comportamiento que el proyecto considera obligatorio | Comportamiento no cubierto ni decisiones de diseño |
| Configuración y esquemas | Contratos, variables, tipos, límites | Comportamiento en tiempo de ejecución |
| Historial Git | Qué cambió, cuándo y en qué contexto | Que lo documentado siga vigente en el estado actual |
| Documentación existente | Intención declarada por el proyecto | Que se corresponda con el estado implementado |
| Decisión explícita del usuario | Requisito o política adoptada | Detalles técnicos no decididos |
| Documentación externa oficial | Comportamiento de la dependencia en la versión consultada | Cómo la usa o la configura este proyecto |

Contrasta siempre el estado implementado con el comportamiento declarado. Un README antiguo no convierte en real una función que el código ya no implementa, y un test no demuestra por sí solo una intención de producto.

## Tratamiento de contradicciones

1. Determina qué fuente tiene responsabilidad sobre esa afirmación concreta. Una especificación puede describir intención y el código el estado implementado: no compiten, se sitúan en secciones distintas.
2. Si dos fuentes reclaman la misma responsabilidad, no redactes un término medio. Expón ambas afirmaciones, identifica cada fuente y pide decisión.
3. Si la contradicción es entre documentación existente e implementación, no actualices la documentación sin autorización cuando la documentación sea la especificación vigente: el arreglo puede corresponder al software.
4. Si la contradicción es entre el usuario y una fuente del repositorio, prevalece la decisión explícita del usuario para la intención, y la fuente del repositorio para el estado implementado. Deja constancia de la discrepancia.

## Redacción de lo no sustentado

Mal: "La API admite paginación por cursor y devuelve 50 registros por defecto."
Bien: "La implementación devuelve 50 registros por defecto (`src/api/list.ts:42`). No se determinó si existe paginación por cursor: no aparece en el código revisado ni en la especificación."

Mal: "Los usuarios podrán exportar en PDF en la próxima versión."
Bien: "Propuesta: exportación en PDF. No está implementada ni decidida; queda pendiente de aprobación."

## Límites de la verificación

- Un alcance acotado produce certeza acotada. Declara qué se revisó y qué no.
- Una fuente externa sin versión identificable no sustenta una afirmación sobre comportamiento.
- La ausencia de evidencia no es evidencia de ausencia: no documentes una carencia sin haber buscado en las fuentes donde debería estar.
