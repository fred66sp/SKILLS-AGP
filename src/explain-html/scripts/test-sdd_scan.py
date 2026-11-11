#!/usr/bin/env python3
"""Pruebas de scripts/sdd_scan.py: perfiles, roles, fases, estructura y hallazgos.

Uso: python3 test-sdd_scan.py
Sale 0 si todo pasa; imprime el caso fallido y sale 1 si no.

Los fixtures se escriben en un directorio temporal, nunca en el repositorio.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sdd_scan  # noqa: E402

SCRIPT = Path(__file__).with_name("sdd_scan.py")

OPENSPEC_PROPOSAL = """---
title: Throttle
---
# Add login throttling

## Why

Too many attempts.

## What Changes

Lock the account after five failures.
"""

OPENSPEC_SPEC = """# auth

## Purpose

Authenticate users.

## Requirements

### Requirement: Session lifetime
The system SHALL expire sessions after 30 minutes.

#### Scenario: Expired session
- WHEN a token is older than 30 minutes
- THEN the system SHALL reject it with an error
"""

OPENSPEC_DELTA = """## ADDED Requirements

### Requirement: Login throttling
After 5 failed attempts the system SHALL lock the account.

#### Scenario: Locked out
- WHEN 5 attempts fail
- THEN the system SHALL return an error
"""

OPENSPEC_TASKS = """# Tasks

- [ ] 1.1 Add throttling
- [x] 1.2 Document it
"""

KIRO_REQUIREMENTS = """# Login requirements

## Requirements

### Requirement 1: Lockout
**User Story:** As a user, I want lockout so that brute force fails.

#### Acceptance Criteria

1. WHEN five attempts fail THEN the system SHALL lock the account for 15 minutes.
2. IF the lockout is active THEN the system SHALL deny access.
"""

KIRO_DESIGN = """# Login design

## Approach

Use a counter per account.

## Non-Goals

- Multi-tenant lockouts.
"""

KIRO_TASKS = """# Tasks

- [ ] 1. Implement lockout
  - _Requirements: 1.1_
- [x] 2. Add tests
  - _Requirements: 1.2, 2.1_
"""

KIRO_BUGFIX = """# Bugfix: sessions never expire

## Bug Condition

WHEN a token is never refreshed THEN sessions never expire.

## Expected Behavior

The system SHALL expire sessions after 30 minutes.
"""

SPEC_KIT_SPEC = """# Login feature

## User Scenarios

A user logs in with an email.

## Requirements

- FR-001: The system MUST allow email login.

## Open questions

- [NEEDS CLARIFICATION] Which identity provider?
"""

SPEC_KIT_TASKS = """# Tasks

- [ ] T001 [P] Implement login
- [ ] T002 Write tests
"""

SPEC_KIT_CONSTITUTION = """# Constitution

## Principles

- Verified changes.
"""

GENERIC_CAPACITY = """# Login capacity

## Purpose

Serve peak traffic.

## Requirements

### Requirement: Peak load
The system SHALL handle peak load.

#### Scenario: Peak arrives
- GIVEN a peak of 10 requests per second
- WHEN the peak arrives
- THEN the system SHALL respond within 200 ms
"""

UNCLASSIFIED = """# Random notes

Some prose without requirements or tasks.
"""

FINDINGS_PROPOSAL = """# Spec de prueba

## Why

Porque sí.
"""

FINDINGS_SPEC = """# core

## Purpose

Core.

## Requirements

### Requirement: Modern interface
The system SHALL have a modern interface.

### Requirement: Persist theme
Store the theme with `localStorage.setItem()` and read it back.

#### Scenario: Light mode
- WHEN the user opens the app
- THEN the system SHALL show the light theme

### Requirement: Audit log
The system SHALL keep an audit log.
WHEN an audit entry is written THEN the log rotates.

### Requirement: Legacy flag
The system SHALL read the legacy flag.

### Scenario: Legacy flag path
- WHEN the flag exists
- THEN the system SHALL honour it
"""

FINDINGS_DELTA = """## MODIFIED Requirements

### Requirement: Telemetry budget
The system SHALL cap telemetry at 100 events per day.
"""

FINDINGS_TASKS = """# Tasks

