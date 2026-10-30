#!/usr/bin/env python3
"""Pruebas de la puerta de forma case-check.py de la skill software-testing.

Se ejecuta la CLI real como proceso y se comprueban códigos de salida y
salidas de texto o JSON. Las plantillas reales de assets/ deben pasar sin
defectos: son el contrato de forma que copian los documentos de trabajo.

Uso:
    python3 test-case-check.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "case-check.py"
ASSETS = Path(__file__).resolve().parent.parent / "assets"

CASE_TEMPLATE = ASSETS / "test-case.md"
REPORT_TEMPLATE = ASSETS / "test-report.md"


def run_check(target: str | Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(target), *extra],
        capture_output=True,
        text=True,
        check=False,
    )


def write_doc(directory: Path, name: str, text: str) -> Path:
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return path


CASE_FULL = """---
tipo: caso
id: TC-001
---

# Caso de prueba TC-001: crear cuenta con correo duplicado

## Objetivo

Comprobar que el alta con un correo ya registrado no crea una segunda cuenta.

## Entorno

[entorno de pruebas]

## Precondiciones

- Existe la cuenta user@example.com.

## Pasos

1. Abre el formulario de alta.
2. Envía el correo user@example.com con una contraseña válida.

## Resultado esperado

El formulario rechaza el alta y muestra el mensaje de correo duplicado.

## Resultado observado

sin ejecutar

## Estado

pendiente

## Evidencia

sin ejecutar

## Notas

Cubre la partición de correo duplicado; no cubre formato inválido.
"""

REPORT_FULL = """---
tipo: informe
id: INF-001
---

# Informe de pruebas INF-001: alta de cuentas

## Alcance

Ronda sobre el alta de cuentas: casos TC-001 a TC-003. Queda fuera la recuperación de contraseña.

## Resultado global

aprobado

## Cobertura

- Lo probado: TC-001 superado, TC-002 superado, TC-003 fallado.
- Lo no probado y su motivo: recuperación de contraseña, fuera de alcance de la ronda.

## Defectos

- BUG-012: el mensaje de correo duplicado no aparece (mayor).

## No verificado

El comportamiento en navegadores distintos del declarado en el entorno.

## Riesgos residuales

Un fallo del proveedor de correo podría bloquear los altas reales.

## Métricas

- Casos ejecutados: 3 de 3
- Casos superados: 2
- Casos fallados: 1
- Casos bloqueados: 0

## Lecciones

