# Descubrir el comportamiento antes de redactar

Léelo en el paso 2 del procedimiento. Úsalo cuando el encargo traiga una historia de usuario, prosa de comportamiento, un defecto real o la transcripción de una discusión de equipo, y todavía no haya ejemplos cerrados. Si el encargo ya aporta ejemplos acordados y sin lagunas, puedes ir directo al paso 3.

Ningún escenario se redacta mientras quede una pregunta abierta que pueda cambiar el comportamiento (invariante 1 del `SKILL.md`). Este fichero es la práctica que hace esa comprobación posible: primero el mapa, después el Gherkin.

## Las tres piezas del descubrimiento

Trabaja con tres tipos de tarjeta y en este orden:

- **Regla de negocio.** Di qué hace el sistema y por qué importa, en una frase y sin nombrar pantallas ni comandos. «Por qué importa» es la parte que suele faltar: si no la escribes, no sabes si la regla es del dominio o un detalle de implementación.
- **Ejemplo concreto.** Un caso con datos reales del dominio del proyecto: rutas de documento, códigos de salida, nombres de etapa de la tubería de CI, severidades de hallazgo. Un ejemplo sin datos no es ejemplo, es la regla repetida.
- **Pregunta abierta.** Lo que el grupo no sabe, lo que depende de otra persona o lo que admite dos resultados distintos. Se escribe como pregunta, con quién la responde.

Una regla necesita al menos un ejemplo. Sin ejemplo, la regla es una frase bonita que nadie puede verificar, y el escenario que redactes a partir de ella saldrá vago. Si no encuentras un ejemplo con datos del dominio, la laguna no es de redacción: falta información, y eso va a la lista de preguntas.

## Qué preguntas bloquean y cuáles no

Una pregunta **bloquea** el paso 3 cuando su respuesta cambia el texto del escenario: el resultado afirmado, los datos del ejemplo o el estado inicial. Para decidirlo, escribe los dos candidatos de respuesta y mira qué pasa con el `Entonces`:

- «¿El enlace roto da código 1 o código 2?» → bloquea: el `Entonces` se escribe distinto según la respuesta.
- «¿La compilación en paralelo ordena el informe por archivo o por hora?» → bloquea si el escenario afirma el orden; no bloquea si el escenario solo afirma que el informe señala el enlace roto.

Una pregunta **no bloquea** cuando las dos respuestas dejan el escenario igual y cambian solo la implementación, la automatización o una decisión de proyecto. Déjala escrita en el mapa, con su dueño, y sigue: no la cierres por suposición ni la conviertas en un paso del escenario.

Regla práctica: si puedes redactar el escenario sin saber la respuesta, no bloquea. Si necesitas saber la respuesta para escribir el `Entonces`, bloquea.

## Reducir por clases de equivalencia antes de redactar

Cuando una regla ya tiene varios ejemplos, agrúpalos por lo que verifican, no por lo que contienen:

1. Escribe en una línea qué afirma el `Entonces` de cada ejemplo.
2. Junta los ejemplos que afirman lo mismo aunque cambien los datos: son la misma clase de equivalencia.
3. Deja un ejemplo por clase, el que mejor ilumina la frontera (vacío, justo en el límite, por encima del límite, no aplicable).
4. Los ejemplos que no caben en ninguna clase son otra regla: escríbelos como regla nueva y vuelve a preguntar por su ejemplo.

Esta reducción se hace aquí, con tarjetas, no en el paso 3 con la tabla `Ejemplos` delante. Reducir tarde es la causa más común de un esquema con siete filas que afirmaban lo mismo.

## El mapa: campos y criterio de listo

Rellena [../assets/behavior-map-template.md](../assets/behavior-map-template.md). El mapa tiene que dejar estas siete cosas escritas:

