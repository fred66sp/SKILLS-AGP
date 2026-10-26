---
name: adr-software
description: "Enrutador de la skill `adr-software` del repositorio: creación y mantenimiento de Architecture Decision Records con contrato de agente. Úsalo cuando haya que proponer, redactar, revisar, aceptar, rechazar, deprecar o sustituir un ADR, inicializar el directorio y el índice, o comprobar sus convenciones. No contiene el contrato: la fuente canónica vive en el paquete homónimo del repositorio, que se lee completo antes de trabajar."
---

# Enrutador de la skill de ADR

Esta carpeta existe solo para que la skill se descubra. El contrato y sus detalles viven en un único sitio y no se copian aquí.

1. Lee `../../src/adr-software/SKILL.md` completo, hasta el final, antes de escribir, cambiar o revisar ningún ADR.
2. Abre sus `references/` solo cuando el paso en curso lo pida, y ejecuta `scripts/adr.py` en lugar de reescribir su lógica.
3. No apliques ninguna regla que no aparezca en ese `SKILL.md` o en sus referencias. Si este enrutador y el paquete difieren, manda el paquete.

Fuente canónica: `../../src/adr-software/`. Documentación del repositorio sobre esta skill: `../../docs/adr-software/index.html`.
