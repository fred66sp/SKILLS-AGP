# Reporting: defectos, métricas e informes

Lo que la prueba produce al cerrar: el reporte de cada defecto, las métricas de la ronda y el informe que alguien leerá para decidir. Todo lo que aquí se escribe queda como afirmación: el rigor es separar lo demostrado de lo supuesto.

## Anatomía del reporte de defecto

Un defecto que no se puede reproducir no es un defecto reportable: es una observación pendiente. El reporte mínimo lleva:

| Campo | Qué exige |
|---|---|
| Título | Qué falla, dónde y cuándo, en una línea. «El alta falla» no es un título; «El alta rechaza correos válidos con dominio largo en el formulario de registro» sí |
| Entorno | Sistema, versión, navegador o CLI, datos de partida. Lo mínimo para reproducir sin preguntar |
| Pasos | Numerados y concretos; cada paso deja un estado observable |
| Resultado esperado | El criterio de la fase A, escrito antes |
| Resultado observado | Lo que ocurrió, con los datos que lo demuestran |
| Evidencia | Salida, captura o registro. La evidencia va junto al reporte, no en la memoria de quien lo vio |
| Severidad | El daño del defecto, sin mirar el calendario |
| Prioridad | La urgencia de arreglarlo, mirando el daño y el contexto de entrega |

- La diferencia entre esperado y observado es el defecto. Si solo hay observado, no hay contraste y no hay defecto: hay una crónica.
- Un defecto por reporte. Los agrupados por el mismo motivo se referencian entre sí; no se mezclan síntomas con causas.

## Severidad y prioridad no son la misma columna

| Defecto | Severidad | Prioridad | Por qué |
|---|---|---|---|
| Caída del sistema al iniciar | Bloqueante | Alta | Daña mucho y ahora |
| Errata en una pantalla invisible sin sesión | Menor | Baja | Daña poco y nunca |
| Fuga de datos silenciosa | Crítico | Máxima | Daña mucho, sin señal visible |
| Enlace roto en la portada | Mayor | Media | Visible, sin bloqueo |

- Severidad alta con prioridad baja ocurre: el daño es grande pero el contexto de entrega lo pospone. La decisión es del encargo, no de quien prueba.
- No se negocia la severidad para subir la prioridad: se argumenta la prioridad con el contexto.

## Métricas honestas

- **Ejecutados:** los que llegaron a ejecutarse. Los bloqueados cuentan en su propia línea, no como superados ni como fallados.
- **Superados:** con evidencia observada. Sin evidencia no son superados, son pendientes optimistas.
- **Fallados:** con reporte. Un fallo sin reporte es una anécdota.
- **Bloqueados:** con el motivo y lo que se pidió para desbloquear.
- La suma cuadra: superados más fallados más bloqueados igual a ejecutados. La puerta lo comprueba con `E08`.
- Trampas habituales: contar re-ejecuciones de un mismo caso como avance, ocultar los bloqueados en «otros», y celebrar cero hallazgos en una ronda sin ángulos nuevos.

## El informe de ronda

La plantilla `assets/test-report.md` fija las secciones; la puerta las comprueba.

- **Alcance:** qué se probó y qué no, con el motivo de cada exclusión.
- **Resultado global:** pendiente, aprobado, aprobado con reservas o suspendido. Con reservas es la forma honesta de «aprobado, pero».
- **Cobertura:** lo probado con sus ids y lo no probado con su motivo. La segunda lista es la que hace creíble a la primera.
- **Defectos:** cada uno con id, título, severidad, prioridad y estado. Si no hay, «ninguno abierto»: la ausencia se escribe, no se calla.
- **No verificado:** lo que esta ronda no puede demostrar, siempre presente.
- **Riesgos residuales:** qué podría fallar a pesar del resultado y qué se vigila tras la entrega.
- **Métricas:** las cuatro líneas, cuadradas.
- **Lecciones:** qué ángulo faltó, qué técnica habría encontrado antes cada defecto, qué se automatiza.

## Comunicar sin inflar

- Escribe para quien decide: el resultado global arriba, la justificación después, los detalles en los ids.
- «No encontrado» no es «inexistente»; «superado» no es «garantizado». El lenguaje del informe respeta el principio 1.
- Los avisos sin evidencia se marcan como observaciones, no como defectos. Inflar para parecer minucioso cuesta credibilidad en la ronda siguiente.
