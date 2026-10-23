# Stack JavaScript / TypeScript (cucumber-js)

Referencia del runner para el paso 7. Sirve para juzgar si un paso es definible y si su detalle pertenece a hooks, no para escribir automatización.

Léelo en el paso 7 del procedimiento de `SKILL.md`, después de `stack-detection.md` y solo cuando el stack detectado es JavaScript / TypeScript con cucumber-js.

## Runner, idioma y ubicación de los `.feature`

- Runner: `cucumber-js` (paquete `@cucumber/cucumber`).
- Idioma: las palabras clave Gherkin del dialecto declarado. El archivo lo fija con el encabezado `# language:` en su primera línea; el proyecto puede cambiar el idioma por defecto con la opción `language` (`--language`, por defecto `en`). `cucumber-js --i18n-languages` lista los idiomas soportados y `cucumber-js --i18n-keywords es` las palabras clave de uno.
- Los `.feature` viven por defecto en `features/**/*.{feature,feature.md}`. El código de soporte se auto-detecta en `features/**/*.@(js|cjs|mjs)` cuando las features están en `features/`.
- Configuración: el primer archivo que encuentra entre `cucumber.json`, `cucumber.yaml`, `cucumber.yml`, `cucumber.js`, `cucumber.cjs`, `cucumber.mjs`.

## Cómo se casa un paso con su definición

Se importa `Given`, `When`, `Then` desde `@cucumber/cucumber` y se les pasa un `pattern`, que es una cadena con Cucumber Expressions o una expresión regular, más la función. La coincidencia es contra el texto del paso. `defineStep` figura como alias en desuso: si el proyecto lo emplea, la revisión sigue siendo válida, pero conviene comprobar qué versión de cucumber-js está instalada antes de citar ningún comando.

Consecuencia para la regla 4: la clave de búsqueda es el texto del paso. Un paso escrito como «la compilación» o «falla» no da material para una expresión que no sea ambigua, y obliga a definir `pattern`s sueltos que luego nadie puede reutilizar en otro escenario.

## Dónde viven los hooks

En los mismos archivos de soporte, con `Before`, `After`, `BeforeStep`, `AfterStep` y los de ámbito global `BeforeAll`/`AfterAll`, admitiendo una expresión de etiquetas (`BeforeStep({ tags: "@foo" }, fn)`). El `World` es un ámbito aislado por escenario: lo que se guarda en `this` en un paso se recupera en los siguientes y se descarta al terminar.

Aquí es donde se responde a la pregunta de `SKILL.md` sobre el detalle de bajo nivel. Levantar el servidor de documentación, limpiar el directorio de salida o tomar el estado inicial del workspace van en `Before`/`AfterStep`, no en Gherkin. En un escenario con «Cuando el validador termina y se escribe el informe en disco», el candidato a hook está identificable: el runner tiene dónde recibir ese trabajo sin tocar la especificación.

Un límite que conviene conocer al proponer la reescritura: cucumber-js no tiene hooks a nivel de `Feature`. Su FAQ explica que el run se organiza en escenarios independientes, y recomienda bajar el setup al nivel de escenario o apuntarlo con etiquetas. Un paso que solo se explica por algo que ocurrió en otro escenario no tiene dónde resolverse en este stack.

## Filtrado por etiquetas

`cucumber-js --tags "@smoke or @wip"`. La opción es repetible y las expresiones se combinan con `and`. Equivalente en configuración: `{ tags: "@interesting" }`.

## Formatos de informe

`--format` acepta los formatter integrados: `progress-bar`, `pretty`, `html` (página independiente), `json` (formato legado, en mantenimiento), `message` (newline-delimited JSON), `usage` y `snippets`. Sin segundo valor, el formatter escribe en stdout; con él, escribe en la ruta indicada: `--format "html":"cucumber-report.html"`.

## Comando de parseo verificado

```bash
cucumber-js --dry-run
```

`--dry-run` (`-d`, también `{ dryRun: true }` en configuración) prepara la ejecución sin correrla: no se ejecuta ningún hook, los pasos se reportan como `skipped` y los pasos `undefined` y `ambiguous` se reportan sin provocar un fallo del proceso. Es justo la evidencia que necesita el informe: dice si cada paso tiene definición, sin ejecutar nada. Equivalente con filtro de etiquetas:

```bash
cucumber-js --dry-run --tags "@ci"
```

Si el proyecto no tiene `@cucumber/cucumber` instalado, no lo ejecutes: declara el parseo como no verificado. La forma de invocar el binario (`npm run`, `npx`, yarn, pnpm) depende del `package.json` del proyecto, así que esta referencia no la fija.

## Tres hechos relevantes para la revisión

1. `Background` y `Rule:` forman parte del modelo. Los propios casos de integration test de cucumber-js fijan que los pasos de `Background` se ejecutan antes de cada escenario y después de los hooks `Before`, y la API de reportes expone `getGherkinExampleRuleMap` mientras el formatter `pretty` tiene la opción `includeRuleLine`. Si el archivo revisado usa esas estructuras, son reales para el runner y se pueden citar como tal.
2. Los pasos admiten data table y docstring como argumentos adicionales, en el orden en que aparecen en el paso. El objeto de tabla expone `hashes()`, `rows()`, `raw()`, `rowsHash()` y `transpose()`. Un paso con tabla es definible; en la revisión, la tabla del paso exige que el paso diga qué hace con ella.
3. Los pasos sin definición se anuncian como `undefined` y cucumber-js genera el snippet con la expresión y sus argumentos. Eso hace demostrable la automatizabilidad: `--dry-run` responde con la firma que faltaría, así que un paso es definible o el runner dice cuál no lo es.

## Fuentes

- cucumber/cucumber-js — `docs/configuration.md`, `docs/dry_run.md`, `docs/filtering.md`, `docs/formatters.md`, `docs/snippets.md`, `docs/faq.md`, `docs/support_files/hooks.md`, `docs/support_files/world.md`, `docs/support_files/api_reference.md`, `docs/support_files/step_definitions.md`, `docs/support_files/data_table_interface.md`, `features/background.feature`.
- cucumber/docs — `content/docs/gherkin/reference.md` (encabezado `# language:`).