- [ ] 1.1 Update specs
- [~] 1.2 Pending decision
- [x] 1.3 Done
"""


def write_tree(base: Path, files: dict) -> Path:
    for rel, content in files.items():
        target = base / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="")
    return base


def file_by_path(model: dict, path: str):
    for item in model["files"]:
        if item["path"] == path:
            return item
    return None


def kinds(model: dict) -> list:
    return [item["kind"] for item in model["findings"]]


def main() -> int:
    failures = 0

    def check(name: str, condition: bool, detail: str = "") -> None:
        nonlocal failures
        if not condition:
            print(f"FALLO «{name}»")
            if detail:
                print(detail)
            failures += 1

    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)

        openspec = write_tree(
            tmp / "openspec-tree",
            {
                "openspec/proposal.md": OPENSPEC_PROPOSAL,
                "openspec/specs/auth/spec.md": OPENSPEC_SPEC,
                "openspec/changes/add-throttle/specs/auth/spec.md": OPENSPEC_DELTA,
                "openspec/changes/add-throttle/tasks.md": OPENSPEC_TASKS,
                "openspec/README.md": "# Índice interno\n\nEste README sí cuenta.\n",
            },
        )
        model = sdd_scan.scan(openspec)
        proposal = file_by_path(model, "openspec/proposal.md")
        delta = file_by_path(model, "openspec/changes/add-throttle/specs/auth/spec.md")
        spec = file_by_path(model, "openspec/specs/auth/spec.md")
        tasks = file_by_path(model, "openspec/changes/add-throttle/tasks.md")
        detail = json.dumps(model, ensure_ascii=False)
        check("openspec: perfil del árbol", model["tree_profile"] == "openspec", detail)
        check(
            "openspec: proposal con rol y fase",
            proposal is not None and proposal["role"] == "proposal"
            and proposal["phase"] == "propose",
            detail,
        )
        check(
            "openspec: front matter no genera encabezados",
            proposal is not None and proposal["title"] == "Add login throttling"
            and proposal["sections"][0]["line"] == 4,
            detail,
        )
        check(
            "openspec: el delta es rol deltas con delta_op",
            delta is not None and delta["role"] == "deltas" and delta["phase"] == "specify"
            and delta["requirements"][0]["delta_op"] == "ADDED",
            detail,
        )
        scenario = delta["requirements"][0]["scenarios"][0] if delta else {}
        check(
            "openspec: escenario con WHEN/THEN sin GIVEN",
            scenario.get("name") == "Locked out" and scenario.get("when")
            and scenario.get("then") and scenario.get("given") == [],
            detail,
        )
        check(
            "openspec: spec vigente con rol specs",
            spec is not None and spec["role"] == "specs"
            and spec["requirements"][0]["delta_op"] is None,
            detail,
        )
        check(
            "openspec: tareas con id y estado",
            tasks is not None
            and [task["state"] for task in tasks["tasks"]] == ["todo", "done"]
            and tasks["tasks"][0]["id"] == "1.1",
            detail,
        )
        check(
            "openspec: README anidado sí aparece, el de la raíz no",
            file_by_path(model, "openspec/README.md") is not None,
            detail,
        )
        missing = [item for item in model["findings"] if item["kind"] == "missing-non-goals"]
        check(
            "openspec: falta de no-objetivos con la proposal como path",
            len(missing) == 1 and missing[0]["path"] == "openspec/proposal.md",
            detail,
        )
        check("openspec: sin ficheros sin clasificar", model["unknown_files"] == [], detail)

        kiro = write_tree(
            tmp / "kiro-tree",
            {
                ".kiro/specs/login/requirements.md": KIRO_REQUIREMENTS,
                ".kiro/specs/login/design.md": KIRO_DESIGN,
                ".kiro/specs/login/tasks.md": KIRO_TASKS,
                ".kiro/specs/login/bugfix.md": KIRO_BUGFIX,
            },
        )
        model = sdd_scan.scan(kiro)
        requirements = file_by_path(model, ".kiro/specs/login/requirements.md")
        kiro_tasks = file_by_path(model, ".kiro/specs/login/tasks.md")
        design = file_by_path(model, ".kiro/specs/login/design.md")
        bugfix = file_by_path(model, ".kiro/specs/login/bugfix.md")
        detail = json.dumps(model, ensure_ascii=False)
        check("kiro: perfil del árbol", model["tree_profile"] == "kiro", detail)
        check(
            "kiro: requirements con rol, fase y EARS",
            requirements is not None and requirements["role"] == "requirements"
            and requirements["phase"] == "specify",
            detail,
        )
        check(
            "kiro: requisito con criterios y escenarios derivados",
            requirements is not None
            and requirements["requirements"][0]["name"] == "Lockout"
            and len(requirements["requirements"][0]["acceptance_criteria"]) == 2
            and len(requirements["requirements"][0]["scenarios"]) == 2,
            detail,
        )
        check(
            "kiro: trazabilidad de tareas",
            kiro_tasks is not None
            and kiro_tasks["tasks"][0]["refs"] == ["1.1"]
            and kiro_tasks["tasks"][1]["refs"] == ["1.2", "2.1"],
            detail,
        )
        check(
            "kiro: design libre y bugfix",
            design is not None and design["role"] == "design"
            and design["phase"] == "design" and bugfix is not None
            and bugfix["role"] == "bugfix" and bugfix["phase"] == "specify",
            detail,
        )
        check("kiro: no-objetivos declarados", model["has_non_goals"] is True, detail)
        check(
            "kiro: sin hallazgo de no-objetivos",
            "missing-non-goals" not in kinds(model),
            detail,
        )

        spec_kit = write_tree(
            tmp / "spec-kit-tree",
            {
                "specs/001-login/spec.md": SPEC_KIT_SPEC,
                "specs/001-login/plan.md": "# Plan\n\n## Steps\n\n1. Build it.\n",
                "specs/001-login/tasks.md": SPEC_KIT_TASKS,
                "specs/001-login/research.md": "# Research\n\n## Findings\n\nNone.\n",
                "specs/001-login/data-model.md": "# Data model\n\n## Entities\n\nUser.\n",
                "specs/001-login/contracts/api.md": "# API\n\n## Login\n\nPOST /login.\n",
                "specs/001-login/quickstart.md": "# Quickstart\n\n## Run\n\nGo.\n",
                "memory/constitution.md": SPEC_KIT_CONSTITUTION,
            },
        )
        model = sdd_scan.scan(spec_kit)
        sk_spec = file_by_path(model, "specs/001-login/spec.md")
        sk_tasks = file_by_path(model, "specs/001-login/tasks.md")
        contracts = file_by_path(model, "specs/001-login/contracts/api.md")
        quickstart = file_by_path(model, "specs/001-login/quickstart.md")
        constitution = file_by_path(model, "memory/constitution.md")
        detail = json.dumps(model, ensure_ascii=False)
        check("spec-kit: perfil del árbol", model["tree_profile"] == "spec-kit", detail)
        check(
            "spec-kit: spec.md con rol specs",
            sk_spec is not None and sk_spec["role"] == "specs",
            detail,
        )
        check(
            "spec-kit: [NEEDS CLARIFICATION] como marcador",
            sk_spec is not None and len(sk_spec["markers"]) == 1
            and sk_spec["markers"][0]["kind"] == "needs-clarification",
            detail,
        )
        check(
            "spec-kit: [P] marca tarea paralela",
            sk_tasks is not None
            and sk_tasks["tasks"][0]["parallel"] is True
            and sk_tasks["tasks"][1]["parallel"] is False,
            detail,
        )
        check(
            "spec-kit: roles y fases de contracts, quickstart y constitution",
            contracts is not None and contracts["role"] == "contracts"
            and contracts["phase"] == "design"
            and quickstart is not None and quickstart["phase"] == "verify"
            and constitution is not None and constitution["role"] == "constitution"
            and constitution["phase"] is None,
            detail,
        )

        generic = write_tree(
            tmp / "generic-tree",
            {
                "docs/capacity.md": GENERIC_CAPACITY,
                "specs/gadgets/notes.md": "# Gadgets\n\nNotas sueltas.\n",
            },
        )
        model = sdd_scan.scan(generic)
        capacity = file_by_path(model, "docs/capacity.md")
        detail = json.dumps(model, ensure_ascii=False)
        check(
            "generic: ficheros de un árbol ajeno no cuentan",
            "capability-without-delta-file" not in kinds(model),
            detail,
        )
        check(
            "generic: forma canónica clasificada",
            model["tree_profile"] == "generic" and capacity is not None
            and capacity["profile"] == "generic"
            and capacity["unclassified_reason"] is None
            and len(capacity["requirements"]) == 1,
            detail,
        )
        check(
            "generic: escenario con GIVEN poblado",
            capacity is not None
            and capacity["requirements"][0]["scenarios"][0]["given"]
            == ["a peak of 10 requests per second"],
            detail,
        )

        unclassified = write_tree(
            tmp / "unclassified-tree", {"notes/misc.md": UNCLASSIFIED}
        )
        model = sdd_scan.scan(unclassified)
        misc = file_by_path(model, "notes/misc.md")
        detail = json.dumps(model, ensure_ascii=False)
        check(
            "sin clasificar: aparece en unknown_files con motivo",
            model["unknown_files"] == ["notes/misc.md"] and misc is not None
            and bool(misc["unclassified_reason"]),
            detail,
        )
        check(
            "sin clasificar: secciones extraídas igual",
            misc is not None
            and misc["sections"] == [{"level": 1, "title": "Random notes", "line": 1}],
            detail,
        )

        findings_tree = write_tree(
            tmp / "findings-tree",
            {
                "openspec/proposal.md": FINDINGS_PROPOSAL,
                "openspec/specs/core/spec.md": FINDINGS_SPEC,
                "openspec/specs/orphan/design.md": "# Orphan\n\n## Notes\n\nSin spec.\n",
                "openspec/changes/retire-legacy/specs/core/spec.md": FINDINGS_DELTA,
                "openspec/changes/retire-legacy/tasks.md": FINDINGS_TASKS,
            },
        )
        model = sdd_scan.scan(findings_tree)
        found = kinds(model)
        detail = json.dumps(model, ensure_ascii=False)
        expected = [
            "scenario-three-hashes",
            "requirement-without-scenario",
            "ears-without-shall",
            "checkbox-pending",
            "capability-without-delta-file",
            "modified-without-target",
            "vague-requirement",
            "prescriptive-requirement",
            "scenario-without-error-case",
            "missing-non-goals",
        ]
        for kind in expected:
            check(f"hallazgos: aparece {kind}", kind in found, detail)
        pending = [item for item in model["findings"] if item["kind"] == "checkbox-pending"]
        findings_tasks = file_by_path(model, "openspec/changes/retire-legacy/tasks.md")
        check(
            "hallazgos: [~] es pending con hallazgo",
            findings_tasks is not None
            and findings_tasks["tasks"][1]["state"] == "pending"
            and pending and pending[0]["line"] == 4,
            detail,
        )
        modified = [item for item in model["findings"] if item["kind"] == "modified-without-target"]
        check(
            "hallazgos: MODIFIED sin destino nombra el requisito",
            len(modified) == 1 and "Telemetry budget" in modified[0]["detail"],
            detail,
        )
        check(
            "hallazgos: capability sin spec.md señala el directorio",
            any(item["path"] == "openspec/specs/orphan/" for item in model["findings"]),
            detail,
        )
        check(
            "hallazgos: un solo missing-non-goals",
            found.count("missing-non-goals") == 1,
            detail,
        )
        check(
            "hallazgos: orden determinista por path, línea y kind",
            model["findings"] == sorted(
                model["findings"], key=lambda item: (item["path"] or "", item["line"], item["kind"])
            ),
            detail,
        )

        again = sdd_scan.scan(findings_tree)
        check(
            "determinismo: dos pasadas dan los mismos bytes",
            json.dumps(model, sort_keys=True, ensure_ascii=False)
            == json.dumps(again, sort_keys=True, ensure_ascii=False),
        )

        lf = write_tree(tmp / "lf-tree", {"docs/capacity.md": GENERIC_CAPACITY})
        crlf = write_tree(
            tmp / "crlf-tree",
            {"docs/capacity.md": GENERIC_CAPACITY.replace("\n", "\r\n")},
        )
        lf_model = sdd_scan.scan(lf)
        crlf_model = sdd_scan.scan(crlf)
        lf_model.pop("root")
        crlf_model.pop("root")
        check(
            "CRLF: el modelo es idéntico al de LF",
            json.dumps(lf_model, sort_keys=True, ensure_ascii=False)
            == json.dumps(crlf_model, sort_keys=True, ensure_ascii=False),
            detail,
        )

        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(openspec)], capture_output=True, text=True
        )
        check(
            "CLI: imprime JSON válido del árbol y sale 0",
            result.returncode == 0
            and json.loads(result.stdout)["tree_profile"] == "openspec",
            result.stderr,
        )

    if failures:
        print(f"{failures} caso(s) fallidos.")
        return 1
    print("OK: sdd_scan descubre perfiles, estructura y hallazgos de forma determinista.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
