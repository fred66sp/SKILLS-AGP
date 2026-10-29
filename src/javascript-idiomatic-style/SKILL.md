---
name: javascript-idiomatic-style
description: "Escribe y revisa JavaScript vanilla mantenible para navegador y Node: declara los dos baselines del motor antes de elegir sintaxis, prefiere la construcción que rechaza a la que convierte, modela la asincronía con rechazos observados, resuelve módulos ESM y CJS, construye DOM sin innerHTML con datos externos y mantiene números, errores y dependencias bajo control. Úsala al crear, refactorizar o revisar .js, .mjs o .cjs sin tipos, al decidir qué parte del código es compartida entre navegador y Node, o al escribir un script o una CLI sin framework. No la uses para TypeScript ni JSX, para frameworks de interfaz, para escribir o ejecutar pruebas, ni para calidad visual y CSS."
metadata:
  version: "0.1.1"
---

# Estilo y diseño idiomático en JavaScript

JavaScript falla continuando: una comparación convierte, una propiedad ausente es `undefined`, una promesa rechazada sin observador solo deja un aviso. El trabajo de esta skill es que el fallo aparezca en el punto más temprano donde pueda verse, y que el código se lea igual seis meses después.

Esta skill posee el lenguaje, la forma de los módulos, la asincronía, el DOM y el runtime de Node. La elección de capa de prueba, los dobles y la puerta determinista son de `javascript-testing-and-verification`.

## Invariantes de estilo JavaScript

1. Declara los dos baselines antes de escribir: el del navegador (`browserslist`, `target` del bundler, Baseline) y el de Node (`engines`, `.nvmrc`, matriz de CI). Una edición ECMAScript no es una promesa de disponibilidad; la feature se comprueba contra el motor concreto.
2. El código que corre en ambos objetivos vive en la intersección de los dos baselines. Lo que solo existe en un lado va detrás de un adaptador nombrado, nunca detrás de `typeof window !== "undefined"` repartido por el dominio.
3. `===` y `!==` siempre. La única excepción es `value == null`, que cubre `null` y `undefined` juntos.
4. `??` para valores ausentes. `||` solo cuando `0`, `""` y `false` significan de verdad «no hay valor». `??` no se mezcla con `||` ni con `&&` sin paréntesis.
5. `?.` donde la ausencia es esperada, no para tapar un bug. Si el dato debe existir, falla al acceder en lugar de propagar `undefined` tres marcos más abajo.
6. Nunca `var`. `const` por defecto; `let` solo cuando el binding cambia. Declara en el primer uso, no al principio de la función.
7. Convierte números con `Number()`, no con `parseInt()`: `parseInt("1e3")` es `1`. No pases `parseInt` como callback, porque `map` le entrega el índice como radix.
8. El dinero no se calcula en coma flotante: unidades enteras en la menor denominación y formato con `Intl.NumberFormat`.
9. `Number.isNaN` para comprobar `NaN`; `Object.is` solo para `NaN` y `-0`.
10. Una función hace una cosa y se lee de arriba abajo: guardas primero, camino feliz sin indentar. `function` con nombre en el módulo, flecha para callbacks. Nunca flecha como método de objeto ni en un prototipo.
11. Un valor que representa un estado no se muta desde fuera. Copia con `structuredClone` cuando el valor lo permita; no escribas un clon profundo a mano.
12. Itera con `for...of` cuando haya `await`, `break` o `return`; con `map` o `filter` cuando transformes; `forEach` no espera promesas y no se usa para efectos asíncronos.
13. Toda promesa tiene un consumidor de sus rechazos: `try/catch` en `async`, `.catch()` en la cadena, o un manejador global que registra y falla. El manejador global es una red, no una estrategia.
14. La asincronía cancelable recibe un `AbortSignal` y lo propaga; `AbortSignal.timeout` fija un plazo. No dejes `fetch` ni un stream sin señal cuando la operación puede abandonarse.
15. Un módulo, un sistema: ESM o CJS según el paquete, sin mezclar en el mismo archivo. `node:` delante de los builtins. En ESM, `import` es estático y hoisteado; `import()` es la vía dinámica.
16. El DOM se construye con nodos y texto: `createElement`, `textContent`, `append`, `template`. `innerHTML` con dato externo es una inyección; `insertAdjacentText` para texto y un saneador solo si el proyecto ya lo tiene.
17. Un listener se registra con su ciclo de vida: `{ once, passive, signal }`, y `AbortController` para retirarlo. Toda suscripción, observer o intervalo se limpia donde se creó.
18. El proceso no se mata a la ligera: `process.exitCode` y salida ordenada; `stdout` para el resultado y `stderr` para el diagnóstico. Una CLI sin framework se parsea con `node:util` `parseArgs`.
19. La dependencia se justifica: primero el lenguaje y la plataforma (`Intl`, `URL`, `structuredClone`, `AbortController`, `fetch`), después una dependencia revisada. No añadas bundler ni framework a un script que el navegador ejecuta tal cual.
20. Respeta la convención del proyecto cuando exista. No reformatees código ajeno ni mezcles una refactorización con un cambio de comportamiento.

