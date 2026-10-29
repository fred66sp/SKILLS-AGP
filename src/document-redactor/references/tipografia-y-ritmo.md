# Tipografía y ritmo

Dos capas que la corrección léxica no alcanza. La tipografía se comprueba con reglas; el ritmo, leyendo en voz alta.

## Tipografía del castellano

| Regla | Correcto | Defecto frecuente |
|---|---|---|
| Comillas | «latinas» en primer nivel, `“inglesas”` dentro, `‘simples’` dentro de las inglesas | `“curvas inglesas”` en el primer nivel |
| Raya | Pegada al texto para incisos y diálogo | ` — ` con espacios, ` -- ` doble guion |
| Signos de apertura | ¿Qué…? ¡Vamos! | `Qué…?`, `Vamos!` |
| Mayúsculas | Solo la primera palabra y los nombres propios | `Guía De Estilo Para El Equipo` |
| Puntos suspensivos | Tres puntos, con espacio delante si cierran frase | Más de tres, o pegados a la palabra |
| Guion y raya | Guion para compuestos (teórico-práctico); raya para incisos | Guion donde va raya |
| Cifras | Espacio fino o duro entre miles; coma decimal; unidad separada | `10,000` al estilo inglés |
| Fechas | `29 de octubre de 2026`; en tablas, `2026-10-29` | `10/29/2026` |
| Siglas | Sin puntos (`CSIC`, `API`); plural sin apóstrofo (`APIs`) | `A.P.I.`, `API's` |

### Comillas

Se convierten, no se mezclan. Jerarquía completa:

```text
«Dijo que el informe cita “tres riesgos” sin numerarlos».
```

En HTML, `&laquo;` y `&raquo;` o el carácter directo en UTF-8. En Markdown, el carácter directo. Nunca comillas curvas en el primer nivel salvo que el medio las imponga.

### Raya

Cuatro usos, en este orden de preferencia:

1. Inciso largo que necesita más separación que una coma: «El plazo —tres semanas— lo fijó el cliente.»
2. Diálogo: «—No lo sé —dijo.»
3. Aclaración final sin verbo: «Llegó tarde —otra vez—.»
4. Pausa que sustituye a dos puntos, con moderación.

Si dudas, usa coma, punto o paréntesis. La raya no debe aparecer más de una vez cada cien palabras en prosa corrida: a partir de ahí es un tic.

### Negritas y listas

- Negrita para el término que el lector busca al escanear, no para frases enteras.
- Una lista cuando los elementos son paralelos y se leen mejor sueltos. Si cada elemento empieza con un término en negrita y dos puntos, casi siempre es prosa partida en trozos.
- Viñetas con verbos conjugados o sustantivos, no mezcla de ambos.
- Sin emojis en el cuerpo. En un mensaje informal, uno suelto; nunca uno por viñeta.

### Títulos

Mayúscula inicial y nombres propios. Sin punto final. Longitud orientativa: hasta ocho palabras; si necesita más, el título contiene una idea de más.

## Ritmo

### Burstiness: variar la longitud

La prosa humana alterna. La de IA tiende a una cadencia media uniforme de quince a veinte palabras por frase. La corrección no es acortar todo, sino romper la uniformidad:

> La biblioteca abre de lunes a sábado. Presta libros, organiza talleres, presta la sala del sótano para reuniones de vecinos y, desde 2019, cuando el ayuntamiento aprobó el plan de lectura, también lleva libros a domicilio para quien no puede salir de casa.

La frase de cinco palabras hace que la de cuarenta se pueda leer. Sin contraste, ambas se vuelven monotonía.

Método de comprobación: cuenta las palabras de cada frase de un párrafo. Si todas caen entre quince y veintidós, reescribe al menos una. Busca dos o tres frases de menos de ocho palabras por cada tres párrafos, no más: el efecto contrario también se nota.

### Regla 70/30

Alrededor del 70 % del vocabulario llano y común; un 30 % preciso. Un texto con todo el vocabulario culto suena a traducción; uno con todo llano, a nota de prensa. La precisión se concentra en el sustantivo y el verbo técnico, no en los adornos.

### Aperturas de frase

Los tres defectos más comunes:

1. Todas las frases empiezan por sujeto y verbo: «El equipo hizo. El equipo decidió. El equipo propuso.»
2. Todas empiezan por conector: «Además…, Asimismo…, Por otro lado…».
3. Todas empiezan por una fórmula de anuncio: «Es importante…, Cabe señalar…, Conviene…».

Alternativas: empezar por el complemento cuando sea lo importante («En 2019 se aprobó el plan»), por una condición («Si el mercado cae…»), por una pregunta real, o por el dato.

### Marcadores discursivos

En registros que los admiten —cercano, divulgativo, comercial—, los marcadores del hablante dan textura: «eso sí», «al fin y al cabo», «la verdad es que», «ahora bien», «total, que», «vamos», «oye». Uno cada tres o cuatro párrafos. En técnico y legal, ninguno.

### Cierre

El último párrafo no resume: termina. Un cierre correcto puede ser un dato, una consecuencia, una pregunta abierta o una decisión. Lo que no puede ser es una frase que valga para cualquier documento.

## Límites por registro

| Recurso | Técnico y legal | Divulgativo | Cercano | Comercial |
|---|---|---|---|---|
| Primera persona | No | Con moderación | Sí | Sí |
| Opinión explícita | No | Sí, marcada | Sí | Sí, con datos |
| Frases cortas de énfasis | Poco | Sí | Sí | Sí |
| Marcadores del habla | No | Alguno | Varios | Alguno |
| Humor | No | Muy poco | Sí | Con cuidado |
| Negritas y listas | Sí, funcionales | Poco | Poco | Poco |

La tabla orienta; la guía de estilo del proyecto decide.

## Qué no se toca

- Código, comandos, rutas, identificadores, nombres de fichero, salida de terminal y frontmatter. Se citan tal cual, incluida su tipografía.
- Nombres propios, marcas y cargos: se respeta su grafía oficial aunque la convención del documento use otra caja.
- Cifras, unidades y fechas: se reescribe el formato solo si el documento lo unifica, y se avisa en el informe.
- Citas textuales entrecomilladas: se corrigen las comillas, no las palabras.
