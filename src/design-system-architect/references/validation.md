# Verificación del sistema

La puerta distingue lo que demuestra de lo que solo declara. Esta referencia explica cada comprobación, sus límites y cómo se lee el resultado.

## Resultados

| Resultado | Significado | Cuándo se usa |
|---|---|---|
| `PASS` | La comprobación se ejecutó y no encontró incumplimientos | Estructura válida, referencias resueltas, catálogo sincronizado, cambio protegido aprobado |
| `FAIL` | Hay un incumplimiento demostrado | Token mal formado, referencia rota, ciclo, cambio protegido sin aprobación, artefacto desincronizado, adaptador que falla |
| `UNKNOWN` | La comprobación no se ejecutó o la evidencia es insuficiente | Falta baseline, catálogo, informe de adaptador o medición visual |

El resultado global es `FAIL` si alguna comprobación falla; si no, `UNKNOWN` si alguna no pudo ejecutarse; solo es `PASS` si todas las ejecutadas pasaron. Un `UNKNOWN` nunca se redondea a `PASS`.

## Comandos y códigos

```bash
python3 scripts/design_system.py check <contrato> [--catalog <dir>] [--json]
python3 scripts/design_system.py gate <contrato> --baseline <anterior> [--approvals <archivo>] [--json]
python3 scripts/design_system.py catalog <contrato> --out <dir> [--json]
python3 scripts/design_system.py discover <raíz> [--json]
```

| Código | Significado |
|---|---|
| `0` | `PASS` |
| `1` | `FAIL` |
| `2` | `UNKNOWN` |
| `3` | Error de uso o de entrada/salida |

`check` comprueba la integridad del contrato y, si el contrato declara `catalog` o `adapters`, su consistencia. `gate` añade la comparación contra un baseline y la comprobación de aprobaciones. `catalog` genera los artefactos. `discover` solo lee.

## Matriz de comprobaciones

| ID | Qué comprueba | `FAIL` cuando | `UNKNOWN` cuando |
|---|---|---|---|
| `contract-structure` | Campos obligatorios, esquema, versión SemVer, identidad, gobernanza, tipos de los campos opcionales | Falta un campo, el tipo es incorrecto o el esquema no es `design-system.v1` | — |
| `token-syntax` | `$value`, `$type`, nombres, tipos y valores | Token sin valor, tipo indeterminable, tipo no reconocido, valor inválido, `$extends`/`$ref` no soportados, anidamiento > 20 | — |
| `token-references` | Existencia de referencias, tokens obsoletos, ciclos, profundidad ≤ 10, coincidencia de tipos y overrides de tema | Referencia rota, ciclo, profundidad excesiva, tipo incompatible, referencia a obsoleto | — |
| `component-contract` | Variantes con `when`/`when_not`, referencias de las bolsas de propiedades, tipo de la referencia, tipos de `states` y `example` | Variante sin regla de uso, referencia rota o tipo incompatible | — |
| `protected-changes` | Cambios en rutas protegidas contra el baseline y su aprobación | Cambio, adición o eliminación sin aprobación que lo cubra | Sin `--baseline`, baseline ilegible, aprobación incompleta o archivo de aprobaciones ilegible |
| `catalog-consistency` | Huellas de las entradas y de los artefactos del catálogo | Entrada o artefacto distinto, artefacto ausente, manifiesto inválido | Catálogo declarado pero no generado, manifiesto ausente o ilegible |
| `component-conformance` | Informes de adaptadores declarados | Un componente con `FAIL` | Informe ausente, ilegible, con esquema distinto o componente sin resultado |

## Qué demuestra cada comprobación

- **Estructura:** que el documento tiene la forma declarada. No demuestra que describa el producto.
- **Tokens:** que los valores y las referencias son coherentes dentro del contrato. No demuestra que el producto los use ni que sean los correctos.
- **Componentes:** que las variantes declaran reglas y referencian tokens existentes. No demuestra que el componente implementado se vea así.
- **Cambios protegidos:** que el contrato actual no cambió una ruta protegida sin una aprobación que la cubra. No autentica la aprobación ni prueba que la persona la emitiera.
- **Catálogo:** que el catálogo se generó con las entradas actuales y que sus artefactos no se editaron. No demuestra que el catálogo sea visualmente correcto.
- **Adaptadores:** que un informe externo declara conformidad o fallo de los componentes. No ejecuta el framework ni sustituye la inspección visual.

## Catálogo y manifiesto

`catalog` escribe en el directorio de salida:

| Archivo | Contenido |
|---|---|
| `index.html` | Catálogo: identidad, accesibilidad, temas, tokens, componentes, patrones, restricciones, decisiones, gobernanza y evidencia |
| `tokens.css` | Variables CSS derivadas de los tokens, con los overrides de tema |
| `catalog.css` | Presentación del catálogo |
| `catalog.json` | Manifiesto de sincronía |

