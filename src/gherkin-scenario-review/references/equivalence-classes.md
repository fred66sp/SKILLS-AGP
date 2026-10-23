# Clases de equivalencia y `Scenario Outline`

Léelo en el paso 5 del procedimiento, al revisar un `Scenario Outline` o un `Examples` con varias filas.

Reglas y criterios: los de la nota de la bóveda. Ejemplos: vueltos a situar en el desarrollo de software por petición del usuario; el criterio que ilustran no cambia.

## Definición

Una **clase de equivalencia** es un conjunto de entradas que producen aproximadamente el mismo tipo de salida. Solo hace falta un ejemplo por clase; el resto son redundantes. Un **`Scenario Outline`** es una plantilla de escenario con una tabla `Examples` cuyas filas se sustituyen en los pasos, lo que genera una prueba por fila sin duplicar el escenario.

## Cuándo un esquema se gana sus filas

Un esquema se justifica cuando cada fila representa una clase de equivalencia distinta que el escenario verifica de verdad. Antes de aceptar las filas, escribe en una línea qué comprueba el `Entonces`.

El caso del validador de enlaces lo ilustra al revés:

~~~gherkin
Scenario Outline: El validador señala un enlace roto
  Dado que el documento bajo análisis contiene un enlace a "<ruta>"
  Cuando se ejecuta la validación del documento
  Entonces el informe señala el enlace de "<ruta>"

  Examples:
    | ruta                 |
    | guias/instalacion.md |
    | guias/configuracion.md |
    | api/cli.md           |
    | api/extensiones.md  |
    | guias/vocabulario.md |
    | api/pruebas.md       |
    | guias/flujos.md      |
~~~

Siete filas, siete pruebas. Lo único que ese escenario comprueba es que *el validador detecta un enlace roto*: le doy una ruta, me devuelve esa ruta. No comprueba severidad, ni orden del informe, ni códigos de salida. ¿Es tan distinta una ruta de otra? Apenas. Las siete filas son la misma clase de equivalencia repetida, y por eso:

- no aportan comprensión —un ejemplo ya explica el comportamiento—;
- no aumentan la cobertura real;
- desperdician tiempo de ejecución.

Añade filas solo cuando cambie lo que se afirma, no cuando cambie el dato. Un documento sin enlaces, un enlace relativo roto y un enlace absoluto inalcanzable son tres clases: cada una necesita su `Entonces`, no solo su fila. Si el `Entonces` es idéntico para dos filas, sospecha de la segunda.

## Agrupar `Examples` por lo que el escenario verifica

1. Lista las columnas y marca cuáles llegan a un `<placeholder>` de los pasos.
2. Marca después cuáles cambian el resultado afirmado en el `Entonces`; solo esas definen la clase.
3. Agrupa las filas por ese subconjunto de columnas y quédate con una por grupo.
4. Comprueba si una columna existe solo para documentar un dato: una columna que ningún paso consume no forma parte del comportamiento.
5. Si dos grupos afirman cosas distintas, son dos escenarios, no dos bloques de filas del mismo esquema.

Las clases de severidad sí se ganan sus filas, porque el resultado afirmado cambia. `../assets/example-feature-good.feature` trae un esquema de este tipo con dos filas, una por clase:

~~~gherkin
Scenario Outline: La severidad del hallazgo decide el resultado de la validación
  Dado que el documento contiene un hallazgo de severidad "<severidad>"
  Cuando se ejecuta la validación del documento
  Entonces la validación termina con el resultado "<resultado>"

  Examples:
    | severidad | resultado |
    | error     | fallo     |
    | aviso     | paso      |
~~~

Una tabla que crece añadiendo columnas —`sistema operativo`, `versión de la herramienta`, `marca del documento`— sin que cambie el `Entonces` está hinchada: registra configuración del entorno, no clases de equivalencia. Ese detalle pertenece a la capa de automatización.

## Coste de ejecución

El coste es real y se puede declarar en el informe. En UI web o móvil, un caso típico tarda alrededor de un minuto. Siete filas son siete minutos. Como es habitual tener suites de cientos o miles de casos, las filas redundantes se traducen en cientos o miles de minutos extra de cómputo, dinero y tiempo hasta la entrega.

Estima el coste solo en escenarios de interfaz. En una validación de línea de órdenes la fila redundante cuesta segundos y el hallazgo pierde peso: declara el coste como bajo en lugar de inventarlo.

## `Simplifica por ejemplos`

Es la advertencia de la nota y la comprobación de cierre de este paso. Al escribir Gherkin es muy fácil añadir filas y columnas a una tabla de ejemplos sin pensar en sus consecuencias: búscalas y elimínalas. Un `.feature` revisado con esta regla suele quedarse con un ejemplo por clase, y lo que se pierde de cantidad se gana en claridad: la tabla dice cuántas clases de equivalencia cree el equipo que existen.

## Qué mide el script

- `redundant-examples` (candidato, regla 3): filas por encima del umbral declarado y filas que solo difieren en una columna. El umbral por defecto es de 5 filas (`--max-outline-rows`, declarado en `--help`), y la segunda comprobación salta con tres filas o más. Es heurística: confirma o refuta cada hallazgo antes de escribirlo.
- `outline-missing-placeholder` (determinista, estructura): esquema sin `Examples`, `<placeholder>` sin columna, columna que ningún paso consume o fila con un número de columnas distinto al de la cabecera. Es un fallo de parseo de datos, no una cuestión de estilo.

Un candidato `redundant-examples` también se refuta: ocurre cuando las filas cubren clases distintas —como las de severidad— y el umbral solo ha contado el volumen. Refutado, se declara con su motivo. En `../assets/example-feature-bad.feature` el esquema `Validate findings` ilustra el otro caso: ocho filas, una columna `cache dir` que ningún paso consume y una fila con columnas de más.

El orden y la longitud de los pasos del esquema están en [structure-and-order.md](structure-and-order.md); el punto de vista de sus pasos, en [language-and-voice.md](language-and-voice.md).

Fuente: nota de la bóveda + práctica estándar de Cucumber.
