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
- **ID:** numeración continua que no se reutiliza jamás. Un item cerrado por implementación pasa a **Retirados** con el commit que lo cerró; uno que ya no se hará, a **Descartado**. La regla existe porque el ID se cita fuera de este fichero —`CHANGELOG.md`, notas de máquina, memorias de sesión— y reutilizarlo hace que dos épocas del backlog signifiquen cosas distintas bajo el mismo número.

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

## Sin refinar

### PBI-05: Garantías de la documentación HTML

- **Tipo:** documentación · **Prioridad:** Could · **Tamaño:** M aproximado · **Estado:** sin refinar
- **Intención:** que `docs/*.html` no se rompa en silencio y que los diagramas se puedan regenerar desde un clon limpio.
- **Falta para estar listo:**
  - decidir si los enlaces y anclas internas de las páginas se validan con un parser, que añade una dependencia, o con el mismo criterio que `check-repo.py` usa para Markdown.
  - resolver la regeneración: el ajuste vive en `archify/LOCAL-PATCH.md`, que no está en el repositorio porque `/archify/` está ignorado; o se versiona el ajuste, o se fija la versión de Archify sin parche.
- **Dependencias:** ninguna. La puerta de `scripts/check-repo.py` ya incluye el catálogo y la página de cada skill.
- **Revisado:** 2026-10-25

### PBI-06: Metaskills — viajes que orquestan varias skills

- **Tipo:** skill · **Prioridad:** Should · **Tamaño:** L · **Estado:** sin refinar
- **Intención:** dar al repositorio una capa de orquestación. Una metaskill es un contrato de viaje: fija una secuencia de fases, delega el método en skills existentes, exige una decisión humana en cada punto de decisión, produce artefactos verificables y deja un archivo de estado que permite retomar el viaje en otra sesión sin reiniciarlo. La metaskill no contiene método propio; solo orden, puertas y evidencia.
- **Viajes candidatos:**
  - *De la idea al entregable:* `prd-cartographer` → `adr-software` → `design-system-architect` → la skill de lenguaje y su verificación → `software-testing` → `document-management-software` → `git-flow-management`.
  - *Reducir deuda técnica:* diagnóstico con `document-management-software` y `software-testing`, corrección gobernada por `adr-software` y las skills de estilo, cierre con verificación independiente.
- **Falta para estar listo:**
  - decidir el alojamiento: carpeta nueva en `src/` o enrutador en `.skills/`, y por qué.
  - definir el formato del tracker de fases (`pending / in-progress / awaiting-evidence / done / deferred: motivo / skipped: motivo`) y dónde vive dentro del proyecto intervenido.
  - fijar la precedencia entre la metaskill y las skills invocadas: quién posee cada artefacto y qué pasa cuando ambas lo tocan.
  - decidir el criterio cuando una skill dependiente no está instalada: instalar, ejecutar un modo mínimo declarado, o abortar. La metaskill debe siempre declarar en qué modo está operando.
  - decidir si `check-repo.py` valida también las fases y artefactos que una metaskill referencia.
  - distinguir con evidencia "seguir fielmente la metaskill" de "hacer algo inspirado en ella": la salida convincente no cierra ninguna fase.
- **Aceptación:**
  - un viaje piloto recorre sus fases de principio a fin en un proyecto desechable y produce los artefactos que anuncia.
  - el viaje se interrumpe y se retoma desde el tracker en una sesión nueva, sin repetir fases ya hechas.
  - una fase GATE no puede saltarse: queda documentado el intento y la negativa.
  - `python scripts/check-repo.py` en `0 errores` y las suites en verde.
- **Dependencias:** ninguna técnica; el punto de decisión real es el alojamiento (`src/` frente a `.skills/`).
- **Revisado:** 2026-11-02

### PBI-07: Evaluación experimental de skills

- **Tipo:** skill · **Prioridad:** Must · **Tamaño:** L · **Estado:** sin refinar
- **Intención:** que el repositorio pueda responder con evidencia si una skill funciona, y no solo si está bien formada. Hoy la puerta valida estructura, rutas y versiones; ningún mecanismo somete el *comportamiento* de un contrato. Falta además un vocabulario que separe las causas de un resultado negativo: sin él, se tiende a "arreglar" una skill sana por un fallo del ejecutor, del entorno o de la integración.
- **Piezas que debe definir el diseño:**
  - protocolo experimental presentado antes de autorizar nada: pregunta, hipótesis, entorno (modelo, agente, herramientas), entradas exactas, criterios observables de éxito y fallo, comandos previstos, riesgos, condiciones de parada.
  - estructura de experimento aislada y conservable: entradas saneadas, sandbox, ejecuciones numeradas sin sobrescribir, evidencia, informe.
  - taxonomía de resultados que distinga al menos: confirmado · parcial · no confirmado · fallo de skill · fallo del ejecutor · fallo de integración · fallo de entorno · entrada defectuosa · criterio insuficiente · no concluyente.
  - cuándo una clase de fallo abre un item de backlog contra la skill y cuándo solo contra el entorno o la prueba.
- **Falta para estar listo:**
  - decidir el alojamiento (¿skill nueva con sus `references/` y plantilla de protocolo, o sección de la guía de creación existente?).
  - decidir dónde viven los experimentos de un repositorio que publica su contenido: carpeta ignorada con informe versionado, o repositorio desechable aparte.
  - fijar la regla de cierre: ninguna fase, versión o claim de "funciona" sin un protocolo ejecutado con sus criterios previos; una salida convincente sin criterio previo no es prueba.
