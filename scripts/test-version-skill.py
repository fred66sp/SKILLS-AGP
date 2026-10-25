#!/usr/bin/env python3
"""Pruebas del versionado independiente con repositorios temporales."""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import skill_versions as sv

SPEC = importlib.util.spec_from_file_location("check_repo_versions", SCRIPTS / "check-repo.py")
CHECK_REPO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_REPO)
VERSION_CLI = SCRIPTS / "version-skill.py"


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="")


def skill(name="demo", version="1.2.3", body="Contenido que no debe cambiar.\n"):
    metadata = f'metadata:\n  author: "tests"\n  version: "{version}"\n'
    return (
        f"---\nname: {name}\ndescription: \"Demo skill for tests.\"\n"
        f"{metadata}---\n\n# {name}\n\n{body}"
    )


def make_repo(root, version="1.0.0"):
    write(root / "src" / "demo" / "SKILL.md", skill(version=version))
    write(
        root / ".skills" / "demo" / "SKILL.md",
        "---\nname: demo\ndescription: \"Enrutador de la skill `demo` para pruebas.\"\n---\n\n"
        "# Enrutador de la skill de pruebas\n\n1. Lee `../../src/demo/SKILL.md` completo.\n\n"
        "Fuente canónica: `../../src/demo/`.\n",
    )
    write(
        root / "README.md",
        "# Demo\n\nContrato completo: [`src/demo/SKILL.md`](src/demo/SKILL.md).\n",
    )
    write(root / "docs" / "demo" / "index.html", "<!doctype html><html><body>demo</body></html>\n")
    write(root / "docs" / "index.html", '<a href="demo/index.html">demo</a>\n')


