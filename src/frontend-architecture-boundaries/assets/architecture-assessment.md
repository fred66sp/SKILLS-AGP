# Plantilla de diagnóstico de arquitectura

Copia esta estructura y sustituye cada marcador. Cada fila necesita fuente; una fila sin fuente es un `Desconocido`.

## Encargo

```text
Tipo: <auditoría | decisión | implementación>
Aplicación y repositorio: <ruta o URL, rama, commit>
Fecha de inspección: <AAAA-MM-DD>
Alcance inspeccionado: <carpetas, servicios y artefactos>
Fuera de alcance: <lo que no se ha mirado>
Acceso disponible: <código, pipelines, métricas, personas>
```

## Stack y entrega

| Dato | Valor | Fuente |
|---|---|---|
| Frameworks y versiones | | |
| Gestor de paquetes y workspaces | | |
| Bundler y versión | | |
| Repositorio único o múltiple | | |
| Builds y pipelines | | |
| Entornos y configuración | | |
| Cadencia de release | | |
| Responsables por área | | |

## Estructura

| Área o módulo | Responsabilidad declarada | Datos que posee | Interfaz pública | Dependencias permitidas | Dueño |
|---|---|---|---|---|---|
| | | | | | |

## Evidencia recogida

| # | Hallazgo | Tipo (`Hecho` / `Inferencia` / `Desconocido`) | Evidencia (ruta:línea, comando, métrica o fuente) | Problema que sugiere |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

## Bloqueos y coordinación

| Dominio | Release bloqueada | Causa observada | Espera medida | Fuente de la medición |
|---|---|---|---|---|
| | | | | |

Si no hay medición, escribe `Desconocido` y no lo conviertas en una conclusión.

## Problemas demostrados

| # | Problema | Evidencia | Impacto observable | ¿Lo resolvería una separación de despliegue? |
|---|---|---|---|---|
| P1 | | | | |

## Desconocidos y cómo obtenerlos

| Dato que falta | Quién puede aportarlo | Cómo se obtiene | Bloquea la decisión |
|---|---|---|---|
| | | | |

## Conclusión del diagnóstico

```text
Problemas demostrados: <lista o "ninguno">
Problemas inferidos: <lista con los hechos que los sostienen>
Evidencia insuficiente para: <decisiones que no se pueden tomar>
Siguiente fase: <comparar opciones | modularizar sin cambiar despliegue | detenerse a recoger evidencia>
```
