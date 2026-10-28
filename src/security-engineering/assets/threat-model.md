# Modelo de amenazas — <sistema>

| Campo | Valor |
|---|---|
| Alcance | <repositorio, servicio, paquete o cambio> |
| Revisión analizada | <commit, versión o fecha> |
| Autor | <quién lo redacta> |
| Fecha | <YYYY-MM-DD> |

## 1. Activos

| Activo | Daño si se compromete | Prioridad |
|---|---|---|
| <credenciales, datos, dinero, disponibilidad> | <daño concreto> | <crítica/alta/media> |

## 2. Adversarios

| Adversario | Acceso inicial | Objetivo probable |
|---|---|---|
| <anónimo, usuario, insider, dependencia> | <qué puede hacer sin atacar> | <qué busca> |

## 3. Límites de confianza

| Límite | Qué cruza | Control en el receptor |
|---|---|---|
| <navegador → API> | <dato o instrucción> | <validación, autorización, esquema> |

## 4. Casos de abuso

| ID | Caso | Entrada | Efecto | Control | Estado |
|---|---|---|---|---|---|
| AB-01 | <quién hace qué> | <dato controlable> | <activo afectado> | <control esperado> | <cubierto/parcial/ausente> |

## 5. Controles existentes

- <control, dónde se aplica y qué evidencia lo demuestra>

## 6. Riesgo residual aceptado

| Riesgo | Severidad | Motivo de aceptación | Control compensatorio |
|---|---|---|---|
| <riesgo que queda> | <crítica/alta/media/baja> | <por qué se acepta> | <qué lo reduce> |

## 7. Supuestos y caducidad

- Versión y configuración asumidas: <...>
- Controles externos asumidos: <WAF, proxy, TLS, red>
- Este análisis caduca si cambian: <modelo, permisos, dependencias, despliegue, datos>
- Preguntas abiertas: <qué falta y quién lo desbloquea>
