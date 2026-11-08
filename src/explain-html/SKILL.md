---
name: explain-html
description: "Genera artefactos HTML autocontenidos —informes, explicadores, cuestionarios interactivos, prototipos, diagramas, presentaciones, comparaciones de alternativas y editores a medida— en la carpeta .explanations/ del proyecto y los abre en el navegador para revisarlos e interactuar con ellos. Se usa cuando la persona pide un informe o un estado, un cuestionario, un prototipo interactivo, un diagrama o flujo, una presentación, una comparación de enfoques lado a lado, un explicador de código o de concepto, o un editor desechable que termina en un botón «copiar como prompt». Cada artefacto es un único .html sin dependencias externas que funciona por file:// y separa hechos verificados de desconocidos. No se usa para documentación duradera del repositorio (eso es document-management-software), para la identidad o el sistema visual de una interfaz de producto (design-system-architect), para implementar una interfaz real (web-interface-visual-design) ni para mantener un catálogo de informes publicado."
metadata:
  version: "0.1.0"
---

# explain-html: artefactos HTML explicativos

Convierte un encargo —un informe, un cuestionario, un prototipo interactivo, un diagrama, una presentación, un explicador o un editor a medida— en un único fichero HTML autocontenido en `.explanations/` del proyecto y lo abre en el navegador para que la persona lo revise e interactúe con él. Un documento que se abre y se navega comunica mejor que un muro de Markdown: cambia el medio y cambia la probabilidad de que alguien lo lea.

## Responsabilidad y límites

- Produce artefactos de revisión, no producto duradero: viven en `.explanations/`, pueden regenerarse o borrarse sin pérdida. El conocimiento verificado vuelve al proyecto por la conversación o por la exportación «copiar como prompt»; nunca modificando ficheros fuera de `.explanations/`.
- Un encargo genera un artefacto nuevo con nombre nuevo. No sobrescribe ni edita un artefacto existente sin instrucción explícita; si el encargo es una nueva vuelta sobre el anterior, crea `<slug>-v2.html` y conserva el primero.
- Autocontención total: sin CDN, sin `<script src>` ni `<link>` a red, sin fuentes remotas, sin imágenes por URL. Todo CSS, JS y SVG va en línea y toda imagen es `data:` o SVG incrustado. El artefacto debe funcionar igual abierto por `file://` que servido por HTTP.
- No inventa datos: cada cifra, estado, fecha y relación del artefacto sale del material fuente o queda en la sección «Desconocidos». No rellena huecos con lo plausible; un gráfico sin datos reales no se dibuja.
- Delega lo que no es suyo: documentación duradera del repositorio a `document-management-software`; identidad y sistema visual de un producto a `design-system-architect`; implementar una interfaz real a `web-interface-visual-design`. Si el artefacto es un paso previo —explorar, decidir, probar, comunicar— es de esta skill.

## Familias de artefacto

| Encargo | Familia | Representación principal |
|---|---|---|
| Comparar enfoques, direcciones o planes | Exploración comparativa | Cuadrícula de opciones lado a lado, cada una con su concesión anotada |
| Explicar cómo funciona un mecanismo, módulo o concepto | Explicador | TL;DR + recorrido plegable + diagrama + trampas |
| Informar estado, evolución o incidente | Informe | Cronología o tabla + mini-gráfico SVG |
| Dibujar flujo, arquitectura, secuencia o proceso | Diagrama | SVG en línea o pipeline CSS |
| Probar una animación, una interacción o un flujo clicable | Prototipo | Página interactiva con deslizadores y controles |
| Preguntar, evaluar o autocorregir | Cuestionario | Preguntas con corrección en vivo y resultado exportable |
| Reordenar, clasificar, editar valores o afinar texto | Editor a medida | Formulario sobre el dato concreto + exportación |
| Presentar en una reunión | Presentación | Secciones a pantalla completa navegables con teclado |

Para la familia elegida lee la sección correspondiente de [artifact-patterns](references/artifact-patterns.md) antes de generar: copia la estructura que describe, no la improvises.

## Procedimiento operativo

### 1. Fijar el encargo

1. Identifica propósito, audiencia y momento de uso: qué debe poder hacer la persona con el artefacto —leer, comparar, decidir, interactuar, copiar— y dónde lo va a abrir.
2. Si falta una decisión que cambia la familia, el contenido o el alcance, pregunta antes de generar. Para detalles reversibles, declara la suposición dentro del propio artefacto.

### 2. Reunir y verificar el material

1. Reúne el material fuente del proyecto que alimenta el artefacto: código, documentación, historial git, salidas de comandos, ficheros que la persona señale.
2. Separa lo verificado —con su fuente: fichero y línea, comando ejecutado— de lo desconocido. Con material insuficiente, el artefacto se entrega igualmente con su sección «Desconocidos» explícita y las preguntas que la desbloquean; nunca con relleno.

### 3. Generar

1. Copia [plantilla-artefacto](assets/plantilla-artefacto.html) como esqueleto y lee [visual-language](references/visual-language.md) para los invariantes tipográficos, cromáticos y de accesibilidad.
2. Genera un único `.explanations/<slug>.html`, con slug en kebab-case descriptivo, por ejemplo `.explanations/estado-semana-45.html`.
3. Cuando el objetivo es devolver datos a la sesión —editor, cuestionario, prototipo afinado—, el artefacto termina en un botón «copiar como prompt» que copia al portapapeles el resultado como texto listo para pegar de vuelta en la conversación.
4. Antes de continuar, revisa que no has introducido CDN, fuentes remotas ni imágenes por URL.

### 4. Verificar y abrir

1. Ejecuta `python3 scripts/check-artifact.py .explanations/<slug>.html` desde la carpeta de la skill y corrige lo que señale.
2. Abre en el navegador con `scripts/open-artifact.sh .explanations/<slug>.html`. Si no hay navegador disponible, informa la ruta completa y sugiere servir el proyecto con `serve-web.sh` si existe.
3. Tras el feedback de la persona, genera la siguiente vuelta como artefacto nuevo y conserva el anterior.

## Cierre

Informa: ruta del artefacto, familia elegida y por qué, qué se verificó de cada bloque y qué queda en «Desconocidos», y una línea sobre cómo pedir cambios. Un artefacto que no pasa `check-artifact.py` no se entrega ni se abre.

## Gestión de errores

- Navegador no disponible: informa la ruta completa y la alternativa de servir el proyecto; no reintenta la apertura.
- Material fuente insuficiente: genera con los verificados y una sección «Desconocidos» explícita; no bloquea el encargo ni rellena el hueco.
- Encargo que no encaja en ninguna familia: elige la más cercana y decláralo en el cierre; si es claramente otro dominio, delega y di a quién.
- `check-artifact.py` falla: corrige y vuelve a ejecutar antes de abrir; la entrega no ocurre con recursos externos o sin título.
