# Modelo del contrato

Forma y semántica de `design-system.json` (`design-system.v1`). El contrato describe el sistema; no es un formato de pantalla ni un volcado de Figma. Los tokens siguen un subconjunto declarado de DTCG 2025.10; el resto del documento es un esquema propio.

## Contrato documentado o contrato máquina-legible

Un documento del proyecto (`DESIGN.md`, un ADR, una guía con los tokens y las reglas) es un contrato de pleno derecho y se lee como fuente documentada. `design-system.json` es **opcional**: solo se crea si habilita algo que el documento no da. Antes de escribirlo, declara qué habilita:

| Lo que habilita | ¿Justifica el JSON? |
|---|---|
| Aprobaciones con alcance comprobable por ruta | Sí |
| Consumidores que leen tokens con tipos y alias | Sí |
| Generación determinista del catálogo y su manifiesto | Sí |
| Puerta de acoplamiento y de cambios contra un baseline | Sí |
| Repetir en otro formato lo que el documento ya dice | No |

Si no habilita nada de la columna «Sí», no se crea. Un documento con 50 tokens y una prueba de sincronía para tapar lo que `check` no ve es peor que el documento solo.

## Dos capas que no se confunden

| Capa | Qué es | Quién manda |
|---|---|---|
| Contrato del sistema | Identidad, gobernanza, componentes, patrones, temas y decisiones | `design-system.json` o un documento del proyecto (`DESIGN.md`, un ADR) |
| Tokens | Valores y alias con `$value`/`$type` | El contrato (`tokens`) o una fuente DTCG (`tokenSources`) |

El contrato puede incluir tokens embebidos o declarar fuentes externas. No se mantienen dos copias: un token definido en ambos sitios es un error de duplicidad.

## Campos superiores

| Campo | Obligatorio | Tipo | Función |
|---|---|---|---|
| `schema` | Sí | string | Debe ser `design-system.v1` |
| `name` | Sí | string | Identificador del sistema |
| `version` | Sí | SemVer | Versión del contrato, no de la skill |
| `status` | No | `bootstrap` \| `refine` \| `locked` | Madurez del contrato |
| `identity` | Sí | objeto | Propósito y principios; `principles` es una lista no vacía |
| `tokens` | Uno de los dos | objeto DTCG | Tokens embebidos |
| `tokenSources` | Uno de los dos | lista de rutas | Archivos DTCG externos, relativos al contrato |
| `themes` | No | objeto | Modo por defecto y overrides por modo |
| `components` | No | objeto | Contratos de componentes |
| `patterns` | No | objeto | Composiciones reutilizables |
| `accessibility` | No | objeto | Reglas declaradas; no sustituye la medición |
| `constraints` | No | objeto | Listas `always` y `never` |
| `decisions` | No | lista | Decisiones con `id`, `decision` y `rationale` |
| `governance` | Sí | objeto | `mode`, `protected`, `configurable`, `exceptions` |
| `catalog` | No | string u objeto | Catálogo generado o externo: `path`, `mode`, `entry`, `sources`, `fingerprint` |
| `implementation` | No | objeto | CSS real del producto: `styles`, que se usa para comprobar acoplamiento |
| `adapters` | No | lista | Informes de conformidad de componentes |
| `sources` | No | lista | Evidencia del descubrimiento |
| `omitted` | No | lista | Secciones ausentes a propósito |
| `provenance` | No | objeto | Origen y revisión del contrato |

Una clave superior desconocida produce un aviso, no un fallo: el contrato puede crecer. Un campo obligatorio ausente o con el tipo incorrecto produce un fallo.

## Tokens

### Subconjunto DTCG implementado

| Regla DTCG 2025.10 | Estado |
|---|---|
| Archivo JSON; grupos y tokens | Implementado |
| `$value` obligatorio; token = objeto con `$value` | Implementado |
| `$type` por token o heredado del grupo; un alias sin tipo hereda el tipo resuelto | Implementado |
| Nombres sin `.`, `{`, `}` ni `$` inicial | Implementado, con alfabeto restringido a `[A-Za-z0-9_-]` y `$root` |
| Alias con `{ruta}` | Implementado |
| Detección de ciclos | Implementado |
| Profundidad de alias ≤ 10 | Implementado |
| Anidamiento de grupos ≤ 20 | Implementado |
| `$root` | Implementado |
| `$deprecated` | Implementado en tokens y grupos; se hereda a los hijos |
| `$description`, `$extensions` | Aceptados y preservados |
| Tipos `color`, `dimension`, `fontFamily`, `fontWeight`, `duration`, `cubicBezier`, `number`, `string` | Validación implementada |
| Tipos compuestos `shadow`, `border`, `typography`, `gradient`, `transition`, `strokeStyle` | Aceptados; sin validación profunda |
| `$extends` | **No implementado**; el validador falla si aparece |
| `$ref` / JSON Pointer | **No implementado**; usa `{ruta}` |
| Todas las reglas de resolución y tipos de la especificación | **No implementado** |

