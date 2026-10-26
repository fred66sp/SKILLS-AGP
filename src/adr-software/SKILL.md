---
name: adr-software
description: "Crea y mantiene Architecture Decision Records (ADR) con contrato de agente: decide si una decisión merece un ADR, captura la intención sin interrogar, redacta contexto, decisión, alcance, alternativas, consecuencias y verificación en formato simple o MADR, y valida el resultado con una puerta determinista. Úsala cuando haya que proponer, redactar, revisar, aceptar, rechazar, deprecar o sustituir un ADR, inicializar el directorio y el índice, o comprobar sus convenciones. No la uses para diseñar la arquitectura, para PRD o requisitos de producto, ni para documentación general del proyecto."
metadata:
  version: "0.1.0"
---

# ADR de software

Escribe ADR para que un agente pueda implementar la decisión sin volver a preguntar. La persona revisa y aprueba; el consumidor principal es el agente que trabajará después con el registro. Un ADR es un contrato de decisión, no un acta: si no permite actuar, no está terminado.

## Invariantes del ADR

1. No escribas antes de delimitar la operación —crear, revisar, cambiar estado, deprecar, sustituir, indexar o auditar— y el directorio de ADR que usa el repositorio.
2. Una decisión tiene un solo ADR vigente. Antes de crear, busca uno existente que la cubra; actualizarlo o sustituirlo prevalece sobre duplicarlo.
3. No conviertas una preferencia o una suposición en decisión. Sin contexto, alternativas y consecuencias, lo que hay es una propuesta.
4. La decisión se escribe en concreto: tecnología, versión, alcance, límite y condición. «Usar una base de datos mejor» no es una decisión.
5. Toda restricción material es medible o verificable. «Rápido», «escalable» y «mantenible» necesitan un valor, una condición o un método de comprobación.
6. El alcance incluye lo que queda dentro y lo que queda fuera. Sin no-goals explícitos, el alcance no está acotado.
7. Cada alternativa real explica por qué se rechazó. Una alternativa de paja no demuestra comparación.
8. Cada consecuencia es concreta y accionable. Una consecuencia que repite la decisión con otras palabras no aporta nada.
9. No inventes datos, enlaces, fechas, responsables ni resultados. Lo que no se sabe se marca como desconocido o se pregunta.
10. No cambies el significado de un ADR aceptado editando su historia. Los aprendizajes se añaden con fecha; un cambio de decisión se publica como ADR nuevo que sustituye al anterior.
11. No declares terminado un ADR sin ejecutar la puerta de revisión y mostrar su resultado. Un ADR que no la supera se entrega como borrador, nunca como aceptado.
12. No presentes como aprobada una decisión que la persona no ha aprobado. El estado inicial de un ADR nuevo es `proposed`.

## Procedimiento del ADR

**Paso 1 — Delimitar la operación.**
1. Identifica una sola operación: crear, actualizar el estado, deprecar, sustituir, mantener el índice o auditar sin modificar.
2. Localiza el directorio y la convención existentes: `docs/decisions/`, `adr/`, `docs/adr/`, `docs/adrs/` o `decisions/`. Si el repositorio ya tiene numeración, nombres con guiones o un índice, esa convención manda.
3. Si no existe directorio, decide con el responsable entre `docs/decisions/` y `adr/`. No crees una estructura nueva cuando ya hay una equivalente.
4. Si el encargo mezcla varias decisiones, sepáralas en ADR distintos antes de redactar. Una decisión por registro.

**Paso 2 — Comprobar duplicados y predecesores.**
1. Busca en el directorio por título, tema y enlaces. Un ADR existente puede cubrir la decisión, contradecirla o haber sido sustituido.
2. Si la decisión ya está aceptada y vigente, no crees otro: informa y propón actualizar el índice o añadir el aprendizaje.
3. Si la decisión cambia la vigente, el resultado es un ADR nuevo que la sustituye; el anterior pasa a `superseded by` con enlace, y ambos se enlazan.
4. Si el repositorio guarda decisiones en otro formato, no lo migres sin pedirlo: adapta la redacción al formato existente.

