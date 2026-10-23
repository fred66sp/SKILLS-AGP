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

## Commit confirmado

Después de la confirmación explícita, ejecuta exactamente el mensaje aprobado:

~~~bash
git commit -m "feat(cli): add staged commit confirmation"
~~~

Si el usuario pide revisar antes de commitear, deja los cambios preparados y detente ahí: ese es un resultado válido.

## Verificación del commit

~~~bash
git show --stat --oneline HEAD
git status --short --branch
~~~

Si el SHA no existe o el diff no coincide con los archivos aprobados, el paso no está terminado.

## Comandos de integración y limpieza

Solo con confirmación que enumere la etapa. Revalida el estado justo antes:

~~~bash
git log --oneline main..<rama>
git merge --no-ff <rama>
git merge-base --is-ancestor <rama> main
git branch -d <rama>
~~~

`git branch -d` se niega a borrar una rama no integrada; no lo sustituyas por `-D` sin autorización específica.

## Comandos remotos

Cualquier comando remoto requiere confirmación propia, aunque el commit ya esté hecho:

~~~bash
git push -u origin <rama>
git ls-remote --heads origin
~~~

No hagas push automáticamente después de commitear. No hagas push forzado sin autorización específica para ese comando.

## Procedimiento de rama

Antes de crear una rama, muestra la rama base y su SHA, el nombre propuesto, el estado de upstream y de adelanto o retraso, y si la rama es solo local o se publicará después.
