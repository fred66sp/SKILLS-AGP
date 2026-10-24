---
name: go-testing-and-verification
description: "Enrutador de la skill `go-testing-and-verification` del repositorio: cubre la lógica con pruebas unitarias y de tabla, fija la salida con golden files, prueba el binario de extremo a extremo con stdout, stderr y código de salida separados, y cierra con la puerta gofmt, build, test, vet, race y lint. Úsalo cuando haya que escribir pruebas, comprobar una regresión o declarar un cambio terminado. No contiene el contrato: la fuente canónica vive en el paquete homónimo del repositorio, que se lee completo antes de trabajar."
---

# Enrutador de la skill de pruebas y verificación

Esta carpeta existe solo para que la skill se descubra. El contrato y sus detalles viven en un único sitio y no se copian aquí.

1. Lee `../../src/go-testing-and-verification/SKILL.md` completo, hasta el final, antes de escribir pruebas o cerrar un cambio.
2. Abre sus `references/` solo cuando la capa de prueba lo pida, y usa `scripts/verify-go.py` en lugar de reescribir la puerta.
3. No apliques ninguna regla que no aparezca en ese `SKILL.md` o en sus referencias. Si este enrutador y el paquete difieren, manda el paquete.

Fuente canónica: `../../src/go-testing-and-verification/`.
