# Informe de verificación

Copia este bloque al entregar. Rellena solo con lo ejecutado: lo no ejecutado se declara en `No verificado`.

```text
Cambio: <qué comportamiento se añadió o se corrigió>
Objetivo verificado: <lo que observa quien usa el código>
Capas: <unittest | pytest | proceso | integración | ninguna y por qué>
Pruebas: <archivos y casos>
Determinismo: <red, reloj, entorno y ficheros controlados>

Comandos y resultado
- compile() sobre los .py                            <PASS | FAIL>
- ruff format --check                                <PASS | FAIL | no disponible>
- ruff check                                         <PASS | FAIL | no disponible>
- mypy | pyright                                     <PASS | FAIL | no disponible>
- pytest | python -m unittest                        <PASS | FAIL | no disponible>
- verify-python.py --root . [flags]                  <PASS | FAIL>
- <comprobación manual>                              <PASS | FAIL | no ejecutada>

No verificado: <qué queda fuera y por qué>
Deuda: <prueba pendiente, frontera sin doble o límite aceptado>
```

Reglas del informe:

- Un comando que no se ejecutó no se marca como `PASS`.
- El resultado de la puerta se copia tal cual, incluido el código de salida.
- Una comprobación manual declara el entorno y si hubo red.
- La deuda se nombra con el motivo; no se deja como impresión.
