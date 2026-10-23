# Stack Go (godog)

Referencia del runner para el paso 7. Sirve para juzgar si un paso es definible y si su detalle pertenece a hooks, no para escribir automatización.

Léelo en el paso 7 del procedimiento de `SKILL.md`, después de `stack-detection.md` y solo cuando el stack detectado es Go con godog.

## Runner, idioma y ubicación de los `.feature`

- Runner: godog, la implementación oficial de Cucumber para Go. No se lanza con un binario propio: se ejecuta dentro de `go test`.
- Idioma: godog parsea con el dialecto Gherkin fijado en `Options.Dialect`, por defecto `en`. El encabezado `# language:` es el mecanismo estándar de Gherkin, pero el control de godog está en el `Options` del proyecto: si no lo toca, el parseo espera inglés, y un `.feature` en español no es ejecutable tal cual. Eso es un hallazgo de automatizabilidad, no de estilo.
- Ubicación: `Options.Paths` por defecto es `["features"]`. Admite directorio, archivo y escenario por línea (`features/build.feature:10`). Las definiciones de pasos viven en un `*_test.go` del paquete probado, junto a `go.mod`.

## Cómo se casa un paso con su definición

Se registra una expresión regular y una función sobre el `ScenarioContext`: `ctx.Step(...)`, `ctx.Given(...)`, `ctx.When(...)`, `ctx.Then(...)`. `Step` casa con cualquier palabra clave; `Given`/`When`/`Then` solo con la suya, y `And`/`But` heredan la palabra clave del paso anterior a efectos de coincidencia.

Dos consecuencias para la revisión. La coincidencia es por texto del paso, así que dos redacciones equivalentes en archivos distintos son dos definiciones: es el riesgo de reutilización que informa `SKILL.md`. Y las expresiones se anclan con `^` y `$` en los ejemplos de la documentación, de modo que un paso que no se entiende sin su escenario tampoco da una expresión legible. Si dos definiciones casan con el mismo paso se aplica la primera registrada; con `--strict` la duplicidad se reporta como ambigüedad.

## Dónde viven los hooks

En el `ScenarioInitializer`: `ctx.Before(...)` y `ctx.After(...)` por escenario, y `ctx.StepContext().Before(...)` / `ctx.StepContext().After(...)` por paso. Para estado de toda la suite, `TestSuiteInitializer`.

`Before` recibe el escenario y devuelve el contexto sustituido: es el sitio natural para crear el workspace temporal, levantar el servidor HTTP de prueba o limpiar el directorio de salida del build de documentación. Un paso de bajo nivel detectado en el paso 4 tiene aquí dónde mudarse, y en godog esos hooks reciben el `context.Context`, así que el detalle mecánico cabe sin tocar la especificación.

## Filtrado por etiquetas

`Options.Tags`, expuesto como `-t` / `--godog.tags` cuando el proyecto enlaza las banderas con el prefijo `godog.`. Sintaxis documentada: `@wip`, `~@wip`, `@wip && ~@new`, `@wip,@undone`; admite `&&`, `,` y `~`. No es la sintaxis de las expresiones de etiquetas de Cucumber: no cites `and`/`not` para este stack.

## Formatos de informe

`Options.Format`, expuesto como `-f` / `--godog.format`, con la forma `name:file` para volcar a un archivo. Integrados: `progress`, `cucumber`, `events`, `junit`, `pretty` (por defecto `pretty`). Con concurrencia `>= 2` solo se soporta salida tipo `progress`. Con `junit` el proyecto tiene XML para el pipeline; con `events` o `cucumber` tiene la traza estructurada que sirve como evidencia de una ejecución.

## Comando de parseo verificado

Sin comando de parseo verificado: comprueba la bandera con la ayuda del runner antes de ejecutarla.

Lo documentado en el README es `go test` con banderas prefijadas, y eso ejecuta:

```bash
go test -v --godog.tags=wip
go test -test.v -test.run ^TestFeatures$
```

`-d` / `--godog.definitions` imprime las definiciones de paso encontradas y termina; no comprueba los `.feature`. Existe una API de parseo sin ejecución (`TestSuite.RetrieveFeatures()`), pero es código del proyecto, no un comando que un revisor pueda lanzar. Por eso, en este stack la automatizabilidad queda como no verificada salvo que el proyecto ejecute la suite y quede el informe delante, con `--strict` para que los pasos `undefined` hagan fallar la ejecución.

## Tres hechos relevantes para la revisión

1. El modelo parseado expone `FindBackground`, `FindRule` y `FindExample` sobre el documento Gherkin: `Background`, `Rule:` y las filas de `Examples` son unidades reales en godog, no decoración del texto.
2. Los pasos admiten `*godog.Table` y `*godog.DocString` como parámetros. Un paso con tabla es definible; la revisión decide si la tabla representa una clase de equivalencia o relleno.
3. Cada escenario ejecutable llega al runner como un `Pickle`, y el resumen cuenta en unidades de escenario (`N scenarios (M undefined)`), así que las filas redundantes de `Examples` que señala la regla 3 tienen coste medible aquí. Los pasos sin definición se listan como `undefined` y el resumen añade el snippet para implementarlos.

## Fuentes

- cucumber/godog — `README.md`, `_autodocs/configuration.md`, `_autodocs/errors.md`, `_autodocs/types.md`, `_autodocs/api-reference/scenario-context.md`, `_autodocs/api-reference/step-context.md`, `_autodocs/api-reference/test-suite.md`, `_autodocs/api-reference/options-and-flags.md`, `internal/formatters/fmt_base.go`.
- cucumber/docs — `content/docs/gherkin/reference.md` (encabezado `# language:`).
