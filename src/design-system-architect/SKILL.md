---
name: design-system-architect
description: "Define, descubre, documenta, gobierna y verifica sistemas de diseño: identidad, tokens DTCG, temas, contratos de componentes, patrones, accesibilidad, movimiento y catálogo. Parte de la implementación y del catálogo que ya existen; un contrato documentado (DESIGN.md, ADR) vale tanto como un JSON. Se activa al crear un sistema visual, auditar uno existente, proponer su evolución, generar tokens o contratos, publicar un catálogo o comprobar que una implementación respeta el sistema aprobado. No se usa para construir pantallas, componentes o recursos gráficos —eso pertenece al contrato de diseño visual de interfaces—, ni para sustituir arquitectura, lógica, seguridad o pruebas funcionales. No inventa un sistema nuevo cuando ya existe uno que debe conservarse."
metadata:
  version: "0.2.0"
---

# Arquitectura y gobierno del sistema de diseño

Un sistema de diseño no es una colección de colores: es un contrato que permite decidir, implementar y verificar sin volver a discutir cada pantalla. Este contrato posee la identidad, los tokens, los componentes y la gobernanza; la interfaz los consume.

**Principio fundamental:** un agente puede diseñar e implementar dentro del sistema, pero no puede modificar sus decisiones consolidadas sin autorización explícita. Tampoco puede editar el contrato para justificar una implementación que lo incumple.

## Punto de partida

El orden manda, y es este:

1. **La implementación viva.** El CSS, los componentes y los valores que el producto ya usa son la evidencia primaria. Se leen primero.
2. **El catálogo que ya existe.** Si hay uno escrito a mano, se conserva y se verifica su acoplamiento. No se reescribe para que se parezca a un contrato.
3. **El contrato documentado.** Un `DESIGN.md`, un ADR o una guía con tokens y reglas es el contrato. Se lee como fuente canónica.
4. **El contrato máquina-legible.** `design-system.json` es opcional y solo se crea cuando habilita algo que el documento no da: aprobaciones con alcance, consumidores, generación o puerta. Si no habilita nada, no se crea.

Empezar por el artefacto que la skill sabe producir —el JSON, el catálogo generado, la puerta— y no por lo que el producto tiene es el error que hace dar vueltas. Un sistema que ya funciona no necesita un segundo formato para demostrarlo.

## Responsabilidad y límites

- Posee la identidad visual, los principios, los tokens, los temas, los contratos de componentes, los patrones, las reglas de accesibilidad y movimiento, las decisiones y su evolución.
- Posee la gobernanza: qué está protegido, qué es configurable, qué excepción está autorizada y qué cambio exige aprobación.
- Posee el catálogo como artefacto generado **o declara el externo que ya existe** y verifica que consume la implementación. Posee la puerta determinista `scripts/design_system.py`.
- **Handoff visual:** define el sistema y entrega la fuente con su control. La composición y el juicio visual final no son de esta skill; cuando el encargo es «que quede impecable», entrega el catálogo acoplado y la evidencia, y no sigue iterando el catálogo hasta que la persona lo rechaza.
- No posee la composición, la implementación de pantallas, los recursos gráficos ni el juicio visual final. Eso pertenece al contrato de diseño visual de interfaces; aquí se define el sistema que esa ejecución debe respetar.
- No es un framework de componentes, un generador de aplicaciones ni una biblioteca de UI. No impone un stack: describe valores y reglas que se aplican al stack presente.
- No posee la accesibilidad completa. Comprueba estructura y declara `UNKNOWN` lo que exige navegador, medición o inspección humana.
- No inventa datos, marcas ni derechos de uso. Lo desconocido se declara; no se rellena con una decisión no autorizada.

## Precedencia

1. La instrucción explícita de la persona para la tarea.
2. La implementación viva y el contrato documentado del proyecto (`DESIGN.md`, un ADR).
3. El contrato máquina-legible (`design-system.json`) y sus fuentes de tokens.
4. Este contrato para descubrir, definir, cambiar o verificar el sistema.
5. El contrato de diseño visual de interfaces para materializar y revisar la ejecución.
6. Los valores por defecto del modelo.

Un contrato existente y bloqueado gana sobre cualquier preferencia estética. Si la tarea exige cambiarlo, se detiene la implementación y se sigue el flujo de gobernanza.

## Modos de trabajo

