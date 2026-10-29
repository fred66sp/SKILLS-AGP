---
name: document-redactor
description: "Redacta y edita la prosa de un documento en castellano con contrato de agente: fija la operación, el registro y los hechos antes de tocar el texto, quita los tics de escritura de IA por racimos y no por casos sueltos, reescribe conservando significado y cobertura, inyecta voz solo en los registros que la admiten, corrige la tipografía española y audita el resultado con una rúbrica de seis dimensiones y una puerta determinista. Úsala al redactar o editar artículos, guías, README, notas de versión, correos, propuestas y documentación, al quitar el tono de IA de un texto, o al adaptar un texto a la voz de un autor. No la uses para decidir qué documentos debe tener un proyecto, para redactar un PRD o un ADR, ni para revisar código."
metadata:
  version: "0.1.0"
---

# Redacción y edición de documentos

Un documento se escribe para un lector que tiene poco tiempo y ninguna obligación de creerte. La escritura de IA falla en dos frentes a la vez: acumula tics reconocibles —importancia inflada, paralelismos negativos, gerundios de consecuencia, relleno— y no tiene voz. Quitar lo primero sin construir lo segundo deja un texto limpio que sigue sonando a máquina.

Esta skill posee la prosa: el registro, la sintaxis, el ritmo, la tipografía y la voz. No posee los hechos, la arquitectura del documento ni el soporte donde vive. Qué documentos debe tener un proyecto es de `document-management-software`; la estructura de un PRD es de `prd-cartographer`; la de un ADR, de `adr-software`. Esta skill no sustituye sus contratos: edita el texto que producen.

## Invariantes de redacción

1. Delimita la operación antes de escribir: redactar un borrador nuevo, editar un texto existente o auditar sin modificar. Una auditoría no toca el fichero.
2. Editar no es reescribir desde cero. Conserva el significado, las afirmaciones, las cifras, los nombres, las fechas, las citas, los enlaces y los compromisos del original.
3. Conserva la cobertura. Si el original tiene cinco ideas y tres párrafos, la edición las mantiene; los párrafos pueden cambiar de forma, el contenido no puede desaparecer. No resumas ni recortes salvo que se pida.
4. No inventes datos, fuentes, citas, ejemplos ni anécdotas. Si una afirmación se queda sin sustento al reescribirla, se marca como pendiente o se pregunta; nunca se rellena con una cita plausible.
5. La edición de estilo no añade ni retira evidencia. Una afirmación sin fuente se señala o se deja como está; no se convierte en un dato con una atribución vaga.
6. Detecta racimos, no casos sueltos. Una raya, un «además» o una palabra culta no prueban nada: lo que delata es la acumulación. Corregir un caso aislado puede empeorar la prosa.
7. Conserva las señales humanas: el detalle concreto y raro, la duda sin resolver, el inciso, la autocorrección, la variedad real de longitud de frase y la decisión de autor que se puede defender.
8. El registro manda. Un texto técnico, legal, de referencia o normativo se queda neutro: ahí la voz humana correcta es la precisión sin adornos. La primera persona, la opinión y el humor solo entran en los registros que los admiten.
9. En castellano, la tipografía es parte del contrato: comillas latinas «» como primer nivel, raya para incisos y diálogo sin sobreusar, signos de apertura ¿¡, mayúscula solo en la primera palabra del titular y en los nombres propios, sin emojis en el cuerpo.
10. El ritmo es la prueba más profunda. Si todas las frases miden y suenan igual, el texto no está terminado aunque no quede un solo tic léxico.
11. No toques código, comandos, identificadores, rutas, frontmatter, datos ni bloques de código. La prosa que los rodea se edita; su contenido se cita tal cual.
12. La convención del documento gana sobre esta skill: guía de estilo del proyecto, plantilla, glosario, medio o manual de marca. Si hay conflicto, se sigue la convención y se declara la diferencia.
13. No entregues como terminado un texto que no ha pasado la auditoría y la puerta determinista. Si no las pasa, se entrega como borrador con lo que queda y por qué.
14. El informe de cambios forma parte del trabajo: qué patrones había, cuáles se corrigieron y cuáles se dejaron a propósito. Sin él, la edición no se puede revisar.
15. Esta skill reduce tics de escritura; no demuestra autoría. Nunca presentes el resultado como prueba de que un texto lo escribió una persona ni de que otro lo escribió una máquina.

