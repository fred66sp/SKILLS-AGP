# Comandos y opciones de playwright-cli

Se abre al construir la secuencia de comandos de una sesión ya confirmada. Refleja la superficie del CLI publicado en la documentación oficial de Playwright; ante duda, manda `playwright-cli --help <comando>`.

## Superficie principal

| Comando | Uso |
|---|---|
| `open [url]` | Abre el navegador; `--headed` lo muestra, `--browser=chrome\|firefox\|webkit\|msedge`, `--mobile`, `--device="iPhone 15"`, `--persistent`, `--profile=<ruta>`, `--config=<fichero>` |
| `attach [nombre]` | Se adjunta a un navegador en marcha; `--extension` usa las pestañas del navegador del usuario |
| `close` / `detach` | Cierra lo lanzado / se separa sin cerrar lo ajeno |
| `goto <url>` | Navega a una URL |
| `type <texto>` | Escribe en el elemento editable con foco |
| `click <destino> [botón]`, `dblclick`, `hover`, `check`, `uncheck` | Interacción por ref, selector CSS o locator de Playwright |
| `fill <destino> <texto>` | Rellena un campo editable |
| `select <destino> <valor>` | Elige una opción de un desplegable |
| `press <tecla>`, `keydown`, `keyup` | Teclado |
| `upload <ficheros...>` | Sube ficheros |
| `snapshot [destino]` | Captura el árbol de accesibilidad; `--filename`, `--depth`, `--boxes` |
| `find [texto]` / `find --regex <patrón>` | Busca en el snapshot y devuelve coincidencias con contexto |
| `eval <función> [destino]` | Ejecuta JavaScript en la página o en un elemento |
| `dialog-accept [texto]` / `dialog-dismiss` | Resuelve un diálogo abierto |
| `resize <ancho> <alto>` | Redimensiona la ventana |
| `go-back`, `go-forward`, `reload` | Historial y recarga |
| `tab-list`, `tab-new [url]`, `tab-close [índice]`, `tab-select <índice>` | Pestañas |
| `screenshot [destino]`, `pdf` | Captura o PDF de la página o de un elemento |
| `console [nivel]` | Mensajes de consola |
| `requests`, `request <índice>`, `request-headers`, `request-body`, `response-headers`, `response-body` | Red observada |
| `route <patrón>`, `route-list`, `unroute [patrón]`, `network-state-set <estado>` | Interceptar y simular red |
| `state-save [fichero]`, `state-load <fichero>` | Guardar y restaurar cookies y almacenamiento |
| `cookie-*`, `localstorage-*`, `sessionstorage-*` | Leer y escribir almacenamiento del navegador |
| `run-code [código]` | Ejecuta un fragmento de Playwright |
| `generate-locator <destino>`, `highlight [destino]` | Propone un locator y resalta el elemento |
| `tracing-start`, `tracing-stop`, `video-start`, `video-stop`, `show` | Traza, vídeo y panel de sesiones |
| `install [--skills]`, `install-browser [navegador]` | Inicializa el espacio e instala navegadores |
| `list`, `close-all`, `kill-all` | Sesiones: listar, cerrar todas, matar las que no responden |
| `delete-data` | Borra los datos de perfil de la sesión |

## Opciones globales

| Opción | Efecto |
|---|---|
| `-s=<nombre>`, `--session=<nombre>` | Ejecuta contra una sesión con nombre |
| `--raw` | Imprime solo el valor, sin estado de página ni snapshot; es lo que permite redirigir a fichero |
| `--json` | Envuelve la respuesta en JSON; úsalo solo si se va a parsear |
| `--help [comando]`, `--version` | Ayuda y versión |
| `config-print` | Muestra la configuración resuelta tras fusionar ficheros, entorno y opciones |

## Snapshots y refs

Cada comando devuelve la URL, el título y la ruta del snapshot. El snapshot es un árbol de accesibilidad con refs `e<n>` en los elementos interactivos. El ref es único dentro de un snapshot y caduca con el siguiente cambio de página.

```bash
playwright-cli find "Add to cart"          # más barato que capturar todo
playwright-cli snapshot --depth=4          # primero una vista superficial
playwright-cli snapshot e34                # después el subárbol que interesa
playwright-cli --raw snapshot > antes.yml  # a fichero, no a la conversación
diff antes.yml despues.yml
```

Los selectores CSS y los locators de Playwright (`getByRole`, `getByTestId`, `getByText`) también se aceptan como destino, pero un ref observado suele ser más fiable que un selector inventado.

## Sesiones y perfiles

- Por defecto el perfil vive en memoria: las cookies sobreviven entre comandos y desaparecen al cerrar.
- `--persistent` guarda el perfil en disco; `--profile=<ruta>` elige el directorio. Es estado que sobrevive y puede mezclar cuentas.
- `PLAYWRIGHT_CLI_SESSION` fija la sesión por defecto en un proceso.
- El directorio de salida por defecto es `.playwright-cli/`; se cambia con `outputDir` en la configuración.

## Configuración

Se fusiona, en este orden: `~/.playwright/cli.config.json`, `.playwright/cli.config.json` del espacio de trabajo, variables `PLAYWRIGHT_MCP_*` y opciones de línea de comandos. `config-print` muestra el resultado. Los ajustes útiles para proporcionalidad son `snapshot.mode`, `snapshot.boxes`, `outputDir`, `outputMaxSize`, `timeouts` y `network.allowedOrigins`.

## Instalación

```bash
npm install -g @playwright/cli
playwright-cli --version
playwright-cli install --skills      # copia la skill oficial en .claude/skills/
playwright-cli install-browser       # descarga los binarios de navegador
```

La skill oficial que instala el CLI cubre los detalles de cada comando. Este paquete no la sustituye: añade la puerta de confirmación, el criterio de coste y la evidencia. Instalar el CLI, los navegadores o la skill son operaciones de máquina y requieren su propia confirmación.
