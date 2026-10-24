# skill-docs-present-tense

Reescribir las páginas `docs/<skill>/index.html` del repositorio como puerta de entrada en presente: sin duplicar el paquete, sin estado de la entrega, con la convención del repositorio marcada como tal. La primera página (`document-management-software`) ya está entregada y sirve de patrón.

## Specs

S1. (literal) «lo extendemos por partes. Primero git-flow-management»

S2. (literal, opción elegida para la primera página) «Página breve (recomendada)». Forma aprobada: siete secciones cortas en este orden — qué hace, cuándo se activa, cómo se usa, qué contiene el paquete, dónde están las reglas, preguntas cortas, los diagramas.

S3. (literal) «Una documentación correcta es la que no tiene estados vivos como por ejemplo referencias a commits, etc. Esos estados ya están en git.»

S4. La página no copia las reglas del paquete: remite a `SKILL.md` y a las `references/`. Si página y paquete difieren, manda el paquete y la página lo declara.

S5. El `index.html`, los dos diagramas de archify y sus recibos se marcan como convención de este repositorio, no como mandato de la skill.

S6. Las tarjetas de preguntas cortas se conservan solo cuando enseñan algo que la página no cubre ya en otra sección.

S7. Se conserva el andamio del HTML (CSS, tema claro/oscuro con `localStorage`, TOC con `IntersectionObserver`, botones de copiado, pie de página). Todos los enlaces y anclas de la página nueva resuelven.

S8. Los ficheros de los diagramas (`*.json`, `*.html`, `*.delivery.json`) no se tocan salvo que su contenido resulte falso. Si hay que regenerarlos, es con `archify deliver` desde `.pi/vendor/archify`, comprobando después que el spec está en LF y que los `sha256` y `bytes` del recibo casan con el disco.

S9. Verificación obligatoria de cada página: etiquetas balanceadas, un solo `h1`, siete secciones de contenido, numeración de secciones e índice coincidentes, cero anclas rotas, cero enlaces a fichero rotos, y `doc-inventory.py --root . --glob "*.md"` sin hallazgos nuevos respecto a la línea base.

## Tasks

| ID | Tarea | Specs | Ruta | Unidad de commit |
|---|---|---|---|---|
| T1 | Reescribir `docs/git-flow-management/index.html` | S2-S9 | `gentle-ai-worker` | `docs(git-flow-management): rewrite the skill page as a present-tense entry point` |
| T2 | Reescribir `docs/skill-creator/index.html` | S2-S9 | `gentle-ai-worker` | `docs(skill-creator): rewrite the skill page as a present-tense entry point` |
| T3 | Reescribir `docs/gherkin-scenario-review/index.html` | S2-S9 | padre, inline | `docs(gherkin-scenario-review): rewrite the skill page as a present-tense entry point` |
| T4 | Reescribir `docs/gherkin-scenario-authoring/index.html` | S2-S9 | padre, inline | `docs(gherkin-scenario-authoring): rewrite the skill page as a present-tense entry point` |
| T3 | ~~Reescribir `docs/gherkin-scenario-review/index.html`~~ | S2-S9 | descartada | la skill y su documentación fueron eliminadas por el usuario |
| T4 | ~~Reescribir `docs/gherkin-scenario-authoring/index.html`~~ | S2-S9 | descartada | la skill y su documentación fueron eliminadas por el usuario |
| T5 | Barrido final del repositorio: `README.md`, `CHANGELOG.md` y las páginas sin estado de la entrega ni listas que caduquen | S3 | padre, inline | pendiente |

## Log

L1 (literal): «lo extendemos por partes. Primero git-flow-management»

L2 Estado de partida: la página de `document-management-software` quedó reescrita en los commits `ca0aec8` (página), `16c8dc2` (regla de exclusión del estado de la entrega en el paquete) y `0353fcc` (índices que reflejan la regla). Esa página es el patrón de las cuatro restantes.

L3 Línea base de hallazgos documentales: `python3 src/document-management-software/scripts/doc-inventory.py --root . --glob "*.md"` devuelve 23 hallazgos, todos preexistentes (encabezados repetidos entre SKILL.md y referencias de varias skills, `hotfix`/`release` duplicados en `git-flow-management`, y `log`/`specs`/`tasks` entre los documentos de `odd/tasks/`). S9 se comprueba contra esa cifra.

L4 Hechos verificados de `git-flow-management` para T1: el paquete tiene 15 ficheros — `SKILL.md` (205 líneas, doce invariantes), nueve `references/`, tres `assets/` (`icon.svg`, `plan-template.md`, `result-template.md`), `scripts/verify-branch.sh` y `agents/openai.yaml`. La página actual tiene 17 secciones y 92.379 bytes, abre prometiendo que «todo lo que hay aquí sale de la propia skill» y copia las doce invariantes y las tablas de las referencias. Nadie enlaza a sus anclas: solo `README.md` enlaza al fichero.

