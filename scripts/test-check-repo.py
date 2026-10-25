#!/usr/bin/env python3
"""Pruebas del validador check-repo.py con repositorios temporales."""

import importlib.util
import json
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

SCRIPT = Path(__file__).with_name("check-repo.py")
SPEC = importlib.util.spec_from_file_location("check_repo", SCRIPT)
CHECK_REPO = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_REPO)


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def skill(name, description="Demo skill for tests.", version="1.0.0"):
    return (
        f"---\nname: {name}\ndescription: \"{description}\"\n"
        f"metadata:\n  version: \"{version}\"\n---\n\n# {name}\n"
    )


def make_repo(root, router_ref="../../src/demo/SKILL.md", router_name="demo", src_name="demo", meta_name=None):
    meta_name = meta_name or router_name
    write(root / "src" / src_name / "SKILL.md", skill(src_name))
    write(
        root / ".skills" / router_name / "SKILL.md",
        f"---\nname: {meta_name}\ndescription: \"Enrutador de la skill `{src_name}` para pruebas.\"\n---\n\n"
        f"# Enrutador de la skill de pruebas\n\n1. Lee `{router_ref}` completo.\n\n"
        f"Fuente canónica: `../../src/{src_name}/`.\n",
    )
    write(
        root / "README.md",
        f"# Demo\n\nContrato completo: [`src/{src_name}/SKILL.md`](src/{src_name}/SKILL.md).\n",
    )
    write(root / "docs" / src_name / "index.html", "<!doctype html><html><body>demo</body></html>\n")
    write(root / "docs" / "index.html", f'<a href="{src_name}/index.html">{src_name}</a>\n')


class CheckRepoTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def errors(self):
        return CHECK_REPO.validate(self.root)[0]

    def test_valid_repo_passes(self):
        make_repo(self.root)
        self.assertEqual(self.errors(), [])

    def test_legacy_router_path_is_rejected(self):
        make_repo(self.root, router_ref="src/demo/SKILL.md")
        self.assertTrue(any("no resuelve" in item for item in self.errors()))

    def test_router_name_must_match_directory(self):
        make_repo(self.root, meta_name="otro")
        self.assertTrue(any("no coincide con la carpeta" in item for item in self.errors()))

    def test_missing_canonical_is_rejected(self):
        make_repo(self.root)
        (self.root / "src" / "demo" / "SKILL.md").unlink()
        self.assertTrue(any("enrutador huérfano" in item for item in self.errors()))

    def test_missing_router_is_rejected(self):
        make_repo(self.root)
        (self.root / ".skills" / "demo" / "SKILL.md").unlink()
        self.assertTrue(any("falta el enrutador" in item for item in self.errors()))

    def test_wrong_canonical_target_is_rejected(self):
        make_repo(self.root, router_ref="../../src/otro/SKILL.md")
        self.assertTrue(any("no resuelve" in item for item in self.errors()))

    def test_broken_markdown_link_is_rejected(self):
        make_repo(self.root)
        write(self.root / "docs" / "guide.md", "# Guía\n\n[destino](missing.md)\n")
        self.assertTrue(any("[enlaces]" in item for item in self.errors()))

    def test_invalid_name_and_description_are_rejected(self):
        write(self.root / "src" / "Demo" / "SKILL.md", skill("Demo", "x" * 1025))
        errors = self.errors()
        self.assertTrue(any("no es minúsculas" in item for item in errors))
        self.assertTrue(any("1025 caracteres" in item for item in errors))

    def test_missing_docs_page_is_rejected(self):
        make_repo(self.root)
        page = self.root / "docs" / "demo" / "index.html"
        page.unlink()
        errors = self.errors()
        self.assertEqual(len([item for item in errors if item.startswith("[catalogo]")]), 1)
        self.assertTrue(any("docs/demo/index.html" in item for item in errors))

    def test_missing_catalog_link_is_rejected(self):
        make_repo(self.root)
        write(self.root / "docs" / "index.html", '<a href="otra/index.html">otra</a>\n')
        errors = self.errors()
        self.assertTrue(any("no enlaza 'docs/demo/index.html'" in item for item in errors))

    def test_missing_readme_reference_is_rejected(self):
        make_repo(self.root)
        write(self.root / "README.md", "# Demo\n")
        errors = self.errors()
        self.assertTrue(any("no referencia 'src/demo/SKILL.md'" in item for item in errors))

    def test_bad_receipt_is_rejected(self):
        make_repo(self.root)
        docs = self.root / "docs" / "demo"
        spec, html = b"{}\n", b"<html></html>\n"
        write(docs / "fig.json", spec.decode())
        write(docs / "fig.html", html.decode())
        write(
            docs / "fig.delivery.json",
            json.dumps({
                "schemaVersion": 1,
                "specification": {"sha256": "0" * 64, "bytes": 1},
                "artifact": {"sha256": sha256(html).hexdigest(), "bytes": len(html)},
            }),
        )
        self.assertTrue(any("specification no coincide" in item for item in self.errors()))

    def test_crlf_spec_is_rejected(self):
        make_repo(self.root)
        docs = self.root / "docs" / "demo"
        spec, html = b"{}\r\n", b"<html></html>\n"
        (docs).mkdir(parents=True, exist_ok=True)
        (docs / "fig.json").write_bytes(spec)
        (docs / "fig.html").write_bytes(html)
        write(
            docs / "fig.delivery.json",
            json.dumps({
                "schemaVersion": 1,
                "specification": {"sha256": sha256(spec).hexdigest(), "bytes": len(spec)},
                "artifact": {"sha256": sha256(html).hexdigest(), "bytes": len(html)},
            }),
        )
        self.assertTrue(any("tiene CR" in item for item in self.errors()))


if __name__ == "__main__":
    unittest.main()
