# language: es
@documentacion
Característica: Compilación de la documentación
  Como mantenedor
  quiero que el build falle cuando un enlace relativo está roto
  para no publicar guías imposibles de seguir

  Antecedentes:
    Dado que el repositorio está en la rama principal
    Y el compilador de documentación está instalado

  Escenario: El build falla ante un enlace relativo roto
    Cuando el compilador procesa un documento con un enlace relativo roto
    Entonces el build termina con el código 3
    Y el informe menciona el documento y la línea del enlace

  Escenario: La reconstrucción incremental no repite el trabajo
    Dado que la caché contiene 20 documentos compilados
    Cuando el compilador procesa un documento modificado
    Entonces la caché contiene 21 documentos
    Y el informe registra un documento recompilado

  Escenario: La carpeta de salida queda fuera del recorrido
    Dado que existe la carpeta de salida del build anterior
    Cuando el compilador recorre el árbol de documentación
    Entonces la carpeta de salida no aparece en el informe
    Y el recorrido incluye los documentos fuente restantes

  Esquema del escenario: El validador asigna la severidad de cada hallazgo
    Dado que el validador analiza un documento con "<hallazgo>"
    Cuando el compilador termina la revisión
    Entonces el informe marca el hallazgo con severidad "<severidad>"

    Ejemplos:
      | hallazgo             | severidad |
      | enlace relativo roto | error     |
      | título duplicado     | aviso     |
