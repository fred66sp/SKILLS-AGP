# Las cuatro reglas como comprobaciones

Léelo en el paso 3 del procedimiento. Aplica cada regla como una comprobación sobre el texto del `.feature`, con el código de `tools/check-feature.py` que la mide. Reglas y criterios: los de la nota de la bóveda; los ejemplos están vueltos a situar en el desarrollo de software por petición del usuario, y el criterio que ilustran no cambia. Los códigos `unparseable-block` y `outline-missing-placeholder` no son de las cuatro reglas: son estructura, y un bloque con uno de esos hallazgos no es un artefacto de comportamiento revisable.

## Regla 1 — regla de oro: legible sin contexto

**Qué prohíbe.** «Trata a los demás lectores como te gustaría ser tratado.» Un escenario que nadie entiende sin haber estado en la reunión no es especificación. Dos formas del mismo fallo: el escenario vago, que no es procesal ni verificable, y el muro de texto, que comunica el cómo y oculta el qué. Prohíbe además un `Dado` que declara una intención de negocio en lugar de un estado inicial, y cualquier paso fuera del orden `Dado → Cuando → Entonces`.

**Cómo detectarlo**, con `step-order`, `missing-then` y `too-many-steps` como hechos y `low-level-vocab` y `business-intent-given` como candidatos. Lee el título y los pasos sin abrir el resto del archivo:

1. Busca `Dado` después de `Cuando` o de `Entonces`, y escenarios sin ningún `Entonces`.
2. Cuenta los pasos efectivos; más de un dígito exige justificación.
3. Marca el vocabulario de interfaz y de consola: clic, botón, tecleo, espera, scroll, URL explícita del servicio.
4. Marca los `Dado` que empiezan por un deseo de negocio y pregunta ante cada `Entonces` cómo se afirmaría su resultado.

MAL — ultra-declarativo: vago, no procesal, no verificable, y el `Dado` declara una propuesta de negocio:

~~~gherkin
Scenario: Documentación
  Dado que quiero una documentación sin enlaces rotos
  Cuando se compila la documentación
  Entonces sale bien
~~~

La segunda cara es el muro de texto ultra-imperativo: la publicación narrada control a control, con la URL del servicio, la contraseña, esperas y lecturas de consola, y los pares `Cuando`/`Entonces` hundidos en el relato. En `../assets/example-feature-bad.feature` esa cara la representa el escenario `Publish the site`.

BIEN — declarativo, en orden, de un dígito y verificable:

~~~gherkin
Scenario: Fallar la compilación por un enlace relativo roto
  Dado que el documento de guía enlaza a una ruta inexistente
  Cuando el desarrollador ejecuta la compilación de documentación
  Entonces la compilación termina con un código de salida distinto de cero
~~~

## Regla 2 — regla cardinal: un escenario, un comportamiento

**Qué prohíbe.** «Un escenario debe cubrir exactamente un comportamiento independiente.» Dos ciclos acción-verificación, un cambio de actor o de objeto a mitad del escenario, o un título que no anuncia todo lo que el cuerpo hace.

**Cómo detectarlo**, con `multiple-action-outcome` como hecho medible:

1. Cuenta los grupos de `Cuando` seguidos de su `Entonces`. Dos grupos son dos comportamientos.
2. Busca cambios de actor o de objeto dentro del mismo escenario.
3. Compara el título con el cuerpo: si no anuncia la segunda verificación, sobra una mitad.
4. Simula el fallo del primer `Entonces`. Si el resto queda sin ejecutar y sin señal, hay dos comportamientos.

**Beneficios que sostiene la división.**

- Colaboración: el equipo discute una sola cosa a la vez y se alinea antes de implementar.
- Automatización: cada fallo de test apunta a un problema único, sin excavar en la traza.
- Eficiencia: cada unidad de trabajo es menos compleja y el ciclo es más rápido.
- Trazabilidad: un comportamiento = un ejemplo = un escenario = un caso = como mucho un fallo con una causa raíz.
- Responsabilidad: sin muros de texto se sabe con transparencia qué se desarrolla y qué se prueba.

MAL — dos comportamientos con los pares duplicados a la vista:

