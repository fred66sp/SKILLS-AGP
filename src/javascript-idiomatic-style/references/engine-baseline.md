# Baseline del motor

Léela en los pasos 1 y 2: decide qué sintaxis se puede escribir antes de escribirla.

## 1. Dos objetivos, dos baselines

| Objetivo | De dónde sale el baseline | Qué manda |
|---|---|---|
| Navegador | `browserslist` en `package.json` o `.browserslistrc`; `target` del bundler si existe | El motor más antiguo de la lista |
| Node | `engines.node`, `.nvmrc`, `.node-version`, matriz de CI | La versión más baja que se ejecuta de verdad |
| Ambos | Intersección de los dos | Lo que puede compartirse sin condición |

- Si no hay `browserslist` ni bundler, el baseline es el navegador que el proyecto declara en su documentación; si tampoco existe, se pregunta antes de usar una feature reciente.
- Si `engines` no existe pero el CI fija una versión, esa versión es el baseline real. `engines` es una advertencia para el instalador, no una garantía.
- Un transpilador cambia el cálculo: el baseline del código fuente pasa a ser el `target` del transpilador, y el del resultado el que declare el proyecto.
- El baseline se anota en el resultado del trabajo. Sin él, «funciona en mi navegador» no significa nada.

## 2. Una edición no es una promesa

Cada edición ECMAScript agrupa features que los motores publicaron en momentos distintos. La misma edición puede contener una feature disponible en todos los motores y otra que aún no existe en uno. Por eso la comprobación se hace **por feature y por motor**, no por número de edición.

Procedimiento para una feature dudosa:

1. Nombra la feature exacta (`Array.prototype.toSorted`, `Set.prototype.union`, `AbortSignal.any`, `import.meta.dirname`).
2. Consulta su disponibilidad en una fuente de compatibilidad con fecha (MDN o el registro de Baseline), no en un blog ni en la tabla de una guía.
3. Comprueba el motor más antiguo del baseline, no el más moderno.
4. Si el motor más antiguo no la tiene, aplica la alternativa del lenguaje o del runtime; no la dejes «porque en el otro objetivo sí funciona».
5. Si la alternativa exige una dependencia, es una decisión que se propone, no que se toma dentro del cambio.

## 3. La intersección

```js
// adaptador de plataforma: la única pieza que sabe en qué objetivo corre
export function crearAlmacen() {
  if (typeof localStorage === "undefined") {
    return almacenEnMemoria();   // Node, pruebas o navegador sin almacenamiento
  }
  return almacenLocal(localStorage);
}
```

- El código compartido usa solo lo que existe en los dos baselines.
- La detección de plataforma vive en un adaptador, una vez, con nombre. No se reparte `typeof window` ni `typeof process` por el dominio.
- Un módulo compartido declara qué globals puede tocar. Si necesita `document` o `node:fs`, deja de ser compartido.
- La rama de cada objetivo se prueba en su objetivo: una simulación de `localStorage` no demuestra que el navegador funcione.

## 4. Qué no se escribe

- No se copia una tabla de features por edición al repositorio: caduca y da una falsa sensación de verificación.
- No se escribe «requiere ES2024» como sustituto de comprobar el motor.
- No se añade un polyfill para una feature que el baseline ya tiene, ni para una que nadie va a ejecutar.
- No se asume que el runtime del CI es el del usuario: el CI fija una versión, el usuario puede tener otra.
- No se confunde `target` de compilación con el runtime de ejecución cuando hay un bundler con transformación propia.

## 5. Señales de que el baseline cambió

| Señal | Qué revisar |
|---|---|
| El CI añade o quita una versión de Node | `engines`, `.nvmrc` y las features usadas |
| `browserslist` cambia | Navegadores objetivo y la intersección |
| Aparece un bundler o cambia su `target` | El baseline del fuente y del resultado |
| Una feature nueva se usa en un archivo compartido | El motor más antiguo de cada objetivo |
| Una dependencia sube su propio `engines` | El baseline real del proyecto |

Un cambio de baseline es un cambio de contrato: se propone aparte, con las features que habilita o retira, y no se cuela dentro de una corrección.
