---
name: frontend-architecture-boundaries
description: "Evalúa y diseña los límites de un frontend: diagnostica acoplamiento y bloqueos de despliegue con evidencia, compara monolito, modularidad interna, composición en build, composición por rutas y módulos remotos, y recomienda la alternativa de menor complejidad que resuelva los problemas demostrados. Define contratos shell-módulo, despliegue y rollback independientes y una migración incremental verificable. Úsala para auditar la arquitectura de una aplicación web, decidir si procede adoptar microfrontends o Module Federation, justificar o descartar la separación de despliegues, o diseñar e implementar esos límites con autorización explícita. No la uses para diseño visual, sistema de diseño, componentes de interfaz, rendimiento de render, elección de framework, arquitectura de backend ni microservicios."
metadata:
  version: "0.1.0"
---

# Límites de arquitectura frontend

Decide y documenta dónde acaban los límites de un frontend y si esos límites deben llegar a ser fronteras de despliegue. La separación del código no garantiza independencia de despliegue; la independencia de despliegue no siempre justifica su coste.

Esta skill sirve para tres encargos y no para uno solo:

1. **Auditoría.** Inspeccionar y diagnosticar sin modificar archivos. El resultado es un informe con evidencia, opciones y recomendación.
2. **Decisión.** Elegir entre mantener la arquitectura, mejorar los límites internos o diseñar una migración incremental a microfrontends.
3. **Implementación.** Ejecutar la alternativa aprobada, solo dentro del alcance autorizado, y demostrar que cumple sus criterios de aceptación.

## Resultados legítimos

Son tres, y ninguno es el resultado por defecto:

- **Mantener la arquitectura existente.** Procede cuando no hay problemas demostrados que la separación resuelva. Se documenta la decisión y las condiciones que la revisarían.
- **Mejorar los límites internos de un frontend modular.** Procede cuando hay acoplamiento, imports cruzados o responsabilidades mezcladas, pero un único despliegue sigue siendo suficiente.
- **Diseñar una migración incremental a microfrontends.** Procede cuando existen bloqueos de despliegue medidos, dominios con ritmos distintos y un coste de coordinación demostrado que la separación reduce.

No recomiendes Module Federation, microfrontends ni ningún runtime de composición por defecto. La tecnología se deriva de requisitos verificables, no al contrario.

## Invariantes

1. **Evidencia antes que arquitectura.** Ninguna recomendación sin un problema observado, medido o declarado por una fuente identificable. Separa siempre hecho observado, inferencia y dato no disponible.
2. **Un monorepo, una app grande o muchos equipos no son prueba de un problema de autonomía.** Son contexto. La prueba es un bloqueo, un retraso, un incidente o un coste de coordinación medido.
3. **Conservadurismo ante la complejidad.** Entre dos opciones que resuelven el problema demostrado, elige la de menor complejidad operativa. Cada salto de complejidad necesita su justificación escrita.
4. **La separación de código no es separación de despliegue.** No declares independencia de despliegue sin comprobar que cada módulo se construye, publica, despliega y revierte por separado.
5. **Contratos mínimos.** El shell no conoce el estado interno, los filtros, los formularios ni los detalles de presentación de un módulo. Si los necesita, el contrato está mal diseñado o la frontera está en el sitio equivocado.
6. **La autoridad vive en el servidor.** Los identificadores, roles y permisos que llegan del navegador no son confiables. La autorización se decide y se aplica en el backend; las operaciones de negocio persistentes se confirman allí, no con eventos del navegador.
7. **Sin autorización no hay modificación.** En una auditoría no se toca código. En una implementación solo se modifica lo que el encargo autoriza.
8. **Toda recomendación es trazable.** Cada afirmación del informe apunta a una ruta, un comando, una métrica o una fuente. Lo que no se pudo comprobar se declara.

## Flujo de trabajo

Sigue las siete fases en orden. La profundidad se ajusta al tamaño del encargo; el orden y las comprobaciones no.

### Fase 1: Inspeccionar

1. Identifica el encargo: auditar, decidir o implementar; qué aplicación, qué repositorio, qué rama y qué límites de acceso existen.
2. Inventaría el stack y el sistema de entrega: framework, gestor de paquetes y workspaces, bundler, repositorio único o múltiple, pipeline, entornos, cadencia de release y responsables.
3. Mapea la estructura: aplicaciones, paquetes, rutas, módulos, carpetas de dominio y dependencias declaradas.
4. Detecta los límites que ya existen: exports públicos, `package.json`, aliases, project references, reglas de lint, CODEOWNERS, contratos de API y documentación de arquitectura.
5. Copia la estructura de `assets/architecture-assessment.md` y registra cada dato con su fuente, fecha y método de obtención.
6. Lee `references/domain-boundaries.md` para saber qué señales buscar y cómo distinguir un límite real de una carpeta.

### Fase 2: Diagnosticar