| Modo | Cuándo | Resultado que cierra |
|---|---|---|
| Descubrir | Hay un producto o un sistema visual existente | Fuentes, tokens, duplicados, componentes y convenciones clasificados como observados, documentados, inferidos o desconocidos |
| Definir | No hay sistema, o la persona autoriza uno nuevo | Contrato mínimo coherente, con identidad, tokens, componentes y gobernanza |
| Auditar | Hay dudas sobre deriva, duplicidad o incumplimiento | Hallazgos con evidencia, sin sobrescribir el sistema |
| Auditar acoplamiento | Hay un catálogo y una implementación; se duda de que el catálogo los una | Informe de fidelidad: clases, importaciones, huellas y `implementation-fidelity`, sin reescribir el catálogo |
| Rehacer catálogo | La persona rechaza el catálogo por fidelidad | Catálogo reconstruido desde la implementación: importa su CSS y usa sus clases |
| Evolucionar | La persona autoriza un cambio | Propuesta, revisión o aprobación según `governance.mode`, aplicación y verificación |

**Dos rechazos por la misma causa cambian el enfoque, no el detalle.** Si la persona rechaza dos veces el catálogo por la misma razón —no se parece, no usa los componentes reales—, no se parchea una tercera vez: se reconstruye desde la implementación. Lo mismo con cualquier otra causa repetida. Un tercer parche de lo mismo es una decisión equivocada, no una iteración.


## Procedimiento

### 1. Descubrir antes de definir

1. Ejecuta `discover` sobre la raíz del proyecto. Es una operación de solo lectura: no escribe ni sobrescribe nada.
2. Lee primero la implementación (CSS, componentes) y el catálogo si existe. El contrato se lee después, como descripción de esos hechos.
3. Clasifica cada fuente:
   - **Observado:** un hecho leído del código o de los archivos (un token DTCG, una variable CSS, un componente).
   - **Documentado:** una decisión escrita en un documento del proyecto.
   - **Inferido:** una hipótesis que necesita confirmación; no se convierte en contrato sin ella.
   - **Desconocido:** una categoría sin evidencia; se declara y no se rellena.
4. Revisa el mapa `duplicates` antes de declarar tokens: el mismo valor en varios archivos suele ser una fuente, un artefacto generado y una copia. Separa las tres cosas. Cada archivo CSS lleva `role` (`source` o `generated`); un `brand-pack` en JSON sin `$value` es una fuente probable, no «no hay tokens».
5. Si existe un contrato o una fuente canónica de tokens, consérvala. No copies sus valores a otro sitio ni crees un sistema paralelo.
6. Si el proyecto ya tiene tokens en archivos DTCG, decláralos en `tokenSources`; no los dupliques dentro de `tokens`.
7. Lee [contract-model](references/contract-model.md) para la forma del contrato y el modelo de evidencia.

### 2. Decidir el soporte del contrato

1. Si existe un `DESIGN.md`, un ADR o una guía con los tokens y las reglas, ese es el contrato. No se reescribe ni se duplica.
2. Solo se escribe `design-system.json` si habilita algo que el documento no da: aprobaciones con alcance, consumidores que leen tokens con tipos, generación determinista o puerta contra un baseline. Declara en `sources` qué habilita; si no habilita nada, no lo crees.
3. No traduzcas el documento a JSON para después escribir una prueba de sincronía que tape lo que `check` no ve. Ese duplicado cuesta más y garantiza menos.

### 3. Proponer el contrato

1. Parte de `assets/design-system.template.json` solo si no hay contrato. Rellena identidad, tokens, temas, componentes, accesibilidad, restricciones y gobernanza.
2. Define tokens en tres niveles cuando el tamaño lo justifique: primitivos, semánticos y de componente. Cuando el contrato distingue esos niveles, los componentes consumen los dos últimos; los primitivos solo se usan con una excepción declarada. El validador comprueba la existencia y el tipo de la referencia, no la intención del nivel.
3. Declara cada componente con su propósito, `when`, `when_not`, variantes, estados y un `example` si existe. Una variante sin regla de uso no está especificada.
4. Declara los temas y sus overrides. El modo por defecto y cada modo deben apuntar a tokens existentes.
5. Declara `governance.mode` (`solo` o `approvals`) y, solo si de verdad se quieren, `governance.protected` y `governance.configurable`. Una ruta protegida sin coincidencias es una promesa vacía: corrígela.
6. Declara `implementation.styles` con el CSS real del producto cuando exista: es lo que permite comprobar que el catálogo y las muestras están acoplados.
7. Si el contrato declara un catálogo (`catalog`), declara su modo: `generated` si lo escribe la skill, `external` si ya existe y se mantiene a mano. En `external`, declara `path`, `entry` y `sources`.
8. Si el contrato declara adaptadores (`adapters`), declara también dónde viven sus informes.

### 4. Gobernar el cambio

Sigue `READ → PROPOSE → APPROVE → APPLY → VERIFY`:

