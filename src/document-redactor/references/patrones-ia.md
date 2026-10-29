# Patrones de escritura de IA en castellano

Catálogo de señales, no lista negra. Cada patrón tiene un identificador estable para que la edición se pueda revisar: `P01`…`P33`. La puerta `scripts/redactor.py` detecta los que se pueden comprobar con una expresión; el resto exige criterio.

## Cómo se usa

1. Recorre el texto y anota los identificadores que aparezcan, con su línea y su fragmento.
2. Busca **racimos**: tres o más patrones en el mismo párrafo, o el mismo patrón repetido en párrafos consecutivos. Un caso aislado se deja salvo que suene mal por sí mismo.
3. Corrige primero los que no admiten discusión —tipografía, artefactos de chat, atribuciones vagas, relleno— y después los que dependen del contexto.
4. No apliques sustituciones mecánicas. La corrección correcta es la que el propio texto pedía.

La regla de oro: si quitar una palabra debilita la frase, la frase ya era débil; si la palabra es la correcta, se queda.

## A. Contenido inflado

### P01. Importancia y legado indebidos
**Señales:** «marcó un antes y un después», «sentó las bases de», «un momento decisivo en la evolución de», «se erige como testimonio de», «refleja una tendencia más amplia», «jugó un papel fundamental».
**Problema:** el texto añade una capa de trascendencia que el hecho no sostiene.
**Antes:** «El instituto se fundó en 1989, marcando un momento decisivo en la estadística regional.»
**Después:** «El instituto se creó en 1989 para recoger y publicar estadística regional.»

### P02. Notabilidad y cobertura mediática
**Señales:** «reconocido a nivel mundial», «aclamado por la crítica», «con una sólida presencia en redes», listar medios sin citar qué dijo cada uno.
**Problema:** se sustituye la prueba por una enumeración de prestigio.
**Corrección:** una cita concreta, con medio y fecha; si no existe, se retira la afirmación.

### P03. Gerundio analítico
**Señales:** cadenas de gerundio al final de la frase: «destacando que…», «poniendo de manifiesto…», «reflejando así…», «simbolizando…».
**Problema:** finge análisis y alarga la frase sin añadir información.
**Antes:** «La paleta conecta con el paisaje, simbolizando el mar y reflejando así el vínculo con la tierra.»
**Después:** «El arquitecto dijo que eligió los azules y verdes por el mar y el paisaje.»

### P04. Lenguaje promocional
**Señales:** «solución integral», «experiencia única», «enclavado en el corazón de», «un enclave vibrante», «de una belleza impresionante», «imprescindible», «de vanguardia».
**Problema:** el tono de folleto invade textos que deberían ser neutros.
**Corrección:** qué es, dónde está, qué tiene. El adjetivo se cambia por un dato.

### P05. Atribución vaga
**Señales:** «los expertos coinciden», «diversos estudios demuestran», «según fuentes del sector», «se dice que», «está demostrado que» sin referencia.
**Problema:** se atribuye una afirmación a una autoridad difusa.
**Corrección:** nombrar la fuente, la fecha y el alcance; si no se conocen, declarar que no se conocen.

### P06. Sección formulista de retos y futuro
**Señales:** «A pesar de sus… se enfrenta a varios retos», «Pese a estos desafíos… sigue prosperando», «Retos y perspectivas», «El futuro es prometedor».
**Problema:** se cierra el documento con un párrafo que no aporta ningún hecho y podría pertenecer a cualquier otro.
**Corrección:** el hecho concreto que se sepa —una cifra, una fecha, una decisión— o nada.

### P07. Léxico sobreusado
**Señales:** profundizar, adentrarse, sumergirse en, fomentar, impulsar, potenciar, optimizar, maximizar, subrayar, recalcar, poner de relieve, el panorama, el ámbito, el universo de, un sinfín de, una miríada de, un abanico de, una amplia gama de, robusto, sólido, holístico, sinérgico, disruptivo, innovador, vanguardista, en aras de, de la mano de.
**Problema:** no están prohibidas; lo que delata es la acumulación y su uso como comodín.
**Corrección:** el verbo concreto («mejorar», «ampliar», «medir») o la cifra. «Una amplia gama» puede ser exacta; «un sinfín de» casi nunca.

### P08. Evitación de la cópula
**Señales:** «se erige como», «se posiciona como», «constituye», «representa un», «cuenta con» donde cabría «es» o «tiene».
**Problema:** se cambia una frase llana por una construcción recargada para parecer más grave.
**Antes:** «La sala se erige como el espacio de arte contemporáneo y cuenta con cuatro salas.»
**Después:** «La sala es el espacio de arte contemporáneo. Tiene cuatro salas.»

### P09. Paralelismo negativo
**Señales:** «No solo X, sino (también) Y», «No se trata (solo) de X, sino de Y», «Más que X, es Y».
**Problema:** es el tic más reconocible del castellano de IA y casi nunca añade matiz: la segunda mitad suele ser la afirmación que se quería hacer.
**Antes:** «No es simplemente una canción, es una declaración de intenciones.»
**Después:** «La canción es una declaración de intenciones.»