## Procedimiento de redacción

**Paso 1 — Delimitar la operación.**
1. Identifica una sola operación: redactar, editar o auditar. Si el encargo mezcla reescribir con cambiar el mensaje, sepáralos: primero se acuerda el contenido, después se edita la prosa.
2. Sitúa el documento: tipo —artículo, guía, README, nota de versión, correo, propuesta, informe—, lector, canal y extensión esperada.
3. Fija el límite de intervención: solo prosa, prosa y estructura, o también hechos. Si el encargo autoriza cambiar afirmaciones, dilo en el informe; si no, están congeladas.
4. Localiza la convención aplicable antes de escribir: guía de estilo del repositorio, plantilla del documento, glosario, manual de marca o ejemplos previos del mismo autor.

**Paso 2 — Fijar hechos y voz.**
1. Extrae y congela el inventario de hechos: cifras, unidades, nombres propios, fechas, versiones, citas, enlaces y compromisos. Ese inventario se compara al final; cualquier diferencia es un defecto de la edición.
2. Marca lo que no tiene fuente. Una cifra sin origen no se «mejora»: se mantiene, se señala o se pregunta.
3. Si hay muestra de la escritura del autor, léela antes de reescribir y anota longitud de frase, nivel léxico, apertura de párrafos, puntuación, coletillas y forma de enlazar ideas. Imita esos rasgos; no los sustituyas por un registro más culto.
4. Si no hay muestra y el encargo no fija registro, infiere el registro del propio texto y del soporte. No preguntes por preguntar: pregunta solo si el registro cambia el resultado de forma material.

**Paso 3 — Inventariar patrones.**
1. Lee `references/patrones-ia.md` y recorre el texto con sus identificadores. Anota el patrón, la línea y el fragmento; no corrijas todavía.
2. Distingue señales de defecto: la tipografía incorrecta y los artefactos de chat son defectos; el léxico, la retórica y el ritmo son señales que exigen juicio.
3. Busca racimos. Un «sin embargo» no es un tic; cinco aperturas con «Además» seguidas sí. Un patrón aislado se deja salvo que suene mal por sí mismo.
4. Comprueba la sección de falsos positivos antes de tocar prosa legítima: pulcritud, vocabulario culto, un inciso, una apertura de carta y una raya suelta no son indicios.

**Paso 4 — Reescribir.**
1. Corrige primero lo que no admite discusión: tipografía, artefactos de chat, atribuciones vagas, relleno y conclusión genérica.
2. Sustituye cada tic por la construcción natural que el propio texto pedía, no por una fórmula de reemplazo. Si quitar una palabra debilita la frase, la frase ya era débil; si la palabra es la correcta, se queda.
3. Reconstruye el ritmo: alterna frases cortas con frases que se toman su tiempo. Un párrafo de frases idénticas se reescribe, no se retoca.
4. Ajusta la voz según el registro y la muestra, con `references/voz-y-registro.md`. En técnico y legal, no inyectes personalidad: elimina adornos y deja el dato.
5. Conserva la estructura del documento salvo que el encargo incluya cambiarla. Un README no se convierte en ensayo ni un informe en artículo de opinión.
6. No reescribas bloques de código, comandos ni frontmatter. Si el texto depende de ellos, la edición se limita a la prosa que los introduce y los comenta.

