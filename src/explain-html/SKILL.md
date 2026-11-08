---
name: explain-html
description: "Genera artefactos HTML autocontenidos —informes, explicadores, cuestionarios interactivos, prototipos, diagramas, presentaciones, comparaciones de alternativas y editores a medida— en la carpeta .explanations/ del proyecto y los abre en el navegador para revisarlos e interactuar con ellos. Se usa cuando la persona pide un informe o un estado, un cuestionario, un prototipo interactivo, un diagrama o flujo, una presentación, una comparación de enfoques lado a lado, un explicador de código o de concepto, o un editor desechable que termina en un botón «copiar como prompt». Cada artefacto es un único .html sin dependencias externas que funciona por file:// y separa hechos verificados de desconocidos. No se usa para documentación duradera del repositorio (eso es document-management-software), para la identidad o el sistema visual de una interfaz de producto (design-system-architect), para implementar una interfaz real (web-interface-visual-design) ni para mantener un catálogo de informes publicado."
metadata:
  version: "0.2.0"
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
- Delega lo que no es suyo: documentación duradera del repositorio a `document-management-software`; identidad y sistema visual de un producto a `design-system-architect`; implementar una interfaz real a `web-interface-visual-design`. Si el artefacto es un paso previo —explorar, decidir, probar, comunicar— es de esta skill.

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

Para la familia elegida lee la sección correspondiente de [artifact-patterns](references/artifact-patterns.md) antes de generar y copia su plantilla de `assets/`. Usa [plantilla-artefacto](assets/plantilla-artefacto.html), el esqueleto base, solo si el encargo no encaja en ninguna familia.

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
| `familia` | Uno de los ocho slugs de la tabla anterior |
| `fuentes` | Lista no vacía de fuentes: `fichero:línea`, comando, conversación fechada |

Es un comentario HTML, no se renderiza y sobrevive a cualquier editor. `check-artifact.py` exige el bloque y sus cuatro campos; si falta, el mensaje dice qué escribir. No se sustituye por un pie visible: el pie es contenido y puede editarse, el comentario es la procedencia.

## Modo rápido con esquema

Para artefactos rutinarios —texto, listas, tablas, cifras y notas, sin composición propia— existe un atajo determinista:

```bash
python3 scripts/render-quick.py <esquema.json> ../../.explanations/<slug>.html
```

El JSON lleva `titulo`, `familia`, `procedencia` (`prompt`, `fecha`, `fuentes`) y `secciones`; cada sección tiene `titulo` y `bloques`, y cada bloque es uno de `parrafo`, `lista`, `tabla`, `cifra` o `nota`. `desconocidos` es opcional. El esquema completo, con las claves admitidas por bloque, está en la cabecera de [render-quick.py](scripts/render-quick.py). La salida usa los mismos tokens y estructura que la plantilla, escapa todo el texto y no depende del reloj: el mismo JSON produce el mismo HTML.

Si el JSON no valida, el script imprime los problemas y sale con código distinto de 0; en ese caso **no se fuerza el esquema**: se cae a la generación a medida normal con la plantilla de familia. El modo rápido es para lo rutinario, no para lo que pide una composición específica.

## Procedimiento operativo

### 1. Fijar el encargo

1. Identifica propósito, audiencia y momento de uso: qué debe poder hacer la persona con el artefacto —leer, comparar, decidir, interactuar, copiar— y dónde lo va a abrir.
2. Si falta una decisión que cambia la familia, el contenido o el alcance, pregunta antes de generar. Para detalles reversibles, declara la suposición dentro del propio artefacto.

### 2. Reunir y verificar el material

1. Reúne el material fuente del proyecto que alimenta el artefacto: código, documentación, historial git, salidas de comandos, ficheros que la persona señale.
2. Separa lo verificado —con su fuente: fichero y línea, comando ejecutado— de lo desconocido. Con material insuficiente, el artefacto se entrega igualmente con su sección «Desconocidos» explícita y las preguntas que la desbloquean; nunca con relleno.

### 3. Generar

