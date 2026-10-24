# Auditoría y verificación de cierre

Léelo en el paso 6 del procedimiento. La auditoría es de solo lectura: no modifica artefactos sin un encargo explícito.

## Auditoría de solo lectura

Recorre el inventario y busca, por orden de impacto:

1. Afirmaciones sin soporte verificable.
2. Documentación obsoleta que contradice el estado implementado.
3. Contradicciones entre fuentes con la misma responsabilidad.
4. Conocimiento importante ausente: lo que se reconstruye cada vez.
5. Duplicación: el mismo dato en dos documentos sin referencia.
6. Documentos sin responsabilidad clara o con responsabilidad solapada.
7. Mezcla de intención, implementación y propuesta sin señalarlo.
8. Enlaces relativos rotos y referencias a rutas inexistentes.
9. Instrucciones imposibles de ejecutar o de verificar.
10. Contexto decisional perdido en decisiones que se reabren.
11. Estado de la propia entrega escrito como documentación: sus ramas, commits, hashes, «se corrigió», «quedó reportado». Git y el registro de trabajo ya lo contienen. La fijación de un tercero (origen y commit de una copia vendida) no entra aquí: es su contrato de reproducibilidad.

Prioriza por impacto sobre comprensión, implementación, operación y mantenimiento. El estilo solo cuenta si impide entender o ejecutar.

## Veredicto por clase de afirmación

No uses un veredicto global. Informa por separado:

| Clase | Valores |
|---|---|
| Cobertura de la responsabilidad | CUBIERTA \| PARCIAL \| AUSENTE |
| Correspondencia con el software | CONFIRMADA \| DIVERGENTE \| NO VERIFICABLE |
| Consistencia interna | CONSISTENTE \| CONTRADICTORIA |
| Vigencia | VIGENTE \| OBSOLETA \| HISTÓRICA |

Una falta de verificación no es un incumplimiento: es un límite del alcance, y se declara como tal.

## Verificación de cierre documental

Antes de declarar terminada una intervención, comprueba y muestra:

1. `python3 scripts/doc-inventory.py --root <ruta>` ejecutado después del cambio, con su código de salida. Incluye la clase de estado de la entrega; la comprobación 8 no se puede sustituir por un autoinforme.
2. Que no haya enlaces relativos nuevos rotos.
3. Que no haya encabezados duplicados nuevos entre documentos, salvo duplicación deliberada y justificada.
4. Que cada afirmación modificada esté sustentada en una fuente identificable.
5. Que el contenido eliminado no fuera la única representación de un conocimiento válido.
6. Que la terminología nueva coincida con la que ya usa el proyecto.
7. Que los comandos, rutas y valores citados existan en el estado actual.
8. Que el documento no conserve estado de la propia entrega que ya vive en Git o en el registro de trabajo: referencias a sus commits y ramas, hashes de sus artefactos, narración de correcciones y reentregas. La fijación de un tercero se conserva: es un contrato de reproducibilidad, no historia de la entrega.

Si falla cualquiera de estas comprobaciones, el resultado es INCOMPLETO o NO VERIFICADO, nunca "terminado". Explica qué condición falta.

## Formato del informe

Cuando el encargo sea una auditoría, o cuando queden hallazgos sin resolver, rellena `assets/audit-report-template.md`. Ordena los hallazgos por impacto y no por orden de aparición en el árbol de archivos.

## Falsos positivos conocidos

- Un encabezado repetido puede ser correcto cuando dos documentos cubren la misma sección con audiencias distintas; decídelo explícitamente, no lo ignores.
- El inventario determinista omite los bloques de código, las citas entre comillas anguladas (el ejemplo que la propia regla enumera) y los documentos con un encabezado H2 llamado `Log`, que son registro de trabajo y no documentación de usuario. Un tercero fijado a un commit tampoco es hallazgo: se busca la narración, no el hash.
- Un enlace a una ruta generada puede no existir antes de compilar; verifica si el repositorio documenta ese paso de generación.
- Una afirmación sin fuente puede ser una decisión del usuario no registrada: pregunta antes de borrarla.
