# Estructura y orden de los pasos

Léelo en los pasos 3 y 4 del procedimiento, al juzgar un escenario con varios comportamientos y al medir su orden, su longitud y su nivel de detalle.

Reglas y criterios: los de la nota de la bóveda. Ejemplos: vueltos a situar en el desarrollo de software por petición del usuario; el criterio que ilustran no cambia.

## Orden estricto

`Dado → Cuando → Entonces` es `setup → acción → verificación`, el mismo `arrange → act → assert` del código de pruebas. Cada tipo hace una sola cosa:

- **`Dado`** establece un estado inicial verificable, no una intención de negocio.
- **`Cuando`** inicia la acción que ejecuta el actor sobre el producto.
- **`Entonces`** afirma el resultado de esa acción.

Un `Dado` después del primer `Cuando` o del primer `Entonces` rompe la secuencia: el script lo marca como `step-order`. Convierte ese paso en estado inicial antes de la acción, o divide el escenario.

## Cronología

Los pasos se escriben en el orden temporal en que ocurren, para que un framework los ejecute sin reordenar nada. Un `Entonces` que describe algo anterior a su `Cuando` es un hallazgo de orden aunque el vocabulario sea correcto.

## Respeta el tipo de paso

No etiquetes de `Dado` un paso que es acción, ni dejes una verificación como `Dado`, solo para conservar la apariencia de orden.

- Estado legítimo: `Dado que el informe de la compilación anterior señala un enlace roto`. El sistema ya está ahí y es observable.
- Acción disfrazada: `Dado que el desarrollador ejecuta la compilación`. Es la acción del escenario: va en `Cuando`. Etiquetada de `Dado`, el escenario se queda sin acción visible y la verificación llega sin nada que la preceda, así que ni el lector ni el script pueden juzgar el orden.

Decide el tipo preguntándote si el paso describe un estado (`Dado`), una acción (`Cuando`) o una afirmación (`Entonces`).

## Longitud de un solo dígito

Cuenta los pasos efectivos del escenario: los propios más los declarados en `Background`. El umbral por defecto del script es de 9 pasos (`--max-steps`, declarado en su `--help`); superarlo emite `too-many-steps`.

Si un escenario necesita más pasos, la pregunta no es cómo numerarlos, sino cuál de estas dos cosas está pasando:

1. El escenario baja demasiado de nivel y hay pasos que pertenecen a la automatización.
2. El escenario cubre más de un comportamiento y hay que dividirlo.

## Declarativo frente a imperativo

El Gherkin declarativo describe *qué* se quiere y deja el *cómo* debajo. El imperativo describe cada interacción: qué control se pulsa, qué campo se rellena, cuánto se espera.

Detecta el modo imperativo por vocabulario de bajo nivel: clic, botón, tecleo, espera, scroll, URL explícita del servicio. El script lo señala como candidato `low-level-vocab`; confírmalo antes de escribirlo en el informe, porque hay términos de esa lista que en cierto proyecto son lenguaje del dominio y no de la interfaz.

Regla de decisión: si el detalle de la herramienta no cambia lo que el comportamiento verifica, súbelo de nivel.

MAL — cómo, no qué:

~~~gherkin
  Cuando el desarrollador hace clic en el botón «Compilar» de la barra lateral
  Y espera cinco segundos a que termine la barra de progreso
~~~

BIEN — qué, y el detalle lo resuelve la automatización:

~~~gherkin
  Cuando el desarrollador ejecuta la compilación de documentación
~~~

## Lo que pertenece a los hooks, no al Gherkin

Un escenario no es el sitio para el arranque del entorno. El setup de bajo nivel —levantar Selenium WebDriver y su navegador, preparar el workspace de la CI, instalar dependencias, crear el directorio de salida, limpiar el estado al final— vive en la capa de automatización, en los hooks de cada escenario o de cada bloque.

- **No va en Gherkin:** arrancar el navegador, configurar esperas, crear el directorio de compilación, preparar usuarios o tokens de prueba, cerrar sesión al terminar.
- **Sí va en Gherkin:** el estado inicial que el lector necesita para entender el comportamiento y que forma parte del dominio.

Al revisar, un paso de arranque de entorno es un hallazgo de regla 1 con reescritura propuesta: el paso desaparece del escenario y se declara que ese detalle corresponde a la capa de automatización. Elegir un subconjunto de escenarios por etiqueta es configuración de la ejecución de CI, no un paso del escenario: un `Dado que la CI ejecuta solo las etiquetas @rapida` traslada una decisión de la tubería al texto de especificación.

Esta skill no escribe el hook ni nombra el comando del runner. Para decidir si un paso es automatizable y dónde vive su preparación, carga en el paso 7 la referencia del stack declarado. En `../assets/example-feature-bad.feature`, `Publish the site` reúne las dos cosas: el muro de texto y el arranque del entorno narrado como pasos.

## Empezar en mitad de la acción

Un escenario puede comenzar con un `Dado` situacional, sin volver al principio del flujo. Es la técnica que hace divisible un muro de texto: el segundo comportamiento arranca en el estado que dejó el primero.

~~~gherkin
Scenario: Publicar un documento ya compilado
  Dado que la documentación compilada contiene el documento modificado
  Cuando se publica el sitio de documentación
  Entonces el sitio publicado muestra el documento modificado
~~~

El `Dado` situacional describe un estado observable del sistema, no una acción pasada: `Dado que el desarrollador compiló el documento modificado` sigue contando la acción y confunde el orden.

## Comprobaciones del paso 4

Ordena las comprobaciones así, porque cada una usa la evidencia de la anterior:

1. Descarta lo que no es especificación: un `Dado` con una propuesta de negocio (`business-intent-given`) es una historia de usuario metida en el escenario.
2. Mide la longitud efectiva de cada escenario, con los pasos de `Background` incluidos.
3. Marca los pasos que comunican el cómo y decide si el escenario está bajo de nivel o cubre dos comportamientos.
4. Verifica el orden estricto y el tipo de cada paso.
5. Comprueba que el escenario tiene al menos un `Entonces`; sin afirmación no hay criterio de aceptación.

En [four-rules.md](four-rules.md) están los códigos correspondientes. El punto de vista y la forma de la frase se revisan en [language-and-voice.md](language-and-voice.md).

Fuente: nota de la bóveda + práctica estándar de Cucumber.