def run_cli(root, *arguments):
    return subprocess.run(
        [sys.executable, str(VERSION_CLI), "--root", str(root), *arguments],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


class SemVerTest(unittest.TestCase):
    def test_valid_versions(self):
        for value in ("0.0.0", "1.0.0", "10.20.30", "1.2.3"):
            self.assertTrue(sv.is_version(value), value)

    def test_invalid_versions(self):
        for value in ("1", "1.0", "01.0.0", "1.00.0", "v1.0.0", "1.0.0-beta", "1.0.0.0", ""):
            self.assertFalse(sv.is_version(value), value)

    def test_increments(self):
        self.assertEqual(sv.next_version("1.2.3", "patch"), "1.2.4")
        self.assertEqual(sv.next_version("1.2.3", "minor"), "1.3.0")
        self.assertEqual(sv.next_version("1.2.3", "major"), "2.0.0")
        self.assertEqual(sv.next_version("2.9.9", "minor"), "2.10.0")

    def test_unknown_increment_is_rejected(self):
        with self.assertRaises(sv.VersionError):
            sv.next_version("1.0.0", "release")


class BumpTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        write(self.root / "src" / "demo" / "SKILL.md", skill())
        self.path = self.root / "src" / "demo" / "SKILL.md"
        if subprocess.run(
            ["git", "init", "-q", str(self.root)], capture_output=True
        ).returncode != 0:
            self.skipTest("git no disponible")

    def test_patch_minor_and_major(self):
        for part, expected in (("patch", "1.2.4"), ("minor", "1.3.0"), ("major", "2.0.0")):
            write(self.path, skill())
            old, new, _ = sv.apply_bump(self.root, "demo", part, [])
            self.assertEqual((old, new), ("1.2.3", expected))

    def test_only_the_version_line_changes(self):
        original = self.path.read_text(encoding="utf-8")
        sv.apply_bump(self.root, "demo", "patch", [])
        updated = self.path.read_text(encoding="utf-8")
        before = original.splitlines()
        after = updated.splitlines()
        self.assertEqual(len(before), len(after))
        changed = [(a, b) for a, b in zip(before, after) if a != b]
        self.assertEqual(len(changed), 1)
        self.assertEqual(changed[0][1], '  version: "1.2.4"')
        self.assertIn("  author: \"tests\"", after)
        self.assertIn("Contenido que no debe cambiar.", updated)
        self.assertTrue(updated.startswith("---\nname: demo\n"))

    def test_line_endings_are_preserved(self):
        self.path.write_bytes(skill().replace("\n", "\r\n").encode("utf-8"))
        sv.apply_bump(self.root, "demo", "patch", [])
        raw = self.path.read_bytes()
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))
        self.assertEqual(sv.read_version(raw.decode("utf-8")), "1.2.4")

    def test_unknown_skill_is_rejected(self):
        with self.assertRaisesRegex(sv.VersionError, "no existe la skill"):
            sv.plan_bump(self.root, "otra", "patch", [])

    def test_missing_version_is_rejected(self):
        write(self.path, "---\nname: demo\ndescription: \"Demo.\"\n---\n")
        with self.assertRaisesRegex(sv.VersionError, "falta metadata.version"):
            sv.plan_bump(self.root, "demo", "patch", [])

    def test_invalid_declared_version_is_rejected(self):
        write(self.path, skill(version="1.0"))
        with self.assertRaisesRegex(sv.VersionError, "no es SemVer"):
            sv.plan_bump(self.root, "demo", "patch", [])

    def test_existing_tag_is_rejected_without_writing(self):
        write(self.path, skill(version="1.2.3"))
        with self.assertRaisesRegex(sv.VersionError, "ya existe"):
            sv.apply_bump(self.root, "demo", "patch", ["demo/v1.2.4"])
        self.assertEqual(sv.read_version(self.path.read_text(encoding="utf-8")), "1.2.3")

    def test_reduction_below_published_is_rejected(self):
        with self.assertRaisesRegex(sv.VersionError, "no se permite reducir"):
            sv.plan_bump(self.root, "demo", "patch", ["demo/v2.0.0"])

    def test_missing_git_information_aborts(self):
        with self.assertRaisesRegex(sv.VersionError, "Git no disponible"):
            sv.plan_bump(self.root, "demo", "patch", None)

    def test_shallow_clone_aborts(self):
        with mock.patch.object(sv, "is_shallow", return_value=True):
            with self.assertRaisesRegex(sv.VersionError, "clon superficial"):
                sv.plan_bump(self.root, "demo", "patch", [])

    def test_dry_run_does_not_write(self):
        original = self.path.read_text(encoding="utf-8")
        result = run_cli(self.root, "bump", "demo", "minor", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1.2.3 -> 1.3.0", result.stdout)
        self.assertIn("--dry-run", result.stdout)
        self.assertEqual(self.path.read_text(encoding="utf-8"), original)

    def test_cli_bump_writes_and_reports(self):
        result = run_cli(self.root, "bump", "demo", "patch")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("demo: 1.2.3 -> 1.2.4", result.stdout)
        self.assertIn("demo/v1.2.4", result.stdout)
        self.assertEqual(sv.read_version(self.path.read_text(encoding="utf-8")), "1.2.4")

    def test_cli_show_and_unknown_skill(self):
        result = run_cli(self.root, "show", "demo")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("declarada: 1.2.3", result.stdout)
        result = run_cli(self.root, "show", "otra")
        self.assertEqual(result.returncode, 1)
        self.assertIn("no existe la skill", result.stderr)


class ValidatorTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        make_repo(self.root)

    def validate(self, tags):
        with mock.patch.object(sv, "git_tags", return_value=tags):
            return CHECK_REPO.validate(self.root)

    def errors(self, tags):
        return self.validate(tags)[0]

    def test_skill_without_metadata_version_is_rejected(self):
        write(self.root / "src" / "demo" / "SKILL.md", "---\nname: demo\ndescription: \"Demo.\"\n---\n")
        self.assertTrue(any("falta metadata.version" in item for item in self.errors([])))

    def test_invalid_version_is_rejected(self):
        write(self.root / "src" / "demo" / "SKILL.md", skill(version="1.0"))
        self.assertTrue(any("no es SemVer" in item for item in self.errors([])))

    def test_repository_without_tags_passes(self):
        self.assertEqual(self.errors([]), [])

    def test_missing_git_information_is_not_a_failure(self):
        errors, notes = self.validate(None)
        self.assertEqual(errors, [])
        self.assertTrue(any("Git no disponible" in note for note in notes))

    def test_shallow_clone_is_flagged(self):
        with mock.patch.object(sv, "is_shallow", return_value=True):
            errors, notes = self.validate([])
        self.assertEqual(errors, [])
        self.assertTrue(any("clon superficial" in note for note in notes))

    def test_declared_version_may_be_unpublished(self):
        self.assertEqual(self.errors(["demo/v0.9.0"]), [])
        self.assertEqual(self.errors(["demo/v1.0.0"]), [])

    def test_published_version_matches_declared(self):
        self.assertEqual(sv.published_status("1.0.0", ["1.0.0"]), "publicada")

    def test_declared_version_below_published_is_rejected(self):
        errors = self.errors(["demo/v1.0.1"])
        self.assertTrue(any("es menor que la publicada 1.0.1" in item for item in errors))

    def test_malformed_tag_is_rejected(self):
        self.assertTrue(any("no es SemVer" in item for item in self.errors(["demo/v1.0"])))

    def test_unknown_skill_tag_is_rejected(self):
        self.assertTrue(any("no existe en src/" in item for item in self.errors(["otra/v1.0.0"])))

    def test_duplicate_tag_is_rejected(self):
        errors = self.errors(["demo/v1.0.0", "demo/v1.0.0"])
        self.assertTrue(any("duplicada" in item for item in errors))

    def test_foreign_tags_are_out_of_scope(self):
        self.assertEqual(self.errors(["v1.0.0", "release-2026"]), [])


class RepositoryTest(unittest.TestCase):
    def test_every_canonical_skill_declares_a_version(self):
        root = SCRIPTS.parent
        for name in sv.skill_names(root):
            text = (root / "src" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(sv.is_version(sv.read_version(text) or ""), name)


if __name__ == "__main__":
    unittest.main()
