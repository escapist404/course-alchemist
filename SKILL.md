---
name: course-alchemist
description: Transform STEM course materials such as scanned PDFs, slides, textbooks, notes, exercise sets, and past exams into self-contained Chinese ctex LaTeX review notes, knowledge structures, practice sets, problem banks, mock exams, and validated TikZ/SVG figures with full solutions. Use for calculus, mathematical analysis, linear algebra, discrete mathematics, and general physics course review, exam sprint training, incremental course projects, TikZ figure generation, OCR review notes, and local problem-bank workflows.
---

# Course Alchemist

将理工科课程资料重构为中文 LaTeX 复习讲义，并生成分层习题、题库与模拟试卷。默认目标不是复刻原资料或做普通 OCR 摘要，而是产出可直接学习、复习和训练考试的成品材料。

## Core Workflow

1. 判定用户目标：系统复习、冲刺训练、题库整理、试卷生成、增量更新，或这些模式的组合。
2. 盘点输入材料：文字 PDF、扫描 PDF、PPT、课堂笔记、习题册、往年题、题目图片、已有课程项目目录或考试风格描述。
3. 若用户提供已有课程项目，先读取 `course.yml`、`state.yml`、已有 `tex/`、`problem_bank/` 和 `review_notes/`，延续术语、符号、编号、题库标签和模板。
4. 先为目标章节生成“学生困惑审计”：从真实学习、做题和复习场景出发，列出最小知识点、隐含前置概念、常见跳步、容易被老师一笔带过的问题，并把高价值困惑自然转化为正文中的解释、注记、例题选择理由和方法触发点。系统复习、增量更新和题库讲解都必须执行这一步。
5. 生成或更新中文 `ctex` LaTeX 产物：讲义优先，按需附习题、解析、题库条目和模拟卷。正文口吻按 `references/writing-style.md` 校准为专业教科书风格。
6. 对公式、OCR、图像、缺页、题意不确定处写入 `review_notes/`，不要把核对噪声塞进正文。
7. 对新增 TikZ 图示运行独立编译与 SVG 验证；尽量编译讲义或做结构检查。最终说明产物路径、验证结果、困惑审计覆盖结果、写作风格检查结果、图示 QA 结果和仍需人工核对的事项。

## Mode Selection

- 系统复习：生成完整讲义、知识关联、推导、典型例题和分层练习。
- 冲刺训练：压缩高频考点、公式方法、易错点、限时训练和模拟卷。
- 题库模式：抽取、改编或生成题目，维护本地题库标签和完整解析。
- 试卷模式：按分值、时间、题型比例、考点覆盖、难度比例和往年题风格组卷。
- 增量更新：只改本次目标章节或材料，更新状态文件，并保持既有风格一致。

若用户没有指定模式，默认顺序为：高质量讲义、知识结构、分层习题、模拟卷。

## Output Defaults

- 讲义使用中文 `ctex`，默认以 `assets/templates/ctex-review-template.tex` 的版式和环境为起点。
- 讲义正文默认采用中文专业教材式叙述：客观、克制、逻辑递进，避免聊天式、营销式、总结式和显露生成痕迹的表达。
- 物理、多元微积分、线性代数等强空间直觉内容应主动判断是否需要图示；数学和物理标准示意图默认先尝试 TikZ/PGFPlots 片段，并通过 `scripts/validate_tikz_figures.py` 生成静态 SVG。
- TikZ 片段放在课程项目的 `figures/tikz/`，验收后的 SVG 放在 `figures/svg/`，编译日志、wrapper、预览和报告放在 `build/tikz/`。
- 生成 TikZ 前必须先写显式图示 IR，默认保存为 `source/figure-ir.json`；IR 应说明图的教学目的、视觉对象、必要语义关系、禁止关系和可检查证据。
- 无法可靠确认方向、拓扑、标签含义或源图关系时，不要臆造 TikZ 图；保留可靠原图或裁剪，并把核对项写入 `review_notes/figure-audit.md`。
- 习题和试卷默认给完整解答，可按需追加评分点、易错点和变式提示。
- 模拟卷默认 100 分、120 分钟、难度比例为基础掌握 30%、考试常规 50%、拔高区分 20%。
- 若有往年题，优先拟合往年题的题型比例、表述方式、计算量和常考点。

