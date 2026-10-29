# Backlog

Lista única y priorizada del trabajo pendiente de este repositorio. Lo más importante está arriba. No se duplica en GitHub Issues ni en ningún otro sitio: si un item necesita debate, se discute enlazándolo aquí.

La práctica viene de [Product backlog](https://www.atlassian.com/agile/scrum/backlogs) de Atlassian, adaptada a un repositorio personal de skills. Las reglas de trabajo y de integración están en [`CONTRIBUTING.md`](CONTRIBUTING.md).

Última revisión: 2026-10-25. Se revisa al abrir una rama y, como mínimo, una vez al mes: se reordena, se refina lo que va a entrar y se mueve a **Descartado** lo que ya no se hará.

## Norte

1. Que cada skill sea un contrato verificable y no un documento plausible.
2. Que el repositorio se comporte igual en cualquier máquina.
3. Que la documentación no se separe de lo que existe.

## Cómo se lee un item

- **Tipo:** skill · puerta · CI · documentación · deuda · investigación.
- **Prioridad:** Must (sostiene el Norte) · Should (mejora clara) · Could (deseable).
- **Tamaño:** S · M · L, estimación gruesa de esfuerzo, no de valor.
- **Estado:** listo · sin refinar · bloqueado.
- **Evidencia:** el hecho observable que justifica el item, con ruta y línea o comando.
- **Aceptación:** una comprobación ejecutable. Sin ella, el item no está listo.

Un item se cierra como se cierran los cambios del repositorio: `python scripts/check-repo.py` en `0 errores`, las suites de `scripts/` y de `src/*/scripts/` en verde, `CHANGELOG.md` con su entrada y `README.md`/`CONTRIBUTING.md` sincronizados si cambia una convención. El incremento de versión y la etiqueta solo se tocan si cambia el contrato de una skill.

## Listo para trabajar

### PBI-03: Validar en los dos sistemas donde se trabaja

- **Tipo:** CI · **Prioridad:** Should · **Tamaño:** M · **Estado:** listo
- **Evidencia:** `.github/workflows/validate.yml` fija `ubuntu-latest` y Python 3.12; el entorno de trabajo es Windows con Python 3.13. El repositorio existe para que todas las máquinas trabajen igual.
- **Resultado esperado:** la puerta se ejecuta en Linux y en Windows y falla en cualquiera de los dos cuando el repositorio se rompe.
- **Aceptación:**
  - matriz `os: [ubuntu-latest, windows-latest]` con la versión de Python alineada o duplicada a propósito.
  - los pasos no invocan `python3` a secas, que no existe en los runners de Windows.
  - las seis comprobaciones de la puerta se ejecutan en ambos jobs.
  - una rama de prueba deja los dos jobs en verde; los minutos de CI quedan anotados en este item.
- **Dependencias:** verificar en verde requiere `push`, que es una operación aparte con su propia confirmación.
- **Revisado:** 2026-10-25

### PBI-06: Contraste del botón primario en tema oscuro

- **Tipo:** documentación · **Prioridad:** Should · **Tamaño:** S · **Estado:** listo
- **Evidencia:** en las páginas escritas a mano de `docs/`, `.btn-primary` usa `color:#fff` sobre un degradado de `--accent` y `--accent-2`; en `data-theme="dark"` esos tokens son claros, así que el texto blanco queda por debajo de 2:1. La página `docs/playwright-cli-usage/index.html` ya lleva una corrección local para su botón.
- **Resultado esperado:** el texto del botón primario se lee en ambos temas sin cambiar la identidad ni el acento de cada skill.
- **Aceptación:**
  - contraste calculado ≥4.5:1 en tema oscuro en todas las páginas escritas a mano;
  - la corrección vive en la regla común o en un token de rol, no repetida por página;
  - `python scripts/check-repo.py` en 0 y captura de una página con el botón legible.
- **Dependencias:** ninguna.
- **Revisado:** 2026-10-29

## Sin refinar

### PBI-05: Garantías de la documentación HTML

- **Tipo:** documentación · **Prioridad:** Could · **Tamaño:** M aproximado · **Estado:** sin refinar
- **Intención:** que `docs/*.html` no se rompa en silencio y que los diagramas se puedan regenerar desde un clon limpio.
- **Falta para estar listo:**
  - decidir si los enlaces y anclas internas de las páginas se validan con un parser, que añade una dependencia, o con el mismo criterio que `check-repo.py` usa para Markdown.
  - resolver la regeneración: el ajuste vive en `archify/LOCAL-PATCH.md`, que no está en el repositorio porque `/archify/` está ignorado; o se versiona el ajuste, o se fija la versión de Archify sin parche.
- **Dependencias:** ninguna. La puerta de `scripts/check-repo.py` ya incluye el catálogo y la página de cada skill.
- **Revisado:** 2026-10-25

## Descartado

| Item | Motivo | Fecha |
|---|---|---|
| Migrar la planificación a GitHub Issues | Rompe la lista única y añade un segundo lugar que mantener; este repositorio ya publica el backlog en git. | 2026-10-25 |
| Unificar todas las descripciones de skill en una sola fuente | Exigiría generar README y catálogo desde el contrato; hoy el coste supera el riesgo real de divergencia. | 2026-10-25 |
