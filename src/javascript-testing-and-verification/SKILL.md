---
name: javascript-testing-and-verification
description: "Demuestra el comportamiento del JavaScript vanilla sin añadir un framework: elige la capa de prueba más pequeña, escribe pruebas con node:test y node:assert/strict, prueba DOM y eventos en una página de navegador o con el entorno que el proyecto ya tenga, simula red, almacenamiento y reloj, prueba el proceso con argv, env y stdin controlados, y cierra con la puerta scripts/verify-js.py, que comprueba sintaxis, ejecuta el script test del proyecto o node --test e informa del baseline de Node. Úsala al escribir o revisar pruebas, validar una frontera no confiable, comprobar una regresión o declarar un cambio terminado. No la uses para estilo, módulos, diseño de DOM ni arquitectura, que son de javascript-idiomatic-style."
metadata:
  version: "0.1.1"
---

# Pruebas y verificación en JavaScript

En JavaScript no hay compilador que diga la verdad: la única evidencia es lo que se ejecuta. Una prueba existe para aumentar la confianza en el comportamiento que importa, no para llenar un porcentaje ni para demostrar que un mock devuelve lo que se le programó.

Esta skill posee la elección de capa, las pruebas, los dobles, el determinismo y la puerta de verificación. El lenguaje, los módulos, la forma del DOM y del runtime son de `javascript-idiomatic-style`.

## Invariantes de verificación JavaScript

1. Prueba comportamiento observable, no detalles de implementación. Si renombrar una función privada rompe el test, el test estaba mal situado.
2. Elige la capa más pequeña que demuestre el comportamiento: función pura en `node:test`, DOM en un navegador, proceso en una ejecución con `argv` y `stdin` controlados, integración real solo cuando la frontera es el riesgo.
3. Usa el runner que el proyecto ya tenga. Si no hay ninguno, `node:test` y el navegador bastan: no añadas Vitest, Jest ni jsdom para probar un módulo pequeño.
4. Un archivo por módulo, junto a él: `x.js` con `x.test.js`. El runner lo descubre sin configuración.
5. Cada test comprueba una razón para fallar y se lee como una frase del comportamiento, no del nombre de una función interna.
6. Ante un fallo, la salida muestra la entrada, lo obtenido y lo esperado. Un `assert(false)` sin mensaje no es una prueba.
7. Nada de red real, reloj real, aleatoriedad ni `sleep` para sincronizar. Se inyecta o se sustituye la frontera.
8. Un `fetch` simulado declara `ok`, `status` y cuerpo; se prueban el error HTTP y el JSON inválido, no solo el camino feliz.
9. En asincronía se espera el evento que señala el final, no un tiempo. El reloj se controla con temporizadores simulados.
10. El DOM se prueba con nodos reales en un navegador. Una página de pruebas sin dependencias es una capa válida, no un apaño.
11. En Node, cuando el contrato es la CLI, se ejecuta el proceso: no se importa su `main` interno para comprobar una flag.
12. `stdout`, `stderr` y código de salida se comprueban por separado; el texto libre no se compara entero si depende del entorno.
13. Una prueba que no puede fallar no aporta nada. Comprueba que el caso negativo falla por la causa prevista.
14. Al corregir un defecto, primero se escribe la prueba que falla por la causa y después la corrección; la prueba queda como regresión.
15. La cobertura es una señal, no un objetivo. No escribas pruebas triviales para subir un número.
16. Un snapshot o golden file solo se usa con salida determinista, y se normalizan rutas, tiempos e identificadores.
17. No se simula el módulo que se está probando ni se prueba el doble en lugar del código.
18. Cada test deja el entorno como lo encontró: temporales, listeners, temporizadores y servidores se cierran.
19. La puerta se ejecuta y se muestra: `scripts/verify-js.py` o los scripts equivalentes del proyecto. Un check no disponible se declara, no se omite.
20. No declares un cambio terminado sin mostrar los comandos ejecutados y su resultado.

## Procedimiento de verificación JavaScript

**Paso 1 — Mapear riesgos y capas.**
1. Enumera lo que el usuario o el agente observan: valores devueltos, texto en pantalla, salida de consola, ficheros, códigos de salida.
2. Marca las fronteras por las que entra dato no confiable: `fetch`, formulario, `localStorage`, `argv`, `env`, fichero.
3. Marca los riesgos: datos que se destruyen, secretos que se filtran, cancelación, compatibilidad del contrato.
4. Descarta las comprobaciones que no añaden confianza; la capa se elige, no se acumula.

**Paso 2 — Elegir capa y runner.**
1. Lee `references/test-layers.md` para la tabla de capas y el criterio de descarte.
2. Comprueba qué runner tiene el proyecto: script `test`, configuración de Vitest o Jest, o ninguno.
3. Con Node, el descubrimiento de `node --test` basta. Con DOM, decide entre navegador real y el entorno que ya exista.
4. Si el runner elegido exige añadir una dependencia, es una decisión que se propone; no se toma dentro del cambio.

