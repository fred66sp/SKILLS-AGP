# Informe de verificación

Copia este bloque al entregar. Rellena solo con lo ejecutado: lo no ejecutado se declara en `No verificado`.

```text
Cambio: <qué comportamiento se añadió o se corrigió>
Objetivo verificado: <lo que observa quien usa el código>
Capas: <node:test | navegador | runner del proyecto | ninguna y por qué>
Pruebas: <archivos y casos>
Determinismo: <red, reloj, almacenamiento y estado controlado>

Comandos y resultado
- node --check <archivos>                          <PASS | FAIL>
- <script test del proyecto | node --test>         <PASS | FAIL | no disponible>
- <script lint del proyecto>                       <PASS | FAIL | no disponible>
- verify-js.py --root . [--test] [--lint]          <PASS | FAIL>
- <comprobación manual en navegador>               <PASS | FAIL | no ejecutada>

No verificado: <qué queda fuera y por qué>
Deuda: <prueba pendiente, frontera sin doble o límite aceptado>
```

Reglas del informe:

- Un comando que no se ejecutó no se marca como `PASS`.
- El resultado de la puerta se copia tal cual, incluido el código de salida.
- Una comprobación manual declara el navegador usado y si hubo red.
- La deuda se nombra con el motivo; no se deja como impresión.
