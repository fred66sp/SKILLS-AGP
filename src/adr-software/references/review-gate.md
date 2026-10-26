# Puerta de revisión del ADR

Aplica antes de declarar un ADR terminado. Léela en el paso 6 del contrato y recórrela completa cuando el script detecte un hallazgo o cuando el ADR vaya a aceptarse.

La pregunta que decide es una: **¿puede un agente implementar esta decisión leyendo solo el ADR, sin preguntar y sin adivinar?** La puerta no puntúa estilo; bloquea huecos que obligarían a interpretar.

## Comprobaciones bloqueantes

### Contexto y problema

- [ ] Quien no conoce el proyecto entiende por qué la decisión existe.
- [ ] El disparador es explícito: qué cambió, se rompió o se romperá.
- [ ] Los sistemas, siglas y piezas se nombran; no se presupone conocimiento tribal.
- [ ] Los enlaces a issues, PR o ADR previos resuelven o se declaran ausentes.

### Decisión

- [ ] La decisión es específica y accionable: nombra la opción elegida, su alcance y su límite.
- [ ] Los no-goals están escritos; se sabe qué queda fuera.
- [ ] Las restricciones son medibles o verificables donde importa.
- [ ] La decisión no depende de una implementación que puede cambiar sin cambiar la decisión.

### Consecuencias

- [ ] Cada consecuencia es concreta, no un deseo.
- [ ] Las tareas de seguimiento están identificadas: migración, configuración, documentación, pruebas.
- [ ] Los riesgos tienen mitigación o una razón de aceptación.
- [ ] Ninguna consecuencia repite la decisión con otras palabras.

### Alternativas (plantilla MADR o decisión con más de una opción)

- [ ] Se consideraron al menos dos opciones reales; no solo «hacerlo» frente a «no hacerlo».
- [ ] Cada opción tiene ventajas e inconvenientes reales, no un hombre de paja.
- [ ] La opción elegida se justifica con los criterios que decidieron.
- [ ] Cada opción rechazada explica por qué se rechazó.

### Confirmación (cuando existe)

- [ ] El criterio se puede implementar como prueba o comprobación.
- [ ] Queda claro quién o qué confirma, y cuándo.

### Metadatos

- [ ] `status` es correcto; un ADR nuevo está en `proposed`.
- [ ] `date` es la fecha del último cambio de estado, en `YYYY-MM-DD`.
- [ ] `decision-makers` nombra a quien posee la decisión.
- [ ] El título es una frase verbal que describe la decisión, no el problema.
- [ ] El nombre del archivo sigue la convención del directorio.
- [ ] No quedan marcadores `{...}`, secciones vacías ni texto de ejemplo.

### Registro

- [ ] El índice enlaza el ADR y la entrada resuelve.
- [ ] Si sustituye a otro, ambos se enlazan y el anterior está en `superseded by`.
- [ ] Si está deprecado, se explica qué lo sustituye o por qué ya no aplica.

## Cómo se cierra un hallazgo

Un hallazgo no se cierra rebajando la afirmación a algo genérico. Se cierra de una de estas formas:

1. Con el dato que faltaba, aportado por la persona o por una fuente del repositorio.
2. Con una decisión explícita de dejar el hueco y el ADR en `proposed`, declarado en el resultado.
3. Retirando la sección si era opcional y no aporta.

Si un hueco impide implementar, el ADR no se acepta aunque el resto esté completo.

## Modos de fallo frecuentes

| Síntoma | Causa | Corrección |
|---|---|---|
| «Mejorar el rendimiento» como consecuencia | Intención vaga | Preguntar qué métrica, cuánto y cómo se mide. |
| Una sola opción | Decisión ya tomada; ADR a posteriori | Preguntar qué se rechazó y por qué. |
| El contexto parece una propuesta de solución | No se enmarcó el problema | Reescribir el contexto como problema y mover la solución a la decisión. |
| Todas las consecuencias son positivas | Selección sesgada | Preguntar qué se vuelve más difícil y cuánto cuesta mantenerlo. |
| «Decidimos usar X» sin motivo | Falta justificación | Preguntar por qué X y no Y. |
| El ADR repite el ticket | No se destiló la decisión | Conservar contexto y consecuencias; quitar el relato del ticket. |
| El estado dice `accepted` sin aprobación | Se confundió redacción con aprobación | Volver a `proposed` hasta que la persona apruebe. |
