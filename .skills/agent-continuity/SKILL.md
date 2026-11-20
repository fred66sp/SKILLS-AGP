---
name: agent-continuity
description: "Memoria de continuidad de proyecto (ACM) sobre db-ai: sesiones, decisiones, checkpoints y preferencias. Úsala al iniciar o cerrar sesión, capturar conocimiento durable, consolidar o reanudar. No para operar db-ai (skill db-ai) ni memoria global."
metadata:
  version: "0.2.0"
---

# Enrutador de la skill de memoria de continuidad de agente (ACM)

Esta carpeta existe solo para que la skill se descubra. El contrato y sus detalles viven en un único sitio y no se copian aquí.

1. Lee `../../src/agent-continuity/SKILL.md` completo, hasta el final, antes de abrir, cerrar o reanudar una sesión de ACM, o de capturar conocimiento.
2. Abre sus `references/` solo cuando la operación en curso lo pida: secuencia de los siete protocolos, criterios de captura y reconciliación de errores.
3. No apliques ninguna regla que no aparezca en ese `SKILL.md` o en sus referencias. Si este enrutador y el paquete difieren, manda el paquete.

Fuente canónica: `../../src/agent-continuity/`. Documentación del repositorio sobre esta skill: `../../docs/agent-continuity/index.html`.
