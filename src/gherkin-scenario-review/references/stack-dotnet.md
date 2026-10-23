# Stack .NET (Reqnroll)

Referencia del runner para el paso 7. Sirve para juzgar si un paso es definible y si su detalle pertenece a hooks, no para escribir automatización.

Léelo en el paso 7 del procedimiento de `SKILL.md`, después de `stack-detection.md` y solo cuando el stack detectado es .NET con Reqnroll. Con SpecFlow en el `*.csproj`, lee también la última sección: los conceptos de esta referencia aplican, los comandos no.

## Runner, idioma y ubicación de los `.feature`

- Runner: Reqnroll, sobre el runner de pruebas del proyecto (`Reqnroll.NUnit`, `Reqnroll.MsTest` o `Reqnroll.xUnit`). Se ejecuta con `dotnet test`.
- Idioma: cada archivo declara el suyo en la cabecera. La documentación de Reqnroll lo escribe `#language: de-DE` y Gherkin lo define como `# language: es`; las dos variantes llevan un nombre de cultura de `CultureInfo`, así que una concreta como `es-ES` es más precisa que el neutro `es` para la conversión de parámetros. El idioma por defecto del proyecto se fija en `reqnroll.json` con `language.feature`. Ten en cuenta la diferencia de grafía al leer el encabezado del `.feature` que estás revisando.
- Ubicación: los `.feature` viven dentro del proyecto de test (el anidamiento habitual muestra `MyFeature.feature` junto a su `MyFeature.feature.cs` generado). La convención que documenta Reqnroll para localizarlos en el editor es el glob `**/*.feature` del proyecto, clave `cucumber.features`.

## Cómo se casa un paso con su definición

Un método público de una clase marcada con `[Binding]`, anotado con `[Given]`, `[When]`, `[Then]` o `[StepDefinition]`. La expresión es una Cucumber Expression (`"el validador encuentra {int} hallazgos"`) o una expresión regular; Reqnroll decide cuál es cuál por heurística (`^`/`$` y `{string}`/`\d+` entre los indicios). Un mismo método puede llevar varias anotaciones para cubrir redacciones distintas. Bindings, hooks y transformaciones de argumentos son globales para todo el proyecto.

Para la revisión, dos lecturas. Como los enlaces son globales, un paso genérico («Cuando se ejecuta la herramienta») es difícil de implementar sin ambigüedad: la propia documentación de Reqnroll recomienda redactar el paso para que el contexto se entienda solo, que es la regla 4. Y como una Cucumber Expression es texto literal con parámetros, un paso que no se entiende suelto tampoco se puede anclar.

## Dónde viven los hooks

En la misma clase de bindings, con `[BeforeTestRun]`, `[BeforeFeature]`, `[BeforeScenario]` (alias `[Before]`), `[BeforeScenarioBlock]`, `[BeforeStep]` y sus `After…`. Admiten filtro por etiqueta (`[BeforeScenario("@requiresUsers")]`) y se acotan con `[Scope]`.

`[BeforeScenario]` y `[BeforeStep]` son el destino natural del arranque del servidor de docs, del workspace temporal o del estado del CLI antes de medir códigos de salida. Un paso de bajo nivel del paso 4 tiene dónde irse sin tocar Gherkin.

## Filtrado por etiquetas

Las etiquetas generan categorías del framework de test, así que el filtro es del runner: `dotnet test --filter TestCategory=done`, combinando con `&` y `|` (`dotnet test --filter "TestCategory=us123&TestCategory=done"`). Las etiquetas de `Rule` se heredan a sus escenarios.

## Formatos de informe

Los formatters integrados de Reqnroll v3.0 o superior se activan en `reqnroll.json` dentro de `formatters`: `html` (documento vivo, con `outputFilePath`) y `message` (Cucumber Messages en `.ndjson`). No hay formatter JUnit documentado por Reqnroll: el XML de resultados lo produce el adaptador del framework de test del proyecto, no Reqnroll.

