# Course Alchemist 交接说明

这份文档用于把当前 `course-alchemist` skill 的设计与实现状态交接给新的 Codex 智能体，以便无缝继续下一步工作。

## 项目背景

我们正在设计并实现一个 Codex skill，名称为 `course-alchemist`。

目标是设计一个面向理工科大学生的 skill，用于将数学和普通物理课程资料重构为高质量中文 LaTeX 复习讲义，并生成分层习题、专题训练和模拟试卷。

它主要解决两个痛点：

1. 原始讲义、课件、教材扫描件常常粗糙、跳步、删节、知识点关联弱，不利于构建知识图谱和系统掌握。
2. 练习题量少、难度不可控、与真实考试风格差异大，导致学生会知识但不适应考试题型。

目标课程包括：

- 高等数学
- 数学分析
- 线性代数
- 离散数学
- 普通物理

## 已确认需求

### 讲义类型

用户希望生成的 LaTeX 讲义可以偏向以下几种形态，并由用户选择：

- 考试复习提纲
- 课堂笔记增强版
- 训练手册
- 或三者混合

不要求固定章节结构。skill 应根据学习目标自动组织内容。

### 默认优先级

默认偏向讲义生成，但也需要能生成习题和试卷。

默认顺序：

1. 高质量、自成一体的中文 LaTeX 讲义
2. 知识结构整理
3. 分层习题或专题训练
4. 模拟试卷与完整解析

如果用户指定“冲刺模式”或“只生成试卷”，则可以调整顺序。

### 使用场景

主要面向：

- 系统性复习
- 期中/期末冲刺
- 按章节增量整理
- 根据往年题风格生成训练材料
- 本地题库维护

### 输入材料

skill 应支持：

- 图像型 PDF
- 扫描课件
- 扫描教材
- 文字 PDF
- PPT
- 课堂笔记
- 习题册
- 往年题
- 用户描述的考试风格
- 已有课程项目目录

### 图像 PDF 处理策略

用户不了解 OCR-only 和视觉理解方案优劣，最终决定采用效果最好的混合方案：

1. 先将 PDF 渲染为逐页图片，保留版面、图形和题目结构。
2. 同时尝试 OCR 或文本抽取，获得可复制文字和粗略公式。
3. 使用视觉理解逐页校对公式、图表、板书结构和题目排版。
4. 将定义、定理、例题、题干和解答重写为 LaTeX。
5. 对公式不确定、OCR 错误、缺页、图像理解不确定处生成独立核对清单。
6. 综合参考资料和课程上下文补全逻辑，生成自成一体的讲义。

如果资料是高质量文字 PDF，可走快速路径：文本抽取优先，图片和公式只做抽样核对。

### 参考书与题源

用户认为课本是公有版权，没有版权问题，可直接使用。

习题来源可以包括：

- 用户喂给 skill 的扫描版练习册
- 本地维护的题库
- 网上遴选题目
- 模型自行生成题目
- 往年题风格分析后改编或生成

题库是可选流程，不是必须每次启用。

### 习题与试卷控制维度

最重要的控制维度：

- 考点
- 难度

其他维度：

- 题型
- 计算量/证明量
- 考试风格
- 考试时间
- 分值结构

考试风格来源：

1. 用户提供若干份往年题，由 skill 分析题型比例、难度、计算量、表述方式和常考点。
2. 用户文字描述，例如“偏计算”“少证明”“喜欢大题套小问”“物理偏建模”等。

答案默认给完整解答。后续可按需追加评分点、易错点和变式提示。

### 模拟卷默认设置

如果用户没有自定义，默认采用：

- 总分：100 分
- 时间：120 分钟
- 难度：基础掌握 30%，考试常规 50%，拔高区分 20%
- 答案：完整解析
- 风格：若有往年题，优先拟合往年题；否则采用课程常见期末风格

### 图像处理

用户希望图像、数学图、普通物理示意图尽量用 TikZ/PGFPlots 重绘，保证版面风格统一。无法可靠重绘时，可以保留原图并配解释。

### 讲义正文来源标注

用户不希望讲义正文显式区分：

- 原课件已有内容
- skill 补充内容
- 参考资料补充内容
- OCR 不确定内容

最终讲义应脱胎于原始课件，但自成一体，读者只看生成讲义即可。

但仍建议保留独立 `review_notes/` 核对清单，用于记录 OCR、公式、图像和缺页等不确定内容，不进入正文。

### 增量更新

用户希望支持增量更新，也支持独立运行。

每门课应有一个课程项目目录，保存状态、模板、章节、题库和核对清单等，以便今天处理第 1 章，明天继续第 2 章时能保持：

- 术语一致
- 符号一致
- 编号一致
- 模板一致
- 题库标签一致
- 图形风格一致

## 已确定 skill 名称

英文名：`course-alchemist`

中文说明不需要另起花哨名字，直接描述功能即可：

> 将理工科课程资料重构为中文 LaTeX 复习讲义，并生成分层习题与模拟试卷。

## 已生成的文件

当前工作区路径：

`/Users/escapist404/Documents/Codex/2026-05-09/skill-review-pdf-latex-review`

skill 目录：

`/Users/escapist404/Documents/Codex/2026-05-09/skill-review-pdf-latex-review/course-alchemist`

已生成文件：

1. `course-alchemist/SKILL.md`
2. `course-alchemist/agents/openai.yaml`
3. `course-alchemist/assets/templates/ctex-review-template.tex`

