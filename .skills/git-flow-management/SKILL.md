---
name: git-flow-management
description: "Enrutador de la skill `git-flow-management` del repositorio: operaciones Git con ceremonia proporcional al tamaño y al riesgo, verificadas con comandos de solo lectura. Úsalo para cualquier operación Git —commit, preparación de ramas, integración, resolución de conflictos, borrado de ramas, push, etiquetas, release, hotfix o auditoría de historial— y cuando haga falta comprobar ascendencia y contención entre referencias con scripts/verify-branch.sh. No contiene el contrato: la fuente canónica es src/git-flow-management/SKILL.md, que se lee completo antes de ejecutar nada."
---

# Enrutador de la skill de operaciones Git

Esta carpeta existe solo para que la skill se descubra. El contrato y sus detalles viven en un único sitio y no se copian aquí.

1. Lee `src/git-flow-management/SKILL.md` completo, hasta el final, antes de proponer o ejecutar cualquier operación Git.
2. Abre sus `references/` solo cuando la operación concreta lo pida, y usa `scripts/verify-branch.sh` en lugar de reconstruir la comprobación a mano.
3. No apliques ninguna regla que no aparezca en ese `SKILL.md` o en sus referencias. Si este enrutador y el paquete difieren, manda el paquete.

Fuente canónica: `src/git-flow-management/`. Documentación del repositorio sobre esta skill: `docs/git-flow-management/index.html`.
