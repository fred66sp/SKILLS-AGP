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

## Tasks

| ID | Tarea | Specs | Unidad de commit |
|---|---|---|---|
| T1 | Contrato documental: `SKILL.md` + cuatro `references/` | S1, S2, S3, S6 | `feat(document-management-software): añadir el contrato documental de la skill` |
| T2 | Plantillas de plan e informe y `scripts/doc-inventory.py` | S6 | `feat(document-management-software): añadir plantillas y script de inventario` |
| T3 | Especificaciones de archify y los dos diagramas entregados | S4 | `docs(document-management-software): añadir las especificaciones y los diagramas` |
| T4 | Página principal y sus enlaces en `README.md` y `CHANGELOG.md` | S4, S5 | `docs(document-management-software): documentar la skill con página y diagramas` |
| T5 | Verificación de la entrega | S5 | sin commit propio: evidencia en el Log |

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
