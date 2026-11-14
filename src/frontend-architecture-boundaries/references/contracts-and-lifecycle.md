# Contratos y ciclo de vida

Este fichero desarrolla la fase 5 del `SKILL.md`. Define qué debe saber el shell de un módulo, qué no debe saber, y cómo se comporta el módulo desde que se carga hasta que se retira.

## Principio del contrato mínimo

El shell compone, resuelve contexto y garantiza navegación, sesión y recuperación. El módulo posee su dominio: su estado, sus datos, sus filtros, sus formularios y su presentación.

El shell no conoce:

- el estado interno del módulo ni sus estructuras de datos;
- los filtros, formularios o pasos de su interfaz;
- los detalles de su presentación, textos, validaciones o componentes;
- sus llamadas de negocio, salvo el permiso para hacerlas.

Si el shell necesita alguno de esos detalles, o el contrato está inflado o el límite está mal trazado. En ese caso, corrige el contrato antes de añadir otra capa que lo oculte.

## Contrato de entrada y montaje

Documenta para cada módulo:

| Campo | Contenido |
|---|---|
| Identidad | Nombre, versión y dueño del módulo |
| Punto de entrada | Qué exporta y cómo se carga |
| Entrada | Elemento contenedor o punto de montaje |
| Contexto | Datos que el shell entrega: locale, tema, entorno, ruta base y referencias a servicios permitidos |
| Salida | Operaciones que el módulo expone al shell, si alguna |
| Eventos | Los que emite y los que consume, con su forma y su significado |
| Errores | Cómo informa de un fallo y qué espera del shell |
| Limpieza | Qué libera al desmontarse |

El montaje debe ser idempotente o declarar que no lo es. Un módulo que no puede volver a montarse tras desmontarse necesita justificación escrita.

## Contexto del shell

El contexto debe ser pequeño, versionado y explícito:

- locale, zona horaria y formato;
- tema o variables de presentación, sin dictar la interfaz del módulo;
- entorno y banderas de funcionalidad, si el proyecto las usa;
- ruta base o rutas autorizadas;
- funciones de navegación expuestas por el shell, nunca el objeto de historial completo;
- acceso a la sesión mediante una API que consulte al servidor, no mediante un objeto de usuario mutable.

No entregues el store global como contexto. Un módulo que lee y escribe el estado de todos los demás no es independiente.

## Desmontaje y limpieza

Al desmontar, el módulo debe:

- cancelar peticiones en curso y suspender trabajos periódicos;
- retirar listeners de ventana, documento y elementos;
- limpiar temporizadores y suscripciones;
- liberar el contenedor que ocupa;
- dejar el historial y la ruta en un estado coherente.

El shell debe retirar el contenedor y no conservar referencias al módulo. Una fuga tras varias navegaciones es un defecto de contrato, no un detalle de rendimiento.

## Routing

- Una sola autoridad posee las rutas y el historial. Las demás consultan y navegan a través de ella.
- Define si el módulo puede declarar rutas hijas y cómo se evita que dos módulos reclamen la misma.
- Define el comportamiento al entrar en una ruta de un módulo que ha fallado: mensaje, reintento y salida.
- El estado de navegación no debe depender de que un módulo esté cargado.

## Eventos entre dominios

Los eventos sirven para notificar hechos, no para confirmar operaciones de negocio.

- Nombra los eventos por el hecho ocurrido, no por la acción de interfaz.
- Define su forma, su versión y su compatibilidad.
- Un evento no es una transacción: si el efecto debe persistir, se confirma en el servidor.
- Evita cadenas de eventos que reconstruyen un flujo de negocio entre módulos. Si el flujo es uno, probablemente el límite está mal.
- El shell no debe interpretar eventos internos del módulo ni usarlos para mantener su propio estado de presentación.

## Versiones y compatibilidad

- Cada módulo declara su versión y la del contrato que implementa.
- El shell declara qué versiones de contrato acepta.
- Un cambio incompatible del contrato exige versión mayor, ventana de convivencia y plan de retirada.
- La compatibilidad se comprueba de forma verificable: una prueba de contrato que ejecute el shell contra las versiones soportadas.
- No declares compatible un módulo solo porque compila contra la interfaz.

## Errores

Distingue, al menos:

- fallo de descarga del artefacto;
- fallo de inicialización;
- fallo de montaje;
- fallo de ejecución posterior al montaje.

Cada uno tiene una respuesta distinta: reintento, mensaje, aislamiento de la ruta, conservación del resto de la aplicación y registro con módulo y versión. El detalle operativo está en `deployment-and-rollback.md`.

Un error de un módulo no debe dejar el shell en un estado del que no pueda salir.

## Dependencias compartidas

- Declara qué dependencias comparte el shell y cuáles trae cada módulo.
- Una dependencia compartida debe tener una única instancia cuando su estado o su identidad lo exijan —por ejemplo, el runtime del framework o la librería de sesión—.
- Fija la política cuando dos módulos exigen versiones incompatibles: actualizar, aislar o no compartir. Cada opción tiene coste.
- Una incompatibilidad detectada en pruebas es un requisito de la política, no un incidente de producción.

## Autenticación y confianza

- El shell puede obtener el contexto de sesión, pero la autorización se decide en el servidor.
- Los identificadores, roles y permisos recibidos del navegador son datos no confiables: se validan y se aplican en el backend.
- Ocultar un botón o una ruta no es autorización.
- Un módulo no recibe credenciales de otro módulo. Si necesita un servicio, usa el mecanismo del shell o su propia integración autorizada.
- Las operaciones persistentes se confirman en el backend. Un evento del navegador no demuestra que una operación se completó.
- Los mensajes entre iframes validan origen y forma; los mensajes entre módulos validan su contrato.

## Lista de comprobación del contrato

- [ ] El contrato cabe en una tabla y no menciona detalles internos del módulo.
- [ ] Montaje y desmontaje están definidos y se han probado más de una vez.
- [ ] El contexto es pequeño, versionado y no incluye el store global.
- [ ] Hay una sola autoridad de routing.
- [ ] Los eventos notifican hechos; las operaciones persistentes se confirman en el servidor.
- [ ] La compatibilidad de versiones tiene una prueba ejecutable.
- [ ] Los cuatro modos de fallo tienen respuesta definida.
- [ ] La política de dependencias compartidas resuelve una incompatibilidad conocida o declara cómo se resolverá.
- [ ] La autorización no depende de datos del navegador.
