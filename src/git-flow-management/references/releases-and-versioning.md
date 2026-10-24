# Releases y versionado

Usa esta referencia solo al preparar una release o un hotfix en un proyecto que tenga versionado de producto.

## SemVer cuando sea aplicable

Usa MAJOR.MINOR.PATCH solo si el proyecto declara Semantic Versioning o el usuario ha adoptado esta política:

- MAJOR: cambio incompatible.
- MINOR: funcionalidad compatible nueva.
- PATCH: corrección compatible.

No deduzcas una versión nueva solo a partir del tipo de commit. Comprueba los cambios públicos, el historial y la política del proyecto.

## Qué decide esta referencia

El recorrido de ramas —crear, integrar, probar contención y proponer borrado— está descrito una sola vez en [operaciones Git Flow verificables](git-flow-operations.md). Este fichero aporta lo que ese recorrido necesita por su parte y no puede deducirse del Git:

- El número de versión que toca, dónde lo declara el proyecto y su entrada en el changelog.
- La etiqueta y la publicación: se crean solo si están en el plan aprobado.
- El nombre esperado de la rama: `release/<version>` y `hotfix/<id>-<slug>`.

Si falta alguna de esas tres decisiones, se pregunta antes de integrar: una release sin versión fijada no se puede cerrar. No hay una segunda lista de pasos en este fichero a la que mantener sincronizada la anterior.
