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
| T2 | Reescribir `docs/skill-creator/index.html` | S2-S9 | padre, inline | `docs(skill-creator): rewrite the skill page as a present-tense entry point` |
| T3 | Reescribir `docs/gherkin-scenario-review/index.html` | S2-S9 | padre, inline | `docs(gherkin-scenario-review): rewrite the skill page as a present-tense entry point` |
| T4 | Reescribir `docs/gherkin-scenario-authoring/index.html` | S2-S9 | padre, inline | `docs(gherkin-scenario-authoring): rewrite the skill page as a present-tense entry point` |
| T5 | Barrido final del repositorio: `README.md`, `CHANGELOG.md` y las cuatro páginas sin estado de la entrega ni listas que caduquen | S3 | padre, inline | `docs: drop delivery state from repository-facing documentation` |

## Log

L1 (literal): «lo extendemos por partes. Primero git-flow-management»

L2 Estado de partida: la página de `document-management-software` quedó reescrita en los commits `ca0aec8` (página), `16c8dc2` (regla de exclusión del estado de la entrega en el paquete) y `0353fcc` (índices que reflejan la regla). Esa página es el patrón de las cuatro restantes.

L3 Línea base de hallazgos documentales: `python3 src/document-management-software/scripts/doc-inventory.py --root . --glob "*.md"` devuelve 23 hallazgos, todos preexistentes (encabezados repetidos entre SKILL.md y referencias de varias skills, `hotfix`/`release` duplicados en `git-flow-management`, y `log`/`specs`/`tasks` entre los documentos de `odd/tasks/`). S9 se comprueba contra esa cifra.

L4 Hechos verificados de `git-flow-management` para T1: el paquete tiene 15 ficheros — `SKILL.md` (205 líneas, doce invariantes), nueve `references/`, tres `assets/` (`icon.svg`, `plan-template.md`, `result-template.md`), `scripts/verify-branch.sh` y `agents/openai.yaml`. La página actual tiene 17 secciones y 92.379 bytes, abre prometiendo que «todo lo que hay aquí sale de la propia skill» y copia las doce invariantes y las tablas de las referencias. Nadie enlaza a sus anclas: solo `README.md` enlaza al fichero.

L5 T1 ejecutada por `gentle-ai-worker` con superficie limitada a `docs/git-flow-management/index.html`, y verificada de forma independiente por el padre: la página queda en 46.277 bytes desde 92.379, sin CRLF, con un `h1`, siete secciones y numeración coincidente entre el TOC y los `section-num`; cero anclas rotas y tres enlaces a fichero que resuelven; cero ocurrencias de `sha256`, `hash`, SHA hex, «se corrigió», «quedó», `--no-ff` o ramas `feature/` y `fix/` citadas; fuera el bloque del hero que prometía que todo sale de la propia skill, y dentro la nota de que manda el paquete (S4) y el sello `de este repositorio` en la sección 7 (S5). El árbol de la sección 4 casa con los quince ficheros reales del paquete, las nueve descripciones de referencias casan con el H1 de cada fichero y la tabla de salidas 0/1/2 de `scripts/verify-branch.sh` casa con el `SKILL.md` y con los `exit 2` del script. Los dos diagramas y sus recibos no se tocaron: `archify check --require-provenance` sigue dando `provenance: current` en ambos. Riesgos declarados: los recuentos («quince ficheros», «nueve referencias») envejecen si crece el paquete, igual que «ocho ficheros» en la página patrón; y no hubo comprobación visual del render, solo estructural. Los SHA de esta entrega viven en `git log`, no en este documento.
