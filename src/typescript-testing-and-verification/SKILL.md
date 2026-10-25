---
name: typescript-testing-and-verification
description: "Diseña y ejecuta la verificación de código TypeScript: validación de todo dato externo en la frontera con Zod 4 y tipos inferidos, comprobación de tipos con tsc --noEmit, pruebas unitarias y de integración, pruebas de extremo a extremo de CLIs, determinismo, errores legibles, variables de entorno al arranque y la puerta de typecheck, lint, test y build con scripts/verify-ts.py. Úsala cuando haya que escribir o revisar pruebas, validar entradas no confiables, comprobar una regresión o declarar un cambio terminado. No la uses para diseño de tipos, estilo general ni arquitectura de la CLI, que tienen su propia skill."
metadata:
  version: "0.1.0"
---

# Validación y verificación en TypeScript

Una prueba existe para aumentar la confianza en el comportamiento que importa, no para llenar un porcentaje. En TypeScript hay dos verdades distintas que deben coincidir: lo que el compilador acepta y lo que el programa recibe en runtime. La verificación demuestra ambas.

Esta skill posee la validación en la frontera, las pruebas y la puerta de verificación. El diseño de tipos, la estructura y la CLI son de `typescript-idiomatic-style`.

## Invariantes de verificación TypeScript

1. Prueba comportamiento observable, no detalles de implementación. Si renombrar una función privada rompe el test, el test estaba mal situado.
2. Elige la capa más pequeña que demuestre el comportamiento: tipo para el contrato estático, esquema para la frontera, unitaria para lógica pura, integración para una frontera real y extremo a extremo para la CLI.
3. El typecheck es una puerta, no una prueba: `tsc --noEmit` con el `tsconfig` del proyecto. No debilites `strict` ni añadas supresiones para que pase.
4. Los tipos de TypeScript se borran en runtime. Todo dato externo se valida antes de usarlo; un `as` no es validación.
5. Usa el validador que el proyecto ya tenga. Si hay que elegir, Zod 4; no añadas un segundo validador ni dos versiones mayores de Zod.
6. El esquema es la fuente del tipo. Deriva con `z.infer` y `z.input`; no escribas a mano una interfaz duplicada que pueda divergir.
7. En handlers y flujos de usuario, `safeParse`; donde un dato inválido es un bug (configuración, invariante interna), `parse`. Cualquier refinamiento o transformación asíncrona exige `parseAsync`/`safeParseAsync`.
8. Define los esquemas una vez, en el ámbito del módulo. No los reconstruyas por petición. En rutas calientes, compila solo con una medición; mantén una sola copia de Zod en el árbol.
9. Valida `process.env` al arrancar y falla el proceso con un mensaje legible. No des un valor por defecto a un secreto obligatorio.
10. Traduce los errores a la forma que consume el receptor: campos para un formulario o un 400, árbol para objetos anidados, texto para logs y arranque. No devuelvas el input completo ni secretos.
11. Prueba cada esquema con entradas válidas, inválidas y límite: cadena vacía, `null`, claves extra, coerción y tipos incorrectos. Comprueba la forma del error, no solo que falle.
12. Escribe pruebas de comportamiento; usa tabla solo cuando todos los casos recorren el mismo camino. Cada fallo debe mostrar caso, entrada, `got` y `want`.
13. Nada de red real, servicios externos, reloj real ni `sleep` para sincronizar. Inyecta reloj, `fetch`, filesystem y aleatoriedad cuando el comportamiento lo necesite.
14. En una CLI, construye el binario una vez y ejecútalo con argumentos y `stdin` controlados. Comprueba por separado `stdout`, `stderr` y código de salida; no asumas TTY.
15. Cubre ayuda, versión, comando desconocido, flag desconocido, JSON válido, modo no interactivo, cancelación, `--dry-run` y falta de `--yes` cuando existan.
16. Los snapshots y golden files son deterministas: normaliza rutas, separadores, tiempos e identificadores. Un cambio de snapshot sin cambio de comportamiento explicado es una regresión, no una actualización.
17. La cobertura es una señal, no un objetivo. No escribas pruebas triviales para subir un número.
18. Al corregir un defecto, escribe primero una prueba que falle por la causa y después la corrección. La prueba queda como regresión.
19. La puerta es explícita y se ejecuta: typecheck, lint, test y build con `scripts/verify-ts.py` o con los scripts equivalentes del proyecto. Un check no disponible se declara; no se omite.
20. No declares un cambio terminado sin mostrar los comandos ejecutados y su resultado.

## Procedimiento de verificación TypeScript

**Paso 1 — Mapear comportamientos, fronteras y riesgos.**
1. Enumera lo que el usuario o el agente observan: comandos, flags, formatos, errores, códigos de salida, efectos y límites.
2. Marca cada frontera por la que entra un dato no confiable: cuerpo HTTP, query, webhook, respuesta de terceros, formulario, fichero, `process.env` y argumentos de la CLI.
3. Marca los riesgos: datos que se destruyen, secretos que se filtran, cancelación, concurrencia, compatibilidad del contrato.
4. Decide la capa de cada comprobación y descarta la que no aporte confianza.

