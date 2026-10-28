# Revisión de código seguro

Aplica al revisar diseño, código o configuración. Léela en el paso 3 del contrato y recorre solo las categorías que el alcance toca.

## Método

1. Localiza las fuentes de datos no confiables: parámetros, cabeceras, cookies, cuerpo, ficheros, colas, webhooks, respuestas de terceros y contenido generado por un modelo.
2. Recorre cada fuente hasta su sumidero: consulta, comando, plantilla, ruta, cabecera, red, log, respuesta o decisión de autorización.
3. Comprueba si el control está en el servidor y en el punto correcto. Una validación en el cliente es una ayuda de usabilidad, no un control.
4. Distingue codificación de validación y de autorización: son controles distintos y no se sustituyen.
5. Registra cada hallazgo con ruta, línea, entrada, efecto y control ausente.

## Autenticación

- Contraseñas con hash lento y salado (Argon2id, scrypt o bcrypt con coste actual). Nunca hash rápido ni cifrado reversible.
- Comparaciones de secretos en tiempo constante cuando el atacante puede medir.
- MFA para cuentas privilegiadas y operaciones sensibles.
- Recuperación de cuenta con token de un solo uso, caducidad corta y respuesta uniforme.
- Sesiones con `HttpOnly`, `Secure` cuando hay TLS, `SameSite` y rotación tras autenticación.
- Sin credenciales por defecto, sin «recordar» tokens en URL y sin sesión eterna.
- Rate limit y bloqueo progresivo en login, registro, recuperación y verificación.

## Autorización

- Comprueba por objeto y por acción, en el servidor, en cada petición. No basta con ocultar el botón.
- Evita IDOR: el identificador de la petición no decide por sí solo a qué recurso se accede; cruza propietario, tenant y permiso.
- Deniega por defecto. Un rol desconocido no hereda permisos.
- No confíes en el `tenant_id`, `user_id` o rol enviados por el cliente.
- Revisa las operaciones masivas y las de administración por separado.
- Prueba con dos cuentas reales de distinto privilegio, no solo con un usuario.

## Inyección

- SQL y NoSQL: consultas parametrizadas o constructor de consultas con valores separados. Nunca concatenación ni interpolación de entrada.
- Comandos: sin shell; lista de argumentos; allowlist de comandos y rutas; permisos mínimos del proceso.
- Plantillas: contexto con escape automático; no compiles plantillas de usuario.
- LDAP, XPath, XML: escape y parámetros del motor; desactiva entidades externas y DTD.
- Cabeceras y logs: elimina saltos de línea de la entrada antes de escribirlos.
- Expresiones regulares: evita complejidad exponencial sobre entrada del usuario; acota longitud.

## SSRF y peticiones salientes

- Allowlist de esquema, host y puerto; resuelve y comprueba la IP antes de conectar.
- Bloquea rangos privados, loopback, link-local y metadatos del proveedor cloud.
- No sigas redirecciones sin volver a validar el destino.
- No devuelvas el cuerpo de la respuesta interna al usuario.
- Timeouts, límite de tamaño y sin reintentos automáticos sobre destinos no confiables.

## XSS, CSRF y frontend

- Codificación contextual al insertar en HTML, atributo, URL, CSS o JavaScript. No uses `innerHTML` con entrada; construye nodos y usa `textContent`.
- CSP restrictiva, sin `unsafe-inline` si se puede evitar; `frame-ancestors` para clickjacking.
- CSRF: token por sesión o doble envío, `SameSite`, y verificación de origen para operaciones con estado.
- CORS: origen explícito y credenciales solo cuando el diseño lo exige. `*` con credenciales está prohibido.
- Cookies: `HttpOnly`, `Secure`, `SameSite`, ámbito de ruta y dominio mínimo.
- Redirecciones: destino validado contra allowlist; nunca `return_to` arbitrario.

## Secretos y criptografía

