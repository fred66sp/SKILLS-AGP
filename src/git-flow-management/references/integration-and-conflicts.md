# Integración y conflictos

Usa esta referencia antes de integrar y en cuanto aparezca un conflicto.

## Selección

| Método | Úsalo cuando | No lo uses cuando |
|---|---|---|
| Merge | La rama es compartida o la política conserva topología. | La política exige linealidad. |
| Rebase | La rama es privada y no publicada. | La rama se comparte o ya está publicada. |
| Cherry-pick | Debe trasladarse un commit aislado. | Debe integrarse una rama completa. |

## Plan previo

Muestra origen, destino, commits incluidos, ancestro común, posibilidad de fast-forward, efecto de historia, validación y riesgo de conflicto.

## Conflicto

1. Detente e informa de operación y archivos afectados.
2. No edites ni prepares marcadores de conflicto automáticamente.
3. Ofrece resolver archivos concretos, abortar o pausar.
4. Para resolver, presenta una decisión semántica por archivo y solicita confirmación de un plan nuevo.
5. Verifica que no quedan archivos sin fusionar y ejecuta la validación acordada.
