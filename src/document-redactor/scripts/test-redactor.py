#!/usr/bin/env python3
"""Pruebas de scripts/redactor.py.

Uso:
    python3 src/document-redactor/scripts/test-redactor.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "redactor.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import redactor  # noqa: E402


CLEAN = """# Guía de estilo del equipo

La biblioteca abre de lunes a sábado. Presta libros, organiza talleres y deja una
sala para estudiar.

El equipo son cuatro personas. Dos trabajan a media jornada y, desde 2019, el
resto se reparte entre la sala infantil, el mostrador y las visitas de institutos
que el año pasado llegaron a 1.200.

¿Quieres reservar la sala? Llama al 96 000 00 00.
"""


class RedactorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, body: str, name: str = "texto.md") -> Path:
        path = self.root / name
        path.write_text(body, encoding="utf-8")
        return path

    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=str(self.root),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def rules(self, body: str) -> list[str]:
        findings, _ = redactor.check(body)
        return [f["rule"] for f in findings]

    def test_clean_text_has_no_findings(self) -> None:
        self.assertEqual(self.rules(CLEAN), [])

    def test_curly_quotes_are_an_error(self) -> None:
        findings, _ = redactor.check("Dijo que “esto va” según lo previsto.\n")
        self.assertEqual([f["rule"] for f in findings], ["T01"])
        self.assertEqual(findings[0]["severity"], "error")

    def test_spaced_dash_and_double_hyphen(self) -> None:
        self.assertIn("T02", self.rules("El plazo — tres semanas — lo fijó el cliente.\n"))
        self.assertIn("T03", self.rules("Llegó tarde -- otra vez.\n"))

    def test_missing_opening_marks(self) -> None:
        self.assertIn("T04", self.rules("Vienes mañana?\n"))
        self.assertIn("T05", self.rules("Vaya sorpresa!\n"))

    def test_emoji_in_body(self) -> None:
        self.assertIn("T06", self.rules("Fase de lanzamiento: el producto sale en julio. 🚀\n"))

    def test_negative_parallelism(self) -> None:
        rules = self.rules("No solo ofrece libros, sino también un espacio de encuentro.\n")
        self.assertIn("P09", rules)

    def test_filler_and_generic_conclusion(self) -> None:
        rules = self.rules("Cabe destacar que los datos mejoran. En conclusión, todo va bien.\n")
        self.assertIn("P24", rules)
        self.assertIn("P26", rules)

    def test_code_blocks_and_inline_code_are_ignored(self) -> None:
        body = (
            "Ejecuta `redactor.py check --json` para ver el informe.\n\n"
            "```text\n-- comillas “curvas” y ¿sin apertura?\n```\n"
        )
        self.assertEqual(self.rules(body), [])

    def test_frontmatter_is_ignored(self) -> None:
        body = "---\ntitle: “Prueba”\n---\n\nTexto limpio y corto.\n"
        self.assertEqual(self.rules(body), [])

    def test_title_case_heading(self) -> None:
        self.assertIn("P17", self.rules("# Negociaciones Estratégicas Y Alianzas Globales\n"))

    def test_heading_with_brand_is_not_flagged(self) -> None:
        self.assertNotIn("P17", self.rules("# Guía de TypeScript y JavaScript\n"))

    def test_bold_label_list(self) -> None:
        body = "- **Experiencia:** mejorada.\n- **Rendimiento:** optimizado.\n"
        self.assertIn("P16", self.rules(body))

    def test_consecutive_connectors_form_a_cluster(self) -> None:
        body = (
            "Además, el equipo creció.\n\n"
            "Además, el coste bajó.\n\n"
            "Además, el plazo se cumplió.\n"
        )
        rules = self.rules(body)
        self.assertEqual(rules.count("P33"), 1)

    def test_uniform_rhythm_is_flagged(self) -> None:
        body = (
            "El equipo revisó el informe con calma y detectó tres errores menores. "
            "La dirección aprobó el plan después de leer las conclusiones del texto. "
            "El cliente firmó el contrato sin pedir cambios en las condiciones. "
            "La entrega se fijó para el lunes siguiente por la mañana temprano.\n"
        )
        self.assertIn("P32", self.rules(body))

    def test_varied_rhythm_is_not_flagged(self) -> None:
        body = (
            "El equipo revisó el informe. Encontró tres errores menores y, tras "
            "discutirlos con la dirección, decidió no reescribir la sección de "
            "costes porque el dato ya estaba aprobado por el cliente en marzo. "
            "Firmaron. La entrega quedó para el lunes.\n"
        )
        self.assertNotIn("P32", self.rules(body))

    def test_exit_code_zero_on_clean_text(self) -> None:
        result = self.run_cli("check", str(self.write(CLEAN)))
        self.assertEqual(result.returncode, 0)
        self.assertIn("0 hallazgos", result.stdout)

    def test_exit_code_one_on_typography_defect(self) -> None:
        result = self.run_cli("check", str(self.write("Dijo que “esto va”.\n")))
        self.assertEqual(result.returncode, 1)
        self.assertIn("T01", result.stdout)

    def test_warning_alone_does_not_fail_without_strict(self) -> None:
        path = self.write("No solo ofrece libros, sino también un espacio.\n")
        self.assertEqual(self.run_cli("check", str(path)).returncode, 0)
        self.assertEqual(self.run_cli("check", str(path), "--strict").returncode, 1)

    def test_json_output(self) -> None:
        result = self.run_cli("check", str(self.write("Dijo que “esto va”.\n")), "--json")
        data = json.loads(result.stdout)
        self.assertEqual(data["counts"]["errors"], 1)
        self.assertEqual(data["findings"][0]["rule"], "T01")
        self.assertEqual(data["stats"]["words"], 4)

    def test_stdin(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "check", "-"],
            input="¿Todo bien?\n", capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0)

    def test_missing_file_returns_two(self) -> None:
        result = self.run_cli("check", str(self.root / "no-existe.md"))
        self.assertEqual(result.returncode, 2)

    def test_requires_subcommand(self) -> None:
        self.assertEqual(self.run_cli().returncode, 2)


if __name__ == "__main__":
    unittest.main()
