# Verificación de flujo

Usa esta referencia después de cualquier operación Git. Un flujo solo es COMPLETO si pasan todas las comprobaciones aplicables a la rama que se ha usado.

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

## Comprobaciones por tamaño

| Tamaño | Obligatorio antes de cerrar |
|---|---|
| Pequeña | Estado del árbol, SHA y mensaje del commit, validación localizada si existe |
| Normal | Lo anterior más contención en `main` cuando hubo integración y validación principal del proyecto |
| Compleja | Lo anterior más comprobaciones de los puntos críticos y de cada rama implicada |

## Commit

- El SHA existe.
- El mensaje cumple el formato Conventional Commits, con descripción en inglés.
- El diff coincide con los archivos aprobados.
- La validación acordada ha terminado con el resultado declarado.
- El árbol de trabajo queda en el estado anunciado, sin cambios ajenos arrastrados.

## Trabajo con rama corta integrada en main

- La rama existía y derivaba de `main`.
- El resultado está contenido en `main`.
- Si la rama se borró, era la correcta, estaba integrada y su borrado se confirmó.

## Feature o fix integrado en develop

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

## Publicación

- Cada comando remoto ejecutado estaba en la confirmación que lo autorizaba.
- La referencia remota esperada existe y apunta al commit declarado.
- No se ha ejecutado ningún push forzado ni borrado remoto sin autorización específica.

## Resultado

- COMPLETO: todas las comprobaciones aplicables pasan.
- INCOMPLETO: alguna condición obligatoria no se ha ejecutado o ha fallado.
- NO VERIFICADO: no hay evidencia suficiente para afirmar el resultado.
