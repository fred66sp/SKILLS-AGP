#!/usr/bin/env python3
"""Pruebas de preflight.py con espacios de trabajo temporales."""

import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("preflight.py")
SPEC = importlib.util.spec_from_file_location("preflight", SCRIPT)
PREFLIGHT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREFLIGHT)


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def fake_binary(root, body='echo "1.2.3"', code=0):
    path = root / "fake-playwright-cli"
    write(path, f"#!/bin/sh\n{body}\nexit {code}\n")
    path.chmod(0o755)
    return path


class PreflightTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_ready_binary_reports_version(self):
        binary = fake_binary(self.root)
        report = PREFLIGHT.check_environment(self.root, str(binary))
        self.assertTrue(report["ready"])
        self.assertEqual(report["binary"]["version"], "1.2.3")
        self.assertEqual(report["notes"], [])

    def test_missing_binary_is_not_ready(self):
        report = PREFLIGHT.check_environment(self.root, "playwright-cli-que-no-existe")
        self.assertFalse(report["ready"])
        self.assertIsNone(report["binary"]["path"])
        self.assertTrue(any("no se encontró" in note for note in report["notes"]))

    def test_failing_binary_is_not_ready(self):
        binary = fake_binary(self.root, body='echo "boom" >&2', code=3)
        report = PREFLIGHT.check_environment(self.root, str(binary))
        self.assertFalse(report["ready"])
        self.assertTrue(any("devolvió 3" in note for note in report["notes"]))

    def test_empty_version_is_not_ready(self):
        binary = fake_binary(self.root, body="true")
        report = PREFLIGHT.check_environment(self.root, str(binary))
        self.assertFalse(report["ready"])
        self.assertTrue(any("no imprimió versión" in note for note in report["notes"]))

    def test_workspace_config_is_detected(self):
        write(self.root / ".playwright" / "cli.config.json", "{}\n")
        report = PREFLIGHT.check_environment(self.root, "playwright-cli-que-no-existe")
        self.assertTrue(report["workspace_config"])

    def test_artifacts_are_counted(self):
        write(self.root / ".playwright-cli" / "page-1.yml", "- tree\n")
        write(self.root / ".playwright-cli" / "page-2.yml", "- tree\n")
        report = PREFLIGHT.check_environment(self.root, "playwright-cli-que-no-existe")
        artifact = {item["path"]: item for item in report["artifacts"]}[".playwright-cli"]
        self.assertEqual(artifact["files"], 2)

    def test_gitignore_coverage_is_reported(self):
        write(self.root / ".playwright-cli" / "page.yml", "- tree\n")
        write(self.root / ".gitignore", "node_modules/\n/.playwright-cli/\ntest-results/\n")
        report = PREFLIGHT.check_environment(self.root, "playwright-cli-que-no-existe")
        self.assertEqual(report["gitignore"]["ignored"], [".playwright-cli", "test-results"])
        self.assertEqual(report["gitignore"]["missing"], [])

    def test_uncovered_artifact_is_reported(self):
        write(self.root / "playwright-report" / "index.html", "<html></html>\n")
        write(self.root / ".gitignore", "node_modules/\n")
        report = PREFLIGHT.check_environment(self.root, "playwright-cli-que-no-existe")
        self.assertEqual(report["gitignore"]["missing"], ["playwright-report"])

    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = PREFLIGHT.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_main_exit_zero_when_ready(self):
        binary = fake_binary(self.root)
        code, out, _ = self.run_main(["--root", str(self.root), "--binary", str(binary)])
        self.assertEqual(code, 0)
        self.assertIn("conclusión: listo", out)

    def test_main_exit_one_when_blocked(self):
        code, out, _ = self.run_main(
            ["--root", str(self.root), "--binary", "playwright-cli-que-no-existe"]
        )
        self.assertEqual(code, 1)
        self.assertIn("conclusión: bloqueado", out)

    def test_main_json_output(self):
        binary = fake_binary(self.root)
        code, out, _ = self.run_main(
            ["--root", str(self.root), "--binary", str(binary), "--json"]
        )
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)["ready"])

    def test_main_rejects_missing_root(self):
        code, _, err = self.run_main(["--root", str(self.root / "no-existe")])
        self.assertEqual(code, 2)
        self.assertIn("no es un directorio", err)


if __name__ == "__main__":
    unittest.main()
