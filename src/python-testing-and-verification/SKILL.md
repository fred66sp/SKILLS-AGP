---
name: python-testing-and-verification
description: "Demuestra el comportamiento de código Python con capas de prueba proporcionadas: pytest y unittest para lógica, fixtures y parametrización, datos temporales, dobles de red, tiempo y entorno, pruebas de proceso para una CLI con `stdout`, `stderr` y código de salida separados, validación de fronteras en runtime, propiedad solo si el proyecto ya usa Hypothesis, y cierre con la puerta `scripts/verify-python.py`, que comprueba sintaxis, formato, lint, tipos y las pruebas del proyecto. Úsala al escribir o revisar pruebas, validar dato no confiable, comprobar una regresión o declarar un cambio terminado. No la uses para estilo, diseño de módulos, empaquetado ni el contrato de la CLI, que son de `python-idiomatic-style`."
metadata:
  version: "0.1.0"
---

# Pruebas y verificación en Python

Una prueba existe para aumentar la confianza en el comportamiento que importa, no para llenar un porcentaje ni para demostrar que un doble devuelve lo que se le programó. En Python, donde el tipo no se comprueba al ejecutar, la prueba es la única evidencia de que la frontera rechaza lo que dice rechazar.

Esta skill posee la elección de capa, las pruebas, los datos, los dobles, el determinismo y la puerta de verificación. El estilo, los tipos, la estructura y la CLI son de `python-idiomatic-style`.

## Invariantes de verificación Python

1. Prueba comportamiento observable, no detalles de implementación. Si renombrar una función privada rompe el test, el test estaba mal situado.
2. Elige la capa más pequeña que demuestre el comportamiento: función pura, módulo con dobles, proceso ejecutado o integración real con la frontera que preocupa.
3. Usa el runner que el proyecto ya tenga. Si no hay ninguno, `unittest` de la biblioteca estándar basta; `pytest` se añade solo con una razón.
4. Con `pytest`, un fichero por módulo o por comportamiento: `tests/test_<modulo>.py`. Con `unittest`, `tests/test_<modulo>.py` y `python -m unittest discover -s tests`.
5. Parametriza una sola vez los casos que recorren el mismo camino con entradas distintas. Si cada caso necesita montaje propio, son funciones separadas.
6. Cada fallo se diagnostica sin leer la prueba: muestra la entrada, lo obtenido y lo esperado. `assert result == esperado, mensaje` en `unittest`; `assert result == esperado` con una aserción de pytest que ya imprime ambos.
7. Usa `pytest.raises(Error) as exc` y comprueba `exc.value` cuando el mensaje o el código sean parte del contrato. No compruebes mensajes completos que dependen del entorno.
8. `tmp_path` para ficheros temporales, `monkeypatch` para entorno y atributos, `capsys` para `stdout` y `stderr`. Ningún test escribe en el directorio del repositorio.
9. Nada de red real, reloj real, aleatoriedad ni `sleep` para sincronizar. La frontera se sustituye o se inyecta.
10. Un doble de red declara el estado, las cabeceras y el cuerpo; se prueban el error HTTP, el JSON inválido y el timeout, no solo el camino feliz.
11. No se simula el módulo que se está probando ni se prueba el doble en lugar del código. Se dobla la frontera, no la función bajo prueba.
12. El DOM no existe en Python: la frontera de un servicio es su cliente, su base de datos o su sistema de ficheros, y se prueba con un doble o con un contenedor declarado.
13. Cuando el contrato es la CLI, se ejecuta el proceso con `subprocess.run`, argumentos, entorno y `stdin` controlados. `stdout`, `stderr` y el código de salida se comprueban por separado.
14. Las pruebas que modifican el entorno usan `monkeypatch` o un fixture con limpieza; no dejan variables, ficheros ni conexiones abiertas.
15. Una prueba que no puede fallar no aporta nada. Comprueba que el caso negativo falla por la causa prevista.
16. Al corregir un defecto, primero se escribe la prueba que falla por su causa y después la corrección; la prueba queda como regresión.
17. La cobertura es una señal, no un objetivo. Un umbral se acepta si ya existía; no se impone dentro de un cambio funcional.
18. `Hypothesis` solo se usa si el proyecto ya lo tiene. Una prueba de propiedad nueva no se añade para una función que tres ejemplos cubren.
19. La puerta se ejecuta y se muestra: `scripts/verify-python.py` o los scripts equivalentes del proyecto. Un check no disponible se declara, no se omite.
20. No declares un cambio terminado sin mostrar los comandos ejecutados y su resultado.

## Procedimiento de verificación Python

**Paso 1 — Mapear riesgos y capas.**
1. Enumera lo que el usuario o el agente observan: valores devueltos, excepciones, salida, ficheros, códigos de salida.
2. Marca las fronteras por las que entra dato no confiable: HTTP, fichero, entorno, `argv`, base de datos, mensaje de cola.
3. Marca los riesgos: datos que se destruyen, secretos que se filtran, concurrencia, compatibilidad del contrato.
4. Descarta las comprobaciones que no añaden confianza; la capa se elige, no se acumula.

**Paso 2 — Elegir capa y runner.**
1. Lee `references/test-layers.md` para la tabla de capas y el criterio de descarte.
2. Comprueba qué runner tiene el proyecto: `[tool.pytest.ini_options]`, `pytest.ini`, `tox.ini`, `unittest` o ninguno. Los comandos de CI mandan.
3. Decide si la frontera se dobla o se ejecuta de verdad. La integración real se reserva para el contrato que no controlas.
4. Si el runner elegido exige añadir una dependencia, es una decisión que se propone; no se toma dentro del cambio.

