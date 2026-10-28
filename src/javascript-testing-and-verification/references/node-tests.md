# Pruebas en Node

Léela en el paso 3 cuando la capa sea `node:test` o la ejecución de un proceso.

## 1. Estructura y descubrimiento

```js
// src/precio.test.js
import test from "node:test";
import assert from "node:assert/strict";
import { totalPedido } from "./precio.js";

test("totalPedido suma líneas y aplica el descuento", () => {
  const pedido = { lineas: [{ precio: 100, cantidad: 2 }], descuento: 50 };
  assert.equal(totalPedido(pedido), 150);
});
```

- `node --test` descubre `*.test.js`, `*-test.js`, `test.js` y los archivos dentro de `test/`.
- El archivo vive junto al módulo; si el proyecto ya agrupa en `test/`, se respeta.
- No hace falta configuración, dependencia ni script para empezar: `node --test`.
- `package.json` con script `test` sigue mandando cuando existe; la puerta lo ejecuta.

## 2. Aserciones

| Necesidad | Aserción |
|---|---|
| Igualdad estricta | `assert.equal` (usa `===`) o `assert.strictEqual` |
| Igualdad profunda | `assert.deepEqual` / `assert.deepStrictEqual` |
| Verdadero | `assert.ok(valor, "mensaje")` |
| Lanza | `assert.throws(fn, /mensaje/)` |
| No lanza | `assert.doesNotThrow(fn)` |
| Rechaza | `await assert.rejects(promesa, /mensaje/)` |

- Importa `node:assert/strict`: todas las igualdades pasan a estrictas sin escribir `strict` en cada llamada.
- Todo `assert.ok` lleva mensaje: sin él, el fallo no dice qué se esperaba.
- `assert.equal(a, b, "esperaba b")` muestra `got` y `want`; es la forma más rápida de leer un fallo.
- Comprueba la forma del error (`code`, `name`) antes que el texto completo, que cambia con el runtime.

## 3. Agrupación y ciclo de vida

- `describe`/`it` para agrupar por comportamiento; `test` suelto cuando el archivo es pequeño.
- `before`, `after`, `beforeEach`, `afterEach` para estado compartido del grupo.
- Un `beforeEach` que crea el objeto bajo prueba evita que un test herede la mutación de otro.
- `t.after` o `t.afterEach` para lo que se abre dentro del test: temporales, servidores, listeners.
- `test.skip` solo con motivo escrito; una prueba omitida no cuenta como cobertura.

## 4. Asincronía y tiempo

- Un test `async` se espera solo; `node --test` no deja promesas sueltas.
- `await` la operación real; no `setTimeout` para «dar tiempo».
- Temporizadores simulados:

```js
test("reintenta tras 100 ms", (t) => {
  t.mock.timers.enable({ apis: ["setTimeout"] });
  const intentos = [];
  const p = reintentar(() => intentos.push(Date.now()), { espera: 100 });
  t.mock.timers.tick(100);
  return p.then(() => assert.equal(intentos.length, 1));
});
```

- Un test que abre un intervalo o un servidor sin cerrarlo deja el proceso vivo: ciérralo en `after`.
- `AbortSignal.timeout` también se simula; no esperes el plazo real.

## 5. Dobles

| Frontera | Cómo se dobla |
|---|---|
| Función propia | Se pasa como parámetro; si no, `t.mock.fn()` |
| Módulo completo | `t.mock.module()` solo con `--experimental-test-module-mocks`; si no, se inyecta la dependencia por parámetro |
| `fetch` | Se sustituye `globalThis.fetch` en el test y se restaura en `finally` |
| Ficheros | Directorio temporal real; no hace falta simular `fs` |
| `process.env` | Se asigna y se restaura en `finally` |
| Reloj | `t.mock.timers` |

- Se dobla la frontera, no el módulo bajo prueba.
- El doble devuelve lo que el contrato promete, incluidos los errores: `{ ok: false, status: 500 }`.
- Restaura siempre: un `globalThis.fetch` sustituido contamina el resto de la suite.
- `t.mock.fn()` registra llamadas; se comprueba el efecto observable, no que el doble fue llamado por llamarse.

## 6. Probar un proceso

```js
import { execFile } from "node:child_process";
import { promisify } from "node:util";
const run = promisify(execFile);

test("--json devuelve un sobre de error con código 2", async () => {
  await assert.rejects(
    run(process.execPath, ["cli.js", "--json"], { env: { ...process.env, NADA: "" } }),
    (error) => {
      assert.equal(error.code, 2);
      assert.match(error.stderr, /"ok": false/);
      return true;
    }
  );
});
```

- Se ejecuta `process.execPath` con el archivo, no el binario global.
- `argv`, `env` y `stdin` se controlan por caso; el entorno heredado se copia y se modifica.
- Se comprueban `stdout`, `stderr` y código de salida por separado.
- Un JSON se parsea y se comprueba su forma; no se compara el texto entero.
- Un proceso que debe terminar se prueba con un límite de tiempo; si no termina, el test falla.

## 7. Salida y diagnóstico

- `--test-reporter spec` para leer el detalle; `--test-reporter tap` para una máquina.
- Un fallo muestra el archivo, la línea y la aserción; si no, el mensaje de la aserción es el que falta.
- Ejecuta el archivo aislado (`node --test src/precio.test.js`) antes de culpar a la suite.
- Dos ejecuciones seguidas: si la segunda falla, hay estado compartido o un temporal sin cerrar.

## 8. Trampas

| Síntoma | Causa | Corrección |
|---|---|---|
| El test pasa sin ejecutar la aserción | `expect` sin `await` o promesa no devuelta | Devolver o esperar la promesa |
| Pasa solo | Estado compartido entre tests | Estado por test |
| Falla por fecha | Reloj real | Reloj inyectado o simulado |
| El proceso no termina | Intervalo, servidor o stream abierto | Cerrar en `after` |
| El mock queda activo en el siguiente test | Sin restaurar | `finally` o `t.after` |
| `deepStrictEqual` falla por prototipos | Objetos de distinta clase | Comparar datos o usar `deepEqual` |
