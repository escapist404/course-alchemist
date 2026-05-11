# TikZ Figure Validation Example

This official example is promoted from `runs/experiment006`. It demonstrates the Course Alchemist TikZ figure workflow for calculus, general physics, and linear algebra figures.

The example keeps the source of truth small and auditable:

- `source/tikz-svg-validation-set.md`: concrete figure requirements.
- `source/figure-ir.json`: explicit figure IR with semantic evidence checks.
- `figures/tikz/*.tex`: TikZ snippets without LaTeX figure wrappers.
- `tex/main.tex`: a native `ctexart` document that embeds the TikZ snippets.
- `review_notes/*.md`: manual audits for figure semantics, geometric relations, and label placement.

Run validation from the repository root:

```bash
python scripts/validate_tikz_figures.py assets/examples/tikz-figure-validation --output .test_tmp/tikz-example-build
```

Compile the ctex wrapper document:

```bash
mkdir -p .test_tmp/tikz-example-latex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=../../../../.test_tmp/tikz-example-latex main.tex
```

Run the compile command from `assets/examples/tikz-figure-validation/tex`.

## 中文说明

本官方样例来自 `runs/experiment006`，用于展示 Course Alchemist 的 TikZ 图示生成流程。它覆盖微积分、普通物理、线性代数三类图示，并保留显式 IR、TikZ 源码、ctex 嵌入文档和人工审计记录。

样例的重点不是“能画出来”而是“能验收”：先用 IR 检查语义证据，再编译导出 SVG，最后人工检查图像关系、标签归属、遮挡和裁切。
