# Gobernanza del sistema visual

Un sistema deja de serlo cuando cada tarea puede cambiar sus decisiones sin dejar rastro. Esta referencia fija quién puede cambiar qué, cómo se demuestra una aprobación y qué límites tiene esa demostración.

## El flujo

```text
READ → PROPOSE → APPROVE → APPLY → VERIFY
```

| Paso | Qué produce | Qué no permite |
|---|---|---|
| READ | Contrato —documentado o JSON—, implementación viva, catálogo existente, fuentes, artefactos y evidencias leídos | Proponer sin haber leído el producto y el catálogo, no solo el contrato |
| PROPOSE | Cambio con ruta, antes, después, motivo, impacto y clase | Aplicar durante la propuesta |
| APPROVE | Confirmación de la persona o, en modo `approvals`, aprobación externa registrada | Que el agente se apruebe a sí mismo |
| APPLY | Cambio solo en las rutas autorizadas | Cambiar el contrato para tapar un incumplimiento |
| VERIFY | `check` o `gate` con su resultado | Declarar `PASS` lo que no se ejecutó |

## Dos regímenes de gobernanza

`governance.mode` decide cuánta ceremonia exige el proyecto:

| Modo | Cuándo | Qué exige un cambio protegido |
|---|---|---|
| `solo` (por defecto) | Una persona revisa y commitea | El commit y su confirmación. Sin archivo de aprobaciones. El `gate` devuelve `UNKNOWN`, porque no puede comprobar esa confirmación |
| `approvals` | Varias personas o un sistema externo revisan | Una aprobación externa con `id`, `path`, alcance y `source` |

En los dos, el agente no puede aprobarse a sí mismo ni crear el registro de aprobación que lo cubre. La diferencia es que en `solo` ese registro no existe: inventarlo añade un archivo que nadie mantiene y una prueba de forma que no demuestra nada. Un proyecto solo con revisión por commit no necesita `approvals`.

## Qué está protegido

| Categoría | Significado | Efecto |
|---|---|---|
| Protegido (`governance.protected`) | Identidad, tokens consolidados, contratos de componentes estables | Cambiar, añadir o eliminar exige revisión; en modo `approvals`, aprobación externa |
| Configurable (`governance.configurable`) | Valores pensados para adaptarse por proyecto o densidad | Se puede cambiar dentro del contrato sin aprobación, con evidencia |
| Excepción (`governance.exceptions`) | Desviación declarada, con motivo y responsable | No convierte un `FAIL` en `PASS`; documenta una decisión aceptada |

Una ruta protegida puede ser exacta (`tokens.color.brand`) o un prefijo con comodín final (`tokens.color.*`, `identity.*`). Una ruta exacta cubre también sus descendientes: proteger `tokens.color.brand` protege el valor y sus componentes internos.

Una ruta protegida que no coincide con nada en el contrato ni en el baseline es una promesa vacía. Se corrige antes de confiar en la puerta.

## Clases de cambio

| Cambio | Clase | Qué exige |
|---|---|---|
| Añadir un token, un componente o un patrón no protegido | Compatible | `check` y, si hay catálogo, regenerarlo |
| Corregir una descripción, un ejemplo o una errata | Compatible | `check` |
| Cambiar el valor de un token protegido | Requiere aprobación | `gate` con baseline y aprobación externa |
| Renombrar o eliminar un token o una variante pública | Requiere aprobación | Aprobación y plan de migración |
| Cambiar la política de accesibilidad, movimiento o identidad | Requiere aprobación | Aprobación explícita y actualización del contrato |
| Deprecar un token o un componente | Requiere aprobación | Motivo, sustituto y ventana de migración |

La versión del contrato sigue SemVer: `MAJOR` para un cambio incompatible (renombrar o eliminar algo que los consumidores usan), `MINOR` para una adición compatible y `PATCH` para una corrección que no cambia el contrato. La versión de la skill es independiente.

## Aprobaciones externas

Solo se usan con `governance.mode: approvals`. El agente **no puede crear ni modificar** el archivo de aprobaciones. Lo aporta la persona o un sistema externo; el agente solo lo lee y lo cita. Si el agente tiene permiso de escritura sobre ese archivo, la garantía es procedural, no criptográfica: Git y la revisión humana son el control real.