No se afirma conformidad DTCG completa. El contrato acepta además una cadena CSS como valor de color para facilitar la autoría; es una extensión, no la forma estricta del tipo `color` de DTCG.

### Forma de un token

```json
{
  "color": {
    "$type": "color",
    "brand": {
      "$description": "Acento de la acción principal.",
      "$value": {
        "colorSpace": "srgb",
        "components": [0.06, 0.46, 0.43],
        "hex": "#0f766e"
      }
    }
  }
}
```

Formas aceptadas por tipo:

- `color`: objeto DTCG con `colorSpace` y `components` de 3 o 4 números, o con `hex`; también una cadena CSS no vacía.
- `dimension`: objeto `{ "value": 16, "unit": "px" }` o cadena con unidad (`px`, `rem`, `em`, `%`, `vw`, `vh`, `vmin`, `vmax`, `ch`, `ex`, `mm`, `cm`, `in`, `pt`, `pc`).
- `duration`: objeto `{ "value": 250, "unit": "ms" }` o cadena con `ms`/`s`.
- `fontFamily`: cadena o lista de cadenas.
- `fontWeight`: número entre 1 y 1000, o `normal`, `bold`, `bolder`, `lighter`, `100`…`900`.
- `number`: número.
- `cubicBezier`: lista de cuatro números.
- `string`: cadena.
- Compuestos: objeto, lista o cadena; el validador no comprueba su estructura interna.

### Referencias y resolución

- Una referencia es `{ruta.del.token}`. La ruta es relativa al mapa de tokens, no al documento completo.
- Una cadena puede contener varias referencias (`1px solid {color.border}`), pero solo una referencia exacta forma una cadena de alias.
- El tipo declarado de un alias debe coincidir con el tipo resuelto del token final.
- Un token obsoleto (`$deprecated`) no puede ser referenciado por otro token ni por un componente.
- Una referencia a un grupo no es válida: debe apuntar a un token.

### Temas

```json
{
  "themes": {
    "default": "light",
    "modes": {
      "light": {},
      "dark": {
        "color.surface": "#0a0f1c",
        "color.text": "{color.neutral.50}"
      }
    }
  }
}
```

Cada override apunta a un token existente y puede ser un valor o una referencia. El catálogo genera `:root` con el modo por defecto y un selector `[data-theme="<modo>"]` para los demás.

## Componentes

```json
{
  "components": {
    "button": {
      "description": "Acción principal.",
      "when": ["La acción principal de una vista."],
      "when_not": ["Navegación."],
      "variants": {
        "primary": {
          "backgroundColor": "{color.brand}",
          "textColor": "{color.on-brand}",
          "rounded": "{radius.control}",
          "padding": "10px 16px",
          "typography": "{typography.label}"
        }
      },
      "states": ["default", "hover", "focus", "disabled"],
      "example": "<button type=\"button\">Guardar</button>"
    }
  }
}
```

- `variants` es un mapa de variante a bolsa de propiedades. Si hay variantes, el componente debe declarar `when` o `when_not`.
- Las propiedades son las del contrato de componentes del proyecto; las más habituales son `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`, `size`, `height`, `width`, `borderColor`, `borderWidth`, `shadow`, `gap` y `opacity`.
- Cada valor puede ser un literal o una referencia. Cuando el contrato distingue niveles, se prefieren tokens semánticos o de componente; los primitivos solo se usan con una excepción declarada. El validador comprueba existencia y tipo, no la intención del nivel.
- `states` nombra los estados que el componente debe cubrir. Nombrarlos no demuestra que existan visualmente.
- `example` es HTML de ejemplo. Cuando el catálogo lo muestra, se escapa en el código y se aísla con `sandbox` si va en un `iframe`; ese aislamiento es una opción, no un requisito. Las clases que use el ejemplo deben existir en el CSS de la implementación declarada: `implementation-fidelity` lo comprueba.
- Si el componente existe en código, declara el módulo o el adaptador que lo comprueba. El contrato no inventa una implementación.

## Patrones, restricciones y decisiones