1. Reúne evidencia de los problemas concretos: imports cruzados, accesos a implementaciones internas, estado y utilidades compartidas, responsabilidades de negocio mezcladas, archivos que siempre cambian juntos, dependencias entre equipos, procesos de build y despliegue, bloqueos reales entre releases y rollbacks costosos o imposibles.
2. Etiqueta cada hallazgo como `Hecho`, `Inferencia` o `Desconocido`. Un `Hecho` tiene ruta, comando, métrica o registro. Una `Inferencia` explica de qué hecho se deriva. Un `Desconocido` dice qué dato falta y cómo obtenerlo.
3. No concluyas que existe un problema de autonomía de despliegue solo porque haya un monorepo, una aplicación grande, varios equipos o un pipeline compartido.
4. Si el diagnóstico depende de datos que no tienes —tiempos de espera, releases bloqueadas, frecuencia de cambios conjuntos, incidentes—, pide esos datos y entrega un diagnóstico provisional. No rellenes el hueco con una hipótesis presentada como hecho.
5. Lee `references/domain-boundaries.md`, secciones «Diagnóstico: qué buscar» y «Evidencia insuficiente».

### Fase 3: Comparar opciones

1. Lee `references/architecture-decision.md` y compara, como mínimo, estas opciones:
   - mantener el monolito existente;
   - monolito modular con límites explícitos;
   - composición por paquetes en build-time;
   - composición por rutas;
   - módulos remotos en runtime.
2. Añade, solo cuando el problema lo justifique, composición en servidor, Web Components, iframes o un orquestador de aplicaciones como single-spa. Lee `references/integration-patterns.md` antes de describir cualquiera de ellas.
3. Evalúa cada opción con los mismos criterios: independencia de despliegue, complejidad operativa, acoplamiento, compatibilidad, rendimiento, desarrollo local, pruebas, rollback, observabilidad y coste de mantenimiento.
4. Declara para cada opción qué problema demostrado resuelve, qué problema no resuelve y qué coste introduce.
5. Si falta evidencia para comparar, la comparación es provisional y así se etiqueta.

### Fase 4: Decidir

1. Elige la alternativa de **menor complejidad** que satisfaga los requisitos verificables. No elijas la más moderna ni la que pide el usuario si la evidencia no la sostiene; explica la diferencia.
2. Deriva la tecnología de los requisitos: si no hace falta cargar código ajeno en runtime, no introduzcas un runtime de módulos remotos.
3. Copia la estructura de `assets/decision-record.md` y registra contexto, hechos, hipótesis, opciones descartadas con su motivo, decisión, consecuencias y condiciones de revisión.
4. Si el resultado es mantener la arquitectura, la decisión también se documenta: qué se comprobó y qué haría falta para revisarla.
5. Lee `references/acceptance-cases.md` cuando el encargo se parezca a uno de sus escenarios; contiene el desenlace esperado y evita justificar una migración por inercia.

### Fase 5: Diseñar

1. Define los límites: candidatos por cohesión funcional, responsabilidad de negocio, propiedad de datos, cambios conjuntos, dependencias externas, interfaz pública y capacidad de prueba independiente. No dividas por componentes visuales pequeños.
2. Define la interfaz pública de cada límite y el mecanismo que impide imports no autorizados, reutilizando las herramientas que el proyecto ya tenga (reglas de lint, `exports`, project references, análisis de dependencias, revisión por propietarios).
3. Diseña el contrato shell-módulo y su ciclo de vida: entrada y montaje, desmontaje y limpieza, parámetros de contexto, routing, eventos entre dominios, versionado y compatibilidad, errores, dependencias compartidas y autenticación. Lee `references/contracts-and-lifecycle.md`.
4. Diseña el despliegue y la recuperación: artefactos por versión, selección explícita de versiones, política de compatibilidad, despliegue y rollback independientes, caché, conservación de artefactos para sesiones activas, comportamiento ante fallos de carga y observabilidad. Lee `references/deployment-and-rollback.md`.
5. Define las pruebas de cada límite: unitarias propias, contrato entre shell y módulo, integración de la composición y simulación de fallos.
6. Si la migración está justificada, planifícala con `assets/migration-checklist.md`, un dominio cada vez.

### Fase 6: Ejecutar

1. Comprueba que el encargo autoriza modificar código y qué alcance exacto cubre. Sin autorización, entrega el diseño y detente.
2. Implementa solo la alternativa decidida. No aproveches para reorganizar áreas no incluidas.
3. Mantén el comportamiento existente salvo que el encargo pida cambiarlo, y conserva la validación y el tratamiento de errores de todo código que muevas.
4. Registra cada desviación del diseño con su motivo y su efecto sobre la decisión.

### Fase 7: Verificar

1. Demuestra cada criterio de aceptación con evidencia ejecutada: comando, resultado, ruta o captura reproducible.
2. Simula los fallos que el diseño promete tolerar: módulo que no descarga, que falla al inicializar, que falla al montar y que falla después de montar.
3. Ejecuta un rollback real o un ensayo controlado. Si no puedes, declara la comprobación como no realizada.
4. Compara el resultado con la línea base del diagnóstico. Si no mejora el problema medido, la decisión se revisa.
5. Aplica la puerta de verificación de esta skill y muestra su resultado.

## Puerta de verificación

