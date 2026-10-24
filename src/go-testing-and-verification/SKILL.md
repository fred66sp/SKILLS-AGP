---
name: go-testing-and-verification
description: "Diseña y ejecuta la verificación de código Go, con prioridad en CLIs: pruebas unitarias y de tabla, golden files deterministas, pruebas de extremo a extremo del binario, casos de error y cancelación, y la puerta gofmt, build, test, vet, race y lint. Úsala cuando haya que escribir o revisar pruebas, fijar el comportamiento de una CLI, comprobar una regresión o declarar un cambio terminado. No la uses para benchmarks de rendimiento, estrategia de errores, diseño de la CLI ni estilo general, que tienen sus propias skills."
---

# Pruebas y verificación en Go

Una prueba existe para aumentar la confianza en el comportamiento que importa, no para llenar un porcentaje. En una CLI, el comportamiento incluye lo que se escribe en `stdout`, lo que se escribe en `stderr`, el código de salida y el estado que queda tras ejecutar.

## Invariantes de verificación

1. Prueba comportamiento observable, no detalles de implementación. Si renombrar una función privada rompe el test, el test estaba mal situado.
2. Elige la capa más pequeña que demuestre el comportamiento: unitaria para lógica pura, golden para formato, extremo a extremo para el contrato del binario.
3. Usa tabla solo cuando todos los casos recorren el mismo camino. Si cada caso necesita montaje, mocks o ramas distintas, escribe funciones separadas.
4. Cada fallo debe ser diagnosticable sin leer el test: función, entradas, `got` y `want`. Imprime `got` antes de `want`; nunca identifiques una fila solo por su índice.
5. `t.Error` es el valor por defecto para acumular fallos. Usa `t.Fatal` solo cuando continuar no tenga sentido. No llames `t.Fatal` desde una goroutine.
6. Todo helper llama `t.Helper()` como primera instrucción y usa `t.Cleanup()` para el desmontaje.
7. No uses bibliotecas de aserciones. `cmp.Diff` es aceptable para estructuras complejas, con la dirección `(-want +got)` en el mensaje.
8. Los errores se comprueban con `errors.Is`/`errors.As`, no con el texto.
9. Los golden files son deterministas: normaliza rutas temporales, separadores, tiempos, IDs y mensajes del sistema. La actualización se hace con una flag explícita y su diff se revisa.
10. La prueba de extremo a extremo construye el binario una vez, lo ejecuta con `exec.CommandContext` y comprueba por separado `stdout`, `stderr` y código de salida. No asume TTY.
11. Prueba la cancelación: el contexto se cancela, la operación retorna pronto y no quedan goroutines ni archivos temporales.
12. Usa `go test -race ./...` cuando haya concurrencia. Un test que solo pasa sin `-race` no demuestra seguridad.
13. Nada de `time.Sleep` para sincronizar, red real, servicios externos ni dependencia del reloj. Inyecta reloj, transporte y filesystem cuando el comportamiento lo necesite.
14. La cobertura es una señal, no un objetivo. No escribas tests triviales para subir un número.
15. La puerta de verificación es explícita: `gofmt -l .` sin salida, `go build ./...`, `go test ./...`, `go vet ./...`; `-race` si hay concurrencia; `golangci-lint` solo si el proyecto lo tiene configurado.
16. No declares un cambio terminado sin mostrar los comandos ejecutados y su resultado. Un check no disponible se declara como tal; no se omite.
17. Al corregir un defecto, escribe primero una prueba que falle por la causa y luego la corrección. La prueba queda como regresión.

## Procedimiento de verificación

**Paso 1 — Mapear comportamientos y riesgos.**
1. Enumera los comportamientos que el usuario o el agente observan: comandos, flags, formatos, errores, códigos de salida, efectos y límites.
2. Marca los riesgos: datos que se destruyen, secretos que se filtran, cancelación, concurrencia, compatibilidad del contrato.
3. Decide la capa de cada comprobación y descarta la que no aporte confianza.

