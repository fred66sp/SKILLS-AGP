# document-management-software

Skill de gestión documental de software en `src/document-management-software/` y su documentación en `docs/document-management-software/`.
Se trabajó en la rama `feature/document-management-software` desde `main`, con un arreglo posterior en
`fix/document-management-software-recibos`; las dos se integraron con `--no-ff`. Después, la historia completa
se unificó en un único commit inicial, a petición explícita y sin remoto de por medio. Sin remoto no hay publicación.

## Specs

S1. La skill se crea en este repositorio, en `src/document-management-software`.
S2. El nombre de la skill es `document-management-software` y coincide exactamente con el nombre del directorio padre.
S3. `C:\Users\alfredo\Documents\IDEAS\RECURSOS\Skills\software-documentalista` es la fuente del material documental, no el destino de la entrega.
S4. La documentación vive en `docs/document-management-software/`: página principal y dos diagramas de archify, cada uno con su especificación y su recibo de entrega.
S5. La entrega va en una rama corta desde `main`, con commits por unidad revisable y sin integrar en `main` hasta revisión explícita.
S6. Se cumple la regla de empaquetado del repositorio: dentro de `src/<skill>/` no hay `README.md`, `CHANGELOG.md` ni guías de instalación.
S7. La documentación de la skill distingue el contrato general de la skill de la convención documental de este repositorio (`index.html`, diagramas de archify, recibos): lo que es del repositorio va marcado como tal y no se presenta como regla de la skill.
S8. `docs/document-management-software/index.html` se escribe en presente y para quien llega por primera vez: siete secciones cortas, sin copiar las reglas del paquete (se remite a `SKILL.md` y a las `references/`) y sin narrar la entrega, sus defectos corregidos ni sus estados pasados.

## Tasks

| ID | Tarea | Specs | Unidad de commit |
|---|---|---|---|
| T1 | Contrato documental: `SKILL.md` + cuatro `references/` | S1, S2, S3, S6 | `feat(document-management-software): añadir el contrato documental de la skill` |
| T2 | Plantillas de plan e informe y `scripts/doc-inventory.py` | S6 | `feat(document-management-software): añadir plantillas y script de inventario` |
| T3 | Especificaciones de archify y los dos diagramas entregados | S4 | `docs(document-management-software): añadir las especificaciones y los diagramas` |
| T4 | Página principal y sus enlaces en `README.md` y `CHANGELOG.md` | S4, S5 | `docs(document-management-software): documentar la skill con página y diagramas` |
| T5 | Verificación de la entrega | S5 | sin commit propio: evidencia en el Log |
| T6 | Reescribir la página como puerta de entrada en presente, sin duplicar el paquete | S7, S8 | `docs(document-management-software): rewrite the skill page as a present-tense entry point` |

### Límites de rebanada

La guía del repositorio es de unas 400 líneas de autoría por commit. T1 y T2 se separaron de una única unidad de 622 líneas para respetarla; el contenido es idéntico. T3 incluye artefactos generados por archify (dos HTML de ~830 KB), que no cuentan como autoría: lo revisable es cada `*.json` y su recibo. T4 no se puede rebanar sin dejar la página rota a medias, porque la documentación referenciada debe existir en el mismo commit; se entrega como unidad única.

## Log

L1 (petición original, literal): «vamos a crear una skill C:\Users\alfredo\Documents\IDEAS\RECURSOS\Skills\software-documentalista con nombre document-management-software»

L2 (literal): «la ruta que te di es la fuente, la creación es en este repositorio, en src/document-mangement-software»

L3 (literal): «Haz la documentación en docs/»

L4 (literal): «adelante» — autoriza crear la rama desde `main`, los commits por unidad y deja la integración pendiente de revisión.

L5 Decisión de interpretación: el nombre `document-management-software` se lee como «gestión documental de software», coherente con el `SKILL.md` de la fuente (disciplina documental), no como dominio de software de gestión documental (DMS). Queda declarado al usuario, que no lo corrigió.

L6 Evidencia de verificación: `validate-metadata.py` → `SUCCESS`, descripción de 838 caracteres. `doc-inventory.py --root src/document-management-software` → 7 documentos, 7 enlaces resueltos, código 0. `archify validate` de los dos specs → ok. `archify check --require-provenance` → `provenance: current`. Re-entrega de los dos diagramas → `sha256` idéntico, reproducible byte a byte. Página: 1 `h1`, 14 secciones, 19 anclas resueltas, 5 enlaces a fichero sin roturas.

L7 Hallazgos ajenos al encargo, reportados y no corregidos: dos plantillas de `git-flow-management` sin H1 y los H2 `hotfix` y `release` duplicados entre sus referencias; y un H2 `Documentación` repetido entre `README.md` y `CONTRIBUTING.md`, ya presente en `main`.