El manifiesto registra:

```json
{
  "schema": "design-system.catalog.v1",
  "inputs": [
    { "kind": "contract", "path": "design-system.json", "sha256": "…" },
    { "kind": "token-source", "path": "tokens/colors.tokens.json", "sha256": "…" },
    { "kind": "skill-template", "path": "skill:assets/catalog.html", "sha256": "…" },
    { "kind": "skill-template", "path": "skill:assets/catalog.css", "sha256": "…" }
  ],
  "artifacts": [
    { "path": "index.html", "sha256": "…", "bytes": 10224 },
    { "path": "tokens.css", "sha256": "…", "bytes": 1112 },
    { "path": "catalog.css", "sha256": "…", "bytes": 5942 }
  ]
}
```

`check` calcula las huellas actuales del contrato, de cada fuente DTCG y de las plantillas de la skill que generan el catálogo, y las compara con `inputs`. Si difieren, el catálogo está desincronizado. Después compara cada artefacto con su huella: una edición manual también lo invalida. El manifiesto no guarda fechas ni rutas absolutas de la máquina; la reproducibilidad depende del contenido. Detecta una desincronización accidental, no una falsificación coordinada del manifiesto y los artefactos: para eso, Git y la revisión son el control.

Todo texto procedente del contrato se escapa. Los `example` se muestran en un `<iframe sandbox>` y también como código escapado; no se ejecutan scripts del contrato.

## Adaptadores de componentes

Un adaptador es un informe, no un comando que el validador ejecute. El contrato declara:

```json
{
  "adapters": [
    { "name": "web", "report": "reports/web-components.json" }
  ]
}
```

El informe usa este formato:

```json
{
  "schema": "design-system.adapter.v1",
  "components": [
    { "name": "button", "status": "PASS", "evidence": "captura y typecheck del componente" },
    { "name": "data-table", "status": "UNKNOWN", "evidence": "sin render en el entorno" }
  ]
}
```

Reglas:

- El informe se lee desde la ruta declarada, relativa al contrato.
- Cada componente del contrato debe tener una entrada. Si falta, el resultado es `UNKNOWN`.
- Un `PASS` sin `evidence` no se acepta: queda en `UNKNOWN`.
- Un `FAIL` en cualquier componente hace que la comprobación sea `FAIL`, con o sin evidencia.
- Un `UNKNOWN` sin ningún `FAIL` deja la comprobación en `UNKNOWN`.
- El validador no ejecuta el comando que produjo el informe. La autenticidad y la calidad de esa evidencia pertenecen al adaptador y a la revisión.

## Visual y accesibilidad

La puerta no abre un navegador ni mide contraste real, foco, teclado, reflow o tamaño de objetivo. Esas comprobaciones se declaran `UNKNOWN` hasta que exista evidencia inspeccionada:

- abrir el resultado renderizado en los tamaños y temas del proyecto;
- comprobar foco visible, orden de tabulación y operabilidad por teclado;
- medir contraste sobre los colores finales, no solo sobre la paleta teórica;
- comprobar texto al 200%, reflow a 320 CSS px y `prefers-reduced-motion`;
- registrar la captura o la ubicación de la inspección.

Un `PASS` estructural no es un `PASS` visual ni un `PASS` de accesibilidad. Presentarlos como equivalentes es una afirmación falsa.

## Descubrimiento

`discover` es una operación de solo lectura. Inventaría:

- contratos o documentos de diseño;
- archivos DTCG y variables CSS;
- archivos de componentes y configuración de interfaz;
- dependencias de interfaz en `package.json`;
- evidencia de `prefers-reduced-motion`.

Cada hecho se clasifica como `observed`, `documented`, `inferred` o `unknown`. Una inferencia no es una decisión: se confirma antes de escribirla en el contrato. Un `unknown` no se rellena con un valor inventado. La prueba de aceptación comprueba que el proyecto no se modifica y que el inventario separa observación de inferencia.

## Uso como puerta

Para un cambio protegido:

```bash
python3 scripts/design_system.py gate design-system.json \
  --baseline .design-system.baseline.json \
  --approvals approvals.json
```

El baseline es el contrato antes del cambio. La aprobación es externa; el agente no la crea. Si el comando devuelve `0`, el cambio está cubierto; si devuelve `1`, hay una ruta sin cubrir o un incumplimiento; si devuelve `2`, falta evidencia y no se puede cerrar.

Un `gate` verde no demuestra que el cambio sea visualmente correcto. Solo demuestra que el contrato no cambió una decisión protegida sin una aprobación que la cubra y que las comprobaciones estructurales ejecutadas pasaron.
