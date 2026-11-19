# Diseño de pruebas

Qué probar y con qué ángulo. Este documento cubre niveles, tipos, técnicas de diseño y la priorización por riesgo que elige el conjunto mínimo suficiente. El proceso de la ronda está en [process](process.md); la forma del caso y del informe, en las plantillas del paquete.

## Niveles

| Nivel | Qué contrasta | Quién lo escribe | Señal típica de fallo |
|---|---|---|---|
| Unitaria | Una unidad aislada con sus colaboradores doblados | Quien implementa | El caso rojo apunta a la línea |
| Integración | Contratos entre piezas reales | Quien implementa o quien prueba | El aislado pasa y el conjunto no |
| Sistema | La necesidad completa sobre el producto montado | Quien prueba | El flujo de usuario se rompe |
| Aceptación | Que la necesidad se resuelve, con datos reales o equivalentes | Quien encarga | «Esto no resuelve lo que pedí» |

- El nivel se elige por dónde vive el riesgo, no por costumbre. Un riesgo de contrato se ve en integración; uno de percepción, en sistema o aceptación.
- Un defecto visto en un nivel alto con causa en uno bajo no se parchea en el alto: baja a la capa que le toca y ahí se cierra con su prueba.

## Tipos

- **Funcionales:** qué hace el sistema. Las técnicas de abajo sirven aquí casi siempre.
- **No funcionales:** cómo lo hace. Rendimiento, límites de carga, accesibilidad, consumo. Cada tipo exige su método de medida; declarar el método es parte del caso.
- **Regresión:** lo que ya funcionaba. La suite del proyecto es la dueña; una ronda añade ángulos, no repite la suite entera a mano.
- **Humo:** la ruta crítica mínima para saber si merece seguir probando. Barato y primero.

## Técnicas de diseño

Cada técnica es un ángulo. Un caso sin técnica declarada suele ser un duplicado de otro.

### Partición de equivalencia

Divide las entradas en clases que el sistema debería tratar igual y elige un representante por clase. Dos casos de la misma clase prueban lo mismo; quita uno.

- Ejemplo: un campo de edad entre 18 y 99 tiene clases: menor de 18, válido, mayor de 99, no numérico, vacío.

### Valores límite

Los defectos se acumulan en las fronteras. Para cada clase con borde, prueba el borde, el borde más uno y el borde menos uno.

- Ejemplo: para 18, prueba 17, 18 y 19. Para longitud máxima 255, prueba 254, 255 y 256.

### Tabla de decisión

Cuando el resultado depende de combinaciones de condiciones, enumera las combinaciones y el resultado de cada una. Cada columna es un caso.

- Ejemplo: alta con correo válido o no, contraseñas iguales o no: la combinación con ambos datos inválidos es la que casi nadie prueba.

### Transición de estados

Cuando el comportamiento depende del estado previo, dibuja los estados y las transiciones válidas; prueba cada transición y las inválidas.

- Ejemplo: una suscripción activa que se cancela, se renueva y se reactiva. La reactivación tras expiración es la transición que falla.

### Exploratorio dirigido

Sin guion previo, con objetivo y tiempo límite. Sirve para encontrar lo que las particiones no vieron; el hallazgo que sobrevive se convierte en caso escrito.

- Regla: sesiones cortas, objetivo declarado, notas de lo recorrido. Sin notas no es prueba, es paseo.

## Cuando la misma fuente escribe el código y los casos

Quien diseña los casos hereda los puntos ciegos de quien escribió el código: la suite sale en verde, la cobertura luce y el defecto sobrevive dentro de la correlación. Es el pesticida en su forma más grave: no que la suite repite ángulos, sino que el diseñador y el autor comparten el mismo mapa mental. Cuando el autor del código y el de los casos son la misma fuente —una persona sola o un agente que hace ambos—, añade al menos un ángulo ajeno al autor. Las técnicas, cada una con su cuándo y su cuándo no:

### Revisión adversarial

Otra fuente, en contexto nuevo y sin ver la conversación ni el diseño, recibe solo el código y el objetivo con una sola misión: encontrar lo que está roto o sin probar. No se le pide aprobar: un revisor al que invitas a aprobar, aprueba. Cada hallazgo llega con evidencia, gravedad y confianza, y un juez lo acepta o lo rechaza con su motivo: quien solo busca fallos siempre encuentra alguno, y sin juez se persiguen falsos positivos.

