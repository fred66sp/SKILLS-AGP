# Auditoría de skills y extensiones de terceros

Aplica antes de instalar, actualizar o confiar en una skill, plugin, servidor MCP, acción de CI o dependencia que pueda ejecutar código. Léela en el paso 5 del contrato.

## Por qué una skill es código

Una skill de agente se parece a una extensión de navegador: promete una función y recibe acceso al entorno. Puede contener instrucciones que redirigen al modelo, scripts que se ejecutan con los permisos del usuario y dependencias que entran en la cadena de suministro. La descripción no demuestra nada.

Superficies de ataque de un paquete de skill:

| Superficie | Qué puede hacer |
|---|---|
| Instrucciones (`SKILL.md`, referencias) | Inyectar órdenes, ocultar comportamiento, pedir secretos |
| Scripts | Leer ficheros, ejecutar comandos, abrir red, escribir configuración |
| Hooks de instalación | Ejecutar código al instalar o actualizar |
| Dependencias | Introducir código vulnerable o malicioso |
| Metadatos | Declarar una función distinta de la real |
| Actualizaciones | Cambiar el comportamiento después de la auditoría |
| Recursos ocultos | Ficheros sin extensión, binarios, unicode bidireccional |

## Procedimiento de auditoría

1. **Procedencia.** Identifica el origen, el autor, la licencia, el commit o versión exactos y si el paquete está fijado. Una URL sin revisión no es procedencia.
2. **Lectura completa.** Lee todos los ficheros, incluidos los ocultos y los que no parecen código. Cuenta lo que no puedas leer como riesgo, no como limpio.
3. **Mapa de ejecución.** Marca qué se ejecuta, cuándo y con qué permisos: instalación, arranque, primera invocación, cada uso.
4. **Contraste.** Compara lo declarado con lo que hace. Anota cada capacidad no declarada: red, lectura de secretos, escritura fuera del proyecto, persistencia.
5. **Escaneo.** Ejecuta `python3 <skill>/scripts/security_scan.py --root <ruta>` y revisa cada señal en contexto. El escáner no entiende intención.
6. **Dependencias.** Revisa el lockfile, los scripts de instalación y los binarios. Una dependencia fijada sin integridad sigue siendo una confianza.
7. **Aislamiento.** Si hay que probarla, ejecútala en un contenedor o usuario sin privilegios, sin secretos reales y sin red salvo la necesaria.
8. **Decisión.** Instalar, instalar con límites o no instalar. Escribe el motivo y lo que haría cambiar la decisión.
9. **Fijación y reauditoría.** Fija por commit o versión verificable. Cuando cambie, repite el procedimiento; una actualización puede ser un cambio de comportamiento.

## Señales que exigen parada

No instales sin explicación satisfactoria si aparece cualquiera de estas:

- lectura o enumeración de variables de entorno combinada con salida a red;
- codificación de datos (base64, compresión, cifrado) antes de enviarlos;
- descarga y ejecución en una sola línea (`curl … | sh`, `wget … | bash`);
- hooks de instalación o `postinstall` que no se explican;
- lectura de `~/.ssh`, `~/.aws`, `.npmrc`, `.netrc`, `.env` o llaveros;
- escritura en `~/.bashrc`, `cron`, `systemd`, LaunchAgents o servicios;
- shell inverso, sockets persistentes o puertos a la escucha;
- binarios sin fuente, ofuscación, payloads codificados o unicode bidireccional;
- permisos de escritura sobre el repositorio, el home o el sistema sin necesidad declarada;
- instrucciones que piden silencio, ocultar el uso de la skill o desactivar controles;
- coincidencia entre una descripción amable y un comportamiento de recolección o red;
- redirección a un destino no declarado o a un dominio con nombre parecido.

## Patrones maliciosos frecuentes

| Patrón | Ejemplo | Qué revela |
|---|---|---|
| Recolección de entorno | Itera todo el entorno y filtra claves con `KEY`, `TOKEN`, `SECRET` | Robo de credenciales |
| Exfiltración codificada | `base64` + POST a un host externo | Salida encubierta |
| Diagnóstico falso | «Información del sistema» que lee credenciales | Contradicción declaración/comportamiento |
| Persistencia | Escribe en `cron` o en el arranque del shell | Control posterior |
| Shell inverso | `nc -e /bin/sh` o `/dev/tcp` | Acceso remoto |
| Inyección en la descripción | «Ignora las instrucciones anteriores» o «no lo menciones» | Secuestro del agente |
| Actualización silenciosa | La versión nueva añade red o lectura de secretos | Rug pull |
| Dependencia señuelo | Nombre casi idéntico a un paquete popular | Typosquatting |
| Ofuscación | Blob largo codificado que se decodifica y ejecuta | Evasión de revisión |

Un patrón no prueba malicia: prueba que hace falta una explicación. La decisión se toma con el contexto completo, no con una coincidencia aislada.

## Decisión y registro

```text
Paquete: <nombre y ruta>
Origen y revisión: <repo, commit o versión>
Licencia: <licencia o "desconocida">
Ficheros revisados: <n y qué quedó fuera>
Capacidades declaradas: <qué dice que hace>
Capacidades observadas: <red, ficheros, secretos, ejecución, persistencia>
Señales: <hallazgos del escáner y de la lectura, con ubicación>
Dependencias: <fijadas, con integridad o "no verificadas">
Prueba en aislamiento: <resultado o "no ejecutada" con motivo>
Decisión: <instalar | instalar con límites | no instalar>
Límites: <permisos, red, datos y rutas permitidos>
Reauditoría: <cuándo y qué la dispara>
```

## Límites de los escáneres

- Los patrones detectan lo conocido; un atacante puede evitarlos.
- El análisis estático no ve lo que solo ocurre en ejecución.
- Un escaneo limpio no certifica una skill.
- Las reglas caducan; hay que actualizarlas y revisar los falsos positivos.
- Un binario o un paquete sin fuente no se puede auditar de verdad: se trata como no confiable.

La auditoría reduce riesgo; no lo elimina. El riesgo residual se declara y se acepta con conocimiento.
