# Reglas de una CLI de TypeScript

Léela en el paso 5 antes de estructurar comandos, prompts, completion o empaquetado. La validación de entradas, las pruebas y la puerta de CI pertenecen a `typescript-testing-and-verification`.

## 1. Contrato observable

| Canal | Contenido |
|---|---|
| `stdout` | Resultado pedido, en texto o JSON |
| `stderr` | Progreso, diagnóstico y errores |
| Código de salida | `0` éxito; `1` fallo de ejecución; `2` uso incorrecto |

- Un flag desconocido o un argumento inválido termina en `2` antes de ejecutar efectos.
- `--help` en la raíz y en cada comando; `--version` solo en la raíz.
- Modo no interactivo cuando no hay TTY, cuando se pasa `--json` o cuando el agente lo pide. Nunca esperes una respuesta que no puede llegar.
- Toda operación destructiva exige `--yes` o una confirmación explícita; `--dry-run` describe el efecto sin aplicarlo.
- El resultado JSON es estable y va solo a `stdout`. El diagnóstico no contamina el documento.

## 2. Comandos con citty

```ts
import { defineCommand, runMain } from "citty";

export default defineCommand({
  meta: { name: "greet", description: "Saluda a una persona" },
  args: {
    name: { type: "string", description: "Nombre", required: true },
    json: { type: "boolean", description: "Salida JSON", default: false },
  },
  run({ args }) {
    const result = { greeting: `Hola, ${args.name}` };
    console.log(args.json ? JSON.stringify(result) : result.greeting);
  },
});
```

- Cada comando exporta por defecto `defineCommand()`. No hay comandos que devuelvan una forma distinta.
- Los subcomandos se cargan de forma perezosa: `() => import("./cmd").then((m) => m.default)`.
- Citty parsea los argumentos. No añadas un segundo parser ni leas `process.argv` a mano salvo para el gate de completion.
- Declara `meta.name`, `meta.description` y los `args` con descripción; la ayuda es el mecanismo de descubrimiento.
- Un comando con lógica reutilizable delega en una función pura y testeable; `run` solo cablea.
- La estructura `cli/` con `commands/`, `prompts/` y `lib/` es opcional. Un solo fichero es válido hasta que el número de comandos justifique separar. No impongas la estructura si no se pidió.

## 3. Prompts y cancelación

- Usa `@clack/prompts` para la interacción; no inventes un lector de líneas propio.
- Comprueba `isCancel()` después de **cada** llamada. Una cancelación termina con el código y el mensaje que el contrato declare; no continúa con un valor vacío.
- Un prompt nunca es la única forma de pasar un dato: acepta flags equivalentes para el modo no interactivo.
- Separa la recogida de datos de la ejecución. La función que ejecuta recibe valores ya validados.
- No muestres secretos en el prompt ni en el historial de shell. Si el dato es sensible, léelo de una variable de entorno o de un fichero con permisos.

## 4. Completion

- Activa el adaptador de `@bomb.sh/tab` solo cuando `process.argv[2] === "complete"`. El adaptador resuelve los subcomandos perezosos y arruina el arranque si se carga siempre.
- No importes los comandos de forma eager para generar la completion.
- Documenta la instalación por shell; no escribas en el perfil del usuario sin pedirlo.
- En el arranque normal, el coste de completion debe ser cero.

## 5. Progreso y TTY

- Un spinner o una barra de progreso solo si la operación puede tardar y la salida no es JSON.
- El progreso va a `stderr`; el resultado, a `stdout`. Así una tubería no se rompe.
- Si no hay TTY, desactiva animaciones y escribe líneas simples o nada.
- No uses artefactos de terminal que oculten el error final. Al terminar, deja el diagnóstico legible y el código de salida correcto.
- Para regiones dinámicas o layouts usa `@bomb.sh/tty` solo cuando el proyecto ya lo tenga o la necesidad lo justifique; un spinner de `@clack/prompts` suele bastar.

## 6. Entrada y build

- Declara `bin` en `package.json` apuntando al fichero construido, con shebang `#!/usr/bin/env node`.
- Publica el artefacto compilado, no `src/`; incluye los tipos y el mapa de declaraciones si la CLI exporta API.
- Las dependencias de ejecución van en `dependencies`; las de build y test, en `devDependencies`. No exijas una devDependency en runtime.
- Si distribuyes un binario único, verifica que el binario arranca sin `node_modules` y que la versión que reporta coincide con el paquete.
- El `packageManager` de `package.json` y el lockfile deben coincidir con el gestor que usa CI.

## 7. Entrega

- Versiona con SemVer y un registro de cambios; un cambio incompatible de flags o de formato JSON sube la major.
- Elige un mecanismo y no dos: Changesets o release-please. La versión se deriva del registro, no se teclea a mano en dos sitios.
- La puerta de CI la posee `typescript-testing-and-verification`: typecheck, lint, test, build y prueba de humo del binario.
- Antes de publicar, comprueba `--help`, `--version`, un comando desconocido y una ejecución no interactiva.
- No publiques desde una máquina con cambios sin preparar. La publicación es una operación aparte, con su confirmación.

## 8. Lista rápida de CLI

- [ ] Cada comando exporta `defineCommand()` y declara `meta` y `args`.
- [ ] Subcomandos perezosos y completion detrás de `argv[2] === "complete"`.
- [ ] `isCancel()` después de cada prompt.
- [ ] Modo no interactivo, `--dry-run` y `--yes` donde corresponda.
- [ ] Resultado en `stdout`, diagnóstico en `stderr`, códigos `0/1/2`.
- [ ] `--help` en raíz y comandos; `--version` en la raíz.
- [ ] `bin`, shebang, artefacto compilado y dependencias de runtime correctas.
- [ ] Estructura `cli/` solo si el tamaño la justifica.
- [ ] Versionado y registro de cambios con un único mecanismo.