## Procedimiento de estilo JavaScript

**Paso 1: Inspeccionar antes de escribir.**
1. Lee `package.json` (`type`, `engines`, `exports`), `browserslist`, `.nvmrc`, la matriz de CI y el gestor si lo hay.
2. Localiza el runner de pruebas, el linter y el script de build; no los sustituyas.
3. Comprueba la sintaxis de partida con `node --check` o con el script del proyecto.
4. Revisa los patrones vecinos: módulos, errores, DOM y nombres. Una regla escrita gana.

**Paso 2: Fijar el baseline y el reparto.**
1. Escribe el baseline de cada objetivo y su intersección.
2. Decide qué módulos son compartidos, cuáles de navegador y cuáles de Node; nombra el adaptador de cada frontera.
3. Marca las fronteras por las que entra dato no confiable: `fetch`, formulario, `localStorage`, `argv`, `env` o fichero. Se validan antes de usarse.
4. Si el proyecto es TypeScript o usa JSX, detente: esa materia es de las skills de TypeScript.

**Paso 3: Modelar datos y estados.**
1. Nombra los estados del dominio; si dos no pueden coexistir, sepáralos con un campo literal y una rama exhaustiva.
2. Decide qué valores son identificadores, cuáles cantidades y cuáles contenido libre. Sin tipos, el nombre y el constructor son el contrato.
3. Define un error propio cuando el consumidor deba distinguirlo: conserva `Error` como base y usa `cause`.

**Paso 4: Escribir.**
1. Contratos antes de cuerpos: parámetros, retorno, errores y cancelación.
2. Guardas primero; devuelve pronto en lugar de anidar.
3. Aplica la referencia que corresponda: lenguaje, asincronía y módulos, navegador o Node.
4. Si una feature no está en el baseline, sustitúyela; no la envuelvas en un polyfill que nadie pidió.

**Paso 5: Verificar.**
1. `node --check` sobre cada archivo tocado.
2. El linter del proyecto, sin desactivar reglas para que pase.
3. Si el código toca el DOM, ábrelo en el navegador; si toca Node, ejecútalo con los argumentos y variables reales.
4. Las pruebas son de `javascript-testing-and-verification`: si no existen, dilo en el resultado en lugar de suplirlas.

**Paso 6: Revisar el diff.**
1. Busca `var`, `==`, `innerHTML`, `eval`, `new Function`, `document.write`, `process.exit(` y `console.log` de producción, además de supresiones nuevas.
2. Comprueba que no has añadido dependencias, capas ni abstracciones que nadie pidió.
3. Cierra con el bloque de resultado.

## Errores y paradas de estilo JavaScript

- Si el proyecto es TypeScript, no conviertas `.ts` a `.js` ni dupliques la lógica: pasa a `typescript-idiomatic-style`.
- Si aparece un framework de interfaz —React, Vue, Svelte, Angular—, no apliques este contrato al componente: queda fuera de alcance.
- Si el baseline no admite la feature y se quiere igual, expón la alternativa para ese motor; no la escribas a ciegas.
- Si el código compartido necesita `node:fs` o `document`, la frontera está mal trazada: mueve la dependencia a un adaptador.
- Si el proyecto mezcla ESM y CJS, no lo unifiques dentro de un cambio funcional; propón la migración aparte.
- Si el dato viene de fuera y no hay validación, no la improvises con un `if` suelto: es una frontera de la skill de verificación.
- Si el build exige un bundler, úsalo; no lo elimines para «volver a vanilla» sin encargo.

## Resultado de estilo JavaScript

```text
Objetivo: <navegador | node | ambos>
Baselines: <browserslist o Baseline declarado · engines o versión de node declarada>
Módulos: <qué se escribió, qué quedó compartido y qué adaptador se añadió>
Decisiones de lenguaje: <igualdad, números, errores, async, DOM o CLI>
Comprobaciones: <node --check, linter, ejecución manual o "ninguna">
Pruebas: <de la skill de verificación, o "no ejecutadas">
Deuda y límites: <lo que queda fuera, con motivo>
```

## Referencias del paquete de estilo

- [language-rules](references/language-rules.md): declaraciones, igualdad, números, funciones, objetos, iteración, clases, expresiones regulares y nombres. Léela en los pasos 2 y 3.
- [async-and-modules](references/async-and-modules.md): promesas, `async/await`, cancelación, orden del event loop, ESM y CJS. Léela en el paso 4.
- [browser-apis](references/browser-apis.md): DOM seguro, eventos, `fetch`, formularios, almacenamiento, Workers y observers. Léela en el paso 4 cuando el código corra en navegador.
- [node-apis](references/node-apis.md): builtins `node:`, ficheros, streams, `argv`, `env`, señales y CLI sin dependencias. Léela en el paso 4 cuando el código corra en Node.
- [engine-baseline](references/engine-baseline.md): cómo se leen y concilian los dos baselines y cómo se comprueba una feature. Léela en los pasos 1 y 2.

Este paquete no incluye `scripts/`: la comprobación es `node --check`, el linter del proyecto y la ejecución real. La puerta determinista vive en `javascript-testing-and-verification`.