**Paso 2 — Validar las fronteras.**
1. Lee `references/validation-rules.md` antes de escribir el primer esquema.
2. Define un esquema por contrato externo y deriva sus tipos. Mantén el esquema cerca del adaptador que lo usa, salvo que cliente y servidor compartan el mismo contrato.
3. Parsea antes de usar. En un handler, `safeParse` y respuesta de error; en configuración, `parse` y arranque fallido.
4. Comprueba que el esquema rechaza lo que debe rechazar y que las transformaciones producen el tipo de salida esperado.
5. Revalida en el servidor aunque el cliente ya haya validado. El cliente no es confiable.

**Paso 3 — Cubrir la lógica con pruebas.**
1. Lee `references/test-layers.md` para elegir la capa.
2. Escribe pruebas unitarias para funciones con ramas, cálculos, validación y transformación. Usa tabla cuando compartan el mismo camino.
3. Prueba los esquemas con válidos, inválidos y límites; comprueba `z.flattenError` o la forma de error que consuma el receptor.
4. Prueba las transformaciones y refinamientos, incluidos los asíncronos con `parseAsync`.
5. Comprueba errores y cancelación sin comparar mensajes completos que dependan del entorno.

**Paso 4 — Probar la CLI, si la hay.**
1. Construye el binario una vez antes de la suite o en el `globalSetup` del runner.
2. Ejecuta cada caso con `spawn`/`execFile`, argumentos explícitos y `stdin` controlado. No dependas del directorio de trabajo: pasa rutas absolutas o usa un directorio temporal.
3. Captura `stdout` y `stderr` por separado y comprueba el código de salida.
4. Cubre `--help`, `--version`, comando desconocido, flag desconocido, JSON válido, modo no interactivo, cancelación, `--dry-run` y falta de `--yes`.
5. Comprueba que un fallo no deja archivos parciales y que los secretos no aparecen en ningún canal.

**Paso 5 — Ejecutar la puerta.**
1. Ejecuta `python src/typescript-testing-and-verification/scripts/verify-ts.py --root . --test --lint --build` o el subconjunto que el proyecto soporte.
2. Si falla, corrige por categoría: tipos, lint, test o build. No silencies con `@ts-ignore` ni desactives una regla sin justificación.
3. Copia `assets/verification-report.md` y rellena cada campo con la salida real.

**Paso 6 — Cerrar con evidencia.**
1. Declara qué se verificó, con qué comando y con qué resultado.
2. Declara lo que no se pudo verificar y por qué.
3. No conviertas un fallo conocido en «pendiente»: o se corrige, o se declara como bloqueo.

## Errores y paradas de verificación TypeScript

- Si una prueba es inestable, no la reintentes hasta que pase: elimina la fuente de no determinismo o márcala como defecto.
- Si un snapshot cambia sin un cambio de comportamiento explicado, no lo actualices: investiga la regresión.
- Si el proyecto usa otro validador, no instales Zod para cumplir esta skill. Aplica el mismo contrato de frontera con la herramienta existente.
- Si hay dos copias de Zod, deduplica antes de depurar un `instanceof ZodError` que falla. No parchees el síntoma.
- Si una prueba de extremo a extremo necesita red real, sustitúyela por un servidor local o declara la dependencia y su coste.
- Si el proyecto no tiene lint configurado, no lo añadas solo para cumplir la puerta; ejecuta las comprobaciones disponibles y declara la ausencia.
- Si `tsc` no está instalado localmente y no hay script `typecheck`, declara el bloqueo; no ejecutes un `npx` que descargue una versión distinta.
- Si el cambio no se puede probar sin datos o credenciales que no están disponibles, entrega el test con un fixture o declara el bloqueo.

## Resultado de verificación TypeScript

```text
Estado: completado | parcial | bloqueado
Comportamientos cubiertos: <lista>
Fronteras validadas: <lista con su esquema>
Capas: <tipos, esquema, unitaria, integración, extremo a extremo>
Comandos ejecutados:
- <comando>: <resultado>
Cobertura: <dato si existe, sin usarlo como objetivo>
No verificado: <lista con motivo, o "ninguno">
```

## Referencias de verificación TypeScript

- [validation-rules](references/validation-rules.md) — Zod 4 en la frontera: esquemas, tipos inferidos, `parse`/`safeParse`, transformaciones, errores, entorno, cliente/servidor y rendimiento. Léela en el paso 2.
- [test-layers](references/test-layers.md) — capas de prueba, esquemas, CLI de extremo a extremo, determinismo y dobles de prueba. Léela en los pasos 3 y 4.
- [verification-report](assets/verification-report.md) — formato de cierre con evidencia. Cópialo en el paso 5.
- [verify-ts](scripts/verify-ts.py) — ejecuta la puerta y devuelve texto o JSON. Úsalo en el paso 5.
