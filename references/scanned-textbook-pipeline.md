# Scanned Textbook Pipeline

本文件定义扫描版课本的额外组件、落盘结构和验收标准。目标不是复刻原书排版，而是把扫描件转成可追溯的结构化素材，供 Course Alchemist 继续生成中文 `ctex` 讲义、题库和试卷。

## Component Stack

- PDF 渲染：优先使用 PyMuPDF，将扫描 PDF 逐页渲染为 300-450 DPI 图片，默认 360 DPI。
- 图像预处理：优先使用 Pillow，保存原始 page image、增强图和缩略图。增强图用于 OCR，原图用于视觉校对。
- 本地 OCR：优先使用 Tesseract + `pytesseract`，输出正文候选和置信度。OCR 输出只作为素材，不直接进入最终讲义。
- 版面分析：初版使用保守启发式，将整页作为可追溯 block；后续可替换为 PaddleOCR、doclayout-yolo、surya 或同类 layout detector。
- 公式识别：初版将疑似公式 block 标记为 `needs_vision_review`，后续可接入 pix2tex、Mathpix、Nougat/LaTeX-OCR 或多模态模型。
- 图表处理：图形、表格和低置信度区域默认进入视觉 QA 或 TikZ/PGFPlots 重绘队列。
- 视觉 QA：多模态模型用于复核公式、图形、复杂版面、跨页内容和低置信度 OCR。

## Output Layout

默认输出目录为 `sources/processed/<source-stem>/`，也可以由 CLI 的 `--output` 指定。

```text
processed/<source-stem>/
├── manifest.json
├── pages/
│   └── p0001.png
├── enhanced/
│   └── p0001.png
├── thumbs/
│   └── p0001.jpg
├── page_records/
│   └── p0001.json
├── chapters/
│   └── <source-stem>.chapter.json
├── crops/
└── review_notes/
    └── source-audit.md
```

## Page Record Schema

每页至少包含：

- `page_id`
- `source_file`
- `page_number`
- `image_path`
- `thumbnail_path`
- `enhanced_image_path`
- `blocks`
- `uncertainties`

每个 block 至少包含：

- `type`: `heading | paragraph | formula | figure | table | example | exercise | footer | unknown`
- `bbox`: 原 PDF/page image 坐标；初版整页占位为 `[0, 0, 1, 1]`
- `text_candidate`
- `latex_candidate`
- `confidence`
- `needs_vision_review`
- `source_ref`
- `reading_order`
- `notes`

## CLI

```powershell
python scripts/process_scanned_textbook.py sources/textbook.pdf --output sources/processed/textbook --dpi 360
```

如果 PyMuPDF、Pillow 或 Tesseract 不可用，脚本仍会生成 manifest、页面占位、章节占位和核对清单。可用 `--expected-pages` 在无法读取 PDF 页数时指定保守页数：

```powershell
python scripts/process_scanned_textbook.py sources/textbook.pdf --expected-pages 12
```

## Vision QA Rules

以下情况必须进入视觉复核：

- OCR 置信度低于 0.86。
- block 类型为 `formula`、`figure`、`table` 或 `unknown`。
- 文本含视觉易混字符，如 `1/l/I`、`0/O`、`b/6`。
- 页面包含矩阵、分段函数、上下标密集公式、跨页例题或跨页习题。
- 版面顺序不明确，例如双栏、脚注、页眉页脚干扰。

复核结果建议归类为：

- `confirmed`: OCR/结构候选可用。
- `corrected`: 已按视觉校对修正。
- `uncertain`: 仍需人工确认，并写入 `review_notes/source-audit.md`。

## Acceptance Tests

- 页码和原 PDF 对齐。
- 每页都有可追溯的 page record。
- 所有 block 都有 `source_ref`、`bbox`、`confidence` 和 `needs_vision_review`。
- 展示公式不直接当成正文，必须保留 LaTeX 候选和视觉复核标记。
- 图形不被强行 OCR 成普通段落；无法确认时保留裁剪或进入重绘队列。
- 不确定项写入 `review_notes/source-audit.md`，最终讲义正文不堆叠 OCR 噪声。
