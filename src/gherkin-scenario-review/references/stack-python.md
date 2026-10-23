# Stack Python (behave y pytest-bdd)

Referencia del runner para el paso 7. Sirve para juzgar si un paso es definible y si su detalle pertenece a hooks, no para escribir automatización.

Léelo en el paso 7 del procedimiento de `SKILL.md`, después de `stack-detection.md` y solo cuando el stack detectado es Python. Usa la sección del runner que el proyecto use (behave o pytest-bdd); los dos comparten Gherkin pero no comparten CLI.

## Runner, idioma y ubicación de los `.feature`

**behave.** Comando `behave`. Sin argumentos, carga las features desde el subdirectorio `features/` del directorio de lanzamiento; dentro hacen falta una carpeta `steps/` y, si existe, `environment.py` en el mismo nivel que `steps/`. El dialecto se declara con el comentario de idioma en la primera línea (`# language: fr` con `Fonctionnalité:` es el ejemplo de la documentación); esa cabecera manda sobre la opción `lang` de `behave.ini` y de la línea de comandos. La lista de idiomas soportados se obtiene con `behave --lang-list`.

**pytest-bdd.** Es un plugin de `pytest`, así que el comando es `pytest`. Los `.feature` se agrupan por semántica en `features/…/x.feature` y la carpeta base se declara con `bdd_features_base_dir = features/` en la sección `[pytest]` de `pytest.ini`, `tox.ini`, `setup.cfg` o `pyproject.toml`. El módulo de test los enlaza con `@scenario("tools/check.feature", "El validador no encuentra hallazgos")` o con `scenarios()`. Soporta la directiva `# language: <language>` desde la versión 8.0.0.

## Cómo se casa un paso con su definición

**behave.** Decoradores `@given`, `@when`, `@then` y `@step` sobre una función que recibe `context` y luego los parámetros. El matcher de pasos por defecto es `parse`, con placeholders `"{texto}"`; `use_step_matcher("re")` cambia a expresiones regulares con grupos nombrados `(?P<name>...)`. Los pasos que empiezan con `and` o `but` pasan a llevar la palabra clave del paso anterior, así que un `Y el informe queda en disco` se resuelve contra las definiciones de `Cuando`.

**pytest-bdd.** Decoradores `@given("hay un artefacto en el workspace")`, `@when(...)`, `@then(...)`, con alias apilando decoradores sobre la misma función. Un `@given` es además un fixture: si devuelve algo y se le pasa `target_fixture="informe"`, ese valor alimenta a los pasos siguientes.

En los dos, la clave de búsqueda es el texto literal del paso. Para la regla 4 esto pesa directo: un paso escrito sin sujeto o como fragmento («la compilación») no puede reutilizarse en otro escenario sin copiar el contexto que lo hacía entendible.

## Dónde viven los hooks

**behave.** En `features/environment.py`: `before_all`, `before_feature`, `before_rule`, `before_scenario`, `before_step` y sus `after_…`, además de `before_tag`. En modo dry-run no se ejecuta ningún hook.

**pytest-bdd.** En fixtures de pytest (`conftest.py`) y en los hooks `pytest_bdd_before_step`, `pytest_bdd_after_step`, `pytest_bdd_step_func_lookup_error`.

La consecuencia para la revisión: preparación de entorno, limpieza y estado compartido tienen dónde irse en ambos runners. Un paso de bajo nivel («Cuando espero a que termine el build de documentación») señalado en el paso 4 tiene destino de hook, y por eso se puede pedir que salga del Gherkin sin decir cómo se implementa.

## Filtrado por etiquetas

**behave.** `behave --tags="@smoke and not @xfail"`; los tags se heredan de Feature a Rule y de Rule a Scenario.

**pytest-bdd.** Los tags Gherkin se convierten en markers de pytest con el `@` quitado: `pytest -m "backend and login and successful"`. Con `--strict-markers`, cada tag usado en los `.feature` debe estar declarado en `markers` del `pytest.ini`.

## Formatos de informe

**behave.** `-f json`, `-f json.pretty`, `-f plain`, `-f pretty`, `-f progress3`; y los que solo sirven en dry-run: `-f steps`, `-f steps.usage`, `-f tags`. La lista de formatters integrados no incluye HTML, así que un informe HTML en un proyecto behave viene de un complemento. El informe JUnit tampoco es un formatter: se activa con la opción de configuración `junit` y su carpeta con `junit_directory`.

**pytest-bdd.** `pytest --cucumberjson=<ruta>` (JSON al estilo Cucumber, con los esquemas expandidos en escenarios), `pytest --junit-xml=<ruta>` (flag de pytest) y `pytest -v --gherkin-terminal-reporter` para salida en Gherkin por terminal.

## Comandos de parseo verificados

```bash
behave --dry-run
pytest --collect-only
```

`behave -d, --dry-run` invoca los formatters sin ejecutar los pasos, y en ese modo los pasos sin definición se marcan con el estado `untested_undefined`: es evidencia de parseo y de coincidencia de definiciones a la vez. `pytest --collect-only` solo recolecta sin ejecutar, y en pytest-bdd la recolección parsea el `.feature` y comprueba que el escenario nombrado existe; la búsqueda de la definición de cada paso ocurre en ejecución, con `StepDefinitionNotFoundError`. Por eso un `--collect-only` en verde no prueba que los pasos sean definibles: lo dice el informe como parseo verificado, no como automatizabilidad verificada.

## Tres hechos relevantes para la revisión

1. `Background`: behave lo soporta y sus pasos se inyectan en cualquier escenario de su ámbito; pytest-bdd implementa el `Background` de Gherkin y sus pasos se ejecutan antes de los `Given` propios de cada escenario. En los dos, el estado repetido tiene dónde vivir sin escribirlo siete veces.
2. Keyword `Rule:`: behave lo trata como contenedor de escenarios con su propio `Background` y sus tags, y expone `before_rule`/`after_rule`; pytest-bdd lo acepta desde la 8.0.0 y tiene un error propio de parseo para un `Rule` mal colocado (`RuleError`). En ese último caso la agrupación no es estilo: es un fallo que el runner reporta.
3. Datos en el paso: behave expone la tabla del paso como `context.table` (iterable por nombre de columna); pytest-bdd pasa argumentos `datatable` y `docstring`. Escenario con tabla en un paso es definible en ambos.

## Fuentes

- behave/behave — `docs/behave.rst`, `docs/gherkin.rst`, `docs/api.rst`, `docs/tutorial.rst`, `docs/appendix.formatters.rst`, `docs/appendix.status.rst`, `docs/new_and_noteworthy_v1.2.6.rst`, `docs/new_and_noteworthy_v1.2.7.rst`, `behave/runner.py` (`should_run_hook` en modo dry-run).
- pytest-dev/pytest-bdd — `README.rst`, `docs/index.rst`, `_autodocs/configuration.md`, `_autodocs/errors.md`, `_autodocs/api-reference/hooks.md`.
- pytest-dev/pytest — `doc/en/reference/reference.rst`, `doc/en/how-to/output.rst`.