**Paso 2 — Cubrir la lógica pura.**
1. Escribe pruebas unitarias para las funciones con ramas, cálculos, validación y transformación.
2. Usa tabla cuando los casos compartan el mismo camino; incluye límites, cero, vacío, error y variantes de entrada.
3. Comprueba errores con `errors.Is`/`errors.As`.

**Paso 3 — Fijar la salida.**
1. Usa golden files para texto y JSON estables. Guarda el fichero esperado junto al test.
2. Normaliza lo que depende del entorno antes de comparar: rutas, `\` frente a `/`, timestamps, IDs aleatorios.
3. Implementa una flag `-update` o un helper equivalente que solo reescriba los golden cuando se pida; revisa el diff antes de aceptarlo.
4. Valida el JSON con `json.Unmarshal` o un esquema, no solo con comparación de cadenas.

**Paso 4 — Probar el binario.**
1. Construye el binario una vez en `TestMain` o con `go build` a un directorio temporal.
2. Ejecuta cada caso con `exec.CommandContext`, argumentos explícitos y `stdin` controlado.
3. Captura `stdout` y `stderr` por separado y comprueba el código de salida.
4. Cubre ayuda, versión, comando desconocido, flag desconocido, JSON válido, `--dry-run`, falta de `--yes` y `EPIPE`.
5. No dependas del directorio de trabajo del test: pasa rutas absolutas o usa `t.TempDir()`.

**Paso 5 — Cubrir errores, seguridad y ciclo de vida.**
1. Prueba cada `code` estable y su código de salida.
2. Comprueba que un fallo no deja archivos parciales y que `--dry-run` no muta.
3. Comprueba que los secretos no aparecen en `stdout`, `stderr` ni en el JSON.
4. Prueba la cancelación con un contexto cancelado y, si hay goroutines, con el detector de carreras.

**Paso 6 — Ejecutar la puerta.**
1. Ejecuta `python src/go-testing-and-verification/scripts/verify-go.py --root .` (o `--race`, `--lint`).
2. Si falla, corrige por categoría: formato, compilación, test, vet, race, lint. No silencies con `//nolint` sin justificación.
3. Copia `assets/verification-report.md` y rellena cada campo con la salida real.

**Paso 7 — Cerrar con evidencia.**
1. Declara qué se verificó, con qué comando y con qué resultado.
2. Declara lo que no se pudo verificar y por qué.
3. No conviertas un fallo conocido en «pendiente»: o se corrige, o se declara como bloqueo.

## Errores y paradas de verificación

- Si un test es inestable, no lo reintentes hasta que pase: elimina la fuente de no determinismo o márcalo como defecto.
- Si el golden cambia sin un cambio de comportamiento explicado, no lo actualices: investiga la regresión.
- Si una prueba de extremo a extremo necesita red real, sustitúyela por un servidor local (`httptest`) o declara la dependencia y su coste.
- Si el proyecto no tiene `golangci-lint`, no lo añadas solo para cumplir la puerta; ejecuta las comprobaciones disponibles.
- Si `-race` no está disponible en la plataforma, decláralo; no lo sustituyas por una ejecución normal y lo presentes como equivalente.
- Si el cambio no se puede probar sin datos o credenciales que no están disponibles, entrega el test con un fixture o declara el bloqueo.

## Resultado de verificación

```text
Estado: completado | parcial | bloqueado
Comportamientos cubiertos: <lista>
Capas: <unitaria, golden, extremo a extremo>
Comandos ejecutados:
- <comando>: <resultado>
Cobertura: <dato si existe, sin usarlo como objetivo>
No verificado: <lista con motivo, o "ninguno">
```

## Referencias de verificación

- [test-layers](references/test-layers.md) — patrones de tabla, golden, extremo a extremo, cancelación y determinismo. Léela en los pasos 2 a 5.
- [verification-report](assets/verification-report.md) — formato de cierre con evidencia. Cópialo en el paso 6.
- [verify-go](scripts/verify-go.py) — ejecuta la puerta y devuelve texto o JSON. Úsalo en el paso 6.
