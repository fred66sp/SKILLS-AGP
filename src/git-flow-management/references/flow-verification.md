# Verificación de flujo

Usa esta referencia después de cualquier operación Git Flow. Un flujo solo es COMPLETO si pasan todas las comprobaciones aplicables.

## Comandos de evidencia

~~~bash
git status --short --branch
git log --graph --oneline --decorate --all -n 40
git merge-base --is-ancestor <ancestor> <descendant>
git branch -vv
git ls-remote --heads <remote>
git ls-remote --tags <remote>
~~~

La comprobación de ascendencia puede ejecutarse con `scripts/verify-branch.sh <ancestro> <descendiente> [remoto]`, que devuelve 0 cuando la contención se verifica, 1 cuando no se cumple y 2 cuando el uso o una referencia es inválido.

## Creación de rama

- La rama existe y es la rama actual o está identificada.
- Su commit de base es descendiente de la base obligatoria.
- No hay cambios no previstos en el árbol.

## Commit

- El SHA existe.
- El mensaje cumple la convención aplicable.
- El diff coincide con los archivos aprobados.
- La validación acordada ha terminado con el resultado declarado.

## Feature o fix integrado

- La rama fuente deriva de develop.
- El resultado está contenido en develop.
- No aparece directamente integrado en main como sustitución del paso de develop.
- La PR o mecanismo de revisión previsto está identificado cuando existe.

## Release integrada

- Release deriva de develop.
- El resultado está contenido en main.
- El resultado de main está contenido en develop.
- La etiqueta, versión y changelog se verifican si estaban incluidos en el plan.

## Hotfix integrado

- Hotfix deriva de main.
- El resultado está contenido en main.
- El resultado de main está contenido en develop.
- La etiqueta o publicación se verifican si estaban incluidas en el plan.

## Resultado

- COMPLETO: todas las comprobaciones aplicables pasan.
- INCOMPLETO: alguna condición obligatoria no se ha ejecutado o ha fallado.
- NO VERIFICADO: no hay evidencia suficiente para afirmar el resultado.
