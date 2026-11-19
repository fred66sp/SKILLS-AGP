---
name: db-ai
description: "Explora, consulta y modifica bases de datos SQLite con la CLI db-ai, que expone tablas, filas y campos como un sistema de archivos y evita generar SQL. Úsala cuando un agente necesite descubrir qué bases hay montadas, inspeccionar tablas y columnas, leer o buscar filas, exportar resultados o escribir con permisos, ETags, dry-run y transacciones. Cubre el descubrimiento progresivo con mounts, ls, tree, stat y describe; la lectura con cat, find, grep y export; y la escritura con touch, write, cp, mv, rm y batch, incluidos cursores, sesiones y códigos de error. No la uses para desarrollar, modificar o depurar la herramienta db-ai, ni para escribir SQL directo, ORMs, migraciones de esquema o administración de motores; tampoco para PostgreSQL u otros motores fuera del MVP. Prefiere la CLI propia del dominio cuando exista y aplique reglas de negocio."
metadata:
  version: "0.1.0"
---

# Enrutador de la skill de operación de bases de datos con db-ai

Esta carpeta existe solo para que la skill se descubra. El contrato y sus detalles viven en un único sitio y no se copian aquí.

1. Lee `../../src/db-ai/SKILL.md` completo, hasta el final, antes de explorar, consultar o modificar ninguna base con `db-ai`.
2. Abre sus `references/` solo cuando la operación en curso lo pida: formas exactas de comando, escritura y lotes, o errores y recuperación.
3. No apliques ninguna regla que no aparezca en ese `SKILL.md` o en sus referencias. Si este enrutador y el paquete difieren, manda el paquete.

Fuente canónica: `../../src/db-ai/`. Documentación del repositorio sobre esta skill: `../../docs/db-ai/index.html`.
