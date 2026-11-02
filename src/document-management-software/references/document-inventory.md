# Inventario y responsabilidad documental

Léelo en el paso 2 del procedimiento, antes de decidir si un artefacto nuevo hace falta.

## Regla de responsabilidad

Cada artefacto responde a una sola pregunta. Si dos documentos responden a la misma pregunta, uno de los dos sobra o debe pasar a ser una referencia del otro.

| Artefacto | Responsable de responder | Merece existir cuando | No debe contener |
|---|---|---|---|
| README | Qué es el proyecto y cómo empezar a usarlo o desarrollarlo | Cualquier repositorio que alguien vaya a ejecutar, instalar o modificar | Detalle de cada módulo, historial de cambios, decisiones internas |
| CONTRIBUTING | Cómo se integra trabajo: ramas, commits, revisión | Hay más de un colaborador o una política que no es evidente | Guía de instalación completa, arquitectura |
| PRD | Qué problema se resuelve, para quién y con qué comportamiento esperado | Hay decisiones de producto que no se deducen del código | Diseño técnico, tareas de implementación |
| SDD / arquitectura | Cómo está estructurado el sistema y por qué | La estructura no es evidente leyendo un único módulo | Requisitos de producto, procedimientos operativos |
| ADR | Por qué se tomó una decisión concreta y qué se descartó | La decisión no es evidente y reabrirla cuesta trabajo | Catálogo de todas las decisiones triviales |
| API / contratos | Qué expone el sistema, con qué tipos, estados y errores | Existe un contrato que otros consumen | Narrativa de producto, guía de instalación |
| Instalación | Cómo se pone en marcha desde cero | Hay pasos no evidentes o requisitos de entorno | Arquitectura interna, decisiones históricas |
| Operación / runbook | Qué hacer mientras el sistema está en producción | Hay procedimientos que se ejecutan con presión y sin margen de error | Explicación conceptual del sistema |
| Troubleshooting | Qué significa un fallo y cómo se resuelve | Los fallos recurrentes no se explican en otro sitio | Especulaciones sobre causas no verificadas |
| Guía de feature / trabajo en curso | Qué se va a construir y en qué estado está | El trabajo dura varias sesiones o lo retoma otra persona | Conocimiento permanente que ya tiene su fuente |
| CHANGELOG | Qué cambió para quien consume el proyecto | El proyecto se publica o se integra en otros | Detalle interno de cada commit |

## Decisión de crear

1. Formula la pregunta que el nuevo artefacto respondería.
2. Busca si esa pregunta ya tiene respuesta en el repositorio.
3. Si la tiene y es correcta, no crees nada: enlaza.
4. Si la tiene y es incorrecta o incompleta, actualiza en lugar de crear.
5. Si la tiene repartida en varios sitios sin fuente canónica, consolida antes de añadir otro.
6. Solo si la pregunta no tiene sitio donde vivir, crea el artefacto mínimo con esa responsabilidad.

## Señales de sobre-documentación

- Secciones de plantilla vacías o con generalidades que nadie consulta.
- El mismo dato repetido en dos documentos sin referencia entre ellos.
- Documentos que describen el estado obsoleto y conviven con la fuente vigente.
- Un documento por tarea trivial.
- Datos que solo describen la máquina o el momento de escribir: rutas locales, estado de Git, remoto o publicación y recuentos de artefactos.
- Secciones que solo explican conceptos obvios para la audiencia declarada.

## Señales de sub-documentación

- Conocimiento crítico que solo existe en la cabeza de una persona o en el historial de conversaciones.
- Decisiones que se reabren porque nadie registró por qué se tomaron.
- Procedimientos operativos que se reconstruyen cada vez que se ejecutan.
- Requisitos que viven únicamente en el código y que el código no puede expresar.
- Instalación que solo funciona siguiendo pasos no escritos.

## Convención del repositorio

Antes de proponer una estructura, comprueba si el repositorio ya declara una: carpeta `docs/`, convención de ADR, formato de CHANGELOG, un `AGENTS.md` o un README con secciones fijas. Respétala aunque no sea la que usarías. Proponer un cambio de convención es un encargo aparte y explícito.

## Alcance del inventario

El script lee `.doc-inventory-ignore` en la raíz, si existe. Un patrón por línea, con `#` para comentarios y líneas vacías ignoradas. Cada patrón es una ruta relativa a la raíz: `a.md` solo excluye el fichero de la raíz y no un `sub/a.md`, y `docs/` solo excluye esa carpeta, no un `sub/docs/`. Lo que cuelga de una ruta excluida queda fuera con ella. `/` final marca una carpeta; sin él, la ruta puede ser un fichero o una carpeta. Se admiten globs simples (`*`, `?`, `[...]`) dentro de un segmento, una barra inicial se ignora y los patrones distinguen mayúsculas en cualquier sistema. No hay negación. El informe dice cuántas rutas quedaron fuera y las enumera; si el archivo existe pero no se puede leer, avisa por la salida de error y sigue sin exclusiones.

El archivo responde a una pregunta de alcance: qué artefactos no son documentación del repositorio y no deben revisarse. Por ejemplo, estado de la máquina, exportaciones generadas, copias que viajan intactas desde su origen o plantillas que solo existen al instalar. No responde a una pregunta de contenido: un hallazgo dentro de un documento revisado se decide, no se ignora.

Las exclusiones de directorio de `--exclude-dir` siguen existiendo para ejecuciones puntuales. El archivo de ignorados se suma a ellas y no las sustituye.