1. Elige la familia y copia su plantilla de `assets/plantilla-<familia>.html`. La plantilla ya trae la estructura completa de esa familia y los invariantes de [visual-language](references/visual-language.md); sustitúyela, no la rodees con otra inventada.
2. Decide la vía: si el artefacto es rutinario y encaja en el esquema, usa `render-quick.py`; si no, escribe el HTML desde la plantilla. Un JSON inválido no bloquea: se cae a la generación a medida.
3. Genera un único `.explanations/<slug>.html`, con slug en kebab-case descriptivo, por ejemplo `.explanations/estado-semana-45.html`.
4. Rellena el bloque de procedencia con el prompt real, la fecha de hoy, el slug de la familia y las fuentes verificadas.
5. Cuando el objetivo es devolver datos a la sesión —editor, cuestionario, prototipo afinado—, el artefacto termina en un botón «copiar como prompt» que copia al portapapeles el resultado como texto listo para pegar de vuelta en la conversación.
6. Antes de continuar, revisa que no has introducido CDN, fuentes remotas ni imágenes por URL.

### 4. Verificar, indexar y abrir

1. Ejecuta `python3 scripts/check-artifact.py ../../.explanations/<slug>.html` desde la carpeta de la skill y corrige lo que señale: recursos externos, título sin personalizar o procedencia incompleta.
2. Regenera el índice: `python3 scripts/build-index.py ../../.explanations`. Lista los artefactos con su título, fecha y familia, en enlaces relativos que funcionan por `file://`. Es parte de generar, no un extra.
3. Abre en el navegador con `scripts/open-artifact.sh ../../.explanations/<slug>.html`. Si no hay navegador disponible, informa la ruta completa y sugiere servir el proyecto con `serve-web.sh` si existe.
4. Tras el feedback de la persona, genera la siguiente vuelta como artefacto nuevo y conserva el anterior.

### 5. Podar versiones antiguas

Los artefactos versionados se llaman `<slug>-v<N>.html` (`estado-semana-45-v2.html`, `estado-semana-45-v3.html`). Cuando una nueva vuelta deja atrás la anterior, ejecuta:

```bash
python3 scripts/lifecycle.py ../../.explanations --dry-run   # ver qué borraría
python3 scripts/lifecycle.py ../../.explanations             # conserva las 3 últimas
```

`lifecycle.py` conserva por defecto las últimas 3 versiones de cada slug, la vigente incluida, y nunca borra la de número más alto. `--keep N` cambia el número; `--dry-run` solo lista. Solo mira el primer nivel de `.explanations/`, solo ficheros que casan con el patrón versionado y no toca nada fuera de esa carpeta. El índice no se poda: tras la poda, vuelve a ejecutar `build-index.py` para que no enlace versiones borradas.

## Cierre

Informa: ruta del artefacto, familia elegida y por qué, qué se verificó de cada bloque y qué queda en «Desconocidos», que el índice se regeneró, y una línea sobre cómo pedir cambios. Un artefacto que no pasa `check-artifact.py` no se entrega ni se abre.

## Gestión de errores

- Navegador no disponible: informa la ruta completa y la alternativa de servir el proyecto; no reintenta la apertura.
- Material fuente insuficiente: genera con los verificados y una sección «Desconocidos» explícita; no bloquea el encargo ni rellena el hueco.
- Encargo que no encaja en ninguna familia: elige la más cercana, usa la plantilla base y decláralo en el cierre; si es claramente otro dominio, delega y di a quién.
- JSON del modo rápido inválido: lee el mensaje, corrige el JSON si el artefacto era rutinario o cae a la generación a medida; no inventa bloques fuera del esquema.
- `check-artifact.py` falla: corrige y vuelve a ejecutar antes de abrir; la entrega no ocurre con recursos externos, sin título o con procedencia incompleta.
- `lifecycle.py` con `--keep 0`: se rechaza porque borraría la versión vigente; usa 1 o más. Si un artefacto no sigue el patrón `<slug>-v<N>.html`, no se poda: renómbralo solo si el encargo lo pide.
