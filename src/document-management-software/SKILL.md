---
name: document-management-software
description: "Gestiona la documentación de un proyecto de software como conocimiento verificable: decide qué artefactos merecen existir, los redacta desde evidencia, evita duplicar la fuente de verdad y demuestra con comprobaciones que lo afirmado sigue siendo cierto. Úsala cuando el agente vaya a crear, revisar, actualizar o auditar README, guías de contribución, PRD, SDD, arquitectura, ADR, API, instalación, operación, runbooks, notas de release, documentación de features u otra documentación técnica de un proyecto de software, y también cuando detecte documentación obsoleta, contradictoria o duplicada. No la uses para contenido comercial, artículos, material de marketing, documentación de producto no técnica, la descripción de una skill de agente, ni para sustituir tests, contratos ejecutables, comentarios de código o mensajes de commit."
metadata:
  version: "1.0.1"
---

# Gestión documental de software

Gestiona la documentación como conocimiento con fuente de verdad, no como texto de acompañamiento. Inspecciona antes de escribir, decide la intervención más pequeña que resuelve el problema, redacta solo lo sustentado y demuestra con comprobaciones que el resultado no contradice al software.

## Invariantes de gestión documental

1. No empieces a escribir. Ninguna redacción es válida sin delimitar antes el encargo y localizar las fuentes disponibles.
2. No conviertas una suposición plausible en un hecho documental. Toda afirmación material debe poder rastrearse hasta una fuente concreta.
3. Una afirmación material tiene una sola fuente canónica. Antes de escribir, comprueba si ya está documentada y dónde corresponde que viva.
4. La documentación es proporcional al riesgo, a la audiencia y al coste de reconstruir el conocimiento. Un documento que nadie consulta y nada evita es un defecto, no una entrega.
5. Actualizar prevalece sobre duplicar; corregir prevalece sobre ampliar; no crear prevalece sobre corregir cuando lo existente ya es correcto.
6. El estado implementado y la intención futura son afirmaciones distintas y no se mezclan en el mismo párrafo sin señalarlo.
7. La política documental del repositorio prevalece sobre cualquier estructura genérica. Si el proyecto ya tiene convención, se respeta.
8. No destruyas conocimiento válido para simplificar. Antes de eliminar, determina qué información quedaría sin representación.
9. No declares terminada una intervención documental sin ejecutar la verificación del paso 6 y mostrar su resultado.
10. Ante contradicción entre fuentes, no la resuelvas con redacción ambigua: hazla visible y pide decisión si el alcance no permite resolverla.
11. No escribas referencias vivas: ni estado de Git, ni remoto o publicación, ni rutas de una máquina concreta, ni recuentos de artefactos que cambian. Envejecen sin aviso y nadie las actualiza.

## Procedimiento

**Paso 1: Delimitar el encargo.**
1. Identifica qué se pide de entre las cuatro operaciones posibles: crear un artefacto, actualizar uno existente, auditar sin modificar, o responder una pregunta sobre el estado documental.
2. Identifica la audiencia y el uso previsto: quien lee documentación de instalación ejecuta pasos; quien lee un ADR decide; quien lee una API integra.
3. Identifica la fuente de verdad por afirmación: código, tests, configuración, esquemas, contratos, historial Git, documentación existente, decisión explícita del usuario o fuente externa oficial.
4. Si falta una fuente imprescindible o el encargo mezcla intención y estado sin aclararlo, formula una sola pregunta concreta y detente. No interrogues para rellenar una plantilla.

**Paso 2: Inventariar antes de decidir.**
1. Ejecuta `python3 scripts/doc-inventory.py --root <ruta>` sobre el árbol documental afectado. Devuelve el inventario y los hallazgos deterministas: enlaces relativos rotos, documentos sin título, documentos vacíos, encabezados repetidos entre documentos y referencias vivas escritas como documentación (estado de Git, rutas de una máquina concreta y recuentos de artefactos).
2. Lee `references/document-inventory.md` para asignar responsabilidad a cada artefacto existente y decidir si hace falta uno nuevo.
3. Resume la cobertura actual: qué responsabilidad documental ya está cubierta, cuál falta y cuál está cubierta dos veces.

**Paso 3: Fijar la certeza de cada afirmación.**
1. Lee `references/evidence-and-claims.md` cuando alguna afirmación no esté directamente sustentada por una fuente.
2. Clasifica la afirmación antes de redactarla: confirmada, inferencia, propuesta, desconocida, contradictoria u obsoleta.
3. Si la verificación exige leer código, tests o configuración, hazlo de forma dirigida y acota la exploración al tema del encargo.

