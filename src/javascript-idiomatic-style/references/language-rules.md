# Reglas de lenguaje

Léela en los pasos 2 y 3 del procedimiento, cuando una decisión de declaración, igualdad, número, función, objeto, iteración o clase no sea evidente.

## 1. Declaraciones y ámbito

| Decisión | Regla | Motivo |
|---|---|---|
| `var` | No se usa nunca | Ámbito de función y hoisting a `undefined` |
| `const` | Por defecto | El binding no cambia; el valor puede ser mutable |
| `let` | Solo si el binding se reasigna | Un `let` asignado una vez en cada rama es un `const` disfrazado |
| Declaración | Una por sentencia | El depurador y `git blame` señalan una línea |
| Posición | En el primer uso | La distancia entre declaración y uso es el ámbito real |
| Sombreado | Evitarlo | Un nombre reutilizado en un bloque interior oculta el de fuera |

Un `const` con objeto no congela el objeto. Si el valor debe ser inmutable, `Object.freeze` es superficial: no sustituye a no mutarlo.

## 2. Igualdad y coerción

| Expresión | Resultado | Uso |
|---|---|---|
| `a === b` | Igualdad estricta, sin conversión | Siempre |
| `a == null` | `true` para `null` y `undefined` | Única excepción admitida |
| `a == b` con otros valores | Convierte y sorprende | Prohibido |
| `Object.is(a, b)` | Distingue `NaN` de `NaN` y `-0` de `0` | Solo para esos dos casos |

El conjunto falsy es `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined` y `NaN`. `[]`, `{}` y `"0"` son truthy.

| Trampa | Qué pasa | Qué se escribe |
|---|---|---|
| `valor \|\| porDefecto` | `0`, `""` y `false` caen al valor por defecto | `valor ?? porDefecto` |
| `x ?? y \|\| z` | `SyntaxError` | Paréntesis explícitos |
| `isNaN("abc")` | `true`, porque convierte primero | `Number.isNaN(Number("abc"))` |
| `parseInt("1e3")` | `1` | `Number("1e3")` → `1000` |
| `["1","7","11"].map(parseInt)` | `[1, NaN, 3]` | `.map((v) => Number(v))` |
| `[] + {}` | `"[object Object]"` | No concatenar estructuras |
| `0.1 + 0.2 === 0.3` | `false` | Comparar con tolerancia o en enteros |

## 3. Números, dinero y fechas

- El dinero se guarda en enteros de la menor denominación (céntimos) y se formatea con `Intl.NumberFormat`. `(1.005).toFixed(2)` devuelve `"1.00"` porque el binario no representa el decimal.
- `Number.isFinite` antes de operar con un valor que llega de fuera; `NaN` se propaga por toda la aritmética sin avisar.
- `BigInt` no se mezcla con `Number` en la misma operación: `1n + 1` lanza `TypeError`. Se convierte de forma explícita en la frontera.
- Los separadores numéricos (`1_000_000`) son legibles y no cambian el valor.
- Una fecha se transporta como instante ISO 8601 en UTC y se presenta con `Intl.DateTimeFormat` en la zona del receptor. No se construye una fecha de negocio con `new Date("2026-02-31")`: el motor la corrige en silencio.
- `Date.now()` para el instante, `performance.now()` para medir duraciones. Un cálculo de negocio no depende del reloj real: recibe la fecha.

## 4. Funciones

- Guardas primero; el camino feliz no va indentado dentro de un `if`.
- `function` con nombre en el ámbito del módulo: hoistea y aparece con nombre en la traza.
- Flecha para callbacks y para funciones que no usan `this`.
- Nunca flecha como método de objeto ni en un prototipo: no tiene `this` propio.
- Parámetros: un objeto cuando haya más de dos o cuando el orden no se lea; nunca booleanos posicionales.
- No se mutan los parámetros. Un parámetro modificado es un efecto invisible para quien llama.
- Valor por defecto en la firma (`function f(opciones = {})`), no dentro del cuerpo.
- Una función asíncrona devuelve una promesa; no mezcla `callback` y promesa en la misma API.

## 5. Objetos, copias y prototipos

| Necesidad | Construcción |
|---|---|
| Leer una propiedad que puede faltar | `obj?.prop` |
| Leer y comprobar existencia propia | `Object.hasOwn(obj, "prop")` |
| Copia superficial | `{ ...obj }` o `Object.assign({}, obj)` |
| Copia profunda de datos | `structuredClone(valor)` |
| Congelar | `Object.freeze(obj)` es superficial |
| Listar claves | `Object.keys`, `Object.values`, `Object.entries` |

