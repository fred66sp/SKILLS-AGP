# APIs del navegador

Léela en el paso 4 cuando el código se ejecute en un documento: DOM, eventos, red, formularios, almacenamiento, observers o Workers.

## 1. Construcción segura de DOM

| Necesidad | Construcción | Nunca |
|---|---|---|
| Insertar texto del usuario | `el.textContent = texto` | `el.innerHTML = texto` |
| Crear un nodo | `document.createElement("li")` | Concatenar HTML |
| Insertar varias filas | `template` + `cloneNode(true)` | `innerHTML +=` en un bucle |
| Insertar texto junto a un nodo | `insertAdjacentText` | `insertAdjacentHTML` con dato externo |
| Atributo de datos | `el.dataset.id = id` | `setAttribute("onclick", ...)` |

`innerHTML` con dato externo es una inyección de HTML: el navegador ejecuta lo que reconoce, incluidos manejadores. `textContent` no interpreta nada. Si el proyecto ya tiene un saneador, se usa para HTML propio y nunca para texto.

- Un fragmento se construye fuera del documento y se inserta una vez: menos repintados y menos estado intermedio.
- Las referencias a nodos se guardan al crear, no se buscan con `querySelector` en cada evento.
- Un identificador se usa para un elemento único; una clase o `data-*` para un grupo.
- `document.write` no se usa: reescribe el documento y rompe la carga.

## 2. Eventos

```js
const controller = new AbortController();

formulario.addEventListener("submit", alEnviar, { signal: controller.signal });
controller.abort(); // retira todos los listeners registrados con esta señal
```

- Delegación en un contenedor estable cuando los hijos se crean y se destruyen; comprueba el origen con `event.target.closest(...)`.
- `{ passive: true }` en `touchstart`, `touchmove` y `wheel` cuando no se llama a `preventDefault`.
- `{ once: true }` para un evento que solo debe ocurrir una vez.
- `{ signal }` para que el listener muera con su componente; evita el `removeEventListener` olvidado.
- `preventDefault` solo cuando el comportamiento por defecto estorba, y se explica en una línea.
- Un formulario se gestiona con `submit`, no con el `click` del botón: así funciona también con Enter.
- No se usa `event.stopPropagation` para arreglar un conflicto de listeners; se corrige el reparto.

## 3. `fetch`

- `fetch` no rechaza por un estado HTTP de error. Se comprueba `respuesta.ok` o `respuesta.status` antes de leer el cuerpo.
- `respuesta.json()` rechaza si el cuerpo no es JSON válido; se trata como un fallo de la operación.
- Un `signal` conecta la petición con el ciclo de vida que la origina.
- `Content-Type` se declara al enviar JSON: `headers: { "Content-Type": "application/json" }` y `body: JSON.stringify(dato)`.
- Las credenciales y el modo CORS se declaran explícitamente; el valor por defecto cambia según el origen.
- Un reintento se justifica por tipo de fallo y tiene límite y espera creciente. No se reintenta un 4xx.
- La respuesta se valida antes de usarla: el tipo declarado no existe en runtime.

## 4. Formularios

- La validación del navegador mejora la experiencia; la del servidor es la que decide. Nunca se omite la segunda.
- `FormData` para enviar campos tal como los ve el usuario; un objeto a mano duplica el mapeo.
- `input.value` siempre es cadena. Un número se convierte y se comprueba (`Number.isFinite`) antes de usarlo.
- El estado de error se muestra junto al campo, con `aria-invalid` y texto asociado; no solo con color.
- Un botón de envío se deshabilita mientras la operación está en curso, y se vuelve a habilitar en `finally`.
- El foco se mueve al primer error en un envío fallido.

## 5. Almacenamiento

| API | Qué guarda | Límite |
|---|---|---|
| `localStorage` | Cadenas, por origen, sin caducidad | Síncrona; lanza `QuotaExceededError` |
| `sessionStorage` | Cadenas, por pestaña | Se pierde al cerrar |
| `document.cookie` | Cadenas pequeñas enviadas al servidor | Sincrónica y torpe; el servidor decide `HttpOnly` |
| IndexedDB | Estructuras grandes y binarios | Asíncrona; necesita versión y migración |

- Todo lo guardado se serializa y se valida al leer: un valor corrupto o de otra versión no debe romper la página.
- El almacenamiento puede fallar por cuota, por modo privado o por política del navegador: se envuelve en `try/catch` y se degrada.
- Un token de sesión no se guarda en `localStorage` si el servidor puede usar `HttpOnly`; el script no debe poder leerlo.

## 6. Observers

- `IntersectionObserver` para visibilidad, no un `scroll` con cálculos por frame.
- `ResizeObserver` para cambios de tamaño de un elemento, no `window.resize` para todo.
- `MutationObserver` para reaccionar a cambios de terceros; no para observar lo que escribe tu propio código.
- Cada observer se desconecta en la limpieza. Un observer sin `disconnect` retiene nodos.

## 7. Workers

- Un Worker recibe y devuelve mensajes serializables; funciones y clases no cruzan.
- `structuredClone` describe lo que se puede transferir. Los `ArrayBuffer` se transfieren con lista de transferencia para no copiar.
- El Worker no toca el DOM. Si necesita datos del documento, se los envía el hilo principal.
- Un Worker de larga vida se termina (`terminate`) cuando ya no hace falta; uno por tarea no se reutiliza sin medir.
- Un módulo Worker se declara con `{ type: "module" }` y respeta el mismo baseline que el hilo principal.

## 8. Ciclo de vida y limpieza

- Todo recurso abierto en el montaje se cierra en el desmontaje: listeners, observers, intervalos, `AbortController`, Workers y conexiones.
- `DOMContentLoaded` si el script está en `head` sin `defer`; con `type="module"` o `defer`, el documento ya está listo.
- Un `<script type="module">` se ejecuta una vez y en orden de dependencias; no se apoya en el orden de dos scripts clásicos.
- La navegación con `beforeunload` solo para advertir de datos sin guardar; no para lógica de negocio.
- La página no depende de `window.onload` para estar operativa: el contenido se sirve y la mejora llega después.

## 9. Trampas del navegador

| Síntoma | Causa | Corrección |
|---|---|---|
| El texto del usuario se interpreta como HTML | `innerHTML` | `textContent` |
| Un listener queda vivo tras navegar | Sin `signal` ni `removeEventListener` | `AbortController` por vista |
| La petición no se cancela al salir | Sin `signal` | Propagar el del ciclo de vida |
| Un `fetch` «fallido» devuelve datos | 404 con cuerpo JSON | Comprobar `ok` |
| El almacenamiento revienta en modo privado | `setItem` lanza | `try/catch` y degradar |
| Dos módulos compiten por el mismo nodo | Estado global implícito | Un dueño por nodo |
