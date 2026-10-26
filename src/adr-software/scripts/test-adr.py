#!/usr/bin/env python3
"""Pruebas de scripts/adr.py.

Uso:
    python3 src/adr-software/scripts/test-adr.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "adr.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import adr  # noqa: E402


CLEAN_ADR = """---
status: proposed
date: 2026-01-10
decision-makers: "Ana, Luis"
---

# Adoptar PostgreSQL 16

## Contexto y problema

Las pruebas necesitan una base de datos compatible con producción.

## Decisión

Usar PostgreSQL 16 en producción. No-goals: no se migra a otro motor.

## Consecuencias

- Good, porque la paridad con producción es completa.
- Bad, porque hay que aprovisionar infraestructura.

## Más información

Seguimiento: configurar el entorno de pruebas.
"""


class AdrTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=str(self.root),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def repo_with_adr(self, name: str = "0001-adoptar-postgresql-16.md", body: str = CLEAN_ADR) -> Path:
        adr_dir = self.root / "docs" / "decisions"
        adr_dir.mkdir(parents=True)
        path = adr_dir / name
        path.write_text(body, encoding="utf-8")
        (adr_dir / "README.md").write_text(
            "# ADR\n\n## ADR\n\n- [Adoptar PostgreSQL 16](%s) (proposed, 2026-01-10)\n" % name,
            encoding="utf-8",
        )
        return path

    def test_slugify_strips_accents_and_symbols(self) -> None:
        self.assertEqual(adr.slugify("Adoptar PostgreSQL 16"), "adoptar-postgresql-16")
        self.assertEqual(adr.slugify("Sustituir decisión: ¿A o B?"), "sustituir-decision-a-o-b")
        self.assertEqual(adr.slugify("!!!"), "decision")

    def test_new_creates_numbered_adr_six_digits(self) -> None:
        result = self.run_cli("new", "--title", "Adoptar PostgreSQL 16", "--deciders", "Ana, Luis")
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.root / "adr" / "0001-adoptar-postgresql-16.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn("status: proposed", text)
        self.assertIn("decision-makers: \"Ana, Luis\"", text)
        self.assertIn("# Adoptar PostgreSQL 16", text)

    def test_new_respects_existing_width_and_number(self) -> None:
        adr_dir = self.root / "adr"
        adr_dir.mkdir()
        (adr_dir / "007-primera.md").write_text(CLEAN_ADR, encoding="utf-8")
        result = self.run_cli("new", "--title", "Segunda")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((adr_dir / "008-segunda.md").is_file())

    def test_new_uses_slug_strategy_for_existing_slug_repo(self) -> None:
        adr_dir = self.root / "adr"
        adr_dir.mkdir()
        (adr_dir / "primera.md").write_text(CLEAN_ADR, encoding="utf-8")
        result = self.run_cli("new", "--title", "Segunda decisión")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((adr_dir / "segunda-decision.md").is_file())

    def test_new_dry_run_writes_nothing(self) -> None:
        result = self.run_cli("new", "--title", "Adoptar", "--dry-run")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(list((self.root / "adr").glob("*.md")) if (self.root / "adr").exists() else [], [])

    def test_new_json_envelope(self) -> None:
        result = self.run_cli("new", "--title", "Adoptar", "--json")
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["operation"], "new")
        self.assertEqual(payload["strategy"], "number")

    def test_new_rejects_empty_title(self) -> None:
        result = self.run_cli("new", "--title", "   ")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--title", result.stderr)

    def test_new_index_outside_dir_writes_nothing(self) -> None:
        outside = self.root / "otro" / "index-fuera.md"
        result = self.run_cli("new", "--title", "Adoptar", "--index-file", str(outside))
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / "adr" / "0001-adoptar.md").exists())

    def test_new_updates_index_by_default(self) -> None:
        result = self.run_cli("new", "--title", "Adoptar")
        self.assertEqual(result.returncode, 0, result.stderr)
        index = (self.root / "adr" / "README.md").read_text(encoding="utf-8")
        self.assertIn("0001-adoptar.md", index)

    def test_new_can_skip_index(self) -> None:
        result = self.run_cli("new", "--title", "Adoptar", "--no-update-index")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / "adr" / "README.md").exists())

    def test_new_updates_index_once_per_adr(self) -> None:
        for title in ("Primera", "Segunda"):
            result = self.run_cli("new", "--title", title, "--update-index")
            self.assertEqual(result.returncode, 0, result.stderr)
        index = (self.root / "adr" / "README.md").read_text(encoding="utf-8")
        self.assertEqual(index.count("(proposed,"), 2)

    def test_status_updates_frontmatter_and_index(self) -> None:
        path = self.repo_with_adr()
        result = self.run_cli("status", str(path), "--status", "accepted", "--date", "2026-02-01")
        self.assertEqual(result.returncode, 0, result.stderr)
        text = path.read_text(encoding="utf-8")
        self.assertIn("status: accepted", text)
        self.assertIn("date: 2026-02-01", text)
        index = (path.parent / "README.md").read_text(encoding="utf-8")
        self.assertIn("(accepted, 2026-02-01)", index)

    def test_status_superseded_requires_target(self) -> None:
        path = self.repo_with_adr()
        result = self.run_cli("status", str(path), "--status", "superseded")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--superseded-by", result.stderr)

    def test_status_superseded_writes_link(self) -> None:
        first = self.repo_with_adr()
        second = first.parent / "0002-nueva.md"
        second.write_text(CLEAN_ADR.replace("Adoptar PostgreSQL 16", "Migrar a PostgreSQL 17"), encoding="utf-8")
        result = self.run_cli("status", str(first), "--status", "superseded", "--superseded-by", second.name)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("superseded by [ADR-0002](0002-nueva.md)", first.read_text(encoding="utf-8"))

    def test_status_rejects_unknown_status(self) -> None:
        path = self.repo_with_adr()
        result = self.run_cli("status", str(path), "--status", "aprobado")
        self.assertEqual(result.returncode, 2)

    def test_bootstrap_creates_clean_tree(self) -> None:
        result = self.run_cli("bootstrap", "--dir", "docs/decisions", "--deciders", "Ana, Luis")
        self.assertEqual(result.returncode, 0, result.stderr)
        adr_dir = self.root / "docs" / "decisions"
        self.assertTrue((adr_dir / "README.md").is_file())
        self.assertEqual(len(list(adr_dir.glob("0*.md"))), 1)
        check = self.run_cli("check", "--root", str(self.root))
        self.assertEqual(check.returncode, 0, check.stderr)
        self.assertIn("Directorio: `docs/decisions`", (adr_dir / "README.md").read_text(encoding="utf-8"))

    def test_bootstrap_is_idempotent(self) -> None:
        self.run_cli("bootstrap", "--dir", "docs/decisions", "--deciders", "Ana")
        result = self.run_cli("bootstrap", "--dir", "docs/decisions", "--deciders", "Ana")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list((self.root / "docs" / "decisions").glob("0*.md"))), 1)

    def test_check_clean_adr(self) -> None:
        self.repo_with_adr()
        result = self.run_cli("check", "--root", str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_flags_placeholders_and_missing_deciders(self) -> None:
        self.run_cli("new", "--title", "Adoptar")
        result = self.run_cli("check", "--root", str(self.root))
        self.assertEqual(result.returncode, 1)
        self.assertIn("[plantilla]", result.stderr)
        self.assertIn("[frontmatter]", result.stderr)

    def test_check_flags_supersede_without_backlink(self) -> None:
        first = self.repo_with_adr()
        second = first.parent / "0002-nueva.md"
        second.write_text(CLEAN_ADR, encoding="utf-8")
        first.write_text(CLEAN_ADR.replace("status: proposed", "status: superseded by [ADR-0002](0002-nueva.md)"), encoding="utf-8")
        result = self.run_cli("check", "--root", str(self.root))
        self.assertEqual(result.returncode, 1)
        self.assertIn("[supersede]", result.stderr)

    def test_check_flags_missing_index_entry(self) -> None:
        path = self.repo_with_adr()
        (path.parent / "README.md").write_text("# ADR\n\n## ADR\n", encoding="utf-8")
        result = self.run_cli("check", "--root", str(self.root))
        self.assertEqual(result.returncode, 1)
        self.assertIn("[indice]", result.stderr)

    def test_check_flags_invalid_real_date(self) -> None:
        self.repo_with_adr(body=CLEAN_ADR.replace("2026-01-10", "2026-02-31"))
        result = self.run_cli("check", "--root", str(self.root))
        self.assertEqual(result.returncode, 1)
        self.assertIn("no es una fecha real", result.stderr)

    def test_bootstrap_rejects_force_index_with_adrs(self) -> None:
        self.run_cli("bootstrap", "--dir", "docs/decisions", "--deciders", "Ana")
        result = self.run_cli("bootstrap", "--dir", "docs/decisions", "--force-index")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--force-index", result.stderr)

    def test_bootstrap_rejects_unknown_status(self) -> None:
        result = self.run_cli("bootstrap", "--dir", "adr", "--first-status", "aprobado")
        self.assertEqual(result.returncode, 2)

    def test_check_reports_missing_explicit_dir(self) -> None:
        result = self.run_cli("check", "--root", str(self.root), "--dir", "no-existe")
        self.assertEqual(result.returncode, 1)
        self.assertIn("[estructura]", result.stderr)

    def test_check_json_shape(self) -> None:
        self.repo_with_adr()
        result = self.run_cli("check", "--root", str(self.root), "--json")
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["findings"], [])

    def test_usage_error_json_envelope(self) -> None:
        path = self.repo_with_adr()
        result = self.run_cli("status", str(path), "--status", "aprobado", "--json")
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["ok"])
        self.assertIn("estado no admitido", payload["error"])

    def test_usage_error_is_exit_two(self) -> None:
        result = self.run_cli("inventado")
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
