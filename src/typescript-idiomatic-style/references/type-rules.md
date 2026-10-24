# Reglas de tipos, módulos y dependencias

Léela en los pasos 2 a 4 del procedimiento, cuando una decisión de tipos o de estructura no sea evidente.

## 1. `tsconfig`

| Opción | Qué garantiza | Cuándo |
|---|---|---|
| `strict` | Activa la familia estricta, incluido `strictNullChecks` | Siempre |
| `noUncheckedIndexedAccess` | Un índice devuelve `T \| undefined` | Proyectos nuevos y librerías |
| `exactOptionalPropertyTypes` | Distingue `?` de `\| undefined` | APIs donde la diferencia es contrato |
| `noImplicitOverride` | Obliga a marcar `override` | Código con clases |
| `isolatedModules` | Cada fichero se transpila aislado | Bundlers, esbuild, SWC, ts-node |
| `verbatimModuleSyntax` | Conserva los imports y exige `import type` | ESM moderno |
| `module` / `moduleResolution` | Resolución real del runtime | `NodeNext` en Node ESM; `Bundler` con bundler |
| `declaration` / `declarationMap` | Tipos publicables y navegables | Librerías |
| `skipLibCheck` | Omite la comprobación de `.d.ts` ajenos | `false` por defecto; `true` solo con motivo |
| `noEmit` | El typecheck no genera artefactos | Script `typecheck` de una app |

- Un solo `tsconfig` raíz; los paquetes lo extienden con `extends` y declaran solo lo que cambia.
- No desactives `strictNullChecks`, `noImplicitAny` ni `strictFunctionTypes` para un cambio puntual.
- `incremental` y las project references se añaden con una medición del build; no son parte de la plantilla mínima.
- El typecheck se ejecuta con `tsc --noEmit` o con el script `typecheck` del proyecto, nunca con el editor como única evidencia.

## 2. `unknown`, `any` y `as`

| Situación | Decisión |
|---|---|
| Entrada externa: HTTP, formulario, entorno, fichero, API de terceros | `unknown` y validación en la frontera |
| `JSON.parse` | Devuelve `unknown`; se valida antes de usarlo |
| `catch` | El error es `unknown`; se estrecha antes de leerlo |
| Genérico sin restricción | `unknown`, no `any` |
| Tipo de una dependencia rota | `any` local en un adaptador, con comentario y sin filtrarlo |
| Valor que ya cumple una invariante demostrada | `as` puntual y comentado |
| Literal que debe conservar su forma | `as const` o `satisfies` |

- `as unknown as T` oculta dos errores y no se acepta en código nuevo.
- Un `as` dentro de una función de construcción puede ser correcto si la función valida antes; fuera de ella, no.
- `@ts-ignore` se sustituye por `@ts-expect-error` con una razón, o se elimina. Una supresión sin fecha ni motivo es deuda invisible.

## 3. Modelar estados

```ts
type RequestState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: Error };

function render<T>(state: RequestState<T>): string {
  switch (state.status) {
    case "idle":
      return "En espera";
    case "loading":
      return "Cargando";
    case "success":
      return String(state.data);
    case "error":
      return state.error.message;
    default: {
      const exhaustive: never = state;
      return exhaustive;
    }
  }
}
```

| Decisión | Regla |
|---|---|
| Varios booleanos que se excluyen | Se sustituyen por una unión discriminada |
| Campo que puede faltar | `?` si la ausencia es válida; `\| null` si el contrato transporta `null` |
| `null` y `undefined` en el mismo campo | `\| null \| undefined` solo si ambos llegan de verdad; si no, normaliza en la frontera |
| Estados de carga | Unión con `status` literal, no `isLoading` + `error` + `data` |
| Conjunto cerrado de valores | Unión de literales o const object |

```ts
const Status = { Draft: "draft", Paid: "paid" } as const;
type Status = (typeof Status)[keyof typeof Status];
```

No uses `enum`: genera código en runtime, no se borra con `isolatedModules` en todos los casos y complica el contrato con JavaScript.

## 4. Tipos branded

Un brand impide mezclar valores que comparten representación. No valida: la validación ocurre en el constructor.

```ts
declare const userIdBrand: unique symbol;
export type UserId = string & { readonly [userIdBrand]: "UserId" };

export function toUserId(value: string): UserId {
  if (!value.startsWith("user_")) {
    throw new Error("UserId must start with user_");
  }
  return value as UserId;
}
```

- Crea el tipo branded cuando dos valores del mismo tipo primitivo no deben intercambiarse.
- Constrúyelo en un único módulo; no repartas `as UserId` por el código.
- Si el identificador se serializa, el tipo de transporte puede ser `string`; la conversión se hace al entrar y al salir.
- No crees un brand para cada `string`: solo para identificadores y cantidades con invariantes.

## 5. Type guards y `satisfies`

