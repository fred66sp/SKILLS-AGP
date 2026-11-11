---
name: explain-html
description: "Genera artefactos HTML autocontenidos —informes, explicadores, cuestionarios, prototipos, diagramas, presentaciones, comparaciones y editores a medida— en .explanations/ del proyecto y los abre en el navegador para revisarlos. Se usa cuando se pide un informe o estado, un cuestionario, un prototipo interactivo, un diagrama o flujo, una presentación, un explicador o un editor desechable con exportación «copiar como prompt»; también ante encargos vagos o revisiones a ciegas: pase de puntos ciegos, entrevista de requisito ambiguo, bitácora de desviaciones, cuestionario de merge o pitch de compra. Cada artefacto es un .html sin dependencias externas que funciona por file:// y separa hechos verificados de desconocidos. No se usa para documentación duradera del repositorio (eso es document-management-software), para la identidad y el sistema visual de un producto (design-system-architect), para implementar una interfaz real (web-interface-visual-design) ni para mantener un catálogo de informes publicado."
metadata:
  version: "0.6.0"
---

# explain-html: artefactos HTML explicativos

Convierte un encargo —un informe, un cuestionario, un prototipo interactivo, un diagrama, una presentación, un explicador o un editor a medida— en un único fichero HTML autocontenido en `.explanations/` del proyecto y lo abre en el navegador para que la persona lo revise e interactúe con él. Un documento que se abre y se navega comunica mejor que un muro de Markdown: cambia el medio y cambia la probabilidad de que alguien lo lea.

## Responsabilidad y límites

- Produce artefactos de revisión, no producto duradero: viven en `.explanations/`, pueden regenerarse o borrarse sin pérdida. El conocimiento verificado vuelve al proyecto por la conversación o por la exportación «copiar como prompt»; nunca modificando ficheros fuera de `.explanations/`.
- Un encargo genera un artefacto nuevo con nombre nuevo. No sobrescribe ni edita un artefacto existente sin instrucción explícita; si el encargo es una nueva vuelta sobre el anterior, crea `<slug>-v2.html` y conserva el primero. El nombre del artefacto final lo decide siempre el encargo; la plantilla solo aporta la estructura.
- Autocontención total: sin CDN, sin `<script src>` ni `<link>` a red, sin fuentes remotas, sin imágenes por URL. Todo CSS, JS y SVG va en línea y toda imagen es `data:` o SVG incrustado. El artefacto debe funcionar igual abierto por `file://` que servido por HTTP.
- Procedencia obligatoria: cada artefacto lleva dentro, al inicio del body, un comentario `<!-- procedencia: {...} -->` con prompt, fecha, familia y fuentes. `check-artifact.py` no lo deja pasar vacío. Sin él, el índice no puede fechar ni clasificar el artefacto y el cierre no puede decir de dónde salió.
- No inventa datos: cada cifra, estado, fecha y relación del artefacto sale del material fuente o queda en la sección «Desconocidos». No rellena huecos con lo plausible; un gráfico sin datos reales no se dibuja.
- No mantiene un catálogo publicado: `.explanations/index.html` es un índice local regenerable, no una aplicación ni documentación duradera.
- Puede usar el sistema visual del proyecto destino sin romper la autocontención: copia sus valores como custom properties en el `:root` del artefacto. Nunca enlaza su CSS ni una fuente externa; la precedencia es intención de la persona → sistema del proyecto → defaults de la plantilla.
- Puede formar un bucle de varios artefactos —exploración → plan → mockups— como memoria del razonamiento, con enlaces relativos entre ficheros hermanos de `.explanations/`. Cada página del bucle pasa la verificación por separado; el índice los lista con la relación que declaren en `enlaces`.
- Delega lo que no es suyo: documentación duradera del repositorio a `document-management-software`; identidad y sistema visual de un producto a `design-system-architect`; implementar una interfaz real a `web-interface-visual-design`. Si el artefacto es un paso previo —explorar, decidir, probar, comunicar— es de esta skill.
- La especificación no es suya: el ciclo de vida de un árbol SDD —crearlo, mantenerlo, aprobarlo— lo gobiernan las skills de la herramienta que lo generó (openspec, Kiro, Spec Kit y sus propias instrucciones). Aquí solo se lee, y la documentación duradera del proyecto sigue siendo de `document-management-software`. La vista `sdd` es de revisión, desechable y regenerable: no sustituye a la spec.

