# Parche local de Archify

Los diagramas de `docs/` se regeneran contra un checkout de [archify](https://github.com/tt-a1i/archify) en su base **v3.2.0** con cuatro ajustes locales puestos. El checkout vive en `archify/` y está ignorado por Git; esta ficha y su diff versionado (`archify-local-patch.diff`, junto a este fichero) son la única fuente para reconstruirlo desde un clon limpio.

## Qué ajusta

- `archify/renderers/workflow/workflow-compiler.mjs`: los lienzos de workflow automáticos emiten siempre `data-reader-fit="width-first"`.
- `archify/renderers/architecture/render-architecture.mjs`: los lienzos de arquitectura automáticos emiten `data-reader-fit="width-first"`.
- `archify/assets/template.html` y `viewer/viewer.css`: el `min-width` móvil para diagramas anchos es `0` en lugar de `720px`.
- `archify/assets/template.html`: las líneas CSS de solo espacios no llevan espacios finales, para que los artefactos recién generados pasen `git diff --check`; el render no cambia.

## Cómo aplicarlo

```bash
git clone https://github.com/tt-a1i/archify archify
git -C archify checkout v3.2.0
git -C archify apply --check ../docs/archify-local-patch.diff && git -C archify apply ../docs/archify-local-patch.diff
```

Sin parche la regeneración funciona pero produce HTML sin los ajustes de ancho; el diff se aplica limpio sobre la base declarada y un `git -C archify diff` en el repo, comparado con el fichero versionado, detecta la deriva del checkout.

## Regenerar después

```sh
node archify/archify/bin/archify.mjs deliver <type> docs/<skill>/<diagram>.json
```

El comando, los recibos y la política de regeneración parcial están en la sección «Documentación» de [`README.md`](../README.md).
