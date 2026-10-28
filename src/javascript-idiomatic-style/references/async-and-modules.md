# Asincronía y módulos

Léela en el paso 4, antes de escribir flujos asíncronos o de decidir cómo se importa y se exporta.

## 1. Promesas

- Una promesa se crea con `new Promise` solo al envolver una API de callback. Lo demás se escribe con `async`.
- `Promise.all` cuando todas deben completarse y el fallo de una invalida el conjunto.
- `Promise.allSettled` cuando cada resultado se informa por separado.
- `Promise.any` para la primera que tenga éxito; `Promise.race` para la primera que termine, con éxito o error.
- `Promise.resolve(valor)` y `Promise.reject(err)` para adaptar, no para envolver una promesa que ya existe.
- Un rechazo sin observador no es un estilo: es una pérdida silenciosa. Se observa en el punto donde se puede decidir algo.

## 2. `async` y `await`

```js
async function leerUsuario(id, { signal } = {}) {
  const respuesta = await fetch(`/api/usuarios/${id}`, { signal });
  if (!respuesta.ok) throw new Error(`HTTP ${respuesta.status}`);
  return respuesta.json();
}
```

- `await` dentro de `try/catch` cuando el fallo se puede manejar; sin `try` cuando debe propagarse y el llamador decide.
- No se anida `try` para cada línea: un `try` por unidad de trabajo con recuperación.
- `return await` solo dentro de un `try` que captura; fuera, `return promesa` y deja que el llamador espere.
- Un bucle con `await` secuencial es correcto si el orden importa. Si no importa, `Promise.all` sobre un `map`.
- Una función `async` que no espera nada debería ser síncrona.

## 3. Errores en asincronía

| Situación | Qué se escribe |
|---|---|
| Fallo esperado del dominio | `Error` propio con `cause` cuando envuelve otro |
| Fallo de la API remota | Comprobar `respuesta.ok`; `fetch` no rechaza por HTTP 4xx o 5xx |
| Cuerpo no JSON | `respuesta.json()` rechaza; se maneja con el mismo `try` |
| Rechazo en un callback no esperado | `.catch()` en la cadena o `await` en el nivel superior |
| Última red | `process.on("unhandledRejection")` o `unhandledrejection` en el navegador, que registra y termina |

Un error propio conserva la pila y el mensaje original: `throw new Error("no se pudo leer el pedido", { cause: err })`. No se reescribe el mensaje de un error ajeno sin motivo.

## 4. Cancelación

- Toda operación que pueda abandonarse acepta `signal` y lo pasa hacia dentro: `fetch`, `setTimeout` de `node:timers/promises`, streams, `AbortSignal.any`.
- Un plazo se expresa con `AbortSignal.timeout(ms)`, no con un `setTimeout` que aborta a mano.
- Varias fuentes de cancelación se combinan con `AbortSignal.any([a, b])` cuando el baseline lo permite; si no, se propaga el que ya exista.
- Al cancelar se distingue `AbortError` de un fallo real: `if (err.name === "AbortError") return;` y no se registra como error.
- El `AbortController` se crea donde se conoce el ciclo de vida y se pasa; no se crea uno por llamada si la cancelación es del conjunto.

## 5. Orden del event loop

| Cola | Qué entra | Consecuencia |
|---|---|---|
| Microtareas | `await`, `.then`, `queueMicrotask` | Se vacía antes de la siguiente macrotarea |
| Macrotareas | `setTimeout`, I/O, eventos | Se ejecuta después de las microtareas |
| Render | Navegador, tras las microtareas | Un `await` no bloquea el pintado |

- Un `await` cede el control: el código que sigue no se ejecuta en el mismo turno. No se asume orden entre dos ramas asíncronas independientes.
- Un bucle que procesa muchos elementos con `await` cede en cada iteración; si compite por un recurso, se limita la concurrencia.
- `setTimeout(fn, 0)` no es «inmediato»: es una macrotarea. Para ceder sin esperar, `await null` o `queueMicrotask`.
- No se sincroniza con `sleep` ni con esperas arbitrarias. Si algo necesita tiempo, se espera el evento que lo señala.

## 6. ESM

```js
import { readFile } from "node:fs/promises";
import { crearPedido } from "./pedidos.js";

export function totalPedido(pedido) { /* ... */ }
export const LIMITE = 100;
```

- `import` es estático y se resuelve antes de ejecutar. Permite análisis y tree shaking; no admite una ruta calculada.
- `import()` devuelve una promesa y sirve para carga condicional o diferida: `const { parse } = await import("./parser.js")`.
- Los enlaces ESM son vivos: un módulo ve el valor actualizado de lo que importa.
- `export default` para una pieza única; nombrados para lo demás. Un `default` que mezcla varias cosas rompe el descubrimiento.
- En ESM no existe `__dirname` ni `require`. Se usa `import.meta.url`, `import.meta.dirname` cuando el runtime lo admite, o `import.meta.resolve`.
- El punto de entrada de un paquete declara `"type": "module"` para que `.js` sea ESM.
- Un módulo no debe tener efectos secundarios al importarse: registrar listeners o abrir ficheros al cargar hace que el orden importe.

## 7. CJS y compatibilidad

- `require` es síncrono y cachea por ruta resuelta; `module.exports` y `exports.nombre` son el mismo objeto al inicio, pero reasignar `exports` rompe la referencia.
- Un paquete CJS puede importar ESM con `import()` dinámico; un paquete ESM no puede `require` un ESM sin ayuda del runtime.
- No se mezclan `require` e `import` en el mismo archivo. La excepción es el `import()` dinámico, que es válido en CJS.
- `__dirname`, `__filename` y `require` son de CJS; en ESM se derivan de `import.meta.url`.
- Un proyecto que migra de CJS a ESM cambia `type`, extensiones y resolución; es un cambio propio, no un arreglo de paso.

## 8. Módulos en `package.json`

| Campo | Qué decide | Regla |
|---|---|---|
| `type` | Si `.js` es ESM o CJS | Se declara una vez, en la raíz |
| `main` | Entrada para `require` | Solo si el paquete sigue siendo CJS |
| `exports` | Mapa de rutas públicas y condiciones | Explícito; sin filtrar rutas internas |
| `imports` | Alias internos con `#` | Para rutas internas compartidas |
| `engines` | Versión de Node esperada | Coherente con el baseline declarado |

- `exports` sustituye a `main` cuando existe: una ruta no listada deja de ser importable. Es el mecanismo para cerrar la API del paquete.
- Un `exports` mal formado falla con `ERR_PACKAGE_PATH_NOT_EXPORTED`; se comprueba con un consumidor real, no solo con el propio paquete.
- Las condiciones (`import`, `require`, `browser`, `node`) se declaran solo si el paquete se publica para varios entornos; en una aplicación no aportan.
- El orden de las condiciones importa: la primera que coincide gana.
