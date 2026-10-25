# Aceptación práctica de la skill

Lee esta referencia al evaluar o cambiar el contrato de la skill. No es una suite de CI ni una exigencia de generar demos en cada proyecto.

## Protocolo común de evaluación

1. Usa los encargos siguientes sin cambiar sus datos. Proporciona el mismo stack, recursos, herramientas, tiempo y contexto de diseño a cada ejecución. Conserva el encargo y las condiciones con la evidencia, fuera del paquete de la skill.
2. Cuando sea posible comparar, usa sesiones independientes con el mismo modelo: una sin esta skill y otra con el contrato y las referencias pertinentes. No muestra el primer resultado a la segunda sesión ni permite que otros contratos reintroduzcan esta skill en la base. Si no se puede aislar, declara la contaminación; no atribuye la mejora a la skill.
3. Renderiza los resultados finales y abre realmente las capturas o vistas. Para páginas usa 390, 768 y 1440 CSS px, además de reflow a 320; para recursos usa los tamaños del encargo. Comprueba carga de fuentes y recursos. Registra tema, viewport, revisión del artefacto y ubicación de evidencia, sin añadir infraestructura al repositorio.
4. Revisa con la rúbrica específica y clasifica cada criterio como **cumple / defecto / no comprobado**, con observación localizada. Un criterio de datos, legibilidad, accesibilidad o encuadre fallido no se compensa con decoración. Las comprobaciones de teclado, semántica o contraste necesitan además medición/inspección pertinente, no solo capturas.
5. Si hay comparación, oculta la identidad de las variantes al revisor cuando sea posible y compara criterio a criterio: mejor / igual / peor, con motivo observable. No afirma causalidad a partir de una sola muestra; repite o usa proyectos reales antes de generalizar.
6. Separa **estructura**, **función** y **visual** en el informe. Guarda defectos y correcciones; vuelve a inspeccionar el render corregido. Sin imágenes inspeccionadas, la calidad visual queda pendiente aunque Markdown, XML o build pasen.

## Escenario A — Interfaz web

**Encargo reproducible:** Diseñar un dashboard de seguimiento de solicitudes para una persona de operaciones. La tarea principal es localizar y abrir solicitudes pendientes. Usar el stack y el sistema visual proporcionados; si no existen, declarar una dirección sobria apropiada, sin inventar marca. Datos de muestra: SOL-101, «Acceso al panel», Ana, pendiente; SOL-102, «Actualizar dirección», Luis, en curso; SOL-103, «Exportar informe», Marta, resuelta. Incluir búsqueda local, filtro por estado y apertura del detalle; mostrar estados vacío y sin resultados sin inventar métricas. Adaptar a móvil, tableta y escritorio.

**Criterios observables:**
- La lista y su tarea principal dominan frente al título o adornos; las tres solicitudes y sus estados coinciden con la fuente.
- Tipografía, interlineado, espaciado y alineaciones permiten escanear identificador, asunto, persona y estado; no hay tarjetas sin agrupación útil.
- Los iconos funcionales pertenecen a una misma familia y los controles tienen nombre, foco visible y área de interacción adecuada.
- Búsqueda, filtro y detalle funcionan con teclado; el estado no se comunica solo por color. Verifica contraste con los colores finales.
- No hay recortes ni desbordamiento accidental en los tamaños comunes del protocolo; el móvil reorganiza información sin perder campos o acciones. Comprueba texto al 200%.

## Escenario B — SVG ilustrativo

**Encargo reproducible:** Crear una ilustración SVG de una carpeta abierta con documentos para una pantalla de carga inicial, sin texto incorporado ni logotipo. Composición sobria con profundidad sutil, una dirección de luz coherente y un acento cromático del sistema proporcionado. No debe parecer un icono ampliado ni incluir datos. Integrarla a 240 y 480 CSS px sobre los fondos claro y oscuro del contexto; si solo existe un tema, definir fondos de prueba explícitos.

**Criterios observables:**
- La carpeta se reconoce por su silueta y las capas tienen proporciones y perspectiva coherentes, sin tangencias o cruces accidentales.
- Curvas, bordes y superficies se ven deliberados; trazo, rellenos y cualquier gradiente apoyan una misma luz y no ensucian el contorno.
- El espacio negativo equilibra la composición y el detalle sigue siendo útil en ambos tamaños; nada queda cortado por `viewBox` o filtros.
- Hay separación suficiente entre planos y fondos; no aparecen halos, dientes o deformación al integrar el recurso.
- IDs y referencias resuelven al mostrar dos instancias juntas; su tratamiento decorativo no introduce foco o nombres redundantes. La validez XML se registra aparte del juicio visual.

## Escenario C — Infografía de proceso

**Encargo reproducible:** Representar el flujo «Solicitud → Validación». Desde Validación, «completa» conduce a Aprobación y después a Archivo; «incompleta» conduce a Corrección y vuelve a Validación. No añadir pasos, porcentajes, duración ni participantes. Producir una infografía SVG integrada en una página con equivalente textual, etiquetas legibles y fuente editable. Permitir lectura en escritorio y móvil sin reducir el texto hasta hacerlo ilegible.

**Criterios observables:**
- Existen exactamente los cinco nodos y las cinco relaciones descritas; la dirección, la bifurcación y el retorno son inequívocos.
- «Completa» e «incompleta» están asociadas a la flecha correcta; cada conector se une a su nodo sin atravesar etiquetas o grupos ajenos.
- Retícula, tamaños, padding, tipografía y flechas son consistentes; no hay cruces evitables, solapamientos ni espacios muertos dominantes.
- El recorrido principal domina y la corrección se identifica sin depender solo del color; no hay información añadida para adornar.
- En móvil la composición se adapta o dispone de vista detallada con scroll localizado justificado; las etiquetas conservan legibilidad y existe explicación textual equivalente.

## Cierre de la aceptación

Informa de escenarios ejecutados, condiciones, evidencia inspeccionada, criterios con defectos o no comprobados y límites de la comparación. Un encargo preparado no es una prueba ejecutada. Una evaluación de contenido sin render no demuestra mejora visual; tampoco la demuestra una captura generada pero no vista.
