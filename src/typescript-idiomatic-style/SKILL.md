---
name: typescript-idiomatic-style
description: "Diseña y escribe TypeScript idiomático y type-first para librerías, servicios y CLIs: tsconfig estricto, uniones discriminadas, tipos branded, type guards, genéricos, tipos condicionales y mapeados, operador satisfies, objetos const en lugar de enum, módulos y exports, referencias de proyecto solo cuando el build lo exige, y reglas de CLI con citty y @clack/prompts. Úsala cuando haya que crear, refactorizar o revisar tipos, APIs y código TypeScript, elegir estructura de módulos o dependencias, o construir una CLI de TypeScript. No la uses para validación de datos en runtime, pruebas ni gates de CI, que tienen su propia skill."
---

# Estilo y diseño idiomático en TypeScript

Escribe TypeScript que haga imposibles los estados inválidos y que un lector pueda mantener sin reconstruir la intención. El sistema de tipos es una herramienta de diseño, no un adorno que se satisface con `as`.

Esta skill posee los tipos, la estructura de módulos, las dependencias y la forma de una CLI de TypeScript. La validación de datos en runtime, las pruebas y la puerta de verificación son de `typescript-testing-and-verification`.

## Invariantes de estilo TypeScript

1. `strict` es el punto de partida, no una opción. Activa además `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `noImplicitOverride` e `isolatedModules` cuando el proyecto pueda asumirlos. No debilites una regla para que pase un cambio.
2. Modela primero los estados que el programa puede ocupar. Una unión discriminada con un campo literal es preferible a varios booleanos que permiten combinaciones imposibles.
3. Usa `unknown` en toda frontera y estrecha con type guards. `any` solo se acepta con una justificación escrita en la misma línea o encima; nunca se propaga a la API pública.
4. Un `as` no valida nada: solo cambia lo que el compilador acepta. Si el valor viene de fuera, se parsea; si el tipo es incorrecto, se corrige.
5. Los identificadores de dominio se modelan con tipos branded y se construyen en un único punto. No se usa `string` desnudo para dos conceptos que no deben mezclarse.
6. Usa `satisfies` para comprobar que un literal cumple una forma sin perder su tipo concreto. Usa `as const` para tablas y constantes; no uses `enum`.
7. Los genéricos existen cuando hay al menos dos instancias reales o una relación entre entradas y salidas. Si no, escribe el tipo concreto.
8. Los tipos condicionales, mapeados y de plantilla se justifican por una necesidad de la API. Si un tipo con nombre y un comentario lo explican mejor, gana el tipo con nombre.
9. Todo type guard devuelve `value is T` y comprueba lo mismo que afirma. Un assertion function solo se usa cuando su fallo siempre lanza y el contrato lo dice.
10. Un `switch` sobre una unión discriminada termina con una comprobación `never` para que añadir una variante rompa la compilación.
11. Las funciones exportadas declaran su tipo de retorno. Los locales lo infieren. La inferencia no se fuerza con anotaciones redundantes.
12. Los imports de tipos usan `import type`; los valores y los tipos no se mezclan en el mismo import si el proyecto separa ambos. Respeta `verbatimModuleSyntax` cuando exista.
13. La estructura mínima gana. Un paquete y un `tsconfig` bastan hasta que el tamaño o el build demuestren lo contrario. No crees monorepo, `packages/` ni project references por anticipación.
14. Las project references, la compilación incremental y el tree shaking se añaden después de medir un problema de build, no como plantilla.
15. Una librería publicada declara `declaration`, `declarationMap` y un `exports` explícito; no filtra tipos internos ni rutas de `src/`.
16. Las dependencias se justifican: primero Node y la biblioteca estándar, después una dependencia revisada en licencia, mantenimiento y seguridad. Un único gestor de paquetes y un único lockfile.
17. Respeta la convención del proyecto cuando exista. No reformatees código ajeno ni mezcles una refactorización con un cambio de comportamiento.

## Procedimiento de estilo TypeScript

**Paso 1 — Inspeccionar antes de escribir.**
1. Lee `package.json`, `tsconfig.json`, la versión de TypeScript y el gestor de paquetes. Localiza el runner de pruebas, el linter y el script de build.
2. Ejecuta el typecheck existente para conocer el estado de partida: `tsc --noEmit` o el script `typecheck` del proyecto.
3. Revisa los tipos y patrones vecinos: uniones, guards, errores, exports y estructura de carpetas. Si hay una regla escrita, prevalece.

**Paso 2 — Modelar los estados.**
1. Escribe una frase por estado del dominio y otra por transición. Si dos estados pueden coexistir y no deberían, faltan uniones discriminadas.
2. Decide qué valores son identificadores, qué valores son cantidades y qué valores son contenido libre. Crea tipos branded solo para los dos primeros.
3. Decide dónde entra el dato externo. Ese punto es una frontera y no se resuelve con un `as`: se valida con la skill de verificación.

**Paso 3 — Escribir los tipos y la implementación.**
1. Define las uniones y sus campos literales. Añade guards que devuelvan `value is T` y una función de renderizado o transición exhaustiva.
2. Escribe las firmas públicas antes del cuerpo. Usa `satisfies` para tablas de configuración y `as const` para constantes.
3. Usa genéricos solo donde la relación entre parámetros y retorno sea real. Comprueba los límites con una prueba de tipos cuando el tipo sea público y no trivial.
4. Si un tipo condicional o mapeado no cabe en una línea legible, párate: probablemente la API necesita un tipo con nombre.

**Paso 4 — Resolver módulos y exports.**
1. Mantén el módulo de dominio separado del adaptador (HTTP, CLI, base de datos). Si el proyecto es pequeño, un solo paquete sigue siendo válido.
2. Evita ciclos. Un barrel `index.ts` solo existe para la API pública del paquete, no para cada carpeta.
3. En una librería, revisa `exports`, `types` y `files`; comprueba que el consumidor no necesita importar desde `src/` ni desde una ruta interna.
4. Añade project references o compilación incremental solo con una medición que muestre el problema y su mejora.

**Paso 5 — Construir la CLI, si la hay.**
1. Lee `references/cli-rules.md` antes de elegir la estructura de comandos.
2. Cada comando exporta `defineCommand()`; los subcomandos se cargan de forma perezosa. No añadas un parser alternativo.
3. Los prompts comprueban `isCancel()` después de cada llamada. Toda operación destructiva exige confirmación explícita y admite modo no interactivo.
4. La salida legible va a `stdout`, el diagnóstico a `stderr` y el código de salida distingue éxito, uso incorrecto y fallo.
5. La completitud de pestañas se activa solo en el proceso de completion; nunca en el arranque normal.
6. Verifica con `--help` que todos los comandos y flags están registrados antes de cerrar.

**Paso 6 — Comprobar el diff.**
1. Ejecuta el typecheck del proyecto y el linter si existe. Un cambio de tipos que rompe la compilación no es un cambio de tipos.
2. Busca `any`, `as`, `enum`, `@ts-ignore` y supresiones nuevas. Cada una necesita una razón o se elimina.
3. Comprueba que no has añadido abstracciones, genéricos, dependencias ni capas que nadie pidió.
4. Cierra con el bloque de resultado.

## Errores y paradas de estilo TypeScript

- Si el proyecto no usa `strict`, no lo actives dentro de un cambio funcional. Propón la migración aparte y demuestra el coste.
- Si una dependencia no expone tipos utilizables, aísla el `any` en un adaptador y documenta el límite; no lo extiendas por el dominio.
- Si el error está en los tipos de un paquete externo, no parchees `node_modules`. Actualiza, usa un wrapper tipado o declara el bloqueo.
- Si el build se vuelve lento, mide antes de añadir project references. No conviertas una optimización no medida en deuda estructural.
- Si el usuario pide una abstracción genérica sin dos usos reales, entrega la versión concreta y explica en una línea qué la haría merecer la abstracción.
- Si la CLI necesita un framework que el proyecto no tiene, no lo añadas sin justificar la dependencia y su coste de mantenimiento.
- Si el dato entra por HTTP, formulario, entorno o API de terceros, no lo valides con un type guard: pasa a `typescript-testing-and-verification`.
- Si una regla de este contrato choca con una convención escrita del proyecto, gana la convención cuando no contradiga el lenguaje.

## Resultado de estilo TypeScript

```text
Estado: completado | parcial | bloqueado
Módulos tocados: <lista con su responsabilidad>
Decisiones de tipos: <uniones, branded, genéricos, satisfies>
Decisiones de estructura: <módulos, exports, project references>
CLI: <comandos, prompts, completion, o "no aplica">
Comprobaciones: <tsc --noEmit, lint, build>
Deuda declarada: <lista, o "ninguna">
No verificado: <lista, o "ninguno">
```

## Referencias de estilo TypeScript

- [type-rules](references/type-rules.md) — tablas de decisión para `tsconfig`, `unknown`, uniones, branded, guards, genéricos, condicionales, módulos, exports y dependencias. Léela en los pasos 2 a 4 cuando una regla no sea evidente.
- [cli-rules](references/cli-rules.md) — contrato de una CLI de TypeScript con citty, `@clack/prompts`, completion, salida y empaquetado. Léela en el paso 5.
