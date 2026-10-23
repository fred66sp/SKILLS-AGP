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

1. `python3 scripts/doc-inventory.py --root <ruta>` ejecutado después del cambio, con su código de salida.
2. Que no haya enlaces relativos nuevos rotos.
3. Que no haya encabezados duplicados nuevos entre documentos, salvo duplicación deliberada y justificada.
4. Que cada afirmación modificada esté sustentada en una fuente identificable.
5. Que el contenido eliminado no fuera la única representación de un conocimiento válido.
6. Que la terminología nueva coincida con la que ya usa el proyecto.
7. Que los comandos, rutas y valores citados existan en el estado actual.

Si falla cualquiera de estas comprobaciones, el resultado es INCOMPLETO o NO VERIFICADO, nunca "terminado". Explica qué condición falta.

## Formato del informe

Cuando el encargo sea una auditoría, o cuando queden hallazgos sin resolver, rellena `assets/audit-report-template.md`. Ordena los hallazgos por impacto y no por orden de aparición en el árbol de archivos.

## Falsos positivos conocidos

- Un encabezado repetido puede ser correcto cuando dos documentos cubren la misma sección con audiencias distintas; decídelo explícitamente, no lo ignores.
- Un enlace a una ruta generada puede no existir antes de compilar; verifica si el repositorio documenta ese paso de generación.
- Una afirmación sin fuente puede ser una decisión del usuario no registrada: pregunta antes de borrarla.
