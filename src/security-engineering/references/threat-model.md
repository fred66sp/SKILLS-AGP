# Modelo de amenazas

Aplica al delimitar un análisis, dibujar límites de confianza, enumerar casos de abuso y clasificar hallazgos. Léelo en el paso 2 y al priorizar en el paso 6 del contrato.

## Qué debe responder

Un modelo de amenazas útil responde cinco preguntas en una página:

1. ¿Qué se protege y qué daño causa perderlo?
2. ¿Quién puede atacarlo y con qué acceso empieza?
3. ¿Por dónde entra y por dónde sale el dato?
4. ¿Qué control impide cada abuso y dónde se aplica?
5. ¿Qué queda sin cubrir y bajo qué supuesto?

Si una respuesta es «depende», escribe de qué depende. Un modelo con supuestos explícitos es más útil que uno aparentemente completo.

## Activos

Clasifica por daño, no por tecnología:

| Activo | Daño si se compromete | Prioridad |
|---|---|---|
| Credenciales y claves | Acceso a todo lo que autorizan; rotación costosa | Crítica |
| Datos personales o regulados | Daño a personas, sanción, pérdida de confianza | Crítica |
| Dinero o capacidad de pago | Pérdida directa o fraude | Crítica |
| Integridad de datos operativos | Decisiones erróneas, corrupción silenciosa | Alta |
| Disponibilidad del servicio | Interrupción, denegación de cartera | Alta |
| Código fuente y secretos comerciales | Ventaja competitiva, vectores posteriores | Alta |
| Reputación y comunicaciones | Suplantación, phishing a clientes | Media |

La ausencia de un activo en la lista no significa que no importe: significa que el alcance no lo cubre y debe declararse.

## Adversarios

| Adversario | Acceso inicial | Capacidad típica |
|---|---|---|
| Anónimo en internet | Sin credenciales | Automatización, enumeración, fuerza bruta |
| Usuario autenticado | Su propia cuenta | Escalada horizontal y vertical, abuso de lógica |
| Insider o empleado | Credenciales y conocimiento | Acceso directo, persistencia, ocultación |
| Dependencia o servicio comprometido | Cadena de suministro | Ejecución en build o runtime, actualización maliciosa |
| Contenido externo | Documento, web, correo, issue | Inyección de instrucciones, datos envenenados |
| Otro agente o herramienta | Mensaje o llamada de herramienta | Escalada entre agentes, confusión de identidad |

Un adversario sin acceso no es el mismo que uno con escritura. Declara el nivel de acceso que asumes; la severidad cambia con él.

## Límites de confianza

Marca cada punto donde un dato o una instrucción cambia de mano:

- navegador → API;
- API → base de datos, cola, almacenamiento;
- servicio → servicio interno;
- modelo → herramienta o servidor MCP;
- agente → agente;
- skill o plugin → sistema operativo;
- CI → producción;
- operador humano → consola de administración.

En cada límite, el receptor valida. Que el emisor sea interno no convierte el dato en confiable si el emisor puede ser comprometido.

## Casos de abuso

Un caso de abuso tiene entrada, privilegio y efecto. Ejemplos por familia:

| Familia | Caso de abuso | Control esperado |
|---|---|---|
| Autorización | Un usuario autenticado lee el pedido de otra cuenta cambiando el identificador | Comprobación por objeto y por acción en el servidor |
| Inyección | Un campo del formulario altera la consulta SQL | Consulta parametrizada, nunca concatenación |
| Inyección de comandos | Un nombre de fichero ejecuta un comando | Sin shell, lista de argumentos, validación |
| SSRF | Una URL de usuario hace que el servidor llame a la red interna | Allowlist de destinos, resolución y bloqueo de rangos privados |
| XSS | Un comentario ejecuta script en el navegador de otro usuario | Codificación contextual y CSP |
| Deserialización | Un payload crea objetos o ejecuta código | Formato sin ejecución, esquema y allowlist de tipos |
| Fuerza bruta | Credenciales probadas sin límite | Rate limit, bloqueo progresivo, MFA |
| Enumeración | Respuestas distintas revelan qué cuentas existen | Respuesta uniforme y tiempos comparables |
| Carrera | Dos peticiones simultáneas saltan un límite | Operación atómica y bloqueo |
| Exfiltración | Un agente envía secretos a un destino externo | Mínimo privilegio, allowlist de red, redacción |
| Inyección de prompt | Un documento recuperado cambia las instrucciones | Separación instrucción/dato, validación de salida |
| Envenenamiento de memoria | Contenido hostil persiste y afecta a otra sesión | Validación, aislamiento, caducidad |

## Rúbrica de severidad

Combina explotabilidad e impacto. La categoría de la vulnerabilidad no decide la severidad; la ruta concreta sí.

| | Impacto bajo | Impacto medio | Impacto alto | Impacto crítico |
|---|---|---|---|---|
| **Explotabilidad alta** (sin autenticación, remota, trivial) | Medio | Alto | Crítico | Crítico |
| **Explotabilidad media** (autenticado, condición simple) | Bajo | Medio | Alto | Crítico |
| **Explotabilidad baja** (privilegios altos, condición rara) | Bajo | Bajo | Medio | Alto |
| **Teórica** (sin ruta demostrada) | Informativo | Bajo | Bajo | Medio |

Ajustes que deben explicarse:

- Sube si el efecto es silencioso, persistente o afecta a muchos usuarios.
- Sube si el atacante puede repetirlo sin coste o automatizarlo.
- Baja si requiere acceso que ya equivale al impacto, o si un control compensatorio lo bloquea en la práctica.
- Un hallazgo sin ruta demostrada se marca como endurecimiento; no se infla para que se priorice.

## Supuestos y caducidad

Todo modelo declara:

- versión o commit analizado;
- configuración de despliegue asumida;
- dependencias y modelo con su versión;
- controles externos asumidos (WAF, proxy, TLS, red);
- fecha y condiciones que invalidan el análisis.

El análisis caduca cuando cambian el modelo, los permisos, las dependencias, la configuración de despliegue o los datos tratados. Un modelo de amenazas sin fecha no se puede reutilizar con honestidad.

## Encaje con otros marcos

- **STRIDE** para diseño: suplantación, manipulación, repudio, divulgación, denegación y elevación.
- **OWASP Top 10** para web y **OWASP API Top 10** para APIs: categorías de revisión, no veredictos.
- **OWASP AI Agent Security** para agentes: herramientas, memoria, aprobaciones, salida, multiagente y pruebas adversariales.
- **NIST AI RMF** para gobierno y riesgo, nunca como sustituto de una traza técnica.
- **CIS / benchmarks** para configuración de infraestructura, con la versión del benchmark declarada.
