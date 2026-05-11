# Course Alchemist

Course Alchemist is a Codex skill for reconstructing STEM course materials into
self-contained Chinese `ctex` review notes, practice sets, local problem banks,
mock exams, and verified teaching figures.

It is designed for exam review and course-material reconstruction in subjects
such as calculus, mathematical analysis, linear algebra, discrete mathematics,
and general physics. OCR output, scanned pages, formulas, and figures are
treated as traceable source material, not final prose.


Course Alchemist 是一个面向理工科课程资料重构的 Codex skill。它的目标不是做普通 OCR 摘要，而是把教材、课件、扫描讲义、习题、往年题等资料整理成可直接复习和训练的中文 `ctex` 讲义、习题集、题库、模拟卷和可验收图示。

## Highlights

- Chinese `ctex` review-note generation with course-project state tracking.
- Confusion-audit driven writing for definitions, derivations, examples, and
  exercises.
- Local scanned textbook processing with page records and review notes.
- TikZ figure generation with explicit IR, semantic evidence checks, standalone
  compilation, SVG export, and manual audit notes.
- Reusable LaTeX templates and official examples under `assets/examples/`.

- 生成中文 `ctex` 复习讲义，并维护课程项目状态。
- 用“学生困惑审计”驱动定义、推导、例题、练习和易错点写作。
- 处理扫描教材，保留页图、OCR、结构化记录和人工核对事项。
- 生成 TikZ 教学图示：先构建显式 IR，再检查语义证据、编译、导出 SVG，并记录人工审计。
- 通过 `assets/templates/` 和 `assets/examples/` 复用模板与官方样例。

## Repository Layout

- `SKILL.md`: main Codex skill instructions.
- `references/`: workflow references for source processing, course projects,
  confusion audits, writing style, examples, and problem banks.
- `assets/templates/`: Chinese LaTeX templates, shared style files, and the
  TikZ standalone wrapper.
- `assets/examples/calculus-continuity-review/`: example course review project.
- `assets/examples/tikz-figure-validation/`: official TikZ/IR/SVG figure
  validation example, promoted from `runs/experiment006`.
- `scripts/process_scanned_textbook.py`: local-first scanned PDF processing.
- `scripts/validate_tikz_figures.py`: TikZ snippet validation, compilation, and
  SVG export.
- `tests/`: unit tests.

## Typical Workflow

1. Collect course sources: PDFs, scanned textbooks, slides, notes, exercises,
   photos, and past exams.
2. Create or update a course project with `course.yml`, `state.yml`, `tex/`,
   `problem_bank/`, and `review_notes/`.
3. Convert scanned source material into structured page records when needed.
4. Generate Chinese `ctex` notes, examples, exercises, solutions, and mock exams.
5. For figures, build explicit IR first, then generate TikZ snippets and run
   semantic plus compile/export validation.
6. Keep uncertain formulas, figure issues, OCR errors, and source conflicts in
   `review_notes/`.
7. Compile or structurally validate outputs before delivery.

## TikZ Figure Workflow

The official example lives at `assets/examples/tikz-figure-validation/`.

Validate the example from the repository root:

```bash
python scripts/validate_tikz_figures.py assets/examples/tikz-figure-validation --output .test_tmp/tikz-example-build
```

The validator reads `source/figure-ir.json`, checks source-level semantic
evidence, compiles each TikZ snippet with a standalone wrapper, exports SVG, and
writes `report.md` plus `manifest.json`.

The example also includes manual audits:

- `review_notes/figure-audit.md`
- `review_notes/relationship-audit.md`
- `review_notes/label-audit.md`

## Scanned Textbook Pipeline

The scanned textbook helper can render pages, prepare enhanced images, run local
OCR when available, and write traceable JSON records plus review notes.

```bash
python scripts/process_scanned_textbook.py sources/textbook.pdf --output sources/processed/textbook --dpi 360
```

If optional PDF rendering or OCR tools are missing, the script still writes
placeholder assets and audit notes:

```bash
python scripts/process_scanned_textbook.py sources/textbook.pdf --expected-pages 12
```

Optional local components:

- PyMuPDF (`fitz`) for PDF rendering.
- Pillow for image preprocessing and thumbnails.
- Tesseract with `pytesseract` for local OCR.

## Tests

Run the Python unit tests from the repository root:

```bash
python -m unittest discover -s tests
```
