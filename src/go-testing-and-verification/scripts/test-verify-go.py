#!/usr/bin/env python3
"""Pruebas del script verify-go.py con módulos Go temporales."""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("verify-go.py")
SPEC = importlib.util.spec_from_file_location("verify_go", SCRIPT)
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)

FORMATTED = """package main

func main() {
	println("ok")
}
"""

UNFORMATTED = """package main
func main(){println("ok")}
"""


def run(root, *args, env=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
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

    def test_gofmt_skips_vendor_testdata_and_hidden(self):
        root = self.make_module(FORMATTED)
        for relative in ("vendor/lib/lib.go", "testdata/fixture.go", ".hidden/hidden.go"):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("package x\nfunc F(){ }\n", encoding="utf-8", newline="\n")

        result = run(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_gofmt_reports_only_module_files(self):
        root = self.make_module(UNFORMATTED)
        path = root / "vendor" / "lib" / "lib.go"
        path.parent.mkdir(parents=True)
        path.write_text("package lib\nfunc F(){ }\n", encoding="utf-8", newline="\n")

        result = run(root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("main.go", result.stdout)
        self.assertNotIn("vendor", result.stdout)

    def test_text_and_json_agree_on_failure(self):
        root = self.make_module(UNFORMATTED)
        text = run(root)
        data = run(root, "--json")

        self.assertEqual(text.returncode, 1, text.stdout + text.stderr)
        self.assertIn("FAIL", text.stdout)
        self.assertEqual(data.returncode, 1, data.stdout + data.stderr)

        payload = json.loads(data.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(
            [check["name"] for check in payload["checks"] if check["status"] == "failed"],
            ["gofmt"],
        )

    def test_missing_go_is_usage_error(self):
        result = run(self.make_module(FORMATTED), env={**os.environ, "PATH": ""})
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("go is not available", result.stderr)

    def test_launch_failure_is_reported_without_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            code, output = VERIFY.run(
                ["definitely-missing-verify-go-tool"], Path(temporary), 5
            )
        self.assertIsNone(code)
        self.assertIn("could not run", output)
        self.assertNotIn("Traceback", output)

    def test_permission_failure_is_reported_without_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            code, output = VERIFY.run([temporary], Path(temporary), 5)
        self.assertIsNone(code)
        self.assertIn("could not run", output)
        self.assertNotIn("Traceback", output)

    def test_timeout_is_reported_without_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            code, output = VERIFY.run(
                [sys.executable, "-c", "import time; time.sleep(5)"],
                Path(temporary),
                1,
            )
        self.assertIsNone(code)
        self.assertIn("timed out after 1s", output)
        self.assertNotIn("Traceback", output)

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
