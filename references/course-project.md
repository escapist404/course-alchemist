# Course Project Reference

读取本文件用于创建或维护长期课程项目，尤其是用户要求增量更新、继续上一章、保持符号一致或维护本地题库时。

## Directory Layout

推荐目录：

```text
<course-name>-review/
├── course.yml
├── state.yml
├── tex/
│   ├── main.tex
│   ├── chapters/
│   ├── problems.tex
│   ├── solutions.tex
│   └── exams/
├── figures/
├── tikz/
├── sources/
├── problem_bank/
└── review_notes/
```

一次性任务可以只生成 `main.tex`、`problems.tex`、`solutions.tex` 和 PDF；长期项目应保留 YAML 状态文件。

## course.yml

`course.yml` 记录稳定课程意图，不频繁改动。

```yaml
course:
  name: 高等数学
  audience: 理工科本科生
  language: zh-CN
  scope:
    - 函数、极限与连续
  source_types:
    - lecture_slides
    - textbook
    - past_exams
  default_mode: 系统复习
  output:
    latex_engine: tectonic
    template: assets/templates/ctex-review-template.tex
    figure_policy: tikz_first
exam_style:
  total_score: 100
  duration_minutes: 120
  difficulty_mix:
    基础掌握: 0.3
    考试常规: 0.5
    拔高区分: 0.2
  notes: 若无往年题，采用常见期末风格。
```

字段约定：

- `course.name`：课程名，必填。
- `course.scope`：当前项目覆盖范围，可以是章节、专题或考试范围。
- `course.source_types`：材料类型枚举，允许 `text_pdf`、`scanned_pdf`、`lecture_slides`、`textbook`、`notes`、`exercise_set`、`past_exams`、`images`。
- `course.output.template`：默认模板路径；用户提供模板时以用户模板为准。
- `exam_style`：默认组卷规则；用户临时指定时覆盖本文件。

## state.yml

`state.yml` 记录会随增量处理变化的状态。

```yaml
progress:
  processed_units:
    - id: ch01-continuity
      title: 函数的连续性
      outputs:
        - tex/main.tex
      source_refs:
        - sources/ch01-slides.pdf
  pending_units: []
conventions:
  notation:
    R: "\\mathbb{R}"
    dx: "\\,\\mathrm{d}x"
  theorem_numbering: within_section
  figure_style: tikz_pgplots_clean
terms:
  连续: 函数值等于极限值
  间断点: 连续性失败的点
problem_bank:
  difficulty_labels:
    - 基础掌握
    - 考试常规
    - 拔高区分
  type_labels:
    - 计算
    - 证明
    - 选择
    - 填空
    - 综合
review:
  open_items:
    - id: review-001
      location: sources/ch01-slides.pdf p.12
      issue: 分段函数题中参数符号疑似 OCR 错误
      status: open
```

更新规则：

- 每次增量更新后追加或更新 `progress.processed_units`。
- 新增术语、符号、图形风格和题库标签时写入 `conventions` 或 `terms`。
- 待核对事项写入 `review.open_items`，并在解决后把 `status` 改为 `resolved`。
- 只改与本次目标相关的状态，避免重写无关章节。

## Incremental Update Procedure

1. 读取 `course.yml` 和 `state.yml`。
2. 浏览目标 `tex/` 文件，确认现有标题层级、环境用法、编号和符号。
3. 处理新增材料，生成或更新对应章节、习题、答案、题库条目和核对清单。
4. 更新 `state.yml` 的进度、术语、符号、题库统计和待核对事项。
5. 编译或做 LaTeX 结构检查，最终报告改动文件和验证结果。
