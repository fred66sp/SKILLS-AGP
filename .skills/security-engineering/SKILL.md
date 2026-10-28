---
name: security-engineering
description: "Enrutador de la skill `security-engineering` del repositorio: ingeniería de seguridad para software y agentes. Úsalo al diseñar una función sensible, revisar seguridad, auditar una dependencia o skill de terceros, investigar una exposición o declarar riesgo residual. No contiene el contrato: la fuente canónica vive en el paquete homónimo del repositorio, que se lee completo antes de trabajar."
---

# Enrutador de la skill de seguridad

Esta carpeta existe solo para que la skill se descubra. El contrato y sus detalles viven en un único sitio y no se copian aquí.

1. Lee `../../src/security-engineering/SKILL.md` completo, hasta el final, antes de analizar, recomendar o corregir nada.
2. Abre sus `references/` solo cuando el paso en curso lo pida, y ejecuta `scripts/security_scan.py` en lugar de reescribir sus reglas.
3. No apliques ninguna regla que no aparezca en ese `SKILL.md` o en sus referencias. Si este enrutador y el paquete difieren, manda el paquete.

Fuente canónica: `../../src/security-engineering/`. Documentación del repositorio sobre esta skill: `../../docs/security-engineering/index.html`.
