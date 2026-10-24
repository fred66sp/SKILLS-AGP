# Plan de intervención documental

Rellena esta plantilla cuando el encargo afecte a más de un documento o cuando crear o eliminar no sea evidente. Sustituye cada campo con contenido concreto; no dejes marcadores.

## Encargo

- Operación: <crear | actualizar | auditar | responder>
- Audiencia y uso previsto: <quién lo lee y para qué decide o ejecuta>
- Alcance: <rutas o áreas cubiertas>
- Fuera de alcance: <lo que se deja explícitamente fuera>

## Estado actual

| Responsabilidad | Artefacto existente | Estado | Evidencia |
|---|---|---|---|
| <pregunta que responde> | <ruta relativa> | <vigente \| obsoleto \| parcial \| ausente> | <fuente que lo sostiene> |

Inventario determinista: `python3 scripts/doc-inventory.py --root <ruta>` → código de salida <0 \| 3>, <n> hallazgos.

## Intervención propuesta

| # | Artefacto | Acción | Motivo | Riesgo |
|---|---|---|---|---|
| 1 | <ruta relativa> | <ninguna \| corregir \| actualizar \| consolidar \| crear \| eliminar> | <qué problema resuelve> | <qué puede salir mal> |

Justificación de la creación o eliminación: <por qué el conocimiento no cabe en un artefacto existente o por qué deja de merecer uno propio>

## Afirmaciones que requieren decisión

| Afirmación | Grado de certeza | Fuente | Qué falta |
|---|---|---|---|
| <afirmación> | <confirmada \| inferencia \| propuesta \| desconocida \| contradictoria \| obsoleta> | <ruta o decisión> | <pregunta exacta> |

## Verificación prevista

- Inventario repetido tras el cambio: sí
- Referencias vivas (rutas de máquina, remoto, recuentos de artefactos) fuera del texto: sí
- Enlaces relativos comprobados: sí
- Contraste contra fuente por afirmación modificada: sí
- Revisión de contenido eliminado: sí
