# Capas de prueba en TypeScript

Léela en los pasos 3 y 4 para elegir la capa y escribir el caso. El runner es el del proyecto; los ejemplos usan `node:test` porque no añade dependencias.

## 1. Elegir la capa en TypeScript

| Capa | Qué demuestra | Coste | Cuándo |
|---|---|---|---|
| Tipos | El contrato compila y las uniones son exhaustivas | Bajo | API pública y utilidades de tipos |
| Esquema | La frontera acepta lo válido y rechaza lo inválido | Bajo | Todo dato externo |
| Unitaria | Lógica, ramas, cálculo, transformación | Bajo | Siempre que haya lógica pura |
| Integración | Frontera real: fichero, proceso, HTTP local | Medio | Cuando el contrato cruza esa frontera |
| Extremo a extremo | Comando, flags, `stdout`, `stderr`, código de salida | Medio-alto | Contrato de la CLI |
| Snapshot | Salida estable y determinista | Medio | Solo formatos que deben permanecer estables |

No escribas la capa más alta para probar una función pura. No escribas solo la más baja cuando el requisito es «el comando sale con `2` sin `--yes`».

## 2. Tipos

- `tsc --noEmit` es la primera comprobación. Si falla, no hay nada más que verificar.
- Una API pública no trivial se fija con una prueba de tipos: `expectTypeOf` si el proyecto ya lo tiene, `tsd` si ya está configurado, o un fixture que solo compila si el tipo es correcto.
- No añadas un framework de tipos para una comprobación aislada. Un fichero `.test-d.ts` incluido en el `tsconfig` puede bastar.
- Prueba los casos negativos con `@ts-expect-error` acompañado de una razón; sin razón, la supresión oculta el problema.

## 3. Esquemas

```ts
import assert from "node:assert/strict";
import test from "node:test";
import * as z from "zod";

import { CreateOrder } from "../src/orders.js";

test("CreateOrder rejects an empty item list", () => {
  const result = CreateOrder.safeParse({
    customerId: "9f1c2f7e-1c2a-4b6e-8a7d-3f5b2c1d0e9a",
    email: "buyer@example.com",
    items: [],
    placedAt: "2026-01-01T00:00:00Z",
  });

  if (result.success) {
    assert.fail("expected validation to fail");
  }
  assert.deepEqual(z.flattenError(result.error).fieldErrors.items, [
    "Too small: expected array to have >=1 items",
  ]);
});
```

- Cubre válido, inválido y límite: `""`, `null`, ausente, tipo incorrecto, clave extra, número fuera de rango y cadena coercible.
- Comprueba la forma del error que consume el receptor, no el texto completo si el runner o la versión pueden cambiarlo.
- Prueba cada transformación y refinamiento por separado; los refinamientos no se ejecutan si la base falla.
- Prueba el caso asíncrono con `safeParseAsync`/`parseAsync`.
- Para entorno, prueba un proceso hijo con una variable ausente y otra inválida; comprueba mensaje y código de salida.

## 4. Lógica pura

```ts
const cases = [
  { name: "zero", input: 0, want: 0 },
  { name: "negative", input: -1, want: 0 },
  { name: "large", input: 10_000, want: 10_000 },
];

for (const { name, input, want } of cases) {
  test(`clamp: ${name}`, () => {
    assert.equal(clamp(input), want);
  });
}
```

- Usa tabla solo cuando todos los casos recorren el mismo camino. Si cada uno necesita montaje o dobles distintos, escribe pruebas separadas.
- Identifica el caso por nombre, no por índice. Muestra `got` y `want` en el mensaje.
- Una prueba debe fallar por una causa y explicar cuál. Un `assert.ok(result)` sin mensaje no es diagnóstico.
- No pruebes funciones privadas por reflejo. Prueba el comportamiento público que las usa.

## 5. Integración

