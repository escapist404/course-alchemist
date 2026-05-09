# Course Alchemist

Course Alchemist is a Codex skill for turning STEM course materials into
self-contained Chinese `ctex` review notes, practice sets, local problem banks,
and mock exams with full solutions.

The project is aimed at exam review and course-material reconstruction for
subjects such as calculus, mathematical analysis, linear algebra, discrete
mathematics, and general physics. It treats OCR output as source material, not
as final prose: scanned pages, formulas, figures, and uncertain source details
are kept traceable so the final notes can be checked and improved.

## What It Contains

- `SKILL.md`: the main Codex skill instructions.
- `references/`: workflow references for course projects, source processing,
  confusion audits, example requests, and scanned textbook pipelines.
- `assets/templates/`: Chinese LaTeX review templates and shared style files.
- `assets/examples/`: a sample calculus continuity review project.
- `assets/fonts/windows-ctex/`: Windows Chinese fonts used by the LaTeX template.
- `scripts/process_scanned_textbook.py`: a local-first scanned PDF processing
  pipeline.
- `tests/`: unit tests for the scanned textbook processing script.

## Typical Workflow

1. Collect course sources such as PDFs, scanned textbooks, slides, notes,
   exercises, photos, and past exams.
2. Create or update a course project with `course.yml`, `state.yml`, `tex/`,
   `problem_bank/`, and `review_notes/`.
3. Convert scanned source material into structured page records when needed.
4. Generate Chinese `ctex` notes, examples, exercises, solutions, and mock exams.
5. Keep uncertain formulas, figures, OCR issues, and source conflicts in
   `review_notes/` instead of mixing them into the final teaching text.
6. Compile or structurally validate the LaTeX output before delivery.

## Scanned Textbook Pipeline

The scanned textbook helper can render pages, prepare enhanced images, run local
OCR when available, and write traceable JSON records plus review notes.

```powershell
python scripts/process_scanned_textbook.py sources/textbook.pdf --output sources/processed/textbook --dpi 360
```

If optional PDF rendering or OCR tools are missing, the script still writes
placeholder assets and audit notes:

```powershell
python scripts/process_scanned_textbook.py sources/textbook.pdf --expected-pages 12
```

Optional local components:

- PyMuPDF (`fitz`) for PDF rendering.
- Pillow for image preprocessing and thumbnails.
- Tesseract with `pytesseract` for local OCR.

## Tests

Run the Python unit tests from the repository root:

```powershell
python -m unittest discover -s tests
```

## LaTeX Notes

The default review-note template lives at
`assets/templates/ctex-review-template.tex`. It is designed for Chinese `ctex`
documents and can use the bundled Windows CJK fonts. Generated PDFs are ignored
by git; keep source `.tex` and structured course data under version control.
