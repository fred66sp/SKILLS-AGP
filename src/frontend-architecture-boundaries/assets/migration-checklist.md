# Lista de migración incremental

Úsala solo cuando la separación esté justificada por un problema demostrado y la decisión esté aprobada. Un dominio cada vez; el orden importa.

## Antes de empezar

- [ ] Existe un problema demostrado con evidencia y una línea base de métricas.
- [ ] La decisión está registrada en `decision-record.md` y aprobada.
- [ ] El alcance autorizado está escrito: qué se separa, qué no y quién revisa.
- [ ] Existe una alternativa de marcha atrás antes de tocar producción.

## Paso 1: Elegir el dominio

- [ ] El dominio tiene límites claros: responsabilidad de negocio, datos propios e interfaz pequeña.
- [ ] Su cadencia o sus bloqueos difieren del resto.
- [ ] Se puede probar sin levantar todo el sistema.
- [ ] No es el dominio más crítico ni el más acoplado; se empieza por uno representativo y reversible.

## Paso 2: Línea base

- [ ] Tiempo de release del dominio y del resto.
- [ ] Releases bloqueadas y esperas medidas.
- [ ] Frecuencia de cambios conjuntos con otras áreas.
- [ ] Tiempo de build y de despliegue.
- [ ] Fallos e incidentes atribuibles al área.
- [ ] Tiempo de recuperación ante un fallo.

Sin línea base no se podrá demostrar que la migración mejora algo.

## Paso 3: Interfaz pública

- [ ] Entrada y montaje definidos.
- [ ] Contexto acotado y versionado.
- [ ] Eventos de hechos, no de operaciones de negocio.
- [ ] Errores y modos de fallo definidos.
- [ ] Autorización decidida en el servidor.

## Paso 4: Pruebas y recuperación

- [ ] Pruebas del módulo aislado.
- [ ] Prueba de contrato entre shell y módulo.
- [ ] Simulación de los cuatro modos de fallo.
- [ ] Rollback ensayado a la versión anterior.
- [ ] Observabilidad con módulo y versión.

## Paso 5: Separar un área

- [ ] Un solo dominio sale del artefacto común.
- [ ] El resto no se reconstruye para publicarlo.
- [ ] La configuración de versiones es explícita y reversible.
- [ ] La caché se comporta como se espera durante el cambio.

## Paso 6: Verificar integrado

- [ ] Navegación completa entre áreas.
- [ ] Sesión y permisos correctos.
- [ ] Fallo del módulo nuevo sin romper el resto.
- [ ] Rendimiento dentro del presupuesto.
- [ ] Pruebas de integración en verde.

## Paso 7: Publicar sin reconstruir módulos ajenos

- [ ] El pipeline publica solo el artefacto del dominio.
- [ ] Los demás conservan su versión.
- [ ] El registro de despliegue identifica versión y responsable.
- [ ] Existe una versión anterior disponible.

## Paso 8: Simular fallos y ejecutar rollback

- [ ] Descarga fallida.
- [ ] Inicialización fallida.
- [ ] Montaje fallido.
- [ ] Fallo posterior al montaje.
- [ ] Rollback ejecutado y registrado.

## Paso 9: Comparar con la línea base

| Métrica | Antes | Después | Cambio |
|---|---|---|---|
| Tiempo de release | | | |
| Releases bloqueadas | | | |
| Cambios conjuntos | | | |
| Tiempo de build | | | |
| Incidentes | | | |
| Recuperación | | | |

## Paso 10: Decidir si continuar

- [ ] El problema medido ha mejorado.
- [ ] El coste operativo es asumible y está documentado.
- [ ] Los fallos nuevos están cubiertos.
- [ ] El equipo puede operar el nuevo artefacto sin ayuda extraordinaria.
- [ ] La decisión de continuar o detenerse está registrada.

Si la mejora no aparece, se detiene la migración y se documenta. No se amplía el alcance para justificar el esfuerzo invertido.
