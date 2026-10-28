#!/usr/bin/env python3
"""Pruebas del script verify-js.py con proyectos JavaScript temporales."""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).with_name("verify-js.py")
SPEC = importlib.util.spec_from_file_location("verify_js", SCRIPT)
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)

MODULE_HINT = "Cannot use import statement outside a module"


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def make_project(files, package=None):
    temporary = tempfile.TemporaryDirectory()
    project = Path(temporary.name)
    if package is not None:
        write(project / "package.json", json.dumps(package))
    for name, content in files.items():
        write(project / name, content)
    return temporary, project


def version_aware(extra=None):
    """run() simulado: responde a --version y delega el resto en extra()."""
    def runner(command, cwd, timeout):
        if "--version" in command:
            return 0, "v24.20.0\n"
        if extra:
            return extra(command, cwd, timeout)
        return 0, ""
    return runner


def invoke(project, *flags, which=None, runner=None):
    available = {"node": "/usr/bin/node", "npm": "/usr/bin/npm"}
    available.update(which or {})

    def lookup(name):
        return available.get(name)

    with mock.patch.object(VERIFY.shutil, "which", side_effect=lookup), \
            mock.patch.object(VERIFY, "run", side_effect=runner or version_aware()) as running:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = VERIFY.main(["--root", str(project), *flags])
    return code, stdout.getvalue(), stderr.getvalue(), running