- Sustituye la red real por un servidor local (`node:http`, MSW o `undici` MockAgent) y ciérralo en el `after`.
- Usa un directorio temporal y rutas absolutas; no dependas del directorio de trabajo del runner.
- Inyecta reloj, `fetch`, filesystem y generador de IDs. No uses `sleep` para esperar una condición.
- Si la prueba necesita una base de datos, usa una instancia efímera y limpia el estado antes de cada caso.
- Comprueba el efecto observable y el estado final; no solo que la llamada no lanzó.

## 6. CLI de extremo a extremo

```ts
import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import test from "node:test";

const run = promisify(execFile);

test("unknown command exits with usage code", async () => {
  await assert.rejects(
    run(process.execPath, ["dist/cli.js", "unknown"], { encoding: "utf8" }),
    (error: NodeJS.ErrnoException & { code?: number; stderr?: string }) => {
      assert.equal(error.code, 2);
      assert.match(error.stderr ?? "", /unknown command/i);
      return true;
    },
  );
});
```

- Construye el binario una vez. No compiles dentro de cada caso.
- Ejecuta con `process.execPath` y el fichero construido, o con el `bin` del paquete. No asumas que el shebang funciona en Windows.
- Captura `stdout` y `stderr` por separado. `execFile` los entrega en el error cuando el código no es cero; comprueba ambos.
- Cubre `--help`, `--version`, comando desconocido, flag desconocido, JSON válido, modo no interactivo, cancelación, `--dry-run` y falta de `--yes`.
- Prueba la cancelación enviando la señal o un `stdin` que simule la interrupción; comprueba que no queda un proceso hijo.
- Comprueba que un fallo no deja archivos parciales.

## 7. Determinismo

- Normaliza rutas absolutas, separadores `\` y `/`, timestamps, IDs y mensajes del sistema antes de comparar.
- Un snapshot solo se actualiza con una bandera explícita y el diff se revisa. Un cambio no explicado es una regresión.
- Ordena las claves de un objeto antes de serializarlo si el contrato no garantiza el orden.
- No dependas del orden de un `Set` o de un `Object.keys` para un resultado estable.
- Ejecuta la suite dos veces si sospechas no determinismo; no la reintentes hasta que pase.

## 8. Dobles de prueba

- Prefiere una dependencia inyectada a un mock global. El mock global contamina otros tests y oculta el acoplamiento.
- Si usas el mock del runner, restáuralo en `afterEach` y comprueba que se llamó con los argumentos esperados.
- No mockees el módulo que estás probando; mockea la frontera externa.
- Un doble debe fallar como fallaría el real: un `fetch` mockeado que nunca rechaza no prueba el manejo de errores.

## 9. Regresión

- Antes de corregir un defecto, escribe la prueba que falla por la causa. Comprueba que falla por la razón correcta.
- Después de la corrección, la prueba queda en la suite. No la borres porque ya pasa.
- Si el defecto estaba en la frontera, añade además el caso de esquema que lo habría rechazado.

## 10. Mapa de la puerta

| Comprobación | Comando | Cuándo |
|---|---|---|
| Tipos | `tsc --noEmit` o script `typecheck` | Siempre |
| Lint | Script `lint` del proyecto | Si existe |
| Test | Script `test` del proyecto | Siempre que haya suite |
| Build | Script `build` del proyecto | Antes de publicar o si el contrato lo exige |
| Versión única | `npm ls zod` o equivalente | Si se usa Zod |

La puerta completa se ejecuta con `python src/typescript-testing-and-verification/scripts/verify-ts.py --root . --test --lint --build`.

## 11. Lista rápida de pruebas

- [ ] `tsc --noEmit` pasa sin suprimir reglas.
- [ ] Cada frontera tiene pruebas de válido, inválido y límite.
- [ ] Los errores de esquema se comprueban por forma, no por texto volátil.
- [ ] La lógica pura tiene tabla o casos separados según el camino.
- [ ] La integración usa servidor local, directorio temporal y dependencias inyectadas.
- [ ] La CLI se prueba con `stdout`, `stderr` y código de salida separados.
- [ ] Snapshots deterministas y actualización explícita.
- [ ] Sin red real, reloj real ni `sleep`.
- [ ] Defecto corregido con prueba de regresión.
- [ ] La puerta se ejecutó y su salida está en el informe.
