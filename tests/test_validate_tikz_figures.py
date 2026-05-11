import json
import shutil
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from scripts import validate_tikz_figures as validator


class TikzDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = Path.cwd() / "test-output-validate-tikz"
        shutil.rmtree(self.sandbox, ignore_errors=True)
        (self.sandbox / "figures" / "tikz").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.sandbox, ignore_errors=True)

    def test_discovers_tex_figures_directory(self):
        figure = self.sandbox / "figures" / "tikz" / "fig01-demo.tex"
        figure.write_text(r"\begin{tikzpicture}[>=Latex]\end{tikzpicture}", encoding="utf-8")

        self.assertEqual(validator.discover_figure_files([self.sandbox]), [figure.resolve()])

    def test_wrapper_uses_shared_preamble_and_target_input(self):
        figure = self.sandbox / "figures" / "tikz" / "fig01-demo.tex"
        figure.write_text(r"\begin{tikzpicture}[>=Latex]\end{tikzpicture}", encoding="utf-8")

        wrapper = validator.build_wrapper_content(figure)

        self.assertIn(r"\usepackage{course-alchemist-review}", wrapper)
        self.assertIn(r"\usetikzlibrary", wrapper)
        self.assertIn(figure.resolve().as_posix(), wrapper)

    def test_axis_snippet_is_wrapped_in_tikzpicture(self):
        figure = self.sandbox / "figures" / "tikz" / "fig-axis.tex"
        figure.write_text(r"\begin{axis}\addplot coordinates {(0,0)};\end{axis}", encoding="utf-8")

        wrapper = validator.build_wrapper_content(figure)

        self.assertIn(r"\begin{tikzpicture}", wrapper)
        self.assertIn(figure.resolve().as_posix(), wrapper)
        self.assertIn(r"\end{tikzpicture}", wrapper)


class TikzStaticAnalysisTests(unittest.TestCase):
    def test_detects_missing_tikzpicture(self):
        issues, _, _ = validator.static_analyze(r"\draw (0,0) -- (1,1);")

        self.assertTrue(any(issue.severity == "error" and "missing" in issue.message for issue in issues))

    def test_detects_outer_figure_wrapper(self):
        content = r"\begin{figure}\begin{tikzpicture}\end{tikzpicture}\caption{demo}\end{figure}"
        issues, _, _ = validator.static_analyze(content)

        self.assertTrue(any(issue.severity == "error" and "figure/caption" in issue.message for issue in issues))

    def test_detects_long_node_text(self):
        content = r"\begin{tikzpicture}[>=Latex]\node {这是一段过长的解释性文字};\end{tikzpicture}"
        issues, _, _ = validator.static_analyze(content)

        self.assertTrue(any(issue.severity == "qa" and "long" in issue.message for issue in issues))


class TikzSemanticAnalysisTests(unittest.TestCase):
    def test_required_semantics_pass_when_evidence_is_present(self):
        ir = {
            "fig01-demo": {
                "purpose": "show an arrow",
                "entities": ["arrow"],
                "required_semantics": [
                    {
                        "id": "arrow-right",
                        "statement": "arrow points from origin to the right",
                        "evidence_all": [r"\\draw\[->", r"-- \(1,0\)"],
                    }
                ],
            }
        }

        errors, checks = validator.semantic_analyze(
            r"\begin{tikzpicture}[>=Latex]\draw[->] (0,0) -- (1,0);\end{tikzpicture}",
            "fig01-demo",
            ir,
        )

        self.assertEqual(errors, [])
        self.assertTrue(any("required pass" in check for check in checks))

    def test_required_semantics_fail_when_evidence_is_missing(self):
        ir = {
            "fig01-demo": {
                "purpose": "show an arrow",
                "entities": ["arrow"],
                "required_semantics": [
                    {
                        "id": "arrow-right",
                        "statement": "arrow points from origin to the right",
                        "evidence_all": [r"\\draw\[->", r"-- \(1,0\)"],
                    }
                ],
            }
        }

        errors, _ = validator.semantic_analyze(
            r"\begin{tikzpicture}[>=Latex]\draw (0,0) -- (1,0);\end{tikzpicture}",
            "fig01-demo",
            ir,
        )

        self.assertTrue(any("required evidence missing" in error for error in errors))