| Campo | Qué guarda |
|---|---|
| Historia | La frase literal del encargo, su fuente y quién participa. |
| Reglas | Un bloque por regla, con el «qué hace» y el «por qué importa» separados. |
| Ejemplos | Al menos uno por regla, con datos del dominio y su resultado observable. |
| Preguntas | Cada pregunta con su marca `¿bloquea la escritura?`, el motivo y quién la responde. |
| Reducción | Las clases de equivalencia y qué ejemplo se conserva en cada una. |
| División | Qué reglas se quedan en este archivo y qué reglas viajan. |
| Estado | La última línea: `MAPA LISTO` o `MAPA INCOMPLETO`. |

El mapa está **listo** para el paso 3 cuando cada regla tiene al menos un ejemplo concreto, ninguna pregunta marcada como bloqueante queda sin responder, y el resultado de división está escrito. Está **incompleto** en cuanto falte un ejemplo en alguna regla, quede una pregunta bloqueante abierta, o dos reglas se contradigan: en ese último caso detén la entrega y reporta las dos con la línea del encargo.

## De la tarjeta al escenario

El mapa no se convierte en Gherkin por traducción literal; se convierte por correspondencia:

- Cada regla da el título de un escenario y su `Cuando` con su `Entonces`.
- Los ejemplos de la regla dan los datos del escenario o, si son clases distintas, las filas de `Ejemplos`.
- Las preguntas bloqueantes se resuelven con el grupo antes de redactar. Si siguen abiertas, el escenario no se escribe: el mapa se entrega con la pregunta.
- Las preguntas no bloqueantes van listadas en la entrega, pero no entran en el archivo. Convertirlas en un paso es meter una decisión de implementación en la especificación.

Si una regla no produce un ciclo acción-verificación completo, vuelve a la tarjeta: falta el ejemplo, no falta un paso.

## Ejemplo de mapa completo

~~~text
Historia: Como mantenedor de la documentación quiero que la compilación señale los
enlaces rotos para no publicar guías que llevan a ninguna parte.

R1  Un enlace relativo a una ruta inexistente hace fallar la compilación.
    E1  guias/instalacion.md enlaza a api/configuracion.md (no existe)
        -> salida: error con la ruta fuente y la ruta destino; código de salida 1.
    E2  Los dos enlaces rotos del mismo documento -> un error por enlace, mismo código.
R2  Un enlace externo no comprueba la red durante la compilación.
    E3  https://ejemplo.invalid/... -> el informe marca el enlace como sin verificar;
        código de salida 0 si no hay errores locales.
P1  ¿El enlace roto devuelve código 1 o 2?            respondida en la sesión: código 1 (autora del validador)
P2  ¿Los dos enlaces salen en una línea del informe?  no bloquea (solo cambia el estilo del informe)
P3  ¿La tubería de CI interrumpe las etapas siguientes? no bloquea (configuración de la tubería)

Clases de equivalencia: ruta local inexistente | ruta local válida | enlace externo.
División: R1 se queda en este archivo; R2 viaja a otra entrega porque depende de una
decisión de red fuera de este encargo.
Estado: MAPA LISTO
~~~

Si P1 siguiera abierta, el estado sería `MAPA INCOMPLETO`: la pregunta cambia el `Entonces`, así que no se redacta ningún escenario y la entrega se queda en el mapa con la pregunta listada.

## Ritmo y resultado de la sesión

Trabaja en voz alta con el grupo cuando esté disponible (three amigos: quien escribe, quien prueba y quien construye) y solo cuando no. Fija un tiempo acotado por historia, de media hora; si el mapa no cierra en ese tiempo, casi siempre es señal de que la historia es demasiado grande, y eso es un resultado válido: la división que propongas vale más que la sesión larga. Escribe las preguntas en verde para separarlas de las reglas, y no borres ninguna aunque ya esté respondida: la respuesta va al ejemplo que la sustituye.

Fuente: práctica estándar de Example Mapping y three amigos; la bóveda del repositorio no documenta la facilitación de estas sesiones.
