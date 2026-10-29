---
name: SKILLS-AGP
description: Sistema visual del catálogo y las páginas de skill, un instrumento de medida en dos temas.
colors:
  verification-teal: "#0f766e"
  signal-blue: "#2563eb"
  instrument-cyan: "#0891b2"
  ledger-violet: "#7c3aed"
  paper: "#f8fafc"
  surface: "#ffffff"
  surface-sunken: "#f1f5f9"
  ink: "#0f172a"
  ink-muted: "#5f6b80"
  line: "#e2e8f0"
  line-strong: "#cbd5e1"
  terminal: "#0a0f1c"
  terminal-surface: "#111827"
  terminal-line: "#1f2937"
  terminal-ink: "#e5e7eb"
  signal-ok: "#10b981"
  signal-warn: "#f59e0b"
  signal-error: "#b91c1c"
typography:
  display:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(34px, 6vw, 62px)"
    fontWeight: 800
    lineHeight: 1.04
    letterSpacing: "-0.035em"
  headline:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "clamp(22px, 3vw, 28px)"
    fontWeight: 700
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "17px"
    fontWeight: 700
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "11.5px"
    fontWeight: 700
    letterSpacing: "0.06em"
  mono:
    fontFamily: "JetBrains Mono, ui-monospace, SF Mono, Fira Code, Menlo, Consolas, monospace"
    fontSize: "12.9px"
    fontWeight: 400
    lineHeight: 1.72
rounded:
  inline: "6px"
  control: "10px"
  panel: "16px"
  pill: "999px"
  circle: "50%"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  2xl: "48px"
  3xl: "64px"
  gutter: "clamp(16px, 4vw, 40px)"
components:
  button-primary:
    backgroundColor: "{colors.verification-teal}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    padding: "11px 18px"
  button-ghost:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "11px 18px"
  icon-button:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    height: "36px"
    width: "36px"
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.panel}"
    padding: "20px"
  skill-card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.panel}"
    padding: "18px 18px 15px"
  pill:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink-muted}"
    rounded: "{rounded.pill}"
    padding: "5px 12px"
  code-block:
    backgroundColor: "{colors.terminal}"
    textColor: "{colors.terminal-ink}"
    rounded: "{rounded.panel}"
    padding: "16px 52px 16px 18px"
  verify-panel:
    backgroundColor: "{colors.terminal}"
    textColor: "{colors.terminal-ink}"
    rounded: "20px"
    padding: "clamp(24px, 3.6vw, 38px)"
  to-top:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.circle}"
    size: "44px"
---

# Design System: SKILLS-AGP

## Overview

**Creative North Star: "El banco de pruebas"**

La documentación se lee como el panel de un banco de pruebas: superficies neutras, líneas finas que separan lo que se mide, un número por sección y un verde que solo se enciende cuando algo se ha comprobado. El color no adorna; identifica. Cada skill trae su propio acento, como cada instrumento del banco lleva su etiqueta, y el verde de verificación queda reservado para el estado.

La densidad es la de un manual técnico bien impreso: párrafos de 60 a 75 caracteres, tablas que se leen de un vistazo, bloques de código oscuros que contrastan con el papel claro. Nada compite con la prosa, porque el lector viene a entender un contrato y a comprobar cómo se cierra.

La elevación es discreta y siempre ambigua entre borde y sombra: las tarjetas se apoyan con una sombra ambiental de pocos píxeles y se delimitan con una línea de un píxel. El movimiento existe para confirmar una acción (un botón que sube 1 px al pasar, una copia que se marca en verde) y se apaga entero con `prefers-reduced-motion`.

La anti-referencia confirmada es el escaparate de marketing: ni testimonios, ni logos de clientes, ni métricas de adopción, ni cifras de rendimiento. Lo que no existe no se representa, y un dato sin fuente no ocupa espacio.

**Key Characteristics:**
- Un acento por familia de skill; el verde de verificación nunca es decoración.
- Tema claro y oscuro con los mismos nombres de token y valores intercambiados.
- Tipografías del sistema, cero descargas; el registro mono para nombres de skill y rutas.
- Bordes de 1 px, radios de 16 px en paneles y 10 px en controles, sombras suaves.
- Página de skill: barra fija, hero con halo, índice lateral y secciones numeradas.