**Paso 3 — Escribir la prueba que falla por la razón correcta.**
1. Lee `references/node-tests.md` o `references/browser-tests.md` según la capa.
2. Escribe el caso mínimo: un comportamiento, una entrada, una comprobación con mensaje.
3. Comprueba que falla por la causa prevista antes de corregir el código, o que el caso negativo lo demuestra.
4. Añade los límites que importan: vacío, cero, `null`, cadena larga, error de red, cancelación.

**Paso 4 — Aislar y estabilizar.**
1. Sustituye red, reloj, aleatoriedad y almacenamiento por dobles controlados.
2. Espera eventos y promesas; nunca `sleep`.
3. Limpia temporales, listeners y temporizadores en `afterEach` o en el propio test.
4. Repite la suite dos veces para detectar dependencia de orden o de estado.

**Paso 5 — Ejecutar la puerta.**
La puerta ejecuta código del proyecto (`node --check` y los scripts del proyecto): ejecútala solo sobre un proyecto confiable o dentro de un contenedor o usuario sin privilegios.

1. `python3 <skill>/scripts/verify-js.py --root <raíz>` para la sintaxis; añade `--test` y `--lint` cuando el proyecto los tenga.
2. La puerta no sustituye al runner del proyecto: si hay script `test`, ese manda.
3. Si `node` no está disponible o el proyecto no tiene `package.json`, la puerta lo dice; no lo interpretes como éxito.

**Paso 6 — Cerrar con evidencia.**
1. Rellena `assets/verification-report.md` con los comandos y su resultado real.
2. Declara lo que no se comprobó y por qué: DOM sin navegador disponible, runner ausente, red no simulada.
3. Cierra con el bloque de resultado.

## Errores y paradas de verificación JavaScript

- Si el proyecto no tiene pruebas y nadie pidió escribirlas, no inventes una suite: informa y deja la decisión.
- Si el test necesita red real o un servicio externo, no lo escribas así: dobla la frontera o declara que no se puede probar.
- Si el DOM solo se puede probar añadiendo un DOM simulado, usa el navegador o declara el límite; no añadas la dependencia por tu cuenta.
- Si el proyecto tiene un runner, no lo sustituyas por `node:test` para «simplificar».
- Si una prueba es inestable, se corrige o se elimina con motivo; no se marca como omitida.
- Si el fallo está en el código y no en la prueba, no ajustes la expectativa para que pase.
- Si la puerta no puede ejecutarse en el entorno, dilo y entrega el resultado como incompleto.

## Resultado de verificación JavaScript

```text
Objetivo verificado: <comportamiento observable>
Capas: <node:test | navegador | runner del proyecto | ninguna y por qué>
Pruebas: <archivos y número de casos; qué cubre cada uno>
Determinismo: <red, reloj y estado controlado, o límite declarado>
Puerta: <verify-js.py con sus checks y resultado, o "no ejecutada" con motivo>
No verificado: <lo que queda fuera, con motivo>
```

## Referencias del paquete de verificación

- [test-layers](references/test-layers.md) — mapa de riesgo, capas, criterio de descarte, determinismo y datos de prueba. Léela en los pasos 1 y 2.
- [node-tests](references/node-tests.md) — `node:test`, `assert/strict`, hooks, dobles, proceso y diagnóstico. Léela en el paso 3 cuando la capa sea Node.
- [browser-tests](references/browser-tests.md) — runner en una página, eventos, red, almacenamiento, esperas y límites. Léela en el paso 3 cuando la capa sea el navegador.
- [test-runner](assets/test-runner.html) — página de pruebas sin dependencias; cópiala en el proyecto y sustituye los casos.
- [verification-report](assets/verification-report.md) — plantilla del cierre con comandos y resultados.

## Puerta del paquete de verificación

`scripts/verify-js.py` es la herramienta determinista. No reescribas su lógica a mano.

```bash
# Sintaxis de todo el proyecto
python3 <skill>/scripts/verify-js.py --root .

# Sintaxis, pruebas y linter del proyecto
python3 <skill>/scripts/verify-js.py --root . --test --lint

# Resultado para una máquina
python3 <skill>/scripts/verify-js.py --root . --test --json
```

La comprobación de sintaxis siempre se ejecuta; `--test` y `--lint` se añaden cuando el proyecto los tenga. Códigos de salida: `0` todo lo ejecutado pasa, `1` alguna comprobación falla, `2` error de uso o entorno. `--json` devuelve `ok`, la versión de node detectada, la declarada en `engines`, las notas y el resultado de cada check.
