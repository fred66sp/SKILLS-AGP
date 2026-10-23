# Commits y ramas

Usa esta referencia al crear una rama o preparar un commit en un proyecto nuevo que aplica la política Git Flow por defecto.

## Ramas

- Usa minúsculas y palabras separadas por guiones.
- Para trabajo asociado a una incidencia conocida: feature/<id>-<slug>, fix/<id>-<slug> o hotfix/<id>-<slug>.
- Para una release: release/<version>.
- Verifica la base antes de crear la rama:

~~~bash
git merge-base --is-ancestor <base> HEAD
git log -1 --oneline <base>
~~~

No crees una rama desde main cuando la tabla de Git Flow exige develop. Si la base está desactualizada frente a su upstream, informa del estado y propón una actualización de la base como operación separada y confirmada.

## Commits convencionales

Usa el formato:

~~~text
<type>(<scope opcional>): <descripción en imperativo>
~~~

Tipos permitidos: feat, fix, docs, chore, refactor, test, style, perf, ci, build y revert.

- Un commit representa un cambio lógico.
- No añadas firmas de IA ni líneas Co-Authored-By salvo solicitud expresa.
- Usa descripción breve, en imperativo y sin punto final.
- Una ruptura compatible se marca con ! o con un pie BREAKING CHANGE.

## Preparación segura

1. Inspecciona cambios rastreados, no rastreados y ya preparados.
2. Separa explícitamente lo que queda fuera del commit.
3. Prepara únicamente rutas enumeradas.
4. Revisa el diff preparado antes de pedir confirmación.
5. Ejecuta la validación acordada antes y después si procede.
