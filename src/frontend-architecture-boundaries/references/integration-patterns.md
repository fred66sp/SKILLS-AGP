# Patrones de integración

Este fichero desarrolla la fase 3 y la fase 5 del `SKILL.md`. Describe las tecnologías de composición con sus capacidades y sus costes. No es un manual de configuración: las APIs y las versiones cambian, y hay que verificar la documentación de la versión que use el proyecto antes de escribir código.

## Composición en build-time

Los módulos se publican como paquetes —workspaces, registro privado o repositorio— y la aplicación los importa al construir.

- **Capacidades.** Propiedad por paquete, versión explícita, pruebas aisladas, tipado compartido y una única salida desplegable.
- **Costes.** Cualquier cambio requiere reconstruir y redesplegar la aplicación; el versionado debe gestionarse.
- **Adecuada para.** Reutilización y límites internos con un solo ritmo de release.
- **Riesgos.** Paquetes que se convierten en dependencias ocultas del shell; cambios de versión que arrastran a todos.

## Composición por rutas

Cada área o ruta se sirve como entrada propia —aplicación separada, HTML propio o bundle independiente— detrás de un router o de un proxy.

- **Capacidades.** Despliegue independiente por área, fallos contenidos por ruta, adopción incremental y recuperación sencilla.
- **Costes.** Navegación entre áreas que puede recargar la página; estado y sesión que deben compartirse; posible duplicación de shell y de dependencias.
- **Adecuada para.** Dominios con pantallas completas propias y pocos momentos de composición en una misma vista.
- **Riesgos.** Experiencia inconsistente entre áreas; autenticación duplicada; problemas de historial del navegador.

## Módulos remotos en runtime

Un contenedor —el shell o host— carga en tiempo de ejecución código publicado por otros equipos.

Module Federation, en sus variantes para bundlers modernos, ofrece conceptos equivalentes:

- **Host y remote.** El host consume; el remote expone módulos, componentes o funciones.
- **Exposes y entry.** El remote declara qué publica y genera un artefacto de entrada —habitualmente `remoteEntry`— que el host descarga y consulta.
- **Shared.** Las dependencias compartidas se pueden declarar para reutilizar una instancia —por ejemplo, el framework— en lugar de duplicarla. La negociación de versiones tiene reglas propias y no resuelve incompatibilidades reales de API.
- **Carga dinámica.** El host puede cargar un remote en un momento concreto, lo que permite seleccionar versión y tratar el fallo.
- **Composición.** El código remoto se monta en un contenedor del host, con las consecuencias de ciclo de vida y estilos que eso implica.

Costes que hay que asumir:

- compatibilidad entre versiones de runtime y de librerías compartidas;
- configuración de publicación y de caché por artefacto;
- diagnóstico de errores que cruzan repositorios;
- estrategia de fallo y de rollback por módulo;
- diferencias entre desarrollo local y producción.

No recomiendes esta opción si el requisito se satisface con build-time o por rutas. Antes de diseñarla, lee `deployment-and-rollback.md` y `contracts-and-lifecycle.md`.

## Orquestadores de aplicaciones

single-spa organiza varias aplicaciones en una página y decide cuál está activa según la ruta.

- **Capacidades.** Aplicaciones independientes con un ciclo de vida explícito —`bootstrap`, `mount`, `unmount`—, actividad por ruta y composición de áreas en una misma página.
- **Costes.** Un contenedor raíz que hay que poseer y mantener, registro de aplicaciones, coordinación de estilos y estado, y disciplina de ciclo de vida.
- **Adecuada para.** Varias aplicaciones de frameworks distintos o adopción incremental por rutas.
- **Riesgos.** El contenedor se convierte en un shell con demasiadas responsabilidades; duplicación de dependencias; orden de montaje y desmontaje mal gestionado.

## Composición en servidor

El servidor compone fragmentos HTML de distintos orígenes —SSI, Edge Side Includes, streaming o un servicio de composición—.

- **Capacidades.** Sin runtime de módulos en el cliente, tiempos de primera carga controlables, aislamiento por fragmento.
- **Costes.** Acoplamiento al servidor de composición, latencia de agregación, caché por fragmento y estrategia de hidratación si hay interactividad.
- **Adecuada para.** Contenido mayoritariamente estático con áreas interactivas acotadas.
- **Riesgos.** Fallos parciales que rompen el HTML; dificultad para compartir estado interactivo.

## Web Components

Cada módulo se publica como custom element con su propio DOM y estilos encapsulados.

- **Capacidades.** Contrato de elemento estándar, aislamiento razonable de estilos, independencia del framework.
- **Costes.** Integración con el router, propiedades frente a atributos, eventos, formularios, accesibilidad y SSR.
- **Adecuada para.** Widgets o áreas autocontenidas con poca integración con el resto.
- **Riesgos.** Shadow DOM que complica estilos globales y pruebas; duplicación de framework si cada elemento trae el suyo.

## iframes

Cada módulo se sirve como documento aislado.

- **Capacidades.** Aislamiento fuerte de CSS y JavaScript, despliegue y fallo independientes, sandbox de seguridad.
- **Costes.** Comunicación por mensajes, altura y scroll, foco, historial, accesibilidad, rendimiento y autenticación.
- **Adecuada para.** Contenido de terceros o áreas con requisitos de aislamiento fuertes.
- **Riesgos.** Integración visual y de navegación pobre; validación de origen y de mensajes imprescindible.

## Criterios técnicos transversales

Antes de elegir un patrón, comprueba:

- **Router.** ¿Quién posee el historial y las rutas? Una sola autoridad evita estados imposibles.
- **Estilos.** ¿Hay encapsulación suficiente o se necesita una política de colisión?
- **Dependencias compartidas.** ¿Puede haber dos versiones incompatibles del framework o de una librería de estado?
- **Sesión y autenticación.** ¿Cómo recibe cada módulo el contexto sin duplicar la lógica de autorización?
- **Fallos.** ¿Qué ocurre si el código no descarga, falla al inicializar o falla después?
- **Pruebas.** ¿Se puede probar el módulo solo y la composición completa?
- **Observabilidad.** ¿Se puede atribuir un error a un módulo y a una versión?

## Advertencia de vigencia

Los ejemplos de configuración de la documentación oficial pueden describir versiones distintas de las del proyecto. Verifica siempre:

1. la versión del bundler, del runtime de composición y del framework;
2. si la API usada existe en esa versión y no está marcada como experimental;
3. el comportamiento de las dependencias compartidas en el entorno real;
4. la estrategia de publicación y de caché del artefacto remoto.

Si no puedes verificar alguno de estos puntos, declara la limitación en el informe. No presentes una configuración de ejemplo como recomendación vigente.