## Familias de artefacto

| Encargo | Familia (slug) | Plantilla | Representación principal |
|---|---|---|---|
| Comparar enfoques, direcciones o planes | Exploración comparativa (`exploracion`) | `plantilla-exploracion.html` | Cuadrícula de opciones lado a lado, cada una con su concesión anotada |
| Explicar cómo funciona un mecanismo, módulo o concepto | Explicador (`explicador`) | `plantilla-explicador.html` | TL;DR + recorrido plegable + diagrama + trampas |
| Informar estado, evolución o incidente | Informe (`informe`) | `plantilla-informe.html` | Cronología o tabla + mini-gráfico SVG |
| Dibujar flujo, arquitectura, secuencia o proceso | Diagrama (`diagrama`) | `plantilla-diagrama.html` | SVG en línea o pipeline CSS |
| Probar una animación, una interacción o un flujo clicable | Prototipo (`prototipo`) | `plantilla-prototipo.html` | Página interactiva con deslizadores y controles |
| Preguntar, evaluar o autocorregir | Cuestionario (`cuestionario`) | `plantilla-cuestionario.html` | Preguntas con corrección en vivo y resultado exportable |
| Reordenar, clasificar, editar valores o afinar texto | Editor a medida (`editor`) | `plantilla-editor.html` | Formulario sobre el dato concreto + exportación |
| Presentar en una reunión | Presentación (`presentacion`) | `plantilla-presentacion.html` | Secciones a pantalla completa navegables con teclado |
| Revisar una especificación antes o durante su implementación (árbol de proposal/specs/deltas/design/tasks, venga de OpenSpec, Kiro, Spec Kit o de Markdown propio) | Especificación SDD (`sdd`) | `plantilla-sdd.html` | Vista de revisión: fases del pipeline, fichas de requisito con GIVEN/WHEN/THEN, progreso de tareas, hallazgos, desconocidos y trazabilidad cuando el documento la declara |
| No sé qué no sé sobre un territorio del proyecto | Pase de puntos ciegos (`blindspots`) | `plantilla-blindspots.html` | Cartas de desconocido desconocido con evidencia y prompt desbloqueador, ensambladas en un prompt de implementación mejorado |
| Un encargo ambiguo que hay que acotar antes de generar nada | Entrevista (`entrevista`) | `plantilla-entrevista.html` | Preguntas una a una ordenadas por radio de explosión, tabla de decisiones y prompt final copiable |

Para la familia elegida lee la sección correspondiente de [artifact-patterns](references/artifact-patterns.md) antes de generar y copia su plantilla de `assets/`. Usa [plantilla-artefacto](assets/plantilla-artefacto.html), el esqueleto base, solo si el encargo no encaja en ninguna familia.

## Descubrir los desconocidos

La tabla anterior serializa lo que ya se sabe: qué forma tiene el encargo y qué plantilla le toca. Hay encargos en los que el problema no es elegir familia, sino que nadie sabe todavía qué preguntar. Estos artefactos no representan conocimiento: lo descubren.

El eje es temporal, no temático. **Antes de implementar** se usan el pase de puntos ciegos —cartas de desconocido desconocido sobre un territorio—, la entrevista —preguntas por radio de explosión—, la dirección con steal/skip, el mock antes de cablear, el plan que se espera retocar y el mapa de la referencia a portar. **Durante** se lleva una bitácora de desviaciones del plan. **Después** aparecen el pitch que pre-responde objeciones y el cuestionario antes de un merge: el trabajo ya está hecho y toca defenderlo o comprobarlo.

