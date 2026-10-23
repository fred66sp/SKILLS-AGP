# Lenguaje y punto de vista

Léelo en el paso 6 del procedimiento, al revisar la redacción de los pasos y su reutilización entre escenarios.

Reglas y criterios: los de la nota de la bóveda. Ejemplos: vueltos a situar en el desarrollo de software por petición del usuario; el criterio que ilustran no cambia.

## Tercera persona

Elige la tercera persona: `el desarrollador`, `la validación`, `el servicio de CI`, `el compilador`. La primera persona es ambigua —`yo` puede ser el programador que escribe el escenario, el usuario que ejecuta la herramienta o el propio sistema— y se rompe en cuanto un escenario habla de dos actores a la vez: `Dado que dos revisores comentan el mismo pull request` deja de tener un `yo` que contar. La tercera persona nombra de forma expresa a cualquier actor o componente del sistema: es objetiva, formal e inequívoca, y por eso es más potente.

La primera persona además obliga a contorsiones para que el mismo paso funcione en bocas distintas. Si el archivo ya usa `yo` de forma consistente, no lo declares violación: registra el punto de vista como preferencia del proyecto y propón la reescritura en tercera persona.

## No mezclar puntos de vista

Un mismo escenario no puede decir `Cuando ejecuto la validación` y `Entonces el informe muestra los hallazgos al revisor`. La mezcla oculta quién ejecuta la acción y rompe la reutilización del paso. Mantén un solo punto de vista por archivo. El script marca la convivencia de `yo`/`mí` con actores en tercera persona como candidato `person-mixed`: lee el escenario completo y confírmalo antes de escribirlo en el informe.

El defecto se cuela al dividir un escenario: `Cuando reviso la caché del build` junto a `Entonces el compilador actualiza la caché` mezcla a quien ejecuta la acción con quien la observa. La fuente muestra el mismo defecto con otros pasos. La división de comportamientos es correcta; el punto de vista, no. El criterio manda sobre el ejemplo.

## Frase sujeto-predicado

Todo paso lleva un sujeto, un verbo y, si acaso, un objeto directo o un sintagma preposicional. Un paso sin verbo no indica qué hacer con él: nadie sabe si hay que verificarlo, abrirlo o ignorarlo.

MAL — fragmento suelto, sin sujeto ni verbo:

~~~gherkin
  Entonces la ruta del enlace roto
~~~

BIEN — frase completa que afirma la presencia de algo:

~~~gherkin
  Y el informe de la compilación señala la ruta del enlace roto
~~~

La reescritura añade el actor (`el informe de la compilación`), el verbo (`señala`) y deja claro qué se verifica. El script señala como candidato `no-subject-verb` los pasos demasiado cortos para contener sujeto y predicado legibles: lee la línea citada y decide, porque un paso breve sí puede ser una frase completa cuando el dominio lo permite.

## Cada paso se entiende suelto

Los pasos se comparten entre escenarios, sobre todo por la automatización. Un paso que depende del contexto de su escenario se reutiliza mal: alguien lo llamará desde un caso donde no significa lo mismo. Sé específico sobre qué es el objeto, dónde está y qué ocurre con él.

MAL — solo se entiende dentro de su escenario:

~~~gherkin
  Entonces falla la compilación
~~~

BIEN — dice el objeto, el lugar y el resultado afirmado:

~~~gherkin
  Entonces la compilación de documentación falla con el informe de enlaces rotos
~~~

El texto del paso es lo que enlaza con la automatización: al renombrar un paso del `.feature`, el enunciado deja de coincidir con su implementación y el escenario queda sin definir. Por eso dos escenarios que redactan el mismo paso de forma distinta son un solo hallazgo: cítalos los dos, propón una única forma y declara el riesgo de reutilización. Antes de dar por bueno un paso, léelo fuera de su escenario, como lo haría quien lo busca reutilizado en otro archivo.

## Los dos conjuntos de palabras clave

Un `.feature` usa un solo idioma de palabras clave, declarado en la primera línea con un encabezado como `# language: es`. `*` funciona como paso alternativo en los dos conjuntos. Los dos conjuntos que admite esta revisión:

| Español | Inglés |
|---|---|
| `Característica` / `Escenario` / `Esquema del escenario` / `Ejemplos` | `Feature` / `Scenario` / `Scenario Outline` / `Examples` |
| `Dado` / `Cuando` / `Entonces` | `Given` / `When` / `Then` |
| `Y` / `Pero` | `And` / `But` |
| `Antecedentes` | `Background` |

Sin encabezado no hay idioma declarado: `scripts/check-feature.py` acepta los dos conjuntos y usa `# language:` solo para saber qué idioma declara el archivo, de modo que un `# language:` no soportado es error de uso (código 2). El runner no es tan tolerante: trabaja con el dialecto declarado, así que un escenario a medias entre `Dado` y `Given` deja pasos sin reconocer. Si el script no reconoce las palabras clave, revisa con los dos conjuntos, informa del motivo y marca el parseo como pendiente de `# language:`.

El texto de los pasos sigue el idioma del negocio, no el de las palabras clave: en un archivo con `# language: en` es correcto que un paso afirme `el informe señala la ruta del enlace roto` si ese es el vocabulario del equipo. Los dos fixtures del paquete muestran los dos conjuntos: `../assets/example-feature-good.feature` está escrito con palabras en español y `../assets/example-feature-bad.feature`, en inglés.

## Comprobaciones del paso 6

1. Decide el punto de vista dominante del archivo y marca los pasos que lo rompen.
2. Marca los pasos sin sujeto o sin verbo y escribe la reescritura como frase completa.
3. Lee cada paso marcado aislado: si no se entiende sin su escenario, reescríbelo con objeto, lugar y resultado.
4. Verifica el encabezado `# language:` y que el archivo no mezcle los dos conjuntos.

Los candidatos que salen de aquí están descritos en [four-rules.md](four-rules.md); la forma del `Dado` situacional, en [structure-and-order.md](structure-and-order.md).

Fuente: nota de la bóveda + práctica estándar de Cucumber.
