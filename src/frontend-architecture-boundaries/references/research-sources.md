# Fuentes de investigación

Este fichero registra qué fundamenta cada fuente y qué límite tiene. La skill no copia su contenido: deriva decisiones y las somete a la evidencia del proyecto.

## Fuentes técnicas

| Fuente | Qué fundamenta | Límite |
|---|---|---|
| [Fowler — Micro Frontends](https://martinfowler.com/articles/microfrontends.html) | Límites por dominio de negocio, equipos autónomos, composición de la interfaz y los costes de coordinación que la separación pretende reducir | Artículo de referencia conceptual, no una especificación de implementación ni una recomendación universal |
| [Webpack — Module Federation](https://webpack.js.org/concepts/module-federation/) | Concepto de host y remote, módulos expuestos, dependencias compartidas y composición en runtime | Documentación de una herramienta y una versión concretas; no demuestra que la separación sea necesaria |
| [Webpack — ModuleFederationPlugin](https://webpack.js.org/plugins/module-federation-plugin/) | Opciones del plugin, declaración de `exposes`, `remotes`, `shared` y del artefacto de entrada del remote | Las opciones y sus nombres cambian entre versiones; verificar contra la versión instalada |
| [Module Federation — runtime](https://module-federation.io/guide/runtime/) | Comportamiento en tiempo de ejecución: carga de remotos, resolución de dependencias compartidas, carga dinámica y consideraciones de compatibilidad | Guía de un proyecto que evoluciona; puede describir una versión distinta de la del proyecto |
| [single-spa — documentación](https://single-spa.js.org/docs/) | Aplicaciones independientes, actividad por ruta, ciclo de vida `bootstrap`/`mount`/`unmount` y contenedor raíz | Documentación de una herramienta concreta; el coste del contenedor y de la coordinación no desaparece |
| [Agent Skills — specification](https://agentskills.io/specification) | Formato de la skill: frontmatter, nombre, descripción, divulgación progresiva y recursos | Especificación de formato; no valida las decisiones de arquitectura del proyecto |

## Qué capacidad sostiene cada fuente

- **Límites de dominio y equipos autónomos.** Fowler aporta el criterio de que la unidad de separación es una responsabilidad de negocio con un equipo que puede poseerla, no una carpeta ni un componente visual.
- **Composición en runtime.** La documentación de Module Federation aporta los conceptos de host, remote, artefacto de entrada y dependencias compartidas, y los límites de la negociación de versiones.
- **Ciclo de vida y composición por rutas.** single-spa aporta el modelo de aplicaciones con montaje y desmontaje explícitos y actividad por ruta.
- **Formato de la skill.** La especificación de Agent Skills aporta la estructura y las reglas de metadatos que este paquete cumple.

## Cómo se usan

1. Cita la fuente cuando una afirmación técnica condicione una recomendación.
2. No presentes una configuración de ejemplo como vigente. Antes de escribir código, verifica la API y la versión en la documentación de la versión instalada.
3. Distingue capacidad documentada de comportamiento comprobado en el proyecto. Solo lo segundo cuenta como evidencia para decidir.
4. Si la documentación de la versión usada no está disponible o contradice la guía general, prevalece la versión instalada y se declara la limitación.

## Fuentes que no se usan como autoridad

- Comparativas de herramientas sin metodología: sirven como pista, no como evidencia.
- Ejemplos de configuración copiados sin versión: no demuestran compatibilidad.
- Argumentos de moda o de adopción: no sustituyen una medición del problema.

## Vigencia

Las fuentes se consultaron para redactar la versión 0.1.0. Las APIs de composición en runtime, los bundlers y los orquestadores cambian con frecuencia. Si una recomendación depende de una capacidad concreta, compruébala en la documentación de la versión que use el proyecto y registra el resultado en el informe.
