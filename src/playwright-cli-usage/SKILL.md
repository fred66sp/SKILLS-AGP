---
name: playwright-cli-usage
description: "Opera un navegador real desde la terminal con playwright-cli para comprobar lo que solo se ve renderizado: navegación, snapshots de accesibilidad con refs, clics, formularios, consola, red, capturas y sesiones. Se activa al explorar una interfaz, reproducir un flujo, localizar elementos o verificar un cambio funcional o visual en un navegador. Exige confirmación explícita antes de abrir o adjuntar un navegador y declara alcance, perfil y datos. No se usa para escribir suites de regresión, que pertenecen al runner del proyecto, ni para decidir calidad visual, que pertenece a web-interface-visual-design."
metadata:
  version: "0.1.0"
---

# Uso proporcionado de playwright-cli

Abre un navegador cuando la pregunta no se responde sin uno. Cada comando cuesta contexto, cada sesión deja estado y cada acción puede cambiar datos de alguien: por eso el contrato empieza por la decisión, sigue por la confirmación y termina por la evidencia.

## Responsabilidad y límites

- Posee la conducción de un navegador real desde la terminal: abrir, observar, interactuar, capturar y cerrar. Posee también la puerta de confirmación y el criterio de proporcionalidad de ese uso.
- No posee la suite de regresión. Si la comprobación debe repetirse, se escribe con el runner de tests del proyecto y la verifica su skill de verificación. `playwright-cli` sirve para descubrir el comportamiento una vez, no para sustituir una prueba.
- No posee el juicio visual. Entrega capturas y estados renderizados a `web-interface-visual-design`; no decide composición, tipografía ni contraste.
- No posee credenciales, datos ni autorización. No inventa usuarios, no reutiliza sesiones ajenas y no amplía el alcance por iniciativa propia.
- La referencia de comandos es la documentación oficial y la skill que instala el propio CLI. Este contrato manda sobre autorización, proporcionalidad, evidencia y cierre.

## Puerta de confirmación

Antes del primer comando que abre o adjunta un navegador (`open`, `attach`, `show`), presenta un briefing y espera un sí explícito. Sin esa confirmación solo están permitidos los comandos de lectura del entorno: `--version`, `--help` y `config-print`.

1. Di qué pregunta responde la automatización y por qué no basta una comprobación sin navegador.
2. Nombra el origen exacto: esquema, host y ruta si aplica; y el entorno real —local, preview, staging o producción—.
3. Declara la sesión: nombre, navegador, headless o `--headed`, dispositivo y perfil. Por defecto, perfil en memoria y headless.
4. Clasifica las acciones previstas: leer, interactuar, escribir datos, enviar formularios, descargar, subir o adjuntar a un navegador existente.
5. Di qué se teclea y de dónde salen los datos. Nunca credenciales reales de producción sin autorización explícita para ese uso.
6. Fija los límites: páginas, pasos máximos, tiempo y lo que no se toca.
7. Acuerda el cierre: qué artefactos se guardan, dónde, cuáles se borran y cómo se cierra la sesión.

Una confirmación genérica no autoriza producción, escritura de datos ni adjuntarse al navegador personal del usuario. Si el alcance cambia —otro origen, otro perfil, otra clase de acción—, se pide de nuevo. Una confirmación caduca al terminar la tarea. Lee [confirmation](references/confirmation.md) antes de redactar el briefing.

## Uso proporcionado

Elige el nivel más bajo que responda la pregunta:

| Nivel | Cuándo | Coste |
|---|---|---|
| Sin navegador | HTML, CSS y JS estático, tests, `curl`, lectura de código o del build | Cero |
| Un comando | Confirmar que el CLI existe, su versión o la configuración resuelta | Mínimo |
| Sesión corta | Un flujo de 3 a 15 comandos con refs y una captura | Acotado |
| Sesión larga o repetible | Se convierte en prueba del proyecto, no en más comandos | Justificado aparte |

- Usa `find` antes que un snapshot completo, `--depth` y el ámbito a un subárbol; guarda con `--raw` en fichero y lee solo el fragmento necesario. No vuelques un snapshot entero en la conversación.
- Reconoce el entorno con `scripts/preflight.py` antes de prometer nada. No instales el CLI ni los navegadores sin confirmación: son cambios de máquina, red y disco.
- Prefiere `--mobile` cuando el layout móvil sea aceptable: la página pesa menos y el snapshot es más pequeño.
- Detente cuando la pregunta esté respondida. No recorras el sitio por curiosidad ni repitas un comando para «comprobar».
- Lee [proportional-use](references/proportional-use.md) al planificar una sesión que vaya a durar más de unos pocos comandos.

## Procedimiento

