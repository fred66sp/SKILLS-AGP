---
status: {STATUS}
date: {DATE}
decision-makers: "{DECIDERS}"
---

# {TITLE}

## Contexto y problema

Las decisiones de arquitectura de este repositorio se tomaban en conversaciones, tickets y cambios de código sin un registro que explicara el motivo. Eso obliga a reconstruir el contexto, permite que dos partes apliquen criterios distintos y dificulta saber si una decisión sigue vigente.

## Decisión

Registrar cada decisión de arquitectura relevante como un ADR en `{ADR_DIR}`, en el idioma y el formato del equipo. Un ADR se crea como `proposed`, se acepta o se rechaza de forma explícita y, cuando se reemplaza, se publica otro que lo sustituye con enlace en ambos sentidos.

No-goals: no se registran decisiones triviales, reversibles y locales; no se duplica en el ADR el contenido de tickets o documentos ya existentes; no se convierten los ADR en un historial de cambios de implementación.

## Consecuencias

- Good, porque el motivo y las alternativas de cada decisión quedan disponibles para quien llega después.
- Good, porque una decisión sustituida se identifica por enlace y no por memoria.
- Bad, porque escribir y mantener un ADR consume tiempo que debe reservarse al crearlo.
- Neutral, porque el índice añade un mantenimiento pequeño que evita buscar a ciegas.

## Más información

Las convenciones del directorio y el índice viven en el `README.md` del propio directorio. La puerta de revisión se ejecuta antes de aceptar un ADR nuevo.
