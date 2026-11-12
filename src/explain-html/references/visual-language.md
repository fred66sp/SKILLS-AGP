# Lenguaje visual del artefacto

Invariantes comunes a todas las familias. Se aplican sobre la plantilla de la familia elegida —o el esqueleto base si ninguna encaja—, que ya los trae; esta referencia los explica y fija los valores que no debe cambiar el artefacto.

## Matriz de representación

Qué técnica usa cada tipo de contenido. Nunca ASCII art, nunca diagramas de texto:

| Tipo de contenido | Representación |
|---|---|
| Flujos, pipelines, máquinas de estado | SVG en línea o pipeline CSS |
| Arquitectura con mucho texto | Tarjetas en CSS Grid, con un diagrama de resumen si ayuda |
| Comparaciones, auditorías, matrices | Tablas HTML semánticas `<table>` |
| Cronologías, roadmaps | Timeline en CSS con marcadores de estado |
| Datos numéricos verificados | Mini-gráfico SVG en línea o KPI |
| Código | `<pre><code>` con las clases `tok-*` que genera `scripts/highlight.py` |
| Prose explicativa | Párrafos a 65ch con jerarquía de encabezados |

## Tipografía

- Escala en `rem` con `html { font-size: 16px }`: el texto reescala con una sola perilla.
- Texto corrido a unos 65ch de máximo; `text-wrap: balance` en titulares.
- Tamaños mínimos: cuerpo ≥ 14px, secundario ≥ 11px, mono ≥ 12px.
- Dos roles de fuente como máximo: uno de texto y uno monoespaciada para código y datos. Familias del sistema con fallback explícito, sin fuentes remotas. La plantilla declara una pila de texto (Inter y la del sistema) y una mono (JetBrains Mono y la del sistema).
- tokens como custom properties: `--bg`, `--surface`, `--sunken`, `--text`, `--muted`, `--line`, `--line-strong`, `--accent`, `--accent-2`, `--accent-3`, `--accent-soft`, `--terminal`, `--terminal-panel`, `--terminal-line`, `--terminal-content`, `--ok`, `--warn`, `--err` y sus marcas `--ok-mark`, `--warn-mark`, `--err-mark`; también `--font`, `--mono`, `--radius*`, `--shadow*`, `--fs-*`, `--gutter`, `--shell` y `--sp-*`. Los patrones referencian esas propiedades, nunca valores fijos.
- Compatibilidad del contrato: `--text-dim` es alias de `--muted`, `--border` y `--border-strong` de `--line` y `--line-strong`, y `--code-bg`, `--code-text`, `--code-border` de `--terminal`, `--terminal-content` y `--terminal-line`. Los patrones del proyecto pueden seguir usando esos roles sin renombrar sus tokens.
- Si el encargo pide el sistema visual del proyecto, copia sus valores con `scripts/tokens-from-project.py` en el `:root` del artefacto. La precedencia es intención de la persona → sistema del proyecto → defaults de la plantilla; el CSS se copia, jamás se enlaza.

## Color

- Roles, no decoración: superficie, texto, borde, acento y semánticos (correcto, aviso, error). El acento índigo `#4f46e5` se usa para lo que pide atención, no como pintura general; `--accent-2` y `--accent-3` solo apoyan diagramas y degradados de portada.
- Tema claro y oscuro con `data-theme="light|dark"` en `<html>`: la plantilla trae `:root` claro, `:root[data-theme="dark"]` y un botón `data-theme-toggle` que persiste en `localStorage`; si no hay preferencia guardada, arranca con `prefers-color-scheme`. La portada usa `.hero` con washes radiales y rejilla.
- El bloque de código va sobre terminal oscuro (`--terminal` con `--terminal-content`) en ambos temas; el código en línea usa la superficie hundida (`--sunken`). Un acento que no llega a AA como texto se sustituye por su variante oscurecida, no se aclara el fondo de la página para compensar.
- Evita los genéricos: no un acento violeta o fucsia por defecto en todo artefacto, ni gradientes decorativos que no separan planos ni apoyan el mensaje.
- Los pares texto/fondo del `:root` deben llegar a WCAG AA 4.5:1. `check-artifact.py` avisa de los que no; un aviso no bloquea, pero se corrige o se justifica.

## Diagramas SVG

Las demos de `docs/explain-html/demo/` siguen estas convenciones; la plantilla las trae en su placeholder.

- **`fill` en cada `<text>`, no en el `<g>` contenedor.** La regla `svg text:not([fill]){fill:currentColor}` respeta el atributo del propio elemento pero no la herencia del grupo: un titular sin `fill` sale con el color del contenedor, apagado. Titulares `fill="var(--text)"`, `font-weight="700"`, `16px`; subtítulos `fill="var(--muted)"`, `11.5px`.
- **`viewBox` ajustado al dibujo.** `.flow-wrap` y `.diagram-wrap` estiran el SVG al 100% del ancho (con `min-width` de 720–760 px): si el dibujo no ocupa todo el `viewBox`, queda un margen muerto a la derecha o abajo. Reparte las cajas por todo el ancho y deja solo el padding del dibujo.
- **Colores por rol, nunca `currentColor` para texto.** Cajas `stroke="var(--line-strong)"`; la caja que decide o destaca, `stroke="var(--accent)"` y `stroke-width="2"`; la puerta o verificación, `stroke="var(--ok-mark)"` y `stroke-width="2"`. Flechas de avance `stroke="currentColor"` y `stroke-width="2"` con `marker-end`; la rama de formalizar puede llevar el acento en flecha y etiqueta, y las neutras van en `var(--muted)`.
- `font-family="Inter, ui-sans-serif, system-ui, sans-serif"` y `text-anchor="middle"` en los `<text>`.
- Cada diagrama va en `<figure>` con `role="img"`, `aria-label` y `<figcaption>`; no se repite aquí: ver «Accesibilidad».

