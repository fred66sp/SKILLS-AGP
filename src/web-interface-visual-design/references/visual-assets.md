# Criterios para recursos visuales

Lee esta referencia en la fase C cuando haya que seleccionar, crear, integrar o revisar recursos gráficos.

## Elegir la categoría y el formato

Antes de dibujar, define mensaje, tamaño de uso, fondo, necesidad de edición y significado accesible. Selecciona por fidelidad y función, no por preferencia por SVG.

| Categoría | Construcción y complejidad | Comprobación específica renderizada |
|---|---|---|
| Icono | Símbolo funcional simple con silueta reconocible, retícula y familia comunes | Reconocible al tamaño de uso; peso y centrado ópticos junto al texto y otros iconos |
| Ilustración | Composición con foco, siluetas, masas y detalle subordinado; curvas deliberadas | Balance, profundidad y narrativa; detalle útil al tamaño final, no formas arbitrarias |
| Logotipo o símbolo | Usa el original autorizado y su geometría; no redibuja una marca existente por aproximación | Proporciones, área de respeto, variantes y reproducción pequeña según la marca |
| Decoración | Refuerza composición sin contenido esencial; puede simplificarse u ocultarse en móvil | No compite con texto ni reduce contraste; recorte intencional, no accidental |
| Diagrama | Nodos y relaciones explícitos, geometría repetible y conectores con dirección clara | Correspondencia exacta con relaciones fuente, lectura y etiquetas sin ambigüedad |
| Infografía | Mensaje informativo, recorrido y codificación de datos antes que efectos | Comprensión del mensaje y fidelidad de datos; leyenda, unidades y escala cuando procedan |

Un diagrama técnico que deba editarse merece fuente estructurada en la herramienta existente; un SVG conviene para composición vectorial controlada; una biblioteca de gráficos para escalas, datos variables e interacción; un bitmap para ilustración pictórica, texturas, iluminación o detalle que no se reproduzca bien con geometría. Una imagen ilustrativa no sustituye datos ni una fuente editable. Mantén la fuente editable disponible cuando sea requisito.

No convierte automáticamente bitmaps a trazados. Si el encargo exige SVG pero su fidelidad no es viable, muestra la limitación y pide decisión antes de cambiar formato. No presenta una aproximación mediocre como equivalente al original.

## Construir SVG con intención

1. Planifica masas, foco y espacio negativo antes de paths. Fija proporciones y ejes de alineación; usa primitivas para formas geométricas y Bézier con tangentes coherentes para curvas. Evita quiebros involuntarios y detalle que desaparezca al reducir.
2. Define `viewBox` con espacio para trazos, marcadores y efectos. Conserva relación de aspecto; usa dimensiones o CSS que eviten deformación y saltos de layout. Revisa el recorte de `clipPath`, máscaras y región de filtros; no soluciona clipping con márgenes enormes que empeoren el encuadre.
3. Ordena capas por profundidad y agrupa partes con sentido mediante `g`. Mantén IDs únicos por instancia para gradientes, filtros, títulos y máscaras al repetir SVG inline. Verifica todas las referencias `url(#...)`.
4. Define rellenos, grosor de trazo, `stroke-linecap` y `stroke-linejoin` coherentes. Ajusta el peso óptico a la escala; usa `vector-effect="non-scaling-stroke"` solo si conviene conservar el grosor al escalar, no como receta universal.
5. Usa gradientes para modelar volumen o dirigir la mirada, con luz y transiciones consistentes. Un filtro debe aportar algo visible: limita área y complejidad, evita halos cortados y sombras que ensucien bordes. No aplica sombreado ilustrativo a iconos de línea.
6. Conserva texto como texto cuando comunique información; no lo convierte en contornos para ocultar problemas de fuente. Comprueba métricas de la fuente final y fallbacks, saltos y legibilidad. No inserta raster oculto para aparentar un vector nativo.
7. Elimina objetos invisibles, paths duplicados, metadatos de editor y precisión numérica innecesaria. Reutiliza geometría cuando aclare, no para volverla opaca. Si hay optimizador instalado, compara el render antes y después; no borra nombres accesibles ni IDs usados por CSS/JS.
8. Comprueba XML, referencias y renderizado en los navegadores objetivo modernos. Inspecciona tamaño de uso y ampliado, fondo claro/oscuro si aplica, bordes, uniones, nitidez, encuadre y contraste; no confunde validez con calidad.

