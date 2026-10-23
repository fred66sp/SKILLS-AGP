# Reglas de redacción documental

Léelo en el paso 5 del procedimiento, antes de escribir o reescribir contenido.

## Proporcionalidad

Ajusta extensión y profundidad a la complejidad real, a la audiencia, al riesgo y al coste de reconstruir el conocimiento. Un proyecto pequeño puede necesitar muy poca documentación; una decisión arquitectónica puede justificar varias páginas.

Elimina antes de añadir. Si una sección no aporta información verificable, bórrala en lugar de rellenarla con generalidades.

## DRY documental

Cada conocimiento importante tiene una fuente canónica y el resto la referencia. Antes de escribir, pregunta:

1. ¿Ya está documentado?
2. ¿Dónde debería vivir canónicamente?
3. ¿Necesita repetirse aquí o basta un enlace?
4. Si se repite, ¿existe riesgo real de divergencia futura?

El DRY no es dogmático: una repetición breve es correcta cuando mejora la comprensión local y no crea dos fuentes de verdad difíciles de mantener. Lo que no es aceptable es mantener manualmente una segunda representación completa de un contrato que ya se genera o se ejecuta.

## Terminología

Usa el término que ya usa el proyecto y no lo varíes: si el dominio dice "expediente", no alternes con "carpeta" ni con "documento". Un sinónimo nuevo en documentación se convierte en una entidad nueva para quien lee.

Cuando el proyecto aún no ha fijado un término, elige uno y úsalo de forma consistente en todos los artefactos que toques en el mismo encargo.

## Estado actual frente a intención

- Lo implementado se describe en presente y se sustenta en código, tests o configuración.
- Lo decidido pero no implementado se marca como decidido y pendiente.
- Lo propuesto se marca como propuesta.
- Lo descartado se puede conservar como contexto histórico, con su motivo y su fecha si se conocen.

No mezcles los cuatro registros en un mismo párrafo sin señalarlo.

## Exactitud operativa

- Copia comandos, rutas, nombres de variables, tipos y valores exactos de la fuente.
- No inventes ejemplos que puedan confundirse con valores reales del proyecto.
- Verifica que los comandos documentados existen en el estado actual del proyecto.
- Usa rutas relativas cuando el documento viva dentro del repositorio.
- No documentes un paso que no hayas podido confirmar como disponible: márcalo como no verificado.

## Estructura orientada a la consulta

- Títulos informativos que permitan decidir si esa sección responde a la pregunta del lector.
- Lo que se consulta con frecuencia y bajo presión, primero.
- Tablas cuando hay que comparar; listas cuando hay que ejecutar en orden; prosa cuando hay que entender un razonamiento.
- Diagramas solo si aclaran relaciones que el texto vuelve confusos. Un diagrama sin fuente de verdad se queda obsoleto en silencio.

## Voz y estilo

- Imperativo y tercera persona: "Ejecuta", "Comprueba", "El servicio expone".
- Frases cortas, afirmaciones verificables.
- Sin relleno, sin lenguaje promocional, sin introducciones genéricas y sin repetir la misma idea con otras palabras.
- Sin adjetivos de valor ("potente", "robusto", "completo") que no se puedan comprobar.

## Preservar el porqué

Cuando una decisión no sea evidente y su contexto evite repetir una investigación o un error, conserva de forma concisa: problema, restricciones, decisión, razón y consecuencias significativas. No conviertas cada cambio trivial en una decisión arquitectónica.