- Cuándo: en todo cambio que ha escrito un agente, sobre todo si toca dinero, permisos, seguridad o validación de datos; y siempre que la misma fuente haya escrito el código y sus casos.
- Cuándo no: en cambios triviales o prototipos que se van a tirar; y sin juez que filtre, no compensa.

### Propiedad (property-based)

En vez de ejemplos elegidos, una regla que se cumple para cualquier entrada —«el resultado ordenado no descarta elementos», «cifrar y descifrar devuelve el original»— y un generador que inventa cientos de casos para romperla, reduciendo el contraejemplo al mínimo. Los ejemplos prueban lo que el diseñador imaginó; la propiedad, lo que no se le ocurrió.

- Cuándo: ida y vuelta (serializar y leer, comprimir y descomprimir), validaciones y parsers (toda entrada rara da un error controlado, nunca un fallo), cálculos con límites (precios, descuentos, rangos, fechas), algoritmos (ordenar, buscar, deduplicar) y migraciones donde la versión nueva debe coincidir con la vieja.
- Cuándo no: en código pegamento, en la interfaz, o cuando la regla hay que forzarla: sin regla real, vuelve a los ejemplos.

### Fuzzing

Entradas masivas, raras o medio rotas, sin regla que comprobar: solo que el programa no rompa ni se cuelgue. En su forma guiada por cobertura, el fuzzer mira qué ramas aún no ha visitado y dirige las entradas hacia ellas. En aplicaciones comunes, un generador de propiedades lanzando datos basura contra la API ya cubre casi todo el valor; el fuzzer guiado brilla en parsers y en lenguajes donde un fallo de memoria es grave.

- Cuándo: código que recibe datos de fuera que no controlas: parsers, decodificadores de archivos, protocolos de red, entrada de usuario.
- Cuándo no: montar un fuzzer guiado en una aplicación CRUD corriente: con entradas aleatorias basta.

### Mutación

Ataca los casos, no el código: introduce errores pequeños uno a uno —cambiar `>=` por `>`— y comprueba si algún caso falla. El mutante que sobrevive señala un caso que pasa sin contrastar nada. Complementa la cobertura honesta: la cobertura de código dice qué se ejecutó; la puntuación de mutación, qué se contrastó.

- Cuándo: lógica crítica ya cubierta —dinero, permisos, validaciones— y suites cuya cobertura sale sospechosamente alta después de escribirlas un agente. Solo sobre el código que cambió: correr la suite entera cientos de veces no escala.
- Cuándo no: en el proyecto entero de una vez, en código sin casos todavía o en código pegamento. No hace falta matar todos los mutantes: algunos son equivalentes y no se pueden matar.

### Diferencial y metamórfico

Cuando no hay oráculo único. Diferencial: versión vieja y versión nueva con las mismas entradas deben coincidir; no hace falta saber la respuesta correcta, solo que las dos digan lo mismo. Metamórfico: relaciones entre salidas cuando la respuesta correcta no se conoce —«buscar con un filtro más no devuelve más resultados»—; el terreno natural de los sistemas con IA.

- Cuándo: migraciones y reescrituras grandes, refactors con referencia viva, cambios de proveedor o de modelo (diferencial); buscadores, recomendadores y productos con un modelo dentro (metamórfico).
- Cuándo no: cuando sí se conoce la respuesta exacta: un caso normal es más claro y más directo.

## Prioridad por riesgo

La prioridad decide el orden, no la cantidad: si el presupuesto se acaba, lo de baja prioridad queda fuera y se escribe en la cobertura.

1. **Impacto:** qué rompe si el defecto existe. Datos de usuarios, dinero, seguridad y disponibilidad van arriba.
2. **Probabilidad:** dónde falla más. Módulos complejos, cambios recientes, código con defectos abiertos, áreas mal entendidas.
3. **Matriz:** impacto alto con probabilidad alta es primero; impacto bajo con probabilidad baja no entra esta ronda, se declara excluido.

## Cobertura honesta

- La cobertura se declara como lo que sí se probó y lo que no: «probado X, no probado Y por Z». Sin la segunda mitad, la primera engaña.
- Un porcentaje de cobertura de código dice qué se ejecutó, no qué se contrastó. No lo uses como medida de calidad de la ronda.
- Las exclusiones son decisiones: se escriben con su motivo en el alcance del informe, no en la memoria de quien probó.
