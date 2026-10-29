---
name: web-interface-visual-design
description: "Diseña, implementa y revisa la calidad visual y comunicativa de interfaces web, componentes, SVG, iconografía, infografías y diagramas. Se activa al diseñar o mejorar páginas, paneles, dashboards o aplicaciones; revisar composición, tipografía, color y jerarquía; crear o revisar SVG e iconos; explicar procesos visualmente; o corregir presentación responsive. Respeta la marca y el sistema de diseño existentes, no impone frameworks y exige inspeccionar el resultado renderizado cuando haya herramientas disponibles. No se usa para backend, bases de datos, lógica de negocio o pruebas puramente funcionales, ni sustituye arquitectura, seguridad o programación idiomática."
metadata:
  version: "0.1.1"
---

# Diseño visual de interfaces web

Produce una interfaz que comunique mejor, no más decoración. La fuente de verdad es el resultado renderizado en su contexto de uso: compilar o validar SVG/XML no demuestra calidad visual.

## Responsabilidad y límites

- Posee composición, dirección de arte, sistemas visuales, componentes reutilizables, recursos gráficos y revisión visual. En una revisión sin encargo de implementación, informa de defectos sin editar.
- Conserva marca, tokens, componentes, contenido y comportamiento válidos. No introduce una identidad nueva ni un rediseño fuera del alcance sin autorización.
- Trabaja sobre el stack presente: HTML/CSS, HTMX, Alpine.js, React, Vue, Svelte u otro. Delega arquitectura, lenguaje, lógica, seguridad y pruebas funcionales a sus contratos especializados; una captura no los sustituye.
- No inventa métricas, datos, relaciones, identidad de marca ni derechos de uso de recursos. Distingue contenido real, muestras proporcionadas y decisiones propuestas.

## Procedimiento operativo

### 1. Fase A: Inspeccionar antes de diseñar

1. Identifica tarea principal, audiencia, contexto de uso, densidad de información y alcance: qué se mantiene y qué puede cambiar. Si falta una decisión que afecte a marca, datos o formato solicitado, pregunta antes de sustituirla; para detalles reversibles, declara una suposición mínima.
2. Examina la interfaz existente y su renderizado si lo hay. Localiza rutas, componentes, CSS, tokens, fuentes, familias de iconos, recursos y estados disponibles. Lee las convenciones del proyecto y sus comandos reales de ejecución y verificación.
3. Comprueba qué herramientas de navegador, captura o renderizado están disponibles y cómo abrir el resultado. No promete capturas ni instala herramientas o dependencias sin necesidad y permisos.
4. Resume defectos observables y elementos que deben preservarse. Prioriza lo que impide comprender o actuar antes que el acabado decorativo.

### 2. Fase B: Fijar una dirección visual breve

1. Expresa en unas líneas: objetivo, foco principal y secundario, estilo adecuado al contexto, referencias pertinentes, paleta y tipografía existentes, retícula y recursos necesarios. No crea un documento formal para decisiones triviales.
2. Traduce el objetivo en composición: asigna espacio y contraste a la tarea principal; agrupa por relación semántica; usa alineaciones compartidas y una retícula que corresponda a la densidad. Una tarjeta delimita un grupo real, no cada fragmento de texto.
3. Ajusta escala tipográfica, longitud de línea e interlineado con contenido real. El título no debe expulsar la tarea principal de la pantalla; las etiquetas y los datos secundarios no deben volverse ilegibles. No impone cantidades fijas de tamaños, colores o componentes.
4. Define roles cromáticos (texto, superficie, acento, estado), relaciones de espaciado, bordes, radios y profundidad. Usa sombras y degradados solo para separar planos o apoyar el mensaje. Evita acumulación de efectos, espacios arbitrarios y estilos incompatibles.
5. Decide cómo cambia la composición en móvil, tableta y escritorio: orden de lectura, columnas, navegación, tablas y gráficos. Adapta agrupaciones y flujo, no solo reduce tamaños.
6. Elige una estética por contexto —técnica, editorial, corporativa, minimalista, clara, oscura o expresiva—, no una receta de plantilla. Si hay diseño existente, la mejora debe ser reconocible como parte de él.

### 3. Fase C: Implementar el mínimo coherente