Comprueba cada punto y adjunta la evidencia. Un punto sin evidencia es un hallazgo, no un aprobado.

- [ ] Cada problema del diagnóstico tiene fuente: ruta y línea, comando ejecutado, métrica o declaración identificable de una persona.
- [ ] Cada afirmación está etiquetada como `Hecho`, `Inferencia` o `Desconocido`.
- [ ] La comparación incluye las cinco opciones mínimas y los diez criterios de la fase 3.
- [ ] La opción recomendada resuelve el problema demostrado con la menor complejidad operativa; las descartadas tienen motivo escrito.
- [ ] No se ha recomendado un runtime de composición sin un requisito que lo exija.
- [ ] El contrato shell-módulo no expone estado interno ni detalles de presentación del módulo.
- [ ] La autorización se decide en el servidor y ninguna operación persistente depende solo de un evento del navegador.
- [ ] Existe una política de versiones y compatibilidad verificable entre artefactos.
- [ ] El diseño distingue los cuatro modos de fallo de carga y define la respuesta de cada uno.
- [ ] El rollback está descrito y, si se ha ensayado, con su resultado.
- [ ] La independencia de despliegue está comprobada con un despliegue o una publicación real por separado, no solo declarada.
- [ ] Las pruebas cubren el contrato y la composición, no solo la unidad.
- [ ] Si es una auditoría, no se ha modificado ningún archivo.
- [ ] Si es una implementación, cada cambio pertenece al alcance autorizado.

## Cierre

Termina con este bloque, rellenado con evidencia y sin adjetivos:

```text
Encargo: <auditoría | decisión | implementación>
Alcance inspeccionado: <rutas, repositorios, ramas y fecha>
Problemas demostrados: <lista con evidencia, o "ninguno">
Hechos / inferencias / desconocidos: <recuento y referencia al anexo>
Opciones comparadas: <las cinco mínimas y las adicionales, o "no procede">
Decisión: <mantener | modularizar | migrar | no decidible>
Tecnología derivada: <ninguna | build-time | rutas | runtime | otra, con el requisito que la exige>
Coste introducido: <operativo, desarrollo, pruebas y observabilidad>
Condiciones de revisión: <qué dato obligaría a revisar la decisión>
Verificación ejecutada: <comandos y resultados>
No verificado: <lista, o "ninguno">
```

No presentes una decisión como aprobada si el usuario no la ha aprobado. Márcala como `Propuesta`.

## Referencias del paquete

- [architecture-decision](references/architecture-decision.md): comparación de alternativas, criterios y reglas de decisión. Léela en la fase 3 y cuando haya que justificar una opción.
- [domain-boundaries](references/domain-boundaries.md): señales de diagnóstico, criterios de límite y mecanismos de control. Léela en las fases 1, 2 y 5.
- [integration-patterns](references/integration-patterns.md): composición build-time, por rutas, en servidor, Web Components, iframes, runtime y single-spa. Léela antes de describir o elegir una tecnología de composición.
- [contracts-and-lifecycle](references/contracts-and-lifecycle.md): contrato shell-módulo, ciclo de vida, dependencias compartidas y confianza. Léela en la fase 5.
- [deployment-and-rollback](references/deployment-and-rollback.md): artefactos, versiones, fallos de carga, rollback y observabilidad. Léela en la fase 5 y en la verificación.
- [acceptance-cases](references/acceptance-cases.md): desenlaces esperados de ocho escenarios típicos. Léela cuando el encargo se parezca a uno de ellos.
- [research-sources](references/research-sources.md): fuentes técnicas y qué capacidad fundamenta cada una. Léela si necesitas justificar una afirmación técnica o comprobar vigencia.
- [architecture-assessment](assets/architecture-assessment.md): plantilla de diagnóstico. Cópiala en la fase 1.
- [decision-record](assets/decision-record.md): plantilla de decisión trazable. Cópiala en la fase 4.
- [migration-checklist](assets/migration-checklist.md): migración incremental paso a paso. Cópiala solo si la migración está justificada.

## Fuera de alcance

No decidas colores, tipografía, composición visual ni accesibilidad visual: pertenece a `web-interface-visual-design` y `design-system-architect`. No elijas framework ni sustituyas las reglas idiomáticas del lenguaje. No diseñes backend, microservicios, API ni infraestructura de datos. No estimes tareas de producto ni redactes un PRD. Si el encargo cruza esos límites, sepáralos y remite a la skill correspondiente.

## Errores y paradas

- Si el usuario pide microfrontends sin describir un problema, entrega el diagnóstico y la comparación; no ejecutes la migración.
- Si los datos de bloqueo o coordinación no existen, entrega un diagnóstico provisional con la evidencia que falta. No los inventes.
- Si una fuente técnica no se puede comprobar en la versión usada por el proyecto, no le atribuyas comportamiento por defecto; declara la limitación y verifica la API.
- Si el encargo autoriza auditar y además pide cambios, separa las dos entregas y no modifiques nada hasta que la implementación esté autorizada por escrito.
- Si la recomendación exige un cambio organizativo que nadie ha aprobado, descríbelo como dependencia, no como decisión tomada.