**Paso 3 — Escribir la prueba que falla por la razón correcta.**
1. Lee `references/pytest-patterns.md` para fixtures, parametrización, excepciones, captura y limpieza.
2. Escribe el caso mínimo: un comportamiento, una entrada, una comprobación con mensaje.
3. Comprueba que falla por la causa prevista antes de corregir el código, o que el caso negativo lo demuestra.
4. Añade los límites que importan: vacío, cero, `None`, cadena larga, error de red, timeout, cancelación.

**Paso 4 — Aislar y estabilizar.**
1. Sustituye red, reloj, aleatoriedad, entorno y sistema de ficheros por dobles o recursos temporales.
2. Espera eventos y procesos; nunca `sleep` como sincronización.
3. Limpia ficheros, conexiones y variables en el fixture o con `monkeypatch`.
4. Repite la suite dos veces, y en orden aleatorio si el runner lo permite, para detectar estado compartido.

**Paso 5 — Probar la frontera y el proceso.**
1. Lee `references/boundaries-and-process.md` cuando el riesgo sea un cliente externo o una CLI.
2. Valida el dato externo en el punto de entrada y prueba el rechazo, no solo la aceptación.
3. Ejecuta la CLI como proceso: ayuda, versión, comando desconocido, flag inválido, `--dry-run`, falta de `--yes`, JSON válido y `KeyboardInterrupt`.

**Paso 6 — Ejecutar la puerta.**
La puerta ejecuta código del proyecto (`pytest`, `ruff` y el comprobador de tipos): ejecútala solo sobre un proyecto confiable o dentro de un contenedor o usuario sin privilegios.

1. Ejecuta `python3 <skill>/scripts/verify-python.py --root .` para la sintaxis.
2. Añade `--format`, `--lint`, `--types` y `--test` según lo que el proyecto tenga configurado. Una herramienta ausente se informa; no se descarga.
3. Si falla, corrige por categoría: sintaxis, formato, lint, tipos, pruebas. No silencies con `# noqa` ni `# type: ignore` sin justificación.
4. Copia `assets/verification-report.md` y rellena cada campo con la salida real.

**Paso 7 — Cerrar con evidencia.**
1. Declara qué se verificó, con qué comando y con qué resultado.
2. Declara lo que no se pudo verificar y por qué: red no disponible, servicio externo, intérprete distinto.
3. No conviertas un fallo conocido en «pendiente»: o se corrige, o se declara como bloqueo.

## Errores y paradas de verificación Python

- Si el proyecto no tiene pruebas y nadie pidió escribirlas, no inventes una suite: informa y deja la decisión.
- Si una prueba necesita red real o un servicio externo, dobla la frontera o declara que no se puede probar. No la ejecutes contra producción.
- Si el fallo está en el código y no en la prueba, no ajustes la expectativa para que pase.
- Si un test es inestable, no lo reintentes hasta que pase: elimina la fuente de no determinismo o márcalo como defecto.
- Si el proyecto usa `unittest`, no lo sustituyas por `pytest` para «simplificar».
- Si la puerta no puede ejecutarse en el entorno, dilo y entrega el resultado como incompleto.
- Si el cambio no se puede probar sin datos o credenciales que no están disponibles, entrega la prueba con un fixture o declara el bloqueo.

## Resultado de verificación Python

```text
Objetivo verificado: <comportamiento observable>
Capas: <unittest | pytest | proceso | integración | ninguna y por qué>
Pruebas: <archivos y número de casos; qué cubre cada uno>
Determinismo: <red, reloj, entorno y ficheros controlados, o límite declarado>
Comandos ejecutados:
- <comando>: <resultado>
Puerta: <verify-python.py con sus checks y resultado, o "no ejecutada" con motivo>
No verificado: <lo que queda fuera, con motivo>
```

## Referencias de verificación Python

- [test-layers](references/test-layers.md) — mapa de riesgo, capas, criterio de descarte, determinismo y datos de prueba. Léela en los pasos 1 y 2.
- [pytest-patterns](references/pytest-patterns.md) — fixtures, parametrización, excepciones, captura, marcadores, `unittest` y diagnóstico. Léela en el paso 3.
- [boundaries-and-process](references/boundaries-and-process.md) — validación en runtime, dobles de red, tiempo y entorno, pruebas de CLI y de propiedad. Léela en el paso 5.
- [verification-report](assets/verification-report.md) — plantilla del cierre con comandos y resultados. Cópiala en el paso 6.
- [verify-python](scripts/verify-python.py) — ejecuta la puerta y devuelve texto o JSON. Úsala en el paso 6.

## Puerta del paquete de verificación

`scripts/verify-python.py` es la herramienta determinista. No reescribas su lógica a mano.

```bash
# Sintaxis de todo el proyecto
python3 <skill>/scripts/verify-python.py --root .

# Formato, lint, tipos y pruebas
python3 <skill>/scripts/verify-python.py --root . --format --lint --types --test

# Resultado para una máquina
python3 <skill>/scripts/verify-python.py --root . --lint --test --json
```

La comprobación de sintaxis siempre se ejecuta y no ejecuta el código: parsea cada `.py` con `compile()`. Las demás se añaden cuando el proyecto las tenga. Códigos de salida: `0` todo lo ejecutado pasa, `1` alguna comprobación falla, `2` error de uso o entorno. `--json` devuelve `ok`, la versión de Python detectada, la declarada en `requires-python`, las notas y el resultado de cada check.
