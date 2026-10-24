---
name: go-errors-and-lifecycle
description: "Enrutador de la skill `go-errors-and-lifecycle` del repositorio: define el contrato de errores, la envoltura e inspección con errors.Is y errors.As, el mapeo a códigos de salida, la propagación de context, la cancelación, las señales, la concurrencia con propietario y el cierre ordenado. Úsalo cuando haya que diseñar o revisar errores y el ciclo de vida de un programa Go. No contiene el contrato: la fuente canónica vive en el paquete homónimo del repositorio, que se lee completo antes de trabajar."
---

# Enrutador de la skill de errores y ciclo de vida

Esta carpeta existe solo para que la skill se descubra. El contrato y sus detalles viven en un único sitio y no se copian aquí.

1. Lee `../../src/go-errors-and-lifecycle/SKILL.md` completo, hasta el final, antes de cambiar errores, contextos o concurrencia.
2. Abre sus `references/` solo cuando el paso en curso lo pida.
3. No apliques ninguna regla que no aparezca en ese `SKILL.md` o en sus referencias. Si este enrutador y el paquete difieren, manda el paquete.

Fuente canónica: `../../src/go-errors-and-lifecycle/`.
