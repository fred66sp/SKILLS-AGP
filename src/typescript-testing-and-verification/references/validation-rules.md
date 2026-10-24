# Reglas de validación en la frontera

Léela en el paso 2 antes de escribir un esquema o traducir un error. La validación de tipos en compilación no sustituye ninguna de estas reglas.

## 1. Dónde validar

| Frontera | Qué se valida | Dónde vive el esquema |
|---|---|---|
| Cuerpo, query y params HTTP | Forma, tipos, límites y formato | Junto al handler o en un módulo compartido |
| Webhook o respuesta de terceros | Todo el contrato externo | Adaptador del proveedor |
| Formulario | Lo que el usuario puede escribir | Módulo compartido cliente/servidor |
| `process.env` | Presencia, formato y valores permitidos | `src/env.ts`, importado al arrancar |
| Fichero o CSV | Estructura y tipos de cada fila | Adaptador de entrada |
| Argumentos de CLI | Tipos y combinaciones | Definición de flags del comando |
| Mensaje de cola o evento | Discriminante y carga | Consumidor del evento |

- Valida en la frontera una vez y pasa valores ya tipados hacia dentro. No reparsees en cada capa.
- Si un dato interno no confiable atraviesa una función pública, esa función también es una frontera.
- Un `JSON.parse` devuelve `unknown`. No lo anotes con `as T`.

## 2. El esquema es la fuente del tipo

```ts
import * as z from "zod";

export const CreateOrder = z.object({
  customerId: z.uuid(),
  email: z.email(),
  items: z.array(z.object({
    sku: z.string().regex(/^[A-Z0-9-]{4,20}$/),
    qty: z.int().positive().max(100),
  })).min(1),
  note: z.string().trim().max(500).optional(),
  placedAt: z.iso.datetime({ offset: true }),
});

export type CreateOrder = z.infer<typeof CreateOrder>;
export type CreateOrderInput = z.input<typeof CreateOrder>;
```

- `z.infer` es el tipo de salida, después de transformaciones y defaults. `z.input` es el tipo de entrada.
- No escribas una interfaz paralela. Si necesitas un tipo de dominio distinto, derívalo o conviértelo explícitamente.
- Define el esquema en el ámbito del módulo. Reconstruirlo por petición pierde la compilación y añade coste.
- Un esquema compartido entre cliente y servidor no importa secretos, base de datos ni módulos de servidor.
- Usa un solo estilo: el API de objetos o `zod/mini`, no ambos en el mismo código.

## 3. `parse` frente a `safeParse`

| Situación | Decisión |
|---|---|
| Handler HTTP, formulario, entrada de usuario | `safeParse` y respuesta de error |
| Configuración o invariante interna | `parse`; si falla, es un bug o un arranque inválido |
| Refinamiento o transformación asíncrona | `parseAsync` o `safeParseAsync` |
| Necesitas el error sin lanzar | `safeParse` |
| Rama que ya ha validado el mismo dato | No reparsees; pasa el valor tipado |

```ts
const result = CreateOrder.safeParse(body);
if (!result.success) {
  return badRequest(z.flattenError(result.error));
}
await createOrder(result.data);
```

- `parse` lanza `ZodError`; úsalo dentro de un `try` que traduzca el fallo, no en un handler que perdería el control.
- `safeParse` nunca lanza por un dato inválido, pero sí puede lanzar por un bug del esquema. No lo uses como sustituto de un `try` general.

## 4. Objetos, cadenas y números

- Los objetos eliminan claves desconocidas por defecto. Usa `z.strictObject()` para rechazarlas o `z.looseObject()` para conservarlas; elige según el contrato, no por comodidad.
- Compón con `.extend()`, `.pick()`, `.omit()`, `.partial()` y `.required()`. `.merge()` está desaconsejado.
- Formatos de cadena de Zod 4 son de nivel superior: `z.email()`, `z.uuid()`, `z.url()`, `z.ipv4()`, `z.iso.date()`, `z.iso.datetime()`. `z.string().email()` está obsoleto.
- `z.uuid()` es estricto con RFC; `z.guid()` es permisivo. Elige el que corresponda al contrato.
- `z.enum(["draft", "paid"])`; `z.nativeEnum` está obsoleto.
- `z.record(z.string(), z.number())` exige siempre esquema de clave y de valor.
- Para números enteros usa `z.int()`; para positivos, `.positive()`; para límites, `.min()`/`.max()`. No confíes en que `z.number()` rechace `NaN` o infinito sin comprobarlo.

## 5. Transformaciones, refinamientos y coerción

```ts
const Signup = z.object({
  password: z.string().min(12, { error: "Usa al menos 12 caracteres" }),
  confirm: z.string(),
}).refine((data) => data.password === data.confirm, {
  error: "Las contraseñas no coinciden",
  path: ["confirm"],
});

const Query = z.object({
  page: z.coerce.number().int().min(1).default(1),
  active: z.stringbool().optional(),
  tags: z.string().transform((value) => value.split(",").filter(Boolean)).optional(),
});
```

- El parámetro unificado es `error` (cadena o función). `message`, `required_error` e `invalid_type_error` son APIs de Zod 3.
- `.refine` para una comprobación; `.superRefine((value, ctx) => ctx.addIssue(...))` para varias. Los refinamientos no se ejecutan si la base ya falló.
- `.default()` devuelve el valor tal cual cuando la entrada es `undefined`; debe coincidir con el tipo de salida. `.prefault()` pasa el default por el esquema.
- `z.coerce.number()` sobre `""` produce `0`: añade `.min(1)` o preprocesa la cadena vacía a `undefined`.
- `z.coerce.boolean()` convierte `"false"` en `true` porque usa `Boolean("false")`. Usa `z.stringbool()` para `"true"/"false"/"yes"/"no"/"1"/"0"`.
- Una conversión bidireccional (ISO string ↔ `Date`) se modela con `z.codec(...)` y `z.decode`/`z.encode`, no con dos esquemas que puedan divergir.

