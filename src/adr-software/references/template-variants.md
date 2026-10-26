# Variantes de plantilla

Aplica al elegir entre las dos plantillas del paquete. Léelo en el paso 5 del contrato cuando la decisión no tenga una forma evidente.

El paquete incluye dos plantillas en `assets/`.

## Simple

Archivo: `assets/adr-simple.md`.

Úsala cuando:

- La decisión tenga una opción claramente ganadora y pocas alternativas.
- Baste con contexto, decisión y consecuencias.
- Las alternativas se puedan descartar en una frase cada una.
- La velocidad importe más que una comparación exhaustiva.

Secciones: Contexto y problema → Decisión → Consecuencias → Alternativas consideradas (opcional) → Más información (opcional).

## MADR

Archivo: `assets/adr-madr.md`.

Úsala cuando:

- Haya varias opciones reales y convenga documentar sus ventajas e inconvenientes.
- Los criterios de decisión deban quedar explícitos.
- La decisión vaya a revisarse y la comparación deba sobrevivir.
- Otras personas necesiten ver el razonamiento, no solo el resultado.

Secciones: Contexto y problema → Criterios de decisión (opcional) → Opciones consideradas → Resultado de la decisión → Consecuencias → Confirmación (opcional) → Ventajas e inconvenientes de las opciones (opcional) → Más información (opcional).

La plantilla sigue [MADR 4.0](https://adr.github.io/madr/).

## Qué comparten

- Frontmatter YAML con estado, fecha y responsables, y los campos opcionales de consultados e informados.
- Encuadre para agente: los marcadores piden concreción, medida y autonomía.
- Sección `Más información` para enlaces, seguimiento y condiciones de revisión.
- Tercera categoría `Neutral` junto a `Good` y `Bad`.

## Cómo elegir

| Señal | Simple | MADR |
|---|---|---|
| Opciones reales | 1–2 | 3 o más |
| Alcance afectado | Pequeño o individual | Varios equipos |
| Reversibilidad | Fácil | Difícil |
| Vida esperada | Meses | Años |
| Revisión de interesados | No | Sí |

En caso de duda, empieza por la simple. Se puede ampliar a MADR cuando la conversación revele más complejidad, sin cambiar la decisión ya redactada.
