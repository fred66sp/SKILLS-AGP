# Guardia de ramas

Usa esta referencia siempre que la rama actual sea `main` o `develop`, y antes de decidir si hace falta una rama de trabajo.

## Decisión según rama y tamaño

| Rama actual | Tamaño de la tarea | Resultado |
|---|---|---|
| main | Pequeña | Permitir trabajo directo: preparar rutas, revisar el diff, proponer mensaje y pedir confirmación. |
| main | Normal o compleja | Proponer una rama corta desde `main` y confirmarla antes de modificar archivos. |
| develop | Cualquier trabajo | BLOQUEAR; proponer feature o fix desde `develop`. |
| main | Integrar una rama de trabajo | Permitir solo tras verificar origen, destino y plan aprobado. |
| develop | Integrar feature, fix, release o hotfix | Permitir solo tras verificar origen, destino y plan aprobado. |

En un repositorio con política Git Flow declarada, la fila de `main` para trabajo normal sigue la tabla de esa política: trabajo normal por rama, no directo en `main`.

## Qué hace pequeña a una tarea

Se cumplen todas:

1. El diff es pequeño y su efecto se entiende leyéndolo.
2. No toca datos almacenados, contratos públicos, seguridad, concurrencia ni código ejecutable en varios módulos.
3. No hay cambios del usuario mezclados en los archivos afectados.
4. Se deshace revirtiendo el commit, sin reescribir historia.

Si alguna condición no se cumple, no es pequeña. Ante la duda, propón una rama: cuesta un comando.

## Comprobación previa

1. Identifica la rama actual y el tamaño de la tarea.
2. Si es trabajo sobre `develop`, no prepares archivos ni propongas un commit.
3. Si estás en `main` con una tarea normal o compleja, propón la rama permitida desde su base y solicita confirmación para ese plan.
4. Tras crearla, verifica rama actual y relación con su base antes de continuar.

## Trabajo directo en main

Permitido en tareas pequeñas, con estas condiciones:

- preparas rutas enumeradas, nunca un add global;
- revisas `git diff --cached` y lo muestras;
- propones el mensaje Conventional Commits en inglés;
- pides confirmación explícita antes de ejecutar el commit;
- verificas el commit y el estado del árbol después.

No existe una excepción documentada que haya que demostrar: la proporcionalidad es la regla.

## Evidencia de integración

Una integración hacia una rama protegida debe identificar:

- origen y destino permitidos;
- commits incluidos;
- mecanismo de revisión si existe;
- estrategia de merge;
- comprobación posterior de que el resultado está contenido en el destino;
- si la rama de trabajo se borra después, con su confirmación.

## Borrado tras integrar

Cuando la rama ya integrada no sea necesaria, informa del nombre, de que su contenido está en `main` y del comando `git branch -d <rama>`, y pide confirmación. No borres trabajo no integrado ni ramas remotas sin autorización específica.
