# Diagramas técnicos premium con dos superficies

Contrato operativo de las diez plantillas de `assets/premium-diagrams/`. Cada archivo sirve sobre superficie oscura y clara sin editar colores: la calibración viaja en tokens CSS dentro del propio SVG. Se leen como base que se adapta, no como imagen cerrada: texto, color y estructura se sustituyen conservando la anatomía.

## Cuándo aplica

- Diagramas técnicos para superficie oscura o clara: arquitectura, topologías, pipelines, bucles, protocolos entre agentes, árboles de decisión, arcos de fases y reparto de capacidad.
- Piezas donde el diagrama es el contenido principal de una sección, una diapositiva o una cabecera de documentación.
- Casos que exigen lectura jerárquica: fases numeradas, mensajes entre componentes, ramas con desenlace.

## Cuándo no

- Sustituir a mano los colores de un atributo de presentación: rompe una de las dos superficies. El color se cambia en los tokens del `<style>`, nunca en el elemento.
- Mezclar las dos calibraciones en la misma página: un diagrama oscuro junto a uno claro compite y pierde la lectura de conjunto. Elige una superficie por página.
- Diagramas de datos que necesitan ejes, escalas o valores exactos: usa un gráfico, no una plantilla.
- Iconos, logotipos, ilustraciones o decoración: aplica la categoría correspondiente de [visual-assets](visual-assets.md).
- Diagramas pequeños (menos de ~640 CSS px de ancho): la tercera línea de texto deja de ser legible; simplifica o usa otra composición.
- Contenido que no cabe en la estructura de la plantilla: no fuerces quince nodos en un anillo de cinco.

## Lienzo y aislamiento

- Los diagramas se dibujaron en lienzos de 1200×760, 1400×840 y 1440×900. Las plantillas están recortadas al contenido con margen, por eso su `viewBox` no coincide con el lienzo original.
- `width`/`height` iguales al `viewBox` recortado; sin `preserveAspectRatio` forzado, sin fondo. El SVG escala por CSS.
- El fondo es transparente: ninguna forma cubre el `viewBox` completo. No añadas un `rect` de fondo; el contenedor decide el color.
- El margen interno del recorte va de 12 a 48 unidades. `modular-service-fabric` toca el borde superior; al reencuadrar, reserva 12 como mínimo por lado.

## Superficies: un archivo, dos calibraciones

Cada SVG lleva un `<style>` con las mismas custom properties dos veces: valores oscuros por defecto y valores claros en el bloque de override. La geometría, los textos, los ids y la semántica son idénticos en ambas.

- Oscuro por defecto: `.pd-<prefijo>, .pd-<prefijo>[data-surface="dark"], .pd-<prefijo>.surface-dark`.
- Claro explícito: `.pd-<prefijo>[data-surface="light"], .pd-<prefijo>.surface-light`.
- Claro automático: `@media (prefers-color-scheme: light) { .pd-<prefijo> { … } }`. Solo cambia la superficie cuando nadie ha fijado una.
- La clase propia (`.pd-rd`, `.pd-pf`, `.pd-hx`…) aísla los tokens de cada plantilla: varias pueden incrustarse en la misma página sin pisarse los nombres.
- Los atributos de presentación no aceptan `var()`: cada color de rol vive en `style="fill:var(--token)"` o `style="stroke:var(--token)"`, nunca en `fill="#hex"`. En el archivo no queda ningún hex de rol fuera del `<style>`; solo sobreviven `fill="none"` y las referencias `url(#…)` a degradados y filtros, que no dependen de la superficie.

| Uso | Cómo se incrusta | Superficie que aplica |
|---|---|---|
| SVG suelto | Abrir el `.svg` en el navegador | Sigue al sistema por la media query |
| Imagen | `<img src="…svg" alt="…">` | Sigue al sistema; el contenedor pone el fondo (casi negro o blanco) |
| Inline | Pegar el `<svg>` y poner `data-surface="light"` o `"dark"` en su raíz | La del atributo, gana sobre la media query; sin atributo, sigue al sistema |