L5 T1 ejecutada por `gentle-ai-worker` con superficie limitada a `docs/git-flow-management/index.html`, y verificada de forma independiente por el padre: la página queda en 46.277 bytes desde 92.379, sin CRLF, con un `h1`, siete secciones y numeración coincidente entre el TOC y los `section-num`; cero anclas rotas y tres enlaces a fichero que resuelven; cero ocurrencias de `sha256`, `hash`, SHA hex, «se corrigió», «quedó», `--no-ff` o ramas `feature/` y `fix/` citadas; fuera el bloque del hero que prometía que todo sale de la propia skill, y dentro la nota de que manda el paquete (S4) y el sello `de este repositorio` en la sección 7 (S5). El árbol de la sección 4 casa con los quince ficheros reales del paquete, las nueve descripciones de referencias casan con el H1 de cada fichero y la tabla de salidas 0/1/2 de `scripts/verify-branch.sh` casa con el `SKILL.md` y con los `exit 2` del script. Los dos diagramas y sus recibos no se tocaron: `archify check --require-provenance` sigue dando `provenance: current` en ambos. Riesgos declarados: los recuentos («quince ficheros», «nueve referencias») envejecen si crece el paquete, igual que «ocho ficheros» en la página patrón; y no hubo comprobación visual del render, solo estructural. Los SHA de esta entrega viven en `git log`, no en este documento.

L6 Hechos verificados de `skill-creator` para T2, antes de delegar: el paquete es de terceros y tiene cuatro ficheros — `SKILL.md`, `references/checklist.md`, `assets/SKILL.template.md` y `scripts/validate-metadata.py` (la ruta `scripts/` en singular; la plantilla vive en `assets/`)—. No se edita: el `README.md` declara que las skills de terceros se sustituyen, no se modifican, así que la página describe lo que hay y no propone mejoras. La página actual tiene 15 secciones y 68.289 bytes, con seis bloques `status-strip`, entre ellos «Cómo se usa en este repositorio» (sección 14), que es registro de entrega. Le enlazan solo dos lineas del `README.md`, sin anclas. Existe un documento de trabajo previo, `odd/tasks/skill-creator-docs.md`, que describe aquella entrega de 15 secciones: no se reescribe, queda como historial y este documento pasa a gobernar la versión en presente.

L7 Cambio de ruta para T2: la tabla decía «padre, inline» y pasa a `gentle-ai-worker`. Motivo: el andamio del padre superó el umbral de señal de contexto y una reescritura completa de página es una unidad acotada de muchas líneas; el mismo camino funcionó en T1 con verificación independiente posterior.

L8 T2 ejecutada por `gentle-ai-worker` (superficie: solo `docs/skill-creator/index.html`) y verificada de forma independiente por el padre. Resultado en disco: 41.575 bytes desde 68.289, LF, `title` que empieza por `skill-creator`, un `h1`, siete secciones con numeración coincidente entre TOC y `section-num`, cero anclas rotas y cuatro enlaces a fichero que resuelven (los dos diagramas, `../../.skills/skill-creator/SKILL.md` y `../best-practices-create-skills/README.md`), cero ocurrencias de estado de la entrega y ningún `status-strip` en el cuerpo. Los recuentos citados casan con el paquete: cuatro ficheros, cinco bloques de la checklist, seis pasos, 500 líneas y 1.024 caracteres. La tabla de salidas del validador se reprodujo con el script real obteniendo 0 / 1 / 1 / 0 (sin `--description`, primera persona, nombre inválido, metadatos válidos). Dos correcciones del informe del worker: los códigos 1 se midieron mal a primera vista porque una tubería se los cubría, y el tamano declarado de 41.846 bytes no es el del disco tras quitar el CSS sin uso. Dos anécdotas propias del paquete de terceros quedan declaradas en la página y no resueltas porque `.skills/**` no se edita: `SKILL.md` nombra `STYLE ERROR` mientras el script imprime `STYLE WARNING`, y el paso 2 lista `INSTALLATION.md` frente al `INSTALLATION_GUIDE.md` de la checklist. Añadido por el padre: la página aclara que el comando está copiado relativo a la carpeta de la skill y que desde la raíz el fichero está en `.skills/skill-creator/scripts/validate-metadata.py`. Diferencia de andamio frente a las otras dos páginas: aquí se borraron las reglas CSS `.status-strip` y `.status-mark` al quedarse sin uso, mientras que `document-management-software` las conserva; cada página es autónoma y ninguna de las dos variantes cambia el render. Los dos diagramas y sus recibos siguen intactos: `archify check --require-provenance` da `provenance: current` en ambos. Comprobación pedida por S9 y no ejecutada por el worker: `doc-inventory.py --root . --glob "*.md"` devuelve 23 hallazgos, la línea base de L3.

L9 (literal): «eliminadas las skills gherkin por mi». El árbol traía 36 borrados sin seguir: los dos paquetes de `src/gherkin-scenario-*` y sus cuatro grupos de ficheros en `docs/gherkin-scenario-*` (página, dos diagramas con spec y recibo). Consecuencia en este plan: T3 y T4 quedan descartadas, no fallidas. Barrido de referencias colgantes: `README.md` pierde las dos secciones de skills, las seis líneas de su listado de documentación y la fila `tools/` de la tabla de estructura, que se queda sin ocupantes porque `tools/check-feature.py` era la única; `CHANGELOG.md` deja de anunciarlas como añadidas, pasa la bala del comprobador a una sección nueva `### Eliminado` y registra la eliminación con sus rutas. Verificación: enlaces del `README.md`, `CONTRIBUTING.md` y `CHANGELOG.md` resuelven todos; las tres rutas inexistentes que cita el `CHANGELOG.md` son precisamente las que describe como eliminadas.
