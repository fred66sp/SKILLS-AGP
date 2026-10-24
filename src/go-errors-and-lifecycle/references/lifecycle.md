# Ciclo de vida: context, concurrencia y cierre

## 1. Context

- `context.Context` es el primer parámetro de las funciones que hacen I/O, esperan o pueden cancelarse:

```go
func Fetch(ctx context.Context, url string) ([]byte, error)
```

- No lo guardes en un struct. El contexto pertenece a la llamada, no al objeto.
- No crees tipos propios que embeban `context.Context`.
- No lo uses para pasar parámetros opcionales ni configuración que no cambia por petición.
- Los valores de contexto son para datos con alcance de petición: trace ID, identidad autenticada. No para dependencias.
- Deriva con timeout o deadline y cancela siempre:

```go
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()
```

- Comprueba `ctx.Err()` al recibir una cancelación y devuélvela tal cual o envuelta, según la frontera.
- No pongas el mismo timeout en todas las capas. El timeout pertenece a la capa que posee el límite.

## 2. Goroutines

Antes de lanzar una, responde por escrito:

1. ¿Quién la posee?
2. ¿Qué condición la hace terminar?
3. ¿Cómo propaga el resultado o el error?
4. ¿Cómo se cancela?
5. ¿Cómo se espera?

Si falta una respuesta, no la lances.

- Prefiere funciones síncronas. El llamador añade concurrencia cuando la necesita; quitarla después es mucho más difícil.
- Nada de goroutines en `init()`. Expón `Close`, `Stop` o `Shutdown`.
- No dejes goroutines bloqueadas enviando o recibiendo sin un receptor garantizado. El recolector no las termina.
- No cierres un canal desde el receptor ni uno que otros productores puedan usar. El propietario del envío cierra.
- Cierra recursos en la capa que los adquiere.
- Para detectar fugas, `go.uber.org/goleak` en tests de paquetes con concurrencia.

### errgroup

Para tareas relacionadas con cancelación y propagación de errores:

```go
g, ctx := errgroup.WithContext(ctx)
g.Go(func() error { return taskA(ctx) })
g.Go(func() error { return taskB(ctx) })
if err := g.Wait(); err != nil {
    return err
}
```

- `errgroup` cancela el contexto cuando una tarea falla. No ignores el contexto derivado.
- Limita la concurrencia con `g.SetLimit(n)` cuando el número de tareas no está acotado.

### WaitGroup

Solo cuando únicamente hay que esperar y no hay errores que propagar. La zero value es válida; no la copies.

### Canales

- Especifica la dirección: `chan<- T`, `<-chan T`.
- Tamaño cero o uno salvo justificación. Un buffer arbitrario oculta un problema de contrapresión.
- Usa canales para transferir propiedad o coordinar etapas; usa mutex para proteger estado compartido pequeño.
- En un `select`, incluye `case <-ctx.Done():` cuando la operación pueda bloquearse.

### Mutex y atomics

- La zero value de `sync.Mutex` y `sync.RWMutex` es válida. No uses `new(sync.Mutex)`.
- No embebas un mutex en un struct público: `Lock` y `Unlock` pasarían a la API.
- No copies un valor que contiene un mutex.
- Usa `atomic.Bool`, `atomic.Int64` y similares en lugar de campos crudos accedidos con `atomic.*`.
- Documenta la seguridad de concurrencia cuando no sea obvia: lectura segura, mutación no segura, cliente thread-safe.

## 3. Señales

```go
ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
defer stop()
```

- La primera señal cancela el contexto; no mates el proceso a la fuerza.
- Propaga `ctx` a todas las operaciones y espera a que terminen con un deadline.
- Sal con `3` cuando la cancelación venga de una señal.
- Un segundo SIGINT puede forzar la salida; si lo implementas, documéntalo y no imprimas una traza.
- En Windows, `os.Interrupt` cubre Ctrl+C; `syscall.SIGTERM` sigue siendo válido para el contrato entre plataformas.

## 4. Cierre ordenado

Orden:

1. Dejar de aceptar trabajo nuevo.
2. Cancelar el contexto.
3. Esperar a las tareas en curso con un deadline.
4. Cerrar recursos en orden inverso a su apertura.
5. Vaciar buffers y cerrar la salida.
6. Devolver el primer error de cierre.

- Un cierre que no cabe en el plazo no se bloquea indefinidamente: se cancela, se registra qué quedó abierto y se sale con el código que corresponda.
- No cierres un recurso dos veces. Si el cierre es idempotente, documenta que lo es.
- No ocultes el error de cierre por el éxito de la operación principal; usa `errors.Join` si ambos importan.

## 5. Timeouts y reintentos

- Un timeout es una decisión de frontera: conexión, petición, operación completa. No lo apliques a ciegas en todas las capas.
- Un reintento solo es válido si la operación es idempotente o el protocolo lo permite.
- Respeta `ctx` entre intentos y aplica backoff con jitter; no reintentes en bucle sin límite.
- No reintentes errores de uso, validación ni conflictos que requieren decisión.
- Distingue timeout de cancelación en el mensaje y en el `code`.

## 6. Lista rápida de ciclo de vida

- [ ] `ctx` es el primer parámetro en I/O y trabajo cancelable.
- [ ] No hay context en structs ni tipos propios.
- [ ] Cada `WithTimeout`/`WithCancel` tiene su `defer cancel()`.
- [ ] Cada goroutine tiene propietario, terminación, propagación, cancelación y espera.
- [ ] No hay goroutines en `init()` ni canales sin cierre claro.
- [ ] Canales con dirección y tamaño justificado.
- [ ] Mutex sin copia y sin embedding público.
- [ ] `main` instala señales y ejecuta cierre ordenado.
- [ ] La cancelación sale con `3` y el timeout con `1`.
- [ ] `go test -race ./...` limpio si hay concurrencia.
