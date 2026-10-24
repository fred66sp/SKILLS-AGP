#!/usr/bin/env python3
"""Pruebas del script verify-ts.py con proyectos TypeScript temporales."""

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).with_name("verify-ts.py")
SPEC = importlib.util.spec_from_file_location("verify_ts", SCRIPT)
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def make_project(package, name="package.json"):
    temporary = tempfile.TemporaryDirectory()
    project = Path(temporary.name)
    write(project / name, json.dumps(package))
    return temporary, project


def invoke(project, *flags, which=None, run_result=(0, "")):
    available = which or {}

    def lookup(name):
        return available.get(name)

    with mock.patch.object(VERIFY.shutil, "which", side_effect=lookup), \
            mock.patch.object(VERIFY, "run", return_value=run_result) as runner:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = VERIFY.main(["--root", str(project), *flags])
    return code, stdout.getvalue(), stderr.getvalue(), runner


class VerifyTsTest(unittest.TestCase):
    def test_typecheck_script_uses_package_manager(self):
        temporary, project = make_project({
            "packageManager": "npm@10.0.0",
            "scripts": {"typecheck": "tsc --noEmit"},
        })
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, runner = invoke(project, which={"npm": "/usr/bin/npm"})

        self.assertEqual(code, 0, stdout + stderr)
        self.assertIn("PASS", stdout)
        runner.assert_called_once_with(
            ["/usr/bin/npm", "run", "typecheck"], project.resolve(), 600
        )

    def test_local_tsc_is_used_without_script(self):
        temporary, project = make_project({})
        self.addCleanup(temporary.cleanup)
        tsc = project / "node_modules" / "typescript" / "bin" / "tsc"
        write(tsc, "")

        code, stdout, stderr, runner = invoke(
            project, which={"npm": "/usr/bin/npm", "node": "/usr/bin/node"}
        )

        self.assertEqual(code, 0, stdout + stderr)
        runner.assert_called_once_with(
            ["/usr/bin/node", str(tsc), "--noEmit"], project.resolve(), 600
        )

    def test_missing_typescript_fails_with_actionable_message(self):
        temporary, project = make_project({})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(
            project, which={"npm": "/usr/bin/npm", "node": "/usr/bin/node"}
        )

        self.assertEqual(code, 1, stdout + stderr)
        self.assertIn("typescript is not installed", stdout)

    def test_requested_script_must_exist(self):
        temporary, project = make_project({
            "scripts": {"typecheck": "tsc --noEmit"},
        })
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, runner = invoke(
            project, "--lint", which={"npm": "/usr/bin/npm"}
        )

        self.assertEqual(code, 1, stdout + stderr)
        self.assertIn('no "lint" script', stdout)
        runner.assert_called_once()

    def test_text_and_json_agree_on_failure(self):
        temporary, project = make_project({
            "scripts": {"typecheck": "tsc --noEmit"},
        })
        self.addCleanup(temporary.cleanup)

        text_code, text_out, text_err, _ = invoke(
            project, "--test", which={"npm": "/usr/bin/npm"}
        )
        json_code, json_out, json_err, _ = invoke(
            project, "--test", "--json", which={"npm": "/usr/bin/npm"}
        )

        self.assertEqual(text_code, 1, text_out + text_err)
        self.assertIn("FAIL", text_out)
        self.assertEqual(json_code, 1, json_out + json_err)

        payload = json.loads(json_out)
        self.assertFalse(payload["ok"])
        self.assertEqual(
            [check["name"] for check in payload["checks"] if check["status"] == "failed"],
            ["test"],
        )

    def test_multiple_lockfiles_is_usage_error(self):
        temporary, project = make_project({})
        self.addCleanup(temporary.cleanup)
        write(project / "package-lock.json", "{}")
        write(project / "pnpm-lock.yaml", "lockfileVersion: 9\n")

        code, stdout, stderr, runner = invoke(project, which={"npm": "/usr/bin/npm"})

        self.assertEqual(code, 2, stdout + stderr)
        self.assertIn("multiple lockfiles", stderr)
        runner.assert_not_called()

    def test_declared_manager_wins_over_lockfile(self):
        temporary, project = make_project({
            "packageManager": "pnpm@9.0.0",
            "scripts": {"typecheck": "tsc --noEmit"},
        })
        self.addCleanup(temporary.cleanup)
        write(project / "package-lock.json", "{}")

        code, stdout, stderr, runner = invoke(
            project, which={"pnpm": "/usr/bin/pnpm"}
        )

        self.assertEqual(code, 0, stdout + stderr)
        runner.assert_called_once_with(
            ["/usr/bin/pnpm", "run", "typecheck"], project.resolve(), 600
        )

    def test_unsupported_manager_is_usage_error(self):
        temporary, project = make_project({"packageManager": "deno@2.0.0"})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project)

        self.assertEqual(code, 2, stdout + stderr)
        self.assertIn("unsupported packageManager", stderr)

    def test_missing_package_json_is_usage_error(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(Path(temporary.name))

        self.assertEqual(code, 2, stdout + stderr)
        self.assertIn("package.json does not exist", stderr)

    def test_missing_manager_is_usage_error(self):
        temporary, project = make_project({"packageManager": "bun@1.0.0"})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project)

        self.assertEqual(code, 2, stdout + stderr)
        self.assertIn("bun is not available", stderr)

    def test_invalid_timeout_is_usage_error(self):
        temporary, project = make_project({})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project, "--timeout", "0")

        self.assertEqual(code, 2, stdout + stderr)
        self.assertIn("--timeout must be greater than zero", stderr)

    def test_json_reports_each_requested_check(self):
        temporary, project = make_project({
            "packageManager": "npm@10.0.0",
            "scripts": {
                "typecheck": "tsc --noEmit",
                "lint": "eslint .",
                "test": "vitest run",
                "build": "tsc",
            },
        })
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(
            project, "--lint", "--test", "--build", "--json",
            which={"npm": "/usr/bin/npm"},
        )

        self.assertEqual(code, 0, stdout + stderr)
        payload = json.loads(stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(
            [check["name"] for check in payload["checks"]],
            ["typecheck", "lint", "test", "build"],
        )

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

    def test_launch_failure_is_reported_without_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            code, output = VERIFY.run(
                ["definitely-missing-verify-ts-tool"], Path(temporary), 5
            )
        self.assertIsNone(code)
        self.assertIn("could not run", output)
        self.assertNotIn("Traceback", output)


if __name__ == "__main__":
    unittest.main()
