# Despliegue y recuperación

Este fichero desarrolla la fase 5 y la verificación de la fase 7 del `SKILL.md`. Su objetivo es impedir que una arquitectura se declare independiente sin serlo.

## Artefactos por versión

- Cada módulo produce un artefacto identificable e inmutable con su versión.
- El shell produce el suyo, y su versión es independiente de las de los módulos que consume.
- La versión debe aparecer en el artefacto, en el registro de despliegue y en la observabilidad.
- Un artefacto no se sobrescribe. Si hay que corregirlo, se publica otra versión.

Sin artefactos separados no hay despliegue separado, aunque el código viva en carpetas distintas.

## Selección explícita de versiones

- El sistema decide qué versión de cada módulo se sirve, y esa decisión es visible y reversible.
- Evita la selección implícita «la última que haya»: impide reproducir un estado y complica el rollback.
- Una configuración de versiones —manifiesto, tabla de rutas, cabecera o registro— es más fácil de auditar y revertir que un despliegue completo.
- Registra qué versión estaba activa, cuándo se cambió y quién lo hizo.

## Política de compatibilidad

Define y verifica:

- versiones de contrato aceptadas por el shell y por cada módulo;
- versiones de dependencias compartidas y qué ocurre si no coinciden;
- ventana de convivencia entre versiones;
- procedimiento de retirada de una versión antigua.

Una política sin prueba es una intención. Añade una prueba que falle cuando un módulo declare una versión de contrato que el shell no acepta, o viceversa.

## Despliegue independiente

Comprueba, no asumas:

1. Publica un módulo nuevo sin reconstruir ni redesplegar los demás.
2. Verifica que el resto de módulos y el shell siguen sirviendo su versión anterior.
3. Comprueba que el pipeline no reconstruye todo por compartir un grafo de build o una imagen.
4. Repite con el shell para confirmar que sus cambios no obligan a republicar cada módulo.

Si cualquiera de los cuatro pasos falla, la independencia es de código, no de despliegue.

## Rollback

- Debe existir una forma de volver a una versión anterior sin reconstruir módulos ajenos.
- El rollback debe cubrir tanto el artefacto como la configuración de selección de versión.
- Define quién puede ejecutarlo, cuánto tarda y qué se comunica.
- Conserva las versiones anteriores el tiempo suficiente para cubrir sesiones activas y una ventana de diagnóstico.
- Ensaya el rollback al menos una vez antes de depender de él. Un rollback no probado es una hipótesis.

## Caché

- Los artefactos versionados se pueden cachear de forma agresiva; la configuración de selección no.
- Una caché mal configurada puede servir una versión retirada o impedir un rollback inmediato.
- Define la invalidación de la configuración y la coherencia entre CDN, navegador y servidor.
- Comprueba el comportamiento con una sesión abierta durante un despliegue.

## Conservación de artefactos para sesiones activas

Una sesión abierta puede necesitar cargar un módulo que ya ha sido sustituido. Decide:

- si las sesiones activas conservan la versión con la que empezaron;
- cuánto tiempo se conservan artefactos antiguos;
- qué ocurre si un artefacto ya no existe;
- cómo se fuerza la actualización sin perder trabajo del usuario.

La respuesta debe estar escrita y probada, no depender de que nadie navegue durante el despliegue.

## Fallos de carga

Distingue cuatro momentos, porque la recuperación es distinta:

1. **Descarga.** El artefacto no llega: red, CDN, ruta incorrecta o versión retirada. Respuesta: reintento acotado, versión alternativa si existe, mensaje y conservación del resto de la aplicación.
2. **Inicialización.** El código llega pero no arranca: versión incompatible, dependencia ausente, error de configuración. Respuesta: registro con módulo y versión, aislamiento de la ruta, alternativa o mensaje.
3. **Montaje.** Arranca pero no puede montarse: contenedor ausente, contrato incumplido, error de datos. Respuesta: no dejar el contenedor en estado inconsistente; permitir reintento o salida.
4. **Ejecución posterior.** Montado y falla después: error de negocio, estado imposible, error no capturado. Respuesta: contención del error, conservación de la navegación y registro con contexto.

En los cuatro casos: el shell debe seguir siendo navegable y los módulos independientes deben seguir funcionando.

## Observabilidad

- Cada error debe identificar módulo, versión, entorno y punto de fallo.
- Registra las cargas de módulos y su resultado, no solo los errores.
- Mide el tiempo de carga y el porcentaje de fallos por módulo y versión.
- Separa errores de integración —descarga, contrato, montaje— de errores de negocio del módulo.
- Una alerta sin módulo y versión no permite decidir un rollback.

## Verificación de la recuperación

- [ ] Existe un artefacto por versión y no se sobrescribe.
- [ ] La versión servida se selecciona de forma explícita y reversible.
- [ ] La compatibilidad de contrato y de dependencias tiene una prueba.
- [ ] Se ha publicado un módulo sin reconstruir los demás.
- [ ] Se ha ejecutado o ensayado un rollback y se registró el resultado.
- [ ] La caché no impide un rollback inmediato.
- [ ] Las sesiones activas tienen una política de versiones y artefactos.
- [ ] Los cuatro modos de fallo están simulados o declarados como no verificados.
- [ ] Un fallo de módulo no rompe la navegación del shell ni los módulos independientes.
- [ ] Los errores de integración se pueden atribuir a módulo y versión.
