# Proyecto y empaquetado

Léela en el paso 4, antes de tocar metadatos, layout, dependencias o build.

## 1. Una sola fuente

`pyproject.toml` contiene metadatos, dependencias y configuración de herramientas. Si el proyecto ya tiene `setup.cfg` o `requirements.txt`, se respeta su autoridad mientras exista; no se crea una cuarta fuente.

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "paquete"
dynamic = ["version"]
requires-python = ">=3.12"
dependencies = ["httpx>=0.27,<1"]

[project.optional-dependencies]
dev = ["pytest>=8", "ruff>=0.6", "mypy>=1.11"]

[project.scripts]
herramienta = "paquete.cli:main"

[tool.hatch.version]
path = "src/paquete/__init__.py"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "RUF"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"
```

Reglas:

- La versión se declara una vez. Si es dinámica, el backend la lee de un único sitio y no se repite en el README ni en un `__version__` escrito a mano en dos módulos.
- `requires-python` refleja lo que CI prueba. Declarar 3.9 sin ejecutarlo es una promesa sin evidencia.
- Un extra opcional (`dev`, `docs`, `postgres`) no se convierte en dependencia base.
- `dependencies` lleva rangos compatibles, no un `==` de la última versión, salvo una razón de compatibilidad documentada.

## 2. Layout

| Situación | Layout |
|---|---|
| Librería publicable | `src/<paquete>/` + `tests/` |
| Aplicación desplegable | `src/<paquete>/` o `<paquete>/`; un `main` y un adaptador por entrada |
| Script de un solo uso | Un `.py` sin paquete ni `__init__` |
| Varios paquetes con ciclo de vida propio | Monorepo con `pyproject.toml` por paquete; no por anticipación |

El layout `src/` evita que las pruebas importen el paquete por accidente desde el directorio actual. Un paquete plano es válido si el proyecto ya lo usa y el build funciona.

Dentro del paquete:

- `__init__.py` expone la API pública mínima con `__all__`. No importa submódulos pesados.
- Los adaptadores (HTTP, base de datos, CLI) viven separados del dominio. La dirección de dependencia apunta al dominio.
- `py.typed` se incluye si el paquete publica tipos; sin él, el consumidor ignora las anotaciones.

## 3. Dependencias

Orden de decisión:

1. Biblioteca estándar. `pathlib`, `json`, `sqlite3`, `urllib`, `dataclasses`, `argparse`, `logging`, `unittest` cubren más de lo que parece.
2. Una dependencia ya presente en el proyecto.
3. Una dependencia nueva, revisada en licencia, mantenimiento, tamaño y seguridad.

- Un solo gestor y un solo lockfile. `uv` es la elección por defecto cuando no hay otra declarada; `pip` + `requirements.txt` se respeta si ya existe.
- El lockfile se versiona en una aplicación y se decide en una librería: una librería publica rangos, no un lock.
- Añadir una dependencia exige decir qué se descartó y por qué. Una dependencia para una función de diez líneas no se acepta.
- Las dependencias de desarrollo no entran en el artefacto publicado.

Comandos habituales con `uv`:

```bash
uv sync --extra dev
uv add httpx
uv add --dev pytest
uv run pytest
uv run ruff check .
uv build
```

## 4. Linter y formateador

- `ruff format` formatea y `ruff check` analiza. No se ejecutan dos formateadores sobre el mismo árbol.
- Las reglas se eligen: el conjunto por defecto de ruff es pequeño. Añadir `B`, `SIM`, `UP`, `I` y `RUF` es razonable; añadir todo sin revisar genera ruido.
- `per-file-ignores` para tests o scripts concretos, nunca un `# noqa` global.
- La configuración vive en `pyproject.toml` para que CI y editor usen la misma.

## 5. Tipos

- `py.typed` en el paquete si publica anotaciones.
- El comprobador se configura en `pyproject.toml` y se ejecuta en CI. Sin configuración, el modo estricto no está activo aunque la herramienta esté instalada.
- Un `stub` propio (`.pyi`) solo para una dependencia sin tipos, no para reescribir el paquete.

## 6. Build y publicación

1. `python -m build` o `uv build` produce `sdist` y `wheel` en `dist/`.
2. Se inspecciona el contenido del wheel: sin tests, sin caches, sin secretos, con `py.typed` si aplica.
3. La instalación se prueba en un entorno limpio: `uv venv` y `uv pip install dist/*.whl`.
4. La publicación usa el token del registro solo en el paso de publicación, nunca en el entorno de desarrollo.
5. Una versión publicada es inmutable: un defecto se corrige con otra versión.

## 7. Qué no se hace

- No se versiona `.venv/`, `dist/`, `build/`, `*.egg-info/`, `__pycache__/` ni `.pytest_cache/`. El `.gitignore` lo declara.
- No se escribe `sys.path.append` para arreglar un import: se corrige el layout o el paquete.
- No se usa `pip install -e .` como sustituto de una instalación reproducible en CI.
- No se publica desde una máquina con credenciales de larga duración si el registro admite publicación confiable.
