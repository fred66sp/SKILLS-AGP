# Capas de prueba

## 1. Elegir la capa

| Capa | Qué demuestra | Coste | Cuándo |
|---|---|---|---|
| Unitaria | Lógica, ramas, validación, cálculo | Bajo | Siempre que haya lógica pura |
| Tabla | Muchos casos del mismo camino | Bajo | Variantes, límites, errores |
| Golden | Formato estable de texto o JSON | Medio | Salida de contrato |
| Extremo a extremo | Comando, flags, stdout, stderr, exit code | Medio-alto | Contrato de la CLI |
| Integración | Frontera real: fichero, proceso, HTTP local | Alto | Cuando el contrato cruza esa frontera |

No escribas la capa más alta para probar una función pura. No escribas solo la más baja cuando el requisito es «el comando devuelve `4` sin `--yes`».

## 2. Pruebas de tabla

```go
func TestParseLimit(t *testing.T) {
    tests := []struct {
        name    string
        input   string
        want    int
        wantErr bool
    }{
        {name: "default", input: "10", want: 10},
        {name: "zero rejected", input: "0", wantErr: true},
        {name: "negative rejected", input: "-1", wantErr: true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := ParseLimit(tt.input)
            if (err != nil) != tt.wantErr {
                t.Fatalf("ParseLimit(%q) error = %v, wantErr %v", tt.input, err, tt.wantErr)
            }
            if got != tt.want {
                t.Errorf("ParseLimit(%q) = %d, want %d", tt.input, got, tt.want)
            }
        })
    }
}
```

- Usa nombres de campo cuando la tabla ocupe muchas líneas o haya campos adyacentes del mismo tipo.
- Incluye las entradas en el mensaje. Nunca `case 3 failed`.
- Un único `wantErr bool` es aceptable; si necesitas comprobar qué error, usa `errors.Is` y añade el centinela a la tabla.
- No uses tabla si cada caso necesita un montaje distinto. La tabla deja de ser legible y oculta la intención.

## 3. Golden files

```go
func TestRenderJSON(t *testing.T) {
    got := render(listResult{Items: []item{{ID: "a"}}})

    want := readGolden(t, "render_json.golden")
    if diff := cmp.Diff(want, got); diff != "" {
        t.Errorf("RenderJSON() mismatch (-want +got):\n%s", diff)
    }
}
```

- Guarda el golden junto al test, en `testdata/`.
- Normaliza antes de comparar:
  - rutas absolutas y temporales: sustitúyelas por `<TMP>`, `<ROOT>`;
  - separadores `\` y `/`;
  - timestamps, duraciones, IDs aleatorios y nombres de host;
  - versiones de Go si el contrato no las incluye.
- La actualización se hace con una flag explícita (`-update`) y se revisa el diff. Un golden actualizado sin explicación es una regresión aceptada a ciegas.
- Para JSON, compara estructura además de texto: `json.Unmarshal` detecta un JSON inválido que una comparación de cadenas no ve.
- No incluyas en el golden rutas de una máquina concreta ni datos que cambian entre ejecuciones.

## 4. Extremo a extremo de una CLI

Construye el binario una vez:

```go
var binPath string

