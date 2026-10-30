# Diseño de pruebas

Qué probar y con qué ángulo. Este documento cubre niveles, tipos, técnicas de diseño y la priorización por riesgo que elige el conjunto mínimo suficiente. El proceso de la ronda está en [process](process.md); la forma del caso y del informe, en las plantillas del paquete.

## Niveles

| Nivel | Qué contrasta | Quién lo escribe | Señal típica de fallo |
|---|---|---|---|
| Unitaria | Una unidad aislada con sus colaboradores doblados | Quien implementa | El caso rojo apunta a la línea |
| Integración | Contratos entre piezas reales | Quien implementa o quien prueba | El aislado pasa y el conjunto no |
| Sistema | La necesidad completa sobre el producto montado | Quien prueba | El flujo de usuario se rompe |
| Aceptación | Que la necesidad se resuelve, con datos reales o equivalentes | Quien encarga | «Esto no resuelve lo que pedí» |

- El nivel se elige por dónde vive el riesgo, no por costumbre. Un riesgo de contrato se ve en integración; uno de percepción, en sistema o aceptación.
- Un defecto visto en un nivel alto con causa en uno bajo no se parchea en el alto: baja a la capa que le toca y ahí se cierra con su prueba.

## Tipos

- **Funcionales:** qué hace el sistema. Las técnicas de abajo sirven aquí casi siempre.
- **No funcionales:** cómo lo hace. Rendimiento, límites de carga, accesibilidad, consumo. Cada tipo exige su método de medida; declarar el método es parte del caso.
- **Regresión:** lo que ya funcionaba. La suite del proyecto es la dueña; una ronda añade ángulos, no repite la suite entera a mano.
- **Humo:** la ruta crítica mínima para saber si merece seguir probando. Barato y primero.

## Técnicas de diseño

Cada técnica es un ángulo. Un caso sin técnica declarada suele ser un duplicado de otro.

### Partición de equivalencia

Divide las entradas en clases que el sistema debería tratar igual y elige un representante por clase. Dos casos de la misma clase prueban lo mismo; quita uno.

- Ejemplo: un campo de edad entre 18 y 99 tiene clases: menor de 18, válido, mayor de 99, no numérico, vacío.

### Valores límite

Los defectos se acumulan en las fronteras. Para cada clase con borde, prueba el borde, el borde más uno y el borde menos uno.

- Ejemplo: para 18, prueba 17, 18 y 19. Para longitud máxima 255, prueba 254, 255 y 256.

### Tabla de decisión

Cuando el resultado depende de combinaciones de condiciones, enumera las combinaciones y el resultado de cada una. Cada columna es un caso.

- Ejemplo: alta con correo válido o no, contraseñas iguales o no: la combinación con ambos datos inválidos es la que casi nadie prueba.

### Transición de estados

Cuando el comportamiento depende del estado previo, dibuja los estados y las transiciones válidas; prueba cada transición y las inválidas.

- Ejemplo: una suscripción activa que se cancela, se renueva y se reactiva. La reactivación tras expiración es la transición que falla.

### Exploratorio dirigido

Sin guion previo, con objetivo y tiempo límite. Sirve para encontrar lo que las particiones no vieron; el hallazgo que sobrevive se convierte en caso escrito.

- Regla: sesiones cortas, objetivo declarado, notas de lo recorrido. Sin notas no es prueba, es paseo.

## Prioridad por riesgo

La prioridad decide el orden, no la cantidad: si el presupuesto se acaba, lo de baja prioridad queda fuera y se escribe en la cobertura.

1. **Impacto:** qué rompe si el defecto existe. Datos de usuarios, dinero, seguridad y disponibilidad van arriba.
2. **Probabilidad:** dónde falla más. Módulos complejos, cambios recientes, código con defectos abiertos, áreas mal entendidas.
3. **Matriz:** impacto alto con probabilidad alta es primero; impacto bajo con probabilidad baja no entra esta ronda, se declara excluido.

## Cobertura honesta

- La cobertura se declara como lo que sí se probó y lo que no: «probado X, no probado Y por Z». Sin la segunda mitad, la primera engaña.
- Un porcentaje de cobertura de código dice qué se ejecutó, no qué se contrastó. No lo uses como medida de calidad de la ronda.
- Las exclusiones son decisiones: se escriben con su motivo en el alcance del informe, no en la memoria de quien probó.
