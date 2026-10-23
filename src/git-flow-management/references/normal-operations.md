# Operaciones normales de Git

Usa esta referencia para la inspección ampliada, los comandos de preparación por rutas enumeradas y la verificación del commit. Los pasos conceptuales de preparación, las convenciones de rama y el formato de commit están en [commits y ramas](commits-and-branches.md); aquí viven los comandos.

## Inspección segura

~~~bash
git status --short --branch
git diff --stat
git diff -- <paths>
git diff --cached --stat
git diff --cached -- <paths>
git log --oneline --decorate -n 12
~~~

Enumera por separado los archivos rastreados modificados, los archivos no rastreados, los cambios preparados, los archivos generados cuando proceda y los cambios ajenos al encargo.

## Comandos de preparación

Prepara únicamente las rutas que el plan enumera y revisa el diff preparado antes de pedir confirmación:

~~~bash
git add -- src/module.ts tests/module.test.ts
git diff --cached
~~~

Evita preparar de forma global. `git add .` y `git add -A` exigen un plan que explique por qué todos los cambios forman una unidad.

## Verificación del commit

~~~bash
git show --stat --oneline HEAD
git status --short --branch
~~~

Si el SHA no existe o el diff no coincide con los archivos aprobados, el paso no está terminado.

## Procedimiento de rama

Antes de crear una rama, muestra la rama base y su SHA, el nombre propuesto, el estado de upstream y de adelanto o retraso, y si la rama es solo local o se publicará después. No hagas push automáticamente.