~~~gherkin
Scenario: Compilación incremental de la documentación
  Dado que la compilación anterior terminó sin errores
  Cuando se modifica un documento y se compila de nuevo
  Entonces solo se recompila el documento modificado
  Cuando se publica el sitio de documentación
  Entonces el sitio publicado contiene el documento modificado
~~~

BIEN — dividido, y el segundo escenario arranca en mitad de la acción con un `Dado` situacional:

~~~gherkin
Scenario: No recompilar los documentos sin cambios
  Dado que la compilación anterior terminó sin errores
  Cuando se modifica un documento y se compila de nuevo
  Entonces solo se recompila el documento modificado

Scenario: Publicar un documento ya compilado
  Dado que la documentación compilada contiene el documento modificado
  Cuando se publica el sitio de documentación
  Entonces el sitio publicado muestra el documento modificado
~~~

**Límite de la regla.** Compilar y publicar pueden considerarse dos comportamientos y también uno solo visto desde el proceso del desarrollador: se compila para poder publicar. La división obligatoria es la de dos ciclos de verificación en el mismo escenario; proponer otra sin un segundo `Cuando` es una estimación del revisor, no una violación determinista.

## Regla 3 — ejemplo único: una clase de equivalencia, un ejemplo

**Qué prohíbe.** «No incluyas ejemplos innecesarios. Céntrate en las clases de equivalencia de la entrada.» Filas de `Examples` que repiten la misma clase, columnas que no cambian el resultado y un `Scenario Outline` usado para no pensar en el comportamiento.

**Cómo detectarlo**, con `redundant-examples` como candidato y `outline-missing-placeholder` como hecho de estructura:

1. Escribe en una línea qué verifica el `Entonces` del esquema.
2. Agrupa las filas por lo que el escenario verifica de verdad, no por lo que la tabla contiene.
3. Pregunta si dos filas producen aproximadamente el mismo tipo de salida: si es así, una sobra.
4. Cuenta el coste de las filas sobrantes cuando el escenario sea de interfaz.

MAL — siete filas de rutas de documento (`guias/instalacion.md`, `guias/configuracion.md`, `api/cli.md`, `api/extensiones.md`, `guias/vocabulario.md`, `api/pruebas.md`, `guias/flujos.md`) afirmadas todas con el mismo `Entonces`: una sola clase repetida siete veces; el caso completo está en [equivalence-classes.md](equivalence-classes.md). BIEN — dos filas, dos clases, porque cambia lo que se afirma:

~~~gherkin
  Examples:
    | severidad | resultado |
    | error     | fallo     |
    | aviso     | paso      |
~~~

## Regla 4 — el cuarto amigo: lenguaje y punto de vista

**Qué prohíbe.** «Imagina que tu profesor de Lengua del instituto va a leer tu Gherkin.» Primera persona ambigua, mezcla de puntos de vista en un mismo escenario, pasos sin sujeto o sin verbo, y pasos que solo se entienden dentro de su escenario.

**Cómo detectarlo**, con `person-mixed` y `no-subject-verb` como candidatos:

1. Decide el punto de vista dominante del archivo y lee cada paso como frase completa.
2. Verifica que todo paso tenga sujeto y verbo; un sintagma suelto no dice qué verificar.
3. Lee un paso aislado: si no se sabe qué es, dónde está y qué ocurre con él, no es reutilizable.
4. Busca `yo` o `mí` conviviendo con `el desarrollador` o `el servicio de CI` en el mismo escenario.

MAL — fragmento sin sujeto ni verbo y primera persona mezclada con tercera:

~~~gherkin
  Entonces la ruta del enlace roto
  Cuando ejecuto la compilación desde mi portátil
~~~

BIEN — frase sujeto-predicado, en tercera persona, legible suelta:

~~~gherkin
  Y el informe de la compilación señala la ruta del enlace roto
  Cuando el desarrollador ejecuta la compilación de documentación
~~~

En [structure-and-order.md](structure-and-order.md) están el orden, la longitud y los hooks; en [equivalence-classes.md](equivalence-classes.md), las clases de entrada; en [language-and-voice.md](language-and-voice.md), el punto de vista.

Fuente: nota de la bóveda + práctica estándar de Cucumber.
