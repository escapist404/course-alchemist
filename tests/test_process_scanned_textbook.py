import json
import shutil
import unittest
from pathlib import Path

from scripts import process_scanned_textbook as pipeline


class ClassifyBlockTests(unittest.TestCase):
    def test_formula_candidates_require_review(self):
        block_type, latex, needs_review, notes = pipeline.classify_block("f(x)=x^2+1", 0.98)

        self.assertEqual(block_type, "formula")
        self.assertEqual(latex, "f(x)=x^2+1")
        self.assertTrue(needs_review)
        self.assertIn("formula candidate requires visual/LaTeX review", notes)

    def test_low_confidence_paragraph_requires_review(self):
        block_type, latex, needs_review, notes = pipeline.classify_block("连续函数的性质", 0.52)

        self.assertEqual(block_type, "paragraph")
        self.assertEqual(latex, "")
        self.assertTrue(needs_review)
        self.assertTrue(any("low OCR confidence" in note for note in notes))

    def test_heading_detection(self):
        block_type, _, needs_review, _ = pipeline.classify_block("第一章 函数与极限", 0.95)

        self.assertEqual(block_type, "heading")
        self.assertFalse(needs_review)


class OutputShapeTests(unittest.TestCase):
    def test_process_without_optional_pdf_renderer_writes_traceable_assets(self):
        sandbox_temp = Path.cwd() / "test-output-process-scanned-textbook"
        shutil.rmtree(sandbox_temp, ignore_errors=True)
        sandbox_temp.mkdir(exist_ok=True)
        try:
            source = sandbox_temp / "scan.pdf"
            source.write_bytes(b"%PDF-1.4\n% placeholder\n")
            output = sandbox_temp / "processed"

            exit_code = pipeline.main(
                [
                    str(source),
                    "--output",
                    str(output),
                    "--expected-pages",
                    "2",
                ]
            )

            self.assertEqual(exit_code, 0)
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            page_record = json.loads((output / "page_records" / "p0001.json").read_text(encoding="utf-8"))
            chapter = json.loads((output / "chapters" / "scan.chapter.json").read_text(encoding="utf-8"))
            audit = (output / "review_notes" / "source-audit.md").read_text(encoding="utf-8")

            self.assertEqual(manifest["page_count"], 2)
            self.assertEqual(manifest["processing_mode"], "hybrid-local-first")
            self.assertEqual(page_record["page_id"], "scan-p0001")
            self.assertEqual(page_record["blocks"][0]["type"], "unknown")
            self.assertTrue(page_record["blocks"][0]["needs_vision_review"])
            self.assertEqual(chapter["page_range"], [1, 2])
            self.assertIn("visual QA required", audit)
        finally:
            shutil.rmtree(sandbox_temp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