- `patterns` describe composiciones reutilizables: cuándo se usan, qué permiten y qué prohíben. No es un árbol de página completo.
- `constraints.always` y `constraints.never` son leyes breves y comprobables. Una regla con «intenta» o «cuando sea apropiado» no cambia el comportamiento de un agente.
- `decisions` conserva el porqué de las decisiones durables. Git es el historial; el contrato guarda la decisión vigente, no la cola de propuestas.

## Gobernanza

`governance.mode` elige el régimen: `solo` (por defecto) o `approvals`.

- **`solo`:** la revisión es el commit y la confirmación de la persona. No hay archivo de aprobaciones y no se exige ninguno. El agente sigue sin poder aprobarse a sí mismo: si cambia una ruta protegida, el `gate` devuelve `UNKNOWN` porque no puede comprobar la confirmación; esa evidencia la aporta la persona.
- **`approvals`:** un cambio en una ruta protegida exige una aprobación externa con alcance, como se describe en [governance](governance.md).

`governance.protected` es opt-in: declara solo lo que de verdad no debe cambiar sin revisión. `governance.configurable` enumera lo que se puede adaptar. `governance.exceptions` declara desviaciones autorizadas con su motivo y su responsable; una excepción no convierte un fallo de conformidad en un `PASS`.

El flujo, el alcance de las aprobaciones y sus límites están en [governance](governance.md).

## Catálogo y adaptadores

El catálogo tiene dos modos. El contrato lo declara con `catalog.mode`:

```json
{
  "catalog": {
    "mode": "external",
    "path": "docs/design-system",
    "entry": "index.html",
    "sources": ["web/src/styles/tokens.css", "web/src/styles/components.css"]
  }
}
```

| Modo | Quién lo mantiene | Qué comprueba `check` |
|---|---|---|
| `generated` | `catalog` lo escribe desde el contrato | Manifiesto y huellas de entradas y artefactos |
| `external` | Una persona, a mano, consumiendo el CSS del producto | Existencia de la entrada y de `sources`, huella opcional y acoplamiento |

Reglas del catálogo externo:

- Declara `path`, `entry` (por defecto `index.html`) y `sources`: los archivos de implementación que importa. No se le genera un `tokens.css` paralelo; `catalog` se niega a generarlo.
- La entrada debe importar al menos una de sus `sources`. Un catálogo que no importa la implementación no es fiel aunque se parezca.
- Prohibido que defina sus propias clases de componente. El validador toma como señal la capa `ds-*` y la devuelve como `FAIL`; una capa con otro prefijo exige revisión humana. Las clases que usa el catálogo deben existir en el CSS del producto.
- `fingerprint` es opcional: un mapa `ruta → sha256` para fijar los archivos que el catálogo consume. `check` compara las huellas y falla si no coinciden.
- Las muestras del contrato que usan clases inexistentes en la implementación también son `FAIL`.

Sin `implementation.styles` (ni `catalog.sources` en modo externo), la fidelidad no se puede medir: `implementation-fidelity` devuelve `UNKNOWN`, no `PASS`.

`adapters` declara informes de conformidad de componentes. El contrato no ejecuta frameworks: lee el informe que produce el adaptador. El formato está en [validation](validation.md).

## Evidencia y límites del contrato

- La prueba de acoplamiento del catálogo manda sobre `check`: demuestra que el catálogo consume la implementación; `check` solo demuestra que el contrato es coherente consigo mismo.
- `tokenSources` queda fuera de `protected-changes`: el `gate` compara el contrato, no las fuentes DTCG en disco. Si los tokens deben protegerse, embébelos en `tokens` o extiende la puerta. No asumas que la protección los cubre.

## Evidencia del descubrimiento

`sources` documenta de dónde sale cada afirmación:

```json
{
  "sources": [
    { "path": "styles.css", "kind": "observed", "note": "12 variables CSS" },
    { "path": "DESIGN.md", "kind": "documented", "note": "principios y paleta" },
    { "path": "components/", "kind": "observed", "note": "inventario de archivos" },
    { "path": "motion", "kind": "unknown", "note": "no se encontró evidencia" }
  ]
}
```

Tipos permitidos: `observed`, `documented`, `inferred`, `unknown`. Una inferencia no se convierte en decisión sin confirmación. Un `unknown` no se rellena con un valor inventado.

## Contrato mínimo

El archivo [design-system.template.json](../assets/design-system.template.json) es un contrato válido que pasa `check`. Úsalo como punto de partida solo cuando no exista un sistema que conservar. Si existe, el contrato se escribe a partir de la evidencia observada y documentada, sin sobrescribir la fuente original.
