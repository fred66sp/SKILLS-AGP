# Fronteras y proceso

Léela en el paso 5, cuando el riesgo sea dato no confiable, un cliente externo o una CLI.

## 1. Validar la frontera en runtime

Una anotación no rechaza nada. En el punto donde el dato entra —fichero, entorno, HTTP, cola, base de datos— se comprueba y se convierte a un tipo del dominio.

```python
def cargar_config(ruta: Path) -> Config:
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    if not isinstance(datos, dict):
        raise ConfigError("la configuración debe ser un objeto JSON")
    puerto = datos.get("puerto")
    if not isinstance(puerto, int) or not 1 <= puerto <= 65535:
        raise ConfigError(f"puerto inválido: {puerto!r}")
    return Config(puerto=puerto)
```

- La comprobación se prueba con el caso válido y con cada rechazo: tipo incorrecto, rango, clave ausente, fichero inexistente.
- El mensaje nombra el campo y el valor recibido; no incluye el contenido completo si puede contener un secreto.
- `bool` es subclase de `int`: exclúyelo antes de comprobar un entero.
- Un `dict` externo se convierte a un `dataclass` o `TypedDict` en la frontera; el dominio no recibe diccionarios sueltos.
- `float` de un JSON puede ser `int`: decide y documenta qué aceptas.

## 2. Dobles de red

| Herramienta | Uso | Límite |
|---|---|---|
| `httpx.MockTransport` | Cliente `httpx` | Solo prueba tu cliente, no el servidor |
| `responses` | Cliente `requests` | Dependencia solo si ya existe |
| Servidor local (`http.server`, `uvicorn` en test) | Contrato real de tu servicio | Más lento; se reserva a la integración |
| Cliente inyectado | Cualquier transporte | El doble no demuestra que la URL sea correcta |

Un doble declara estado, cabeceras y cuerpo. Se prueban el error HTTP, el JSON inválido, el timeout y la cancelación, no solo el camino feliz. Un doble que devuelve siempre `200` demuestra que tu código llama al doble.

## 3. Tiempo, azar y entorno

- El reloj se inyecta (`now: Callable[[], datetime]`) o se dobla en el módulo que lo consume. `freezegun` solo si ya está en el proyecto.
- `random` se sustituye por un generador con semilla fija; `secrets` no se prueba por valor, se prueba la forma.
- `monkeypatch.setenv` y `monkeypatch.delenv` restauran al terminar. Un test no hereda la variable del anterior.
- `TZ` y `LC_ALL` se fijan cuando el formato forma parte del resultado.
- Un test que cambia el directorio de trabajo lo restaura con `monkeypatch.chdir`.

## 4. Prueba de proceso

```python
import json
import subprocess
import sys


def test_json_valido(tmp_path):
    resultado = subprocess.run(
        [sys.executable, "-m", "paquete", "--json", "--config", str(tmp_path / "c.json")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stderr
    assert json.loads(resultado.stdout)["ok"] is True
    assert resultado.stderr == ""
```

- `sys.executable` garantiza el mismo intérprete que ejecuta la suite.
- `capture_output=True` separa `stdout` y `stderr`; se comprueban por separado.
- `timeout` explícito: un proceso colgado no bloquea CI para siempre.
- `check=False` para poder comprobar el código de salida.
- Casos mínimos: `--help`, `--version`, comando desconocido, flag inválido, `--dry-run`, falta de `--yes`, JSON válido y señal de interrupción.
- No se asume TTY. Un proceso sin terminal no debe esperar entrada.

## 5. Prueba de propiedad

- `Hypothesis` se usa solo si el proyecto ya lo tiene.
- Una estrategia genera datos del dominio, no `st.text()` genérico, que produce entradas que el contrato no acepta.
- Una propiedad afirma una invariante, no repite la implementación.
- Un fallo de Hypothesis deja un ejemplo reproducible; se añade como caso explícito de regresión.

## 6. Integración real

- Se reserva para la frontera cuyo comportamiento no controlas: base de datos, cola, servicio externo.
- Se marca (`@pytest.mark.integration` o `network`) y se ejecuta en un job separado si tarda.
- Un contenedor de prueba declara su versión; no se usa «la última» sin fijarla.
- Si el servicio no está disponible, el test falla o se omite con una razón visible; nunca pasa en silencio.

## 7. Límites que se declaran

- Red no disponible: se declara en el informe.
- Servicio externo sin entorno local: se declara el bloqueo.
- Plataforma distinta: se declara la diferencia y se ejecuta en CI si existe.
- Secreto ausente: el test se escribe con un literal falso; la integración real la ejecuta quien tenga la credencial.
