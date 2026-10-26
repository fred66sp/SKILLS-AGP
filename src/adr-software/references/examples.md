# Ejemplos de ADR

Aplica como referencia de forma, no de contenido. Los dos ejemplos describen la misma decisión con distinto nivel de detalle. Nunca copies su texto en un ADR real ni dejes marcadores de plantilla.

## Versión corta (plantilla simple)

```markdown
---
status: accepted
date: 2025-06-15
decision-makers: Ana Torres, Luis Vega
---

# Usar SQLite en desarrollo y pruebas

## Contexto y problema

Las pruebas de integración necesitan una base de datos, pero hoy usan una instancia PostgreSQL compartida. Eso produce fallos intermitentes por escrituras concurrentes y un CI de más de tres minutos solo para preparar el esquema. Hace falta una base rápida y aislada para desarrollo local y CI, sin aprovisionar infraestructura.

## Decisión

Usar SQLite mediante `better-sqlite3` en desarrollo local y en las pruebas de CI. Producción sigue en PostgreSQL. El acceso a datos pasa por una capa fina que abstrae el motor y se prueba contra SQLite y contra PostgreSQL.

No-goals: no se migra producción a SQLite ni se construye un ORM completo.

## Consecuencias

- Good, porque la preparación del CI baja de más de tres minutos a unos dos segundos.
- Good, porque cada ejecución queda aislada y no comparte estado.
- Good, porque el equipo puede ejecutar la suite completa sin conexión.
- Bad, porque hay que mantener compatibilidad entre los dialectos SQL de SQLite y PostgreSQL.
- Bad, porque algunas funciones de PostgreSQL, como operadores JSONB y columnas de array, no se prueban en local.

## Alternativas consideradas

- PostgreSQL en Docker por ejecución: paridad alta, pero añade más de 90 segundos de arranque y exige Docker dentro del CI.
- PostgreSQL en memoria con `pg-mem`: buena compatibilidad de API, pero no soporta triggers ni CTE del esquema y su mantenimiento es irregular.

## Más información

Seguimiento: crear la capa de acceso a datos y un job semanal que ejecute la suite contra PostgreSQL real. Revisar la decisión si los fallos por dialecto superan dos por trimestre.
```

## Versión larga (plantilla MADR)

El mismo caso con análisis de opciones:

```markdown
---
status: accepted
date: 2025-06-15
decision-makers: Ana Torres, Luis Vega
consulted: Marta Ruiz (DBA), equipo de plataforma
informed: equipo de frontend, QA
---

# Usar SQLite en desarrollo y pruebas

## Contexto y problema

Las pruebas de integración necesitan una base de datos, pero hoy usan una instancia PostgreSQL compartida. Esto causa dos problemas:

1. Fallos intermitentes por escrituras concurrentes entre desarrolladores y trabajos de CI.
2. CI lento: cada ejecución dedica más de tres minutos a aprovisionar y sembrar la base.

¿Cómo proporcionar una base rápida y aislada para desarrollo y CI sin perder confianza en la compatibilidad con producción?

## Criterios de decisión

- Velocidad del CI: el aprovisionamiento actual es el cuello de botella de un pipeline de cinco minutos.
- Aislamiento: cero estado compartido entre ejecuciones paralelas.
- Paridad con producción: detectar diferencias de dialecto antes de desplegar.
- Experiencia del equipo: `npm test` debe funcionar sin infraestructura externa.
- Mantenimiento: la solución no debe exigir un responsable dedicado.

## Opciones consideradas

- SQLite mediante `better-sqlite3`.
- PostgreSQL en Docker por ejecución de CI.
- PostgreSQL en memoria con `pg-mem`.

## Resultado de la decisión

Opción elegida: «SQLite mediante `better-sqlite3`», porque elimina el cuello de botella del CI, aísla cada ejecución, funciona sin conexión y tiene un coste de mantenimiento bajo. El riesgo de divergencia de dialecto se mitiga con un job semanal contra PostgreSQL real.

### Consecuencias

- Good, porque la preparación de la base en CI baja a unos dos segundos.
- Good, porque cada ejecución usa un archivo propio y no comparte estado.
- Good, porque el equipo puede ejecutar la suite completa sin infraestructura.
- Bad, porque hay que mantener una capa de acceso que oculte las diferencias de dialecto.
- Bad, porque las funciones específicas de PostgreSQL no se prueban en local.
- Neutral, porque la capa añade unas 200 líneas, pero también facilita una migración futura.

### Confirmación

- El pipeline mide el tiempo de preparación de la base y avisa si supera diez segundos.
- Un job semanal ejecuta la suite completa contra PostgreSQL real.
- Toda consulta nueva se revisa en ambos motores o se marca como exclusiva de PostgreSQL con una anotación.

## Ventajas e inconvenientes de las opciones

### SQLite mediante `better-sqlite3`

Enlaces de SQLite para Node.js, sin infraestructura.

- Good, porque solo añade una dependencia.
- Good, porque su API síncrona simplifica la preparación y el cierre.
- Neutral, porque exige una capa fina de abstracción.
- Bad, porque no soporta JSONB, arrays ni el manejo de fechas de PostgreSQL.
- Bad, porque no ejercita planes de consulta ni extensiones de PostgreSQL.

### PostgreSQL en Docker por ejecución

Un contenedor nuevo por trabajo de CI.

- Good, porque la paridad con producción es total.
- Good, porque no necesita capa de abstracción.
- Bad, porque añade más de 90 segundos por ejecución.
- Bad, porque exige Docker dentro del CI y amplía la superficie de seguridad.
- Bad, porque el equipo necesita Docker local para `npm test`.

### PostgreSQL en memoria con `pg-mem`

Emulador de PostgreSQL en memoria.

- Good, porque su compatibilidad SQL es mayor que la de SQLite.
- Good, porque no requiere infraestructura.
- Bad, porque no soporta triggers, CTE ni joins laterales del esquema.
- Bad, porque su última publicación acumula meses sin mantenimiento.
- Bad, porque depurar sus fallos exige conocer sus rarezas.

## Más información

- Seguimiento: crear la capa de acceso a datos.
- Seguimiento: configurar el job semanal contra PostgreSQL real.
- Relacionado: ADR que fija PostgreSQL para producción.
- Revisar si los fallos por divergencia de dialecto superan dos por trimestre.
```
