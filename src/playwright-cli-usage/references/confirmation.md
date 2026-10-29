# Briefing y confirmación del navegador

Se abre antes del primer comando que lanza o adjunta un navegador. Sin la confirmación que describe esta referencia, solo se permite leer el entorno con `--version`, `--help` y `config-print`.

## Plantilla del briefing

Siete líneas, sin relleno. Se copian y se completan; lo que no se pueda completar se declara como desconocido.

```text
Objetivo: <pregunta observable y por qué hace falta el navegador>
Origen: <https://host/ruta> (<local | preview | staging | producción>)
Sesión: <nombre>, <navegador>, <headless | headed>, <dispositivo>, perfil <en memoria | persistente | adjunto>
Acciones: <leer | interactuar | escribir | enviar | descargar | subir | adjuntar>
Datos: <qué se teclea, origen de credenciales, qué dato real se evita>
Límites: <páginas, pasos máximos, tiempo y lo que no se toca>
Cierre: <artefactos que se guardan, cuáles se borran, cómo se cierra la sesión>
¿Confirmas esta sesión?
```

Ejemplo mínimo:

```text
Objetivo: comprobar que el formulario de alta muestra el error de correo duplicado; el test de unidad no cubre el render del mensaje.
Origen: http://localhost:4321/registro (local)
Sesión: alta-local, chrome, headless, escritorio, perfil en memoria
Acciones: interactuar; rellenar y enviar con un correo de prueba desechable
Datos: nombre y correo ficticios; sin credenciales reales
Límites: una página, 12 pasos, 5 minutos; no se toca ningún dato fuera del formulario
Cierre: se conserva un snapshot del mensaje y se borra al entregar; `close` al terminar
```

## Clases de acción y permiso

| Acción | Permiso que exige |
|---|---|
| Leer una página pública | Confirmación del briefing |
| Navegar por varias páginas del mismo origen | Confirmación del briefing, con el límite de páginas escrito |
| Rellenar un formulario sin enviarlo | Confirmación del briefing |
| Enviar un formulario, crear, modificar o borrar | Confirmación específica de esa acción, aunque el briefing esté aprobado |
| Usar credenciales, aunque sean de prueba | Origen de las credenciales declarado y aprobado |
| Adjuntarse al navegador personal del usuario (`attach --extension`, `--cdp`) | Confirmación específica; es su sesión real y puede tener datos privados |
| Perfil persistente o `--profile` sobre un directorio existente | Confirmación específica; el estado sobrevive y puede mezclar cuentas |
| Subir o descargar ficheros | Confirmación específica, con rutas y contenido |
| `eval`, `run-code`, `route`, `delete-data`, `cookie-set`, `localstorage-set` | Confirmación específica; ejecutan código o alteran estado |
| `show`, `show --annotate`, `video-start`, `tracing-start` | Confirmación específica; muestran, graban o exponen la pantalla |
| Instalar el CLI o un navegador | Confirmación específica; modifican la máquina |

## Cuándo se vuelve a preguntar

- Cambia el origen: otro host, otro puerto, otro esquema, producción en vez de local.
- Cambia el perfil: de memoria a persistente, de lanzado a adjunto.
- Aparece una acción de la tabla que no estaba en el briefing.
- El usuario introduce credenciales o datos reales que no se habían declarado.
- Se supera el límite de páginas, pasos o tiempo acordado.
- Un diálogo del navegador pide permisos del sistema: cámara, micrófono, ubicación, notificaciones, portapapeles.

## Lo que no vale como confirmación

- «Adelante», «haz lo que veas», «tú mismo» o una aprobación del plan anterior no autorizan escritura de datos, producción ni adjuntarse al navegador del usuario.
- Una confirmación anterior no cubre otra tarea ni otra sesión.
- La ausencia de respuesta no es un sí. Si el usuario no confirma, se entrega la alternativa sin navegador.
- La urgencia no sustituye la confirmación. Si no hay tiempo para confirmar, no hay tiempo para ejecutar.

## Si el usuario rechaza

1. No ejecutes `open` ni `attach`.
2. Di qué parte de la pregunta queda sin responder y qué alternativa existe: revisar el HTML servido, ejecutar el test del proyecto, leer el código, pedir una captura al usuario.
3. Deja la sesión sin abrir y sin artefactos.
