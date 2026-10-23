# Informe de auditoría documental

Rellena esta plantilla para una auditoría o cuando queden hallazgos sin resolver. Ordena los hallazgos por impacto.

## Alcance revisado

- Ruta o área: <rutas relativas>
- Artefactos revisados: <n>
- Fuentes contrastadas: <código, tests, configuración, decisiones>
- Fuera de alcance: <lo que no se pudo revisar y por qué>

## Veredicto

| Clase | Valor | Evidencia |
|---|---|---|
| Cobertura de la responsabilidad | <CUBIERTA \| PARCIAL \| AUSENTE> | <artefactos que la cubren> |
| Correspondencia con el software | <CONFIRMADA \| DIVERGENTE \| NO VERIFICABLE> | <fuentes contrastadas> |
| Consistencia interna | <CONSISTENTE \| CONTRADICTORIA> | <contradicciones encontradas> |
| Vigencia | <VIGENTE \| OBSOLETA \| HISTÓRICA> | <documentos afectados> |

## Hallazgos

| # | Impacto | Tipo | Ubicación | Hallazgo | Acción propuesta |
|---|---|---|---|---|---|
| 1 | <alto \| medio \| bajo> | <sin soporte \| obsoleto \| contradictorio \| ausente \| duplicado \| sin responsabilidad \| enlace roto \| terminología> | <ruta:línea o sección> | <qué está mal, en una frase verificable> | <corrección mínima> |

Impacto alto: induce a error en implementación, operación o seguridad, o destruye conocimiento único.
Impacto medio: obliga a reconstruir conocimiento o a reabrir una decisión ya tomada.
Impacto bajo: fricción de lectura o inconsistencia de forma.

## Comprobaciones ejecutadas

| Comprobación | Comando o método | Resultado |
|---|---|---|
| Inventario y hallazgos deterministas | `python3 scripts/doc-inventory.py --root <ruta>` | <código de salida y resumen> |
| Contraste por afirmación | <método> | <cuántas confirmadas, cuántas no verificables> |
| Revisión de contenido eliminado | <método> | <conocimiento preservado o perdido> |

## Pendiente

| Qué falta | Qué lo desbloquea | Bloquea a |
|---|---|---|
| <fuente o decisión ausente> | <pregunta exacta o acción concreta> | <artefacto o afirmación> |