1. **READ:** lee el contrato, la implementación, el catálogo existente, las fuentes y los artefactos. No propongas nada sin haberlos leído.
2. **PROPOSE:** escribe el cambio con ruta, valor anterior, valor propuesto, motivo, impacto y clase (compatible o requiere aprobación). Si la ruta está protegida, aplica el régimen de `governance.mode`.
3. **APPROVE:** en modo `solo`, la persona revisa y confirma en el commit; no hay archivo de aprobaciones. En modo `approvals`, la persona o un sistema externo aporta una aprobación. En ambos, el agente **no puede crear ni modificar** el registro que lo autoriza. `approved_by` por sí solo no autoriza nada: se exigen `id`, `path`, `approved_by`, `approved_at`, `source` y `reason`. El validador comprueba el alcance de la aprobación, no su autenticidad.
4. **APPLY:** aplica solo las rutas autorizadas. No cambies el contrato para que una implementación incumplidora parezca válida.
5. **VERIFY:** ejecuta `gate` contra el baseline y declara el resultado. Si no hay baseline o no hay aprobación comprobable, el resultado es `UNKNOWN`, no `PASS`.

Lee [governance](references/governance.md) antes de proponer un cambio protegido.

### 5. Documentar sin duplicar

1. **Primer corte vertical obligatorio.** Antes de generar o reconstruir el catálogo completo, entrega un componente real: importado de la implementación, con su CSS y sus clases, revisado por la persona. Solo después se generaliza. Un catálogo entero construido sobre una suposición se rechaza entero.
2. Si hay implementación viva, el catálogo importa su CSS y usa sus clases. El `iframe` es una opción para aislar `example`, no un requisito ni una excusa para redibujar componentes.
3. Elige el modo del catálogo:
   - **`generated`:** `catalog` escribe `index.html`, `tokens.css`, `catalog.css` y la entrada del manifiesto. Consume los mismos tokens que el producto; no crea una segunda paleta.
   - **`external`:** el catálogo ya existe y se mantiene a mano. No se le genera un `tokens.css` paralelo y no define clases de componente propias (`ds-*`): importa las del producto. `check` verifica su entrada, sus `sources` y su huella; `implementation-fidelity` verifica el acoplamiento.
4. Un catálogo que no puede importar la implementación se declara `inferred`: no se presenta como fiel ni se usa como evidencia.
5. El manifiesto del catálogo generado guarda las huellas del contrato, de cada fuente DTCG, de las plantillas y de cada artefacto. Cualquier cambio relevante lo invalida y `check` lo demuestra.
6. La composición y la revisión visual del catálogo no son de esta skill. Se entregan al contrato de calidad visual del proyecto, sin cambiar el contenido ni los tokens, y sin seguir iterando el catálogo después de esa entrega.

### 6. Verificar y cerrar

1. Ejecuta `check` sobre el contrato. Comprueba estructura, tokens, referencias, `catalog-consistency` e `implementation-fidelity`; si declara adaptadores, lee sus informes.
2. Ejecuta `gate` contra el baseline anterior cuando el cambio toque rutas protegidas.
3. La evidencia primaria del contrato es la prueba de acoplamiento: que el catálogo importa la implementación y usa sus clases. `check` solo demuestra coherencia del contrato consigo mismo.
4. Separa tres afirmaciones:
   - **Estructura:** el contrato, los tokens, las referencias y los componentes son coherentes.
   - **Visual:** la interfaz renderizada se parece al sistema. Requiere inspección; sin ella es `UNKNOWN`.
   - **Accesibilidad:** contraste, foco, teclado y reflow se miden en el render. Sin medición es `UNKNOWN`.
5. Un `PASS` estructural no demuestra calidad visual ni conformidad de accesibilidad. No lo presentes como si lo hiciera.
6. Cierra con la evidencia ejecutada, los `UNKNOWN` y sus motivos, y los cambios de contrato pendientes de aprobación.

## El contrato

`design-system.json` es un esquema propio (`design-system.v1`). Los tokens siguen un subconjunto declarado de DTCG 2025.10: `$value`, `$type`, grupos, herencia de tipo, alias con `{ruta}`, `$root` y `$deprecated`.

Un contrato documentado (`DESIGN.md`, un ADR) es de pleno derecho y no se duplica. `design-system.json` es opcional: se crea solo si habilita aprobaciones con alcance, consumidores, generación o puerta, y se justifica en [contract-model](references/contract-model.md).

No se afirma conformidad DTCG completa: no se implementan `$extends`, JSON Pointer, todos los tipos compuestos ni todas las reglas de la especificación. Los detalles y los límites están en [contract-model](references/contract-model.md).

Campos principales: `identity`, `tokens` o `tokenSources`, `themes`, `components`, `patterns`, `accessibility`, `constraints`, `decisions`, `governance`, `catalog`, `implementation`, `adapters`, `sources` y `omitted`.

