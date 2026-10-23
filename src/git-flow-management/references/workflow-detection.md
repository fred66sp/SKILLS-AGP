# Detección de política de ramas

Usa esta referencia tras la inspección de solo lectura y antes de cualquier operación persistente en un repositorio existente.

## Jerarquía de evidencia

Clasifica por la evidencia más fuerte disponible:

1. Documentación que declara una política operativa o su precedencia.
2. Ramas remotas activas, protecciones conocidas y mecanismos de revisión.
3. Historial de integración y relaciones entre ramas.
4. Ramas locales y convenciones de nombre.

Que exista un documento no prueba que el flujo se haya ejecutado correctamente. Que exista una rama llamada `develop` tampoco prueba Git Flow.

## Clasificación

| Evidencia observada | Clasificación | Respuesta |
|---|---|---|
| Sin política declarada y con `main` como única rama de larga vida | Modelo por defecto | Aplica la proporcionalidad: rama solo cuando la tarea no es pequeña. |
| `main` estable con ramas cortas integradas directamente a ella | Modelo por defecto, ya en uso | Consérvalo; no crees `develop`. |
| Documento que declara Git Flow o `develop` como rama de integración | Git Flow declarado | Respeta su tabla de bases y destinos desde el siguiente trabajo. |
| Documento de Git Flow aplicable, pero solo `main` y `develop` en el mismo commit inicial | Git Flow documentado, pendiente de evidencia | Sigue la política; no declares práctica demostrada. |
| Evidencia repetida de feature, release o hotfix integradas con `develop` | Git Flow existente y evidenciado | Sigue nombres, destinos y reglas observadas. |
| Versiones de mantenimiento prolongadas | Flujo de ramas de release | Respeta sus reglas y pide aclaración antes de cambios cruzados. |
| Evidencia contradictoria o sin política | Desconocido | Expón hechos y pide decisión antes de actuar. |

## Regla de adaptación

Una guía explícita del repositorio puede obligar el siguiente trabajo aunque la historia no haya proporcionado aún una prueba operativa. No migres ni inventes infraestructura adicional por ello.

Para una política documental sobria:

- no añadas Issues, PR obligatorias, SemVer, remoto o reglas de merge si el documento no los exige;
- usa el patrón de nombre especificado por el documento;
- no conviertas la ausencia de remoto en incumplimiento del flujo local;
- distingue siempre política declarada, estructura presente y uso demostrado.

## Proporcionalidad frente a política

La proporcionalidad decide cuánta ceremonia aplicas, no qué modelo de ramas usas. Si el repositorio declara ramas de trabajo obligatorias, una tarea pequeña no autoriza a saltárselas. Si no declara nada, una tarea pequeña no obliga a abrir rama.
