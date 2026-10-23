# Stack Java / Kotlin (cucumber-jvm)

Referencia del runner para el paso 7. Sirve para juzgar si un paso es definible y si su detalle pertenece a hooks, no para escribir automatización.

Léelo en el paso 7 del procedimiento de `SKILL.md`, después de `stack-detection.md` y solo cuando el stack detectado es la JVM con cucumber-jvm.

## Runner, idioma y ubicación de los `.feature`

- Runner: cucumber-jvm (artefactos `io.cucumber`: `cucumber-java`, `cucumber-junit-platform-engine`).
- Idioma: cada `.feature` declara el suyo con el encabezado `# language:`; las anotaciones de pasos se importan del paquete localizado `io.cucumber.java.<ISO2>`, así que un archivo en español se atiende con anotaciones `io.cucumber.java.es.*`. La CLI lista idiomas y palabras clave con `--i18n-languages` y `--i18n-keywords LANG`.
- Ubicación: los `.feature` son recursos del classpath de test. La sintaxis de ruta admite `PATH/name.feature`, `classpath:com/example/features` y `name.feature:3:9` para escenarios por línea. Sin feature path declarado, Cucumber escanea la raíz del classpath y sus subdirectorios.
- Glue (paquete donde están pasos y hooks): `--glue`/`-g` en la CLI, `cucumber.glue` en propiedades.

## Cómo se casa un paso con su definición

Un método anotado con `@Given`, `@When` o `@Then` cuya cadena es una Cucumber Expression (`"el pipeline falla con {int}"`) o una expresión regular. El mismo método puede atender a varios pasos repitiendo la anotación. En `cucumber-java8` los hooks se declaran llamando a `Before`, `After`, `BeforeStep` y `AfterStep` desde el constructor de la clase de glue.

Para la revisión esto importa dos veces. Primero, la coincidencia es por texto: repetir la misma idea con otra redacción en dos archivos distintos fuerza dos definiciones, y ese es el riesgo de reutilización de pasos que informa `SKILL.md`. Segundo, los parámetros van en la propia frase: si un paso no se entiende suelto (regla 4), tampoco se puede convertir en una expresión con parámetros legibles.

## Dónde viven los hooks

En el glue, anotados con `@Before`, `@After`, `@BeforeStep`, `@AfterStep`, con expresión de etiquetas opcional (`@Before("not @legacy")`) y acceso al `Scenario` (`getName()`, `getUri()`, `getLine()`) y al `Step` (`getKeyword()`, `getText()`, `getLine()`).

Ahí es donde pertenecen el arranque del servidor de aplicación, la preparación del workspace o la captura del log del build. Un paso del tipo «Dado que el entorno de test está levantado» tiene destino de hook en este stack, así que se puede señalar como detalle de bajo nivel con evidencia.

## Filtrado por etiquetas

`-t` / `--tags TAG_EXPRESSION` en la CLI y `cucumber.filter.tags` en `cucumber.properties` o `junit-platform.properties`. La expresión admite `and`, `or`, `not` y paréntesis, como muestra el valor de ejemplo de la documentación. Con Maven, el patrón documentado para acotar la ejecución es pasar las propiedades como `-D`, por ejemplo sobre una feature concreta:

```bash
mvn test -Dsurefire.includeJUnit5Engines=cucumber -Dcucumber.plugin=pretty -Dcucumber.features=path/to/example.feature:10
```

## Formatos de informe

Plugins registrados con `-p` / `--plugin PLUGIN[:PATH]`. Los integrados: `html`, `json`, `junit`, `message`, `pretty`, `progress`, `rerun`, `summary`, `teamcity`, `testng`, `timeline`, `usage`, `unused`. `junit` escribe XML JUnit; `html` y `json` dan el reporte de ejecución; `usage` y `unused` dicen qué definiciones se emplean. Equivalente en propiedades: `cucumber.plugin=pretty, json:path/to/report.json`.

## Comando de parseo verificado

```bash
java -cp "path/to/each/jar:path/to/compiled/.class/files" io.cucumber.core.cli.Main /path/to/your/feature/files --glue com.example.glue --dry-run
```

`--dry-run` (`-d`) está documentado como «Skip execution of glue code», y la invocación de la CLI con `-cp` y `--glue` es la que publica la documentación de Cucumber. La ruta del `-cp` es del proyecto: hay que resolver los frascos de `io.cucumber` y las clases compiladas de test antes de lanzarlo.

Para el motor de JUnit Platform existe la propiedad `cucumber.execution.dry-run=`. La documentación lista la propiedad, pero no documenta cómo se le pasa desde Maven o Gradle en un proyecto concreto: sin comprobarlo con la ayuda del runner, usa la CLI de arriba o declara el parseo como no verificado.

## Tres hechos relevantes para la revisión

1. `Rule:` está soportado: con JUnit Platform, seleccionar la línea de un `Rule` ejecuta todos los escenarios que contiene, así que la agrupación por regla es real y no decorativa. `Background` sigue la definición de Gherkin: un único conjunto de pasos por `Feature` o por `Rule`, ejecutados antes de cada escenario y después de los hooks `Before`.
2. Los pasos admiten tabla como último parámetro (`DataTable`, o colecciones `List<Map<String, String>>`, `Map<String, String>` y equivalentes) y, desde la 8.x, tabla y docstring a la vez en un mismo paso. Un paso con tabla es definible; lo que hay que revisar es que la tabla aporte la clase de equivalencia y no relleno.
3. Los pasos sin definición se reportan como `undefined` y la CLI genera snippets con `--snippets [underscore|camelcase]` (por defecto `underscore`). Con `--dry-run` delante, «hay definición para cada paso» deja de ser una suposición del revisor.

## Fuentes

- cucumber/cucumber-jvm — `cucumber-core/src/main/resources/io/cucumber/core/options/USAGE.txt`, `cucumber-core/README.md`, `cucumber-java/README.md`, `cucumber-java8/README.md`, `cucumber-junit-platform-engine/README.md`, `release-notes/v8.0.0.md`.
- cucumber/docs — `content/docs/cucumber/api.md` (CLI Runner, `--glue`, `-cp`), `content/docs/gherkin/reference.md` (`# language:`, `Rule`).
