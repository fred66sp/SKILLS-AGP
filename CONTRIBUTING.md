# Flujo de trabajo Git

Política de este repositorio. Prevalece sobre cualquier Git Flow genérico: no se crean ramas, etiquetas ni reglas de merge que no estén aquí.

## Modelo

- `main` es la única rama de larga vida. Contiene lo que está listo para usarse.
- No hay `develop`, `release/*` ni `hotfix/*`. Introducirlos exige cambiar esta política antes.

## Unidad de trabajo

Antes de proponer una skill nueva, se decide qué unidad resuelve la necesidad. La escalera va de menos a más coste y se toma la primera que cubre el caso hoy, no la que cubría un caso hipotético mañana.

| Unidad | Cuándo corresponde | Qué arrastra |
|---|---|---|
| Nada | Problema puntual que no se repite. | Nada. |
| Instrucciones del agente | Comportamiento permanente, que debe aplicarse en cualquier proyecto. | El fichero de instrucciones de cada máquina. No es contenido publicable de este repositorio. |
| Script | Operación determinista: misma entrada, misma salida, sin criterio. | Fichero en `scripts/` o `src/<skill>/scripts/` con su prueba. |
| Skill | Conocimiento especializado que se necesita bajo demanda y con criterio. | Contrato en `src/<skill>/SKILL.md`, enrutador en `.skills/`, página en `docs/`, puerta con prueba si trae scripts. |
| Viaje (metaskill) | Recorrido con varias fases y decisiones humanas que hay que poder retomar en otra sesión. | No existe todavía: lo decide la tarea sk-5 del tablero. Mientras no exista, se invocan las skills en orden y el orden se documenta en la tarea. |

Dos reglas de aplicación:

- La escalera decide **qué se escribe**, no qué se usa primero: una necesidad real se cubre con la unidad más baja que la resuelva ya.
- Subir un peldaño se justifica con evidencia de que el inferior no cubre el caso. La anticipación de que quizá lo cubra más adelante no sube nada.

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
6. Antes de pedir esa confirmación se ha hecho el barrido previo: documentación, enrutadores (local y global si existe), `CHANGELOG`, plantillas y referencias describen ya lo que va a quedar en el repositorio.

Cualquier otra cosa entra por una rama corta. Ante la duda, rama.

## Tareas

El tablero tasks-ai de `.tasks-ai/` es el registro del trabajo pendiente y en curso; sustituye a `BACKLOG.md`, retirado. Se trabaja en una tarea por cambio y la tarea se crea antes de tocar ficheros. Al empezar, pasa a `in_progress`; los avances, las decisiones y los bloqueos van en comentarios en el momento en que surgen. El commit va antes que el cierre: el tablero no guarda estado de Git, así que no registra ramas, hashes ni si el cambio está publicado. Las órdenes están en [`.tasks-ai/AGENTS.md`](.tasks-ai/AGENTS.md) y las reglas de etiquetas en [`.tasks-ai/CONTRATO_ETIQUETAS.md`](.tasks-ai/CONTRATO_ETIQUETAS.md).

## Enrutadores de skills

Cada skill de `src/<skill>/` se descubre por su enrutador en `.skills/<skill>/SKILL.md`: metadatos de disparo y una instrucción para leer el contrato completo. Al cambiar una skill, revisa su enrutador en el mismo cambio:

- Si cambian los disparadores, el alcance, las referencias o los scripts, actualiza la descripción y las instrucciones del enrutador.
- El enrutador no copia reglas: si enrutador y contrato difieren, manda el contrato. Corrige el enrutador.
- La ruta al contrato es relativa a la carpeta del enrutador (`../../src/<skill>/SKILL.md`). `python scripts/check-repo.py` comprueba el nombre, esa ruta y que no haya enrutadores huérfanos ni skills sin enrutador.

Si la skill tiene además un enrutador global en `~/.config/opencode/skills/<skill>/SKILL.md`, actualízalo también: misma descripción y mismo cuerpo, con la ruta absoluta a este repositorio y a su página de `docs/` si el enrutador local la menciona. Ese enrutador es estado local de la máquina: no se versiona, no es requisito para contribuir y `check-repo.py` no lo comprueba. Si existe y no se actualiza, el agente seguirá descubriendo la versión anterior de la skill. Las skills de terceros de `.skills/` no llevan enrutador global.

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
- `.tasks-ai/`: tablero del repositorio. Se versionan las instrucciones, el contrato de etiquetas y los ajustes; la base, el binario y las extensiones son estado local y `tasks-ai init` las restaura.
- `serve.sh`: servidor del tablero en segundo plano, en el puerto 8892, con pid y registro en `.run/`.
- `PRODUCT.md`: contexto de producto que lee el trabajo de diseño antes de tocar una interfaz: plataforma, usuarios, propósito, límites y las ausencias que no se deben rellenar.
- `DESIGN.md`: sistema visual del catálogo y de las páginas de skill. Los tokens del frontmatter son normativos y el cuerpo explica dónde se aplica cada uno.
- `.gitattributes`: fin de línea del repositorio. Todo texto viaja en LF (`* text=auto eol=lf`); lo que se compara byte a byte se declara con `-text`.
- `opencode.json`: configuración compartida de OpenCode, con los agentes y el modelo de cada uno; el estado local de OpenCode vive en `.opencode/` y no se versiona.
- `docs/`: guías y diagramas generados, con sus especificaciones y recibos. Las páginas de skill comparten `docs/assets/site.css` y `docs/assets/site.js`, y declaran su acento con `data-skill`.
