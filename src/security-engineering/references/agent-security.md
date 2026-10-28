# Seguridad de agentes, LLM y MCP

Aplica cuando un modelo decide, usa herramientas, mantiene memoria o se coordina con otros agentes. Léela en el paso 4 del contrato. Está basada en la guía de seguridad de agentes de OWASP, sin copiarla.

## Modelo de confianza

El modelo no es una frontera de seguridad. Todo lo que el modelo «decide» se valida en el componente que ejecuta. Un prompt no es un control de acceso y una instrucción del sistema no es una autorización.

- El modelo propone; el ejecutor autoriza, valida y registra.
- La descripción de una herramienta, de un servidor MCP o de una skill es contenido no confiable: puede contener instrucciones hostiles.
- El contenido recuperado (documentos, webs, correos, issues) es dato, nunca instrucción.
- La identidad del actor viaja fuera del contexto del modelo y no se acepta desde el texto.

## Herramientas y mínimo privilegio

- Concede solo las herramientas que la tarea necesita. Separa conjuntos por nivel de confianza.
- Define por herramienta: operaciones permitidas (`read` frente a `write`), rutas, comandos, hosts, tablas y campos.
- Allowlist explícita; lo no listado se deniega. Un comodín de shell, ruta o SQL anula el control.
- Las credenciales de una herramienta no se reutilizan para otra ni se exponen al modelo.
- El ejecutor comprueba permisos y alcance, no la herramienta que el modelo dice usar.
- Herramientas de solo lectura por defecto; escritura y borrado requieren permiso explícito.
- MCP: trata cada servidor como tercero. Revisa qué herramientas expone, qué rutas toca y a qué red accede; no confíes en su descripción.

## Inyección de prompt

- Separa instrucciones de datos con delimitadores y etiquetas de origen; el modelo debe saber qué texto es contenido.
- Valida y normaliza el contenido externo antes de incluirlo; elimina instrucciones incrustadas cuando el formato no las necesita.
- No ejecutes ni obedezcas texto recuperado que pida cambiar de objetivo, revelar el sistema o llamar herramientas.
- Usa una llamada separada para resumir o clasificar contenido no confiable cuando el riesgo lo justifique.
- La inyección indirecta es la norma: web, PDF, correo, comentario de issue y respuesta de API.
- Las pruebas deben incluir instrucciones hostiles en cada fuente, no solo en el mensaje del usuario.

## Memoria y contexto

- Valida y sanea antes de persistir; no guardes el mensaje crudo como memoria de confianza.
- Aísla memoria por usuario, sesión y tenant. Una memoria compartida es un canal entre atacantes.
- Define caducidad, tamaño máximo y número máximo de entradas.
- Redacta secretos y datos personales antes de guardar; audita el contenido persistido.
- Integridad para memoria de larga duración; una entrada modificada no se usa como verdad.
- No permitas que la memoria recuperada cambie reglas del sistema; es contexto, no política.

## Aprobaciones y acciones de alto impacto

Clasifica acciones por riesgo: lectura, escritura, comunicación externa, dinero, administración y borrado.

- Las acciones irreversibles, financieras, administrativas o visibles al exterior requieren aprobación humana.
- La aprobación se vincula al actor, herramienta, destino, parámetros normalizados, fecha y caducidad.
- Se consume una sola vez y en el mismo paso atómico que la ejecución; no se reutiliza ni se comparte.
- Cambiar el destino o un parámetro invalida la aprobación y exige otra.
- Separa quien decide de quien ejecuta: el agente propone, el servicio de política valida.
- Falla cerrado si no se puede clasificar el riesgo, validar la aprobación o registrar la acción.
- Ante duda, pide confirmación; nunca la simules con un flag del prompt.

## Salida y ejecución

- Valida la salida con esquema antes de ejecutarla o mostrarla.
- Allowlist de herramientas y acciones en la salida, no solo en la entrada.
- Detecta exfiltración: datos sensibles codificados, URLs con payload, destinos no declarados, volúmenes anómalos.
- Límites de tamaño y de frecuencia; una respuesta no puede convertirse en un bucle de acciones.
- Redacta secretos y datos personales de la salida mostrada y registrada.
- No ejecutes código generado sin sandbox y sin revisar qué importa y a qué red accede.

