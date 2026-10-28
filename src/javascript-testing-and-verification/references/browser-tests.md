# Pruebas en el navegador

Léela en el paso 3 cuando la capa sea el DOM: nodos, eventos, formularios, almacenamiento y esperas.

## 1. El runner en una página

`assets/test-runner.html` es una página sin dependencias: registra casos con `test(nombre, fn)`, los ejecuta al cargar y muestra el resultado en el documento. Se copia junto al código, se añaden los casos y se abre en el navegador.

```html
<script src="precio.js"></script>
<script src="test-runner.js"></script>
<script>
  test("totalPedido ignora líneas sin precio", () => {
    const total = totalPedido({ lineas: [{ cantidad: 2 }, { precio: 100, cantidad: 1 }] });
    equal(total, 100);
  });
</script>
```

- Los scripts se cargan en orden: primero el código, después el runner, después los casos.
- El resultado se publica al terminar la carga; recargar la página repite la suite.
- Sin servidor, con `file://`, funciona si el código no usa módulos ESM con rutas absolutas. Con módulos hace falta un servidor estático, porque `file://` bloquea los imports.
- El runner es para desarrollo y para una comprobación manual declarada; no sustituye a CI.

## 2. Qué se prueba en el DOM

| Comprobación | Cómo |
|---|---|
| Texto visible | `nodo.textContent` |
| Nodo creado con la etiqueta correcta | `nodo.tagName` |
| Atributo o estado | `getAttribute`, `checked`, `disabled` |
| Clase o estado visual | `classList.contains` |
| Orden de hijos | `parent.children` |
| Nodo retirado | `nodo.isConnected` |
| Foco | `document.activeElement` |

- Se comprueba lo que el usuario percibe: el texto, el estado del control y la presencia del nodo.
- No se comprueba el HTML completo de un contenedor: cualquier atributo nuevo rompe la prueba sin cambiar el comportamiento.
- No se comprueba el estilo calculado salvo que el color o la visibilidad sean el contrato.

## 3. Eventos y formularios

```js
const formulario = document.createElement("form");
const campo = document.createElement("input");
campo.value = "texto";
formulario.append(campo);
document.body.append(formulario);

test("el envío usa el valor del campo", () => {
  let recibido = null;
  formulario.addEventListener("submit", (evento) => {
    evento.preventDefault();
    recibido = new FormData(formulario).get("campo");
  }, { once: true });
  formulario.requestSubmit();
  equal(recibido, "texto");
});
```

- `requestSubmit()` dispara la validación y el evento `submit`, como el usuario; `dispatchEvent` no valida.
- `click()` para botones; `dispatchEvent` solo para eventos que el navegador no puede provocar.
- Los eventos personalizados llevan `detail` con datos comprobables.
- Un formulario que se envía en el test debe limpiarse después: se retira del documento en el propio test.
- El foco se comprueba después del evento que lo mueve, no antes.

## 4. Red y almacenamiento

- `fetch` se sustituye por una función que devuelve un objeto con `ok`, `status` y `json()`. El original se restaura al terminar.
- Un caso de error HTTP se simula con `ok: false` y un cuerpo JSON; comprueba que el código lo trata como fallo.
- `localStorage` se limpia antes y después de cada caso; el estado de una ejecución anterior no debe influir.
- Un fallo de cuota se simula lanzando en `setItem`; comprueba que el código degrada y no rompe la página.
- Los tiempos de espera se simulan con un `AbortController` propio; no esperes el plazo real.

## 5. Esperas y estabilidad

- Se espera el evento que cierra la operación: `submit`, `load`, `message`, una promesa.
- Un `setTimeout` de espera es una prueba frágil: en una máquina lenta falla y en una rápida esconde el problema.
- Para pintado y medidas, `requestAnimationFrame` dos veces o `await new Promise(requestAnimationFrame)`; nunca un número de milisegundos.
- Un test que depende de un `IntersectionObserver` necesita el observer simulado o un contenedor con tamaño real.
- La suite se ejecuta dos veces seguidas: si el segundo resultado difiere, hay estado o tiempo.

## 6. Aislamiento

- Cada caso retira lo que añadió: nodos, listeners, entradas de almacenamiento, intervalos.
- El documento de pruebas no se reutiliza con estado de otro caso; si hace falta, un `div` contenedor por test.
- Un listener global registrado por el código se retira con el `AbortController` del caso.
- Los casos no dependen del orden: se pueden ejecutar sueltos.

## 7. Límites y cuándo cambiar de capa

- El runner de página demuestra comportamiento del DOM; no demuestra accesibilidad completa, CSS ni rendimiento.
- Cuando el proyecto ya tiene un runner con DOM simulado, se usa ese para la suite automática y esta página queda como comprobación manual.
- Una prueba de extremo a extremo se justifica cuando el recorrido cruza varias páginas o depende del servidor; se declara como tal y no sustituye a las de unidad.
- Si el código solo se puede probar con un DOM simulado que el proyecto no tiene, se declara el límite en el informe; no se añade la dependencia sin decisión.
