# Flujo de trabajo Git

Política de este repositorio. Prevalece sobre cualquier Git Flow genérico: no se crean ramas, etiquetas ni reglas de merge que no estén aquí.

## Modelo

- `main` es la única rama de larga vida. Contiene lo que está listo para usarse.
- No hay `develop`, `release/*` ni `hotfix/*`. Introducirlos exige cambiar esta política antes.

## Ramas de trabajo

Se crean desde `main` y viven lo mínimo posible. Nombres en minúsculas, con palabras separadas por guiones.

| Patrón | Uso |
|---|---|
| `feature/<slug>` | Skill, contenido o funcionalidad nueva |
| `fix/<slug>` | Corrección de un defecto |
| `docs/<slug>` | Documentación |
| `refactor/<slug>` | Reestructuración sin cambio de comportamiento |
| `chore/<slug>` | Mantenimiento, herramientas, configuración |
## Integración

- Se integra en `main` con merge no fast-forward: `git merge --no-ff <rama>`.
- Sin `squash` ni `rebase` sobre ramas ya publicadas.
- Antes de integrar, la ascendencia se comprueba con evidencia: `src/git-flow-management/scripts/verify-branch.sh main <rama>` debe salir con código 0.
- Después de integrar, se verifica el cierre con evidencia mostrada: estado y rama, SHA y mensaje del commit, contención en `main` y referencias.

## Commits

- Conventional Commits: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `style`, `perf`, `ci`, `build`, `revert`.
- Descripción breve, en imperativo y sin punto final.
- Un commit representa un cambio lógico.
- Sin firmas de IA ni líneas `Co-Authored-By` salvo petición expresa.
- Ningún commit con cabos sueltos: lo que se descubre durante la preparación se arregla o se pregunta antes, no en un commit de corrección inmediata.

## Trabajo directo en `main`

Una tarea **pequeña** puede ir directamente a `main`, sin rama. Es pequeña cuando se cumplen todas estas condiciones:

1. El diff es pequeño y su efecto se entiende leyéndolo.
2. No toca datos almacenados, contratos públicos, seguridad, concurrencia ni código ejecutable en varios módulos.
3. No hay cambios ajenos mezclados en los archivos afectados.
4. Se deshace revirtiendo el commit, sin reescribir historia.

Y en todos los casos, también en `main`:

5. Los cambios se dejan preparados en el stage con su mensaje Conventional Commits en inglés, y la confirmación llega después de revisar el diff.
6. Antes de pedir esa confirmación se ha hecho el barrido previo: documentación, `CHANGELOG`, plantillas y referencias describen ya lo que va a quedar en el repositorio.

Cualquier otra cosa entra por una rama corta. Ante la duda, rama.

## Remoto

Ninguno por ahora. Crear un remoto, publicar o hacer `push` es una operación aparte, con su propio plan y su confirmación.

## Documentación

- `README.md`: qué es el repositorio y cómo se usa una skill.
- `CHANGELOG.md`: historial, con formato Keep a Changelog 1.1.0 y versionado SemVer 2.0.0.
- `docs/`: guías y diagramas generados, con sus especificaciones y recibos.
