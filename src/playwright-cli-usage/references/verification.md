# Evidencia, artefactos y cierre

Se abre antes de redactar el cierre de una sesión de navegador. El objetivo es no confundir «el comando funcionó» con «el comportamiento es el esperado».

## Qué demuestra cada cosa

| Observación | Demuestra | No demuestra |
|---|---|---|
| Código de salida `0` | El comando se aceptó y terminó | Que la interfaz hiciera lo pedido |
| Ref en un snapshot | El elemento existía y era interactivo en ese momento | Que el clic surtiera efecto |
| Snapshot posterior | El estado del DOM después de la acción | Que sea el estado correcto si el criterio no está escrito |
| URL o título | Navegación efectiva | Que el contenido sea el esperado |
| `console` | Presencia o ausencia de mensajes registrados | Que no haya errores silenciosos |
| `requests` / respuestas | Una petición concreta y su resultado | Que el resto del flujo sea correcto |
| Captura inspeccionada | El estado visual en ese viewport y tema | Interacción, accesibilidad completa o comportamiento en otro tamaño |
| Test del proyecto | Comportamiento repetible bajo sus condiciones | Que la sesión manual no hiciera falta |

Regla: una afirmación de comportamiento necesita una observación **posterior** a la acción, y el criterio debe estar escrito antes de mirar. Si el criterio se inventa después, no es verificación.

## Cierre mínimo

1. Cierra la sesión que abriste con `close`. Si estabas adjunto a un navegador ajeno, `detach`.
2. Enumera los artefactos producidos y su ruta: snapshots, capturas, trazas, vídeo, estado de autenticación.
3. Borra lo que no sea evidencia necesaria. Un estado de autenticación, una traza o un vídeo pueden contener datos personales o tokens.
4. Comprueba que el árbol de trabajo no incorpora artefactos del navegador: `.playwright-cli/`, `test-results/`, `playwright-report/` y ficheros `*.state.json` deben estar ignorados o fuera del repositorio.
5. Declara el resultado en tres partes: lo observado, lo supuesto y lo no verificado.

## Higiene de artefactos

- `.playwright-cli/` es caché de trabajo, no entregable: no se versiona.
- `state-save` escribe cookies y almacenamiento; el fichero es sensible y se borra al terminar salvo que el usuario pida conservarlo.
- Las capturas y los vídeos pueden mostrar datos reales. Se revisan antes de adjuntarlos y se guardan solo si son la evidencia.
- Un perfil persistente guarda más que la sesión: no se reutiliza entre tareas ni se comparte.
- Si el proyecto no ignora esos artefactos, se avisa; añadirlos al `.gitignore` es un cambio aparte y se propone, no se impone.

## Triaje de fallos

| Síntoma | Primera observación | Acción |
|---|---|---|
| El elemento no aparece | Snapshot y `find` del texto visible | Corregir el ref o el criterio; no inventar selectores |
| El comando se queda esperando | Estado de la página, diálogo abierto, consola | Resolver el diálogo o detenerse e informar |
| La acción no cambia nada | Snapshot posterior, red, consola | Identificar si falta un paso intermedio o si la app falla |
| La página carga distinto | Tamaño, dispositivo, tema, sesión | Repetir con la condición declarada, sin cambiar varias a la vez |
| Error de red o 5xx | Logs del servidor, `requests` | Detenerse: no es un problema del navegador |
| CAPTCHA o 2FA |—| Parar y pedir intervención; no automatizar la burla |

## Informe de cierre

```text
Sesión: <nombre> · <navegador> · <headless | headed> · perfil <...>
Origen: <url>
Pregunta: <la del briefing>
Observado: <qué se vio, con el comando o el snapshot que lo demuestra>
Evidencia: <rutas de snapshot, captura o salida>
Supuesto: <lo que no se comprobó y por qué se asume>
No verificado: <lo que quedó fuera, con el motivo>
Artefactos: <conservados y borrados>
Sesión cerrada: <sí | no, y por qué>
```

Un cierre sin la línea «No verificado» es un cierre incompleto. Un cierre que dice «visualmente correcto» sin haber inspeccionado la imagen es falso.
