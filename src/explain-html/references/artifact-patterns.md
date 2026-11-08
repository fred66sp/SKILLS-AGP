# Patrones por familia de artefacto

Estructura de cada familia. Lee solo la sección de la familia elegida y copia su plantilla completa de `../assets/`; no improvises una variante propia. El esqueleto [plantilla-artefacto](../assets/plantilla-artefacto.html) queda solo para encargos que no encajan en ninguna familia. Todas las plantillas traen `ASUNTO DEL ARTEFACTO` y el bloque de procedencia vacío para sustituirlos.

## Exploración comparativa

Plantilla: [`plantilla-exploracion.html`](../assets/plantilla-exploracion.html).

Cuándo: la persona no sabe qué dirección tomar y hay que poner las opciones una al lado de otra para poder señalar una.

Estructura: encabezado con la pregunta que resuelve → cuadrícula de opciones (2–3 columnas, `display: grid`) → pie con recomendación y criterio.

Cada opción es una tarjeta con: nombre corto, cómo funciona en 2–4 líneas, ejemplo o boceto visual (SVG en línea), y su **concesión** etiquetada de forma visible («qué pierde» o «cuándo falla»). Las opciones deben ser claramente distintas: varía mecanismo o estructura, no solo nombres. Evita neutralizar la comparación con prosa idéntica.

## Explicador

Plantilla: [`plantilla-explicador.html`](../assets/plantilla-explicador.html).

Cuándo: la persona quiere entender cómo funciona algo —un mecanismo del código, un concepto, un proceso— y lo va a leer una vez o dos.

Estructura: caja de TL;DR al principio (3–5 líneas: qué es, por qué importa, dónde está en el código) → diagrama del flujo completo (SVG en línea) → recorrido por pasos como `<details>` plegables, cada uno con el fragmento de código real anotado → sección «Trampas» al final → sección «Desconocidos».

El diagrama representa el mecanismo, no su nombre: el camino de una petición por una caché dice más que una caja etiquetada «caché». Cada fragmento de código va con su fichero y línea de origen.

## Informe

Plantilla: [`plantilla-informe.html`](../assets/plantilla-informe.html).

Cuándo: estado periódico, evolución de un trabajo, resumen de incidente. Se lee rápido, no se estudia.

Estructura: resumen en la primera pantalla (qué se entregó, qué se retrasó, una cifra clave) → tabla o cronología coloreada por estado → mini-gráfico SVG si hay datos reales → acciones de seguimiento → «Desconocidos».

La cronología es una lista con marcadores de estado (`hecho`, `en curso`, `bloqueado`) con color semántico consistente. Un gráfico solo se dibuja con datos verificados: sin datos reales, tabla, no gráfico.

## Diagrama

Plantilla: [`plantilla-diagrama.html`](../assets/plantilla-diagrama.html).

Cuándo: flujo, arquitectura, secuencia o proceso que vive mejor como caja y flecha que como prosa.

Estructura: título con la pregunta que responde el diagrama → el diagrama → leyenda de formas y colores → notas de los puntos que necesitan explicación.

Dos técnicas, en línea, sin dependencias:

- **SVG en línea**: para topologías, mapas de módulos y caminos. `<figure>` con `role="img"`, `aria-label` y `<figcaption>`. Resalta el camino caliente.
- **Pipeline CSS**: para secuencias lineales de 3–6 pasos. Cajas conectadas con flechas, cada paso con su etiqueta y descripción corta.

Etiqueta cada flecha con su propósito o su frecuencia. Un diagrama sin leyenda de estados no se entrega.

## Prototipo

Plantilla: [`plantilla-prototipo.html`](../assets/plantilla-prototipo.html).

Cuándo: probar una animación, una interacción o un flujo clicable; el movimiento y la interacción no se describen, se sienten.

Estructura: zona de prueba a pantalla completa → panel de controles (deslizadores, interruptores) → botón «copiar como prompt».

Los controles son `<input type="range">` y `<input type="checkbox">` conectados a variables CSS o al estado de la demo. Responde en vivo a cada cambio. Para un flujo clicable, pantallas mínimas enlazadas entre sí con fidelidad suficiente para notar si la interacción es correcta, sin datos reales ni backend.

