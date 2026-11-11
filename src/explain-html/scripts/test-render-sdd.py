#!/usr/bin/env python3
"""Pruebas de scripts/render-sdd.py: secciones, puerta, determinismo y seccionamiento.

Uso: python3 test-render-sdd.py
Sale 0 si todo pasa; imprime el caso fallido y sale 1 si no.

Los fixtures se escriben en un directorio temporal, nunca en el repositorio.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifact_meta  # noqa: E402
import sdd_scan  # noqa: E402

SCRIPT = Path(__file__).with_name("render-sdd.py")
CHECKER = Path(__file__).with_name("check-artifact.py")
PROMPT = "Genera el artefacto del árbol SDD de prueba"
FECHA = "2026-11-11"

OPENSPEC_PROPOSAL = """# Add throttling

## Why

Too many attempts.
"""

OPENSPEC_SPEC = """# auth

## Requirements

### Requirement: Session lifetime
The system SHALL expire sessions after 30 minutes.

### Scenario: Expired session
- GIVEN a token older than 30 minutes
- WHEN the client presents it
- THEN the system SHALL reject it with an error
"""

OPENSPEC_DELTA = """## MODIFIED Requirements

### Requirement: Telemetry budget
The system SHALL cap telemetry at 100 events per day.

#### Scenario: Budget exceeded
- WHEN the daily budget is exhausted
- THEN the system SHALL drop events with an error
"""

OPENSPEC_TASKS = """# Tasks

- [ ] 1.1 Add limiter [P]
- [x] 1.2 Document it
- [~] 1.3 Decide retries

[NEEDS CLARIFICATION] Which provider finishes the rollout?
"""

GENERIC_NOTES = """# Notas

## Contexto

Se habló del alcance.

| Tema | Estado |
| --- | --- |
| Throttle | abierto |

- Uno
- Dos
"""

KIRO_REQUIREMENTS = """# Login requirements

## Requirements

### Requirement 1: Lockout
The system SHALL lock the account after five failures.

#### Acceptance Criteria

1. GIVEN five failed attempts WHEN the window closes THEN the system SHALL lock the account for 15 minutes.
2. WHEN the lockout is active THEN the system SHALL deny access.
"""

KIRO_TASKS = """# Tasks

- [ ] 1. Implement lockout [P]
  - _Requirements: 1.1_
- [x] 2. Add tests
  - _Requirements: 1.2, 2.1_
"""

GENERIC_ONLY = """# Notas sueltas

## Contexto

