# Diagnóstico y límites de dominio

Este fichero desarrolla las fases 1, 2 y 5 del `SKILL.md`: qué evidencia recoger, cómo diagnosticar y cómo proponer límites que se puedan sostener.

## Diagnóstico: qué buscar

### Estructura y dependencias

- Imports que cruzan carpetas de dominio sin pasar por un punto de entrada.
- Accesos a implementaciones internas: rutas profundas, símbolos no exportados, estado global o utilidades privadas.
- Dependencias circulares o cadenas de import largas que aparecen en revisiones.
- Código compartido sin dueño: utilidades, tipos, estilos y constantes que todos modifican.
- Diferencias entre la arquitectura documentada y los imports reales.

### Responsabilidades y cambios

- Módulos que contienen reglas de varios dominios de negocio.
- Archivos de dominios distintos que cambian en el mismo commit con frecuencia.
- Carpetas cuyos cambios siempre requieren cambios en otra carpeta.
- Personas o equipos que necesitan aprobar cambios de otro equipo para publicar.
- Reuniones o esperas de coordinación con coste medido.

### Entrega

- Procesos de build: uno o varios, compartidos o por artefacto.
- Pipelines y cadenas de publicación: ¿publicar un área obliga a reconstruir el resto?
- Cadencia de release por área y acoplamiento de fechas.
- Bloqueos reales: releases detenidas por un dominio, esperas registradas, ventanas perdidas.
- Rollbacks: quién puede revertir qué, cuánto tarda y con qué efecto sobre otras áreas.
- Entornos y configuración: ¿puede desplegarse una versión distinta por entorno y por módulo?

### Autonomía

- Propiedad del código y de la decisión técnica por dominio.
- Dependencia de un equipo central para cambios locales.
- Capacidad de un equipo para probar y publicar sin coordinar una ventana común.

## Clasificación de la evidencia

Registra cada hallazgo con una de estas etiquetas:

- **Hecho.** Observado de forma reproducible: ruta y línea, comando con su salida, métrica con su fuente, decisión registrada o declaración atribuida a una persona identificada.
- **Inferencia.** Conclusión derivada de hechos. Escribe qué hechos la sostienen y qué la debilitaría.
- **Desconocido.** Dato que falta. Escribe qué dato es, quién puede aportarlo y cómo se obtendría.

Una carpeta compartida no es un hecho de acoplamiento: es una señal que exige comprobar quién la modifica y con qué frecuencia. Un pipeline compartido no es un hecho de bloqueo: es una condición que exige medir esperas.

## Evidencia insuficiente

Si no hay datos de bloqueos, esperas, frecuencia de cambios conjuntos ni coste de coordinación:

1. No concluyas que hace falta migrar.
2. Entrega un diagnóstico provisional con lo observado y una lista concreta de datos que faltan.
3. Propón la medición mínima: por ejemplo, registrar durante un periodo las releases bloqueadas por otro dominio, el tiempo de espera y los cambios que exigieron tocar dos áreas.
4. Mantén la recomendación como `Propuesta` y limita la implementación a mejoras de límites internos que no dependan de la decisión pendiente.

Una migración justificada por una intuición es un coste permanente comprado con una hipótesis.

## Candidatos a límite

Un límite es un candidato cuando cumple varios de estos criterios, no uno solo:

- **Cohesión funcional.** El candidato resuelve una responsabilidad de negocio reconocible por sus usuarios o por el negocio.
- **Responsabilidad de negocio.** Su vocabulario, sus reglas y sus decisiones pertenecen a un dominio identificable.
- **Propiedad de datos.** Es dueño de los datos que muestra y de las reglas que los transforman; no depende de que otro módulo le preste su estado.
- **Cambios conjuntos.** Los archivos del candidato cambian juntos y rara vez obligan a cambiar otros.
- **Dependencias externas.** Tiene un conjunto acotado de dependencias hacia fuera y una interfaz pública pequeña.
- **Interfaz pública.** Se puede describir con pocas operaciones, entradas y salidas estables.
- **Prueba independiente.** Se puede probar sin levantar el resto del sistema, o con un sustituto explícito del resto.
- **Ritmo propio.** Su cadencia de cambio o de release difiere de la del resto, o se espera que difiera.

No dividas por componentes visuales pequeños —botones, tablas, formularios— ni por capas técnicas —servicios, hooks, estilos—. Eso produce fronteras que cambian siempre juntas.

## Antipatrones de límite

- **Límite por equipo sin dominio.** Si dos equipos comparten la misma responsabilidad de negocio, la frontera reproduce el acoplamiento.
- **Límite por pantalla.** Una pantalla suele componer varios dominios; partirla por píxeles crea contratos cambiantes.
- **Límite por framework.** Carpetas `components/`, `services/` o `utils/` no son dominios.
- **Límite que necesita el estado de otro.** Un módulo que no puede funcionar sin el estado interno de otro no es independiente.
- **Límite sin dueño.** Un módulo sin responsable claro se convierte en código compartido de todos.

## Control de límites

Reutiliza lo que el proyecto ya tenga. No añadas una herramienta nueva si existe una regla equivalente.

| Mecanismo | Qué impide | Cuándo usarlo |
|---|---|---|
| Regla de lint de dependencias | Imports entre límites no declarados | Proyectos con ESLint y arquitectura por capas o dominios |
| `exports` del paquete | Importar rutas internas | Paquetes o workspaces con `package.json` |
| Project references o rutas tipadas | Dependencias no declaradas entre proyectos | TypeScript con varios proyectos |
| Análisis de dependencias en CI | Ciclos y dependencias prohibidas | Repositorios con CI ya existente |
| CODEOWNERS y revisión por propietario | Cambios sin responsable | Equipos con propiedad definida |
| Grafo de build | Builds que arrastran áreas ajenas | Pipelines con caché o construcción incremental |

La regla debe fallar de forma determinista: si el proyecto ya ejecuta lint o un análisis en CI, el límite se comprueba allí. Si no hay ninguna herramienta, propón la más pequeña disponible en el stack y documenta su coste.

## Salida del diagnóstico

Cada límite propuesto lleva:

- nombre y responsabilidad de negocio;
- datos que posee;
- interfaz pública mínima;
- dependencias permitidas y prohibidas;
- mecanismo de control y dónde se ejecuta;
- pruebas que lo cubren;
- dueño y condiciones de revisión.

Si un límite no puede describirse así, todavía no está listo para convertirse en frontera de despliegue.
