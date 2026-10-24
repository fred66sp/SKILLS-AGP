# Operaciones Git Flow verificables

Usa esta referencia solo en un repositorio que declara la política Git Flow, o cuando el usuario la encarga expresamente. En el modelo por defecto no hay develop, release ni hotfix.

En todos los casos, el commit sigue el protocolo de confirmación de la skill: rutas preparadas, mensaje Conventional Commits en inglés, confirmación explícita y verificación posterior. Ninguna de estas secuencias autoriza un push.

## Feature o fix

1. Verifica que la rama procede de develop antes de modificarla.
2. Realiza commits coherentes, cada uno confirmado.
3. Comprueba divergencia con develop antes de integrar.
4. Usa PR si existe un mecanismo de revisión. Si no existe, indícalo en el plan.
5. Integra en develop según la estrategia declarada, con autorización.
6. Prueba que el resultado está contenido en develop.
7. Si la rama ya no se necesita, propón borrarla y pide confirmación.

## Release

1. Crea `release/<version>` desde `develop` solo al preparar una release, y verifica la ascendencia antes de trabajar.
2. Limita cambios a estabilización, versión, notas y correcciones aprobadas.
3. Fija el número de versión, dónde lo declara el proyecto y su entrada de changelog según [releases y versionado](releases-and-versioning.md).
4. Valida la preparación antes de integrar.
5. Integra en `main`; crea etiqueta y publicación solo si están en el plan aprobado; integra el resultado en `develop`.
6. Prueba que `main` y `develop` contienen el resultado.
7. Propón el borrado de la rama de release y pide confirmación.

## Hotfix

1. Crea `hotfix/<id>-<slug>` desde `main` para una corrección urgente, y verifica la ascendencia antes de trabajar.
2. Mantén el parche mínimo y validado.
3. Fija la versión y su entrada de changelog según [releases y versionado](releases-and-versioning.md).
4. Integra en `main`; crea etiqueta y publicación solo si fue aprobada.
5. Integra el resultado exacto en `develop`.
6. Prueba que ambas ramas contienen la corrección.
7. Propón el borrado de la rama de hotfix y pide confirmación.

No elimines una rama por el hecho de haber integrado cambios. El borrado requiere informar antes y una confirmación específica.