El ángulo de correo duplicado llegó tarde: la partición se detectó en la revisión del diseño.
"""


class UsageErrors(unittest.TestCase):
    def test_missing_file_exits_two(self) -> None:
        result = run_check("/ruta/inexistente/caso.md")
        self.assertEqual(result.returncode, 2)
        self.assertIn("no existe", result.stderr)

    def test_undetectable_type_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_doc(Path(tmp), "suelt.md", "# Notas sueltas\n\nTexto sin tipo.\n")
            result = run_check(path)
            self.assertEqual(result.returncode, 2)
            self.assertIn("tipo", result.stderr.lower())

    def test_broken_frontmatter_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_doc(Path(tmp), "roto.md", "---\ntipo: caso\n# Sin cerrar\n\nTexto.\n")
            result = run_check(path)
            self.assertEqual(result.returncode, 2)
            self.assertIn("frontmatter", result.stderr.lower())

    def test_forced_type_overrides_autodetection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_doc(Path(tmp), "caso.md", CASE_FULL)
            result = run_check(path, "--tipo", "informe")
            self.assertEqual(result.returncode, 1)
            self.assertIn("E01", result.stdout)


class CaseChecks(unittest.TestCase):
    def test_real_case_template_passes(self) -> None:
        result = run_check(CASE_TEMPLATE)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("OK", result.stdout)
        self.assertNotIn("E0", result.stdout)

    def test_full_case_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_doc(Path(tmp), "caso.md", CASE_FULL)
            result = run_check(path)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_case_passed_without_evidence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = CASE_FULL.replace("## Estado\n\npendiente", "## Estado\n\nsuperado")
            path = write_doc(Path(tmp), "caso.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("E03", result.stdout)

    def test_case_passed_with_placeholder_evidence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = CASE_FULL.replace("## Estado\n\npendiente", "## Estado\n\nsuperado")
            path = write_doc(Path(tmp), "caso.md", text)
            result = run_check(path)
            self.assertIn("E03", result.stdout)

    def test_case_failed_with_evidence_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = CASE_FULL.replace("## Estado\n\npendiente", "## Estado\n\nfallado").replace(
                "## Evidencia\n\nsin ejecutar",
                "## Evidencia\n\nCaptura y consola en evidencia/TC-001.png",
            )
            path = write_doc(Path(tmp), "caso.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_invalid_state_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = CASE_FULL.replace("## Estado\n\npendiente", "## Estado\n\nquizá")
            path = write_doc(Path(tmp), "caso.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("E02", result.stdout)

    def test_feminine_state_is_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = CASE_FULL.replace("## Estado\n\npendiente", "## Estado\n\nsuperada").replace(
                "## Evidencia\n\nsin ejecutar",
                "## Evidencia\n\nSalida de consola registrada.",
            )
            path = write_doc(Path(tmp), "caso.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertNotIn("E02", result.stdout)

    def test_missing_section_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = CASE_FULL.replace("## Evidencia\n\nsin ejecutar\n\n", "")
            path = write_doc(Path(tmp), "caso.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("E01", result.stdout)
            self.assertIn("Evidencia", result.stdout)

    def test_steps_without_numbering_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = CASE_FULL.replace("1. Abre el formulario de alta.\n2. Envía el correo", "Abre el formulario de alta.\nEnvía el correo")
            path = write_doc(Path(tmp), "caso.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("E04", result.stdout)

    def test_blocked_state_warns_and_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = CASE_FULL.replace("## Estado\n\npendiente", "## Estado\n\nbloqueado")
            path = write_doc(Path(tmp), "caso.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("W01", result.stdout)

    def test_placeholders_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = CASE_FULL.replace("[entorno de pruebas]", "TODO por decidir")
            path = write_doc(Path(tmp), "caso.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("E05", result.stdout)

    def test_empty_bracket_without_dash_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = CASE_FULL.replace("[entorno de pruebas]", "sistema X, [ ]")
            path = write_doc(Path(tmp), "caso.md", text)
            result = run_check(path)
            self.assertIn("E05", result.stdout)

    def test_placeholder_inside_code_fence_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = CASE_FULL.replace(
                "## Evidencia\n\nsin ejecutar",
                "## Evidencia\n\n```\nTODO captura pendiente\n```",
            ).replace("## Estado\n\npendiente", "## Estado\n\nsuperado")
            path = write_doc(Path(tmp), "caso.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_autodetection_by_heading_without_frontmatter_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = CASE_FULL.replace("tipo: caso\n", "").replace("---\n", "", 1)
            path = write_doc(Path(tmp), "caso.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("caso", result.stdout)


class ReportChecks(unittest.TestCase):
    def test_real_report_template_passes(self) -> None:
        result = run_check(REPORT_TEMPLATE)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("OK", result.stdout)

    def test_full_report_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_doc(Path(tmp), "informe.md", REPORT_FULL)
            result = run_check(path)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_invalid_global_result_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = REPORT_FULL.replace("## Resultado global\n\naprobado", "## Resultado global\n\nmmm")
            path = write_doc(Path(tmp), "informe.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("E06", result.stdout)

    def test_coverage_without_gap_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = REPORT_FULL.replace("- Lo no probado y su motivo: recuperación de contraseña, fuera de alcance de la ronda.\n", "")
            path = write_doc(Path(tmp), "informe.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("E07", result.stdout)

    def test_incoherent_metrics_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = REPORT_FULL.replace("Casos ejecutados: 3 de 3", "Casos ejecutados: 2 de 3")
            path = write_doc(Path(tmp), "informe.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("E08", result.stdout)

    def test_coherent_metrics_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_doc(Path(tmp), "informe.md", REPORT_FULL)
            result = run_check(path)
            self.assertNotIn("E08", result.stdout)

    def test_metrics_without_integers_warn(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = REPORT_FULL.replace(
                "- Casos ejecutados: 3 de 3",
                "- Casos ejecutados: pendiente de cierre",
            )
            path = write_doc(Path(tmp), "informe.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("W02", result.stdout)

    def test_missing_section_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = REPORT_FULL.replace("## Lecciones\n\nEl ángulo de correo duplicado llegó tarde: la partición se detectó en la revisión del diseño.\n", "")
            path = write_doc(Path(tmp), "informe.md", text)
            result = run_check(path)
            self.assertEqual(result.returncode, 1)
            self.assertIn("E01", result.stdout)
            self.assertIn("Lecciones", result.stdout)


class JsonOutput(unittest.TestCase):
    def test_json_with_defects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            text = CASE_FULL.replace("## Estado\n\npendiente", "## Estado\n\nsuperado")
            path = write_doc(Path(tmp), "caso.md", text)
            result = run_check(path, "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["tipo"], "caso")
            self.assertTrue(payload["defectos"])
            self.assertIn(payload["defectos"][0]["codigo"], {"E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08"})

    def test_json_clean_template(self) -> None:
        result = run_check(CASE_TEMPLATE, "--json")
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["defectos"], [])
        self.assertEqual(payload["tipo"], "caso")


if __name__ == "__main__":
    unittest.main(verbosity=2)