1. Reutiliza tokens, componentes y patrones adecuados. Introduce un componente reutilizable solo cuando exista una responsabilidad o repetición real; no convierte cada variación en una abstracción.
2. Implementa jerarquía y estructura antes de detalles gráficos. Comprueba espaciado entre elementos relacionados frente a secciones, alineación de texto y controles, superficies y estados de hover, foco, activo, deshabilitado y feedback. Incluye carga, vacío, error y éxito cuando correspondan a la tarea.
3. Para cualquier SVG, icono, ilustración, logotipo, decoración, diagrama o infografía, lee [visual-assets](references/visual-assets.md) antes de elegir formato o dibujar. Aplica los criterios de su categoría, no los de otra.
4. Construye accesibilidad junto con la composición: HTML semántico, orden de lectura y tabulación lógico, foco visible no oculto y controles operables por teclado. Da nombre accesible a controles de solo icono; no depende del tooltip, del color ni del hover para transmitir información esencial.
5. Comprueba contraste [WCAG AA](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html): texto normal al menos 4.5:1, texto grande (al menos 24 CSS px, o 18.67 CSS px en negrita) 3:1 y límites/indicadores necesarios de controles y gráficos 3:1, con las excepciones de la norma. Mide los colores realmente adyacentes y estados, no solo la paleta teórica.
6. Conserva texto legible y contenido al ampliar texto al 200% y al comprobar reflow a 320 CSS px; permite scroll localizado para contenido genuinamente bidimensional, no para ocultar un fallo de layout. Usa áreas de interacción adecuadas: al menos 24×24 CSS px o una [excepción de WCAG 2.2](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) aplicable y comprobada, como separación o control equivalente.
7. Evita animación innecesaria y respeta `prefers-reduced-motion`. No introduce movimiento esencial sin alternativa ni destellos peligrosos.

### 4. Fase D: Inspeccionar, corregir y volver a renderizar

1. Ejecuta los comandos de validación aplicables del proyecto y comprueba rutas, recursos y consola. Registra por separado estructura/sintaxis, comportamiento funcional y resultado visual.
2. Si hay herramientas de renderizado disponibles, abre la página o el SVG final en navegador o equivalente, espera fuentes, recursos y un estado visual estable e **inspecciona las imágenes renderizadas**, no solo el DOM, las medidas o el éxito de la captura. Si fija o desactiva animaciones para capturar, registra esa condición y comprueba el movimiento por separado cuando corresponda. Para un recurso aislado, comprueba también su integración al tamaño de uso.
3. Revisa móvil, tableta y escritorio y los puntos donde cambia el layout; usa como punto de partida 390, 768 y 1440 CSS px, ajustándolos al proyecto. Incluye 320 CSS px, zoom, textos largos, estados pertinentes y temas existentes. Comprueba teclado y foco en la interfaz real; una imagen no demuestra interacción accesible.
4. Recorre este orden para evitar pulir lo incorrecto:
   - **Mensaje y jerarquía:** tarea y datos principales identificables; ninguna decoración compite con ellos.
   - **Composición:** proporciones equilibradas, alineaciones y ritmo; sin espacios muertos, recortes, solapamientos o desbordamientos accidentales.
   - **Tipografía y color:** tamaños, saltos, interlineado y contraste legibles; títulos y densidad proporcionados al contexto.
   - **Recursos:** iconos con tamaño óptico y trazo compatibles; SVG nítido a tamaño real; etiquetas y conectores inequívocos; datos fieles a su fuente.
   - **Adaptación y estados:** jerarquía conservada, foco visible y feedback comprensible sin depender solo del color.
5. Para cada defecto, identifica ubicación, efecto sobre el usuario y corrección mínima. Corrige y vuelve a renderizar los tamaños y estados afectados. No acepta una imagen anterior como evidencia del código corregido.
6. Conserva evidencia proporcional: captura o ubicación del render final, viewport, tema/estado, observaciones y comprobaciones ejecutadas. Si una herramienta falla, intenta la alternativa disponible; declara lo que no pudo inspeccionarse. Sin renderizador o sin acceso a sus imágenes, informa **«validación visual pendiente»**, nunca «visualmente verificado».

### 5. Fase E: Entregar con límites explícitos

1. Resume qué cambia, qué se conserva y qué decisiones visuales son relevantes.
2. Separa los resultados: validación estructural, funcional y visual, con evidencia realmente inspeccionada. Enumera defectos pendientes y limitaciones de formato, herramientas o fidelidad.
3. Para evaluar esta skill, no cada cambio de interfaz, usa los escenarios de [visual-acceptance](references/visual-acceptance.md). No convierte esa aceptación manual en una suite pesada de CI.

## Gestión de errores y criterio de cierre

- Si un recurso externo no está disponible o su licencia es desconocida, no lo presenta como integrado ni autorizado: usa uno aprobado o informa del bloqueo.
- Si el SVG solicitado no puede alcanzar la fidelidad necesaria, explica la limitación y propone una alternativa de formato; no sustituye el formato sin aprobación ni vende geometría aproximada como equivalente.
- Si hay conflicto entre marca y una preferencia estética, conserva la marca. Si afecta a legibilidad o accesibilidad, expone el conflicto y propone el ajuste mínimo.
- Si solo hay XML válido, build correcto o métricas automáticas, puede afirmar esa comprobación, no calidad visual ni accesibilidad completa. Un defecto visual observado sin resolver impide el cierre visual, aunque los tests pasen.
