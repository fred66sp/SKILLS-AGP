# Integración y conflictos

Usa esta referencia antes de integrar y en cuanto aparezca un conflicto.

## La integración es una decisión aparte

Trabajar en una rama y fusionarla en `main` son decisiones distintas. No integres por iniciativa propia: la integración se pide o se autoriza. Puedes incluirla en el plan junto con el commit y el borrado de la rama, y recibir una sola confirmación que enumere las tres etapas.

Antes de integrar comprueba brevemente:

- que la tarea está terminada y la validación acordada se ha ejecutado;
- que no hay cambios del usuario que vayan a perderse;
- que la rama que se integra es la correcta y deriva de la base esperada.

## Estrategia

La estrategia la fija la política del repositorio; si no fija ninguna, elige la que mantenga el historial claro y sencillo para ese repositorio. `--no-ff` no es obligatorio por sí mismo.

| Método | Úsalo cuando | No lo uses cuando |
|---|---|---|
| Merge | La rama es compartida o la política conserva topología. | La política exige linealidad. |
| Rebase | La rama es privada y no publicada. | La rama se comparte o ya está publicada. |
| Cherry-pick | Debe trasladarse un commit aislado. | Debe integrarse una rama completa. |

## Plan previo

Muestra origen, destino, commits incluidos, ancestro común, posibilidad de fast-forward, efecto de historia, validación, riesgo de conflicto y si la rama se borra después.

## Después de integrar

1. Comprueba el estado final y muestra la contención con evidencia.
2. Si la rama ya no se necesita, informa del nombre, de su contenido integrado y del comando `git branch -d <rama>`, y pide confirmación antes de borrarla.
3. Si el usuario no confirma el borrado, deja la rama y dilo en el informe final.

## Conflicto

1. Detente e informa de operación y archivos afectados.
2. No edites ni prepares marcadores de conflicto automáticamente.
3. Ofrece resolver archivos concretos, abortar o pausar.
4. Para resolver, presenta una decisión semántica por archivo y solicita confirmación de un plan nuevo.
5. Verifica que no quedan archivos sin fusionar y ejecuta la validación acordada.