- Una instancia por plantilla y documento: los ids no cambian entre superficies. Si necesitas la misma plantilla dos veces en una página, duplica el archivo, cambia el prefijo de ids y ajusta `data-surface`; nunca pegues el mismo SVG dos veces.
- El fondo lo decide el contenedor. Oscuro: `#080E1C`–`#0C1729`. Claro: `#FFFFFF` o el blanco roto de la página.
- `data-surface="dark"` existe para forzar oscuro cuando el sistema está en claro. Úsalo en la raíz del `<svg>` o con la clase `surface-dark` en el mismo elemento.

## Paleta y roles

Cada rol es un token. Cambiar la calibración es cambiar el valor del token en el `<style>`, no recorrer el dibujo. Familia canónica, usada por 6 de las 10 plantillas.

| Rol | Token | Oscuro | Claro | Dónde |
|---|---|---|---|---|
| Panel / tarjeta | `--panel` → `--panel-end` | `#14253A` → `#0C1729` | `#FFFFFF` → `#E9F0F7` | Relleno de tarjetas y nodos |
| Panel radial | `--panel` → `--panel-end` | `#111F34` → `#0B1526` | `#FFFFFF` → `#E8EFF6` | Variante de `radial-orchestration` |
| Borde de tarjeta | `--border` | `#293C55` (1.5) | `#C3D2E0` | Contorno de tarjeta y panel |
| Azul primario | `--blue-1` → `--blue-2` → `--blue-3` | `#57D5FF` → `#168BD5` → `#075397` | `#3DB5EC` → `#0F7FC7` → `#0A4E8C` | Cintas de flujo, estructura, hitos |
| Lima | `--lime-1` → `--lime-2` | `#E8FF79` → `#B8DC24` | `#C6E23B` → `#8FB312` | Acento, hito activo, barra de énfasis |
| Teal | `--ring-2`… / serie | `#1B7F88` → `#41D0C4` | `#14747C` → `#22A79B` | Estado alterno, segunda serie |
| Naranja de excepción | `--orange` | `#E3A65D` | `#C07E2F` | Rama de rechazo o revisión |
| Texto primario | `--text-1` / `--num` / `--title` | `#F2F9FF`, `#F3F8FF`, `#EFF8FF` | `#0B1B2B` | Títulos y etiquetas |
| Texto secundario | `--text-2` / `--sub` | `#A6C0D6`, `#89A6BF` | `#47647E` | Descripción de tarjeta |
| Texto terciario | `--text-3` / `--desc` | `#6E92AF` | `#4C6884` | Microcopy, unidades, leyenda |
| Acento de texto azul | `--accent` / `--kicker` | `#5ECAF5`, `#49C7FA` | `#0B6FA9` | Numeración de fase, kicker |
| Nodo / hub | `--node` / `--hub` / `--core` | `#0A1423`, `#0B1728`, `#0C1C2E` | `#FFFFFF` → `#E9F0F7` | Hub, círculo central |
| Borde de nodo | `--node-edge` | `#275D84` | `#B9CBDB` | Contorno de hub |
| Insignia | `--badge` / `--badge-edge` | `#12324D` / `#2D678C` | `#E3EDF7` / `#C3D2E0` | Píldoras de estado |
| Sombra | `--shadow` / `--shadow-alpha` | `#01050E` al 55 % | `#14304D` al 18 % | `fill` de tarjeta y nodo (`dy` 8, desenfoque 13) |
| Conector | `--connector` | `#3E607D`, `#263C54` | `#7C97AF` | Líneas finas, patillas |
| Pulso discontinuo | `--pulse` | `#9BE8FF` | `#2E9BD6` | Trazo discontinuo sobre la cinta |
| Arco de fondo | `--arc` / `--track` | `#102B45`, `#11273A` | `#D7E2EC` | Arco apagado y pista del anillo |
| Retícula | — | `#29455C` al 18 %, paso 44, trazo 0.8 | — | Eliminada al aislar |

Familia B, usada por `adaptive-delivery-loop`, `execution-arc`, `signal-distribution` y `modular-service-fabric`: los mismos roles con otros tokens. En oscuro, fondo `#091321` → `#111F34`; azul `#4AB7F0` → `#16629E`; lima `#E5F77D` → `#8BCF73`. En claro se aplica el mismo criterio: superficies `#FFFFFF`/`#E9F0F7`, tintas `#0B1B2B`/`#47647E`, bordes `#C3D2E0`, conectores `#7C97AF` y las series de cada plantilla.