## Comando de parseo verificado

```bash
dotnet test -e "REQNROLL_DRY_RUN=true" MyReqnrollProject.csproj
```

Dry run documentado en `docs/execution/dry-run.md`: la ejecución omite el código de los handlers de paso y sirve para comprobar que todos los pasos declarados en los `.feature` enlazan con un handler C#, combinable con los formatters para recoger nombres de feature, escenarios y enlaces de pasos. La propia documentación advierte de que exportar la variable en la sesión no basta; usa `-e` del CLI de .NET o un archivo `.runsettings` con `REQNROLL_DRY_RUN`.

## Tres hechos relevantes para la revisión

1. `Background` y `Rule:` soportados, incluido `Background` a nivel de `Rule`. Las etiquetas de una `Rule` se heredan a sus escenarios, así que filtrar por categoría una regla arrastra a todo su bloque: una agrupación mal hecha cambia qué se ejecuta.
2. Pasos con tabla y con `Scenario Outline`: la tabla del paso se recibe como `Table` (alias `DataTable`). Con MsTest, las filas de `Examples` se generan como `[DataRow]` dentro de un único método test, y con `generator.allowRowTests` en `false` se vuelve a un método por fila. El coste de las filas redundantes de la regla 3 es real y visible en el explorador de tests.
3. Los pasos sin enlace se reportan como resultado inconcluso por defecto (error en los frameworks sin soporte de inconcluso) y la salida del test incluye el esqueleto del método de enlace que falta. El comportamiento se configura con `runtime.missingOrPendingStepsOutcome` y `runtime.stopAtFirstError`. Con el dry run delante, «estos pasos son definibles» deja de ser una suposición del revisor.
4. La heurística de expresión puede cambiar el significado del texto: una expresión con `/` se interpreta como alternancia de Cucumber Expression salvo que los marcadores `^`/`$` la declaren regex. Para la revisión importa en un caso concreto: un paso con barras o llaves puede parecer definible al leerlo y no serlo con la expresión que el proyecto escribiría, así que conviene apoyarse en el dry run y no en la intuición.

## Antes de citar un comando

Comprueba en el proyecto dónde está el `reqnroll.json` (las opciones de `language.feature`, `formatters` y `runtime` viven ahí) y qué framework de test acompaña a Reqnroll: `Reqnroll.NUnit`, `Reqnroll.MsTest` o `Reqnroll.xUnit`. El comando de dry run lleva la ruta del `.csproj`, así que sin esas dos piezas localizadas no hay forma de escribirlo correcto para ese repositorio.

## Con SpecFlow en el proyecto

SpecFlow es el antecesor: Reqnroll es un fork de enero de 2024 sobre el código de SpecFlow v4, y el repositorio original de SpecFlow se quitó de GitHub en diciembre de 2024. La diferencia práctica es de nombres: paquetes `SpecFlow.*` en lugar de `Reqnroll.*` y espacio de nombres `TechTalk.SpecFlow` en lugar de `Reqnroll`; los atributos de pasos y hooks son los mismos. Las banderas de esta referencia (`REQNROLL_DRY_RUN`, `formatters` en `reqnroll.json`) no aplican a SpecFlow: no las cites para ese proyecto y declara el parseo como no verificado por el runner.

## Fuentes

- reqnroll/reqnroll — `docs/automation/step-definitions.md`, `docs/automation/hooks.md`, `docs/automation/scoped-bindings.md`, `docs/automation/cucumber-expressions.md`, `docs/execution/dry-run.md`, `docs/execution/executing-specific-scenarios.md`, `docs/execution/test-results.md`, `docs/gherkin/feature-language.md`, `docs/gherkin/gherkin-reference.md`, `docs/installation/configuration.md`, `docs/installation/setup-ide.md`, `docs/installation/formatter-configuration.md`, `docs/reporting/reqnroll-formatters.md`, `docs/guides/migrating-from-specflow.md`, `docs/help/faq.md`.