func TestMain(m *testing.M) {
    dir, err := os.MkdirTemp("", "cli-e2e-")
    if err != nil {
        panic(err)
    }
    defer os.RemoveAll(dir)

    binPath = filepath.Join(dir, "tool.exe")
    if runtime.GOOS != "windows" {
        binPath = filepath.Join(dir, "tool")
    }

    cmd := exec.Command("go", "build", "-o", binPath, ".")
    if out, err := cmd.CombinedOutput(); err != nil {
        panic(fmt.Sprintf("go build: %v\n%s", err, out))
    }

    os.Exit(m.Run())
}
```

Cada caso:

```go
func runCLI(t *testing.T, stdin string, args ...string) (stdout, stderr string, code int) {
    t.Helper()

    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    cmd := exec.CommandContext(ctx, binPath, args...)
    cmd.Stdin = strings.NewReader(stdin)

    var out, errOut bytes.Buffer
    cmd.Stdout = &out
    cmd.Stderr = &errOut

    err := cmd.Run()
    if ctx.Err() != nil {
        t.Fatalf("command %v timed out: %v", args, ctx.Err())
    }

    code = 0
    if err != nil {
        var exitErr *exec.ExitError
        if !errors.As(err, &exitErr) {
            t.Fatalf("run %v: %v", args, err)
        }
        code = exitErr.ExitCode()
    }

    return out.String(), errOut.String(), code
}
```

Reglas:

- Comprueba `stdout` y `stderr` por separado. Un resultado correcto en el flujo equivocado es un fallo.
- Comprueba el código de salida exacto, no solo «distinto de cero».
- Pasa `stdin` explícito; no heredes el del test.
- Usa `t.TempDir()` para los datos de entrada y salida.
- No asumas TTY. Si el comportamiento depende de TTY, inyéctalo como dependencia o prueba ambos caminos con un helper.
- No dependas de la red. Si hace falta, usa `httptest.NewServer` y pásale la URL al binario.
- Si el binario abre un fichero de configuración, pásalo con `--config` a una ruta temporal.

### Casos mínimos de contrato

- [ ] `--help` sale con `0` y muestra uso.
- [ ] `<comando> --help` sale con `0`.
- [ ] `--version` sale con `0`.
- [ ] Comando desconocido sale con `2`.
- [ ] Flag desconocido sale con `2`.
- [ ] `--json` produce JSON válido y solo JSON en `stdout`.
- [ ] Error en modo JSON produce el sobre de error y el código esperado.
- [ ] `--dry-run` no muta el estado.
- [ ] Operación destructiva sin `--yes` sale con `4`.
- [ ] Cancelación sale con `3` y no deja basura.

## 5. Errores y cancelación

- Comprueba semántica, no texto:

```go
if !errors.Is(err, ErrNotFound) {
    t.Fatalf("Lookup(%q) error = %v, want ErrNotFound", key, err)
}
```

- Para un error tipado:

```go
var conflict *ConflictError
if !errors.As(err, &conflict) {
    t.Fatalf("Delete() error = %v, want *ConflictError", err)
}
```

- Cancela un contexto y comprueba que la operación retorna antes del timeout:

```go
ctx, cancel := context.WithCancel(context.Background())
cancel()

err := Run(ctx)
if !errors.Is(err, context.Canceled) {
    t.Fatalf("Run(cancelled) error = %v, want context.Canceled", err)
}
```

- Si hay goroutines, añade `go.uber.org/goleak` o una comprobación equivalente. Un test que pasa con goroutines vivas sigue siendo un fallo.

## 6. Determinismo

- No uses `time.Sleep` para esperar. Usa canales, `sync.WaitGroup`, `t.Cleanup` o un contexto con deadline.
- Inyecta el reloj si el resultado depende de la hora. Un `now func() time.Time` en el struct es suficiente; no hace falta una biblioteca.
- No dependas del orden de un map. Ordena las claves antes de comparar o serializar.
- No dependas del directorio de trabajo del test. Usa `t.TempDir()` y rutas absolutas.
- No dependas del locale ni de la codificación de la consola. Fija UTF-8 y evita mensajes del sistema en los golden.
- Si un test necesita paralelismo, `t.Parallel()` solo cuando los casos sean independientes y no compartan estado global.

## 7. Organización

- Prefiere tests de caja negra (`package foo_test`) para el contrato público; usa caja blanca (`package foo`) para detalles internos que no se pueden observar de otra forma.
- Un helper de test se nombra y se documenta como cualquier función; llama `t.Helper()`.
- `TestMain` solo cuando todo el paquete necesita montaje y desmontaje. Para un caso concreto, usa `t.Cleanup`.
- No compartas estado mutable entre tests. Si lo haces, `t.Parallel()` lo convertirá en una carrera.
- Los tests de regresión llevan en el nombre o en un comentario el defecto que fijan, no un número de ticket que caduca.

## 8. Lista rápida de pruebas

- [ ] Cada comportamiento importante tiene una capa de prueba adecuada.
- [ ] Los fallos incluyen función, entradas, `got` y `want`.
- [ ] Los errores se comprueban con `errors.Is`/`errors.As`.
- [ ] Los golden se normalizan y su actualización es explícita.
- [ ] El binario se prueba con `stdout`, `stderr` y código de salida separados.
- [ ] `--dry-run`, `--yes`, JSON y cancelación están cubiertos.
- [ ] No hay `time.Sleep`, red real ni dependencia del orden de map.
- [ ] `go test -race` limpio si hay concurrencia.
- [ ] La puerta se ejecutó y su resultado está en el informe.