Series que conservan su hue pero no su luminosidad, porque en claro el color de serie también carga texto:

| Plantilla | Oscuro | Claro |
|---|---|---|
| `signal-distribution` | `#D6EC37`, `#37B8EB`, `#246BA3`, `#34536D`, `#78D5E9` | `#C6E23B`, `#3DB5EC`, `#0A4E8C`, `#7C97AF`, `#7FD3E6` |
| `adaptive-delivery-loop` | `#B6E86E`, `#56C4AB`, `#2A9A9C`, `#217A87` | `#C6E23B`, `#58C4B2`, `#2E9C93`, `#14747C` |
| `execution-arc` | `#B8EB70`, `#79D8AA`, `#45B9AF`, `#278CAA`, `#2670A6` | `#C6E23B`, `#7FD3B4`, `#46BFAE`, `#2C93B4`, `#2E77AE` |

Dos tintas no figuran en la tabla porque solo existen en claro: `--lime-ink` `#557000` y `--orange-ink` `#8F5720`. Son el paso oscuro de lima y ámbar cuando el color lleva texto encima; el relleno sigue usando `#C6E23B`/`#8FB312` y `#C07E2F`. El terciario claro baja a `#4C6884` en vez del nominal `#5A7794` porque este mide 4.1:1 sobre el extremo oscuro del panel y no alcanza 4.5:1.

Semántica fija: azul = flujo y estructura; lima = hito, acento o resultado; teal = serie alterna; naranja = excepción. Cambiar el significado de un rol rompe la lectura. El recambio del par completo del degradado y de su tinta asociada mantiene la semántica; invertir un rol suelto no.

## Tipografía

- Pila única: `Inter, Segoe UI, Arial, sans-serif`. Sin fuentes incrustadas ni descargas; la pila resuelve a la sans del sistema.
- Escala real: 57 cifra principal · 29–34 título de hub · 22–26 título de tarjeta o cabecera · 17–20 etiqueta de fase · 14–16 cuerpo de tarjeta · 10–13 microcopy, unidades y leyenda.
- Pesos: 500–650 para cuerpo y descripción, 700–750 para numeración y kicker, 800–850 para títulos. No bajes de 500: la tercera línea se pierde en las dos superficies.
- Etiquetas en mayúsculas con `letter-spacing` de 1 a 2.5; el resto sin espaciado adicional.
- `text-anchor="middle"` dentro de nodos y círculos; `start` en tarjetas, con la numeración alineada a la izquierda.

## Sistema de tarjetas

- Tamaño típico 240–330 de ancho por 96–120 de alto, con radio 18–24. `radial-orchestration` usa filas tipo píldora de 88 de alto y radio 44; las piezas pequeñas, radios de 9 a 17.
- Barra de acento vertical a la izquierda: 5–6 de ancho, radio 3, altura completa de la tarjeta. Es el marcador de fase o de serie.
- Relleno con el gradiente de panel, borde `#293C55` de 1.5 y sombra en oscuro; borde `#C3D2E0`, relleno claro y sombra al 18 % en claro. El borde por sí solo no delimita (1.4:1 contra el panel en oscuro, 1.3:1 en claro): la separación la produce el contraste de relleno contra el fondo y la sombra.
- Contenido de tarjeta: numeración de fase, etiqueta en mayúsculas, una línea de descripción corta. Tres niveles como máximo.
- Las tarjetas de una misma serie comparten ancho y alto; la variación de tamaño solo marca jerarquía real.

## Trazos, conectores y nodos