### Accesibilidad y frontera de confianza

- SVG decorativo inline: `aria-hidden="true"`, sin foco ni información exclusiva. En `img`, usa `alt=""` si es decorativo.
- SVG informativo inline: nombre accesible, por ejemplo `role="img"` con `aria-labelledby` y `title` de ID único; añade descripción o equivalente textual para información compleja. En `img`, usa un `alt` que comunique su propósito; el título interno no sustituye ese atributo.
- Diagramas y datos complejos: ofrece resumen y contenido equivalente en HTML o tabla cuando sea necesario; no intenta meter toda la explicación en un nombre accesible.
- El botón o enlace posee la interacción y su nombre; el SVG hijo decorativo no añade una segunda etiqueta ni un foco extra.
- Trata SVG externo/no confiable como contenido activo: no inyecta markup crudo. Usa el tratamiento seguro del proyecto, evita scripts, manejadores y referencias externas no necesarias y respeta CSP; la revisión de seguridad especializada sigue aplicando.

## Seleccionar e integrar iconografía

1. Reutiliza la familia y variante presentes. Sin una existente, compara una biblioteca consolidada compatible (Lucide, Heroicons, Tabler Icons, Material Symbols u otra), su licencia y cobertura semántica. No añade una dependencia completa por pocos iconos: usa imports individuales o recursos permitidos por la licencia y las convenciones.
2. Elige el símbolo estándar que el usuario reconozca antes de inventar uno. No usa emoji como sustituto profesional salvo que el tono y el encargo lo justifiquen. Un icono ambiguo necesita etiqueta visible, no solo nombre para lector de pantalla.
3. Mantén familia, trazo o relleno, esquinas, proporciones, color y estados. Compara tamaño óptico, no solo anchura CSS: dos cajas iguales pueden tener pesos distintos. Ajusta alineación respecto a la línea de texto y área interactiva sin estirar paths.
4. Distingue iconografía funcional de ilustración: un dibujo expresivo no debe simular un control, ni la retícula minimalista de un icono limitar una ilustración compleja. Si hace falta un icono propio, construye con la retícula y el lenguaje de la familia y compáralo renderizado con sus vecinos.

## Construir infografías y diagramas

1. Escribe la pregunta que debe responder y extrae de la fuente entidades, relaciones, orden, cifras, unidades y excepciones. Lo desconocido se declara; no rellena huecos con datos o flechas inventados.
2. Elige estructura por contenido: pasos y decisiones para procesos; capas o agrupaciones para arquitectura conceptual; filas alineadas para comparación; eje temporal para fechas; grafo para dependencias; gráfico con escala para magnitudes. No implica causalidad con una simple proximidad ni tiempo proporcional donde no lo haya.
3. Boceta el recorrido de lectura y asigna jerarquía a título, grupos, nodos, conectores y etiquetas. Ordena nodos para minimizar cruces y conectores largos; usa puertos y trazados consistentes. Separa flechas y texto, evita solapamientos y espacios muertos. Distingue dirección, bifurcación y retorno sin depender solo del color.
4. Dimensiona nodos para el contenido, con padding y tipografía comunes; alinea por retícula y agrupa por significado. No reduce todo hasta volver las etiquetas ilegibles para encajarlo. En pantallas pequeñas, recompone o proporciona una vista detallada accesible con scroll localizado cuando la relación bidimensional lo requiera.
5. En métricas, declara fuente, periodo, unidad, denominador y escala pertinentes. Longitudes y áreas deben representar magnitudes honestamente; no trunca ejes sin indicarlo ni usa perspectiva decorativa que distorsione comparaciones. No inventa porcentajes, conclusiones o precisión.
6. Renderiza y sigue el recorrido como lector: ¿qué ocurre primero?, ¿qué conecta con qué?, ¿qué significa cada codificación? Contrasta cada etiqueta y flecha con la fuente. Comprueba que el mensaje se entiende sin memorizar una leyenda y que existe equivalente textual cuando corresponde.
