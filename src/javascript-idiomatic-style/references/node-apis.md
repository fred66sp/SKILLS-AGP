# APIs de Node

Léela en el paso 4 cuando el código se ejecute en Node: ficheros, streams, argumentos, variables de entorno, señales o una CLI sin dependencias.

## 1. Builtins

- Los builtins se importan con prefijo `node:` (`node:fs/promises`, `node:path`, `node:process`). Sin prefijo se confunden con paquetes y se rompe el análisis estático.
- El código compartido con el navegador no importa builtins. Si necesita una capacidad del sistema, la recibe por parámetro o detrás de un adaptador.
- `node:path` para rutas de fichero; `URL` para direcciones. No se concatena con `"/"` a mano.
- `node:os` expone `tmpdir()` y `homedir()`: se usan en lugar de rutas fijas.

## 2. Ficheros

```js
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { join } from "node:path";

const texto = await readFile(join(dir, "datos.json"), "utf8");
const datos = JSON.parse(texto);
```

- `node:fs/promises` en código asíncrono. La variante síncrona solo en el arranque o en un script cuyo único trabajo es leer algo pequeño.
- `readFile` con `"utf8"` devuelve cadena; sin codificación devuelve `Buffer`. Elige de forma explícita.
- `writeFile` sobrescribe. Para una escritura que no debe perder datos, se escribe en un temporal y se renombra con `rename`.
- `mkdir(dir, { recursive: true })` es idempotente; no compruebes la existencia antes de crear.
- `path.join` para unir, `path.resolve` para absoluto, `path.relative` para mostrar. `fileURLToPath(import.meta.url)` cuando la ruta nace de un módulo ESM.
- `JSON.parse` no valida: devuelve lo que diga el texto. Un fichero de configuración se valida antes de usarlo.
- Los errores de `fs` traen `code` (`ENOENT`, `EACCES`, `EEXIST`). Se distingue por `code`, no por el mensaje.

## 3. Streams

- `for await (const trozo of stream)` para consumir; `pipeline(a, b, c)` para encadenar con manejo de errores y cierre.
- `pipeline` de `node:stream/promises` cierra y libera los recursos si algo falla. Encadenar con `.pipe()` deja fugas en el error.
- Un stream que se crea se consume o se destruye. Un `readable` sin consumidor mantiene el proceso vivo.
- La contrapresión es del consumidor: no se acumula en memoria un fichero entero para luego partirlo.
- Para leer líneas, `readline` sobre el stream; no partir por `"\n"` después de leer todo.

## 4. Proceso: `argv`, `env` y salida

| Necesidad | Construcción |
|---|---|
| Argumentos propios | `process.argv.slice(2)` |
| Parseo sin dependencias | `parseArgs` de `node:util` |
| Variables de entorno | `process.env.NOMBRE`, validadas al arrancar |
| Resultado | `process.stdout.write` o `console.log` |
| Diagnóstico | `process.stderr.write` o `console.error` |
| Código de salida | `process.exitCode = 1` |
| Fin ordenado | Dejar que el proceso termine solo |

- `process.exit()` trunca la salida y salta la limpieza. Se usa `process.exitCode` y se deja terminar; `exit` solo en una parada dura demostrada.
- Una variable de entorno ausente que es obligatoria falla al arrancar con un mensaje que nombra la variable. No se le da un valor por defecto silencioso a un secreto.
- Un flag desconocido es un error de uso, no un aviso: se informa en `stderr` y se sale con `2`.
- La salida legible va a `stdout`; el progreso y los errores a `stderr`, para que una tubería no se contamine.
- `process.cwd()` es el directorio desde el que se invoca, no el del módulo. Una ruta por defecto se resuelve contra `cwd` de forma explícita.

## 5. Señales y cierre

- `SIGINT` y `SIGTERM` se manejan cuando hay algo que cerrar: ficheros, conexiones, temporales.
- El manejador hace la limpieza mínima, registra y deja terminar con el código adecuado. Un segundo `SIGINT` puede forzar la salida.
- El `AbortController` del proceso conecta la señal con las operaciones en curso para que se cancelen, no solo para que el proceso muera.
- Un `setInterval` o un servidor mantiene vivo el proceso: si el script debe terminar, se limpia o se llama a `unref()`.

## 6. CLI sin dependencias

```js
import { parseArgs } from "node:util";

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    help: { type: "boolean", short: "h" },
    json: { type: "boolean" },
    out: { type: "string" },
  },
});
```

- `parseArgs` cubre flags cortos, largos, valores y posicionales. No añadas un parser para tres flags.
- `--help` enumera los comandos y flags reales; se mantiene a mano junto a las opciones declaradas.
- `--json` devuelve una estructura con sobre de éxito o de error y no mezcla texto libre.
- `--dry-run` informa de lo que haría sin escribir; `--yes` es obligatorio en una operación destructiva.
- El modo no interactivo se detecta con `process.stdin.isTTY` y nunca se bloquea esperando entrada.
- Un comando idempotente puede repetirse sin daño; si no lo es, lo dice.

## 7. Paquetes y `exports`

- Un paquete declara `"type": "module"` si su `.js` es ESM, y entonces el punto de entrada es ESM.
- `exports` cierra la API: lo no listado deja de importarse. Se revisa con un consumidor real.
- `imports` (`"#interno/*"`) para rutas internas compartidas, en lugar de relativas largas.
- `engines` declara la versión de Node esperada y se contrasta con el CI. Es una advertencia para el instalador, no una garantía: el código comprueba lo que necesita.
- `bin` apunta a un fichero con shebang `#!/usr/bin/env node` y permisos de ejecución.

## 8. Diagnóstico y trampas

| Síntoma | Causa | Corrección |
|---|---|---|
| El proceso no termina | Timer, stream o servidor vivo | Limpiar o `unref()` |
| La salida se corta | `process.exit` antes de vaciar | `process.exitCode` y dejar terminar |
| `ERR_MODULE_NOT_FOUND` en ESM | Extensión ausente o ruta sin `file://` | `./archivo.js` y `fileURLToPath` |
| `require is not defined` | ESM | `import` o `createRequire` |
| Los datos del fichero son `undefined` | `JSON.parse` sin validar | Validar en la frontera |
| Una variable de entorno llega vacía | Ausente, no vacía | Comprobar `undefined`, no falsy |
- `console.log` en una CLI es salida; en una librería es ruido. La librería no escribe en la salida del consumidor.
- `process.on("uncaughtException")` no sustituye a manejar el error: el estado del proceso ya no es fiable.
- Un `debugger` o un `console.log` de depuración no se entrega en el diff.
