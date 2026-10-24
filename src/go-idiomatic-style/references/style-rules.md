# Reglas de estilo y diseño

## 1. Formato

- `gofmt` decide el formato. Ejecuta `go fmt ./...`; no corrijas a mano lo que la herramienta normaliza. No formatees `vendor/` ni `testdata/`.
- `goimports` solo si el proyecto ya lo usa. No es un requisito del lenguaje.
- La llave de apertura va en la misma línea. No hay límite rígido de longitud: divide por claridad, no por una columna.
- Reduce anidación con retornos tempranos. Omite el `else` cuando el `if` ya retorna, continúa o rompe.
- Los comentarios son frases completas. El comentario de un símbolo exportado empieza por su nombre y termina en punto.
- No dejes código comentado, imports sin usar ni variables intermedias que solo se usan una vez sin aportar nombre.

## 2. Nombres

| Elemento | Regla | Ejemplo |
|---|---|---|
| Paquete | minúsculas, sin `_`, una palabra de dominio | `config`, `oauth2`, `tabwriter` |
| Exportado | PascalCase | `ParseURL`, `MaxRetries` |
| No exportado | camelCase | `parseURL`, `maxRetries` |
| Receptor | 1-2 letras del tipo, igual en todos los métodos | `func (c *Client)` |
| Constante | MixedCaps, nunca `ALL_CAPS` | `DefaultTimeout` |
| Acrónimo | caso coherente | `userID`, `HTTPClient`, `ParseURL` |
| Interfaz de un método | método + `-er` | `Reader`, `Formatter` |
| Variable | longitud proporcional al ámbito | `i`, `buf`, `pendingOrders` |
| Test | `TestXxx`, guion bajo solo para variantes | `TestParse_InvalidInput` |

- No uses `this`, `self` ni `me` como receptor.
- No repitas el contexto: `widget.New()`, no `widget.NewWidget()`; `p.Name()`, no `p.ProjectName()`.
- No ocultes identificadores predeclarados: `error`, `string`, `len`, `cap`, `append`, `copy`, `new`, `make`, `any`, `nil`.
- Un nombre largo no compensa un concepto confuso. Si necesitas `userAccountPermissionChecker`, probablemente sobra una capa.

## 3. Paquetes

- Un paquete tiene una responsabilidad que se explica en una frase.
- No lo dividas solo porque el archivo sea largo, para crear paquetes de un solo tipo ni si provoca ciclos.
- Divídelo cuando las partes no comparten símbolos no exportados, cuando las usan grupos distintos o cuando la documentación se vuelve inabarcable.
- Evita `util`, `common`, `helpers`, `shared` y `misc`. Si necesitas un cajón, nómbralo por el dominio que contiene.
- Los imports se agrupan: biblioteca estándar primero, línea en blanco, dependencias externas.
- `import _` solo en `main` o tests. `import .` no se usa salvo una excepción documentada de test.
- Evita `init()`. Si es imprescindible, debe ser determinista, sin I/O, sin entorno y sin depender del orden entre paquetes.

## 4. Estructura

Aplicación pequeña:

```text
project/
├── go.mod
├── go.sum
└── main.go          # cableado; la lógica empieza aquí
```

- Si la lógica deja de caber en `main.go`, añade `internal/<dominio>`; no antes.

Varios binarios:

```text
project/
├── cmd/
│   └── <binario>/
│       └── main.go  # cableado
├── internal/
│   ├── cli/         # parseo, ayuda, formato
│   └── <dominio>/   # casos de uso
├── pkg/             # solo si hay API pública para otros módulos
└── go.mod
```

- No copies una plantilla de proyecto sin necesidad. `pkg/` no existe para lucir estructura.
- `main` construye dependencias, llama a `run` y hace `os.Exit`. Nada más.
- Las flags se declaran en `main` o en el paquete de CLI, nunca en la librería de dominio.
- La librería recibe configuración por parámetro. No lee variables de entorno ni flags por su cuenta.
- El patrón preferido es `func run(ctx context.Context, args []string, stdin io.Reader, stdout, stderr io.Writer) int`.
- No uses variables globales mutables. Inyecta reloj, entorno y escritores.

## 5. Funciones

- Una responsabilidad comprensible. Si la función necesita un comentario para explicar qué hace, divídela.
- Comprueba errores inmediatamente y devuélvelos con contexto. El camino feliz queda sin indentar.
- Firma en una línea si cabe. Si no, un argumento por línea con coma final.
- Un booleano posicional ambiguo se documenta con `/* name */` o se sustituye por un tipo con nombre.
- No pases puntero a interfaz: `io.Reader`, no `*io.Reader`.
- Las funciones que aceptan formato terminan en `f` (`Errorf`, `Logf`) para que `go vet` las reconozca.
- Ordena el archivo: tipos, constructores, métodos exportados, métodos no exportados, utilidades.
- Los retornos con nombre se usan cuando aclaran la firma, no para ahorrar una línea con un `return` desnudo. Un `return` desnudo solo es aceptable en funciones de pocas líneas.

