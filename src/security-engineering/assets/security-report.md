# Informe de seguridad: <alcance>

| Campo | Valor |
|---|---|
| Operación | <diseñar / revisar / auditar / corregir / comprobar / investigar> |
| Alcance | <repositorio, servicio, paquete o cambio> |
| Revisión analizada | <commit, versión o fecha> |
| Fecha | <YYYY-MM-DD> |

## Resumen

<Qué se revisó, qué se encontró y qué queda abierto. Sin adjetivos y sin declarar el sistema «seguro».>

## Método aplicado

- Modelo de amenazas: <ruta o "no aplica" con motivo>
- Categorías revisadas: <autorización, inyección, secretos, agentes, ...>
- Herramientas ejecutadas: <comando y versión>
- Fuera de alcance: <qué no se revisó>

## Hallazgos

| ID | Severidad | Categoría | Ubicación | Impacto | Estado |
|---|---|---|---|---|---|
| SEC-001 | <crítica/alta/media/baja/informativa> | <categoría> | <ruta:línea> | <activo y efecto> | <abierto/corregido/aceptado> |

### SEC-001: <título>

- **Entrada:** <qué controla el atacante>
- **Traza:** <entrada → transformación → efecto>
- **Impacto:** <qué activo y cuánto>
- **Control ausente:** <qué debería impedirlo y dónde>
- **Corrección:** <cambio mínimo aplicado o propuesto>
- **Evidencia:** <prueba, reproducción sintética o comando>
- **Supuestos:** <los que sostienen la severidad>

## Correcciones aplicadas

| Hallazgo | Cambio | Prueba de regresión |
|---|---|---|
| SEC-001 | <qué se cambió y dónde> | <comando y resultado> |

## Evidencia de verificación

```text
<comandos ejecutados y su resultado real>
```

## Riesgo residual

| Riesgo | Severidad | Motivo de aceptación | Control compensatorio |
|---|---|---|---|
| <riesgo que queda> | <...> | <...> | <...> |

## No verificado

- <qué quedó fuera y qué lo desbloquearía>

## Caducidad

Este informe deja de ser válido si cambian el modelo, los permisos, las dependencias, la configuración de despliegue o los datos tratados.