### P10. Tríada compulsiva
**Señales:** ideas forzadas en grupos de tres: «rápido, fácil y eficaz», «innovación, inspiración e impacto», «X, Y y Z» en cada enumeración.
**Problema:** agrupar de tres en tres para parecer completo.
**Corrección:** dos elementos suelen bastar; si hay cuatro, se ponen cuatro.

### P11. Variación elegante
**Señales:** llamar a lo mismo de tres formas en frases seguidas: «el protagonista», «el personaje principal», «la figura central», «el héroe».
**Problema:** se evita la repetición a costa de la claridad.
**Corrección:** repetir el término correcto. Repetir no es un defecto.

### P12. Rangos falsos
**Señales:** «desde X hasta Y» donde los extremos no están en una escala: «desde principiantes hasta expertos», «de la A a la Z», «desde startups a multinacionales».
**Problema:** la fórmula sugiere una cobertura que no existe.
**Corrección:** enumerar lo que hay.

### P13. Impersonal de relleno
**Señales:** «se puede observar que», «cabe señalar que», «se hace necesario», «cabe preguntarse», «es preciso destacar».
**Problema:** esconde al actor o elimina el sujeto cuando la frase activa sería más clara.
**Corrección:** sujeto y verbo. «El sistema guarda los resultados solo» en lugar de «se puede observar que los resultados se preservan».

## B. Estilo y tipografía

### P14. Raya sobreusada
**Regla:** la raya —existe en castellano— sirve para incisos y diálogo. Lo que delata es usarla donde irían coma, punto, dos puntos o paréntesis, o escribirla con espacios al estilo inglés y como doble guion.
**Corrección:** revisar cada raya. Si es un inciso legítimo, se queda; si sustituye a una coma por costumbre anglosajona, se cambia.

### P15. Negritas mecánicas
**Problema:** frases enteras en negrita sin jerarquía: cada concepto, cada cifra, cada advertencia.
**Corrección:** negrita solo para el término que el lector busca al escanear. Si hay más de dos por sección, sobra alguna.

### P16. Lista con etiqueta en negrita
**Señales:** viñetas que abren con `**Término:** definición` en serie.
**Problema:** convierte prosa en formulario y fragmenta ideas que se leían mejor seguidas.
**Corrección:** un párrafo con las ideas enlazadas, o una lista real de elementos paralelos, sin etiqueta redundante.

### P17. Title case en titulares
**Regla:** el español no usa mayúscula en cada palabra. Solo la primera palabra y los nombres propios.
**Antes:** «## Negociaciones Estratégicas Y Alianzas Globales»
**Después:** «## Negociaciones estratégicas y alianzas globales»

### P18. Emojis en el cuerpo
**Problema:** decorar titulares y viñetas con iconos que no aportan información y rompen la lectura en voz alta o en un lector de pantalla.
**Corrección:** quitarlos. Un emoji suelto en un mensaje informal no es un tic; una lista de cinco, sí.

### P19. Comillas inglesas
**Regla:** jerarquía del castellano: «latinas» como primer nivel, “inglesas” dentro de ellas y ‘simples’ dentro de las inglesas. Convertir las comillas curvas y rectas del original a latinas salvo que el medio imponga otra cosa.
**Antes:** «Dijo que "el proyecto va según lo previsto".»
**Después:** «Dijo que «el proyecto va según lo previsto».»

## C. Comunicación

### P20. Artefactos de chat
**Señales:** «¡Claro! Aquí tienes…», «Espero que te sirva», «¡Por supuesto!», «Si necesitas algo más, dímelo», «Aquí va un resumen de…».
**Problema:** texto de conversación pegado como contenido.
**Corrección:** empezar por la primera afirmación útil; el saludo se queda solo si el soporte es un correo y el destinatario lo espera.

### P21. Avisos de corte y conjetura disfrazada
**Señales:** «hasta mi última actualización», «según la información disponible», «aunque los detalles son escasos…», «probablemente se crió…», «se cree que».
**Problema:** se escribe un párrafo sobre no haber encontrado la fuente y después se rellena con una hipótesis presentada como dato.
**Corrección:** decir lo que no se sabe y parar, o citar la fuente real.

### P22. Gerundio de consecuencia
**Señales:** «…, logrando así…», «…, garantizando…», «…, permitiendo…», «…, consiguiendo que…».
**Problema:** finge una relación causal que la frase no demuestra.
**Corrección:** punto y frase nueva, o «y así».
**Antes:** «Rediseñamos el alta, reduciendo el abandono y logrando que más usuarios terminaran el registro.»
**Después:** «Rediseñamos el alta. El abandono bajó y más usuarios terminaron el registro.»