**Paso 3 — Capturar la intención.**
1. Formula una pregunta cada vez y solo sobre lo que falte. No interrogues para rellenar una plantilla ni repitas lo que el contexto ya responde.
2. Cubre, en este orden y omitiendo lo claro: qué se decide, por qué ahora, qué restricciones existen, qué resultado medible se espera, qué alternativas se consideraron, cuál es la inclinación actual, quién decide y quién debe saberlo, y qué necesita saber quien lo implemente.
3. Profundiza donde la decisión sea difusa: peor resultado si es errónea, qué la haría revisarse, qué se decide no hacer y qué patrón previo del repositorio se relaciona.
4. Para operaciones de mantenimiento —migración de formato, traducción fiel, cambio de estado explícito o actualización mecánica del índice— puedes omitir la entrevista cuando la transformación es explícita, el contexto de origen está completo y el significado no cambia.
5. Si el cambio altera la decisión, el motivo, el alcance, las alternativas o la relación con otros ADR, vuelve a preguntar. Detente cuando puedas redactar todas las secciones sin inventar nada; si dudas de alguna, pregunta una vez más.

**Paso 4 — Decidir si procede un ADR.**
1. Crea un ADR cuando la decisión sea difícil de revertir, afecte a varios módulos o equipos, imponga una restricción duradera, tenga alternativas reales o su coste de cambio sea alto.
2. No crees un ADR para una decisión trivial, reversible y local, para un detalle de implementación sin consecuencias ni para una preferencia sin impacto. Si no procede, dilo y no generes el archivo.
3. Si la decisión no está tomada, redacta el ADR como `proposed` con las preguntas abiertas visibles. No la presentes como aceptada.

**Paso 5 — Redactar.**
1. Elige plantilla. Usa `assets/adr-simple.md` cuando haya una opción clara y pocas alternativas; usa `assets/adr-madr.md` cuando haya tres o más opciones reales, revisión entre equipos o una decisión que vaya a compararse. Lee `references/template-variants.md` si dudas.
2. Copia la plantilla y sustituye cada marcador por contenido concreto. No dejes marcadores, secciones vacías ni texto de ejemplo en un ADR destinado a aceptarse.
3. Escribe el título como frase verbal: «Adoptar PostgreSQL 16 con pgvector», no «Problema de base de datos».
4. En el contexto, explica el problema y el disparador antes de la solución: qué cambió, qué se rompió o qué se romperá si no se decide.
5. En la decisión, incluye alcance, límites y no-goals. Añade la condición que la haría revisarse.
6. En las consecuencias, separa lo bueno, lo malo y lo neutro, y nombra las tareas de seguimiento: migraciones, configuración, pruebas, documentación y responsables.
7. En las alternativas, explica el motivo del rechazo con el criterio que decidió: coste, riesgo, compatibilidad, operación o mantenimiento.

**Paso 6 — Pasar la puerta de revisión.**
1. Ejecuta `python3 <skill>/scripts/adr.py check --root <raíz>`. Sin hallazgos, devuelve 0; con hallazgos, devuelve 1 y los nombra con archivo y motivo.
2. Lee `references/review-gate.md` y recorre la puerta completa cuando el script no pueda decidir sobre contenido, alternativas o consecuencias.
3. La puerta responde a una pregunta: ¿puede un agente implementar esta decisión con el ADR, sin preguntar y sin adivinar? Si la respuesta es no, corrige o declara el hueco.
4. No aceptes un ADR con marcadores pendientes, una decisión ambigua, un alcance sin no-goals o consecuencias sin tareas. Los huecos se cierran o se entregan como borrador declarado.

**Paso 7 — Mantener el registro.**
1. Cambia el estado con `python3 <skill>/scripts/adr.py status <archivo> --status <valor>`; si el estado es `superseded`, usa `--superseded-by <ruta>` para que el enlace quede escrito.
2. Un cambio de estado actualiza la fecha del frontmatter. No reescribas el cuerpo para acomodar el nuevo estado.
3. Para deprecar, explica en `Más información` qué la sustituye o por qué ya no aplica. No borres el ADR.
4. Para añadir un aprendizaje, agrega una entrada fechada en `Más información`. No reescribas la decisión original.
5. El índice se actualiza al crear por defecto. Usa `--no-update-index` solo si el repositorio decide no mantener índice; si existe uno, cada ADR tiene entrada y las entradas resuelven.

