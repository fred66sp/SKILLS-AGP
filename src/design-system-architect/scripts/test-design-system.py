#!/usr/bin/env python3
"""Pruebas de scripts/design_system.py.

Uso:
    python3 src/design-system-architect/scripts/test-design-system.py
"""

from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "design_system.py"
SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import design_system as ds  # noqa: E402


def base_contract() -> dict:
    return {
        "schema": "design-system.v1",
        "name": "acme",
        "version": "0.1.0",
        "status": "refine",
        "identity": {
            "purpose": "Un producto de operaciones.",
            "principles": ["La claridad manda.", "Un acento con significado."],
        },
        "tokens": {
            "color": {
                "$type": "color",
                "brand": {
                    "$value": {
                        "colorSpace": "srgb",
                        "components": [0.06, 0.46, 0.43],
                        "hex": "#0f766e",
                    }
                },
                "on-brand": {
                    "$value": {"colorSpace": "srgb", "components": [1, 1, 1], "hex": "#ffffff"}
                },
            },
            "spacing": {
                "$type": "dimension",
                "md": {"$value": {"value": 16, "unit": "px"}},
            },
            "radius": {
                "$type": "dimension",
                "control": {"$value": {"value": 10, "unit": "px"}},
            },
            "typography": {
                "body": {
                    "$type": "typography",
                    "$value": {
                        "fontFamily": "Inter, system-ui, sans-serif",
                        "fontSize": "16px",
                        "fontWeight": 400,
                        "lineHeight": 1.6,
                    },
                }
            },
        },
        "components": {
            "button": {
                "description": "Acción principal.",
                "when": ["La acción principal de una vista."],
                "when_not": ["Navegación."],
                "variants": {
                    "primary": {
                        "backgroundColor": "{color.brand}",
                        "textColor": "{color.on-brand}",
                        "rounded": "{radius.control}",
                        "padding": "10px 16px",
                        "typography": "{typography.body}",
                    }
                },
                "states": ["default", "hover", "focus", "disabled"],
                "example": "<button type=\"button\">Guardar</button>",
            }
        },
        "accessibility": {"standard": "WCAG 2.2 AA", "focusVisible": True},
        "governance": {
            "mode": "approvals",
            "protected": ["identity.*", "tokens.color.*"],
            "configurable": ["tokens.spacing.*"],
            "exceptions": [],
        },
        "constraints": {
            "always": ["Usa tokens semánticos."],
            "never": ["Usa el color como único indicador."],
        },
        "decisions": [
            {"id": "DS-001", "decision": "Un solo acento.", "rationale": "El color identifica."}
        ],
        "omitted": [],
    }


def approvals(path: Path, entries: list[dict]) -> None:
    path.write_text(
        json.dumps({"schema": "design-system.approvals.v1", "approvals": entries}, ensure_ascii=False),
        encoding="utf-8",
    )


def approval_entry(**overrides) -> dict:
    entry = {
        "id": "APR-001",
        "path": "tokens.color.brand",
        "approved_by": "Ana",
        "approved_at": "2026-10-30",
        "source": "confirmación de la persona en la sesión",
        "reason": "El acento cambia de tono sin cambiar de significado.",
    }
    entry.update(overrides)
    return entry


class DesignSystemTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write(self, name: str, data: dict) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ds.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def snapshot(self, root: Path) -> list[tuple[str, int, int, str]]:
        result = []
        for current, dirs, files in os.walk(root):
            dirs[:] = [name for name in dirs if name not in {".git", "__pycache__"}]
            for name in files:
                path = Path(current) / name
                stat = path.stat()
                result.append(
                    (
                        str(path.relative_to(root)),
                        stat.st_size,
                        stat.st_mtime_ns,
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                    )
                )
        return sorted(result)

    # -- Integridad ---------------------------------------------------------

    def test_template_passes(self) -> None:
        code, out, _ = self.run_cli("check", str(SKILL_ROOT / "assets" / "design-system.template.json"))
        self.assertEqual(code, ds.EXIT_PASS)
        self.assertIn("RESULT: PASS", out)

    def test_minimal_contract_passes(self) -> None:
        contract = self.write("design-system.json", base_contract())
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_PASS)
        self.assertIn("RESULT: PASS", out)

    def test_json_output(self) -> None:
        contract = self.write("design-system.json", base_contract())
        code, out, _ = self.run_cli("check", str(contract), "--json")
        self.assertEqual(code, ds.EXIT_PASS)
        payload = json.loads(out)
        self.assertEqual(payload["result"], "PASS")
        self.assertTrue(any(check["id"] == "token-syntax" for check in payload["checks"]))

    def test_invalid_token_fails(self) -> None:
        contract_data = base_contract()
        contract_data["tokens"]["color"]["brand"]["$value"] = {"colorSpace": "no-existe"}
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("FAIL token-syntax", out)
        self.assertIn("colorSpace", out)

    def test_circular_reference_fails(self) -> None:
        contract_data = base_contract()
        contract_data["tokens"]["color"]["a"] = {"$type": "color", "$value": "{color.b}"}
        contract_data["tokens"]["color"]["b"] = {"$type": "color", "$value": "{color.a}"}
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("ciclo", out)

    def test_missing_reference_fails(self) -> None:
        contract_data = base_contract()
        contract_data["components"]["button"]["variants"]["primary"]["backgroundColor"] = "{color.inexistente}"
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("referencia inexistente", out)

    def test_type_mismatch_fails(self) -> None:
        contract_data = base_contract()
        contract_data["tokens"]["color"]["alias"] = {"$type": "dimension", "$value": "{color.brand}"}
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("no coincide", out)

    def test_alias_without_type_infers_target_type(self) -> None:
        contract_data = base_contract()
        contract_data["tokens"]["alias-sin-tipo"] = {"$value": "{color.brand}"}
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_PASS)

    def test_unsupported_extends_fails(self) -> None:
        contract_data = base_contract()
        contract_data["tokens"]["color"]["extended"] = {"$extends": "{color}"}
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("$extends", out)

    def test_deprecated_token_reference_fails(self) -> None:
        contract_data = base_contract()
        contract_data["tokens"]["color"]["brand"]["$deprecated"] = True
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("obsoleto", out)

    def test_deprecated_group_marks_children(self) -> None:
        contract_data = base_contract()
        contract_data["tokens"]["color"]["$deprecated"] = "Se sustituye por el tema nuevo."
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("obsoleto", out)

    def test_variant_without_usage_rule_fails(self) -> None:
        contract_data = base_contract()
        del contract_data["components"]["button"]["when"]
        del contract_data["components"]["button"]["when_not"]
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("when o when_not", out)

    def test_missing_token_source_fails(self) -> None:
        contract_data = base_contract()
        del contract_data["tokens"]
        contract_data["tokenSources"] = ["tokens/inexistente.tokens.json"]
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("no encontrada", out)

    def test_absolute_token_source_fails(self) -> None:
        contract_data = base_contract()
        del contract_data["tokens"]
        contract_data["tokenSources"] = ["/tmp/tokens.json"]
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("relativo al contrato", out)

    def test_theme_override_type_mismatch_fails(self) -> None:
        contract_data = base_contract()
        contract_data["themes"] = {"default": "light", "modes": {"dark": {"color.brand": "{spacing.md}"}}}
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("esperaba color", out)

    def test_component_property_type_mismatch_fails(self) -> None:
        contract_data = base_contract()
        contract_data["components"]["button"]["variants"]["primary"]["backgroundColor"] = "{spacing.md}"
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("esperaba color", out)

    def test_exception_without_approver_fails(self) -> None:
        contract_data = base_contract()
        contract_data["governance"]["exceptions"] = [
            {"path": "components.button", "reason": "Densidad especial."}
        ]
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("approved_by o approval", out)

    def test_check_warns_that_protected_changes_are_not_evaluated(self) -> None:
        contract = self.write("design-system.json", base_contract())
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_PASS)
        self.assertIn("no evalúa cambios protegidos", out)

    # -- Puerta de cambios protegidos ---------------------------------------

    def test_gate_unchanged_passes(self) -> None:
        contract_data = base_contract()
        contract = self.write("design-system.json", contract_data)
        baseline = self.write("baseline.json", contract_data)
        code, out, _ = self.run_cli("gate", str(contract), "--baseline", str(baseline))
        self.assertEqual(code, ds.EXIT_PASS)
        self.assertIn("PASS protected-changes", out)

    def test_gate_without_baseline_is_unknown(self) -> None:
        contract = self.write("design-system.json", base_contract())
        code, out, _ = self.run_cli("gate", str(contract))
        self.assertEqual(code, ds.EXIT_UNKNOWN)
        self.assertIn("UNKNOWN protected-changes", out)
        self.assertNotIn("RESULT: PASS", out)

    def test_gate_protected_change_without_approval_fails(self) -> None:
        baseline_data = base_contract()
        contract_data = copy.deepcopy(baseline_data)
        contract_data["tokens"]["color"]["brand"]["$value"]["hex"] = "#115e59"
        contract = self.write("design-system.json", contract_data)
        baseline = self.write("baseline.json", baseline_data)
        code, out, _ = self.run_cli("gate", str(contract), "--baseline", str(baseline))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("FAIL protected-changes", out)
        self.assertIn("tokens.color.brand", out)

    def test_gate_protected_change_with_approval_passes(self) -> None:
        baseline_data = base_contract()
        contract_data = copy.deepcopy(baseline_data)
        contract_data["tokens"]["color"]["brand"]["$value"]["hex"] = "#115e59"
        contract = self.write("design-system.json", contract_data)
        baseline = self.write("baseline.json", baseline_data)
        approval = self.root / "approvals.json"
        approvals(approval, [approval_entry()])
        code, out, _ = self.run_cli(
            "gate", str(contract), "--baseline", str(baseline), "--approvals", str(approval)
        )
        self.assertEqual(code, ds.EXIT_PASS)
        self.assertIn("PASS protected-changes", out)

    def test_approval_with_only_approved_by_is_unknown(self) -> None:
        baseline_data = base_contract()
        contract_data = copy.deepcopy(baseline_data)
        contract_data["tokens"]["color"]["brand"]["$value"]["hex"] = "#115e59"
        contract = self.write("design-system.json", contract_data)
        baseline = self.write("baseline.json", baseline_data)
        approval = self.root / "approvals.json"
        approvals(approval, [{"approved_by": "Ana", "path": "tokens.color.brand"}])
        code, out, _ = self.run_cli(
            "gate", str(contract), "--baseline", str(baseline), "--approvals", str(approval)
        )
        self.assertEqual(code, ds.EXIT_UNKNOWN)
        self.assertIn("UNKNOWN protected-changes", out)

    def test_gate_locked_system_unchanged_passes(self) -> None:
        contract_data = base_contract()
        contract_data["status"] = "locked"
        contract = self.write("design-system.json", contract_data)
        baseline = self.write("baseline.json", contract_data)
        code, out, _ = self.run_cli("gate", str(contract), "--baseline", str(baseline))
        self.assertEqual(code, ds.EXIT_PASS)
        self.assertIn("PASS protected-changes", out)

    def test_gate_compatible_addition_passes(self) -> None:
        baseline_data = base_contract()
        contract_data = copy.deepcopy(baseline_data)
        contract_data["tokens"]["spacing"]["lg"] = {"$value": {"value": 24, "unit": "px"}}
        contract = self.write("design-system.json", contract_data)
        baseline = self.write("baseline.json", baseline_data)
        code, out, _ = self.run_cli("gate", str(contract), "--baseline", str(baseline))
        self.assertEqual(code, ds.EXIT_PASS)
        self.assertIn("PASS protected-changes", out)

    # -- Catálogo -----------------------------------------------------------

    def catalog_contract(self) -> tuple[Path, Path]:
        contract_data = base_contract()
        contract_data["catalog"] = {"path": "catalog"}
        contract_data["implementation"] = {"styles": ["web/app.css"]}
        contract = self.write("design-system.json", contract_data)
        (self.root / "web").mkdir(exist_ok=True)
        (self.root / "web" / "app.css").write_text(".btn-primary { color: #0f766e; }\n", encoding="utf-8")
        out = self.root / "catalog"
        code, _, _ = self.run_cli("catalog", str(contract), "--out", str(out))
        self.assertEqual(code, ds.EXIT_PASS)
        return contract, out

    def test_gate_solo_mode_protected_change_is_unknown(self) -> None:
        baseline = copy.deepcopy(base_contract())
        baseline["governance"]["mode"] = "solo"
        current = copy.deepcopy(baseline)
        current["tokens"]["color"]["brand"]["$value"]["hex"] = "#115e59"
        baseline_path = self.write("baseline.json", baseline)
        contract = self.write("design-system.json", current)
        code, out, _ = self.run_cli("gate", str(contract), "--baseline", str(baseline_path))
        self.assertEqual(code, ds.EXIT_UNKNOWN)
        self.assertIn("governance.mode es solo", out)

    def test_catalog_consistency_passes(self) -> None:
        contract, _ = self.catalog_contract()
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_PASS)
        self.assertIn("PASS catalog-consistency", out)

    def test_catalog_detects_contract_change(self) -> None:
        contract, _ = self.catalog_contract()
        contract_data = json.loads(contract.read_text(encoding="utf-8"))
        contract_data["name"] = "acme-renombrado"
        contract.write_text(json.dumps(contract_data, ensure_ascii=False), encoding="utf-8")
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("FAIL catalog-consistency", out)

    def test_catalog_detects_artifact_edit(self) -> None:
        contract, out_dir = self.catalog_contract()
        with (out_dir / "index.html").open("a", encoding="utf-8") as handle:
            handle.write("\n<!-- editado -->\n")
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("no coincide con el manifiesto", out)

    def test_catalog_missing_is_unknown(self) -> None:
        contract_data = base_contract()
        contract_data["catalog"] = {"path": "catalog"}
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_UNKNOWN)
        self.assertIn("UNKNOWN catalog-consistency", out)

    def test_catalog_manifest_includes_token_sources(self) -> None:
        colors = {
            "color": {
                "$type": "color",
                "brand": {
                    "$value": {
                        "colorSpace": "srgb",
                        "components": [0.06, 0.46, 0.43],
                        "hex": "#0f766e",
                    }
                },
                "on-brand": {
                    "$value": {"colorSpace": "srgb", "components": [1, 1, 1], "hex": "#ffffff"}
                },
            }
        }
        source = self.write("tokens/colors.tokens.json", colors)
        contract_data = base_contract()
        del contract_data["tokens"]["color"]
        contract_data["tokenSources"] = ["tokens/colors.tokens.json"]
        contract_data["catalog"] = {"path": "catalog"}
        contract = self.write("design-system.json", contract_data)
        out = self.root / "catalog"
        code, _, _ = self.run_cli("catalog", str(contract), "--out", str(out))
        self.assertEqual(code, ds.EXIT_PASS)
        manifest = json.loads((out / "catalog.json").read_text(encoding="utf-8"))
        kinds = sorted(item["kind"] for item in manifest["inputs"])
        self.assertEqual(kinds, ["contract", "skill-template", "skill-template", "token-source"])
        self.assertEqual(len(manifest["inputs"]), 4)

        source_data = json.loads(source.read_text(encoding="utf-8"))
        source_data["color"]["brand"]["$value"]["hex"] = "#115e59"
        source.write_text(json.dumps(source_data, ensure_ascii=False), encoding="utf-8")
        code, out_text, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("FAIL catalog-consistency", out_text)

    def test_catalog_escapes_contract_html(self) -> None:
        contract_data = base_contract()
        contract_data["name"] = "<script>alert(1)</script>"
        contract_data["components"]["button"]["example"] = "<img src=x onerror=alert(1)>"
        contract_data["catalog"] = {"path": "catalog"}
        contract = self.write("design-system.json", contract_data)
        out = self.root / "catalog"
        code, _, _ = self.run_cli("catalog", str(contract), "--out", str(out))
        self.assertEqual(code, ds.EXIT_PASS)
        page = (out / "index.html").read_text(encoding="utf-8")
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", page)
        self.assertIn("sandbox", page)

    def test_catalog_is_deterministic(self) -> None:
        contract, out_dir = self.catalog_contract()
        first = {
            name: (out_dir / name).read_bytes()
            for name in ("index.html", "tokens.css", "catalog.css", "catalog.json")
        }
        code, _, _ = self.run_cli("catalog", str(contract), "--out", str(out_dir))
        self.assertEqual(code, ds.EXIT_PASS)
        second = {
            name: (out_dir / name).read_bytes()
            for name in ("index.html", "tokens.css", "catalog.css", "catalog.json")
        }
        self.assertEqual(first, second)

    # -- Catálogo externo y acoplamiento ------------------------------------

    def external_contract(
        self, example: str = '<button class="btn-primary">Guardar</button>'
    ) -> Path:
        contract_data = base_contract()
        contract_data["catalog"] = {
            "mode": "external",
            "path": "docs/ds",
            "sources": ["web/app.css"],
        }
        contract_data["components"]["button"]["example"] = example
        contract = self.write("design-system.json", contract_data)
        (self.root / "web").mkdir(exist_ok=True)
        (self.root / "web" / "app.css").write_text(
            ".btn-primary { color: #0f766e; }\n.btn-ghost { color: #0f172a; }\n",
            encoding="utf-8",
        )
        catalog = self.root / "docs" / "ds"
        catalog.mkdir(parents=True)
        (catalog / "index.html").write_text(
            '<link rel="stylesheet" href="../../web/app.css"><p class="btn-primary">Guardar</p>\n',
            encoding="utf-8",
        )
        return contract

    def test_external_catalog_with_product_classes_passes(self) -> None:
        contract = self.external_contract()
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_PASS)
        self.assertIn("PASS catalog-consistency", out)
        self.assertIn("PASS implementation-fidelity", out)

    def test_catalog_without_implementation_is_unknown(self) -> None:
        contract_data = base_contract()
        contract_data["catalog"] = {"path": "catalog"}
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_UNKNOWN)
        self.assertIn("UNKNOWN implementation-fidelity", out)

    def test_external_catalog_sample_with_unknown_class_fails(self) -> None:
        contract = self.external_contract(
            '<button class="btn-primary ds-button">Guardar</button>'
        )
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("FAIL implementation-fidelity", out)
        self.assertIn("ds-button", out)

    def test_external_catalog_own_class_layer_fails(self) -> None:
        contract = self.external_contract()
        (self.root / "docs" / "ds" / "catalog.css").write_text(
            ".ds-card { padding: 8px; }\n", encoding="utf-8"
        )
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("capa propia", out)

    def test_external_catalog_must_import_implementation(self) -> None:
        contract = self.external_contract()
        (self.root / "docs" / "ds" / "index.html").write_text(
            "<p>Catálogo escrito a mano</p>\n", encoding="utf-8"
        )
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("no importa la implementación", out)

    def test_external_catalog_is_not_generated(self) -> None:
        contract = self.external_contract()
        code, _, err = self.run_cli("catalog", str(contract), "--out", str(self.root / "otro"))
        self.assertEqual(code, ds.EXIT_USAGE)
        self.assertIn("external", err)

    # -- Adaptadores --------------------------------------------------------

    def test_adapter_missing_report_is_unknown(self) -> None:
        contract_data = base_contract()
        contract_data["adapters"] = [{"name": "web", "report": "reports/web.json"}]
        contract = self.write("design-system.json", contract_data)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_UNKNOWN)
        self.assertIn("UNKNOWN component-conformance", out)

    def test_adapter_fail_is_fail(self) -> None:
        contract_data = base_contract()
        contract_data["adapters"] = [{"name": "web", "report": "reports/web.json"}]
        contract = self.write("design-system.json", contract_data)
        report = {
            "schema": "design-system.adapter.v1",
            "components": [{"name": "button", "status": "FAIL", "evidence": "render"}],
        }
        self.write("reports/web.json", report)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("FAIL component-conformance", out)

    def test_adapter_pass_passes(self) -> None:
        contract_data = base_contract()
        contract_data["adapters"] = [{"name": "web", "report": "reports/web.json"}]
        contract = self.write("design-system.json", contract_data)
        report = {
            "schema": "design-system.adapter.v1",
            "components": [{"name": "button", "status": "PASS", "evidence": "render"}],
        }
        self.write("reports/web.json", report)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_PASS)
        self.assertIn("PASS component-conformance", out)

    def test_adapter_pass_without_evidence_is_unknown(self) -> None:
        contract_data = base_contract()
        contract_data["adapters"] = [{"name": "web", "report": "reports/web.json"}]
        contract = self.write("design-system.json", contract_data)
        report = {
            "schema": "design-system.adapter.v1",
            "components": [{"name": "button", "status": "PASS"}],
        }
        self.write("reports/web.json", report)
        code, out, _ = self.run_cli("check", str(contract))
        self.assertEqual(code, ds.EXIT_UNKNOWN)
        self.assertIn("UNKNOWN component-conformance", out)
        self.assertIn("sin evidencia", out)

    # -- Descubrimiento -----------------------------------------------------

    def project_fixture(self) -> Path:
        project = self.root / "proyecto"
        project.mkdir()
        (project / "DESIGN.md").write_text(
            "# Sistema existente\n\n## Principios\n\n- Claridad.\n", encoding="utf-8"
        )
        tokens = {
            "color": {
                "$type": "color",
                "bg": {"$value": {"colorSpace": "srgb", "components": [1, 1, 1], "hex": "#ffffff"}}
            }
        }
        (project / "tokens").mkdir()
        (project / "tokens" / "colors.tokens.json").write_text(
            json.dumps(tokens), encoding="utf-8"
        )
        (project / "styles.css").write_text(
            ":root { --color-bg: #ffffff; --space-md: 16px; }\n"
            "@media (prefers-reduced-motion: reduce) { * { animation: none; } }\n",
            encoding="utf-8",
        )
        (project / "src" / "components").mkdir(parents=True)
        (project / "src" / "components" / "Button.tsx").write_text(
            "export function Button() { return null; }\n", encoding="utf-8"
        )
        return project

    def test_discover_reads_existing_project_without_writing(self) -> None:
        project = self.project_fixture()
        before = self.snapshot(project)
        code, out, _ = self.run_cli("discover", str(project), "--json")
        self.assertEqual(code, ds.EXIT_PASS)
        inventory = json.loads(out)
        kinds = {fact["kind"] for fact in inventory["facts"]}
        self.assertIn("observed", kinds)
        self.assertIn("documented", kinds)
        self.assertIn("inferred", kinds)
        self.assertTrue(any(fact["path"] == "DESIGN.md" for fact in inventory["facts"]))
        documented = next(fact for fact in inventory["facts"] if fact["path"] == "DESIGN.md")
        self.assertIn("Principios", documented.get("detail", {}).get("headings", []))
        self.assertTrue(any(fact["path"] == "styles.css" for fact in inventory["facts"]))
        self.assertEqual(before, self.snapshot(project))

    def test_discovery_marks_unknown_categories(self) -> None:
        empty = self.root / "vacio"
        empty.mkdir()
        code, out, _ = self.run_cli("discover", str(empty), "--json")
        self.assertEqual(code, ds.EXIT_PASS)
        inventory = json.loads(out)
        unknowns = {item["what"] for item in inventory["unknown"]}
        self.assertIn("tokens", unknowns)
        self.assertIn("componentes", unknowns)

    def test_discover_finds_nested_brand_pack_and_duplicates(self) -> None:
        project = self.root / "producto"
        (project / "docs" / "tasks-ai-brand" / "design").mkdir(parents=True)
        (project / "docs" / "tasks-ai-brand" / "design" / "tokens.json").write_text(
            json.dumps(
                {"color": {"brand": "#0f766e"}, "typography": {"body": {"fontFamily": "Inter"}}},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (project / "web" / "src").mkdir(parents=True)
        (project / "web" / "src" / "app.css").write_text(
            ":root { --accent: #0f766e; }\n", encoding="utf-8"
        )
        (project / "web" / "public").mkdir(parents=True)
        (project / "web" / "public" / "brand.css").write_text(
            ":root { --brand: #0f766e; }\n", encoding="utf-8"
        )
        code, out, _ = self.run_cli("discover", str(project), "--json")
        self.assertEqual(code, ds.EXIT_PASS)
        inventory = json.loads(out)
        self.assertTrue(any("brand-pack" in fact["what"] for fact in inventory["facts"]))
        self.assertNotIn("tokens", {item["what"] for item in inventory["unknown"]})
        duplicates = {item["value"]: item for item in inventory["duplicates"]}
        self.assertGreaterEqual(duplicates["#0f766e"]["count"], 3)

    def test_discover_separates_generated_artifacts(self) -> None:
        project = self.root / "producto"
        (project / "web").mkdir(parents=True)
        (project / "web" / "app.css").write_text(
            ":root { --accent: #0f766e; }\n", encoding="utf-8"
        )
        catalog = project / "docs" / "ds"
        catalog.mkdir(parents=True)
        (catalog / "catalog.json").write_text(
            json.dumps({"schema": "design-system.catalog.v1", "inputs": [], "artifacts": []}),
            encoding="utf-8",
        )
        (catalog / "tokens.css").write_text(
            ":root { --ds-color-brand: #0f766e; }\n", encoding="utf-8"
        )
        code, out, _ = self.run_cli("discover", str(project), "--json")
        self.assertEqual(code, ds.EXIT_PASS)
        inventory = json.loads(out)
        roles = {
            fact["path"]: fact.get("detail", {}).get("role")
            for fact in inventory["facts"]
            if fact["what"].endswith("variable(s) CSS")
        }
        self.assertEqual(roles["web/app.css"], "source")
        self.assertEqual(roles["docs/ds/tokens.css"], "generated")
        self.assertTrue(
            any(fact["what"] == "catálogo generado existente" for fact in inventory["facts"])
        )

    # -- Contrato documental de la integración ------------------------------

    def test_routing_documents_split(self) -> None:
        new_skill = (REPO_ROOT / "src" / "design-system-architect" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        old_skill = (REPO_ROOT / "src" / "web-interface-visual-design" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("sistema visual", new_skill.lower())
        self.assertIn("design-system-architect", old_skill)
        self.assertIn("consume", old_skill.lower())

    def test_governance_documents_approval_limits(self) -> None:
        governance = (SKILL_ROOT / "references" / "governance.md").read_text(encoding="utf-8")
        self.assertIn("no puede crear", governance.lower())
        self.assertIn("no autentica", governance.lower())

    # -- Errores de uso -----------------------------------------------------

    def test_missing_contract_is_usage_error(self) -> None:
        code, _, err = self.run_cli("check", str(self.root / "no-existe.json"))
        self.assertEqual(code, ds.EXIT_USAGE)
        self.assertIn("no existe", err)

    def test_invalid_json_is_fail(self) -> None:
        path = self.root / "roto.json"
        path.write_text("{no es json", encoding="utf-8")
        code, _, err = self.run_cli("check", str(path))
        self.assertEqual(code, ds.EXIT_FAIL)
        self.assertIn("JSON inválido", err)


if __name__ == "__main__":
    unittest.main()