## `SKILL.md` 当前内容概要

`SKILL.md` 已经包含：

- YAML frontmatter
  - `name: course-alchemist`
  - 英文 `description`
  - `metadata.short-description`
- 适用场景
- 默认原则
- 工作模式
  - 系统复习模式
  - 冲刺训练模式
  - 题库模式
  - 试卷模式
- 输入处理
- 图像 PDF 混合处理策略
- 输出项目结构
- 讲义生成要求
- 数学课程侧重点
- 普通物理侧重点
- 习题与试卷生成要求
- 增量更新流程
- 交互策略
- 质量检查
- 默认模板说明

## `agents/openai.yaml` 当前内容

文件路径：

`course-alchemist/agents/openai.yaml`

内容概要：

```yaml
interface:
  display_name: "Course Alchemist"
  short_description: "将理工科资料炼成 LaTeX 讲义与试卷"
  default_prompt: "Use $course-alchemist to turn my STEM course materials into Chinese LaTeX review notes and practice exams."

policy:
  allow_implicit_invocation: true
```

## 默认 `ctex` 讲义模板

文件路径：

`course-alchemist/assets/templates/ctex-review-template.tex`

模板目标：

- 中文 `ctexart`
- A4 页面
- 页边距窄一些，但保证阅读体验
- 支持数学公式
- 支持 TikZ / PGFPlots
- 内置页眉页脚
- 使用 `tcolorbox` 提供彩色框
- 适合理工科复习讲义、例题、考点、易错点和解答

模板当前边距设置：

```tex
\usepackage[
  a4paper,
  left=1.55cm,
  right=1.55cm,
  top=1.65cm,
  bottom=1.8cm,
  headheight=14pt,
  headsep=0.45cm,
  footskip=0.85cm
]{geometry}
```

模板内置环境：

- `definition`：定义
- `theorem`：定理
- `lemma`：引理
- `hint`：提示
- `examspot`：考点
- `pitfall`：易错点
- `attention`：需要关注的点
- `method`：方法
- `example`：例题
- `solutionbox`：解答

模板使用 `tcolorbox`，每类内容有不同颜色框。当前配色大致为：

- 定义：蓝色
- 定理：紫色
- 引理：青色
- 提示：绿色
- 考点：橙色
- 易错点：红色
- 关注点：灰蓝色
- 方法：墨绿色
- 例题：靛蓝色
- 解答：中性灰色

模板中包含一小段“连续性”示例内容，用于展示版面效果。实际作为模板使用时，可删除示例正文，仅保留导言区和环境定义。

## 编译验证

已经使用 bundled Tectonic 编译过模板。

编译命令使用的是：

```bash
/Users/escapist404/.codex/plugins/cache/openai-bundled/latex-tectonic/0.1.1/bin/tectonic --outdir /private/tmp/course-alchemist-template-build course-alchemist/assets/templates/ctex-review-template.tex
```

编译结果：

- 成功生成 PDF
- 输出路径：
  `/private/tmp/course-alchemist-template-build/ctex-review-template.pdf`
- 生成了预览图：
  `/private/tmp/course-alchemist-template-build/ctex-review-template.pdf.png`

编译中曾出现一个问题：

- 原模板加载了 `physics` 宏包，同时自定义了 `\dd`
- `physics` 已经定义了 `\dd`，导致冲突
- 已修复：删除了 `\usepackage{physics}`

当前模板编译成功，但有 macOS 中文字体 ToUnicode 映射警告：

- 这是中文字体相关警告
- 不影响 PDF 版面生成
- 后续如果需要跨平台可复现编译，建议明确配置开源中文字体或模板字体策略

## 当前状态

当前已经完成：

- 需求细化
- skill 名称确定
- skill 目录创建
- `SKILL.md` 初版
- `agents/openai.yaml` 初版
- 默认 `ctex` 讲义模板
- 模板编译验证
- 模板预览检查

尚未完成但建议下一步做：

1. 设计 `course.yml` schema
2. 设计 `state.yml` schema
3. 设计 `problem_bank` 题库 schema
4. 将 `ctex-review-template.tex` 拆分为更可复用的 `.sty` 或 `.cls`
5. 创建一个示例课程项目目录
6. 写一组测试任务，验证 skill 是否能按预期触发
7. 将 skill 安装到 `~/.codex/skills/course-alchemist`
8. 用真实课程资料试跑一次完整流程
9. 为图像 PDF 处理制定具体工具链，例如 PDF 渲染、OCR、图像理解、公式核对、TikZ 重绘策略
10. 为模拟卷和题库建立更严格的标签体系

## 重要设计倾向

后续继续工作时请保持这些倾向：

- 不要把 `course-alchemist` 做成单纯 OCR 工具。
- 不要只做资料摘要，要重构成可学习、可复习、可考试训练的成品讲义。
- 讲义默认自成一体，不要求读者回看原材料。
- 讲义结构不固定，应由用户目标决定。
- 默认偏系统复习，但支持冲刺训练。
- 习题和试卷默认给完整解答。
- 题库是可选流程，而非每次强制。
- 图像尽量 TikZ/PGFPlots 重绘。
- 不确定内容进入 `review_notes/`，不要塞进讲义正文。
- 支持课程项目目录和增量更新。
- 编辑时尽量保持 skill 简洁，避免加入 README、INSTALLATION_GUIDE 等额外文档。
