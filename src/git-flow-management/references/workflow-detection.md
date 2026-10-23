# Detección de política de ramas

Usa esta referencia tras la inspección de solo lectura y antes de cualquier operación persistente en un repositorio existente.

## Jerarquía de evidencia

Clasifica por la evidencia más fuerte disponible:

1. Documentación que declara una política operativa o su precedencia.
2. Ramas remotas activas, protecciones conocidas y mecanismos de revisión.
3. Historial de integración y relaciones entre ramas.
4. Ramas locales y convenciones de nombre.

Que exista un documento no prueba que el flujo se haya ejecutado correctamente. Que exista una rama llamada develop tampoco prueba Git Flow.

## Clasificación

| Evidencia observada | Clasificación | Respuesta |
|---|---|---|
| Documento de Git Flow aplicable, pero solo main y develop en el mismo commit inicial | Git Flow documentado, pendiente de evidencia | Aplica la política desde el siguiente trabajo; no declares práctica demostrada. |
| Main/master, develop y evidencia repetida de feature, release o hotfix integradas | Git Flow existente y evidenciado | Sigue nombres, destinos y reglas observadas. |
| Main/master y ramas cortas integradas directamente a ella | Flujo distinto | Presérvalo; no crees develop. |
| Versiones de mantenimiento prolongadas | Flujo de ramas de release | Respeta sus reglas y pide aclaración antes de cambios cruzados. |
| Evidencia contradictoria o sin política | Desconocido | Expón hechos y pide decisión antes de actuar. |

## Regla de adaptación

En un repositorio existente, una guía explícita puede obligar el siguiente trabajo aunque la historia no haya proporcionado aún una prueba operativa. No migres ni inventes infraestructura adicional por ello.

Para una política documental sobria:

- no añadas Issues, PR obligatorias, SemVer, remoto o reglas de merge si el documento no los exige;
- usa el patrón de nombre especificado por el documento;
- no conviertas la ausencia de remoto en incumplimiento del flujo local;
- distingue siempre política declarada, estructura presente y uso demostrado.