## Colors

Paleta de instrumento: neutros fríos de papel y tinta, un verde que mide y una familia de acentos que etiqueta.

### Primary

- **Verde de verificación** (#0f766e): acento del catálogo y de las skills sin color propio (`git-flow-management`, `best-practices-create-skills`, `typescript-testing-and-verification`). En oscuro sube a `#2dd4bf`. Es también el color del punto de estado del pill y de los checks del hero, con `signal-ok` (#10b981) para el punto.

### Secondary

- **Azul de señal** (#2563eb): segundo acento del catálogo y de casi todas las páginas; en oscuro `#60a5fa`. Aparece en el degradado del botón primario y en el segundo halo del hero.

### Tertiary

- **Cian de instrumento** (#0891b2): tercer halo del hero y acento de `javascript-testing-and-verification`. En oscuro `#22d3ee`.
- **Violeta de registro** (#7c3aed): cuarto halo del catálogo y acento de `go-idiomatic-style` y `skill-creator`. En oscuro `#a78bfa`.

### Neutral

- **Papel** (#f8fafc): fondo de página en claro. En oscuro lo sustituye `terminal` (#0a0f1c).
- **Superficie** (#ffffff): fondo de tarjetas, tablas y controles. En oscuro `terminal-surface` (#111827).
- **Superficie hundida** (#f1f5f9): cabeceras de tabla, código en línea y fondos de apoyo. En oscuro `terminal-line` (#1f2937).
- **Tinta** (#0f172a): texto principal. En oscuro `terminal-ink` (#e5e7eb).
- **Tinta atenuada** (#5f6b80): prosa secundaria, etiquetas y metadatos. En oscuro `#94a3b8`.
- **Línea** (#e2e8f0): separadores de 1 px y bordes de tarjeta. En oscuro `#334155`.
- **Línea fuerte** (#cbd5e1): bordes de controles y del pill. En oscuro `#475569`.
- **Terminal** (#0a0f1c), **terminal-surface** (#111827) y **terminal-line** (#1f2937): el bloque de código es oscuro en ambos temas, con borde `#1f2937` y texto `#e5e7eb`.

### Señales

- **Verde de estado** (#10b981), **ámbar de aviso** (#f59e0b) y **rojo de error** (#b91c1c). Llevan texto solo en su variante oscurecida (`--ok-text` #047857, `--warn-text` #b45309, `--error-text` #b91c1c), que mantiene AA sobre papel claro. En oscuro: `#34d399`, `#fbbf24`, `#f87171`.

### Acento por familia

Cada página de skill declara su `--accent` y un `--accent-2` derivado. Los valores vivos:

| Skill | Acento | Segundo |
|---|---|---|
| `adr-software` | #92400e | #d97706 |
| `best-practices-create-skills` | #0f766e | #2563eb |
| `document-management-software` | #1e40af | #0ea5e9 |
| `document-redactor` | #9b2c4a | #b45309 |
| `git-flow-management` | #0f766e | #2563eb |
| `go-cli-ai-first` | #0369a1 | #2563eb |
| `go-errors-and-lifecycle` | #c2410c | #b91c1c |
| `go-idiomatic-style` | #6d28d9 | #2563eb |
| `go-testing-and-verification` | #15803d | #0d9488 |
| `javascript-idiomatic-style` | #b45309 | #d97706 |
| `javascript-testing-and-verification` | #0e7490 | #0891b2 |
| `prd-cartographer` | #1e40af | #0ea5e9 |
| `python-idiomatic-style` | #2b5b84 | #3b82f6 |
| `python-testing-and-verification` | #a16207 | #d97706 |
| `security-engineering` | #9f1239 | #be123c |
| `skill-creator` | #6d28d9 | #2563eb |
| `typescript-idiomatic-style` | #1d4ed8 | #2563eb |
| `typescript-testing-and-verification` | #0f766e | #2563eb |
| `web-interface-visual-design` | #1e40af | #2563eb |

En tema oscuro el acento se aclara para sobrevivir al fondo: `#fcd34d` en `adr-software`, `#2dd4bf` en las de verde, `#fbbf24` en las ámbar.

### Named Rules

**La regla del verde de verificación.** El verde solo aparece donde algo se comprueba: el punto de estado, los checks del hero, el aviso de copia correcta y las marcas `ok` de la sección de Verificación. Usarlo como decoración de una tarjeta es un error.

**La regla del acento prestado.** Una página usa el acento de su skill, nunca el de otra. El catálogo es la única superficie con el verde como acento global, y lo comparte con las skills que no tienen color propio.

**La regla del halo teñido.** Los halos del hero y del panel de verificación se derivan del acento con `color-mix` al 20-26 %; nunca se escriben como un color suelto.

## Typography

**Display Font:** Inter, con pila del sistema (ui-sans-serif, system-ui, Segoe UI, Roboto, Arial)
**Body Font:** la misma pila
**Label/Mono Font:** JetBrains Mono, con pila de monosistema (ui-monospace, SF Mono, Fira Code, Menlo, Consolas)

**Character:** una sola familia para todo el texto y un mono para lo que identifica máquinas: nombres de skill, rutas, comandos y números de paso. La jerarquía se construye con tamaño, peso y espacio de letra, no con familias distintas.

### Hierarchy

- **Display** (800, `clamp(34px, 6vw, 62px)`, 1.04, -0.035em): el `h1` del hero. En el catálogo el degradado del tramo final va en `.grad`; en las páginas de skill, en tinta de acento.
- **Headline** (700, `clamp(22px, 3vw, 28px)`, -0.02em): el `h2.title` de cada sección, siempre junto a un recuadro numerado de 30×30.
- **Title** (700, 17px, -0.01em): los `h3` dentro de una sección y los títulos de tarjeta.
- **Body** (400, 16px, 1.65): prosa, con el `p.sub` de sección limitado a 74ch y el `p.lead` del hero a 660px.
- **Label** (700, 11.5px, 0.06em, mayúsculas): cabeceras de tabla, títulos del índice lateral y la etiqueta «repo» con borde discontinuo.
- **Mono** (400, 12.9px, 1.72): bloques de código, código en línea, rutas y el nombre de cada skill en su tarjeta (14.2px, 750).

### Named Rules

**La regla del nombre en mono.** Todo lo que un agente o un lector copiaría va en la pila mono: `src/<skill>/`, comandos, identificadores. La prosa no usa mono ni para énfasis.

**La regla de la tipografía no descargada.** No hay `@font-face` ni petición a un CDN de fuentes. Si Inter o JetBrains Mono no están instaladas, la pila del sistema las sustituye sin cambio de métrica visible.

## Layout

Contenedor de 1180px con relleno lateral `clamp(16px, 4vw, 40px)`. El hero del catálogo usa esos 1180px en dos columnas desde 960px (texto y pieza ilustrativa); el de una página de skill es de una columna y limita a 1080px. La página de skill pasa a dos columnas desde 1020px: índice de 214px y contenido flexible, separados por 56px.

El ritmo vertical es constante: 64px entre secciones, 24px entre bloques hermanos, 16px en las rejillas y 12px entre elementos de una misma lista. Las tarjetas de skill se reparten en 1, 2 o 4 columnas según el ancho; las de contenido, en 1 o 2; la infografía de anatomía pasa a 3 columnas desde 1080px.

Puntos de ruptura observados: 480, 560, 620, 640, 720, 760, 860, 900, 960, 1020, 1080 px. La navegación superior aparece a 860px y el índice lateral a 1020px; por debajo de 560px el botón de catálogo se queda en icono de 36px.

**La regla del índice que no se convierte en menú.** En pantallas estrechas el índice lateral desaparece; no se sustituye por un desplegable ni por una barra de secciones. El lector que necesita saltar usa el botón de volver arriba y el buscador del navegador.

## Elevation & Depth

Sistema híbrido, con el borde como primera señal de profundidad y la sombra como segunda. Las superficies son planas en reposo y se apoyan con una sombra ambiental de baja opacidad; ninguna sombra dura, ningún `inset` salvo la línea interior de los bloques de código del catálogo.

### Shadow Vocabulary

- **Ambiental** (`box-shadow: 0 1px 2px rgba(15, 23, 42, .05), 0 8px 24px -12px rgba(15, 23, 42, .18)`): tarjetas, tablas, controles y bloques de código en reposo.
- **Elevada** (`box-shadow: 0 20px 60px -30px rgba(15, 23, 42, .35)`): el panel de verificación del catálogo y el botón primario al pasar el cursor.
- **En oscuro** las dos suben de opacidad (`rgba(0, 0, 0, .4)` y `.8`), porque el fondo no aporta contraste propio.

**La regla del borde antes que la sombra.** La profundidad se comunica primero con una línea de 1 px; la sombra solo separa una superficie del papel. Una tarjeta sin borde y solo con sombra no pertenece a este sistema.

**La regla de la elevación sin rango.** La sombra no ordena importancia. Dos tarjetas del mismo tamaño llevan la misma sombra aunque una sea más relevante; la relevancia se marca con el acento y con la posición.

## Shapes

Radio de 16px para paneles (tarjetas, tablas, bloques de código), 10px para controles (botones, iconos, recuadros de paso), 8px en las esquinas interiores de los elementos del índice y 6px en el código en línea. Las píldoras son de 999px y el botón de volver arriba es un círculo de 44px.

El lenguaje de forma es de esquinas redondeadas pequeñas y consistentes: nada de esquinas vivas ni de radios grandes que conviertan una tarjeta en una burbuja. Dos gestos dan identidad: la franja de 3px en el borde superior de cada tarjeta de skill, teñida con su acento, y el recuadro numerado de 9px de radio junto a cada título de sección.

Las tarjetas de skill llevan además un degradado de 166° desde el 8 % del acento hacia la superficie; ese tinte solo alcanza la mitad superior y no se repite en ningún otro componente.

El hero del catálogo superpone una rejilla de 56px en `line-strong` al 45 % de opacidad, enmascarada con un degradado radial que la apaga hacia la mitad de la página. Es textura de fondo, no estructura: no se dibuja sobre una página de skill ni sobre un panel.

## Components

### Buttons

- **Shape:** rectángulo de 10px de radio, altura derivada del relleno, 11px arriba y abajo.
- **Primary:** degradado de 135° entre el acento, el segundo acento y el violeta en el catálogo (en las páginas de skill, solo los dos primeros) con texto blanco y la sombra ambiental.
- **Hover / Focus:** sube 1px, refuerza la sombra y quita el subrayado. El foco visible es un contorno de 2px del acento con 3px de separación.
- **Ghost:** superficie blanca, borde de 1px en línea fuerte, texto en tinta. Dentro del panel oscuro invierte a blanco al 4 % con borde `#334155`.

### Chips

- **Style:** píldora de 999px, fondo de superficie, borde de 1px en línea fuerte, texto de 12.5px en tinta atenuada, con un punto de estado de 7px en verde y halo del 22 %.
- **Variantes:** la etiqueta de repositorio es de 11.5px, mayúsculas, borde discontinuo y sin relleno; la etiqueta de familia de una tarjeta usa el 8 % del acento como fondo y el 32 % como borde, con texto derivado al 58 % del acento.

### Cards / Containers

- **Corner Style:** 16px en tarjetas de contenido, 10px en recuadros de paso y en elementos de rejilla.
- **Background:** superficie blanca en claro, `terminal-surface` en oscuro; la tarjeta de skill añade el degradado teñido descrito en Shapes.
- **Shadow Strategy:** ambiental en reposo, elevada solo en el panel de verificación.
- **Border:** 1px en línea; la tarjeta de skill sustituye el borde superior por 3px del acento al 80 %.
- **Internal Padding:** 20px en tarjetas de contenido, 18px arriba y lados con 15px abajo en las de skill, 16px en los pasos de flujo.

### Tables

Cabecera en superficie hundida con etiquetas de 11.5px en mayúsculas; filas separadas por 1px de línea, la última sin borde; el hover tiñe la fila con el 3 % del acento. Envoltorio con borde, radio y sombra, desplazamiento horizontal propio para no romper la página. Por debajo de 640px la primera columna deja de ser `nowrap`.

### Code blocks

Fondo terminal en ambos temas, borde `#1f2937`, 16px de relleno con 52px a la derecha para el botón. El botón de copiar mide 30px de alto, vive en la esquina y está oculto hasta el hover o el foco; en pantallas sin hover se muestra siempre. Al copiar, el texto y el borde pasan a verde de estado durante un instante.

### Callouts

La nota es una banda con borde izquierdo de 1px del acento, fondo al 10 % del acento y esquinas redondeadas solo a la derecha. Se usa para lo que cambia el resultado de un paso, no para repetir lo que ya dice la tabla.

### Navigation

Barra fija de 12px de relleno vertical, fondo al 82 % con desenfoque de 14px y borde inferior. La marca es un icono de 34px con 10px de radio, el nombre en 15px/700 y un subtítulo de 11px en mayúsculas. La navegación del catálogo aparece a 860px en pastillas de 8px; el índice lateral marca el ítem activo con el acento, borde izquierdo de 2px y fondo al 10 %.

### Signature components

**Anatomía de una skill.** La única pieza ilustrativa del sitio, y no se reutiliza como decoración. Marco de 16px de radio con tres halos (16 %, 14 % y 12 % de los tres acentos), retícula de puntos de 20px en `line`, borde en `line-strong` y una barra superior de 3px con cuatro paradas (verde, azul al 42 %, violeta al 74 %, naranja `#c2410c`). Dentro: entrada de 18×24px con borde al 38 % del azul, conector de 2px en degradado con la etiqueta en una píldora de 20px, y paquete con borde discontinuo al 55 % del acento. El núcleo se limita a 460px, lleva 22px de relleno, 14px de radio y un borde de 2px resuelto con degradado en `border-box`; su nombre va en mono de 21px. Los tres nodos de recursos son columnas de 18×12px con borde al 42 % del cian y un raíl horizontal de 2px que los une. El bloque de lo que queda fuera del paquete es el único con borde izquierdo violeta. La entrada en pantalla sigue el orden de lectura: entrada, conector que se dibuja, paquete, núcleo y recursos; cada nodo se eleva 2px y su icono crece un 6 % al pasar el cursor, con `prefers-reduced-motion` dejando el diagrama estático y visible.

**Panel de verificación.** Cierre del catálogo y nada más: 20px de radio, 38px de relleno, borde `#1f2937` y sombra elevada sobre `terminal`, con tres halos radiales en `rgba(20, 184, 166, .16)`, `rgba(37, 99, 235, .18)` y `rgba(124, 58, 237, .18)`. La etiqueta es de 11px en mayúsculas con 0.11em y un punto verde de 6px con halo de 3px; el título, de 28px en `#f8fafc`; la lista de comprobaciones, de 13.3px en `#cbd5e1` con checks de 13px. A la derecha, un bloque de código de 12.9px con los comandos de la puerta en `#5eead4` y los comentarios en `#64748b`. Los ocho componentes de este sistema tienen su fragmento autocontenido en `.impeccable/design.json`.

## Do's and Don'ts

### Do:

- **Do** declarar el acento de cada página en `:root` y derivar de él halos, tintes y bordes con `color-mix`.
- **Do** mantener el par claro/oscuro con los mismos nombres de token; cambiar valores, no estructura.
- **Do** usar `--radius` (16px) en paneles y `--radius-sm` (10px) en controles.
- **Do** apoyar cada superficie con 1px de borde además de la sombra ambiental.
- **Do** poner en mono los nombres de skill, rutas y comandos, y en 700/11.5px en mayúsculas las etiquetas.
- **Do** limitar la prosa a 74ch y el `lead` a 660px.
- **Do** apagar animaciones y transiciones con `prefers-reduced-motion`.

### Don't:

- **Don't** representar lo que no existe: ni testimonios, ni logos de clientes, ni métricas de adopción, ni cifras de rendimiento.
- **Don't** usar el verde de verificación como color de una familia ni como relleno decorativo.
- **Don't** descargar tipografías, iconos ni scripts: el sitio es HTML, CSS y JavaScript propios.
- **Don't** introducir un color fuera de los tokens de acento: los 17 acentos son la paleta permitida.
- **Don't** sustituir el índice lateral por un menú desplegable en pantallas estrechas.
- **Don't** usar sombras duras, biseles ni degradados ajenos al halo del hero y al botón primario.
- **Don't** añadir una segunda familia tipográfica para compensar la falta de una fuente descargada.
