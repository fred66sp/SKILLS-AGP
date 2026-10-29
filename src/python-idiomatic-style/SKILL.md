---
name: python-idiomatic-style
description: "Escribe y revisa Python idiomático y tipado para librerías, servicios y CLIs: declara el intérprete y el empaquetado en pyproject.toml, modela datos con dataclasses, enums y Protocol, anota las fronteras públicas y comprueba tipos con mypy o pyright, propaga errores con causas específicas y context managers, evita estado mutable compartido, organiza dependencias con uv y ruff, y mantiene una CLI con argparse, salida separada y códigos de salida. Úsala al crear, refactorizar o revisar módulos `.py`, al elegir estructura de proyecto y dependencias, o al construir una CLI de Python. No la uses para pruebas, cobertura ni puertas de verificación, que tienen su propia skill, ni para validación de datos en runtime."
metadata:
  version: "0.1.0"
---

# Estilo y diseño idiomático en Python

Python no impide casi nada: un `dict` acepta cualquier clave, un `None` viaja hasta donde no se espera y un `except Exception` convierte un defecto en silencio. El trabajo de esta skill es que el código diga lo que acepta, lo que devuelve y lo que puede fallar, y que el intérprete y el comprobador de tipos lo sostengan.

Esta skill posee el lenguaje, los tipos, la estructura del proyecto, las dependencias, el empaquetado y la forma de una CLI. Las pruebas, la elección de capa, los datos de prueba y la puerta de verificación son de `python-testing-and-verification`.

## Invariantes de estilo Python

1. Declara el intérprete antes de escribir: `requires-python` en `pyproject.toml` y la misma versión en la matriz de CI. Una sintaxis nueva, como `match`, `X | Y`, `Self` o `tomllib`, se usa solo si el mínimo declarado la admite.
2. `pyproject.toml` es la única fuente de metadatos y de configuración de herramientas. No repartas versión, dependencias ni reglas de ruff entre `setup.py`, `setup.cfg`, `requirements.txt` y `tox.ini`; si ya existen por historia, no añadas una cuarta.
3. Estructura `src/` para una librería publicable: `src/<paquete>/` y `tests/` hermanos. Un script suelto no necesita paquete; un paquete no finge ser un script.
4. Anota las firmas públicas: parámetros y retorno. Los locales se infieren. `Any` se justifica en la misma línea o no se escribe; nunca llega a la API pública.
5. Modela los datos con `dataclass(frozen=True, slots=True)` cuando sean valores, `Enum` cuando el conjunto sea cerrado, `TypedDict` cuando la forma sea un diccionario externo y `Protocol` cuando el consumidor defina el contrato. Una tupla posicional de cuatro elementos no es un tipo.
6. `None` no es un valor por defecto universal: si la ausencia es un estado, se modela con `X | None` y se comprueba. Un parámetro opcional no cambia de significado según el tipo que reciba.
7. Nunca uses un objeto mutable como valor por defecto (`def f(x=[])`, `x={}`). Usa `None` y construye dentro, o `field(default_factory=...)`.
8. Las excepciones son parte del contrato: define una base del paquete, deriva causas específicas y conserva la original con `raise ... from exc`. `except Exception: pass` no es manejo de errores; `except Exception` sin `raise` exige una razón escrita.
9. Usa `with` para todo recurso: ficheros, conexiones, locks, transacciones y cambios de entorno. Si el recurso no lo trae, envuélvelo en `contextlib.contextmanager` antes de repetir el `try/finally`.
10. Itera y transforma con comprensiones cuando la expresión quepa en dos líneas y no tenga efectos; si necesita ramas, `try` o `await`, se escribe el bucle.
11. Un generador no se consume dos veces. Si el resultado se recorre más de una vez, materialízalo en una lista o devuelve una colección.
12. La mutación se declara: una función que modifica su argumento lo dice en el nombre o en la docstring, y no lo hace con un valor que el llamante cree propio.
13. El dinero no se calcula en `float`: `Decimal` con contexto explícito o enteros de la menor denominación. Una fecha se transporta con zona (`datetime.now(timezone.utc)`) y se compara con zonas compatibles; `datetime.utcnow()` está prohibido.
14. Las rutas se manejan con `pathlib.Path`, no con concatenación de cadenas. La codificación se declara siempre que se lea o escriba texto: UTF-8 por defecto en el proyecto.
15. Un `print` es salida de usuario, no diagnóstico. El diagnóstico va a `logging`; `stdout` queda para el resultado que otro programa consume.
16. Una dependencia se justifica: primero la biblioteca estándar, después una dependencia revisada en licencia, mantenimiento y seguridad. Un solo gestor y un solo lockfile.
17. `ruff` es el formateador y el linter por defecto cuando el proyecto no declare otros. La configuración vive en `pyproject.toml` y el conjunto de reglas se elige, no se hereda por copia.
18. Una CLI usa `argparse` salvo que el proyecto ya tenga Typer o Click. El contrato no cambia con la herramienta: `stdout` para el resultado, `stderr` para el diagnóstico, códigos de salida acotados y modo no interactivo.
19. Respeta la convención del proyecto cuando exista. No reformatees código ajeno ni mezcles una refactorización con un cambio de comportamiento.

## Procedimiento de estilo Python

