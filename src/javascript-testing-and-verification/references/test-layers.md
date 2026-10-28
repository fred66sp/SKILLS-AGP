# Capas de prueba

Léela en los pasos 1 y 2, al decidir qué se prueba y en qué capa.

## 1. Mapa de riesgo

Antes de escribir, responde estas cuatro preguntas y anota la respuesta:

| Pregunta | Qué produce |
|---|---|
| ¿Qué observa quien usa esto? | La lista de comportamientos que merecen prueba |
| ¿Por dónde entra dato que no controlas? | Las fronteras que se doblan o se validan |
| ¿Qué se destruye o se filtra si falla? | Los casos que no se pueden omitir |
| ¿Qué cambia con frecuencia? | Dónde una prueba estabiliza y dónde estorba |

Una prueba vale por el fallo que detecta, no por la línea que cubre. Si no puedes nombrar el fallo que detectaría, sobra.

## 2. Capas y qué demuestra cada una

| Capa | Herramienta | Demuestra | No demuestra |
|---|---|---|---|
| Función pura | `node:test` + `assert/strict` | Cálculo, transformación y límites | Integración con el runtime ni DOM |
| Módulo con dependencias | `node:test` con dobles | Reparto de responsabilidades y errores | Que la frontera real responda así |
| DOM | Página de pruebas en un navegador | Nodos, eventos, foco y texto | Que el CSS se vea bien |
| Proceso o CLI | `node archivo.js --flag` | `stdout`, `stderr`, código de salida | Uso interactivo en una terminal real |
| Integración real | El runner del proyecto con servicios reales | El contrato completo, incluida la red | Nada más allá de lo ejercitado |
| Extremo a extremo | Navegador automatizado | El recorrido del usuario | El detalle de cada módulo |

Reglas de elección:

- La capa más pequeña que pueda fallar por la causa que temes.
- Una prueba de DOM no se sustituye por una de función: comprueban cosas distintas.
- Una prueba de proceso no se sustituye por importar una función interna cuando el contrato es la salida.
- La integración real se reserva para la frontera cuyo comportamiento no controlas.

## 3. Cuándo no escribir una prueba

- El valor es una constante o una reexportación sin lógica.
- La comprobación repetiría lo que ya afirma el runner o el lenguaje.
- El caso no puede fallar sin que falle otro que ya cubre la misma causa.
- La prueba necesitaría red real y el proyecto no tiene entorno para ello: primero el doble.
- Solo subiría la cobertura.

Cuando no se escribe, se declara en el informe con el motivo. Una ausencia explicada es información; una ausencia silenciosa es deuda.

## 4. Determinismo

| Fuente de azar | Qué se hace |
|---|---|
| Reloj | Temporizadores simulados o reloj inyectado |
| Fecha actual | Se pasa como parámetro o se fija en el test |
| Aleatoriedad | Generador inyectado con semilla fija |
| Red | `fetch` sustituido por una función que devuelve respuestas preparadas |
| Ficheros | Directorio temporal por test, creado y borrado en el propio test |
| Orden de tests | Cada test crea su estado; no comparte objetos mutables |
| Zona horaria y locale | Se fijan cuando el formato es parte del resultado |
| Identificadores generados | Se comprueba la forma, no el valor |

Una prueba que pasa sola y falla en la suite depende de estado compartido. Una que falla el lunes y pasa el martes depende del reloj o de la red.

## 5. Datos de prueba

- Un dato por caso, con el nombre que describe el caso: `pedidoSinLineas`, `precioCero`, `textoConEmoji`.
- Los fixtures viven junto a la prueba si son suyos; en `fixtures/` si los comparten varios archivos.
- Un fixture grande se recorta al mínimo que conserva el rasgo que se prueba.
- Los datos con fechas fijas se escriben completos; nunca se calculan a partir de hoy.
- Un dato inválido se construye a propósito, no se toma de la salida de un caso válido.

## 6. Cobertura y otras señales

- La cobertura indica qué no se ejecutó; no indica qué está bien probado.
- Una línea cubierta por una prueba que no comprueba nada sigue sin verificar.
- La mutación —cambiar el código y ver si la suite lo detecta— es una señal mejor, y se aplica a mano en los módulos críticos.
- Un umbral de cobertura en CI se acepta si ya existía; no se impone dentro de un cambio funcional.

## 7. Regresión

1. Reproduce el defecto con la prueba más pequeña que falle por su causa.
2. Comprueba que falla por esa causa y no por un error de la prueba.
3. Corrige el código, no la expectativa.
4. Deja la prueba en la suite: es la memoria del defecto.
5. Si el defecto venía de una frontera sin doble, añade el doble y el caso que faltaba.

Un defecto sin prueba deja abierta la misma puerta por la que entró.