### Formato

```json
{
  "schema": "design-system.approvals.v1",
  "approvals": [
    {
      "id": "APR-2026-014",
      "path": "tokens.color.brand",
      "approved_by": "Ana",
      "approved_at": "2026-10-30",
      "source": "confirmación en la sesión de revisión, 30/10",
      "reason": "El acento cambia de tono sin cambiar de significado."
    }
  ]
}
```

Campos obligatorios: `id`, `path`, `approved_by`, `approved_at` (AAAA-MM-DD), `source` y `reason`. `approved_by` por sí solo no autoriza nada.

### Qué comprueba el validador

- Que el archivo declara el esquema esperado.
- Que cada entrada tiene todos los campos y una fecha válida.
- Que el `path` de la aprobación cubre cada ruta protegida que cambió.
- Que no hay cambios protegidos sin una aprobación que los cubra.

### Qué no comprueba

- **No autentica** la identidad de `approved_by`.
- No demuestra que la aprobación venga de fuera del agente.
- No verifica que el `source` exista.
- No impide que alguien con escritura forje el archivo.

Por eso una aprobación ausente, incompleta o dudosa devuelve `UNKNOWN` o `FAIL`, nunca `PASS`. La firma, el ticket o el correo son la fuente real cuando el proyecto los exige; el archivo solo hace explícito su alcance.

## Aplicar el cambio

1. Comprueba que la aprobación cubre exactamente las rutas que cambian.
2. Edita solo esas rutas. Si aparece una ruta adicional, se detiene y se propone.
3. Si el catálogo es `generated`, regenéralo. Si es `external`, no lo regeneres: comprueba que sigue importando la implementación y que sus muestras usan clases existentes. No edites el HTML, el CSS ni el manifiesto generados a mano.
4. Ejecuta `gate` con el mismo baseline y la misma aprobación. Guarda la salida.
5. Si el resultado es `FAIL`, corrige la implementación o vuelve a proponer. No cambies el contrato para que el resultado pase.
6. Si el resultado es `UNKNOWN`, falta evidencia: baseline, catálogo, informe o aprobación. No lo presentes como cierre.

## Excepciones autorizadas

Una excepción no es un permiso para saltarse la puerta. Es una desviación declarada:

```json
{
  "path": "components.data-table.variants.compact.padding",
  "reason": "La tabla compacta necesita más densidad que la escala general.",
  "approved_by": "Ana",
  "approval": "APR-2026-018"
}
```

El validador no convierte un `FAIL` de conformidad en `PASS` por una excepción. Si el adaptador demuestra un incumplimiento, el resultado sigue siendo `FAIL`; la excepción explica por qué el sistema lo acepta, no lo oculta. La decisión de aceptar el riesgo es de la persona.

## Orden de actualización

Cuando un cambio aprobado toca contrato y artefactos:

1. Contrato y fuentes de tokens.
2. Catálogo generado.
3. Informes de adaptadores, si existen.
4. Evidencia de la puerta.

El orden inverso produce un catálogo que describe un sistema que ya no existe. `check` lo detecta comparando las huellas de las entradas y de los artefactos.

## Decisiones durables

Una decisión que cambia la forma del sistema se registra en `decisions` con su `id`, su decisión y su razón. El historial de Git guarda el cambio; el contrato guarda la decisión vigente. No se mantiene una cola de propuestas dentro del contrato ni un changelog paralelo.

## Paradas

- **Sin aprobación:** no se aplica el cambio protegido. Se devuelve la propuesta y se espera.
- **Sin confirmación en modo `solo`:** no se declara el cambio cerrado. La revisión y el commit son la evidencia; el `gate` devuelve `UNKNOWN` y no se fabrica un archivo de aprobaciones para convertirlo en `PASS`.
- **Aprobación incompleta:** se devuelve `UNKNOWN` con el campo que falta.
- **Aprobación que no cubre la ruta:** se devuelve `FAIL` con la ruta no cubierta.
- **Conflicto entre contrato y producto:** se detiene la implementación y se expone la divergencia. No se «arregla» el contrato a conveniencia.
- **Cambio de alcance:** se propone una aprobación nueva; no se reutiliza una anterior.
