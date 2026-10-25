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

## Versiones de las skills

Cada skill de `src/<skill>/` se versiona por separado con SemVer `MAJOR.MINOR.PATCH`. La versión vive en el frontmatter de su `SKILL.md` y es la fuente de verdad:

```yaml
metadata:
  version: "1.0.0"
```

- `PATCH`: correcciones, aclaraciones y ajustes compatibles.
- `MINOR`: capacidades o instrucciones nuevas compatibles.
- `MAJOR`: cambio incompatible del contrato o del comportamiento esperado del agente.
- Un cambio del repositorio que no altera una skill no cambia su versión.

Las skills de terceros fijadas en `.skills/` no usan este versionado: se actualizan sustituyendo el directorio por otra revisión.

### Consultar y preparar un incremento

```bash
python scripts/version-skill.py list
python scripts/version-skill.py show <skill>
python scripts/version-skill.py bump <skill> <patch|minor|major> [--dry-run]
```

`list` muestra la versión declarada, la última publicada y el estado. `bump` actualiza solo `metadata.version`, preserva el resto del frontmatter y del contenido, y se niega a repetir una etiqueta existente o a reducir la versión. Si no puede comprobar las etiquetas, se detiene. No ejecuta `git commit`, `git tag` ni `git push`.

Una versión declarada sin etiqueta está en desarrollo. `python scripts/check-repo.py` acepta esa situación, pero rechaza una versión declarada menor que la última publicada, versiones o etiquetas mal formadas y etiquetas de skills que no existen en `src/`. La validación solo considera etiquetas con la forma `<skill>/v...`; cualquier otra queda fuera de su ámbito. Si Git no está disponible, avisa y no puede comprobar las etiquetas; no las da por inexistentes. En un clon superficial avisa de que pueden faltar, y `bump` se detiene.

### Publicar

La etiqueta `<skill>/v<MAJOR.MINOR.PATCH>` marca el commit integrado que publica esa versión. Git asocia la etiqueta al repositorio completo, no a la carpeta de la skill; el commit contiene todas las skills tal como estaban en ese momento. Las etiquetas publicadas son inmutables: una corrección se publica con una versión nueva.

1. `python scripts/version-skill.py bump <skill> <patch|minor|major>`.
2. `python scripts/check-repo.py` y `python scripts/test-version-skill.py`.
3. Revisar el diff: `git diff -- src/<skill>/SKILL.md` debe contener solo la línea de versión.
4. Integrar el cambio con el flujo de este documento.
5. Crear la etiqueta sobre el commit integrado, con autorización: `git tag <skill>/v<versión> <commit>`.
6. Publicar la etiqueta, con autorización: `git push origin <skill>/v<versión>`.

### Recuperar una versión publicada

```bash
git show <skill>/v<versión>:src/<skill>/SKILL.md
git worktree add ../<skill>-<versión> <skill>/v<versión>
```

El primer comando lee el contrato de esa versión. El segundo abre el repositorio completo en ella, porque la etiqueta no apunta a una skill aislada. El historial del repositorio sigue en `CHANGELOG.md`; no hay changelog por skill.

## Remoto

Crear un remoto, publicar o hacer `push` es una operación aparte, con su propio plan y su confirmación.

## Ficheros de raíz

- `README.md`: qué es el repositorio y cómo se usa una skill.
- `CHANGELOG.md`: historial del repositorio, con las categorías de Keep a Changelog y sin secciones de versión; qué cambió entre dos versiones de una skill lo responde el historial de Git.
- `BACKLOG.md`: trabajo pendiente priorizado; es la única lista de planificación del repositorio.
- `.gitattributes`: fin de línea del repositorio. Todo texto viaja en LF (`* text=auto eol=lf`); lo que se compara byte a byte se declara con `-text`.
- `docs/`: guías y diagramas generados, con sus especificaciones y recibos.