L8 (literal): «primero en document-management-software lo reviso y luego lo extendemos, pero por lo que he entendido la skill estaba bien, solo es problema de documentarlo bien.»

L9 Decisión derivada de L8: el paquete `src/document-management-software/` se declara correcto y no se toca; su invariante 7 (la política documental del repositorio prevalece) es la puerta de adaptación. La mezcla estaba solo en `docs/document-management-software/index.html`: la promesa del hero («todo lo que hay aquí sale del paquete instalado») era falsa para las secciones 10, 11 y 14, que son convención de SKILLS-AGP. Se arregla la página (T6, S7). El mismo patrón existe en las otras cuatro páginas del repositorio: queda fuera de este encargo hasta revisión de esta.

L10 (literal): «No me gusta nada como está documentado, es extremadamente complicado entenderlo, se habla de estados pasados, etc. Quien lee eso por primera vez y quiere saber que hace la skill se vuelve loco y no entiende nada.»

L11 Diagnóstico de L10 y decisión: la página era un duplicado del paquete (10 invariantes, 7 pasos con sus tablas de parada, 6 grados de certeza, tablas de fuentes, checklist, cierre) y a la vez un informe de entrega («se aplicó a su propio paquete antes de publicarlo», «dos defectos se corrigieron», «quedaron reportados, no corregidos»). Duplicar contradice la invariante 3 de la propia skill. Se reescribe `docs/document-management-software/index.html` en seis secciones en presente (S8), con la evidencia de la entrega solo en este documento (L6, L7, L9) y la convención del repositorio marcada en la sección 6. Opción elegida por el usuario: «Página breve (recomendada)».

L12 Evidencia de T6: `doc-inventory.py --root src/document-management-software` → exit 0, sin hallazgos (el paquete no cambia). Comprobación estructural de la página reescrita → etiquetas balanceadas, 1 `h1`, 6 secciones de contenido, 0 anclas rotas, 3 enlaces a fichero resueltos (`SKILL.md`, `flujo-de-trabajo.html`, `arquitectura.html`). La página pasa de 70.078 a 39.255 bytes. Quedan reglas CSS del andamio original sin uso (`status-strip`, `sev-*`, `plain`, `cols-3`): se conservan para no divergir del andamio de las otras cuatro páginas.

## Commits

La historia se unificó después en un único commit inicial del repositorio. Las unidades que existieron antes de esa
unificación, en orden, fueron:

- `feat(document-management-software): añadir el contrato documental de la skill`
- `feat(document-management-software): añadir plantillas y script de inventario`
- `docs(document-management-software): añadir el diagrama de arquitectura`
- `docs(document-management-software): añadir el diagrama de flujo de trabajo`
- `docs(document-management-software): documentar la skill con página y diagramas`
- `docs(odd): registrar los commits de la entrega`
- `fix(document-management-software): corregir el recibo del diagrama de flujo`

L13 (literal): «a mí lo de Preguntas cortas, me parecía buena idea y ayuda mucho en el entendimiento.»

L14 Decisión derivada de L13: vuelve la sección Preguntas cortas como sección 6, con las seis preguntas que enseñan algo que la página ya no copia (inferencia frente a propuesta, documentar sin leer código, por qué el código no basta, convención propia del proyecto, dependencia externa, cierre proporcional). Se descartan las tres que repetían la sección 1 o la 2: si escribe o solo revisa, si siempre crea un documento nuevo, y si sustituye a los tests.

L15 (literal): «si puedes poner el enlace me parece buena idea.»

L16 Verificación en `.pi/vendor/archify` (v3.2.0), hecha sobre una copia en directorio temporal, nunca sobre los ficheros del repositorio: el enlace de vuelta a `index.html` no es expresable dentro de un artefacto `workflow` ni `architecture`. `common.schema.json` solo admite `url` en `brandMark` (forzoso `https?://`) y en `repository` (que además exige una `revision` de 40 hex); `patch explainer` solo aplica a artefactos `explainer`, y el HTML generado no contiene ninguna región de explainer; los renderers no emiten ningún `<a>` salvo el data URL del brand mark. La vía manual queda descartada con evidencia: tras inyectar un `<a href="index.html">` en el HTML, `finalize workflow` da `pass` y vuelve a renderizar desde el spec, de modo que el enlace inyectado desaparece (0 apariciones). Decisión: se declara la limitación en la sección 7 de la página («se vuelve con el botón atrás del navegador») y los cuatro ficheros de los diagramas no se tocan, así que sus recibos siguen siendo válidos.
