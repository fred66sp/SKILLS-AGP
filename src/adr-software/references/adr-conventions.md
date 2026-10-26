# Convenciones del ADR

Aplica al localizar o crear el directorio de ADR, nombrar archivos, fijar estados, mantener el índice y decidir qué se puede editar. Léelo en los pasos 1, 2 y 7 del contrato.

## Directorio

Si el repositorio ya tiene un directorio de ADR, se conserva. Si no lo tiene, elige entre:

- `docs/decisions/` — convención MADR, recomendada cuando el proyecto ya usa `docs/`.
- `adr/` — alternativa simple para repositorios pequeños o sin estructura documental.

Orden de detección que usa `scripts/adr.py`: `docs/decisions/`, `adr/`, `docs/adr/`, `docs/adrs/`, `decisions/`. Si ninguno existe, la convención nueva se decide con el responsable y no se crea un directorio que contradiga la estructura existente.

## Nombres

Patrón con numeración: `NNNN-titulo-con-guiones.md`.

- `NNNN` es un número secuencial con relleno de ceros. El ancho lo fija el primer ADR del directorio; sin referencias previas, cuatro dígitos.
- El título va en minúsculas, con guiones y una frase verbal en presente: `0001-adoptar-postgresql-16.md`.
- Si el repositorio ya usa solo nombres con guiones, se conserva esa convención: `adoptar-postgresql-16.md`.
- Los números son locales al directorio o a la categoría. Dos categorías pueden repetir el mismo número.

## Secciones mínimas

Todo ADR contiene, como mínimo:

1. **Contexto y problema** — por qué la decisión existe ahora, qué la dispara y qué restricciones aplican.
2. **Decisión** — qué se elige, con alcance, límites y no-goals.
3. **Consecuencias** — qué se vuelve más fácil y más difícil, qué riesgos aparecen y qué tareas quedan.

Un ADR con contrato de agente añade además: restricciones medibles, no-goals explícitos, tareas de seguimiento y, cuando exista, un criterio de confirmación que se pueda convertir en prueba o comprobación.

## Estados

El estado vive en el frontmatter YAML:

```yaml
---
status: proposed
date: 2025-06-15
decision-makers: Ana, Luis
---
```

| Estado | Significado |
|---|---|
| `proposed` | En discusión; todavía no decidido. |
| `accepted` | Vigente y debe seguirse. |
| `rejected` | Considerado y descartado de forma explícita. |
| `deprecated` | Ya no aplica; se explica qué lo sustituye o por qué caducó. |
| `superseded by [ADR-0002](0002-titulo.md)` | Reemplazado por otro ADR; se enlazan ambos sentidos. |

`adr.py status` solo escribe los estados simples. Para `superseded` exige `--superseded-by` y escribe el enlace relativo; el ADR sustituto debe enlazar de vuelta al anterior en `Más información`.

## Frontmatter

| Campo | Obligatorio | Contenido |
|---|---|---|
| `status` | Sí | Estado vigente. |
| `date` | Sí | Fecha del último cambio de estado, `YYYY-MM-DD`. |
| `decision-makers` | Sí | Personas que poseen la decisión. |
| `consulted` | No | Expertos consultados, comunicación bidireccional. |
| `informed` | No | Interesados informados, comunicación unidireccional. |
| `technical-story` | No | Enlace a issue, PR o ticket que originó la decisión. |

Los campos opcionales se omiten cuando no existen; no se rellenan con marcadores.

## Mutabilidad

- Añadir información con fecha es preferible a reescribir lo existente.
- Un cambio de decisión se publica como ADR nuevo que sustituye al anterior. No se edita la decisión aceptada para que parezca la nueva.
- Cambiar el estado, corregir una errata y añadir una nota posterior son ediciones en sitio válidas.
- El cuerpo de un ADR aceptado conserva su historia. Si una consecuencia resultó falsa, se añade la observación fechada; no se borra la original.

## Categorías

Cuando el directorio acumula ADR de materias distintas, se admiten subdirectorios:

```text
docs/decisions/
  backend/
    0001-adoptar-postgresql-16.md
  frontend/
    0001-adoptar-react.md
  infrastructure/
    0001-adoptar-terraform.md
```

La numeración es local a cada categoría. El esquema se elige pronto y se documenta en el índice; si el repositorio ya tiene uno, se respeta.

## Índice

El índice vive en `README.md` o `index.md` dentro del directorio de ADR y enlaza cada registro sin copiar su contenido. `adr.py new --update-index` inserta la entrada bajo el encabezado `## ADR` y no duplica una entrada cuyo enlace ya existe. `adr.py check` verifica que todas las entradas resuelven y que todo ADR tiene entrada.