class VerifyJsTest(unittest.TestCase):
    def test_syntax_checks_every_source_file(self):
        temporary, project = make_project({
            "src/a.js": "export const a = 1;\n",
            "src/b.cjs": "module.exports = 1;\n",
            "src/c.mjs": "export const c = 1;\n",
        })
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, runner = invoke(project)

        self.assertEqual(code, 0, stdout + stderr)
        self.assertIn("PASS", stdout)
        checked = [call.args[0] for call in runner.call_args_list if "--check" in call.args[0]]
        self.assertEqual(len(checked), 3)
        self.assertTrue(all(call[0] == "/usr/bin/node" for call in checked))

    def test_syntax_failure_names_the_file(self):
        temporary, project = make_project({"src/bad.js": "var bad = ;\n"})

        def failing(command, cwd, timeout):
            if "--check" in command:
                return 1, "SyntaxError: Unexpected token ';'"
            return 0, ""

        code, stdout, stderr, _ = invoke(project, runner=version_aware(failing))
        self.addCleanup(temporary.cleanup)

        self.assertEqual(code, 1, stdout + stderr)
        self.assertIn("FAIL", stdout)
        self.assertIn("src/bad.js", stdout)
        self.assertIn("Unexpected token", stdout)

    def test_project_without_files_passes_with_note(self):
        temporary, project = make_project({})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project)

        self.assertEqual(code, 0, stdout + stderr)
        self.assertIn("no .js, .mjs or .cjs file", stdout)

    def test_dependencies_and_minified_files_are_skipped(self):
        temporary, project = make_project({
            "src/a.js": "export const a = 1;\n",
            "node_modules/pkg/b.js": "export const b = 1;\n",
            "dist/c.js": "export const c = 1;\n",
            "src/d.min.js": "var d=1;\n",
        })
        self.addCleanup(temporary.cleanup)

        _, _, _, runner = invoke(project)

        checked = [Path(call.args[0][-1]).name for call in runner.call_args_list if "--check" in call.args[0]]
        self.assertEqual(checked, ["a.js"])

    def test_missing_node_is_a_usage_error(self):
        temporary, project = make_project({})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project, which={"node": None})

        self.assertEqual(code, 2)
        self.assertIn("node is not available", stderr)

    def test_missing_root_is_a_usage_error(self):
        code, stdout, stderr, _ = invoke("/ruta/que/no/existe")

        self.assertEqual(code, 2)
        self.assertIn("not a directory", stderr)

    def test_zero_timeout_is_rejected(self):
        temporary, project = make_project({})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project, "--timeout", "0")

        self.assertEqual(code, 2)
        self.assertIn("--timeout", stderr)

    def test_test_flag_requires_package_json(self):
        temporary, project = make_project({})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project, "--test")

        self.assertEqual(code, 2)
        self.assertIn("package.json does not exist", stderr)

    def test_project_test_script_uses_package_manager(self):
        temporary, project = make_project({}, package={"scripts": {"test": "vitest run"}})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, runner = invoke(project, "--test")

        self.assertEqual(code, 0, stdout + stderr)
        commands = [call.args[0] for call in runner.call_args_list]
        self.assertIn(["/usr/bin/npm", "run", "test"], commands)

    def test_without_script_node_test_runs_discovered_files(self):
        temporary, project = make_project({"src/a.test.js": "import test from 'node:test';\n"}, package={})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, runner = invoke(project, "--test")

        self.assertEqual(code, 0, stdout + stderr)
        commands = [call.args[0] for call in runner.call_args_list]
        self.assertIn(["/usr/bin/node", "--test"], commands)

    def test_without_script_or_tests_is_actionable(self):
        temporary, project = make_project({"src/a.js": "export const a = 1;\n"}, package={})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project, "--test")

        self.assertEqual(code, 1, stdout + stderr)
        self.assertIn('no "test" script', stdout)

    def test_missing_lint_script_fails_with_message(self):
        temporary, project = make_project({}, package={})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project, "--lint")

        self.assertEqual(code, 1, stdout + stderr)
        self.assertIn('no "lint" script', stdout)

    def test_lint_script_runs_when_present(self):
        temporary, project = make_project({}, package={"scripts": {"lint": "eslint ."}})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, runner = invoke(project, "--lint")

        self.assertEqual(code, 0, stdout + stderr)
        commands = [call.args[0] for call in runner.call_args_list]
        self.assertIn(["/usr/bin/npm", "run", "lint"], commands)

    def test_json_and_text_agree_on_failure(self):
        temporary, project = make_project({"src/a.js": "export const a = 1;\n"}, package={})
        self.addCleanup(temporary.cleanup)

        text_code, text_out, text_err, _ = invoke(project, "--lint")
        json_code, json_out, json_err, _ = invoke(project, "--lint", "--json")

        self.assertEqual(text_code, 1, text_out + text_err)
        self.assertIn("FAIL", text_out)
        self.assertEqual(json_code, 1, json_out + json_err)
        payload = json.loads(json_out)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["node"], "24.20.0")
        self.assertEqual(payload["checks"][0]["name"], "syntax")

    def test_declared_engine_below_runtime_is_a_note_not_a_failure(self):
        temporary, project = make_project(
            {"src/a.js": "export const a = 1;\n"}, package={"engines": {"node": ">=26"}}
        )
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project)

        self.assertEqual(code, 0, stdout + stderr)
        self.assertIn("NOTA", stdout)
        self.assertIn("engines.node", stdout)

    def test_module_syntax_in_js_is_retried_with_detect_module(self):
        temporary, project = make_project({"src/a.js": "export const a = 1;\n"})

        def old_runtime(command, cwd, timeout):
            if "--check" in command and "--experimental-detect-module" in command:
                return 0, ""
            if "--check" in command:
                return 1, MODULE_HINT
            return 0, ""

        code, stdout, stderr, _ = invoke(project, runner=version_aware(old_runtime))
        self.addCleanup(temporary.cleanup)

        self.assertEqual(code, 0, stdout + stderr)
        self.assertIn("ESM in .js detected", stdout)

    def test_failed_retry_keeps_the_original_failure(self):
        temporary, project = make_project({"src/a.js": "export const a = 1;\n"})

        def broken_runtime(command, cwd, timeout):
            if "--experimental-detect-module" in command and "--version" in command:
                return 9, "bad option"
            if "--check" in command:
                return 1, MODULE_HINT
            return 0, ""

        code, stdout, stderr, _ = invoke(project, runner=version_aware(broken_runtime))
        self.addCleanup(temporary.cleanup)

        self.assertEqual(code, 1, stdout + stderr)
        self.assertIn(MODULE_HINT, stdout)

    def test_collects_only_source_suffixes(self):
        temporary, project = make_project({
            "src/a.js": "",
            "src/b.mjs": "",
            "src/c.cjs": "",
            "src/d.ts": "",
            "src/e.jsx": "",
        })
        self.addCleanup(temporary.cleanup)

        self.assertEqual(
            sorted(path.name for path in VERIFY.find_sources(project)),
            ["a.js", "b.mjs", "c.cjs"],
        )


if __name__ == "__main__":
    unittest.main()