Ofrécelos proactivamente, sin esperar a que la persona los pida, cuando el encargo llegue vago, cuando el territorio sea desconocido para el agente, cuando el plan en curso se esté desviando o la víspera de un merge. Un encargo que se acota con tres preguntas no necesita tres artefactos: elige el más pequeño que desbloquee la siguiente decisión.

| Momento | Artefacto | Familia | Se documenta en |
|---|---|---|---|
| Antes de implementar | Pase de puntos ciegos: cartas con evidencia y prompt que desbloquea | `blindspots` | [Pase de puntos ciegos](references/artifact-patterns.md#pase-de-puntos-ciegos) |
| Antes de implementar | Entrevista: preguntas por radio de explosión, decisiones y prompt final | `entrevista` | [Entrevista](references/artifact-patterns.md#entrevista) |
| Antes de implementar | Brainstorm con respuestas ensamblables; dirección con steal/skip | `exploracion` | [Familia prestada](references/artifact-patterns.md#artefactos-de-desconocidos-con-familia-prestada) |
| Antes de implementar | Mapa de la referencia a portar | `explicador` | [Familia prestada](references/artifact-patterns.md#artefactos-de-desconocidos-con-familia-prestada) |
| Durante | Bitácora de desviaciones del plan | `informe` | [Familia prestada](references/artifact-patterns.md#artefactos-de-desconocidos-con-familia-prestada) |
| Después | Pitch que pre-responde objeciones; cuestionario antes de un merge | `informe`, `cuestionario` | [Familia prestada](references/artifact-patterns.md#artefactos-de-desconocidos-con-familia-prestada) |

Mismos invariantes que el resto: procedencia completa, `check-artifact.py` en verde y autocontención total. La diferencia está en el cierre: en estos artefactos lo normal es que el objetivo sea la exportación «copiar como prompt» —el prompt de implementación, las decisiones acordadas, las preguntas sin responder— para devolver el descubrimiento a la conversación.

## Metadatos de procedencia

Todo artefacto empieza el body con este comentario (la plantilla ya lo trae vacío):

```html
<!-- procedencia: {"prompt": "Pásame el estado de la semana",
     "fecha": "2026-11-08", "familia": "informe",
     "fuentes": ["git log", "src/x.py:12"]} -->
```

| Campo | Contenido |
|---|---|
| `prompt` | El encargo que originó el artefacto, en una línea |
| `fecha` | Día de generación en `AAAA-MM-DD` |
| `familia` | Uno de los once slugs de la tabla anterior |
| `fuentes` | Lista no vacía de fuentes: `fichero:línea`, comando, conversación fechada |
| `enlaces` | Opcional. Lista de ficheros `.html` hermanos del bucle, por ejemplo `["plan.html", "mockups.html"]` |

Es un comentario HTML, no se renderiza y sobrevive a cualquier editor. `check-artifact.py` exige el bloque y sus cuatro campos; si falta, el mensaje dice qué escribir. `enlaces` es opcional; si está, solo admite nombres de fichero hermanos —sin carpetas, URLs ni rutas absolutas— para que el bucle siga funcionando por `file://`. No se sustituye por un pie visible: el pie es contenido y puede editarse, el comentario es la procedencia.

## Modo rápido con esquema

Para artefactos rutinarios —texto, listas, tablas, cifras y notas, sin composición propia— existe un atajo determinista:

```bash
python3 scripts/render-quick.py <esquema.json> ../../.explanations/<slug>.html
```

El JSON lleva `titulo`, `familia`, `procedencia` (`prompt`, `fecha`, `fuentes`) y `secciones`; cada sección tiene `titulo` y `bloques`, y cada bloque es uno de `parrafo`, `lista`, `tabla`, `cifra` o `nota`. `desconocidos` es opcional. El esquema completo, con las claves admitidas por bloque, está en la cabecera de [render-quick.py](scripts/render-quick.py). La salida usa los mismos tokens y estructura que la plantilla, escapa todo el texto y no depende del reloj: el mismo JSON produce el mismo HTML.

Si el JSON no valida, el script imprime los problemas y sale con código distinto de 0; en ese caso **no se fuerza el esquema**: se cae a la generación a medida normal con la plantilla de familia. El modo rápido es para lo rutinario, no para lo que pide una composición específica.

## Tokens del proyecto destino

Cuando el proyecto ya declara su sistema visual y el encargo pide usarlo, el artefacto copia los **valores**, no los enlaza. La precedencia es: intención explícita de la persona → sistema del proyecto → defaults de la plantilla de familia.

```bash
python3 scripts/tokens-from-project.py ../../DESIGN.md
python3 scripts/tokens-from-project.py ../../design-system.json
```

- `DESIGN.md`: extrae las custom properties de sus bloques cercados `css`.
- `design-system.json`: recorre `tokens` en formato DTCG y convierte cada `$value` de cadena en una custom property; un alias `{color.brand}` sale como `var(--color-brand)`.

Pega el bloque `:root` que emite dentro del `<style>` del artefacto y mapea los nombres del proyecto a los roles que usan los patrones (`--bg`, `--surface`, `--text`, `--text-dim`, `--accent`, `--ok`, `--warn`, `--err`) sin renombrar los tokens que conserves. Nunca añadas `<link>`, `@import` ni `url()` externos: `check-artifact.py` los rechaza y rompen la promesa de `file://`. Si el sistema no declara tokens legibles, el script sale 1: usa los defaults de la plantilla y dilo en el cierre.

## Bucles de artefactos enlazados

Un encargo puede necesitar varios artefactos que se leen en orden —una exploración, un plan, unos mockups— y que funcionan como memoria del razonamiento. La convención:

- Todos viven como hermanos en `.explanations/`, con un `<a href="plan.html">` relativo y el nombre de fichero sin carpetas.
- Cada página enlazada pasa `check-artifact.py` como cualquier artefacto; ningún eslabón se salta la puerta.
- El artefacto que conoce el bucle declara sus hermanos en la procedencia:

```html
<!-- procedencia: {"prompt": "...", "fecha": "2026-11-08", "familia": "exploracion",
     "fuentes": ["conversación"], "enlaces": ["plan.html", "mockups.html"]} -->
```

`build-index.py` muestra esa relación en el índice junto al artefacto. Los enlaces del cuerpo son contenido, pero siguen siendo rutas relativas: ni `file:///` absolutos ni URLs que conviertan el bucle en una dependencia de red.

## Código en el artefacto

Cuando el artefacto muestre código de los lenguajes del proyecto (`go`, `python`, `json`, `bash`, `html`, `javascript`, `css`), resáltalo con `scripts/highlight.py` en lugar de escribirlo a mano o cargar una librería:

```bash
python3 scripts/highlight.py go ../../ruta/al/fichero.go
python3 scripts/highlight.py python     # lee stdin
python3 scripts/highlight.py --css      # bloque CSS de los tokens
```

La salida es un fragmento con `<span class="tok-kw|tok-str|tok-com|tok-num|tok-fn">`, escapada y determinista: misma entrada, misma salida. Pega el fragmento dentro de `<pre><code>` y el bloque de `--css` una sola vez en el `<style>` del artefacto; el CSS va en línea y la autocontención se mantiene. No añadas reglas `tok-*` de otro origen ni confíes el resaltado a un recurso remoto.

## Procedimiento operativo

### 1. Fijar el encargo

1. Identifica propósito, audiencia y momento de uso: qué debe poder hacer la persona con el artefacto —leer, comparar, decidir, interactuar, copiar— y dónde lo va a abrir.
2. Si falta una decisión que cambia la familia, el contenido o el alcance, pregunta antes de generar. Para detalles reversibles, declara la suposición dentro del propio artefacto.

### 2. Reunir y verificar el material

1. Reúne el material fuente del proyecto que alimenta el artefacto: código, documentación, historial git, salidas de comandos, ficheros que la persona señale.
2. Separa lo verificado —con su fuente: fichero y línea, comando ejecutado— de lo desconocido. Con material insuficiente, el artefacto se entrega igualmente con su sección «Desconocidos» explícita y las preguntas que la desbloquean; nunca con relleno.

### 3. Generar

1. Elige la familia y copia su plantilla de `assets/plantilla-<familia>.html`. La plantilla ya trae la estructura completa de esa familia y los invariantes de [visual-language](references/visual-language.md); sustitúyela, no la rodees con otra inventada.
2. Decide la vía: si el artefacto es rutinario y encaja en el esquema, usa `render-quick.py`; si el encargo es revisar una especificación SDD, `render-sdd.py` la escribe sin HTML a mano; si no, escribe el HTML desde la plantilla. Un JSON inválido no bloquea: se cae a la generación a medida.
3. Genera un único `.explanations/<slug>.html`, con slug en kebab-case descriptivo, por ejemplo `.explanations/estado-semana-45.html`. Si el encargo es un bucle multi-artefacto, cada página es un fichero hermano y declara a las demás en `enlaces`.
4. Rellena el bloque de procedencia con el prompt real, la fecha de hoy, el slug de la familia y las fuentes verificadas.
5. Si el proyecto declara su sistema visual y el encargo lo pide, ejecuta `tokens-from-project.py` y copia los valores en el `:root` según la precedencia de la sección anterior; no enlaces su CSS.
6. Si el artefacto muestra código, pásalo por `highlight.py` y pega su CSS una sola vez en el `<style>`.
7. Cuando el objetivo es devolver datos a la sesión —editor, cuestionario, prototipo afinado—, el artefacto termina en un botón «copiar como prompt» que copia al portapapeles el resultado como texto listo para pegar de vuelta en la conversación.
8. Antes de continuar, revisa que no has introducido CDN, fuentes remotas, imágenes por URL ni hojas enlazadas al copiar los tokens.

**Especificación SDD.** Para un árbol de documentos SDD no se escribe HTML a mano: `python3 scripts/sdd_scan.py <árbol>` imprime el modelo estructural —perfiles, requisitos, tareas y hallazgos— y `python3 scripts/render-sdd.py <árbol> --out ../../.explanations/<slug>.html --prompt "…" --date AAAA-MM-DD [--title "…"]` escribe el artefacto. Prompt y fecha van por flag, así que la misma entrada produce los mismos bytes. Antes de abrir, contrasta el modelo con el árbol que pidió la persona —que no se ha escaneado la carpeta de al lado— y pasa `check-artifact.py` como cualquier artefacto. Reglas de la familia:

- Los perfiles `openspec`, `kiro`, `spec-kit` y `generic` son convención de lectura, no frontera. Un fichero sin perfil reconocido no se descarta: se transcribe tal cual en modo degradado, con aviso visible, sin inventarle fichas ni progreso.
- Un árbol grande se corta por fase del pipeline —y el detalle de hallazgos y desconocidos a la hermana `<slug>-hallazgos.html` en modo seccionado—, nunca por tamaño. El umbral de 100 KB es el de la puerta y no se toca.
- El renderer no llama a ninguna CLI ni lee código fuente: los hallazgos son solo los comprobables en Markdown —requisito vago, spec prescriptora, escenario único sin caso de error, ausencia de no-objetivos— más los estructurales del escáner.
- Escribe solo dentro de `.explanations/`; un `--out` fuera de ahí o `index.html` es error.

### 4. Verificar, revisar a ojo, indexar y abrir

1. Ejecuta `python3 scripts/check-artifact.py ../../.explanations/<slug>.html` desde la carpeta de la skill y corrige lo que señale como error: recursos externos, HTML mal formado, título sin personalizar, procedencia incompleta o `enlaces` inválidos. Los avisos —contraste de tokens por debajo de WCAG AA y ficheros de más de 100 KB— no bloquean, pero se leen y se corrigen o se justifican.
2. Regenera el índice: `python3 scripts/build-index.py ../../.explanations`. Lista los artefactos con su título, fecha, familia y, si la declaran, sus enlaces. Es parte de generar, no un extra. En un bucle, verifica cada página por separado y abre la que sirve de entrada.
3. Abre en el navegador con `scripts/open-artifact.sh ../../.explanations/<slug>.html`. Si no hay navegador disponible, informa la ruta completa y sugiere servir el proyecto con `serve-web.sh` si existe.
4. **Verificación perceptiva**, obligatoria antes de declarar el artefacto entregado. Si hay navegador automatizable —la skill `playwright-cli-usage` del repositorio indica cómo conseguirlo; no es una dependencia técnica de esta skill—, captura el artefacto renderizado y revísalo visualmente. Si no lo hay, abre el artefacto y pide a la persona que lo revise. En ambos casos mira el primer viewport, 390, 768 y 1440 px, el foco, el contraste, el desborde horizontal y el tema oscuro. No declares una revisión visual que no has hecho.
5. Tras el feedback de la persona, genera la siguiente vuelta como artefacto nuevo y conserva el anterior.

### 5. Podar versiones antiguas

Los artefactos versionados se llaman `<slug>-v<N>.html` (`estado-semana-45-v2.html`, `estado-semana-45-v3.html`). Cuando una nueva vuelta deja atrás la anterior, ejecuta:

```bash
python3 scripts/lifecycle.py ../../.explanations --dry-run   # ver qué borraría
python3 scripts/lifecycle.py ../../.explanations             # conserva las 3 últimas
```

`lifecycle.py` conserva por defecto las últimas 3 versiones de cada slug, la vigente incluida, y nunca borra la de número más alto. `--keep N` cambia el número; `--dry-run` solo lista. Solo mira el primer nivel de `.explanations/`, solo ficheros que casan con el patrón versionado y no toca nada fuera de esa carpeta. El índice no se poda: tras la poda, vuelve a ejecutar `build-index.py` para que no enlace versiones borradas.

## Cierre

Informa: ruta del artefacto, familia elegida y por qué, qué se verificó de cada bloque y qué queda en «Desconocidos», qué tokens del proyecto se copiaron —o que se usaron los de la plantilla—, si forma un bucle y con qué páginas, qué revisión perceptiva se hizo y en qué anchuras, que el índice se regeneró, y una línea sobre cómo pedir cambios. Un artefacto que no pasa `check-artifact.py` no se entrega ni se abre.

## Gestión de errores

- Navegador no disponible: informa la ruta completa y la alternativa de servir el proyecto; no reintenta la apertura.
- Material fuente insuficiente: genera con los verificados y una sección «Desconocidos» explícita; no bloquea el encargo ni rellena el hueco.
- Encargo que no encaja en ninguna familia: elige la más cercana, usa la plantilla base y decláralo en el cierre; si es claramente otro dominio, delega y di a quién.
- JSON del modo rápido inválido: lee el mensaje, corrige el JSON si el artefacto era rutinario o cae a la generación a medida; no inventa bloques fuera del esquema.
- `check-artifact.py` falla: corrige y vuelve a ejecutar antes de abrir; la entrega no ocurre con recursos externos, HTML mal formado, sin título, con procedencia incompleta o con enlaces no relativos.
- `check-artifact.py` solo avisa (contraste bajo o más de 100 KB): no bloquea la entrega, pero ajusta el par de tokens o reparte el contenido en un artefacto enlazado; si la persona acepta el aviso, dilo en el cierre.
- `tokens-from-project.py` no encuentra tokens: usa los defaults de la plantilla y declara en el cierre que el sistema del proyecto no aportó valores legibles; no inventes un sistema ni enlaces CSS.
- Bucle con un eslabón roto: cada página se verifica y se enlaza por su nombre relativo; si una aún no existe, no la declares en `enlaces` ni la enlaces como si estuviera terminada.
- Entrevista interrumpida: exporta lo respondido hasta el momento como prompt parcial y declara qué queda por preguntar; no descartes las respuestas ni generes el artefacto como si la entrevista hubiera terminado.
- Revisión perceptiva no disponible: abre el artefacto y pide la revisión a la persona; no sustituyas la comprobación visual por una suposición.
- `lifecycle.py` con `--keep 0`: se rechaza porque borraría la versión vigente; usa 1 o más. Si un artefacto no sigue el patrón `<slug>-v<N>.html`, no se poda: renómbralo solo si el encargo lo pide.
