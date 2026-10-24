# Las cuatro reglas al escribir

Léelo en el paso 3 del procedimiento. Aquí las cuatro reglas están convertidas en decisiones de redacción: qué escribes en el borrador y qué corriges tú antes de lanzar el comprobador. No es una auditoría —eso lo hace `gherkin-scenario-review` sobre el archivo cerrado— y tampoco repite su teoría: si necesitas el criterio de revisión con detalle, lee sus fichas, pero solo cuando revises, no como lectura previa para escribir.

Los once códigos que cierran el paso 4 están en la tabla del final; ahí se marca cuáles se evitan al escribir y cuáles se resuelven contra el archivo ya redactado. La forma del archivo entero —`# language:`, `Característica:`, historia de usuario, `Antecedentes`, dos `Escenario` y un `Esquema del escenario`— está en [../assets/feature-template.feature](../assets/feature-template.feature); cópiala y sustituye el contenido, no la estructura.

## Regla 1 — legible sin contexto

**Qué escribes.** Un escenario que se entiende leyendo solo su título y sus pasos: orden `Dado → Cuando → Entonces`, vocabulario del dominio, y los pasos necesarios para afirmar el resultado, sin pasar de un dígito. Los pasos de `Antecedentes` cuentan en la longitud.

**Qué corriges en el borrador.** Un `Dado` que declara la propuesta de valor en vez del estado inicial; los verbos de consola y de interfaz (clic, botón, tecleo, espera, scroll, URL del servicio); un `Entonces` que nadie sabe cómo se afirma.

~~~gherkin
# MAL — intención de negocio como estado, y un Entonces que no se puede verificar
Escenario: Documentación
  Dado que quiero una documentación sin enlaces rotos
  Cuando se compila la documentación
  Entonces sale bien

# BIEN — estado inicial, acción, verificación observable
Escenario: Fallar la compilación por un enlace relativo roto
  Dado que el documento de guía enlaza a una ruta inexistente
  Cuando el desarrollador ejecuta la compilación de documentación
  Entonces la compilación termina con un código de salida distinto de cero
~~~

La propuesta de valor va en la documentación bajo `Característica:`, como historia de usuario, no dentro de un escenario.

## Regla 2 — un escenario, un comportamiento

**Qué escribes.** Un ciclo acción-verificación por escenario: un solo `Cuando` con su `Entonces`. El título anuncia todo lo que el cuerpo comprueba.

**Qué corriges en el borrador.** El segundo `Cuando` que aparece con su propio `Entonces`; el cambio de actor o de objeto a mitad del escenario; el título que menciona una sola de las dos mitades. Divide y escribe cada parte con su propio `Dado`.

~~~gherkin
# MAL — compilar y publicar, dos comportamientos en un escenario
Escenario: Compilación incremental de la documentación
  Dado que la compilación anterior terminó sin errores
  Cuando se modifica un documento y se compila de nuevo
  Entonces solo se recompila el documento modificado
  Cuando se publica el sitio de documentación
  Entonces el sitio publicado contiene el documento modificado

# BIEN — dos escenarios, y el segundo arranca en el estado que dejó el primero
Escenario: No recompilar los documentos sin cambios
  Dado que la compilación anterior terminó sin errores
  Cuando se modifica un documento y se compila de nuevo
  Entonces solo se recompila el documento modificado

Escenario: Publicar un documento ya compilado
  Dado que la documentación compilada contiene el documento modificado
  Cuando se publica el sitio de documentación
  Entonces el sitio publicado muestra el documento modificado
~~~

## Regla 3 — un ejemplo por clase de equivalencia

**Qué escribes.** Un escenario por comportamiento con los datos que lo ilustran, y `Esquema del escenario` solo cuando las filas de `Ejemplos` son clases de equivalencia distintas: cada fila cambia lo que el `Entonces` afirma. La reducción de clases ya la hiciste en el paso 2; aquí la transcribes.

**Qué corriges en el borrador.** Las filas que solo cambian un nombre, una ruta o un número de línea; la columna que ningún `<marcador>` consume; el `<marcador>` sin columna; el esquema que se usa para no pensar el comportamiento.

~~~gherkin
# MAL — la misma clase repetida siete veces: cambia el dato, no lo que se verifica
  Esquema del escenario: Marcar un documento como pendiente de revisión
    Cuando el validador revisa el documento <ruta>
    Entonces el informe marca el documento como pendiente de revisión
    Ejemplos:
      | ruta                   |
      | guias/instalacion.md   |
      | guias/configuracion.md |
      | api/cli.md             |
      | api/extensiones.md     |
      | guias/vocabulario.md   |
      | api/pruebas.md         |
      | guias/flujos.md        |

