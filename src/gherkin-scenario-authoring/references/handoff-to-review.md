# Traspaso a la revisión

Léelo en el paso 5 del procedimiento, al cerrar la entrega. Este fichero fija qué se entrega, qué se deja de declarar y cómo se lee el exit 0 del comprobador compartido.

## Qué se entrega

Cuatro bloques, en este orden y sin adornos:

1. **Rutas escritas.** Cada `.feature` con su número de escenarios, contando los `Esquema del escenario` por su bloque y no por sus filas. Si el archivo ya existía, di qué escenarios añadiste y cuáles preservaste.
2. **El mapa de descubrimiento**, con las reglas, los ejemplos y las preguntas abiertas que siguen sin responder. Las preguntas se entregan listadas, tal cual están; no se cierran por suposición y no se desaparecen de la entrega porque incomoden. Si alguna bloquea el comportamiento, no hay archivo que entregar: se entrega el mapa con esa pregunta y se dice por qué se paró la redacción.
3. **El comando del paso 4 con su salida literal y su exit code.** La invocación desde la raíz del repositorio:

   ~~~bash
   python tools/check-feature.py --path features/compilacion-de-documentacion.feature
   ~~~

   Salida esperada en limpio: `<ruta>: sin hallazgos` y el resumen `0 hallazgos (0 deterministas, 0 candidatos)`, con exit 0. Con hallazgos, exit 3 y una línea por hallazgo con su código, su posición `archivo:linea` y su mensaje. Si el exit es 2, es error de uso o idioma no soportado: corrige la invocación o el encabezado `# language:`, no el escenario.
4. **Qué queda fuera del alcance de esta entrega**: la calificación del artefacto y la automatización.

## Qué NO se declara

El veredicto `APTO`, `APTO CON RESERVAS` o `NO APTO` lo emite `gherkin-scenario-review`. Quien escribe no se lo atribuye: ni «el archivo es apto», ni «cumple las cuatro reglas», ni «queda listo para producción».

El exit 0 acredita tres cosas y solo tres: **estructura**, **orden** y **longitud**. No acredita legibilidad real, independencia del comportamiento, que el ejemplo ilustrado sea el que el dominio necesita, ni que el escenario sea automatizable. Los cinco códigos candidatos los resuelves tú por criterio, y ese criterio es justamente lo que la revisión confirma o refuta.

Frase honesta para la entrega: «el comprobador sale 0; la calificación la decide la revisión».

## Cómo se lee la salida

Cada hallazgo ocupa una línea, ordenada por la posición en el archivo, con seis partes:

- La marca: `[D]` si es determinista, `[C]` si es candidato.
- El número de regla que mide, o `-` cuando es de estructura y no de las cuatro reglas.
- El código (`step-order`, `redundant-examples`, …).
- La posición `archivo:linea`.
- La evidencia entre comillas, truncada a 64 caracteres.
- El mensaje, que propone la corrección.

Al final sale siempre un resumen con el recuento: hallazgos totales, deterministas y candidatos. Ese resumen es lo que se copia en la entrega; reescribirlo a mano es donde se cuela un cero que no existía. Si necesitas volcar los hallazgos al informe, usa `--json`: emite un array con los campos del hallazgo menos el número de regla, y añade el campo `file` con la ruta en formato `/`.

## Forma del mensaje de entrega

~~~text
Escrito: features/compilacion-de-documentacion.feature — 3 escenarios (1 esquema con 2 filas).
Mapa: features/behavior-map-compilacion-documentacion.md — 3 reglas, 5 ejemplos,
      1 pregunta abierta sin responder: ¿la tubería de CI corta las etapas siguientes
        tras el código 1? — no bloquea: configuración de la tubería, no el `Entonces`
Comprobación: python tools/check-feature.py --path features/compilacion-de-documentacion.feature
  → sin hallazgos · 0 hallazgos (0 deterministas, 0 candidatos) · exit 0
Fuera de alcance: veredicto de calidad (gherkin-scenario-review) y step definitions.
~~~

Corto significa: rutas, recuentos, preguntas abiertas, salida del comprobador y el fuera de alcance. Nada de resumen de cada escenario, nada de relato de las cuatro reglas, nada de autoaval.

## Antes de cerrar la entrega

1. Comprueba que cada escenario del archivo corresponde a una regla del mapa. Un escenario sin regla detrás es invención de quien escribe.
2. Vuelve a leer las preguntas abiertas: siguen abiertas en la entrega, y ninguna se convirtió en un paso del escenario.
3. Si el archivo ya existía, verifica que solo cambiaron los escenarios del comportamiento nuevo y di cuáles se preservaron.
4. Ejecuta el comprobador una última vez después del último retoque. Un exit 0 de hace tres ediciones no es el exit 0 de la entrega.

## Tres fallos típicos de traspaso

1. **Entregar sin exit 0.** El comprobador da 3 y la entrega describe el archivo como terminado. Sin exit 0 se entrega el fallo con sus líneas y se dice qué queda pendiente, no el artefacto. Y si `tools/check-feature.py` no existe en la máquina, se informa la ruta que falta y se para: no se simula la comprobación ni se escribe un parseo propio.
2. **Cerrar preguntas abiertas por suposición.** La pregunta bloqueante se resuelve «lo más probable» y el escenario sale con un comportamiento inventado. La pregunta se entrega abierta; si cambia el `Entonces`, el escenario no se escribe.
3. **Atribuirse el veredicto de la revisora.** Escribir «APTO» o «cumple las cuatro reglas» en el mensaje de entrega. Eso usurpa el papel: la autoría produce y comprueba lo mecánico; la revisión califica. Dos iteraciones sin progreso en el paso 4, por cierto, tampoco se disfrazan de entrega: son señal de que el comportamiento está mal descubierto y hay que volver al paso 2.