**Paso 5 — Auditar.**
1. Segunda pasada sobre tu propio borrador: «¿qué sigue sonando a IA aquí?». Anota cada resto con su identificador.
2. Puntúa la rúbrica de seis dimensiones de `references/evaluacion.md`. Es criterio, no algoritmo; el umbral es 42 sobre 60.
3. Si queda por debajo del umbral y llevas menos de tres iteraciones, vuelve al paso 4. Si llevas tres, entrega el texto como borrador y declara los restos.
4. Comprueba el inventario de hechos del paso 2: toda cifra, nombre, fecha, cita y enlace sigue igual. Una diferencia se corrige antes de continuar.

**Paso 6 — Pasar la puerta.**
1. Ejecuta `python scripts/redactor.py check <fichero>` sobre el texto final. Sin `--strict`, falla con los defectos deterministas; con `--strict`, también con los avisos.
2. Corrige lo que la puerta marque. Si un aviso es un falso positivo, dilo en el informe y no lo silencies cambiando el texto.
3. La puerta no juzga el significado, la voz ni la calidad del argumento. No sustituye a la auditoría ni a la revisión humana.

**Paso 7 — Entregar.**
1. Entrega el texto final en el soporte que corresponda y, salvo que se pida solo el texto, el informe de `assets/informe-edicion.md`.
2. En el informe, nombra los patrones corregidos con su identificador, la puntuación por dimensión y lo que se dejó a propósito.
3. Declara lo no verificado: hechos sin fuente, afirmaciones que no se pudieron contrastar, registros ambiguos y límites de la revisión.

## Errores y paradas de redacción

- Si el texto ya es humano y está limpio, no lo toques: dilo y explica por qué. Sobre-editar destruye lo que lo hacía bueno.
- Si el encargo es «que suene humano» sobre un texto sin hechos ni intención propia, no hay nada que humanizar: pide el material de origen antes de escribir.
- Si el documento es un contrato, un texto legal, una política publicada o una comunicación sujeta a aprobación, la edición es de forma y no de fondo; cualquier cambio de significado lo aprueba su responsable.
- Si el texto contiene afirmaciones reguladas —salud, dinero, seguridad, datos personales—, no las reformules para que suenen mejor: señálalas y deja la decisión a quien responde de ellas.
- Si la muestra de voz contradice la guía de estilo del proyecto, gana la guía y se declara la diferencia.
- Si el registro es genuinamente ambiguo y cambia el resultado, haz una sola pregunta; si no cambia, decide y dilo.
- Si el usuario pide solo el texto, entrega solo el texto. El informe es el valor por defecto, no una imposición.
- Si la puerta falla por un defecto que no puedes corregir sin cambiar el significado, no la des por superada: entrega el borrador y declara el bloqueo.

## Resultado de redacción

```text
Estado: completado | borrador | bloqueado
Operación: redactar | editar | auditar
Documento: <tipo, lector, canal, registro>
Hechos congelados: <cifras, nombres, fechas, citas y enlaces comprobados>
Patrones corregidos: <identificadores y qué se cambió>
Patrones conservados: <identificadores y por qué>
Puntuación: <clara X, ritmo X, confianza X, autenticidad X, densidad X, alma X — total X/60>
Puerta: <comando y resultado>
No verificado: <lista, o "ninguno">
```

## Referencias de redacción

- [patrones-ia](references/patrones-ia.md) — catálogo numerado de tics de la escritura de IA en castellano, agrupados por contenido, léxico, estilo, comunicación y relleno, con señales, ejemplo y corrección. Se lee en el paso 3.
- [tipografia-y-ritmo](references/tipografia-y-ritmo.md) — comillas, raya, titulares, signos de apertura, emojis, negritas, listas, *burstiness*, regla 70/30 y marcadores discursivos. Se lee en los pasos 3 y 4.
- [voz-y-registro](references/voz-y-registro.md) — modos de trabajo, perfiles de registro, calibración con una muestra del autor, límites de la voz y qué no se toca. Se lee en los pasos 2 y 4.
- [evaluacion](references/evaluacion.md) — rúbrica de seis dimensiones, formato de entrega, falsos positivos, señales humanas y método de evaluación con y sin skill. Se lee en el paso 5.