## 6. Datos

### Slices

| Caso | Decisión |
|---|---|
| Colección vacía que se serializa a JSON | `[]T{}` si el contrato exige `[]`; `var s []T` si `null` es válido |
| Tamaño conocido | `make([]T, 0, n)` |
| `append` | Asigna siempre: `s = append(s, v)` |
| Copia en frontera | `append([]T(nil), s...)` o `copy` explícito |
| Conjunto | `map[T]struct{}` |

- No distingas `nil` de vacío en una API salvo que la serialización o la semántica lo exijan. Si lo haces, documéntalo.

### Maps

- Inicializa antes de escribir: `make(map[K]V)`.
- Usa capacidad cuando el número de claves se conoce y el mapa es grande.
- No dependas del orden de iteración. Si necesitas orden, ordénalo explícitamente.
- Para membership, `map[T]struct{}`; el valor booleano solo si tiene un significado además de la presencia.

### Structs

- Usa nombres de campo al inicializar, salvo tablas de test de tres campos o menos.
- Omite los campos con valor cero; deja que Go los inicialice.
- Usa `&T{}` en lugar de `new(T)` cuando haya campos.
- Los tags de serialización son contrato: cambiarlos puede romper el cable.
- No copies un valor de tipo `T` si sus métodos están en `*T`; afecta a `sync.Mutex`, `bytes.Buffer` y tipos que los contienen.

### Punteros y valores

| Usa puntero cuando | Usa valor cuando |
|---|---|
| El método muta el receptor | El tipo es pequeño e inmutable |
| `nil` representa ausencia | La copia es clara y segura |
| La estructura es grande | No importa distinguir el cero |
| Necesitas identidad compartida | El valor cero es un valor válido |

- No justifiques la elección con «va al stack» o «va al heap»: decide el compilador.

## 7. Interfaces

- La interfaz vive en el consumidor, no en el productor.
- Debe tener solo los métodos que el consumidor usa. No hay un número mágico, pero una interfaz de diez métodos suele ser una estructura disfrazada.
- Devuelve tipos concretos desde constructores. Si el tipo solo existe para implementar la interfaz, puedes devolver la interfaz para ocultarlo, pero es la excepción.
- No definas interfaces antes de tener un uso real ni «para poder mockear».
- Usa interfaces estándar (`io.Reader`, `io.Writer`, `fmt.Stringer`) cuando encajen.
- La comprobación en tiempo de compilación `var _ I = (*T)(nil)` se añade solo cuando no hay otra conversión estática que la garantice.
- Las aserciones de tipo usan `v, ok := x.(T)`. Sin `ok`, un fallo es un panic.
- No embebas tipos en structs públicos: su conjunto de métodos pasa a ser tu API.

## 8. Dependencias

- Biblioteca estándar primero. Una dependencia se justifica por una necesidad que la estándar no cubre bien.
- Revisa licencia, mantenimiento, versión y superficie de seguridad antes de añadirla.
- No envuelvas una dependencia «para poder cambiarla» si el wrapper no aporta comportamiento.
- Mantén `go.mod` y `go.sum` coherentes; ejecuta `go mod tidy` después de un cambio de imports.
- Fija versiones en CI cuando la herramienta lo permita. No actualices dependencias dentro de un cambio funcional sin relación.

## 9. Comentarios y documentación

- El comentario explica el porqué, la invariante o la decisión no obvia. No repite lo que el código ya dice.
- Todo símbolo exportado que forme API pública lleva comentario que empieza por su nombre.
- Un `TODO` incluye qué falta y qué lo desbloquea; no se usa como sustituto de una decisión.
- Los ejemplos ejecutables (`ExampleXxx`) son documentación verificada; si existen, deben compilar y producir la salida declarada.

## 10. Lista rápida de estilo

- [ ] `gofmt` limpio y `go vet` sin hallazgos.
- [ ] Sin `util`, `common`, `helpers` ni `shared`.
- [ ] Sin interfaces, genéricos u opciones sin uso real.
- [ ] `main` delgado y `os.Exit` solo allí.
- [ ] Sin estado global mutable ni `init` con efectos.
- [ ] Errores comprobados; ninguno descartado sin justificación.
- [ ] `append` asignado; maps inicializados; structs con campos nombrados.
- [ ] Nombres sin repetición de contexto y acrónimos coherentes.
- [ ] Dependencias justificadas y `go.mod` coherente.
- [ ] Sin reformateos ajenos ni cambios de comportamiento mezclados.
