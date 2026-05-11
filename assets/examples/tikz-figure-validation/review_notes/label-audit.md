# Experiment006 标签关系审计

本审计检查标签与元素、标签与标签之间的关系：标签是否明确指代目标元素，是否因靠近其他元素产生歧义，是否与线条、箭头、边界或其他标签重叠。

## 已修正的问题

- `assets/templates/tikz-standalone-wrapper.tex`：加入 `\pagestyle{empty}`，去除单图 PDF/SVG 中的页码污染。
- `calc-01-derivative-tangent`：将 `tangent` 与 `secant` 标签移到对应直线旁侧，并加白底留白，避免压线和靠近边界导致误读。
- `calc-03-polar-sector`：将 `r_1` 改为外侧引线标签，将 `r_2`、`D`、径向 `r` 和 `dA` 分散放置，避免半径标签与边界射线、径向箭头和面积元标签互相干扰。
- `phys-01-projectile-motion`：仅保留一个 `g` 标签指代一组向下重力箭头，移动 `trajectory` 标签，避免与中间的重力箭头和轨迹曲线重叠。
- `phys-02-point-charge-field`：将 `equipotential` 改为外侧标签并用短引线指向虚线圆，避免它贴在径向电场线上而被误读为电场线标签。
- `phys-03-inclined-plane-forces`：为 `N`、`f`、`mg\sin\theta`、`mg\cos\theta` 标签增加位置偏移和白底留白，使它们分别清楚指向对应箭头。
- `linalg-02-projection-subspace`：移动投影向量与残差标签，避免残差标签压住虚线残差段或靠近直角标记。
- `linalg-03-eigenvector-action`：移动 `Aw` 标签，避免与水平轴线混在一起。

## 当前逐图结论

- `calc-01-derivative-tangent`：`P,Q,\Delta x,tangent,secant` 均有清楚归属，无标签重叠。
- `calc-02-riemann-area`：`a,b,f(x),\int_a^b f(x)\,dx` 位置稳定；积分标签位于填充区域内部但不遮挡边界关系。
- `calc-03-polar-sector`：`r_1,r_2,D,dA,r,\theta,\theta=\alpha` 间距已拉开；`r_1` 使用引线明确指向内圆弧。
- `phys-01-projectile-motion`：`v_0,v_{0x},v_{0y},g,trajectory,ground` 均不重叠；`g` 标签与向下箭头组的归属清楚。
- `phys-02-point-charge-field`：`\vec E` 指向径向电场线，`equipotential` 通过引线指向虚线圆，二者不再混淆。
- `phys-03-inclined-plane-forces`：主力与分量标签均邻近对应箭头，且与斜面、物块、角标保持可读间距。
- `linalg-01-linear-transform-grid`：`e_1,e_2,Ae_1,Ae_2,A,original,transformed` 均未压线，归属明确。
- `linalg-02-projection-subspace`：`v`、`\operatorname{proj}_L v`、残差、`L` 和直角标记互不遮挡。
- `linalg-03-eigenvector-action`：`v,w,Av=\lambda v,Aw,A,before,after` 均与目标向量或变换箭头保持明确关系。
