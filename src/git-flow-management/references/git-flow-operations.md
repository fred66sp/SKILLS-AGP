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

1. Crea release/<version> desde develop solo al preparar una release.
2. Limita cambios a estabilización, versión, notas y correcciones aprobadas.
3. Valida preparación antes de integrar.
4. Integra en main; etiqueta solo si fue aprobada; integra el resultado en develop.
5. Prueba que main y develop contienen el resultado.
6. Propón el borrado de la rama de release y pide confirmación.

## Hotfix

1. Crea hotfix desde main para una corrección urgente.
2. Mantén el parche mínimo y validado.
3. Integra en main; etiqueta solo si fue aprobada.
4. Integra el resultado exacto en develop.
5. Prueba que ambas ramas contienen la corrección.
6. Propón el borrado de la rama de hotfix y pide confirmación.

No elimines una rama por el hecho de haber integrado cambios. El borrado requiere informar antes y una confirmación específica.