**Paso 1: Inspeccionar antes de escribir.**
1. Lee `pyproject.toml`, el lockfile, la versión de Python de CI y las herramientas declaradas: ruff, mypy o pyright, pytest, build.
2. Localiza la disposición real: `src/`, paquete plano, `tests/` y puntos de entrada (`[project.scripts]`).
3. Ejecuta el comprobador de tipos y el linter existentes para conocer el estado de partida; no los sustituyas.
4. Revisa los patrones vecinos: errores, modelos, nombres, imports y logging. Una regla escrita gana sobre la preferencia.

**Paso 2: Modelar los datos y los estados.**
1. Escribe una frase por entidad y otra por estado. Si dos estados no pueden coexistir, sepáralos con una unión o dos tipos.
2. Decide qué valores son identificadores, cuáles cantidades y cuáles contenido libre. Anota los dos primeros y no los mezcles con `str` desnudo en la API pública.
3. Decide dónde entra el dato externo: fichero, entorno, HTTP, base de datos. Ese punto es una frontera y se valida en runtime con `python-testing-and-verification`; el tipo no valida nada.
4. Define el error base del paquete y sus causas antes de escribir el camino feliz.

**Paso 3: Escribir el módulo.**
1. Escribe las firmas públicas antes de los cuerpos. Anota parámetros, retorno y excepciones documentadas.
2. Guardas primero y retorno temprano; el camino feliz no va indentado dentro de condicionales.
3. Aplica `references/language-rules.md` y `references/type-rules.md` cuando la decisión no sea evidente.
4. Los imports se agrupan por biblioteca estándar, terceros y locales, y se ordenan con la herramienta del proyecto. Sin imports circulares ni `import *`.

**Paso 4: Resolver el proyecto y las dependencias.**
1. Lee `references/project-and-packaging.md` antes de tocar metadatos, layout o build.
2. Mantén el dominio separado del adaptador (HTTP, CLI, base de datos). Un paquete pequeño con un módulo por responsabilidad sigue siendo válido.
3. Añade una dependencia solo con una razón y su alternativa descartada. Un extra opcional no se convierte en dependencia base.
4. Fija el backend de build y comprueba que `python -m build` produce el artefacto esperado antes de publicar.

**Paso 5: Construir la CLI, si la hay.**
1. Lee `references/cli-rules.md` antes de elegir comandos y flags.
2. Cada comando valida sus argumentos al entrar, no a mitad del trabajo. `--help` y `--version` funcionan sin efectos.
3. Toda operación destructiva exige confirmación explícita y admite `--dry-run` y modo no interactivo. `KeyboardInterrupt` devuelve un código distinto de éxito, sin traza.
4. La salida legible va a `stdout`, el diagnóstico a `stderr`; `--json` es estable y no mezcla avisos con datos.

**Paso 6: Comprobar el diff.**
1. Ejecuta `ruff format --check`, `ruff check` y el comprobador de tipos. Un cambio que rompe la comprobación no está terminado.
2. Busca `Any`, `# type: ignore`, `cast`, `except Exception`, `print` de diagnóstico y dependencias nuevas. Cada uno necesita una razón o se elimina.
3. Comprueba que no has añadido capas, abstracciones ni opciones que nadie pidió.
4. Cierra con el bloque de resultado.

## Errores y paradas de estilo Python

- Si el proyecto no tiene comprobador de tipos, no lo impongas dentro de un cambio funcional: propón la adopción aparte y demuestra el coste.
- Si una dependencia no publica tipos utilizables, aísla el `Any` en un adaptador y documenta el límite; no lo extiendas por el dominio.
- Si el error viene de una herramienta externa, no parchees el entorno virtual compartido. Actualiza, aísla o declara el bloqueo.
- Si el usuario pide una abstracción genérica sin dos usos reales, entrega la versión concreta y explica en una línea qué la haría merecer la abstracción.
- Si el dato entra por HTTP, formulario, entorno o API de terceros, no lo valides con una anotación: pasa a `python-testing-and-verification`.
- Si el proyecto mezcla dos gestores de paquetes o dos lockfiles, no añadas el tercero: informa y deja la decisión.
- Si una regla de este contrato choca con una convención escrita del proyecto, gana la convención cuando no contradiga el lenguaje ni el contrato de la CLI.

## Resultado de estilo Python

```text
Estado: completado | parcial | bloqueado
Módulos tocados: <lista con su responsabilidad>
Decisiones de tipos: <dataclasses, enums, Protocol, uniones, genéricos>
Decisiones de proyecto: <layout, pyproject, dependencias, build>
CLI: <comandos, flags, salida, códigos de salida, o "no aplica">
Comprobaciones: <ruff format --check, ruff check, mypy|pyright>
Deuda declarada: <lista, o "ninguna">
No verificado: <lista, o "ninguno">
```

## Referencias de estilo Python

- [language-rules](references/language-rules.md): intérprete, estructura, nombres, funciones, datos, excepciones, recursos, asincronía y logging. Léela en los pasos 2 y 3 cuando una regla no sea evidente.
- [type-rules](references/type-rules.md): tablas de decisión para anotaciones, `Any`, uniones, `Protocol`, `TypedDict`, genéricos, `overload`, `TypeGuard` y supresiones. Léela en el paso 3.
- [project-and-packaging](references/project-and-packaging.md): `pyproject.toml`, layout, dependencias, extras, lockfile, backend de build y publicación. Léela en el paso 4.
- [cli-rules](references/cli-rules.md): contrato de una CLI de Python con `argparse` o Typer, salida, códigos de salida, cancelación y empaquetado del punto de entrada. Léela en el paso 5.
