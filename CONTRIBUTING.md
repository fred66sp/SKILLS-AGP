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

## Excepción directa a `main`

Un commit directo en `main` solo se permite cuando se cumplen **todas** estas condiciones:

1. El diff toca únicamente documentación (`docs/**`, ficheros `*.md`) o configuración no ejecutable (`.gitignore`, `.gitattributes`) con cambios de una o dos líneas.
2. El diff completo tiene menos de 20 líneas añadidas o eliminadas.
3. No cambia código ejecutable ni ficheros de `src/**/scripts/`.
4. El cambio se ha validado de forma proporcional: enlaces que resuelven, cifras y rutas comprobadas.
5. La confirmación llega después de revisar el diff y es específica para ese commit.

Cualquier otra cosa entra por una rama corta.

## Remoto

Ninguno por ahora. Crear un remoto, publicar o hacer `push` es una operación aparte, con su propio plan y su confirmación.

## Documentación

- `README.md`: qué es el repositorio y cómo se usa una skill.
- `CHANGELOG.md`: historial, con formato Keep a Changelog 1.1.0 y versionado SemVer 2.0.0.
- `docs/`: guías y diagramas generados, con sus especificaciones y recibos.
