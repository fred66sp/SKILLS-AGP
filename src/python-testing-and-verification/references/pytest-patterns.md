# Patrones de prueba

Léela en el paso 3, al escribir el caso.

## 1. Organización

```text
tests/
├── conftest.py          # fixtures compartidos, sin lógica de negocio
├── test_precios.py      # un módulo o un comportamiento por fichero
├── test_cli.py          # el proceso, no la función interna
└── fixtures/
    └── pedido.json      # datos compartidos, recortados al mínimo
```

- `tests/` fuera del paquete. En layout `src/`, el paquete se instala en modo editable y las pruebas lo importan por su nombre, nunca por ruta relativa.
- `conftest.py` contiene fixtures, no aserciones ni importaciones de conveniencia.
- Un nombre de test es una frase del comportamiento: `test_rechaza_cantidad_negativa`, no `test_calcular_2`.

## 2. `unittest`

```python
import unittest


class PrecioTest(unittest.TestCase):
    def test_redondea_a_dos_decimales(self):
        self.assertEqual(calcular_total("10.005"), Decimal("10.01"))

    def test_rechaza_cantidad_negativa(self):
        with self.assertRaises(ValueError) as ctx:
            calcular_total("-1")
        self.assertIn("cantidad", str(ctx.exception))
```

- `setUp` para el estado común; `addCleanup` para lo que debe deshacerse. Un `tearDown` que falla oculta el fallo original.
- `subTest` parametriza dentro de una clase; los casos siguen siendo independientes.
- `assertRaises` como context manager cuando se comprueba el mensaje; como llamada cuando solo importa el tipo.

## 3. `pytest`

```python
import pytest


@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [("0", 0), ("10.005", 1001), ("-1", None)],
    ids=["cero", "redondeo", "negativo"],
)
def test_total(entrada, esperado):
    if esperado is None:
        with pytest.raises(ValueError):
            calcular_total(entrada)
    else:
        assert calcular_total(entrada) == esperado
```

- `parametrize` para el mismo camino con entradas distintas; `ids` cuando el valor no se lee.
- `pytest.raises(Error, match="...")` para el mensaje; `match` es una regex, no una igualdad.
- `pytest.approx` para `float`; nunca `==` con coma flotante.
- `pytest.mark.skipif` para un límite de plataforma declarado, no para esconder un fallo.
- `-x` durante el desarrollo, la suite completa antes de cerrar.

## 4. Fixtures

| Fixture | Uso | Cuidado |
|---|---|---|
| `tmp_path` | Ficheros y directorios por test | Es único por test; no se reutiliza entre tests |
| `monkeypatch` | Variables de entorno, atributos y `cwd` | Se restaura al terminar el test |
| `capsys` | `stdout` y `stderr` | No captura salida de un subproceso |
| `caplog` | Registros de `logging` | Fija el nivel en el test |
| Propio | Recurso del dominio | `yield` y limpieza en el `finally` |

```python
@pytest.fixture
def cliente(tmp_path):
    ruta = tmp_path / "datos.json"
    ruta.write_text("{}", encoding="utf-8")
    return Cliente(ruta)
```

- Un fixture con `scope="session"` solo para un recurso caro e inmutable. Un fixture de sesión mutable comparte estado entre tests.
- Un fixture no contiene aserciones ni lógica de negocio.
- Una dependencia entre fixtures se declara por parámetro, no por importación.

## 5. `unittest.mock`

- `mock.patch` como decorador o context manager; la ruta se parchea donde se usa, no donde se define.
- `autospec=True` para que la firma se compruebe. Sin él, un mock acepta cualquier argumento.
- `mock.patch.dict(os.environ, {...}, clear=True)` para un entorno aislado.
- No se parchea lo que se está probando. Se parchea la frontera.
- `assert_called_once_with` comprueba la llamada, no el efecto. Si el efecto importa, se comprueba el efecto.

## 6. Diagnóstico

- En `unittest`, el mensaje va en la aserción: `self.assertEqual(got, want, f"entrada={entrada!r}")`.
- En `pytest`, la aserción ya imprime los valores; añade contexto solo cuando el valor no se lee.
- Un fallo intermitente se reproduce con `-p no:randomly` o repitiendo la suite; no se arregla con un `sleep`.
- Un test que falla solo en CI declara la diferencia: versión de Python, variable de entorno, sistema operativo.
- Los warnings se tratan como señales: `filterwarnings = ["error"]` en `pyproject.toml` convierte un `DeprecationWarning` en fallo, y se corrige el origen.

## 7. Marcadores y configuración

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
markers = ["slow: tarda más de un segundo", "network: requiere un servicio local"]
```

- Un marcador que no está declarado falla con `--strict-markers`; así no se escribe `@pytest.mark.slow` sin registrarlo.
- `-m "not slow"` para el bucle rápido; el cierre ejecuta la suite completa.
- La configuración vive en `pyproject.toml`, compartida por CI y editor.

## 8. Errores frecuentes

| Síntoma | Causa | Corrección |
|---|---|---|
| El test pasa con el doble y falla en producción | El doble no reproduce el contrato | Dobla la frontera real o añade una prueba de integración |
| El test falla solo en la suite | Estado compartido entre tests | Fixture por test, sin mutables de módulo |
| La fecha del test cambia | Reloj real | Inyecta el reloj o fija la fecha |
| El test no captura el error | `except Exception` en el código bajo prueba | Corrige el código; no relajes la aserción |
| `capsys` no ve la salida | Es de un subproceso | Usa `subprocess.run` y captura su salida |
| El test deja ficheros | Ruta fija en el repositorio | `tmp_path` |
