# Plantilla de informe de revisión de un `.feature`

Rellena este informe en el paso 8 del procedimiento de `SKILL.md`. Copia la estructura; no la resumas ni dejes campos vacíos sin explicarlos. Un campo sin evidencia es un hallazgo en sí mismo: se declara en `Sin verificar`.

~~~markdown
# Revisión de <ruta-del-archivo>

- Palabras clave detectadas: `# language: es` | `# language: en` | sin encabezado (inferido por <motivo>)
- Stack declarado por el proyecto: <cucumber-js | cucumber-jvm | pytest-bdd | behave | Reqnroll | godog | sin stack>
- Comprobación determinista: `python tools/check-feature.py --path <ruta>` → exit <0|3|2>
- Parseo verificado por el runner: <comando ejecutado y resultado> | no verificado (<motivo>)

## Veredicto del archivo

**APTO | APTO CON RESERVAS | NO APTO | FUERA DE ALCANCE**

Motivo en una línea: <qué lo coloca ahí, citando el hallazgo de mayor prioridad>.

## Veredicto por escenario

| Escenario | Línea | Veredicto | Hallazgos | Regla |
|---|---|---|---|---|
| <título> | <n> | APTO / APTO CON RESERVAS / NO APTO | <código>@<línea>, <código>@<línea> | <1-4> |

## Hallazgos

Para cada hallazgo, en orden de prioridad: `multiple-action-outcome` y los deterministas de
estructura primero, después los de lenguaje, al final los candidatos confirmados.

- **<código>** (regla <n>, <determinista | candidato confirmado>) — <ruta>:<línea>
  - Evidencia: `<paso literal>`
  - Por qué importa: <una línea, en términos de colaboración, triaje o coste de ejecución>
  - Reescritura propuesta:
    ~~~gherkin
    <escenario o pasos corregidos>
    ~~~

## Candidatos refutados

- **<código>** — <ruta>:<línea> — refutado porque <motivo concreto, no "es aceptable">.

## Sin verificar

- <qué comprobación no se pudo hacer y por qué: sin runner instalado, sin stack declarado,
  idioma no soportado por el script, tabla ilegible>.

## Recuento

- Deterministas confirmadas por el script: <n>
- Estimaciones confirmadas por el criterio: <n>
- Candidatos refutados: <n>
- Escenarios revisados: <n> de <m> del archivo
~~~

## Reglas de relleno

1. Cada hallazgo cita el código del script y la regla de las cuatro. Si el hallazgo no lo produjo el script, se marca como `candidato confirmado` o como `estimación` y se dice en la línea de recuento.
2. La reescritura propuesta no añade comportamiento que el escenario original no tuviera. Si hace falta decidir qué comportamiento queda en cada escenario dividido, se pregunta antes de entregar el informe.
3. `FUERA DE ALCANCE` no lleva tabla por escenario: se usa cuando el texto no es Gherkin o cuando el encargo pide escribir, descubrir o automatizar.
4. El informe no declara que una prueba pase o falle, ni que un paso esté implementado. Solo califica el artefacto de especificación.