```ts
type ApiSuccess = { ok: true; data: unknown };
type ApiFailure = { ok: false; error: string };
type ApiResult = ApiSuccess | ApiFailure;

function isSuccess(result: ApiResult): result is ApiSuccess {
  return result.ok === true;
}

const routes = {
  home: "/",
  users: "/users",
  user: (id: string) => `/users/${id}`,
} satisfies Record<string, string | ((id: string) => string)>;
```

- Un predicado debe comprobar exactamente lo que afirma; si puede devolver `true` para un valor que no cumple `T`, es un cast disfrazado.
- Usa `satisfies` para validar tablas sin perder los literales; no anotes la tabla con un tipo ancho.
- Una assertion function (`asserts value is T`) solo es correcta si lanza cuando la condición falla.
- Estrecha con `typeof`, `in`, `instanceof` y `Array.isArray` antes de inventar un guard.

## 6. Genéricos y tipos calculados

| Necesidad | Decisión |
|---|---|
| Dos o más instancias reales con la misma forma | Genérico con restricción |
| Relación entre parámetro y retorno | Genérico, no `unknown` con casts |
| Un solo uso | Tipo concreto |
| Transformar un objeto | `Pick`, `Omit`, `Partial`, `Required`, `Record` |
| Aplanar promesas | `Awaited<T>` |
| Extraer parámetros o retorno | `Parameters<T>`, `ReturnType<T>` |
| Unión con todos los casos agotados | `never` en el `default` |
| Rutas o eventos con gramática finita | Template literal types |
| Texto arbitrario con reglas complejas | Validación en runtime, no tipos |

- No reimplementes un utility type de la biblioteca estándar. Si `Partial<T>` no expresa la intención, escribe un tipo con nombre y documéntalo.
- `DeepReadonly`, `RequireExactlyOne` y similares se añaden cuando la API los necesita; no como catálogo.
- Un tipo público no trivial se acompaña de una prueba de tipos (`expectTypeOf`, `tsd` o un fixture que solo compila si el tipo es correcto). No añadas un framework de tipos solo para una comprobación.
- Evita los tipos que obligan a leer tres niveles de condicionales. Si no se explican en una frase, la API está confusa.

## 7. Funciones y API

- Las funciones exportadas declaran el retorno. Los locales lo infieren.
- Prefiere un objeto de opciones a partir de tres parámetros o de dos booleanos seguidos.
- Acepta `readonly T[]` cuando no mutas la colección; devuelve el tipo concreto que produces.
- No exportes estado mutable. Si necesitas configuración, pásala por parámetro.
- Una promesa no se deja flotando: se espera, se devuelve o se maneja con un `.catch` explícito. `void promesa` solo con un manejador de errores detrás.
- Un error no se convierte en `undefined` silenciosamente. Decide si se propaga, se envuelve o se convierte en un resultado tipado, y documéntalo.

## 8. Módulos y exports

- Usa ESM y el `module`/`moduleResolution` que corresponda al runtime. No mezcles `require` y `import` en código nuevo.
- `import type` para tipos; `export type` para reexportarlos. Con `verbatimModuleSyntax` es obligatorio.
- Evita ciclos. Si dos módulos se necesitan, extrae el contrato compartido a un tercero.
- Un `index.ts` de barrel solo para la API pública del paquete. Los barrels internos ocultan dependencias y rompen el tree shaking.
- En una librería, declara `exports` con `types` y `import`/`require` explícitos. No publiques `src/` ni rutas internas.
- Los alias de path deben funcionar en `tsc`, en el runner y en el runtime. Si no, usa rutas relativas.
- Las project references se reservan para un monorepo real con builds medidos; no para un paquete único.

## 9. Dependencias

- Primero Node (`node:fs`, `node:crypto`, `fetch`) y la biblioteca estándar. Una dependencia se justifica por una necesidad concreta.
- Revisa licencia, mantenimiento, versión y superficie de seguridad antes de añadirla.
- Un único gestor de paquetes y un único lockfile. No mezcles `package-lock.json` con `pnpm-lock.yaml`.
- No mantengas dos versiones mayores de la misma librería. `npm ls <paquete>` o el equivalente debe mostrar una sola.
- No envuelvas una dependencia «para poder cambiarla» si el wrapper no aporta comportamiento.
- Actualiza dependencias en un cambio separado del cambio funcional.

## 10. Lista rápida de tipos

- [ ] `strict` activo y sin supresiones nuevas sin motivo.
- [ ] Sin `any` en la API pública; `unknown` en las fronteras.
- [ ] Sin `as` para silenciar un error de tipo.
- [ ] Estados modelados con uniones discriminadas y `never` exhaustivo.
- [ ] Identificadores de dominio con brand y constructor único.
- [ ] Sin `enum`; const objects con `as const`.
- [ ] Genéricos con dos usos reales o una relación real.
- [ ] `satisfies` en tablas; retorno explícito en exportadas.
- [ ] Imports de tipos con `import type`.
- [ ] Sin barrels internos, ciclos ni alias que el runtime no resuelva.
- [ ] Project references y build incremental solo con medición.
- [ ] Dependencias justificadas y una sola versión por librería.
- [ ] Sin reformateos ajenos ni cambios de comportamiento mezclados.