# BIEN — dos filas, dos clases, porque cambia la afirmación
  Ejemplos:
    | severidad | resultado |
    | error     | fallo     |
    | aviso     | paso      |
~~~

**Por qué dos filas de la misma clase están mal.** No son cobertura: son dos pruebas que ejecutan el mismo camino y afirman lo mismo. Cuestan tiempo de tubería, ensucian el informe y, cuando fallan, no dicen qué cambió. Si necesitas varios datos de la misma clase, el sitio está debajo del Gherkin: en la automatización o en los datos de prueba.

## Regla 4 — tercera persona y frase completa

**Qué escribes.** Pasos en tercera persona, con sujeto y predicado, que se entienden leídos sueltos, fuera de su escenario. Un solo punto de vista por archivo.

**Qué corriges en el borrador.** El `yo` conviviendo con `el desarrollador` o `el servicio de CI`; los fragmentos sin verbo; los pasos que dependen del contexto de la línea anterior para saber qué verifican.

~~~gherkin
# MAL
  Entonces la ruta del enlace roto
  Cuando ejecuto la compilación desde mi portátil

# BIEN
  Y el informe de la compilación señala la ruta del enlace roto
  Cuando el desarrollador ejecuta la compilación de documentación
~~~

## Forma de un paso que se entiende suelto

Escribe cada paso como `actor + verbo + objeto + resultado`: quién hace la cosa, qué hace, sobre qué, y qué se observa. Un paso de menos de tres palabras casi nunca la tiene; un paso que empieza por `se` sin actor legible tampoco. Si al leerlo aislado hace falta abrir el escenario para saber de qué documento o qué etapa se habla, reescríbelo con el nombre completo del objeto.

## `Dado` situacional: la palanca de la división

Al partir un escenario, el segundo no vuelve al principio del flujo: se sitúa con un `Dado` que describe el estado observable que dejó el primero.

- Estado, correcto: `Dado que la documentación compilada contiene el documento modificado`.
- Acción pasada, incorrecto: `Dado que el desarrollador compiló el documento modificado`. Sigue contando la acción, deja el escenario sin `Cuando` propio y confunde el orden.

Puente entre escenarios: el estado que nombras tiene que ser observable y alcanzable desde el escenario anterior; si no, la división es prematura y hay otra regla que descubrir.

## `Y` encadenado o palabra clave nueva

`Y` encadena pasos del mismo tipo dentro del mismo grupo: varios `Dado` de estado, varios `Entonces` de la misma verificación. Un cambio de tipo abre palabra clave nueva: `Cuando` para la acción, `Entonces` para la afirmación. Dos señales de que usas `Y` donde toca otra palabra: un `Y` que introduce una acción después de los estados (`Y el desarrollador lanza la compilación` → `Cuando`), y un `Y` bajo `Cuando` que esconde un segundo `Cuando` con su `Entonces`, que es la regla 2 avisando.

`Pero` sirve para una excepción del mismo grupo; no lo uses para llevar la narrativa al paso siguiente.

## Los once códigos y en qué momento se cierran

`--max-steps 9` y `--max-outline-rows 5` son los umbrales por defecto del comprobador.

| Código | Tipo | Dónde se cierra | Cómo |
|---|---|---|---|
| `step-order` | determinista | al escribir | ningún `Dado` después del primer `Cuando` o `Entonces` |
| `missing-then` | determinista | al escribir | cada escenario con al menos un `Entonces` |
| `multiple-action-outcome` | determinista | al escribir | un `Cuando` y su `Entonces`; si hay dos, divide (regla 2) |
| `too-many-steps` | determinista | al escribir | un dígito contando `Antecedentes`; súbelo de nivel o divide |
| `unparseable-block` | determinista | paso 4 | encabezado `Característica:`, título en cada escenario, paso o tabla sueltos |
| `outline-missing-placeholder` | determinista | paso 4 | cada `<marcador>` con su columna y cada columna consumida |
| `low-level-vocab` | candidato | paso 4 | revisa si el término es lenguaje del dominio o de la interfaz |
| `person-mixed` | candidato | paso 4 | reescribe los pasos a tercera persona |
| `no-subject-verb` | candidato | paso 4 | reescribe el paso como frase completa |
| `redundant-examples` | candidato | paso 4 | confirma si las filas son clases distintas; si no, deja una |
| `business-intent-given` | candidato | paso 4 | mueve la intención a la historia bajo `Característica:` |

Los cuatro primeros no deberían aparecer nunca: se evitan con la decisión de redacción, no con la corrección. Los dos deterministas que quedan para el paso 4 son mecánica del archivo: se corrigen mirando la línea que señala el comprobador. Los cinco candidatos los marca el script, pero el juicio es tuyo: en el paso 4 los resuelves antes de entregar, porque la invariante 8 y el paso 3 los exigen aunque el exit 0 no los exija.