- Conectores finos: 1.5–2. Cintas de flujo: banda exterior 22–94 con relleno oscuro o su equivalente claro y banda interior 11–42 con el gradiente azul; pulso discontinuo de 2–4 con `dasharray` `3 19` o `4 18`.
- Arcos de progreso: trazo 3; el arco de fondo usa `#102B45`/`#11273A` en oscuro y `#D7E2EC` en claro, y el activo el gradiente azul o lima.
- Cabezas de flecha con `marker` de 6×6, `refX` 8, trazo 1.7 y color de acento.
- Nodos: círculo blanco en claro y casi negro en oscuro, con borde de 2–9 según tamaño, sombra opcional y un solo elemento de texto destacado; la tinta se invierte con el nodo.
- Un conector nunca cruza una tarjeta ni un texto; si el recorrido lo exige, curva fuera del bloque.

## Retícula y márgenes

- Retícula de 44 unidades, trazo 0.8 al 18 %: solo en el lienzo de página, no en el diagrama aislado.
- Separación entre tarjetas de una lista: 20–40. Entre bloques: 48–80.
- Alineación: las tarjetas de una columna comparten eje `x`; los nodos de una órbita comparten radio y ángulos regulares.
- Centra la composición en el `viewBox`. El recorte busca equilibrio visual, no margen idéntico en los cuatro lados: evita que un lado quede vacío.

## Cómo adaptar

1. **Sustituir textos conservando la jerarquía.** Mantén el número de niveles y la longitud: etiqueta en mayúsculas de hasta 20 caracteres a 18–22; descripción de hasta 34 caracteres por línea y dos líneas como máximo a 12–15; numeración de dos dígitos. Estima el ancho antes de escribir: `≈ 0.58 × font-size × caracteres` para texto normal y `≈ 0.66 ×` para mayúsculas en peso 800; es una orientación, la medida real es el render. Si el texto no cabe, acorta o baja un nivel de detalle; no reduzcas el tamaño por debajo de 10.
2. **Recolorear cambiando tokens, no elementos.** Edita solo el `<style>`: el bloque por defecto y el bloque claro. Mantén el mismo nombre de token en los dos y cambia los dos extremos del mismo rol. Los degradados heredan el token en sus `stop`, así que un cambio de paleta no exige tocar cada forma. Después revisa que ningún `fill`/`stroke` haya vuelto a un hex literal: rompería la superficie contraria. Si añades un rol nuevo, añádelo como par oscuro/claro.
3. **Separar interfaz de diagrama.** Son interfaz y se quitan al aislar: fondo de página, retícula, cabecera con eyebrow, separadores horizontales, pies y numeración de página. En estas plantillas ya están eliminados, incluidos los `defs` que quedaban sin uso. Es diagrama lo que se conserva: nodos, tarjetas, conectores, numeración de fase, leyendas y píldoras de estado.
4. **Incrustar sin colisiones.** Cada plantilla lleva prefijo propio en todos sus `id` y en sus referencias `url(#…)` / `href="#…"`: `rd-`, `pf-`, `hx-`, `dt-`, `il-`, `mp-`, `sd-`, `sf-`, `ad-`, `ea-`. La variante clara no crea prefijos nuevos: es el mismo archivo. Escoge la superficie con `data-surface` en la raíz y no dupliques la plantilla en la misma página.
5. **Comprobar contraste en las dos superficies.** Medido sobre el relleno real. En oscuro, sobre panel `#14253A` y nodo `#0C1729`: primario 14.6:1, secundario 8.2:1, terciario 4.7:1, acento azul 8.3:1, lima 16.3:1, teal 9.4:1. En claro, sobre el extremo oscuro del panel `#E9F0F7` y sobre insignia `#E3EDF7`: primario 15.2:1, secundario 5.4:1, terciario 5.0:1, acento azul 4.7:1, lima de texto `#557000` 4.9:1, teal de texto `#14747C` 4.8:1, ámbar de texto `#8F5720` 5.0:1. Texto blanco solo sobre el extremo oscuro del azul (`#0A4E8C`, 8.5:1); sobre `#3DB5EC` la tinta es oscura (7.5:1). En el anillo de `signal-distribution`, la tinta oscura rinde 11.9:1 sobre lima, 7.5:1 sobre azul, 5.7:1 sobre slate y 10.3:1 sobre cian; el 19 % va en blanco sobre `#0A4E8C`. El texto normal exige 4.5:1; el texto grande (24 px o más, o 18.67 px en negrita) admite 3:1. Los números de 29 px de `execution-arc` sobre las cuñas más oscuras quedan en 3.6:1 y 4.9:1: son texto grande y cumplen, pero no bajes su tamaño. Un texto que transmite información no es decorativo aunque sea pequeño. Los bordes de tarjeta no son indicadores necesarios; si un estado depende de un borde, súbelo a 3:1.
6. **Fijar el ancho mínimo.** La plantilla está pensada para 900 CSS px de ancho o más. Entre 640 y 900, elimina el tercer nivel de texto y aumenta los tamaños restantes en un paso. Por debajo de 640, usa una composición lineal, no esta.