Texto plano sin requisitos ni tareas.
"""


def write_tree(base: Path, files: dict) -> Path:
    for rel, content in files.items():
        target = base / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="")
    return base


def render(tree: Path, out: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(tree), "--out", str(out),
         "--prompt", PROMPT, "--date", FECHA, *extra],
        capture_output=True, text=True,
    )


def gate(path: Path) -> tuple:
    result = subprocess.run(
        [sys.executable, str(CHECKER), str(path)], capture_output=True, text=True
    )
    clean = result.returncode == 0 and not result.stderr.strip()
    return clean, result


def meta_of(path: Path):
    text = path.read_text(encoding="utf-8")
    match = artifact_meta.find(text)
    if match is None:
        return None, ["no hay bloque de procedencia"]
    return artifact_meta.load(match)


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

        # --- Árbol openspec con hallazgos, delta, degradado y marcador --------
        tree = write_tree(
            tmp / "openspec-tree",
            {
                "openspec/proposal.md": OPENSPEC_PROPOSAL,
                "openspec/specs/auth/spec.md": OPENSPEC_SPEC,
                "openspec/changes/add-throttle/specs/auth/spec.md": OPENSPEC_DELTA,
                "openspec/changes/add-throttle/tasks.md": OPENSPEC_TASKS,
                "notas.md": GENERIC_NOTES,
            },
        )
        out_dir = tmp / "open" / ".explanations"
        out = out_dir / "arbol.html"
        first = render(tree, out)
        second = render(tree, out_dir / "copia.html")
        text = out.read_text(encoding="utf-8") if out.is_file() else ""
        model = sdd_scan.scan(tree)
        expected_fuentes = [item["path"] for item in model["files"]]

        check("openspec: código 0", first.returncode == 0, first.stdout + first.stderr)
        check(
            "openspec: una sola página",
            out.is_file() and not list(out_dir.glob("arbol-*.html")),
            str(sorted(p.name for p in out_dir.glob("*.html"))),
        )
        check(
            "determinista",
            second.returncode == 0 and out.is_file()
            and text == (out_dir / "copia.html").read_text(encoding="utf-8"),
        )
        clean, result = gate(out)
        check("openspec: puerta sin errores ni avisos", clean, result.stdout + result.stderr)

        meta, problems = meta_of(out)
        check("procedencia: bloque válido", problems == [], str(problems))
        check(
            "procedencia: familia sdd",
            isinstance(meta, dict) and meta.get("familia") == "sdd",
            json.dumps(meta, ensure_ascii=False) if meta else "sin meta",
        )
        check(
            "procedencia: fuentes = .md del modelo, ordenadas",
            isinstance(meta, dict) and meta.get("fuentes") == expected_fuentes,
            f"{meta.get('fuentes') if meta else None} != {expected_fuentes}",
        )
        check(
            "procedencia: prompt y fecha de los flags",
            isinstance(meta, dict) and meta.get("prompt") == PROMPT and meta.get("fecha") == FECHA,
        )

        checks = [
            ("chips: perfil openspec", "openspec · 4" in text),
            ("chips: perfil generic", "generic · 1" in text),
            (
                "chips: sin perfil reconocido",
                "1 de 5 ficheros sin perfil reconocido" in text,
            ),
            ("progreso: números", "<strong>1 de 3</strong>" in text and "1 marcadas [P]" in text),
            ("escenario: triplete GIVEN/WHEN/THEN", '<span class="lbl">GIVEN</span>' in text and '<span class="lbl">WHEN</span>' in text and '<span class="lbl">THEN</span>' in text),
            ("delta: color por operación", 'class="delta delta-modified">MODIFIED' in text),
            ("fases: las siete más Sin fase", all(f'id="fase-{phase}"' in text for phase in ["explore", "propose", "specify", "design", "tasks", "apply", "verify", "misc"])),
            ("fase vacía visible", "Sin ficheros en esta fase" in text),
            ("hallazgos: kind y fichero:línea", "scenario-three-hashes" in text and "openspec/specs/auth/spec.md:" in text),
            ("hallazgos: delta sin destino", "modified-without-target" in text),
            ("hallazgos: no-objetivos a nivel de árbol", "a nivel de árbol" in text),
            ("desconocidos: motivo del sin-perfil", "sin perfil reconocido: encabezados sin anclas" in text),
            ("desconocidos: marcador", "necesita aclaración" in text),
            ("degradado: aviso visible", "Sin perfil reconocido:" in text),
            ("degradado: secciones del modelo", "<h3>Contexto</h3>" in text or "<h4>Contexto</h4>" in text),
            ("degradado: tabla transcrita", "<td>abierto</td>" in text),
            ("sin refs: no hay matriz", 'id="trazabilidad"' not in text),
        ]
        for name, ok in checks:
            check(name, ok, "" if ok else text[:0])

        # --- Árbol kiro con refs: matriz y criterios de aceptación -----------
        kiro = write_tree(
            tmp / "kiro-tree",
            {
                "kiro/specs/login/requirements.md": KIRO_REQUIREMENTS,
                "kiro/specs/login/tasks.md": KIRO_TASKS,
            },
        )
        kiro_out = tmp / "kiro" / ".explanations" / "login.html"
        result = render(kiro, kiro_out)
        kiro_text = kiro_out.read_text(encoding="utf-8") if kiro_out.is_file() else ""
        check("kiro: código 0", result.returncode == 0, result.stdout + result.stderr)
        clean, result = gate(kiro_out)
        check("kiro: puerta sin errores ni avisos", clean, result.stdout + result.stderr)
        check("kiro: matriz de trazabilidad", 'id="trazabilidad"' in kiro_text and "<code>1.1</code>" in kiro_text)
        check("kiro: refs de la segunda tarea", "1.2, 2.1" in kiro_text)
        check("kiro: progreso", "<strong>1 de 2</strong>" in kiro_text)
        check("kiro: criterios de aceptación", "Criterios de aceptación" in kiro_text and "<ol>" in kiro_text)
        check("kiro: GIVEN del criterio EARS", '<span class="lbl">GIVEN</span>' in kiro_text)

        # --- Árbol genérico sin perfil: degradado fiel, sin inventar ----------
        generic = write_tree(tmp / "generic-tree", {"notas/suelta.md": GENERIC_ONLY})
        generic_out = tmp / "generic" / ".explanations" / "suelta.html"
        result = render(generic, generic_out)
        generic_text = generic_out.read_text(encoding="utf-8") if generic_out.is_file() else ""
        check("genérico: código 0", result.returncode == 0, result.stdout + result.stderr)
        clean, result = gate(generic_out)
        check("genérico: puerta sin errores ni avisos", clean, result.stdout + result.stderr)
        check("genérico: sin barra de progreso", 'class="progress"' not in generic_text)
        check("genérico: sin matriz", 'id="trazabilidad"' not in generic_text)
        check("genérico: aviso y cuerpo", "Sin perfil reconocido:" in generic_text and "Texto plano sin requisitos ni tareas." in generic_text)
        check("genérico: navegación fija completa", 'id="fase-apply"' in generic_text and "Sin ficheros en esta fase" in generic_text)

        # --- Refusals --------------------------------------------------------
        loose = tmp / "suelto.html"
        result = render(tree, loose)
        check("refusal: --out sin .explanations", result.returncode == 2 and "explanations" in result.stderr, result.stdout + result.stderr)
        check("refusal: no escribe nada", not loose.exists())
        missing = render(tmp / "no-existe", tmp / "otro" / ".explanations" / "x.html")
        check("refusal: árbol inexistente", missing.returncode == 2 and "no es un directorio" in missing.stderr)
        index_attempt = render(tree, tmp / "otro" / ".explanations" / "index.html")
        check(
            "refusal: no sobrescribe index.html",
            index_attempt.returncode == 2 and "build-index" in index_attempt.stderr,
        )

        # --- Seccionamiento: un árbol grande no es un muro -------------------
        big = tmp / "big-tree"
        lines = ["# core", "", "## Requirements", ""]
        for index in range(300):
            lines += [
                f"### Requirement: Capacity {index:03d}",
                f"The system SHALL handle scenario {index:03d} within 200 ms.",
                "",
                f"#### Scenario: Load {index:03d}",
                f"- GIVEN a load of {index} requests per second",
                "- WHEN the peak arrives",
                "- THEN the system SHALL respond with no error",
                "",
            ]
        write_tree(big, {"openspec/specs/core/spec.md": "\n".join(lines)})
        big_out_dir = tmp / "big" / ".explanations"
        big_out = big_out_dir / "grande.html"
        result = render(big, big_out)
        big_pages = sorted(big_out_dir.glob("*.html"))
        check("seccionamiento: código 0", result.returncode == 0, result.stdout + result.stderr)
        check("seccionamiento: índice y hermanas", len(big_pages) > 1 and big_out.is_file(), str([p.name for p in big_pages]))
        check("seccionamiento: aviso honesto por stderr", "AVISO" in result.stderr and "Specify" in result.stderr, result.stderr)
        sizes = {path.name: len(path.read_bytes()) for path in big_pages}
        check("seccionamiento: cada página bajo el umbral", all(value < 100_000 for value in sizes.values()), str(sizes))
        index_text = big_out.read_text(encoding="utf-8")
        check("seccionamiento: índice con fases, hallazgos y desconocidos", 'id="fases"' in index_text and 'id="hallazgos"' in index_text and 'id="desconocidos"' in index_text)
        check("seccionamiento: índice enlaza a las hermanas", all(f'href="{path.name}"' in index_text for path in big_pages if path != big_out))

        links = {}
        for path in big_pages:
            page_meta, page_problems = meta_of(path)
            check(f"seccionamiento: procedencia válida en {path.name}", page_problems == [], str(page_problems))
            enlaces = page_meta.get("enlaces") if isinstance(page_meta, dict) else None
            check(f"seccionamiento: enlaces declarados en {path.name}", isinstance(enlaces, list) and bool(enlaces), json.dumps(page_meta, ensure_ascii=False))
            links[path.name] = set(enlaces or [])
            clean, gate_result = gate(path)
            check(f"seccionamiento: puerta limpia en {path.name}", clean, gate_result.stdout + gate_result.stderr)
        for name, declared in links.items():
            for other in declared:
                check(f"seccionamiento: {name} enlaza a un hermano existente", (big_out_dir / other).is_file(), other)
                check(f"seccionamiento: enlace {name} ↔ {other} es bidireccional", name in links.get(other, set()), f"{name} -> {other}")

        # --- Seccionamiento con muchos hallazgos: el índice no se hincha -----
        noisy = tmp / "noisy-tree"
        noisy_root = noisy / "openspec" / "changes" / "grande"
        noisy_root.mkdir(parents=True, exist_ok=True)
        (noisy_root / "proposal.md").write_text(
            "## Why\nNecesitamos algo grande.\n## What Changes\n- 300 requisitos\n",
            encoding="utf-8",
        )
        for capability, offset in (("c1", 0), ("c2", 150)):
            spec_dir = noisy_root / "specs" / capability
            spec_dir.mkdir(parents=True, exist_ok=True)
            bundle = ["## ADDED Requirements"]
            for index in range(offset, offset + 150):
                bundle += [
                    f"### Requirement: R{index:03d}",
                    f"The system SHALL do action {index} within {index}ms.",
                    "#### Scenario: ok",
                    f"- WHEN trigger {index} THEN result {index}",
                    "",
                ]
            (spec_dir / "spec.md").write_text("\n".join(bundle), encoding="utf-8")
        (noisy_root / "tasks.md").write_text(
            "".join(f"- [ ] {number}.1 tarea{number}\n" for number in range(1, 61)),
            encoding="utf-8",
        )

        noisy_a = tmp / "noisy-a" / ".explanations"
        noisy_b = tmp / "noisy-b" / ".explanations"
        first_noisy = render(noisy, noisy_a / "ruido.html")
        second_noisy = render(noisy, noisy_b / "ruido.html")
        noisy_pages = sorted(noisy_a.glob("*.html"))
        noisy_index = noisy_a / "ruido.html"
        noisy_text = noisy_index.read_text(encoding="utf-8")
        detail_pages = sorted(noisy_a.glob("ruido-hallazgos*.html"))
        check("ruido: código 0", first_noisy.returncode == 0, first_noisy.stdout + first_noisy.stderr)
        check("ruido: índice y hermanas", noisy_index.is_file() and len(noisy_pages) > 1, str([p.name for p in noisy_pages]))
        noisy_sizes = {path.name: len(path.read_bytes()) for path in noisy_pages}
        check("ruido: todas las páginas bajo el umbral", all(value < 100_000 for value in noisy_sizes.values()), str(noisy_sizes))
        check("ruido: página hermana de hallazgos", bool(detail_pages), str([p.name for p in noisy_pages]))
        check(
            "ruido: el índice solo recuenta por kind",
            "ears-without-shall · 300" in noisy_text
            and "scenario-without-error-case · 300" in noisy_text,
        )
        check("ruido: el índice no lleva el detalle", "no cubre ningún caso de fallo" not in noisy_text)
        check(
            "ruido: el detalle vive en la hermana",
            any("no cubre ningún caso de fallo" in path.read_text(encoding="utf-8") for path in detail_pages),
        )
        check(
            "ruido: el índice enlaza la hermana de hallazgos",
            bool(detail_pages) and f'href="{detail_pages[0].name}"' in noisy_text,
        )
        noisy_texts = {}
        for path in noisy_pages:
            page_text = path.read_text(encoding="utf-8")
            noisy_texts[path.name] = page_text
            clean, gate_result = gate(path)
            check(f"ruido: puerta limpia en {path.name}", clean, gate_result.stdout + gate_result.stderr)
        names = set(noisy_texts)
        for path in noisy_pages:
            page_meta, page_problems = meta_of(path)
            check(f"ruido: procedencia válida en {path.name}", page_problems == [], str(page_problems))
            enlaces = set(page_meta.get("enlaces") or []) if isinstance(page_meta, dict) else set()
            check(
                f"ruido: enlaces completos y simétricos en {path.name}",
                enlaces == names - {path.name},
                f"{sorted(enlaces)} != {sorted(names - {path.name})}",
            )
        noisy_second_pages = sorted(noisy_b.glob("*.html"))
        check(
            "ruido: determinista",
            second_noisy.returncode == 0
            and [p.name for p in noisy_second_pages] == [p.name for p in noisy_pages]
            and all(
                path.read_bytes() == (noisy_b / path.name).read_bytes()
                for path in noisy_pages
            ),
        )

        # --- Familia declarada ----------------------------------------------
        check("artifact_meta contiene la familia sdd", "sdd" in artifact_meta.FAMILIES)
        sdd_meta, sdd_problems = meta_of(out)
        check("artifact_meta.load acepta el bloque sdd", sdd_problems == [] and sdd_meta.get("familia") == "sdd")

    if failures:
        print(f"{failures} caso(s) fallidos.")
        return 1
    print("OK: render-sdd produce artefactos deterministas, completos y bajo el umbral; secciona por fase con enlaces bidireccionales.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
