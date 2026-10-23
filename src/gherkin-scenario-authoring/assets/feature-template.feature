# language: es
#
# Plantilla de `.feature`: copia esta forma y sustituye cada <hueco>. Los huecos del
# `Esquema del escenario` se rellenan solo con las columnas de la tabla `Ejemplos` del
# final; los de la cabecera salen del mapa de descubrimiento (paso 2). Los dos `Escenario`
# son un ejemplo resuelto: escribe los tuyos con datos reales de tu proyecto.
# Quita estos comentarios antes de entregar y pasa el comprobador:
#   python tools/check-feature.py --path <ruta>.feature   (debe salir con 0)

@<etiqueta-de-tema>
Característica: <título-de-la-característica>
  Como <rol-que-recibe-el-valor>
  quiero <capacidad-que-el-sistema-ofrece>
  para <beneficio-que-se-puede-medir>

  Antecedentes:
    Dado que el repositorio tiene el compilador de documentación instalado

  Escenario: El enlace relativo roto corta el build
    Cuando el compilador procesa un documento con un enlace relativo roto
    Entonces el build termina con el código 1
    Y el informe menciona el documento y la ruta que falta

  Escenario: Un aviso de bajo impacto no corta el build
    Dado que el validador clasifica un enlace externo como aviso de bajo impacto
    Cuando el compilador procesa el documento con ese aviso
    Entonces el build termina con el código 0
    Y el informe lista el aviso sin marcar la compilación como fallo

  Esquema del escenario: La severidad del hallazgo decide el código del build
    Dado que el documento acumula <cantidad> hallazgos de severidad <severidad>
    Cuando el compilador termina la revisión del documento
    Entonces el build termina con el código <codigo>

    Ejemplos:
      | cantidad | severidad | codigo |
      | 1        | error     | 1      |
      | 4        | aviso     | 0      |

# Huecos y de dónde salen: <etiqueta-de-tema>, <título-de-la-característica>,
# <rol-que-recibe-el-valor>, <capacidad-que-el-sistema-ofrece> y <beneficio-que-se-puede-medir>
# van del mapa de descubrimiento y del encargo. <cantidad>, <severidad> y <codigo> son las
# columnas `cantidad`, `severidad` y `codigo` de la tabla `Ejemplos` de arriba.