**Fase A: Decidir si hace falta un navegador.**
1. Formula la pregunta observable que hay que responder y comprueba si el código, el DOM servido, un test existente o una captura previa ya la responden.
2. Comprueba si el proyecto tiene runner de tests y si la comprobación va a repetirse. Si se repite, la salida es una prueba, no una sesión manual.
3. Declara el nivel de la escalera y el presupuesto de pasos. Si no cabe en una sesión corta, divide el encargo.

**Fase B: Reconocer el entorno.**
1. Ejecuta `python3 scripts/preflight.py` y lee su salida. Distingue «CLI ausente» de «CLI disponible»; si `open` falla después por falta de navegador, es un caso distinto y se informa como tal.
2. Localiza el origen real que se va a abrir: servidor local, preview o URL pública. Comprueba que responde antes de culpar al navegador.
3. Revisa configuración y artefactos: `.playwright/cli.config.json`, `.playwright-cli/` y si el proyecto los ignora en Git.

**Fase C: Confirmar.**
1. Presenta el briefing de la sección anterior con los datos de B y pide confirmación explícita.
2. Si la respuesta no cubre una acción de escritura, adjuntar el navegador del usuario o usar producción, vuelve a preguntar solo por esa acción.
3. Si el usuario rechaza, informa de la alternativa sin navegador y no ejecutes `open`.

**Fase D: Ejecutar en pasos pequeños.**
1. Abre una sesión nombrada con el perfil acordado: `playwright-cli -s=<nombre> open <url>`. Usa `--headed` solo si el usuario debe ver o intervenir.
2. Observa con `find` o `snapshot` y usa los refs que devuelve la observación. Un ref vale hasta el siguiente cambio de página: vuelve a observar tras navegar.
3. Ejecuta una acción por comando (`click`, `fill`, `type`, `press`, `select`, `check`) y lee la respuesta antes de la siguiente.
4. Si hay un diálogo abierto, resuélvelo con `dialog-accept` o `dialog-dismiss` antes de continuar.
5. Cuando el resultado dependa del comportamiento y no solo del DOM, mira `console`, `requests` o una captura. Una captura se inspecciona como imagen, no se da por buena por existir.
6. No añadas esperas a ciegas ni subas timeouts para tapar un fallo. Si algo no ocurre, observa otra vez e identifica la causa.

**Fase E: Cerrar y declarar.**
1. Cierra lo que abriste: `close` en la sesión propia; `detach` si estabas adjunto a un navegador que no lanzaste. Usa `close-all` o `kill-all` solo sobre sesiones propias y con confirmación.
2. Borra o declara los artefactos: snapshots, capturas, trazas, vídeo y estado de autenticación. Nada de eso se versiona.
3. Separa lo observado de lo supuesto y entrega la evidencia. Lee [verification](references/verification.md) antes de redactar el cierre.

## Evidencia y cierre

- Código de salida cero significa que el comando se aceptó, no que la interfaz hiciera lo esperado.
- Un ref demuestra que el elemento existía en ese snapshot; no demuestra que la acción surtiera efecto.
- El efecto se demuestra con una observación posterior: URL, texto del snapshot, consola, red o captura inspeccionada.
- Una prueba del proyecto demuestra comportamiento repetible; una sesión de CLI solo demuestra lo ocurrido en esa sesión.
- Si no se pudo comprobar algo, se escribe «no verificado» con el motivo. No se sustituye por «parece correcto».

## Errores y paradas

- **CLI ausente o versión desconocida:** informa del resultado de `preflight.py`. Propón `npm install -g @playwright/cli` y `playwright-cli install-browser` con su coste; no los ejecutes sin confirmación.
- **Navegador ausente:** `install-browser` descarga binarios. Requiere confirmación, como cualquier instalación.
- **Ref inválido o elemento ausente:** vuelve a observar. No inventes refs, selectores ni coordenadas.
- **Timeout:** observa el estado real y la consola. No incrementes timeouts, no añadas `waitForTimeout` y no reintentes en bucle.
- **CAPTCHA, 2FA o consentimiento:** detente y pide intervención del usuario. No intentes sortearlo ni automatizar la burla.
- **Adjunto a un navegador existente:** confirma antes, no cierres ventanas ajenas y usa `detach` al terminar.
- **Datos reales en juego:** si la acción escribe, compra, borra o cambia una cuenta, para y confirma esa acción concreta, aunque el briefing ya estuviera aprobado.
- **Sesión colgada:** lista con `list`, cierra la propia y, solo si es tuyo, `kill-all` con confirmación.

## Precedencia

- La skill oficial que instala `playwright-cli` posee la referencia de comandos. Este contrato posee la autorización, la proporcionalidad, la evidencia y el cierre.
- La suite de regresión y su puerta pertenecen a la skill de verificación del lenguaje del proyecto. `playwright-cli` descubre; la prueba conserva.
- El juicio visual pertenece a `web-interface-visual-design`. Este contrato aporta el render y su evidencia.
- Credenciales, datos personales y superficies sensibles se tratan con `security-engineering`; aquí se aplican al navegador, no se redefinen.
