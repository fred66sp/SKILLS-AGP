# Backlog

Lista única y priorizada del trabajo pendiente de este repositorio. Lo más importante está arriba. No se duplica en GitHub Issues ni en ningún otro sitio: si un item necesita debate, se discute enlazándolo aquí.

La práctica viene de [Product backlog](https://www.atlassian.com/agile/scrum/backlogs) de Atlassian, adaptada a un repositorio personal de skills. Las reglas de trabajo y de integración están en [`CONTRIBUTING.md`](CONTRIBUTING.md).

Última revisión: 2026-11-02. Se revisa al abrir una rama y, como mínimo, una vez al mes: se reordena, se refina lo que va a entrar y se mueve a **Descartado** lo que ya no se hará.

## Norte

1. Que cada skill sea un contrato verificable y no un documento plausible.
2. Que el repositorio se comporte igual en cualquier máquina.
3. Que la documentación no se separe de lo que existe.

## Cómo se lee un item

- **Tipo:** skill · puerta · CI · documentación · deuda · investigación.
- **Prioridad:** Must (sostiene el Norte) · Should (mejora clara) · Could (deseable).
- **Tamaño:** S · M · L, estimación gruesa de esfuerzo, no de valor.
- **Estado:** listo · sin refinar · bloqueado.
- **Evidencia:** el hecho observable que justifica el item, con ruta y línea o comando.
- **Aceptación:** una comprobación ejecutable. Sin ella, el item no está listo.
- **ID:** numeración continua que no se reutiliza jamás. Un item cerrado por implementación pasa a **Retirados** con el commit que lo cerró; uno que ya no se hará, a **Descartado**. La regla existe porque el ID se cita fuera de este fichero, en `CHANGELOG.md`, en notas de máquina y en memorias de sesión, y reutilizarlo hace que dos épocas del backlog signifiquen cosas distintas bajo el mismo número.

Un item se cierra como se cierran los cambios del repositorio: `python scripts/check-repo.py` en `0 errores`, las suites de `scripts/` y de `src/*/scripts/` en verde, `CHANGELOG.md` con su entrada y `README.md`/`CONTRIBUTING.md` sincronizados si cambia una convención. El incremento de versión y la etiqueta solo se tocan si cambia el contrato de una skill.

## Listo para trabajar

### PBI-03: Validar en los dos sistemas donde se trabaja

- **Tipo:** CI · **Prioridad:** Should · **Tamaño:** M · **Estado:** listo
- **Evidencia:** `.github/workflows/validate.yml` fija `ubuntu-latest` y Python 3.12; el entorno de trabajo es Windows con Python 3.13. El repositorio existe para que todas las máquinas trabajen igual.
- **Resultado esperado:** la puerta se ejecuta en Linux y en Windows y falla en cualquiera de los dos cuando el repositorio se rompe.
- **Aceptación:**
  - matriz `os: [ubuntu-latest, windows-latest]` con la versión de Python alineada o duplicada a propósito.
  - los pasos no invocan `python3` a secas, que no existe en los runners de Windows.
  - las seis comprobaciones de la puerta se ejecutan en ambos jobs.
  - una rama de prueba deja los dos jobs en verde; los minutos de CI quedan anotados en este item.
- **Dependencias:** verificar en verde requiere `push`, que es una operación aparte con su propia confirmación.
- **Revisado:** 2026-10-25

### PBI-08: Recibos de procedencia para skills de terceros

- **Tipo:** puerta · **Prioridad:** Should · **Tamaño:** S · **Estado:** listo
- **Evidencia:** `README.md:261` declara `.skills/skill-creator/` fijada a una revisión de `mgechev/skills-best-practices`, afirma que la copia es idéntica byte a byte y fija la comprobación en `git diff` contra esa revisión, que exige un clon del repositorio upstream que no está en este. Desde un clon limpio nadie puede verificar lo que se afirma. El mecanismo que falta ya existe para otra cosa: `check_receipts` en `scripts/check-repo.py:311-348` compara `sha256` y bytes de cada artefacto contra un recibo JSON con `schemaVersion` y falla nombrando el archivo (`:346-349`). El árbol importado lo forman `SKILL.md`, `references/checklist.md`, `assets/SKILL.template.md` y `scripts/validate-metadata.py`, y este último es ejecutable, que es la parte que más puede sorprender.
- **Resultado esperado:** la puerta comprueba la procedencia desde un clon limpio, sin clon upstream y sin pasos manuales, y la deriva local no puede pasar en silencio.
- **Aceptación:**
  - `python scripts/check-repo.py` en un clon limpio verifica el `sha256` y los bytes de **todos** los ficheros del árbol importado contra un recibo versionado junto a la skill; no depende de `git diff` ni de que exista el repositorio upstream.
  - alterar un byte de cualquiera de esos ficheros hace fallar la puerta con un mensaje que nombra el archivo y código de salida 1. La puerta **falla**; informar y seguir no protege nada.
  - un script de `scripts/` regenera el recibo de forma determinista desde la copia importada, sin depender de la máquina ni de la fecha; una importación nueva añade su entrada sin edición manual del recibo.
  - `scripts/test-check-repo.py` cubre recibo ausente, byte alterado y regeneración estable, y la suite pasa.
  - `README.md` apunta al recibo como la comprobación de la fijación y `CONTRIBUTING.md` describe el paso de importación que lo genera.
- **Fuera del alcance de este item:** la regla de «variantes locales» que estaba redactada aquí. `README.md:253` fija otra política —las skills de terceros no se editan aquí, se sustituyen por otra revisión—, así que permitir forks locales es un cambio de política que va primero en `CONTRIBUTING.md` y después, si hace falta, en un item propio con su condición de disparo. No hay hoy ninguna variante local que lo justifique.
- **Dependencias:** ninguna. Convive con el control de versiones actual: las skills propias se rigen por sus etiquetas, las de terceros por su fijación.
- **Revisado:** 2026-11-02

## Sin refinar

### PBI-07: Evaluar una skill con experimentos, no con estructura

- **Tipo:** skill · **Prioridad:** Must · **Tamaño:** L · **Estado:** sin refinar
- **Intención:** responder con evidencia si una skill *funciona*, no solo si está bien formada. La puerta valida estructura, rutas, versiones y recibos; ningún mecanismo somete el comportamiento de un contrato. Y sin un vocabulario que separe las causas de un resultado negativo se tiende a «arreglar» una skill sana por un fallo del ejecutor, del entorno o de la prueba.
- **Evidencia:** el método ya existe y funciona en `archify/.agents/skills/archify-tuning/SKILL.md`: el paso 1 de su loop fija problema, hipótesis, qué evidencia lo apoya o lo refuta y presupuesto; el paso 6 cierra con una sola disposición entre confirmado, fix verificado, candidato experimental, enfoque rechazado o listo para revisión independiente; conserva el primer borrador y todos los intentos fallidos; reanuda desde un journal. `references/experiment-design.md` añade «Discovery is not proof of improvement», «One pair provides a case observation» y el congelado de revisión, runtime y contexto por brazo. El problema no es diseñar el método desde cero: es que vive dentro de `/archify/`, ignorado en `.gitignore:111`, así que no es reproducible desde un clon limpio ni reutilizable por las skills propias. El mismo obstáculo, aplicado a los diagramas, está en PBI-05.
- **Piezas que debe fijar el diseño:**
  - portar el método a una unidad versionada de este repositorio, con atribución a Archify, sin importar Archify entero.
  - protocolo presentado antes de autorizar nada: pregunta, hipótesis, entorno (modelo, agente, herramientas), entradas exactas, criterios observables de éxito y de fallo, comandos previstos, riesgos y condiciones de parada.
  - estructura de experimento aislada y conservable: entradas saneadas, sandbox, ejecuciones numeradas que no sobrescriben, evidencia e informe.
  - taxonomía de resultados con cuatro clases accionables: confirmado · defecto de skill · defecto de entorno o ejecutor · criterio insuficiente. Se amplía solo cuando un experimento real obligue a distinguir una quinta; una lista larga de clases sin un caso que las separe sería otro documento plausible.
  - qué abre cada clase: un item contra la skill, contra el entorno, o contra el propio protocolo.
- **Falta para estar listo:**
  - alojamiento de la unidad portada: skill nueva con sus `references/` y plantilla de protocolo, o sección de la guía de creación que ya aporta `skill-creator`.
  - dónde viven los experimentos de un repositorio que publica su contenido: carpeta ignorada con informe versionado, o repositorio desechable aparte. Archify lo resuelve con un directorio fuera del repo porque sus borradores llevan contenido de proyectos que pueden ser privados; hay que decir si esa solución se adopta tal cual.
  - la regla de cierre, que es de este item y la consumen el resto: ninguna fase, versión o afirmación de «funciona» sin un protocolo ejecutado con sus criterios previos, y una salida convincente sin criterio previo no es prueba. PBI-10 y PBI-11 no la redefinen.
- **Aceptación:**
  - el método portado se lee desde un clon limpio dentro de una unidad versionada de este repositorio y nombra su origen.
  - un experimento piloto, con protocolo aprobado de antemano, se ejecuta al menos dos veces contra una skill propia, clasifica su resultado con las cuatro clases y deja el informe completo en la estructura definida.
  - una repetición crea una ejecución nueva; ninguna evidencia anterior se sobrescribe.
  - la guía distingue «seguir fielmente la skill» de «hacer algo inspirado en ella» y dice qué se exige para cerrar una fase con cada una.
- **Dependencias:** ninguna para empezar; el piloto natural es una skill con ejecuciones reales ya documentables.
- **Revisado:** 2026-11-02

### PBI-09: Matriz de selección entre skills, solo si hay evidencia

- **Tipo:** documentación · **Prioridad:** Could · **Tamaño:** S · **Estado:** sin refinar
- **Intención:** decidir si hace falta una matriz «qué skill uso para este problema» aparte del catálogo, o si la respuesta visible ya vive en los sitios que existen.
- **Evidencia:** el README ya reparte materia en ocho bloques «Precedencia» (`:126`, `:146`, `:154`, `:179`, `:188`, `:203`, `:215`, `:227`) y las descripciones de los enrutadores de `.skills/` son la tabla de ruteo que el agente usa de verdad, validadas por `check_router` y `check_skills` en `scripts/check-repo.py:198` y `:267`. Una matriz escrita a mano es una tercera copia que se oxida con la skill siguiente, y el Descartado ya rechazó generar una fuente única porque el coste superaba el riesgo de divergencia.
- **Fuera de este item:** la escalera de unidad de trabajo (script → skill → metaskill → instrucciones del agente → nada) se escribió en `CONTRIBUTING.md`, que es donde se decide antes de añadir una skill. Este item no la duplica.
- **Falta para estar listo:**
  - un caso real: que el agente o una persona elija la unidad equivocada dos veces teniendo el catálogo y los bloques de precedencia delante.
  - decidir entonces si queda sujeta a la puerta por las slugs que referencia, o como guía libre.
- **Aceptación:**
  - con la evidencia anterior, la matriz señala para cada tipo de problema una skill concreta del repositorio.
  - las referencias solo usan slugs existentes y una slug inexistente hace fallar la puerta si quedó sujeta a ella.
  - README, catálogo y matriz no se contradicen en la precedencia declarada.
- **Dependencias:** PBI-10 para la fila skill-vs-metaskill; sin esa decisión, la matriz se escribe sobre arena.
- **Revisado:** 2026-11-02

### PBI-10: Contrato de viaje de una metaskill (decisión, sin artefactos)

- **Tipo:** investigación · **Prioridad:** Should · **Tamaño:** M · **Estado:** sin refinar
- **Intención:** decidir si este repositorio necesita una capa de orquestación y con qué contrato, antes de escribir ningún viaje. Una metaskill no contendría método propio: solo orden, puertas y evidencia, delegando el método en skills existentes y dejando un archivo de estado que permita retomar el viaje en otra sesión sin reiniciarlo.
- **Preguntas a responder:**
  - alojamiento: carpeta nueva en `src/`, o enrutador en `.skills/`, y por qué.
  - precedencia entre la metaskill y las skills invocadas: quién posee cada artefacto y qué pasa cuando ambas lo tocan.
  - skill dependiente no instalada: instalar, ejecutar un modo mínimo declarado, o abortar. La metaskill declara siempre en qué modo opera.
  - si `check-repo.py` valida también las fases y los artefactos que una metaskill referencia, o el viaje queda fuera de la puerta.
  - estados del tracker: se reutiliza un vocabulario de fases que ya exista —el journal de Archify con sus checkpoint y su resume, o el tracker de fases de este entorno— o se demuestra que ninguno sirve y se propone uno con `pending / in-progress / awaiting-evidence / done / deferred: motivo / skipped: motivo`. No se añade un tercer idioma de estados al repositorio sin argumentarlo.
- **Salida:** una decisión con alternativas y consecuencias, registrada como ADR con `adr-software`. Si la conclusión es que el catálogo no necesita la capa, el viaje no se hace y PBI-11 pasa a Descartado con el motivo.
- **Aceptación:**
  - las cinco preguntas tienen respuesta escrita en el ADR, cada una con la alternativa descartada.
  - el ADR pasa su propia puerta: `python src/adr-software/scripts/adr.py` sin defectos en el índice.
  - el contrato no cierra ninguna fase con «la salida parece buena»: cita el criterio de cierre de PBI-07.
- **Dependencias:** PBI-07 presta la regla de evidencia; este item no la reescribe.
- **Revisado:** 2026-11-02

### PBI-11: Piloto de un viaje

- **Tipo:** skill · **Prioridad:** Should · **Tamaño:** L · **Estado:** sin refinar
- **Intención:** recorrer un viaje de principio a fin en un proyecto desechable y comprobar si el contrato de PBI-10 produce los artefactos que anuncia.
- **Viajes candidatos:**
  - *De la idea al entregable:* `prd-cartographer` → `adr-software` → `design-system-architect` → la skill de lenguaje y su verificación → `software-testing` → `document-management-software` → `git-flow-management`.
  - *Reducir deuda técnica:* diagnóstico con `document-management-software` y `software-testing`, corrección gobernada por `adr-software` y las skills de estilo, cierre con verificación independiente.
- **Aceptación:**
  - el piloto recorre sus fases y produce los artefactos que anuncia, clasificados con la taxonomía de PBI-07.
  - el viaje se interrumpe y se retoma desde el tracker en una sesión nueva, sin repetir fases ya hechas.
  - una fase GATE no puede saltarse: queda documentado el intento y la negativa.
  - `python scripts/check-repo.py` en `0 errores` y las suites en verde.
- **Dependencias:** PBI-07 (criterio de prueba) y PBI-10 (contrato). Sin ellas, el piloto solo produciría un documento plausible, que es lo que prohíbe el Norte 1.
- **Revisado:** 2026-11-02

### PBI-05: Garantías de la documentación HTML

- **Tipo:** documentación · **Prioridad:** Could · **Tamaño:** M aproximado · **Estado:** sin refinar
- **Intención:** que `docs/*.html` no se rompa en silencio y que los diagramas se puedan regenerar desde un clon limpio.
- **Falta para estar listo:**
  - decidir si los enlaces y anclas internas de las páginas se validan con un parser, que añade una dependencia, o con el mismo criterio que `check-repo.py` usa para Markdown.
  - resolver la regeneración: el ajuste vive en `archify/LOCAL-PATCH.md`, que no está en el repositorio porque `/archify/` está ignorado; o se versiona el ajuste, o se fija la versión de Archify sin parche. Es el mismo obstáculo que PBI-07 encuentra desde el otro lado: allí el método útil está en la copia ignorada y hay que elevarlo.
- **Dependencias:** ninguna. La puerta de `scripts/check-repo.py` ya incluye el catálogo y la página de cada skill.
- **Revisado:** 2026-10-25

## Retirados

Cerrados por implementación. El ID queda consumido y no vuelve a usarse.

| ID | Item | Cerrado en |
|---|---|---|
| PBI-01 | Que una skill no entre sin documentación (puerta de catálogo) | [`b21cedb`](https://github.com/fred66sp/SKILLS-AGP/commit/b21cedb) · 2026-10-25 |
| PBI-02 | Declarar el fin de línea dentro del repositorio | [`0e6b6ee`](https://github.com/fred66sp/SKILLS-AGP/commit/0e6b6ee) · 2026-10-25 |
| PBI-04 | `CHANGELOG` con las versiones publicadas | [`fc905b9`](https://github.com/fred66sp/SKILLS-AGP/commit/fc905b9) · 2026-10-25 |
| PBI-06 | Contraste del botón primario en tema oscuro | [`31d0f80`](https://github.com/fred66sp/SKILLS-AGP/commit/31d0f80) · 2026-11-01 |

## Descartado

| Item | Motivo | Fecha |
|---|---|---|
| Generar la documentación con Hugo | Los HTML son artefactos con recibo `sha256` y la puerta corre con solo Python; generar el sitio obliga a commitear la salida (vuelven los diffs de 20 ficheros) o a meter un build en la validación. El chrome duplicado se resolvió con `docs/assets/site.css` y `site.js`, sin toolchain nueva. | 2026-11-01 |
| Migrar la planificación a GitHub Issues | Rompe la lista única y añade un segundo lugar que mantener; este repositorio ya publica el backlog en git. | 2026-10-25 |
| Unificar todas las descripciones de skill en una sola fuente | Exigiría generar README y catálogo desde el contrato; hoy el coste supera el riesgo real de divergencia. | 2026-10-25 |
