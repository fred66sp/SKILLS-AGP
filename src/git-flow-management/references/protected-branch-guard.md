# Guardia de ramas protegidas

Usa esta referencia siempre que la rama actual sea main o develop.

## Decisión obligatoria

| Rama actual | Operación solicitada | Resultado |
|---|---|---|
| main | Trabajo normal, corrección, documentación o commit | BLOQUEAR; proponer hotfix si es producción o la rama correcta según política. |
| develop | Trabajo normal, corrección, documentación o commit | BLOQUEAR; proponer feature o fix desde develop. |
| main | Integrar release o hotfix | Permitir solo tras verificar origen, destino y plan aprobado. |
| develop | Integrar feature, fix, release o hotfix | Permitir solo tras verificar origen, destino y plan aprobado. |

## Comprobación previa

1. Identifica la rama actual.
2. Clasifica la operación como trabajo o integración.
3. Si es trabajo sobre una rama protegida, no prepares archivos ni propongas un commit.
4. Propón crear la rama permitida desde la base obligatoria y solicita una confirmación para ese plan.
5. Tras crearla, verifica rama actual y relación con su base antes de continuar.

## Evidencia de integración

Una integración hacia una rama protegida debe identificar:

- origen y destino permitidos;
- commits incluidos;
- mecanismo de revisión si existe;
- estrategia de merge;
- comprobación posterior de que el resultado está contenido en el destino.