## References

按需读取这些文件，不要一次性加载全部：

- `references/course-project.md`：创建或维护课程项目目录、`course.yml`、`state.yml` 时读取。
- `references/confusion-audit.md`：生成或更新讲义、例题解析、题库讲解时读取，用于强制检查学生困惑点是否被覆盖。
- `references/writing-style.md`：生成或润色讲义正文时读取，用于把叙述校准为专业教科书风格并去除 AI 味。
- `references/problem-bank.md`：建立题库、抽题、组卷、标注题目元数据时读取。
- `references/source-processing.md`：处理 PDF、扫描件、PPT、题目照片、往年题、TikZ/SVG 图示生成或图像核对时读取。
- `references/example-tasks.md`：需要判断典型请求应走哪种模式、输出什么、如何验收时读取。

## Quality Bar

- 正文应自成一体，补齐必要定义、定理条件、推导步骤、例题方法和考试触发点。
- 正文应像经过教材编辑整理的讲义，而不是问答回复或模型总结；优先使用定义、命题、说明、证明、例题、解、注记等稳定教学单元承载内容。
- “系统性”必须体现为足够细的基础铺垫：每个主要概念块都要能回答“它是什么、为什么需要这些条件、从哪里来、怎么用、真实读者会在哪里卡住、这处卡顿如何推动下一段解释或例题”。
- 不能默认读者已经理解教师或模型容易跳过的中间知识。若一个结论依赖定义展开、符号约定、代数变形、几何直觉、单位量纲、极限/积分/线性代数前置事实，应在正文或例题解析中显式交代。
- 讲义生成后必须做困惑点覆盖检查：把预设困惑清单逐项映射到定义、解释、例题、图示、易错点或练习；没有覆盖的项补入正文。补入方式应自然服务当前段落，避免把困惑点机械列成“学生可能会问”的清单。仍依赖用户材料确认的项写入 `review_notes/confusion-audit.md`。
- 不在正文反复标注“来自课件”“来自参考书”“模型补充”等来源差异；不确定性进入 `review_notes/`。
- 不使用“下面我们来”“需要注意的是”“总的来说”“通过以上内容”“希望本讲义能够帮助”等泛化串场；不要自称、不要提及生成过程、不要把教学目标写成产品说明。
- 术语、符号、编号、图形风格、题库标签和难度标准保持一致。
- 物理讲义不能只堆公式；受力、场线、通量、高斯面、等势面、坐标系、线性变换、曲面/区域等关键空间关系应通过清晰文字、已验证 TikZ/SVG、可靠图像引用或图示核对清单支撑。
- 每张 TikZ 图必须先有图示目标，再生成片段并独立编译为 SVG；图内只保留必要 label，解释性句子进入正文或 caption。
- 验证 TikZ 图时必须同时检查 IR 语义：对象、方向、拓扑、分量关系、投影/变换关系等核心语义若无法从 TikZ 源或人工视觉 QA 中确认，则图示不得视为通过。
- 图示或源图必须可读且物理/数学关系正确；标签不得遮挡曲线、箭头、面域、坐标轴、粒子、边界线或填充区域。无法确认的方向、符号含义、标签遮挡和源图歧义写入 `review_notes/figure-audit.md`。
- LaTeX 产物应能编译；如果无法编译，明确说明原因、未验证风险和下一步修复建议。
- 对扫描资料不要只信 OCR；公式、图形、板书结构和题目排版必须结合视觉核对。
- 定稿前做一次风格扫读：删去空泛评价、重复铺垫和口语化提示，把“AI 式概括”改成可验证的定义、条件、推导、例题或注记。
