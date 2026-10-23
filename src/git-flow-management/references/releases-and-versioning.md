# Releases y versionado

Usa esta referencia solo al preparar una release o un hotfix en un proyecto que tenga versionado de producto.

## SemVer cuando sea aplicable

Usa MAJOR.MINOR.PATCH solo si el proyecto declara Semantic Versioning o el usuario ha adoptado esta política:

- MAJOR: cambio incompatible.
- MINOR: funcionalidad compatible nueva.
- PATCH: corrección compatible.

No deduzcas una versión nueva solo a partir del tipo de commit. Comprueba los cambios públicos, el historial y la política del proyecto.

## Release

1. Verifica que release/<version> procede de develop.
2. Limita cambios a estabilización, versión, notas y correcciones aprobadas.
3. Comprueba ubicaciones de versión y changelog si existen.
4. Integra release en main mediante el mecanismo previsto.
5. Crea etiqueta y publicación solo si están en el plan aprobado.
6. Integra el resultado de main de vuelta a develop.
7. Verifica que ambos destinos contienen la release.

## Hotfix

1. Verifica que hotfix/<id>-<slug> procede de main.
2. Mantén el parche mínimo.
3. Integra en main y publica etiqueta solo si procede.
4. Integra el mismo resultado de vuelta a develop.
5. Verifica que main y develop contienen la corrección.

No elimines una rama de release u hotfix por el hecho de haber integrado cambios. El borrado requiere una operación y autorización específica.
