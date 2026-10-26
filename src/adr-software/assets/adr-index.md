# Architecture Decision Records (ADR)

Un Architecture Decision Record (ADR) recoge una decisión de arquitectura relevante con su contexto y sus consecuencias. Este índice enlaza los registros del directorio; no repite sus decisiones.

## Convenciones

- Directorio: `{ADR_DIR}`
- Nombres: `NNNN-titulo-con-guiones.md` al empezar de cero; si el repositorio ya usa solo guiones, `titulo-con-guiones.md`.
- Estados: `proposed`, `accepted`, `rejected`, `deprecated`, `superseded`.

## Flujo

- Un ADR nuevo se crea como `proposed`.
- Se discute y se itera.
- Cuando se decide, pasa a `accepted` o `rejected`.
- Si más adelante se reemplaza, se crea otro ADR y el anterior pasa a `superseded` con enlace en ambos sentidos.

## ADR