class TikzValidationCommandTests(unittest.TestCase):
    def setUp(self):
        self.sandbox = Path.cwd() / "test-output-validate-tikz"
        shutil.rmtree(self.sandbox, ignore_errors=True)
        (self.sandbox / "figures" / "tikz").mkdir(parents=True)
        self.figure = self.sandbox / "figures" / "tikz" / "fig01-demo.tex"
        self.figure.write_text(
            r"\begin{tikzpicture}[>=Latex]\draw (0,0) -- (1,1);\end{tikzpicture}",
            encoding="utf-8",
        )
        self.output = self.sandbox / "build" / "tikz"

    def tearDown(self):
        shutil.rmtree(self.sandbox, ignore_errors=True)

    def test_missing_tools_produces_static_only_result(self):
        tools = validator.ToolState(xelatex=None, dvisvgm=None, pdfcrop=None, pdftocairo=None, qlmanage=None)

        result = validator.validate_figure(self.figure, self.output, tools)

        self.assertEqual(result.status, "static-only")
        self.assertTrue(any("static-only" in item for item in result.qa_items))

    def test_successful_toolchain_writes_svg_metadata(self):
        tools = validator.ToolState(
            xelatex="/bin/xelatex",
            dvisvgm="/bin/dvisvgm",
            pdfcrop=None,
            pdftocairo=None,
            qlmanage=None,
        )

        def fake_run(command, env=None):
            if "xelatex" in command[0]:
                (self.output / "wrappers" / "fig01-demo.wrapper.pdf").write_text("pdf", encoding="utf-8")
            if "dvisvgm" in command[0]:
                (self.output / "svg" / "fig01-demo.svg").write_text(
                    '<svg width="42pt" height="24pt"></svg>',
                    encoding="utf-8",
                )
            return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

        with mock.patch.object(validator, "run_command", side_effect=fake_run):
            result = validator.validate_figure(self.figure, self.output, tools, preview=False)

        self.assertEqual(result.status, "passed")
        self.assertEqual(result.width, "42pt")
        self.assertEqual(result.height, "24pt")

    def test_main_writes_manifest_and_returns_nonzero_on_static_error(self):
        bad = self.sandbox / "figures" / "tikz" / "bad.tex"
        bad.write_text(r"\draw (0,0) -- (1,1);", encoding="utf-8")

        with mock.patch.object(validator, "detect_tools", return_value=validator.ToolState(None, None, None, None, None)):
            exit_code = validator.main([str(bad), "--output", str(self.output)])

        manifest = json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 1)
        self.assertEqual(manifest["figure_count"], 1)
        self.assertEqual(manifest["failed_count"], 1)
        self.assertTrue((self.output / "report.md").exists())

    def test_main_uses_default_project_ir_for_semantic_checks(self):
        ir_path = self.sandbox / "source" / "figure-ir.json"
        ir_path.parent.mkdir(parents=True)
        ir_path.write_text(
            json.dumps(
                {
                    "figures": [
                        {
                            "id": "fig01-demo",
                            "purpose": "show a diagonal arrow",
                            "entities": ["diagonal arrow"],
                            "required_semantics": [
                                {
                                    "id": "has-arrow",
                                    "statement": "figure uses a drawn path",
                                    "evidence_all": [r"\\draw"],
                                }
                            ],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        with mock.patch.object(validator, "detect_tools", return_value=validator.ToolState(None, None, None, None, None)):
            exit_code = validator.main([str(self.sandbox), "--output", str(self.output)])

        manifest = json.loads((self.output / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(exit_code, 0)
        self.assertEqual(manifest["semantic_error_count"], 0)
        self.assertGreater(manifest["semantic_check_count"], 0)


if __name__ == "__main__":
    unittest.main()
