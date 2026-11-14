# Decisión de arquitectura

Compara alternativas con los mismos criterios y elige la de menor complejidad que resuelva el problema demostrado. Este fichero desarrolla la fase 3 y la fase 4 del `SKILL.md`.

## Las cinco opciones mínimas

| Opción | Qué es | Qué resuelve | Qué no resuelve | Coste principal |
|---|---|---|---|---|
| Mantener el monolito | Un único artefacto y un único despliegue, con la estructura actual | Nada por sí sola; preserva lo que ya funciona | Acoplamiento interno y bloqueos de release | Ninguno nuevo; el coste actual permanece |
| Monolito modular | Un despliegue, límites internos explícitos e interfaz pública por módulo | Imports cruzados, responsabilidades mezcladas y cambios en cascada | Bloqueos de despliegue entre dominios | Disciplina de límites; refactor de imports |
| Composición build-time | Paquetes versionados que se combinan al construir la aplicación | Reutilización, propiedad clara por paquete y pruebas aisladas | Despliegues independientes | Versionado y publicación de paquetes; releases coordinadas |
| Composición por rutas | Cada ruta o área se sirve como aplicación o entrada separada | Separación de despliegues por área y fallos contenidos por ruta | Composición dentro de una misma pantalla | Contratos de navegación y sesión; duplicación de shell |
| Módulos remotos en runtime | Un shell carga código de módulos publicados por separado | Despliegue independiente con integración en la misma pantalla | Complejidad, compatibilidad y diagnóstico de fallos | Runtime, versiones compartidas, observabilidad y recuperación |

Opciones adicionales, solo con un requisito que las exija: composición en servidor, Web Components, iframes y orquestadores de aplicaciones como single-spa. Sus detalles están en `integration-patterns.md`.

## Criterios de evaluación

Puntúa cada opción con la misma escala y con evidencia. No uses una media: un criterio con resultado inaceptable descarta la opción aunque los demás sean buenos.

1. **Independencia de despliegue.** ¿Se puede publicar un módulo sin reconstruir ni redesplegar los demás? ¿Y revertirlo?
2. **Complejidad operativa.** Artefactos, entornos, pipelines, configuración, permisos y personas necesarias para operar.
3. **Acoplamiento.** Dependencias entre módulos, estado compartido, utilidades comunes y frecuencia de cambios conjuntos.
4. **Compatibilidad.** Versiones de runtime, librerías compartidas, navegadores y APIs internas que deben convivir.
5. **Rendimiento.** Peso descargado, peticiones añadidas, tiempo hasta interacción y coste de mantener varias versiones vivas.
6. **Desarrollo local.** ¿Se puede trabajar y probar un módulo sin levantar el sistema completo?
7. **Pruebas.** Unitarias, de contrato, de integración y simulación de fallos; qué se puede verificar por separado.
8. **Rollback.** Selección de versión anterior, tiempo de recuperación y efecto sobre sesiones activas.
9. **Observabilidad.** Errores de carga y de ejecución atribuibles a un módulo y a una versión concretos.
10. **Coste de mantenimiento.** Personas, documentación y automatización que la opción exige de forma permanente.

## Escalera de complejidad

Sube un escalón solo cuando el anterior no satisface un requisito demostrado:

1. Mantener la arquitectura y corregir el proceso que causa el bloqueo (por ejemplo, un pipeline que no puede publicar por separado).
2. Clarificar límites internos y aplicar control de imports.
3. Extraer paquetes versionados en build-time.
4. Separar rutas o áreas con despliegue propio.
5. Componer módulos remotos en runtime.

Cada escalón añade modos de fallo que antes no existían. Si el problema es de coordinación de personas y no de artefactos, la respuesta puede ser de proceso, no de arquitectura.

## Reglas de decisión

- **Un bloqueo medido y atribuible al pipeline común** es el requisito que más justifica separar despliegues. Sin medición, no hay justificación.
- **Acoplamiento interno con un solo ritmo de release** se resuelve mejor con límites internos que con microfrontends.
- **Necesidad de componer pantallas con módulos de distintos equipos en runtime** es el requisito propio de los módulos remotos. La familiaridad con la herramienta no es un requisito.
- **Reutilización de código sin independencia de release** se resuelve en build-time.
- **Fallos que deben quedar contenidos por área** pueden resolverse con composición por rutas antes que con un runtime.
- **Presupuesto de rendimiento ajustado** penaliza la composición en runtime; cuantifícalo antes de decidir.
- **Equipos pequeños con releases coordinadas** rara vez necesitan separar despliegues. La separación añade coste proporcional al número de artefactos, no al número de carpetas.

## Registro de la decisión

Rellena `../assets/decision-record.md` con:

- contexto y problema demostrado, con su evidencia;
- hechos, inferencias y desconocidos que afectan a la decisión;
- opciones consideradas, incluida la de no cambiar nada;
- motivo del descarte de cada opción;
- decisión y tecnología derivada, con el requisito que la exige;
- consecuencias: coste operativo, de desarrollo, de pruebas y de observabilidad;
- condiciones que obligan a revisar la decisión.

Una decisión sin condiciones de revisión es una decisión que nadie volverá a examinar.

## Falsos positivos frecuentes

- **«Tenemos un monorepo, así que necesitamos microfrontends.»** Un monorepo es una decisión de organización del código, no una prueba de bloqueo de despliegue.
- **«La aplicación es grande.»** El tamaño no demuestra acoplamiento entre equipos ni lentitud de release.
- **«Module Federation es el estándar.»** Es una tecnología disponible, no un requisito. Solo entra si hay que cargar código ajeno en runtime.
- **«Cada equipo tendrá su release.»** Si los módulos comparten versión de librerías y ventana de despliegue, la independencia es nominal.
- **«Lo pide el usuario.»** Se documenta como requisito del encargo, pero si la evidencia no lo sostiene se explica el desacuerdo antes de ejecutar.
