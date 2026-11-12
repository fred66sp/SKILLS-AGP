# AGENTS.md

Este repositorio es una colección de skills para agentes. La descripción canónica, el catálogo y la forma de usar una skill están en [`README.md`](README.md).

Este fichero solo enruta: no define reglas, comandos, recuentos ni estados. Si contradice a otra fuente, manda la otra fuente y se corrige este mapa.

## Fuentes canónicas

| Qué se busca | Dónde vive |
|---|---|
| Qué es el repositorio, catálogo, estructura, uso de una skill, validación, empaquetado y skills de terceros | [`README.md`](README.md) |
| Ramas, commits, integración, versiones y enrutadores | [`CONTRIBUTING.md`](CONTRIBUTING.md) |
| Contrato de una skill: activación, procedimiento, referencias, scripts y cierre | `src/<skill>/SKILL.md` |
| Qué skill aplica a un encargo | [`README.md`](README.md), sección «Skills disponibles», y la descripción de cada `.skills/<skill>/SKILL.md` |
| Enrutador de una skill propia | `.skills/<skill>/SKILL.md` |
| Trabajo pendiente y prioridad | [`.tasks-ai/AGENTS.md`](.tasks-ai/AGENTS.md), sección «Cuándo se usa qué» |
| Decisiones durables (ADR) | La base del tablero, con `tasks-ai adr`; su exportación versionada es [`docs/decisions/`](docs/decisions/) (generada: no se edita a mano; `adr export --check` detecta deriva) |
| Etiquetas del tablero: clases, asignación y catálogo | [`.tasks-ai/CONTRATO_ETIQUETAS.md`](.tasks-ai/CONTRATO_ETIQUETAS.md) → «1. Las clases y su convivencia», «2. Asignación correcta a una tarea», «3. Gestión del catálogo» |
| Servidor del tablero | [`serve.sh`](serve.sh) |
| Servidor de la documentación HTML | [`serve-web.sh`](serve-web.sh) |
| Contexto de producto y sistema visual | [`PRODUCT.md`](PRODUCT.md), [`DESIGN.md`](DESIGN.md) |
| Documentación pública, diagramas, recibos y fin de línea | `docs/` y [`README.md`](README.md), sección «Documentación» |
| La puerta que ejecuta la CI | [`.github/workflows/validate.yml`](.github/workflows/validate.yml); los mismos comandos en [`README.md`](README.md), sección «Validación» |

## Punto de entrada por encargo

| Encargo | Lee antes | Cierre |
|---|---|---|
| Crear o editar una skill | [`docs/best-practices-create-skills/README.md`](docs/best-practices-create-skills/README.md), [`.skills/skill-creator/SKILL.md`](.skills/skill-creator/SKILL.md), [`README.md`](README.md) secciones «Regla de empaquetado» y «Enrutadores de skills propias», y [`CONTRIBUTING.md`](CONTRIBUTING.md) secciones «Enrutadores de skills» y «Versiones de las skills» | La verificación de [`README.md`](README.md), sección «Validación» |
| Evaluar si una skill funciona | [`CONTRIBUTING.md`](CONTRIBUTING.md), sección «Evaluar una skill con experimentos» | Un informe clasificado en las cuatro clases como comentario de la ficha evaluada |
| Operación Git | [`src/git-flow-management/SKILL.md`](src/git-flow-management/SKILL.md) y [`CONTRIBUTING.md`](CONTRIBUTING.md) | El script que fije el contrato |
| Crear o etiquetar una tarea | [`.tasks-ai/CONTRATO_ETIQUETAS.md`](.tasks-ai/CONTRATO_ETIQUETAS.md) sección 2 | La tarea nace con su tipo y su estructural (`task` o `epic`); el catálogo vivo, en `tasks-ai tags` |
| Escribir o actualizar documentación | [`src/document-management-software/SKILL.md`](src/document-management-software/SKILL.md) | El inventario que fije el contrato |
| Redactar o corregir prosa | [`src/document-redactor/SKILL.md`](src/document-redactor/SKILL.md) | La puerta que fije el contrato |
| Regenerar un diagrama | [`README.md`](README.md), sección «Documentación» | El recibo del artefacto |
| Trabajar en interfaz o sistema visual | [`src/design-system-architect/SKILL.md`](src/design-system-architect/SKILL.md) o [`src/web-interface-visual-design/SKILL.md`](src/web-interface-visual-design/SKILL.md) | Lo que fije el contrato |

## Mantenimiento de este fichero

- Enlaza la fuente; no copies su contenido.
- Añade una fila solo cuando el punto de entrada no se deduzca del catálogo.
- Si una ruta deja de existir, este mapa está obsoleto: corrígelo en lugar de reconstruir aquí lo que decía.
