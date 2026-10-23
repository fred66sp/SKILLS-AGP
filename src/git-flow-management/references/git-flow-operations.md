# Operaciones Git Flow verificables

Usa esta referencia para cada operación de Git Flow en un proyecto nuevo o ya configurado con este modelo.

## Feature o fix

1. Verifica que la rama procede de develop antes de modificarla.
2. Realiza commits coherentes.
3. Comprueba divergencia con develop antes de integrar.
4. Usa PR si existe un mecanismo de revisión. Si no existe, indícalo en el plan.
5. Integra en develop según la estrategia declarada.
6. Prueba que el resultado está contenido en develop.

## Release

1. Crea release/<version> desde develop solo al preparar una release.
2. Limita cambios a estabilización, versión, notas y correcciones aprobadas.
3. Valida preparación antes de integrar.
4. Integra en main; etiqueta solo si fue aprobada; integra el resultado en develop.
5. Prueba que main y develop contienen el resultado.

## Hotfix

1. Crea hotfix desde main para una corrección urgente.
2. Mantén el parche mínimo y validado.
3. Integra en main; etiqueta solo si fue aprobada.
4. Integra el resultado exacto en develop.
5. Prueba que ambas ramas contienen la corrección.

No elimines una rama por el hecho de haber integrado cambios. El borrado requiere operación y autorización específica.