- Sin secretos en código, tests, imágenes, logs ni variables de build públicas. Usa gestor de secretos o entorno inyectado.
- Un secreto expuesto se rota. Retirarlo del historial no lo invalida.
- Algoritmos actuales: AES-GCM o ChaCha20-Poly1305 para cifrado autenticado; SHA-256 o superior para integridad; RSA ≥ 3072 o ECDSA/Ed25519 para firmas.
- IV/nonce único por operación; nunca reutilices nonce en modo contador.
- Compara en tiempo constante; no inventes construcciones criptográficas.
- TLS verificado por defecto; no desactives la verificación para «que funcione».

## Exposición de datos

- Devuelve solo los campos que el consumidor necesita. No serialices la entidad completa.
- Redacta secretos, tokens y datos personales en logs, trazas, errores y respuestas.
- Errores al usuario sin traza, consulta, ruta ni versión interna; detalle en el log con identificador de correlación.
- Datos en reposo cifrados cuando la clasificación lo exige; copias de seguridad con la misma protección.
- Retención y borrado definidos; no guardes más de lo necesario ni para siempre.
- En agentes y LLM, el contexto es una superficie de exposición: minimiza lo que se incluye.

## Deserialización y ficheros

- Evita deserialización nativa de datos no confiables (pickle, Java serialization, PHP unserialize, YAML unsafe).
- Usa formatos de datos sin ejecución y esquema con allowlist de campos y tipos.
- Subidas: valida tipo real, tamaño y nombre; guarda fuera del webroot; renombra; sirve con `Content-Disposition` y tipo seguro; nunca ejecutes lo subido.
- Rutas: canonicaliza y comprueba que el resultado queda dentro del directorio permitido; rechaza `..`, rutas absolutas y enlaces simbólicos.
- Extracción de archivos: evita zip slip y límites de expansión.

## Dependencias y cadena de suministro

- Fija versiones y usa lockfile; revisa actualizaciones antes de aplicarlas.
- Audita dependencias directas y transitivas con la herramienta del ecosistema.
- Revisa scripts de instalación, binarios precompilados y descargas en build.
- Verifica integridad (hash o firma) cuando el artefacto viene de fuera.
- No instales paquetes con nombre sospechosamente similar a uno popular (typosquatting).
- En CI, permisos mínimos del token, acciones fijadas por SHA y secretos fuera de logs.

## Errores, límites y concurrencia

- Falla cerrado: si la comprobación de permiso, la política o la auditoría falla, deniega.
- Sin trazas internas al cliente; con identificador para correlación.
- Timeouts en toda llamada externa; límite de tamaño y de profundidad.
- Rate limit por usuario, IP y operación sensible; protección contra denegación de cartera.
- Operaciones de dinero, cupones, stock y aprobaciones: atómicas y con control de idempotencia.
- Revisa carreras TOCTOU entre comprobar y usar; usa transacción o bloqueo.
- Reintentos con backoff y sin duplicar efectos.

## Configuración y despliegue

- Depuración desactivada en producción; sin consola de administración expuesta.
- Permisos de fichero mínimos; proceso sin root; contenedor sin privilegios y con sistema de ficheros de solo lectura cuando se pueda.
- Secretos por entorno o gestor, nunca en la imagen.
- Cabeceras de seguridad: HSTS solo con TLS estable, `X-Content-Type-Options`, `Referrer-Policy`, CSP.
- Backups probados y con acceso restringido.
- Logs con retención y acceso limitados; sin datos sensibles en claro.

## Cómo informar un hallazgo

```text
ID: SEC-001
Severidad: <crítica | alta | media | baja | informativa>
Categoría: <autorización | inyección | secretos | ...>
Ubicación: <ruta:línea o componente>
Entrada: <qué controla el atacante>
Traza: <entrada → transformación → efecto>
Impacto: <qué activo y cuánto>
Control ausente: <qué debería impedirlo y dónde>
Corrección propuesta: <cambio mínimo>
Evidencia: <prueba o reproducción sintética>
Supuestos: <los que sostienen la severidad>
```

Sin traza, el hallazgo es una observación. Sin ubicación y evidencia, no es reproducible.