## Monitorización y auditoría

- Registra decisión, herramienta, parámetros redactados, resultado, actor, sesión y política aplicada.
- Un log sin actor ni política no sirve para forense ni para detectar abuso.
- Alerta sobre aprobaciones repetidas, saltos de aprobación, privilegios elevados, frecuencia anómala y aumento de acciones de riesgo.
- Mide coste y tokens por sesión y usuario; un bucle puede ser una denegación de cartera.
- Conserva la traza el tiempo necesario y protégela de escritura por el propio agente.

## Multiagente

- Define límites de confianza entre agentes; un agente de baja confianza no delega en uno privilegiado sin control.
- Autentica el mensaje y aplica los permisos del emisor en el receptor. Una firma válida no concede permiso.
- Firma los componentes relevantes (emisor, destinatario, tipo, payload, creación, caducidad, identificador) con una implementación mantenida.
- Ventana de validez corta y rechazo de identificadores repetidos; un timestamp solo no evita la repetición.
- Sin estado compartido para detectar repetición, rechaza o usa otro mecanismo; no asumas deduplicación global.
- Cifra el transporte: la firma no da confidencialidad.
- Cortacircuitos y límite de profundidad para evitar fallos en cascada.

## Protección de datos

- Clasifica el dato antes de incluirlo en contexto: público, interno, confidencial, restringido.
- Minimiza: el contexto contiene lo necesario, no todo lo disponible.
- Redacta o enmascara según clasificación y operación (contexto, log, salida).
- Cifra en tránsito y en reposo cuando corresponde; controla retención y borrado.
- No envíes datos regulados a un proveedor de modelo sin base y contrato; declara el flujo.
- Los datos de prueba son sintéticos; nunca clientes reales en fixtures.

## Límites de coste y disponibilidad

- Presupuesto de tokens, llamadas, reintentos y tiempo por sesión.
- Límite de profundidad de cadena de herramientas y de agentes.
- Backoff con techo; sin reintentos infinitos.
- Detección de bucles por repetición de acción y por falta de progreso.
- Aislamiento de ejecución: contenedor, usuario sin privilegios, red restringida, cuota de CPU y memoria.

## Pruebas adversariales

Mantén una matriz repetible y ejecútala en CI cuando cambien prompt, herramientas, memoria, recuperación, políticas o proveedor:

| Caso de abuso | Qué se valida |
|---|---|
| Secuestro de instrucciones | Las instrucciones del sistema no se sustituyen por contenido del usuario o recuperado |
| Uso indebido de herramienta | Una herramienta no autorizada se deniega aunque el modelo la pida con seguridad |
| Escalada de privilegios | Una sesión de baja confianza no alcanza herramientas, secretos ni acciones de administración |
| Envenenamiento de memoria | El contenido hostil se sanea, acota, caduca o rechaza antes de persistir |
| Exfiltración | El contexto sensible no sale por herramientas, citas, logs ni salida final |
| Abuso recursivo | Los límites de profundidad, reintento, token y coste detienen el bucle |
| Salto de aprobación | Una acción de alto impacto no se ejecuta sin aprobación válida, vigente y ligada a los parámetros |
| Cadena multiagente | Un agente comprometido no hace que otro exceda su límite |

Evidencia que se conserva: versión del agente, proveedor y modelo, política de herramientas, configuración de recuperación, casos ejecutados, resultado esperado y observado, y riesgo residual aceptado con su control compensatorio.

## Señales de diseño inseguro

- El prompt contiene la lista de permisos y el ejecutor no comprueba nada.
- La herramienta recibe un comando, ruta o consulta libre.
- La aprobación es un booleano del contexto o un `user_confirmed` sin vínculo.
- La memoria guarda el mensaje crudo y se comparte entre usuarios.
- El agente lee variables de entorno y tiene salida a red sin allowlist.
- El servidor MCP se instala sin revisar y se le da el directorio del proyecto entero.
- No hay límite de tokens, reintentos ni profundidad.
- Los logs guardan el prompt completo con secretos y datos personales.