El botón «copiar como prompt» lee el estado actual de los controles (valores, opciones) y copia un texto como `Ajusta el componente: duración 300ms, escala 1.04, easing cubic-bezier(0.34, 1.56, 0.64, 1)` con `navigator.clipboard.writeText`. Feedback visible: el botón cambia a «Copiado» durante un segundo.

## Cuestionario

Plantilla: [`plantilla-cuestionario.html`](../assets/plantilla-cuestionario.html).

Cuándo: evaluar comprensión de un tema, autoevaluación, preparación de una entrevista o revisión de conocimiento.

Estructura: cabecera con tema y número de preguntas → preguntas de una en una o en lista → corrección en vivo → resultado final con puntuación → botón «copiar resultado» → «Desconocidos» solo si el cuestionario cubre un material verificable.

Reglas: cada pregunta con sus opciones como `<button>` o `<label>` + `<input type="radio">`; la explicación de la respuesta correcta se muestra tras responder, no antes; la puntuación y las respuestas falladas van al texto del botón de copia. Las preguntas salen del material fuente o de la persona; no se inventan datos factuales dentro de las opciones.

## Editor a medida

Plantilla: [`plantilla-editor.html`](../assets/plantilla-editor.html).

Cuándo: la persona tiene que reordenar, clasificar o editar algo que es un martirio de expresar en texto —prioridades, configuración con restricciones, valores de color o curvas, listas largas—.

Estructura: el dato cargado, visible y editable → validación o avisos en línea cuando el estado sea incoherente → botón «copiar como prompt» (o «copiar diff») que exporta solo lo cambiado.

El editor es desechable y específico de este dato, no un producto: no crea persistencia, no guarda en `localStorage` salvo que el encargo lo pida, no añade funciones para después. La exportación copia el estado final estructurado —JSON o texto plano— con una razón por cambio cuando aplique.

## Presentación

Plantilla: [`plantilla-presentacion.html`](../assets/plantilla-presentacion.html).

Cuándo: comunicar en una reunión con las flechas del teclado, sin herramienta de escritorio.

Estructura: secciones `<section>` a `100dvh` con navegación por teclado (flechas, espacio, Home/End) → barra de progreso fina → contador «n / total» → índice accesible.

Reglas: una idea por diapositiva; títulos grandes y cuerpo mínimo; los diagramas en diapositiva propia; sin animación esencial y con `prefers-reduced-motion` respetado. Sin JS, el deck sigue siendo legible como página con scroll: cada sección apilada es contenido completo.

## Bucles de varios artefactos

Un mismo razonamiento puede necesitar varias páginas —exploración → plan → mockups— que se leen en orden. No es un documento con capítulos: son artefactos hermanos de `.explanations/` que se enlazan con rutas relativas y funcionan como memoria del razonamiento.

- Cada página es un `.html` de primer nivel con su propia familia y su propio bloque de procedencia.
- Los enlaces del cuerpo usan el nombre relativo (`<a href="plan.html">`), nunca `file:///`, rutas absolutas ni URLs.
- La página que conoce el bucle declara sus hermanos en `enlaces` dentro de la procedencia. `build-index.py` muestra esa relación; `check-artifact.py` rechaza nombres con carpetas, URLs o rutas absolutas.
- Cada eslabón pasa `check-artifact.py` por separado. Un bucle con una página rota no está terminado.
- La entrada del bucle se abre primero y se nombra en el cierre; las demás se alcanzan desde ella.

Ejemplo de procedencia en la primera página:

```html
<!-- procedencia: {"prompt": "Explora y prepara el rediseño del panel", "fecha": "2026-11-08",
     "familia": "exploracion", "fuentes": ["conversación", "src/panel.py:40"],
     "enlaces": ["plan-panel.html", "mockups-panel.html"]} -->
```

## Código resaltado

Cuando la familia muestre código real, el fragmento va dentro de `<pre><code>` con las clases que produce `scripts/highlight.py`: `tok-kw`, `tok-str`, `tok-com`, `tok-num` y `tok-fn`.

- Genera el fragmento con `python3 scripts/highlight.py <lenguaje> <fichero>` (o por stdin) y pega su bloque `--css` una sola vez en el `<style>` del artefacto.
- No escribas el resaltado a mano ni cargues una librería: la salida es determinista, escapa el HTML y no introduce recursos externos.
- Cada fragmento lleva su fichero y línea de origen; el color no sustituye la anotación de lo que importa.