## Espacio y composición

- El contenedor compartido es `.shell`: `width: min(100% - 2·--gutter, --shell)` con `--shell: 1180px` y `--gutter: clamp(16px, 4vw, 40px)`. La portada es `.hero` con washes radiales y `.grid-bg` para la rejilla; no se inventa otro ancho de página.
- El primer viewport del artefacto deja clara su pregunta y su respuesta principal.
- Una tarjeta delimita un grupo real, no cada fragmento de texto; `min-width: 0` en hijos de grid y flex para evitar desbordes.
- Sin overflow horizontal a anchura de escritorio normal; el artefacto se lee en 390, 768 y 1440 px apilando columnas, no reduciendo tamaños hasta romper.

## Componentes compartidos

- Barra superior `.top` pegajosa con marca `.brand` (`.mark` y `.brand-text`) y el botón de tema `.theme`; sin enlaces externos, la navegación interna usa `#contenido`.
- Portada `.hero.grid-bg` con `.eyebrow`, `h1`, `.lead`, `.meta-row` y `.tag`/`.tag-accent`/`.tag-ok`; acciones con `.btn.btn-primary` o `.btn.btn-ghost`.
- Secciones con `.section` y `.section-head > .num + h2`; agrupaciones en `.card`; avisos en `.note`, `.note-ok` y `.note-warn`.
- Tablas dentro de `.table-wrap`, con `thead th` sobre `--sunken`; el código dentro de `pre` sobre `--terminal` y el código en línea sobre `--sunken`.
- Las piezas propias de cada familia (preguntas, editor, diapositivas, diagrama, tarjetas de puntos ciegos) se apoyan en las anteriores y no redefinen los tokens.

## Interacción

- Controles nativos (`<input>`, `<button>`, `<details>`) antes que controles a medida.
- Foco visible en todo control operable; el teclado alcanza lo que alcanza el ratón.
- El retorno al agente es siempre un botón «copiar como prompt» con `navigator.clipboard.writeText` y feedback visible («Copiado» durante un segundo). El texto copiado es texto listo para pegar en la conversación, no HTML.
- Sin animación esencial; respeta `prefers-reduced-motion` desactivando transiciones decorativas.

## Accesibilidad

- HTML semántico: `<table>` con encabezados para datos, `<details>` para lo plegable, `<figure>` con `role="img"`, `aria-label` y `<figcaption>` para cada diagrama.
- La información esencial no depende solo del color: los estados llevan etiqueta o forma.
- Contraste: texto normal ≥ 4.5:1, texto grande y bordes significativos ≥ 3:1, medidos en el tema que se entrega.

## Revisión perceptiva

La verificación estática no ve si el artefacto se lee. Antes de declararlo entregado:

- Con un navegador automatizable —la skill `playwright-cli-usage` del repositorio indica cómo prepararlo; no es una dependencia de esta skill—, ejecuta `scripts/perceive.py <artefacto>` y revisa las capturas: mide el desborde horizontal a 390, 768 y 1440 px y recoge los errores de consola, pero no juzga la calidad.
- Si sale 3, no hay navegador: ábrelo con `open-artifact.sh` y pide a la persona que lo revise.
- En ambos casos, mira el primer viewport, 390, 768 y 1440 px, el foco visible, el contraste en los dos temas, el desborde horizontal y los estados vacíos. Corrige lo que veas antes de abrir la conversación de cierre.
- No declares una revisión visual que no has hecho: si no la hiciste, di quién la hará.

## Lista de comprobación final

Antes de entregar, comprueba:

1. Un único `.html` en `.explanations/`, sin ningún recurso externo (lo verifica `check-artifact.py`).
2. `<title>` con el asunto concreto del artefacto.
3. Bloque de procedencia completo: prompt, fecha, familia y fuentes; `enlaces` solo con hermanos relativos si forma un bucle (lo verifica `check-artifact.py`).
4. HTML bien formado: etiquetas balanceadas y `html`/`head`/`body` sin anidar mal (lo verifica `check-artifact.py`).
5. Primera pantalla: pregunta y respuesta principal visibles a 390, 768 y 1440 px.
6. Temas claro y oscuro legibles con el toggle `data-theme`, o un solo tema justificado; los pares texto/fondo avisados por contraste se corrigieron o se justifican.
7. Si se usaron tokens del proyecto, se copiaron sus valores en el `:root` con la precedencia persona → proyecto → plantilla, sin CSS enlazado.
8. Diagramas dentro de `<figure>` con etiqueta accesible y leyenda; cada `<text>` lleva su `fill` y el `viewBox` no deja espacio muerto a la derecha ni abajo.
9. Código dentro de `<pre><code>` con las clases de `highlight.py` y su CSS en línea una sola vez, sobre terminal oscuro (`--terminal*`).
10. Foco visible y teclado operable en controles.
11. Botón «copiar como prompt» funcional en los artefactos interactivos con retorno.
12. Sección «Desconocidos» presente cuando haya material no verificado; sin datos inventados en gráficos, tablas o cifras.
13. Fichero por debajo de 100 KB o contenido repartido en artefactos enlazados; si `check-artifact.py` avisó del tamaño, se atendió.
14. Índice regenerado al publicar con `publish.py`, con los enlaces del bucle visibles, y `lifecycle.py` ejecutado si hay vueltas antiguas.
15. Revisión perceptiva hecha con `perceive.py` —o delegada de forma explícita si sale 3— y dicha en el cierre con las anchuras miradas.
