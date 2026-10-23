# Lista de las cuatro reglas por escenario

Pásala en el paso 8, después de las comprobaciones por regla. Cada pregunta lleva el código del
script que la respalda: si el código no disparó, la pregunta se responde con el criterio y se
declara como estimación.

## Regla 1 · ¿se entiende sin contexto?

- [ ] ¿Cualquiera que no estuvo en la sesión entiende qué se especifica?
- [ ] ¿Los pasos están en orden `Dado → Cuando → Entonces`? — `step-order`, `too-many-steps`
- [ ] ¿Hay entre 1 y 9 pasos efectivos, contando `Background`? — `too-many-steps`
- [ ] ¿El escenario describe el qué en lugar del cómo? — `low-level-vocab`
- [ ] ¿Cada `Dado` declara estado inicial y no una intención de negocio? — `business-intent-given`
- [ ] ¿Hay al menos una verificación? — `missing-then`
- [ ] ¿El bloque es Gherkin parseable y con título? — `unparseable-block`

## Regla 2 · ¿cubre un solo comportamiento?

- [ ] ¿El escenario tiene un único ciclo acción-verificación? — `multiple-action-outcome`
- [ ] ¿El título anuncia todo lo que el cuerpo hace?
- [ ] Si hay dos comportamientos, ¿se nombra cuál queda en cada escenario dividido y con qué `Dado` se sitúa cada uno?
- [ ] ¿Un fallo de este escenario señalaría una sola causa raíz?

## Regla 3 · ¿aporta algo cada fila?

- [ ] ¿Cada fila de `Examples` representa una clase de equivalencia distinta? — `redundant-examples`
- [ ] ¿Las columnas de `Examples` llegan a un `<placeholder>` del escenario? — `outline-missing-placeholder`
- [ ] ¿Qué coste de ejecución añade cada fila que no amplía la cobertura real?
- [ ] ¿Se podría quedar el escenario en un ejemplo sin perder comprensión?

## Regla 4 · ¿lo leería tu profesor de Lengua?

- [ ] ¿Un solo punto de vista en todo el archivo, preferiblemente tercera persona? — `person-mixed`
- [ ] ¿Cada paso tiene sujeto y predicado? — `no-subject-verb`
- [ ] ¿Cada paso se entendería suelto, fuera de su escenario?
- [ ] ¿La redacción es reutilizable como definición de paso sin contorsiones?

## Veredicto

- `NO APTO`: cualquier determinista de regla 2, un escenario sin `Entonces`, un orden imposible o un bloque no parseable.
- `APTO CON RESERVAS`: sin esas violaciones y con estimaciones confirmadas o hallazgos menores de lenguaje.
- `APTO`: sin hallazgos con impacto después de refutar los candidatos.
- `FUERA DE ALCANCE`: el texto no es un `.feature` o el encargo pide escribir, descubrir o automatizar.
