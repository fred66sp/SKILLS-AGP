# Evaluación de la edición

El criterio no se sustituye por una nota, pero una nota repetible obliga a mirar lo que se suele saltar. La rúbrica es una estimación con criterio, no un algoritmo: dos revisores pueden discrepar en un punto por dimensión.

## Rúbrica de seis dimensiones

Puntúa de 1 a 10 cada dimensión del texto **final**. Umbral: 42 sobre 60.

| Dimensión | Pregunta |
|---|---|
| Claridad | ¿Las afirmaciones van directas o envueltas en anuncios y andamiaje? |
| Ritmo | ¿La prosa varía y suena natural, o es metronómica? |
| Confianza | ¿Respeta la inteligencia del lector o lo lleva de la mano explicando lo obvio? |
| Autenticidad | ¿Suena a una persona concreta o podría haberlo escrito cualquiera? |
| Densidad | ¿Hay algo recortable? ¿Alguna frase que no aporte dato, decisión ni matiz? |
| Alma | ¿Tiene voz propia, o es un texto neutro que podría servir para cualquier otro tema? |

En registros técnicos y legales, «Alma» no premia la opinión: premia que el texto no sea un relleno impersonal. Un informe perfecto no necesita personalidad; necesita no tener una sola frase vacía.

## Iteraciones

1. Borrador: se corrigen los patrones y se reconstruye el ritmo.
2. Auditoría: se relee el borrador y se anota qué sigue sonando a IA, con identificador.
3. Reescritura: se corrigen los restos y se vuelve a puntuar.

Si la puntuación es igual o superior al umbral, se entrega. Si no, y llevas menos de tres iteraciones, se vuelve a la auditoría. A las tres, se entrega como borrador con los restos declarados. Perseguir la nota más allá de tres pasadas suele empeorar el texto: se sobreedita.

## Puerta determinista

Antes de puntuar, o junto con la puntuación, ejecuta:

```bash
python scripts/redactor.py check <fichero>
python scripts/redactor.py check <fichero> --strict
python scripts/redactor.py check <fichero> --json
```

- Sin `--strict`, el código de salida es 1 si hay defectos deterministas —comillas curvas, raya con espacios, doble guion, signos de apertura, emojis— y 0 si solo hay avisos.
- Con `--strict`, cualquier aviso también devuelve 1.
- Un aviso no es una orden. La puerta detecta señales; corregirlas o justificarlas es criterio del revisor.

La puerta no comprueba significado, hechos, cobertura, voz ni calidad del argumento. No sustituye a la auditoría ni a la revisión de quien publica.

## Falsos positivos

Antes de reescribir, comprueba que no estás destrozando prosa legítima. Esto no es indicio de IA por sí solo:

- Gramática y estilo impecables. Pulcritud no es máquina.
- Vocabulario culto. La IA abusa de palabras concretas, no de todo término culto.
- Una raya suelta, un conector suelto, unas comillas curvas puestas por el editor.
- Prosa seca o sobria. Sequedad sin tics es solo un registro.
- Afirmaciones sin fuente. Casi toda la web va sin citar; la falta de cita no prueba autoría.
- Formato limpio y complejo. Las plantillas y los editores visuales producen eso.

Ante la duda, busca racimos. Una raya sola no es nada; una raya, una tríada, «vibrante tapiz» y un «en conclusión» en el mismo texto es un patrón.

## Señales humanas que se conservan

- Detalle concreto, raro y difícil de inventar: una dirección exacta, una cifra con su origen, una anécdota que no redondea.
- Sentimientos encontrados o tensión sin resolver.
- Referencias de una época o una subcultura concretas.
- Decisiones de autor defendibles: si el autor sabe explicar por qué cortó algo, es su voz.
- Variedad real de longitud de frase.
- Incisos, paréntesis y autocorrecciones.

Sobre-editar destruye justo lo que hace humano un texto. Si el original ya tiene estas señales y pocos tics, el trabajo es dejarlo casi igual.

## Formato de entrega

Por defecto, texto y informe. Si se pide solo el texto, solo el texto.

```markdown
## Texto

<texto final>

## Puntuación

| Dimensión | Puntuación |
|---|---|
| Claridad | X/10 |
| Ritmo | X/10 |
| Confianza | X/10 |
| Autenticidad | X/10 |
| Densidad | X/10 |
| Alma | X/10 |
| **Total** | **X/60** |

## Cambios

- P09, P24: se quitó el paralelismo negativo y dos muletillas.
- P32: se acortaron seis frases y se dejó una de cinco palabras por párrafo.
- P17: titulares a mayúscula inicial.

## No verificado

- Las cifras de 2024 no se contrastaron: no se aportó la fuente.
```

La plantilla está en `assets/informe-edicion.md`.

## Cómo se evalúa la skill

Una edición no demuestra que la skill mejore nada. Para saberlo, se compara con y sin ella sobre el mismo texto y el mismo modelo:

| Métrica | Qué se mide | Señal de fallo |
|---|---|---|
| Preservación factual | Cada cifra, nombre, fecha, cita y reserva coincide con el original | El texto más fluido cambia el significado |
| Especificidad | Las afirmaciones nombran actor, acción, objeto o condición medible | Los beneficios abstractos sustituyen detalles |
| Conservación de voz | Un revisor reconoce al autor en una muestra ciega | Todos los textos adoptan la misma cadencia |
| Accionabilidad | El lector identifica la decisión o el siguiente paso sin releer | La idea aparece tras un preámbulo |
| Coste de revisión | Minutos y cambios materiales hasta aprobar | El resultado limpio exige reconstruirlo |

Casos mínimos: un texto de IA puro, un texto humano bien escrito, un texto con muestra de voz, un texto técnico que debe quedar neutro y un texto con afirmaciones sin fuente. Un texto humano que apenas se toca es una prueba tan importante como uno de IA que se corrige.

## Límites

- La skill reduce tics; no detecta autoría y no debe usarse como detector.
- La puerta comprueba forma, no verdad. Una afirmación falsa puede pasar limpia.
- La puntuación es criterio, no medida reproducible.
- La revisión de quien publica sigue siendo necesaria en cualquier texto con afirmaciones reguladas, compromisos o datos personales.