## 6. Uniones discriminadas

```ts
const Event = z.discriminatedUnion("type", [
  z.object({ type: z.literal("paid"), orderId: z.string(), amount: z.number() }),
  z.object({ type: z.literal("refunded"), orderId: z.string(), reason: z.string() }),
]);
```

- Usa `z.discriminatedUnion` cuando haya un campo literal que selecciona la rama: es más rápido y produce errores más claros que `z.union`.
- El discriminante debe existir en todas las ramas y ser un literal.
- Para estados de una máquina, el esquema y la unión de TypeScript deben describir los mismos casos. Si divergen, el esquema es la verdad de runtime y el tipo debe derivarse de él.

## 7. Errores

| Función | Forma | Uso |
|---|---|---|
| `z.flattenError(error)` | `{ formErrors, fieldErrors }` | Formularios planos y cuerpos 400 |
| `z.treeifyError(error)` | Árbol anidado | Objetos y arrays anidados |
| `z.prettifyError(error)` | Texto multilínea con rutas | Logs, CLI y fallos de arranque |

- `error.issues` contiene los problemas crudos (`code`, `path`, `message`). `.errors`, `.format()` y `.flatten()` están obsoletos o eliminados.
- Devuelve campos y mensajes al cliente; nunca el input completo, secretos ni trazas internas.
- Un mensaje de error es contrato de usuario: estabilízalo y pruébalo. Un mensaje de log puede cambiar.
- No traduzcas un fallo de validación a un `500`. Es un `400` o el código de uso que corresponda.

## 8. Variables de entorno

```ts
const Env = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  DATABASE_URL: z.url(),
  PORT: z.coerce.number().int().default(3000),
  STRIPE_SECRET_KEY: z.string().startsWith("sk_"),
  FEATURE_X: z.stringbool().default(false),
});

const parsed = Env.safeParse(process.env);
if (!parsed.success) {
  console.error(`Entorno inválido:\n${z.prettifyError(parsed.error)}`);
  process.exit(1);
}
export const env = parsed.data;
```

- Importa este módulo al arrancar, antes de usar cualquier variable. Falla al inicio, no en el primer uso.
- No des default a un secreto obligatorio ni a una URL de producción.
- Los secretos de servidor no entran en un módulo que el bundle del cliente importe.
- Prueba el arranque con una variable ausente y con una inválida; comprueba el mensaje y el código de salida.

## 9. Cliente y servidor

- Comparte el esquema en un módulo sin dependencias de servidor (`packages/schemas` o `src/shared/`).
- El formulario y el endpoint importan el mismo objeto. El cliente valida para dar feedback; el servidor revalida porque el cliente no es confiable.
- Zod implementa Standard Schema: tRPC, TanStack Form, Hono y otros lo aceptan directamente.
- Para OpenAPI, exporta con `z.toJSONSchema(schema, { io: "input" })`; usa `target: "openapi-3.0"` si el contrato lo exige.
- No publiques un esquema con campos internos que el cliente no debe conocer. Separa el contrato público del modelo de persistencia.

## 10. Rendimiento

- Esquema en el ámbito del módulo, una sola instancia.
- En rutas calientes, `z.compile(schema)` (Zod 4.5+) o `import "zod/compile"` para compilar todos. Mide antes y después; no lo apliques por reflejo.
- Zod 4 compila objetos con `new Function`. Bajo una CSP sin `'unsafe-eval'`, configura `z.config({ jitless: true })`.
- Valida en la frontera y pasa el valor tipado. Repetir la validación en cada capa multiplica el coste sin añadir confianza.

## 11. Migración de Zod 3 a Zod 4

| Zod 3 | Zod 4 |
|---|---|
| `z.string().email()` | `z.email()` |
| `z.string().uuid()` | `z.uuid()` |
| `z.nativeEnum(X)` | `z.enum(X)` |
| `.merge()` | `.extend()` |
| `message:` | `error:` |
| `.flatten()` | `z.flattenError(error)` |
| `z.coerce.boolean()` para `"false"` | `z.stringbool()` |

- Migra un paquete a la vez y comprueba que solo hay una copia de `zod` en el árbol.
- `instanceof ZodError` falla si conviven dos copias; deduplica antes de depurar.
- Un refinamiento asíncrono con `parse` lanza; usa `parseAsync`.

## 12. Errores frecuentes

- Validar solo en el cliente y confiar en el servidor.
- Usar `as Schema` tras un `safeParse` fallido.
- Reconstruir el esquema en cada petición.
- `.optional()` en un campo que llega como `null`; usa `.nullable()` o `.nullish()`.
- Esperar que un refinamiento de objeto se ejecute cuando un campo ya falló.
- Devolver el `ZodError` completo al cliente con rutas internas.
- Mezclar `zod@3` y `zod@4` en el mismo proceso.

## 13. Lista rápida de validación

- [ ] Toda frontera externa tiene esquema y tipo derivado.
- [ ] `unknown` en la entrada; sin `as` para aceptar datos.
- [ ] `safeParse` en handlers; `parse` en configuración e invariantes.
- [ ] Async con `parseAsync`/`safeParseAsync`.
- [ ] Esquemas en ámbito de módulo y una sola versión de Zod.
- [ ] Entorno validado al arrancar; secretos obligatorios sin default.
- [ ] Errores traducidos a campos, árbol o texto según el receptor.
- [ ] Sin secretos ni input completo en la respuesta.
- [ ] Transformaciones y refinamientos probados, incluidos límites.
- [ ] Cliente y servidor comparten esquema; el servidor revalida.