### P23. Tono servil
**Señales:** «¡Excelente pregunta!», «Tienes toda la razón», «Es un punto muy acertado».
**Problema:** halago previo a la respuesta, propio de un asistente, no de un documento.
**Corrección:** responder. El reconocimiento del interlocutor, si hace falta, va en una frase sobria.

## D. Relleno y matización

### P24. Muletillas
**Señales:** «cabe destacar/señalar/mencionar que», «es importante señalar/tener en cuenta», «en el mundo actual», «en la era digital», «hoy en día» en exceso, «dicho esto», «con esto en mente».
**Corrección:** suprimir la fórmula y dejar la afirmación. «Cabe destacar que los datos muestran» → «Los datos muestran».

### P25. Matización excesiva
**Señales:** «podría quizá considerarse que, en cierto modo, tal vez…».
**Problema:** la acumulación de salvedades vacía la afirmación.
**Corrección:** conservar la incertidumbre real y una sola marca por frase.

### P26. Conclusión genérica
**Señales:** «En resumen», «En conclusión», «En definitiva», «En última instancia», «El futuro es prometedor», «Tiempos apasionantes por delante».
**Problema:** se cierra con una frase que no contiene ningún hecho y que podría cerrar cualquier otro texto.
**Corrección:** el último dato concreto o la última consecuencia. Si no hay nada que añadir, terminar antes.

### P27. Signposting mecánico
**Señales:** «En primer lugar… en segundo lugar… por último…», «Por un lado… por otro lado…», «Vamos a sumergirnos en…», «Veamos a continuación…», «Sin más dilación…».
**Problema:** se anuncia lo que se va a hacer en lugar de hacerlo.
**Corrección:** empezar por el contenido. El orden se entiende sin numerarlo.

### P28. Tropos de autoridad
**Señales:** «La verdadera pregunta es», «en el fondo», «lo que de verdad importa», «el quid de la cuestión».
**Problema:** se anuncia una revelación que la frase siguiente no cumple.
**Corrección:** hacer la pregunta o la afirmación directamente.

### P29. Encabezado fragmentado
**Señales:** un encabezado seguido de una frase de una línea que lo repite antes del contenido.
**Corrección:** suprimir la frase; el encabezado ya la dice.

### P30. Escritura anclada al cambio
**Problema:** documentación y comentarios que narran el diff —«esta función se añadió para sustituir el enfoque anterior»— en vez de describir lo que hay. Se acepta en notas de versión, changelogs y guías de migración.
**Corrección:** describir el estado actual: qué hace, con qué límite y por qué.

## E. Castellano y ritmo

### P31. Aposición de manual
**Señales:** «La paella, ese plato emblemático de nuestra gastronomía, …», «Cervantes, insigne autor del Quijote, …».
**Problema:** se explica lo que el lector ya sabe con una aposición pomposa.
**Corrección:** el dato que aporte algo; si no, se suprime.

### P32. Ritmo uniforme
**Señales:** todas las frases con longitud y estructura parecidas; cadencia de metrónomo.
**Problema:** es el tic más profundo y el que más delata, porque sobrevive a la corrección del léxico.
**Corrección:** alternar frases de tres o cuatro palabras con frases de veinticinco o treinta. Ver `tipografia-y-ritmo.md`.

### P33. Conectores formulaicos en exceso
**Señales:** «Además», «Asimismo», «Por consiguiente», «No obstante», «Sin embargo» abriendo párrafo tras párrafo.
**Problema:** un conector suelto no es un tic; cinco aperturas iguales sí.
**Corrección:** a veces el mejor conector es ninguno. Empezar por el sujeto.

## Corrección de un racimo

Texto recibido:

> En el competitivo mundo actual, la biblioteca se erige como un referente cultural que marca un antes y un después. No solo ofrece libros, sino también un espacio de encuentro. Además, cuenta con un sinfín de actividades. Cabe destacar que su equipo, apasionado y comprometido, trabaja cada día para fomentar la lectura, logrando así acercar la cultura a todos los públicos. En definitiva, un lugar imprescindible.

Racimo: P24, P08, P01, P09, P07, P24, P03/P22, P26, P04. Se corrige el fondo y el ritmo, no cada palabra por separado:

> La biblioteca abre de lunes a sábado. Presta libros, organiza talleres y deja una sala para estudiar. El equipo son cuatro personas, dos de ellas a media jornada, y el año pasado recibieron 1.200 visitas de institutos.

La segunda versión no arregla el texto: lo sustituye por los hechos que el primero escondía. Si esos hechos no existen, la corrección honesta es preguntarlos, no inventarlos.

## Procedencia

El catálogo se apoya en los patrones documentados por [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) y en las adaptaciones al castellano de [`humanamente`](https://github.com/vicentealvarezasencio/humanamente) y de [`blader/humanizer`](https://github.com/blader/humanizer), ambos con licencia MIT. Los ejemplos y la redacción de este catálogo son propios.
