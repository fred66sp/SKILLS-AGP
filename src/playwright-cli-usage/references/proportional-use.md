# Uso proporcionado y coste de contexto

Se abre al planificar una sesión que vaya a durar más de unos pocos comandos. La pregunta que ordena todo: ¿cuál es la comprobación más pequeña que responde lo que se pregunta?

## Escalera de decisión

1. **Sin navegador.** El HTML servido, el CSS, el DOM construido, un test unitario, `curl`, la consola del servidor o una captura que ya exista responden muchas veces. Si responden, no hay sesión.
2. **Un comando.** `--version`, `--help`, `config-print`, una URL. Sirve para reconocer el entorno, no para verificar comportamiento.
3. **Sesión corta.** Un flujo concreto, de 3 a 15 comandos, con refs, una captura si la imagen es la evidencia y cierre inmediato. Es el caso normal: comprobar que un cambio se ve, reproducir un fallo, localizar un elemento, leer un mensaje de error.
4. **Sesión larga.** Solo si el encargo lo justifica y el usuario lo ha confirmado con su límite de pasos. Si el flujo se va a repetir, el nivel correcto no es más CLI: es una prueba en el runner del proyecto.

## Palancas de coste

- **`find` antes que `snapshot`.** Devuelve solo coincidencias con contexto, como `grep -C`. En una página grande ahorra la mayor parte del árbol.
- **`--depth` y ámbito.** `snapshot --depth=4` y luego `snapshot e34` sobre el subárbol. Un snapshot completo casi nunca hace falta.
- **`--raw` a fichero.** `playwright-cli --raw snapshot > snapshot.yml` deja el árbol en disco y en la conversación solo queda una ruta. Lee el fragmento que necesites, no el fichero entero.
- **`--json` solo al parsear.** Envolver la salida para leerla a ojo añade ruido.
- **`--mobile` cuando el layout lo permita.** La página móvil suele ser más ligera y su snapshot más pequeño.
- **Una sesión por tarea.** Abrir y cerrar cuesta menos que mantener varias vivas y confundirlas.
- **No repetir la observación.** Si la página no cambió, el snapshot anterior sigue siendo válido. Se vuelve a observar tras navegar o tras una acción que cambia el DOM.
- **Capturas con criterio.** Una captura es evidencia visual; no sustituye a un snapshot para localizar un elemento ni se hace «por si acaso».

El diseño del CLI ya apunta en esa dirección: el snapshot se guarda en disco y en el contexto solo entra su ruta, no el árbol completo. La disciplina consiste en no deshacer esa ventaja leyendo el fichero entero sin necesidad.

## Presupuesto de una sesión

Antes de abrir, escribe en el briefing:

- número máximo de páginas distintas;
- número máximo de comandos;
- tiempo máximo;
- condición de parada: «cuando vea X» o «cuando falle Y».

Al llegar al límite, se para y se informa de lo observado y de lo que queda. Ampliar el presupuesto es una decisión del usuario, no una decisión del agente.

## Cuándo no usar la CLI

- La comprobación debe ejecutarse en cada cambio: escríbela como test del proyecto.
- La pregunta es de accesibilidad estática, contraste o estructura: hay comprobadores y revisión de código; el navegador solo confirma el render.
- La página exige credenciales reales de producción, pagos o datos personales de terceros: no es un trabajo de exploración.
- El sitio está caído o el origen no responde: primero se comprueba el servidor; abrir el navegador no arregla un 502.
- El agente no puede confirmar con el usuario: no hay sesión.

## Antipatrones

- Abrir «para ver qué hay» y recorrer el sitio sin pregunta ni límite.
- Volcar snapshots completos en la conversación y razonar sobre ellos.
- Usar `eval` o `run-code` para saltarse la interfaz cuando bastaba un `fill`.
- Añadir `waitForTimeout`, subir timeouts o reintentar en bucle en lugar de observar.
- Dejar la sesión abierta «por si acaso» y artefactos en el árbol de trabajo.
- Convertir una sesión exploratoria en la única prueba de una regresión.
- Adjuntarse al navegador del usuario sin confirmación y cerrar sus pestañas.