**Paso 8 — Cerrar con evidencia.**
1. Revisa el diff y el índice. Un ADR nuevo sin entrada en el índice, o una entrada sin archivo, es un defecto de entrega.
2. Cierra con el bloque de resultado del ADR, relleno con lo observado.
3. Si no puedes ejecutar la puerta, dilo; no la sustituyas por una impresión.

## Errores y paradas del ADR

- Si falta la decisión o el motivo, no redactes un ADR completo: entrega el contexto y las preguntas que faltan.
- Si dos documentos del repositorio contradicen la decisión, expón la contradicción y pide decisión; no elijas la fuente más reciente sin evidencia.
- Si el estado es `superseded` y no hay enlace al sustituto, el ADR está incompleto: escribe el enlace o vuelve a `deprecated`.
- Si la persona pide un ADR para una decisión ya aceptada, no lo dupliques: propón un ADR de sustitución o una entrada de aprendizaje.
- Si el ADR describe una implementación concreta que puede cambiar sin cambiar la decisión, mueve ese detalle a las tareas de seguimiento.
- Si la puerta devuelve hallazgos que no puedes resolver con la información disponible, entrega el ADR como borrador y enumera los hallazgos.

## Resultado del ADR

Cierra siempre con este bloque, sin adjetivos:

```text
Operación: <crear | actualizar estado | deprecar | sustituir | indexar | auditar>
ADR: <ruta o "ninguno">
Estado: <proposed | accepted | rejected | deprecated | superseded | borrador>
Directorio y convención: <ruta, numeración o slug>
Puerta de revisión: <sin hallazgos | hallazgos enumerados>
Decisiones pendientes: <lista con la pregunta que las desbloquea, o "ninguna">
Seguimiento: <tareas concretas, o "ninguno">
```

## Referencias del paquete de ADR

- [adr-conventions](references/adr-conventions.md) — directorio, nombres, estados, frontmatter, mutabilidad, categorías e índice. Léelo en los pasos 1, 2 y 7.
- [review-gate](references/review-gate.md) — puerta de revisión de agente y modos de fallo frecuentes. Léelo en el paso 6.
- [template-variants](references/template-variants.md) — cuándo usar la plantilla simple o MADR. Léelo en el paso 5 si dudas.
- [examples](references/examples.md) — un ADR corto y el mismo con análisis de opciones. Consúltalo como referencia de forma, nunca para copiar contenido.
- [adr-simple](assets/adr-simple.md) — plantilla de decisión directa. Cópiala en el paso 5.
- [adr-madr](assets/adr-madr.md) — plantilla MADR para decisiones con varias opciones. Cópiala en el paso 5.
- [adr-bootstrap](assets/adr-bootstrap.md) — primer ADR que escribe `bootstrap`, ya redactado y sin marcadores. No lo copies para una decisión nueva.
- [adr-index](assets/adr-index.md) — índice del directorio de ADR. Úsalo al inicializar o al corregir el índice.

## Scripts del paquete de ADR

`scripts/adr.py` es la herramienta determinista del paquete. No reescribas su lógica a mano.

```bash
# Crear un ADR propuesto, con índice
python3 <skill>/scripts/adr.py new --title "Adoptar PostgreSQL 16 con pgvector" --deciders "Ana, Luis" --update-index

# Ver el resultado sin escribir
python3 <skill>/scripts/adr.py new --title "Adoptar PostgreSQL 16" --dry-run --json

# Cambiar estado; el enlace es obligatorio al sustituir
python3 <skill>/scripts/adr.py status adr/0001-usar-postgresql.md --status superseded --superseded-by 0002-migrar-a-postgresql-16.md

# Inicializar directorio, índice y primer ADR
python3 <skill>/scripts/adr.py bootstrap --dir docs/decisions

# Puerta determinista sobre el repositorio
python3 <skill>/scripts/adr.py check --root .
```

Códigos de salida: `0` sin hallazgos, `1` hallazgos o error de la operación, `2` error de uso. `--json` emite un sobre con `ok`, la operación y los hallazgos.