## Comandos

Los scripts son un solo archivo sin dependencias. Para que la puerta exista en el proyecto y en su CI, cópialos a `tools/design-system/` del proyecto —o invócalos con su ruta absoluta desde el pipeline— y ejecútalos ahí. Una puerta que el CI del proyecto no puede ejecutar no es una puerta.

Desde la raíz del proyecto, con el validador vendorizado:

```bash
python3 tools/design-system/design_system.py discover . --json
python3 tools/design-system/design_system.py check design-system.json --json
python3 tools/design-system/design_system.py catalog design-system.json --out docs/design-system
python3 tools/design-system/design_system.py gate design-system.json --baseline .design-system.baseline.json [--approvals approvals.json]
```

| Código | Significado |
|---|---|
| `0` | `PASS`: todas las comprobaciones ejecutadas han pasado |
| `1` | `FAIL`: hay al menos un incumplimiento demostrado |
| `2` | `UNKNOWN`: una comprobación necesaria no se pudo ejecutar |
| `3` | Error de uso o de entrada/salida |

## PASS, FAIL y UNKNOWN

- **`PASS`** solo si la comprobación se ejecutó y no encontró incumplimientos.
- **`FAIL`** si hay un incumplimiento demostrado: token mal formado, referencia rota, ciclo, cambio protegido sin la aprobación que exige su régimen, catálogo desincronizado, muestra con clases que no existen en la implementación, capa `ds-*` propia del catálogo externo o adaptador que falla.
- **`UNKNOWN`** si la comprobación no se ejecutó o la evidencia es insuficiente: falta el baseline, falta el catálogo, no hay implementación declarada, falta el informe del adaptador, el régimen es `solo` y hay un cambio protegido, o la comprobación requiere un navegador o una persona.

`UNKNOWN` nunca se redondea a `PASS`. Un contrato válido no es un diseño correcto; una puerta verde no sustituye la inspección renderizada.

Lee [validation](references/validation.md) para la matriz de comprobaciones y lo que cada una demuestra.

## Evidencia y cierre

- Un hallazgo se escribe con la ruta y el valor observado; no con una impresión.
- Una aprobación se cita con su `id` y su `source`; no se inventa ni se atribuye.
- Un catálogo se entrega con su manifiesto y las huellas, o con la prueba de que importa la implementación y usa sus clases.
- Un cambio de contrato se entrega con la propuesta, la aprobación y el `gate`.
- Una comprobación visual o de accesibilidad se entrega con la evidencia inspeccionada o se declara `UNKNOWN`.

## Errores y paradas

- **Sistema existente sin contrato:** no lo sustituyas. Propón un contrato que lo describa y conserva sus decisiones; si hay contradicciones, decláralas.
- **Contrato documentado que ya existe:** no lo traduzcas a JSON sin motivo. Si el JSON no habilita nada, el trabajo termina en el documento y la evidencia.
- **Token o componente inexistente:** no lo inventes para que compile. Propón el token, su nivel y su motivo; espera aprobación si la ruta es protegida.
- **Fuente canónica duplicada:** detente y decide cuál manda. No copies valores entre dos fuentes; usa el mapa `duplicates` de `discover`.
- **Catálogo que redibuja la implementación:** si el catálogo define sus propias clases o copia valores, no lo parches: reconstruye desde la implementación y elimina la capa duplicada.
- **Catálogo rechazado dos veces por fidelidad:** es una parada. Se reconstruye desde la implementación. No hay tercer parche.
- **Aprobación ausente o dudosa:** bloquea el cambio. `approved_by` sin `source`, `id` o alcance no es una autorización. En modo `solo` la confirmación es la revisión y su commit; no fabricas un archivo de aprobaciones para cerrar.
- **Catálogo generado desincronizado:** vuelve a generarlo. No edites el HTML ni el CSS generados.
- **Comprobación imposible:** devuelve `UNKNOWN` con el motivo. No la sustituyas por una suposición.
- **Contrato que no describe el producto:** no lo «arregles» cambiando el producto sin autorización. Expón la divergencia y propón el cambio de contrato.

## Referencias

| Archivo | Cuándo se lee |
|---|---|
| [contract-model](references/contract-model.md) | Antes de escribir o revisar un contrato, tokens o componentes |
| [governance](references/governance.md) | Antes de proponer un cambio protegido, una excepción o una aprobación |
| [validation](references/validation.md) | Antes de ejecutar la puerta, interpretar `FAIL`/`UNKNOWN` o declarar el cierre |
| [design-system.template.json](assets/design-system.template.json) | Al crear un contrato nuevo |
| [catalog.html](assets/catalog.html) y [catalog.css](assets/catalog.css) | Solo los usa `catalog`; no se editan a mano por proyecto |
