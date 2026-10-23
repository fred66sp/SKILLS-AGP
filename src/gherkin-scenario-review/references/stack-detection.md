# Detección del stack

Localiza el runner que va a ejecutar el `.feature` que tienes delante y elige una sola referencia de stack. La detección no cambia las cuatro reglas: solo decide desde qué runner se juzga si un paso es definible y si un detalle de bajo nivel pertenece a hooks.

Léelo en el paso 7 del procedimiento de `SKILL.md`, antes que cualquier `stack-<stack>.md`. Carga después una sola de esas referencias.

## Tabla de decisión

Lee siempre los dos primeros grupos (gestor de dependencias y configuración del runner) antes de decidir. Un `.feature` en `features/` no identifica el stack por sí solo: las cinco familias usan esa carpeta.

| Señal en el proyecto | Stack | Referencia a cargar |
|---|---|---|
| `package.json` con `@cucumber/cucumber` en `dependencies` o `devDependencies`, más `cucumber.json`, `cucumber.js`, `cucumber.mjs` o carpeta `features/` | JavaScript / TypeScript | `stack-javascript.md` |
| `requirements.txt` o `pyproject.toml` con `behave`, más `behave.ini` o `features/steps/` con `environment.py` | Python (behave) | `stack-python.md` |
| `requirements.txt`, `pyproject.toml` o `pytest.ini` con `pytest-bdd`, más la clave `bdd_features_base_dir` o imports de `pytest_bdd` en `test_*.py` | Python (pytest-bdd) | `stack-python.md` |
| `pom.xml` o `build.gradle` con artefactos `io.cucumber`, más `.feature` bajo `src/test/resources` o `src/test/features`, `cucumber.properties`/`junit-platform.properties` o una clase con `@Suite` | Java / JVM | `stack-java.md` |
| `*.csproj` con paquetes `Reqnroll.*`, más `reqnroll.json` y archivos `.feature` en el proyecto de test | .NET | `stack-dotnet.md` |
| `go.mod` con `github.com/cucumber/godog`, más `features/*.feature` y un `*_test.go` que use `godog.ScenarioContext` | Go | `stack-go.md` |

## Orden de lectura

1. Lee el manifiesto de dependencias: `package.json`, `requirements.txt`, `pyproject.toml`, `pom.xml`, `build.gradle`, `*.csproj`, `go.mod`. Es la señal más fiable, porque declara el runner que se resuelve al ejecutar.
2. Lee los lock files para confirmar la versión cuando el informe necesite precisar comportamiento de un `--dry-run`: `package-lock.json`, `pnpm-lock.yaml`, `uv.lock`, `gradle.lockfile`, `packages.lock.json`, `go.sum`.
3. Confirma con la configuración del runner: `cucumber.json`/`cucumber.js`, `behave.ini`, `pytest.ini`, `junit-platform.properties`, `reqnroll.json`. Ninguna de estas configuraciones existe en godog: allí la configuración vive en el código del `TestMain`.
4. Mira los archivos de test ya escritos: `features/steps/*.py`, `src/test/java/**/*StepDefinitions.java`, `**/*StepDefinitions.cs`, `*_test.go` con `ctx.Step`. Un directorio de pasos es la prueba más fuerte de que el runner está instalado.

## Casos de conflicto

- Dos stacks en el mismo repositorio (monorepo, o un backend Go con un frontend JS): decide por la carpeta que contiene el `.feature` revisado y carga una sola referencia. Nunca mezcles dos.
- El `.feature` está fuera de cualquier ruta esperada y no hay manifiesto: declara el stack como no identificado.
- Un `package.json` con `@badeball/cypress-cucumber-preprocessor` u otro envoltorio no es cucumber-js puro. Si el proyecto no expone el CLI `cucumber-js`, trata el comando de parseo como no verificado.
- El encabezado `# language:` no identifica el stack: los cinco leen dialectos Gherkin. Úsalo solo para saber con qué palabras clave revisó el archivo el paso 2.

## Sin runner en el proyecto

Si no aparece ningún manifiesto con runner, ni configuración, ni carpeta de pasos, el proyecto no tiene automatización declarada. La revisión se aplica igual: los pasos 2 a 6 y el informe no dependen del stack.

En ese caso escribe en el informe la frase siguiente, y nada más en materia de automatizabilidad:

> Sin runner detectado: la automatizabilidad de los pasos no está verificada. La revisión juzga el artefacto como especificación.

No afirmes que un paso «no se puede automatizar» ni que «no hay forma de definirlo». Lo que no se comprueba, se declara como no comprobado.

## Criterio compartido: hook o Gherkin

La documentación de Cucumber da el criterio que sirve a los cinco stacks: lo que ocurre en un hook `Before` es invisible para quien solo lee las features, así que conviene valorar `Background` como alternativa más explícita cuando el setup debe ser legible por personas no técnicas; el hook se deja para la lógica de bajo nivel, como arrancar un navegador o borrar datos de una base de datos. `Background` se ejecuta antes de cada escenario, pero después de los hooks `Before`, y admite un único bloque por `Feature` o por `Rule`.

Aplica ese criterio con la referencia del stack detectado: un paso de bajo nivel del paso 4 es candidato a hook si el stack tiene dónde recibirlo, y es candidato a `Background` si ese estado lo consume el negocio.

## Con un runner detectado

Aplica el paso 7 con la referencia del stack detectado y recuerda el orden de evidencia que exige `SKILL.md`:

1. Comprueba si el runner está instalado en el proyecto destino antes de proponer ningún comando. La referencia documenta el comando, no garantiza que el binario exista.
2. Ejecuta el comando de parseo o de dry-run que la referencia trae verificado, si lo trae. Con su salida delante, la definibilidad de los pasos queda como hecho observado.
3. Si la referencia trae la línea de fallback, omite el comando y declara el parseo como no verificado por el runner. Nunca inventes la bandera.

## Fuentes

- cucumber/docs — `content/docs/cucumber/api.md` (criterio `Before` frente a `Background`), `content/docs/gherkin/reference.md` (un solo bloque de `Background` por `Feature` o `Rule`).
- cucumber/cucumber-js — `docs/configuration.md`, `docs/support_files/api_reference.md`.
- behave/behave — `docs/behave.rst` (configuration file parameters), `docs/gherkin.rst` (layout de `features/`).
- pytest-dev/pytest-bdd — `_autodocs/configuration.md` (`bdd_features_base_dir`), `docs/index.rst` (organización de `features/`).
- cucumber/cucumber-jvm — `cucumber-core/src/main/resources/io/cucumber/core/options/USAGE.txt`, `cucumber-junit-platform-engine/README.md`.
- reqnroll/reqnroll — `docs/automation/hooks.md`, `docs/installation/setup-ide.md` (`cucumber.features`, `cucumber.glue`).
- cucumber/godog — `README.md` (carpeta `features/` junto a `go.mod` y a un `*_test.go` con las definiciones), `_autodocs/configuration.md` (`Paths` por defecto `["features"]`).
