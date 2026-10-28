#!/usr/bin/env python3
"""Pruebas del script verify-python.py con proyectos Python temporales."""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).with_name("verify-python.py")
SPEC = importlib.util.spec_from_file_location("verify_python", SCRIPT)
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def make_project(files, pyproject=None):
    temporary = tempfile.TemporaryDirectory()
    project = Path(temporary.name)
    if pyproject is not None:
        write(project / "pyproject.toml", pyproject)
    for name, content in files.items():
        write(project / name, content)
    return temporary, project


def invoke(project, *flags, which=None, modules=None, runner=None):
    tools = {"ruff": "/usr/bin/ruff"}
    tools.update(which or {})
    available_modules = {"mypy": True, "pytest": True}
    available_modules.update(modules or {})

    def lookup(name):
        return tools.get(name)

    def find(name):
        return available_modules.get(name, False)

    def default_runner(command, cwd, timeout):
        return 0, ""

    with mock.patch.object(VERIFY.shutil, "which", side_effect=lookup), \
            mock.patch.object(VERIFY, "find_module", side_effect=find), \
            mock.patch.object(VERIFY, "run", side_effect=runner or default_runner) as running:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = VERIFY.main(["--root", str(project), *flags])
    return code, stdout.getvalue(), stderr.getvalue(), running