- `structuredClone` no copia funciones, no conserva prototipos y lanza con valores no clonables. Un clon a mano con `JSON.parse(JSON.stringify(x))` pierde `Date`, `Map` y `undefined`.
- `Object.hasOwn` sustituye a `obj.hasOwnProperty(...)`, que falla si la clave se llama `hasOwnProperty` o si el objeto no tiene prototipo.
- Un objeto de configuración no se muta después de construirse. Si hay que derivarlo, se crea otro.
- No se añaden propiedades a prototipos de builtins.
- `Map` para claves que no son cadenas o cuando importa el orden de inserción y el borrado frecuente; objeto plano para registros de forma fija.

## 6. Iteración y colecciones

| Caso | Construcción |
|---|---|
| Recorrer con `await`, `break` o `return` | `for...of` |
| Transformar | `map` |
| Filtrar | `filter` |
| Acumular | `reduce` solo si la operación es una reducción real |
| Buscar uno | `find` / `findIndex` |
| Comprobar todos o alguno | `every` / `some` |
| Ordenar sin mutar | `toSorted` si el baseline lo permite; si no, `[...lista].sort(...)` |

- `sort` sin comparador convierte a cadena y ordena por unidades UTF-16: `[10, 9, 1].sort()` da `[1, 10, 9]`. Siempre comparador, salvo que el orden lexicográfico sea el deseado.
- `forEach` no espera promesas y no se puede interrumpir. Para efectos asíncronos, `for...of` con `await`.
- `map` no es un `forEach` con retorno: si no se usa el resultado, `forEach` o `for...of`.
- Un agujero en un array (`new Array(3)`) no es lo mismo que `undefined`: `map` lo salta y `for...of` lo recorre. Evita arrays dispersos.

## 7. Clases

- Se usan cuando hay estado y comportamiento que se crean juntos y se instancian varias veces. Una función que devuelve un objeto es suficiente para un caso único.
- Campos privados `#campo` para el estado interno; `#metodo` para lo que no forma parte del contrato.
- Comprobación de marca con `#campo in obj` en lugar de mirar una propiedad convencional.
- Los campos se inicializan en la declaración; el constructor solo recibe y valida.
- Un bloque `static {}` para la inicialización estática compleja.
- `extends` solo con una relación real; si dos clases comparten comportamiento, composición antes que herencia.
- Un método que puede fallar lanza, no devuelve `undefined` ni un booleano de estado.

## 8. Expresiones regulares

- Una expresión con nombre (`const RE_EMAIL = /.../`) en el ámbito del módulo; no se compila por iteración.
- `lastIndex` es estado: una regex con flag `g` reutilizada entre llamadas da resultados alternos. Usa `matchAll` o crea la regex en el punto de uso.
- Prefiere grupos con nombre (`(?<year>\d{4})`) a índices posicionales.
- No uses una regex para analizar HTML, JSON ni código. Para texto libre, acota con `^...$` y prueba los límites.
- Una entrada del usuario que se interpola en una regex se escapa antes; el repositorio puede no tener un `escapeRegExp` y no hace falta inventarlo si el caso no existe.

## 9. Nombres y forma

- Un concepto, una palabra en todo el código: `getUser` en todas partes, no `getUser` junto a `fetchUserInfo`.
- Abreviaturas admitidas: `url`, `id`, `err`, `ctx`, `req`, `res`, `db`, `fn`. El resto se escribe completo.
- Nada de contexto redundante: `coche.marca`, no `coche.cocheMarca`.
- Se nombra por papel, no por estructura: `usuario`, no `usuarioObjeto` ni `datosUsuario`.
- Una letra solo en un ámbito de dos líneas: índice de bucle o parámetro de comparador.
- Ficheros en `kebab-case` salvo que el directorio ya use otra convención.
- Un módulo exporta lo que su nombre promete. Si exporta tres cosas sin relación, son tres módulos.

## 10. Trampas frecuentes

| Síntoma | Causa | Corrección |
|---|---|---|
| Una comparación pasa cuando no debería | `==` con tipos distintos | `===` |
| Un `0` se convierte en el valor por defecto | `\|\|` | `??` |
| `sort` devuelve un orden extraño | Sin comparador | `(a, b) => a - b` |
| Un `import` lee `undefined` al cargar | Ciclo de módulos o ESM/CJS mezclados | Romper el ciclo, revisar `type` |
| `await` dentro de `forEach` no espera | `forEach` ignora promesas | `for...of` |
| `this` es `undefined` en un método | Flecha como método | `function` o método de clase |
| Un número pierde precisión al sumar | Coma flotante | Enteros en la menor unidad |
| Un listener se ejecuta dos veces | Registro duplicado en cada render | Registrar una vez y retirar con `signal` |
