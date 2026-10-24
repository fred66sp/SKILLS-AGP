#!/usr/bin/env python3
"""Comprobaciones de doc-inventory.py. Ejecutar: python3 scripts/test-doc-inventory.py

Cubre la clase nueva `estado de la entrega` y suena contra las cuatro clases ya
existentes, que no pueden cambiar de comportamiento con este cambio.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "doc-inventory.py")


def run(args, cwd=None):
    return subprocess.run(
        [sys.executable, SCRIPT] + args,
        capture_output=True, text=True, encoding="utf-8", cwd=cwd,
    )


class Base(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="docinv-")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write(self, name, text):
        path = os.path.join(self.root, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        return name

    def json_findings(self, extra=()):
        proc = run(["--root", self.root, "--json", *extra])
        self.assertIn(proc.returncode, (0, 3), proc.stderr)
        return json.loads(proc.stdout)["findings"]

    def delivery(self):
        return self.json_findings().get("delivery_state", [])


class EstadoDeLaEntrega(Base):
    """RED observado antes de implementar: estas diez comprobaciones fallaban."""

    def test_narracion_de_correccion(self):
        self.write("a.md", "# Título\n\nSe corrigió el error de la guía.\n")
        self.assertEqual(len(self.delivery()), 1)

    def test_narracion_de_reporte(self):
        self.write("a.md", "# Título\n\nQuedó reportado, no corregido.\n")
        self.assertEqual(len(self.delivery()), 1)

    def test_narracion_de_anterior(self):
        self.write("a.md", "# Título\n\nAntes decía otra cosa.\n")
        self.assertEqual(len(self.delivery()), 1)

    def test_narracion_de_antes_a_despues(self):
        self.write("a.md", "# Título\n\nLa página pasa de 15 secciones y 92.379 bytes a siete.\n")
        hallazgos = self.delivery()
        familias = sorted(item["family"] for item in hallazgos)
        self.assertEqual(familias, ["narracion", "recuento"], [item["excerpt"] for item in hallazgos])

    def test_recuento_que_caduca(self):
        self.write("a.md", "# Título\n\nEl fichero pesa 8.185 bytes.\n")
        self.assertEqual(self.delivery()[0]["family"], "recuento")

    def test_salta_bloque_de_codigo(self):
        self.write(
            "a.md",
            "# Título\n\n```text\nSe corrigió el error.\nPasa de 15 secciones.\n```\n\nNada más.\n",
        )
        self.assertEqual(self.delivery(), [])

    def test_salta_bloque_de_codigo_tilde(self):
        self.write("a.md", "# Título\n\n~~~\nSe corrigió el error.\n~~~\n")
        self.assertEqual(self.delivery(), [])

    def test_no_es_hallazgo_la_cita_de_la_propia_regla(self):
        self.write("a.md", "# Título\n\nDeja fuera las narraciones: «se corrigió», «antes decía».\n")
        self.assertEqual(self.delivery(), [])

    def test_registro_de_trabajo_exento(self):
        self.write(
            "a.md",
            "# Registro\n\n## Specs\n\nS1.\n\n## Tasks\n\nT1.\n\n## Log\n\nL1 Se corrigió y quedó reportado.\n",
        )
        self.assertEqual(self.delivery(), [])

    def test_salida_tres_y_ruta_linea(self):
        self.write("a.md", "# Título\n\nSe corrigió el error.\n")
        proc = run(["--root", self.root])
        self.assertEqual(proc.returncode, 3)
        self.assertIn("- estado de la entrega: a.md:3", proc.stdout)

    def test_frase_de_dominio_git_no_es_hallazgo(self):
        self.write(
            "a.md",
            "# Git\n\n## Rama\n\nLa rama de release se borra tras el commit.\n"
            "El SHA y el mensaje del commit se muestran al cerrar.\n",
        )
        self.assertEqual(self.delivery(), [])

    def test_fijacion_de_un_tercero_enlazada_no_es_hallazgo(self):
        self.write(
            "a.md",
            "# Skills\n\n## Procedencia\n\n"
            "Fijada en el commit [`a0bfa56`](https://github.com/mgechev/skills-best-practices/commit/"
            "a0bfa56bbcd676383f6ca57bb7e344d0856bc38e) del 2026-07-27.\n",
        )
        self.assertEqual(self.delivery(), [])


class ReferenciaGit(Base):
    """El registro de trabajo tampoco conserva referencias de Git."""

    def test_sha_en_registro_de_trabajo_si_es_hallazgo(self):
        self.write(
            "a.md",
            "# Registro\n\n## Specs\n\nS1.\n\n## Log\n\nL1 Cerrado en `802f79a feat(x): y`.\n",
        )
        hallazgos = self.delivery()
        self.assertEqual([item["family"] for item in hallazgos], ["gitref"])

    def test_sha_suelto_en_prosa_de_guia(self):
        self.write("a.md", "# Guia\n\nSe integró como 1a2b3c4 en la rama principal.\n")
        self.assertEqual(self.delivery()[0]["family"], "gitref")

    def test_pin_enlazado_de_un_tercero_no_es_hallazgo(self):
        self.write(
            "a.md",
            "# Skills\n\n## Procedencia\n\nFijada en el commit [`a0bfa56`]"
            "(https://github.com/mgechev/skills-best-practices/commit/a0bfa56bbcd676383f6ca57bb7e344d0856bc38e).\n",
        )
        self.assertEqual(self.delivery(), [])

    def test_hex_largo_de_recibo_no_es_hallazgo(self):
        self.write("a.md", "# Diagramas\n\n## Recibo\n\nEl `sha256` del artefacto es `d3208c0e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c`.\n")
        self.assertEqual(self.delivery(), [])

    def test_politica_de_commit_no_es_hallazgo(self):
        self.write(
            "a.md",
            "# Contribuir\n\n## Commits\n\nNingún commit se ejecuta sin confirmación explícita.\n"
            "Los cambios se dejan preparados en el stage.\nTrabajo directo en `main` para tareas pequeñas.\n",
        )
        self.assertEqual(self.delivery(), [])

    def test_frases_de_estado_de_la_entrega(self):
        self.write("a.md", "# Registro\n\n## Log\n\nL1 Quedó commiteado y el árbol limpio.\n")
        self.assertEqual([item["family"] for item in self.delivery()], ["gitstate"])

    def test_rutas_de_fichero_no_son_sha(self):
        self.write("a.md", "# Guia\n\n## Uso\n\nEdita `deadbeef.md` y `scripts/doc-deadbeef.py`.\n")
        self.assertEqual(self.delivery(), [])


class ClasesPreexistentes(Base):
    """La comprobación diferencial: lo que ya se reportaba sigue reportándose igual."""

    def test_enlace_roto(self):
        self.write("a.md", "# A\n\n[Véase](falta.md).\n")
        hallazgos = self.json_findings()
        self.assertEqual(len(hallazgos["broken_links"]), 1)
        self.assertEqual(self.delivery(), [])

    def test_sin_h1(self):
        self.write("a.md", "Sin encabezado de nivel uno.\n")
        self.assertEqual(self.json_findings()["missing_h1"], ["a.md"])

    def test_documento_vacio(self):
        self.write("a.md", "\n")
        self.assertEqual(self.json_findings()["empty_documents"], ["a.md"])

    def test_h2_repetido(self):
        self.write("a.md", "# A\n\n## Uso\n\nTexto.\n")
        self.write("b.md", "# B\n\n## Uso\n\nTexto.\n")
        self.assertEqual(self.json_findings()["duplicate_h2"]["uso"], ["a.md", "b.md"])

    def test_arbol_limpio_sale_cero(self):
        self.write("a.md", "# A\n\n## Uso\n\nTexto verificable.\n")
        proc = run(["--root", self.root])
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_frontmatter_no_cuenta_como_titulo(self):
        self.write("a.md", "---\nname: x\ndescription: y\n---\n\nSin H1.\n")
        self.assertEqual(self.json_findings()["missing_h1"], ["a.md"])

    def test_error_de_uso(self):
        self.assertEqual(run(["--root", os.path.join(self.root, "no-existe")]).returncode, 2)
        self.write("a.md", "# A\n\nTexto.\n")
        self.assertEqual(run(["--root", self.root, "--glob", "src/*.md"]).returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