class VerifyPythonTest(unittest.TestCase):
    def test_syntax_checks_every_source_file(self):
        temporary, project = make_project({
            "src/paquete/__init__.py": "X = 1\n",
            "tests/test_a.py": "def test_ok():\n    assert True\n",
        })
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, runner = invoke(project)

        self.assertEqual(code, 0, stdout + stderr)
        self.assertIn("PASS", stdout)
        self.assertIn("PASSED syntax", stdout)
        runner.assert_not_called()

    def test_syntax_failure_names_the_file(self):
        temporary, project = make_project({"src/roto.py": "def f(:\n    pass\n"})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project)

        self.assertEqual(code, 1, stdout + stderr)
        self.assertIn("FAIL", stdout)
        self.assertIn("src/roto.py", stdout)

    def test_project_without_files_passes_with_note(self):
        temporary, project = make_project({})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project)

        self.assertEqual(code, 0, stdout + stderr)
        self.assertIn("no .py file was found", stdout)

    def test_virtualenv_and_cache_are_skipped(self):
        temporary, project = make_project({
            "src/a.py": "A = 1\n",
            ".venv/lib/b.py": "def b(:\n",
            "__pycache__/c.py": "def c(:\n",
            "build/d.py": "def d(:\n",
        })
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project)

        self.assertEqual(code, 0, stdout + stderr)
        self.assertIn("PASSED syntax", stdout)
        self.assertNotIn(".venv", stdout)

    def test_missing_ruff_fails_lint(self):
        temporary, project = make_project({"src/a.py": "A = 1\n"})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project, "--lint", which={"ruff": None})

        self.assertEqual(code, 1, stdout + stderr)
        self.assertIn("ruff is not available", stdout)

    def test_lint_runs_ruff_check(self):
        temporary, project = make_project({"src/a.py": "A = 1\n"})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, runner = invoke(project, "--lint")

        self.assertEqual(code, 0, stdout + stderr)
        commands = [call.args[0] for call in runner.call_args_list]
        self.assertIn(["/usr/bin/ruff", "check", "."], commands)

    def test_format_runs_ruff_format_check(self):
        temporary, project = make_project({"src/a.py": "A = 1\n"})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, runner = invoke(project, "--format")

        self.assertEqual(code, 0, stdout + stderr)
        commands = [call.args[0] for call in runner.call_args_list]
        self.assertIn(["/usr/bin/ruff", "format", "--check", "."], commands)

    def test_missing_type_checker_fails(self):
        temporary, project = make_project({"src/a.py": "A = 1\n"})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(
            project, "--types", which={"ruff": None}, modules={"mypy": False}
        )

        self.assertEqual(code, 1, stdout + stderr)
        self.assertIn("mypy is not installed", stdout)

    def test_types_runs_mypy(self):
        temporary, project = make_project({"src/a.py": "A: int = 1\n"})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, runner = invoke(project, "--types")

        self.assertEqual(code, 0, stdout + stderr)
        commands = [call.args[0] for call in runner.call_args_list]
        self.assertIn([VERIFY.sys.executable, "-m", "mypy", "."], commands)

    def test_test_uses_pytest_when_available(self):
        temporary, project = make_project({"tests/test_a.py": "def test_a():\n    pass\n"})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, runner = invoke(project, "--test")

        self.assertEqual(code, 0, stdout + stderr)
        commands = [call.args[0] for call in runner.call_args_list]
        self.assertIn([VERIFY.sys.executable, "-m", "pytest"], commands)

    def test_test_falls_back_to_unittest(self):
        temporary, project = make_project({"tests/test_a.py": "import unittest\n"})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, runner = invoke(project, "--test", modules={"pytest": False})

        self.assertEqual(code, 0, stdout + stderr)
        commands = [call.args[0] for call in runner.call_args_list]
        self.assertIn(
            [VERIFY.sys.executable, "-m", "unittest", "discover", "-s", "tests"], commands
        )

    def test_test_fails_without_runner_or_tests(self):
        temporary, project = make_project({"src/a.py": "A = 1\n"})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project, "--test", modules={"pytest": False})

        self.assertEqual(code, 1, stdout + stderr)
        self.assertIn("no test_*.py file was found", stdout)

    def test_failed_check_turns_the_gate_red(self):
        temporary, project = make_project({"src/a.py": "A = 1\n"})
        self.addCleanup(temporary.cleanup)

        def failing(command, cwd, timeout):
            return 1, "Found 1 error"

        code, stdout, stderr, _ = invoke(project, "--lint", runner=failing)

        self.assertEqual(code, 1, stdout + stderr)
        self.assertIn("Found 1 error", stdout)

    def test_json_matches_exit_code(self):
        temporary, project = make_project({"src/a.py": "A = 1\n"})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project, "--lint", "--json")

        self.assertEqual(code, 0, stdout + stderr)
        data = json.loads(stdout)
        self.assertTrue(data["ok"])
        self.assertEqual(data["checks"][0]["name"], "syntax")
        self.assertIn("python", data)

    def test_missing_root_is_a_usage_error(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        missing = Path(temporary.name) / "no-existe"

        code, stdout, stderr, _ = invoke(missing)

        self.assertEqual(code, 2, stdout + stderr)
        self.assertIn("not a directory", stderr)

    def test_timeout_must_be_positive(self):
        temporary, project = make_project({})
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project, "--timeout", "0")

        self.assertEqual(code, 2, stdout + stderr)
        self.assertIn("--timeout", stderr)

    def test_requires_python_below_current_is_a_note(self):
        temporary, project = make_project(
            {"src/a.py": "A = 1\n"},
            pyproject='[project]\nname = "x"\nrequires-python = ">=99"\n',
        )
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project)

        self.assertEqual(code, 0, stdout + stderr)
        self.assertIn("is below requires-python", stdout)

    def test_invalid_pyproject_is_a_usage_error(self):
        temporary, project = make_project({"src/a.py": "A = 1\n"}, pyproject="[project\n")
        self.addCleanup(temporary.cleanup)

        code, stdout, stderr, _ = invoke(project)

        self.assertEqual(code, 2, stdout + stderr)
        self.assertIn("pyproject.toml", stderr)

    def test_runner_oserror_becomes_a_failed_check(self):
        temporary, project = make_project({"src/a.py": "A = 1\n"})
        self.addCleanup(temporary.cleanup)

        def broken(command, cwd, timeout):
            return None, "could not run ruff: missing"

        code, stdout, stderr, _ = invoke(project, "--lint", runner=broken)

        self.assertEqual(code, 1, stdout + stderr)
        self.assertIn("could not run ruff", stdout)


if __name__ == "__main__":
    unittest.main()
