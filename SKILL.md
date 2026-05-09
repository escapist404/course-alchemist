---
name: course-alchemist
description: Transform STEM course materials such as scanned PDFs, slides, textbooks, notes, exercise sets, and past exams into self-contained Chinese ctex LaTeX review notes, knowledge structures, practice sets, problem banks, and mock exams with full solutions. Use for calculus, mathematical analysis, linear algebra, discrete mathematics, and general physics course review, exam sprint training, incremental course projects, TikZ figure redrawing, OCR review notes, and local problem-bank workflows.
---

# Course Alchemist

将理工科课程资料重构为中文 LaTeX 复习讲义，并生成分层习题、题库与模拟试卷。默认目标不是复刻原资料或做普通 OCR 摘要，而是产出可直接学习、复习和训练考试的成品材料。

## Core Workflow

1. 判定用户目标：系统复习、冲刺训练、题库整理、试卷生成、增量更新，或这些模式的组合。
2. 盘点输入材料：文字 PDF、扫描 PDF、PPT、课堂笔记、习题册、往年题、题目图片、已有课程项目目录或考试风格描述。
3. 若用户提供已有课程项目，先读取 `course.yml`、`state.yml`、已有 `tex/`、`problem_bank/` 和 `review_notes/`，延续术语、符号、编号、题库标签和模板。
4. 先为目标章节生成“学生困惑审计”：列出最小知识点、隐含前置概念、常见跳步、容易被老师一笔带过的问题，并据此追问或回填讲义。系统复习、增量更新和题库讲解都必须执行这一步。
5. 生成或更新中文 `ctex` LaTeX 产物：讲义优先，按需附习题、解析、题库条目和模拟卷。
6. 对公式、OCR、图像、缺页、题意不确定处写入 `review_notes/`，不要把核对噪声塞进正文。
7. 尽量编译或做结构检查；最终说明产物路径、验证结果、困惑审计覆盖结果和仍需人工核对的事项。

## Mode Selection

- 系统复习：生成完整讲义、知识关联、推导、典型例题和分层练习。
- 冲刺训练：压缩高频考点、公式方法、易错点、限时训练和模拟卷。
- 题库模式：抽取、改编或生成题目，维护本地题库标签和完整解析。
- 试卷模式：按分值、时间、题型比例、考点覆盖、难度比例和往年题风格组卷。
- 增量更新：只改本次目标章节或材料，更新状态文件，并保持既有风格一致。

若用户没有指定模式，默认顺序为：高质量讲义、知识结构、分层习题、模拟卷。

## Output Defaults

- 讲义使用中文 `ctex`，默认以 `assets/templates/ctex-review-template.tex` 的版式和环境为起点。
- 物理、多元微积分、线性代数等强空间直觉内容必须主动安排图示；数学和物理示意图优先用 TikZ/PGFPlots 重绘，无法可靠重绘时保留原图并解释。
- 习题和试卷默认给完整解答，可按需追加评分点、易错点和变式提示。
- 模拟卷默认 100 分、120 分钟、难度比例为基础掌握 30%、考试常规 50%、拔高区分 20%。
- 若有往年题，优先拟合往年题的题型比例、表述方式、计算量和常考点。

## References

按需读取这些文件，不要一次性加载全部：

- `references/course-project.md`：创建或维护课程项目目录、`course.yml`、`state.yml` 时读取。
- `references/confusion-audit.md`：生成或更新讲义、例题解析、题库讲解时读取，用于强制检查学生困惑点是否被覆盖。
- `references/problem-bank.md`：建立题库、抽题、组卷、标注题目元数据时读取。
- `references/source-processing.md`：处理 PDF、扫描件、PPT、题目照片、往年题或 TikZ 重绘时读取。
- `references/example-tasks.md`：需要判断典型请求应走哪种模式、输出什么、如何验收时读取。

## Quality Bar

- 正文应自成一体，补齐必要定义、定理条件、推导步骤、例题方法和考试触发点。
- “系统性”必须体现为足够细的基础铺垫：每个主要概念块都要能回答“它是什么、为什么需要这些条件、从哪里来、怎么用、学生会卡在哪里、卡住时先看哪一步”。
- 不能默认读者已经理解教师或模型容易跳过的中间知识。若一个结论依赖定义展开、符号约定、代数变形、几何直觉、单位量纲、极限/积分/线性代数前置事实，应在正文或例题解析中显式交代。
- 讲义生成后必须做困惑点覆盖检查：把预设困惑清单逐项映射到定义、解释、例题、图示、易错点或练习；没有覆盖的项补入正文，仍依赖用户材料确认的项写入 `review_notes/confusion-audit.md`。
- 不在正文反复标注“来自课件”“来自参考书”“模型补充”等来源差异；不确定性进入 `review_notes/`。
- 术语、符号、编号、图形风格、题库标签和难度标准保持一致。
- 物理讲义不能只堆公式；受力、场线、通量、高斯面、等势面、坐标系、线性变换、曲面/区域等关键空间关系应有足够图示支撑。
- 图示必须可读且物理/数学关系正确：文字标注不能遮挡或压住图形，电场线/流线/轨迹等不应出现违背概念的相交，图内只保留必要符号 label，解释性文字放到正文或图注。
- LaTeX 产物应能编译；如果无法编译，明确说明原因、未验证风险和下一步修复建议。
- 对扫描资料不要只信 OCR；公式、图形、板书结构和题目排版必须结合视觉核对。
