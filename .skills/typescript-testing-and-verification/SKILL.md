---
name: typescript-testing-and-verification
description: "Enrutador de la skill `typescript-testing-and-verification` del repositorio: valida las fronteras con Zod 4 y tipos inferidos, comprueba los tipos con tsc --noEmit, cubre la lógica con pruebas y la CLI de extremo a extremo, y cierra con typecheck, lint, test y build mediante scripts/verify-ts.py. Úsalo cuando haya que escribir o revisar pruebas, validar entradas no confiables, comprobar una regresión o declarar un cambio terminado. No contiene el contrato: la fuente canónica vive en el paquete homónimo del repositorio, que se lee completo antes de trabajar."
---

# Enrutador de la skill de verificación TypeScript

Esta carpeta existe solo para que la skill se descubra. El contrato y sus detalles viven en un único sitio y no se copian aquí.

1. Lee `../../src/typescript-testing-and-verification/SKILL.md` completo, hasta el final, antes de escribir pruebas o cerrar un cambio.
2. Abre sus `references/` solo cuando la capa o la frontera lo pida, y usa `scripts/verify-ts.py` en lugar de reescribir la puerta.
3. No apliques ninguna regla que no aparezca en ese `SKILL.md` o en sus referencias. Si este enrutador y el paquete difieren, manda el paquete.

Fuente canónica: `../../src/typescript-testing-and-verification/`.
