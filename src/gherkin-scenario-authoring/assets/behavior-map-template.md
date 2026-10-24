# Plantilla del mapa de descubrimiento

Rellena este mapa en el paso 2 del `SKILL.md`, antes de redactar cualquier escenario.
Duplica el bloque `Regla R<n>` tantas veces como reglas de negocio encuentres y sustituye
cada `<hueco>`. Práctica completa en [references/behavior-discovery.md](../references/behavior-discovery.md).

Regla de parada: mientras quede una pregunta con `¿bloquea la escritura? sí`, el mapa no
está listo y no se escribe ni un `Escenario`. Esas preguntas se entregan listadas y sin
resolver; nunca se cierran por suposición.

## Historia

- Encargo literal: <frase del encargo, copiada, no resumida>
- Fuente: <historia de producto | defecto real | prosa de comportamiento | conversación de three amigos>
- Participantes: <quien escribe> · <quien prueba> · <quien construye>

## Regla R1 — <título corto de la regla>

- Regla: <qué hace el sistema, en una frase y sin nombrar pantallas ni comandos>
- Por qué importa: <consecuencia de no cumplirla>
- Ejemplos concretos:
  - E1 — <datos reales del dominio> → <resultado observable>
  - E2 — <otros datos, otra frontera> → <resultado observable>
- Preguntas que levantan estos ejemplos:
  - P1 — <pregunta> → ¿bloquea la escritura? sí | no — motivo: <por qué cambia o no el `Entonces`> — responde: <persona>
  - P2 — <pregunta> → ¿bloquea la escritura? sí | no — motivo: <...> — responde: <persona>

## Regla R2 — <título corto de la regla>

- Regla: <...>
- Por qué importa: <...>
- Ejemplos concretos:
  - E3 — <dato real> → <resultado observable>
- Preguntas que levantan estos ejemplos:
  - P3 — <pregunta> → ¿bloquea la escritura? sí | no — motivo: <...> — responde: <persona>

## Preguntas abiertas

Copia aquí todas las preguntas del mapa, una por fila. `¿bloquea la escritura?` admite dos
respuestas: `sí` cuando la respuesta cambia el texto del escenario (el `Entonces`, los datos
o el estado inicial); `no` cuando las dos respuestas dejan el escenario igual.

| #  | Pregunta             | ¿bloquea la escritura? sí / no | Motivo                 | Responde    |
|----|----------------------|--------------------------------|------------------------|-------------|
| <#>| <pregunta literal>   | sí / no                        | <qué cambia en el escenario> | <persona>   |

## Reducción por clases de equivalencia

Agrupa los ejemplos por lo que afirman, no por lo que contienen. Dos ejemplos que comprueban
el mismo `Entonces` con otros datos son la misma clase, y sobra uno.

- Clases: <clase A> | <clase B> | <frontera: vacío, justo en el límite, por encima, no aplicable>
- Ejemplos que se quedaron en la misma clase: <E2 y E3> — afirman <el mismo resultado> y solo cambian <los datos>
- Se conserva: <E2> — ilustra mejor <la frontera de la clase>
- Ejemplos sin clase: <E5> → no encaja en ninguna regla: se escribe como <regla nueva> o viaja <fuera de alcance>

## División

- Reglas que se quedan en este archivo: <R1, R2>
- Reglas que viajan a otra entrega: <R3> — motivo: <depende de una decisión fuera de este encargo>
- Escenarios previstos tras la reducción: <n> (uno por comportamiento)

## Estado del mapa

El estado es la última línea del mapa rellenado, y solo admite estos dos valores:

Estado: **MAPA LISTO | MAPA INCOMPLETO**

- `MAPA LISTO`: cada regla tiene al menos un ejemplo concreto con datos del dominio, ninguna
  pregunta lleva `¿bloquea la escritura? sí` sin responder, y la división está escrita. Se
  puede pasar al paso 3 y copiar la forma de `assets/feature-template.feature`.
- `MAPA INCOMPLETO`: falta un ejemplo en alguna regla, queda una pregunta bloqueante sin
  respuesta, o dos reglas se contradicen. No se redacta ningún escenario: se reportan las
  preguntas tal cual están y, si hay contradicción, las dos reglas con su línea del encargo.
- Preguntas bloqueantes abiertas (obligatorio con `MAPA INCOMPLETO`): <P1 — motivo — a quién se pregunta>

## Ejemplo corto rellenado

Muestra la diferencia entre las tres piezas: la regla afirma el comportamiento, el ejemplo
pone los datos, la pregunta marca lo que el grupo todavía no sabe.

~~~text
R1 — Un enlace relativo roto corta el build de documentación; si no, se publican guías que llevan a ninguna parte.
  E1  guias/instalacion.md enlaza a api/config.md, que no existe → error con la ruta origen y la destino, código de salida 1
  E2  El mismo documento con dos enlaces rotos → un error por enlace, código de salida 1 otra vez
  P1  ¿El enlace roto da código 1 o código 2?          ¿bloquea la escritura? sí  (el `Entonces` se escribe distinto)
  P2  ¿Los dos enlaces salen en una línea del informe? ¿bloquea la escritura? no  (solo cambia el estilo del informe)
Estado: MAPA INCOMPLETO — pregunta bloqueante abierta: P1, se pregunta a la autora del validador.
~~~

## Cómo se rellena

1. Escribe la regla del negocio antes que el escenario: sin regla no hay título que valga.
2. Busca un ejemplo con datos reales por regla. Si no lo encuentras, la laguna no es de redacción: anótala como pregunta.
3. Marca cada pregunta con `¿bloquea la escritura?` y su motivo; no decidas tú la respuesta.
4. Reduce los ejemplos a una clase de equivalencia cada uno antes de pensar en la tabla `Ejemplos`.
5. Cierra con la línea de `Estado`. Si sale `MAPA INCOMPLETO`, entrega el mapa y las preguntas, no el `.feature`.
