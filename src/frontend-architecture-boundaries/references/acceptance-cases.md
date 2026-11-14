# Casos de aceptación

Ocho escenarios que la skill debe resolver sin desviarse hacia una migración por inercia. Se leen cuando el encargo se parece a uno de ellos; cada uno indica el desenlace esperado y la regla que lo sostiene.

| # | Escenario | Desenlace esperado |
|---|---|---|
| 1 | App pequeña, un equipo, releases coordinadas | Mantener; no recomendar microfrontends |
| 2 | Monolito acoplado con imports cruzados | Clarificar límites y modularidad interna |
| 3 | Releases bloqueadas por un pipeline común | Evaluar seriamente separar despliegues |
| 4 | Shell que conoce el interior del módulo | Identificar acoplamiento y proponer interfaz mínima |
| 5 | Un módulo no se descarga | Preservar navegación y recuperación controlada |
| 6 | Una versión nueva falla tras publicar | Rollback sin reconstruir módulos ajenos |
| 7 | Versiones incompatibles de una librería compartida | Política de compatibilidad verificable |
| 8 | Sin datos de bloqueos ni costes | Diagnóstico provisional y petición de evidencia |

## Caso 1: app pequeña, un equipo, despliegues coordinados

**Situación.** Una aplicación, un equipo, un pipeline y ninguna release retenida. La coordinación es barata porque no hay nadie con quien coordinar.

**Desenlace.** Mantener la arquitectura. Documentar la decisión, los límites internos que ya existen y las condiciones que la revisarían —por ejemplo, un segundo equipo con ritmo propio o bloqueos medidos—.

**Regla aplicada.** Un monorepo, una app grande o muchos equipos no son prueba de un problema de autonomía (`SKILL.md`, invariante 2). La separación de despliegues añade un coste que aquí no compra nada.

**Prohibido.** Recomendar microfrontends «para el futuro» o porque el equipo crecerá. El crecimiento es una hipótesis sin fecha ni evidencia.

## Caso 2: monolito acoplado

**Situación.** Imports cruzados entre áreas, reglas de negocio compartidas en utilidades y cambios que siempre tocan dos o tres carpetas. El despliegue sigue siendo uno y no hay bloqueos medidos.

**Desenlace.** Priorizar los límites internos: identificar dominios, definir interfaces públicas, prohibir imports no autorizados con la herramienta que ya exista y agregar pruebas por límite. Si el despliegue único sigue siendo suficiente, no se separa.

**Regla aplicada.** El acoplamiento interno con un solo ritmo de release se resuelve mejor con límites internos (`references/architecture-decision.md`, «Reglas de decisión»). La modularidad es el paso 2 de la escalera de complejidad.

**Prohibido.** Convertir el acoplamiento en una migración a runtime sin haber probado antes los límites internos.

## Caso 3: releases bloqueadas por un pipeline común

**Situación.** Dos dominios estables, con cadencias distintas, cuyas releases esperan por un pipeline compartido. Existen retrasos medidos: fechas perdidas, esperas registradas, rollbacks conjuntos.

**Desenlace.** Evaluar seriamente la separación de despliegues. Comparar composición por rutas y módulos remotos en runtime con los diez criterios, y elegir la menor complejidad que elimine el bloqueo. Si la causa es el pipeline y no los artefactos, la primera opción puede ser separar el pipeline, no la interfaz.

**Regla aplicada.** Un bloqueo medido y atribuible al pipeline común es el requisito que más justifica separar despliegues (`references/architecture-decision.md`, «Reglas de decisión»). La independencia se comprueba publicando un módulo sin reconstruir los demás (`references/deployment-and-rollback.md`, «Despliegue independiente»).

**Prohibido.** Dar por hecha la independencia porque los módulos viven en carpetas distintas.

## Caso 4: contrato excesivo

**Situación.** El shell conoce los filtros, los formularios, el estado interno o los textos del módulo; los pasa como parámetros y reacciona a cambios internos.

**Desenlace.** Identificar el acoplamiento, señalar qué información no debería cruzar la frontera y proponer una interfaz mínima: entrada y contenedor, contexto acotado, eventos de hechos y errores. Mover al módulo la responsabilidad de su estado, sus filtros y su presentación.

**Regla aplicada.** El contrato mínimo prohíbe exponer estado interno y detalles de presentación (`SKILL.md`, invariante 5; `references/contracts-and-lifecycle.md`, «Principio del contrato mínimo»). Si el shell necesita el detalle, el límite está mal trazado.

**Prohibido.** Añadir una capa que oculte el acoplamiento sin corregir el contrato.

## Caso 5: fallo de un módulo remoto

**Situación.** Un módulo no se descarga o no arranca. El shell y el resto de módulos deben seguir siendo utilizables.

**Desenlace.** Preservar la navegación y los módulos independientes. Definir la respuesta por momento del fallo —descarga, inicialización, montaje, ejecución posterior—, con reintento acotado, mensaje claro, registro con módulo y versión y, si existe, versión alternativa. La ruta afectada se aísla; el resto de la aplicación no se bloquea.

**Regla aplicada.** `references/deployment-and-rollback.md`, «Fallos de carga». Un error de un módulo no puede dejar el shell en un estado sin salida.

**Prohibido.** Recargar toda la aplicación como única respuesta o dejar una pantalla en blanco sin diagnóstico.

## Caso 6: rollback tras un despliegue fallido

**Situación.** Una versión nueva de un módulo falla después de publicarse. Hay que volver a la anterior sin reconstruir los módulos ajenos ni el shell.

**Desenlace.** Seleccionar la versión anterior en la configuración de versiones, verificar que el resto conserva sus versiones y registrar el cambio. Comprobar que la caché no sirve la versión retirada y que las sesiones activas tienen una política definida.

**Regla aplicada.** `references/deployment-and-rollback.md`, «Rollback» y «Selección explícita de versiones». El rollback se ensaya antes de depender de él.

**Prohibido.** Presentar un rollback que exige reconstruir todo el sistema como independiente.

## Caso 7: dependencias incompatibles

**Situación.** El shell y un módulo remoto exigen versiones incompatibles de una librería compartida —por ejemplo, el framework o la librería de estado—.

**Desenlace.** Detectar el riesgo antes de producción: la negociación de versiones no elimina una incompatibilidad real de API. Definir una política verificable: versión única compartida y ventana de actualización, aislamiento de la dependencia con su coste, o no compartirla. Añadir una prueba que falle cuando las versiones declaradas dejen de ser compatibles.

**Regla aplicada.** `references/contracts-and-lifecycle.md`, «Dependencias compartidas»; `references/integration-patterns.md`, «Módulos remotos en runtime».

**Prohibido.** Declarar compatibilidad porque la aplicación arranca en local con una sola versión instalada.

## Caso 8: evidencia insuficiente

**Situación.** No hay datos de bloqueos, esperas, frecuencia de cambios conjuntos ni coste de coordinación. La petición de microfrontends llega sin problema demostrado.

**Desenlace.** Diagnóstico provisional: lo observado, lo inferido y lo desconocido. Petición concreta de evidencia y propuesta de medición mínima. La recomendación queda como `Propuesta`; si se implementa algo, se limita a mejoras de límites internos que no dependan de la decisión pendiente.

**Regla aplicada.** `SKILL.md`, fase 2 y «Errores y paradas»; `references/domain-boundaries.md`, «Evidencia insuficiente».

**Prohibido.** Justificar la migración con una hipótesis, con una moda tecnológica o con el tamaño del repositorio.
