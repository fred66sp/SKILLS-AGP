#!/usr/bin/env python3
"""Pruebas del script verify-go.py con módulos Go temporales."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("verify-go.py")

FORMATTED = """package main

func main() {
	println("ok")
}
"""

UNFORMATTED = """package main
func main(){println("ok")}
"""


def run(root, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


class VerifyGoTest(unittest.TestCase):
    def make_module(self, source):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)

        root = Path(temporary.name)
        (root / "go.mod").write_text("module example.com/demo\n\ngo 1.21\n", encoding="utf-8", newline="\n")
        (root / "main.go").write_text(source, encoding="utf-8", newline="\n")
        return root

    def test_formatted_module_passes(self):
        result = run(self.make_module(FORMATTED))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_unformatted_module_fails(self):
        result = run(self.make_module(UNFORMATTED))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("gofmt", result.stdout)
        self.assertIn("main.go", result.stdout)

    def test_json_reports_each_check(self):
        result = run(self.make_module(FORMATTED), "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(
            [check["name"] for check in payload["checks"]],
            ["gofmt", "build", "test", "vet"],
        )

    def test_missing_root_is_usage_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "missing"
            result = run(root)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