- **Aceptación:**
  - un experimento piloto con protocolo aprobado de antemano clasifica su resultado con la taxonomía y deja el informe completo en la estructura definida.
  - una repetición crea una ejecución nueva; ninguna evidencia anterior se sobrescribe.
  - la guía resultante distingue explícitamente "seguir fielmente la skill" de "hacer algo inspirado en ella".
- **Dependencias:** ninguna para empezar; el piloto natural es una skill con ejecuciones reales ya documentables.
- **Revisado:** 2026-11-02

### PBI-08: Manifiesto de procedencia para skills de terceros

- **Tipo:** puerta · **Prioridad:** Should · **Tamaño:** M · **Estado:** sin refinar
- **Intención:** que una skill de terceros fijada a una versión no pueda derivar en silencio. El repositorio ya declara el fijado; falta la comprobación: un manifiesto con hash por documento importado, regenerable desde un script, que la puerta contrasta en cada ejecución y que detecta cambios locales respecto del snapshot importado.
- **Regla companion:** las copias importadas se conservan intactas; toda mejora propuesta sobre ellas se registra como variante local con origen, versión declarada, hash de referencia, cambios, problema que resuelve y evidencia comparativa.
- **Falta para estar listo:**
  - decidir el alcance del hash: solo `SKILL.md` o el árbol completo de la skill de terceros (los `scripts/` son la parte que más puede sorprender).
  - decidir cómo se registra la revisión upstream en el momento de importar, para que la nota de procedencia no quede como `UNKNOWN` por defecto.
  - decidir si la puerta falla ante deriva local o solo la informa.
- **Aceptación:**
  - el script regenera el manifiesto de forma determinista desde un clon limpio, sin depender de la máquina ni de la fecha de ejecución.
  - alterar un byte de una skill de terceros importada hace fallar la puerta con un mensaje que nombra el archivo.
  - una importación nueva añade su entrada sin edición manual del manifiesto.
- **Dependencias:** ninguna; convive con el control de versiones actual de las skills propias.
- **Revisado:** 2026-11-02

### PBI-09: Guía de selección y matriz de decisión

- **Tipo:** documentación · **Prioridad:** Should · **Tamaño:** M · **Estado:** sin refinar
- **Intención:** dar al repositorio una respuesta visible a «¿qué unidad de trabajo uso?» antes de que el catálogo crezca más. Cubre dos decisiones distintas: elegir la skill correcta para un problema (por capa y tipo: producto, arquitectura, lenguaje, verificación, documentación, Git, visual) y elegir entre skill puntual o viaje completo. La decisión de viaje solo será estable cuando exista PBI-06; la de selección entre skills ya se puede escribir a mano sobre el catálogo actual.
- **Precedencia anticipada de creación:** antes de añadir una skill, decidir si la necesidad corresponde a otra solución más simple: operación determinista → script; conocimiento especializado bajo demanda → skill; recorrido con varias fases y decisiones humanas → metaskill; comportamiento permanente del agente → instrucciones del agente; problema puntual → nada.
- **Falta para estar listo:**
  - decidir el formato: página única o entrada por bloque, y cómo se sincroniza con la sección de precedencias del README sin duplicarla.
  - decidir si la matriz entra bajo la validación de la puerta (nombres de skill referenciados) o queda como guía libre.
- **Aceptación:**
  - para cada tipo de problema descrito en la guía, esta señala una skill (o viaje) concreta del repositorio y cuándo conviene invocarlas directamente en vez del viaje.
  - las referencias a skills de la guía solo usan slugs existentes; una slug inexistente hace fallar la puerta si la guía quedó sujeta a ella.
  - README, catálogo y guía no se contradicen en la precedencia declarada.
- **Dependencias:** PBI-06 para la parte skill-vs-metaskill; la primera mitad es independiente.
- **Revisado:** 2026-11-02

## Retirados

Cerrados por implementación. El ID queda consumido y no vuelve a usarse.

| ID | Item | Cerrado en |
|---|---|---|
| PBI-01 | Que una skill no entre sin documentación (puerta de catálogo) | `b21cedb` · 2026-10-25 |
| PBI-02 | Declarar el fin de línea dentro del repositorio | `0e6b6ee` · 2026-10-25 |
| PBI-04 | `CHANGELOG` con las versiones publicadas | `fc905b9` · 2026-10-25 |
| PBI-06 | Contraste del botón primario en tema oscuro | `31d0f80` · 2026-11-01 |

## Descartado

| Item | Motivo | Fecha |
|---|---|---|
| Generar la documentación con Hugo | Los HTML son artefactos con recibo `sha256` y la puerta corre con solo Python; generar el sitio obliga a commitear la salida (vuelven los diffs de 20 ficheros) o a meter un build en la validación. El chrome duplicado se resolvió con `docs/assets/site.css` y `site.js`, sin toolchain nueva. | 2026-11-01 |
| Migrar la planificación a GitHub Issues | Rompe la lista única y añade un segundo lugar que mantener; este repositorio ya publica el backlog en git. | 2026-10-25 |
| Unificar todas las descripciones de skill en una sola fuente | Exigiría generar README y catálogo desde el contrato; hoy el coste supera el riesgo real de divergencia. | 2026-10-25 |