**Paso 4: Elegir la intervención mínima.**
1. Selecciona una sola intervención: ninguna, corrección puntual, reordenación, eliminación de duplicación, ampliación localizada, referencias cruzadas o creación de un artefacto con responsabilidad propia.
2. Rellena `assets/documentation-plan-template.md` cuando el encargo afecte a más de un documento o cuando la decisión de crear o eliminar no sea evidente.
3. Descarta la creación de un documento nuevo si el conocimiento cabe en uno existente sin degradar su responsabilidad.
4. Si la intervención detectada es un refactor documental masivo, informa del coste y del riesgo de revisión antes de ejecutarlo.

**Paso 5: Redactar.**
1. Lee `references/authoring-rules.md` antes de escribir o reescribir contenido.
2. Escribe en imperativo y en tercera persona, con la terminología que ya usa el proyecto, no con sinónimos nuevos.
3. Copia rutas, comandos, nombres, tipos y valores exactos de la fuente; no los reconstruyas de memoria ni los inventes.
4. Marca explícitamente lo que es propuesta, lo que es inferencia y lo que no se pudo determinar.
5. Deja fuera toda sección que no aporte información verificable. Una sección vacía de plantilla es un defecto de entrega.

**Paso 6: Verificar.**
1. Vuelve a ejecutar `python3 scripts/doc-inventory.py --root <ruta>`: un enlace roto, un encabezado nuevo duplicado o una referencia viva nueva es una regresión que introduce este cambio.
2. Lee `references/audit-checklist.md` y recorre la lista de comprobación aplicable al tipo de intervención.
3. Contraste cada afirmación modificada contra su fuente. Si una afirmación no se puede verificar en el alcance disponible, degrada su redacción a lo que sí se sostiene.
4. Comprueba que no se perdió conocimiento válido: compara el contenido anterior con el nuevo antes de aceptar una reescritura.

**Paso 7: Cerrar con evidencia.**
1. Informa de la intervención aplicada, de los artefactos tocados y de la verificación ejecutada con su resultado.
2. Rellena `assets/audit-report-template.md` cuando el encargo fuera una auditoría o cuando quedaran hallazgos sin resolver.
3. Enumera lo que quedó pendiente por falta de fuente, con la pregunta exacta que lo desbloquea.

## Gestión de errores

- Si `scripts/doc-inventory.py` sale con código 2, corrige los argumentos: la ruta no existe o el patrón no es válido. No sustituyas el script por una exploración manual del árbol.
- Si el script sale con código 3, hay hallazgos reales. Trátalos como entrada del paso 4, no como ruido: decide para cada uno si se corrige en este encargo o se reporta.
- Si la fuente contradice la documentación existente, determina primero cuál tiene responsabilidad sobre esa afirmación. Si ambas pretenden tenerla, reporta la contradicción y no elijas por cuenta propia.
- Si el repositorio no documenta convención documental, aplica la estructura mínima justificada por el contenido y no importes una plantilla completa.
- Si el encargo pide documentar algo que no existe todavía en el software, redáctalo como propuesta explícita y no como estado actual.
- Si un documento externo o dependencia no se puede consultar en la versión usada por el proyecto, no atribuyas comportamiento a esa versión: declara la limitación.

## Resultado de la intervención documental

Cierra siempre con estas cinco líneas, rellenadas con evidencia y sin adjetivos:

```text
Intervención: <ninguna | corrección | actualización | creación | auditoría>
Artefactos: <rutas relativas tocadas, o "ninguno">
Verificación: <comando ejecutado y su código de salida>
Afirmaciones no sustentadas: <lista, o "ninguna">
Pendiente: <qué falta y qué pregunta lo desbloquea, o "nada">
```

Si un campo no se puede rellenar con evidencia, ese campo es el hallazgo.

## Referencias

- [document-inventory](references/document-inventory.md): responsabilidad de cada tipo de documento y decisión de crearlo o no. Léelo en el paso 2.
- [evidence-and-claims](references/evidence-and-claims.md): grados de certeza, verificación por tipo de fuente y tratamiento de contradicciones. Léelo en el paso 3.
- [authoring-rules](references/authoring-rules.md): reglas de proporcionalidad, DRY documental, terminología, redacción y exclusión de las referencias vivas. Léelo en el paso 5.
- [audit-checklist](references/audit-checklist.md): auditoría de solo lectura y verificación de cierre. Léelo en el paso 6.
- [documentation-plan-template](assets/documentation-plan-template.md): plan de intervención. Úsalo en el paso 4.
- [audit-report-template](assets/audit-report-template.md): informe de auditoría. Úsalo en el paso 7.
- [doc-inventory](scripts/doc-inventory.py): inventario determinista y hallazgos de documentación, incluidas las referencias vivas. Úsalo en los pasos 2 y 6.
- [test-doc-inventory](scripts/test-doc-inventory.py): comprobaciones del script: `python3 scripts/test-doc-inventory.py`. Se ejecutan al cambiar el script o sus clases de hallazgo.