## Catálogo

Una plantilla por diagrama, con las dos superficies en el mismo archivo.

| Archivo | Tipo | viewBox | Prefijo | Clase | Mejor uso |
|---|---|---|---|---|---|
| `radial-orchestration.svg` | Topología radial con hub | 1275×688 | `rd-` | `pd-rd` | Orquestador que delega en N servicios, con detalle por tarjeta |
| `pipeline-flow.svg` | Pipeline secuencial en onda | 1312×499 | `pf-` | `pd-pf` | Proceso de cinco etapas con subdetalle bajo cada nodo |
| `hexagonal-architecture.svg` | Arquitectura hexagonal | 1082×826 | `hx-` | `pd-hx` | Puertos y adaptadores, núcleo de dominio, fronteras por capas |
| `decision-tree.svg` | Árbol de decisión | 1200×633 | `dt-` | `pd-dt` | Flujo con dos comprobaciones, ramas y desenlaces |
| `improvement-loop.svg` | Bucle cerrado | 1005×482 | `il-` | `pd-il` | Ciclo de cuatro fases que se repite |
| `multiagent-protocol.svg` | Secuencia de mensajes | 1400×641 | `mp-` | `pd-mp` | Protocolo request/response entre agentes |
| `signal-distribution.svg` | Anillo segmentado y lista | 1076×560 | `sd-` | `pd-sd` | Reparto de capacidad o cuota entre cinco áreas |
| `modular-service-fabric.svg` | Cadena isométrica de módulos | 1124×514 | `sf-` | `pd-sf` | Servicios encadenados con servicios de apoyo |
| `adaptive-delivery-loop.svg` | Anillo de fases con lista | 1174×633 | `ad-` | `pd-ad` | Ciclo con panel de fases y centro de estado |
| `execution-arc.svg` | Arco de progreso | 1024×676 | `ea-` | `pd-ea` | Hitos sobre un arco con estado actual |

## Checklist de cierre

1. XML válido y `viewBox` propio; `width`/`height` coherentes con el recorte.
2. Todos los `id` con prefijo de plantilla y únicos; toda referencia `url(#…)` y `href="#…"` resuelve dentro del archivo.
3. Sin recursos externos: ni `http`, ni `<image>`, ni fuentes incrustadas o descargadas; solo la pila genérica.
4. Fondo transparente: ningún `rect`, `path` o `circle` cubre el `viewBox`; el fondo lo pone el contenedor.
5. `<title>` y `<desc>` en castellano, concretos, y `role="img"` en el `svg`.
6. Ningún hex de rol fuera del `<style>`: todo color de superficie es un token y las formas lo consumen con `var()`.
7. Las dos superficies renderizadas: oscura sobre fondo casi negro y clara sobre blanco. Ni textos lavados, ni sombras sucias, ni formas que desaparecen, ni un lienzo oscuro sobre página clara.
8. Contraste medido en ambas: normal ≥4.5:1, grande ≥3:1, sobre el relleno real; el blanco solo sobre azul oscuro.
9. Los tres caminos probados: SVG suelto, `<img>` y SVG inline con `data-surface` en las dos superficies; el atributo explícito gana a la preferencia del sistema.
10. Cada texto cabe en su forma y la jerarquía tiene tres niveles como máximo, con un solo nivel display por diagrama; compruébalo renderizando a tamaño real, no contando caracteres.
11. Recorte con margen de al menos 12 unidades, composición centrada e inspección a 100 % y al ancho de uso. El XML válido no demuestra calidad visual.
