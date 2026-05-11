# Experiment006 Figure Audit

本文件记录 TikZ/SVG 验证集的生成结果。需求来源见 `runs/experiment006/source/tikz-svg-validation-set.md`，TikZ 源片段见 `runs/experiment006/figures/tikz/`，最终 SVG 见 `runs/experiment006/figures/svg/`，验证报告见 `runs/experiment006/build/tikz/report.md`。

验证命令：

```bash
python -m scripts.validate_tikz_figures runs/experiment006 --output runs/experiment006/build/tikz --no-preview
```

验证结果：9 张图全部通过独立编译与 SVG 导出。当前本机 `dvisvgm` 导出 PDF 时失败，脚本按设计使用 `pdftocairo` 生成 SVG，并在报告中记录为 QA 提醒。

- [x] `calc-01-derivative-tangent.svg`：导数切线与割线图；需人工检查 `P,Q` 是否均在曲线上、切线/割线是否区分清楚、`\Delta x` 是否位于水平投影之间。
- [x] `calc-02-riemann-area.svg`：定积分矩形逼近图；需人工检查矩形是否在 `[a,b]` 内、曲线是否清楚、填充区域是否位于曲线下方。
- [x] `calc-03-polar-sector.svg`：极坐标扇环区域；需人工检查内外半径、角向箭头、小面积元位置和区域边界。
- [x] `phys-01-projectile-motion.svg`：斜抛运动分解；需人工检查 `v_{0x}`、`v_{0y}`、`g` 的方向和轨迹形状。
- [x] `phys-02-point-charge-field.svg`：正点电荷电场线；需人工检查电场线是否径向向外、是否不相交、等势圆是否保持辅助地位。
- [x] `phys-03-inclined-plane-forces.svg`：斜面受力分析；需人工检查 `mg`、`N`、`f` 以及重力分量方向。
- [x] `linalg-01-linear-transform-grid.svg`：线性变换网格；需人工检查右侧网格是否为两组平行线、`Ae_1,Ae_2` 是否不共线。
- [x] `linalg-02-projection-subspace.svg`：正交投影；需人工检查投影点是否在 `L` 上、残差是否垂直于 `L`、直角标记是否位于垂足。
- [x] `linalg-03-eigenvector-action.svg`：特征向量作用；需人工检查 `v` 与 `Av` 是否共线、`w` 与 `Aw` 是否不共线。
