# Plantilla de registro de decisión

Una decisión trazable: cada afirmación se puede comprobar y cada descarte tiene motivo. Sustituye los marcadores.

## Cabecera

```text
Decisión: <mantener | modularizar | separar despliegues | migrar incrementalmente | no decidible>
Estado: <Propuesta | Aprobada | Rechazada>
Fecha: <AAAA-MM-DD>
Autor: <quién la propone>
Aprueba: <quién y con qué alcance, o "pendiente">
Aplicación: <repositorio y área>
```

## Contexto

<Qué situación motiva la decisión, en dos o tres frases. Sin adjetivos.>

## Problema demostrado

| # | Problema | Evidencia | Impacto |
|---|---|---|---|
| P1 | | | |

Si no hay problema demostrado, el estado es `Propuesta` y la decisión es «no decidible».

## Hechos, inferencias y desconocidos

```text
Hechos: <lista con fuente>
Inferencias: <lista con los hechos que las sostienen>
Desconocidos: <lista con cómo se obtendrían>
```

## Opciones consideradas

| Opción | Resuelve | No resuelve | Coste | Veredicto |
|---|---|---|---|---|
| Mantener | | | | |
| Monolito modular | | | | |
| Build-time | | | | |
| Por rutas | | | | |
| Runtime | | | | |
| <Otra, si procede> | | | | |

## Decisión

<Qué se decide y por qué es la alternativa de menor complejidad que satisface los requisitos.>

```text
Tecnología derivada: <ninguna | build-time | rutas | runtime | otra>
Requisito que la exige: <requisito verificable>
Requisitos que no se cumplen con esta opción: <lista o "ninguno">
```

## Consecuencias

| Dimensión | Efecto | Mitigación |
|---|---|---|
| Complejidad operativa | | |
| Acoplamiento | | |
| Compatibilidad | | |
| Rendimiento | | |
| Desarrollo local | | |
| Pruebas | | |
| Rollback | | |
| Observabilidad | | |
| Mantenimiento | | |

## Contrato e interfaz

<Límites, interfaz pública, contrato shell-módulo y mecanismo de control. Remite a los ficheros de diseño si existen.>

## Verificación

| Criterio de aceptación | Cómo se comprueba | Resultado |
|---|---|---|
| | | |

## Condiciones de revisión

- <Dato o evento que obliga a revisar la decisión>
- <Fecha o hito de revisión, si procede>
