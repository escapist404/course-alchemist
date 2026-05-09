# Problem Bank Reference

读取本文件用于题库整理、抽题、组卷、生成分层练习或分析往年题风格。

## Storage

推荐每章或每专题一个 YAML 文件：

```text
problem_bank/
├── ch01-continuity.yml
└── exams-derived.yml
```

题目正文和解析使用 LaTeX 字符串。长题可以用 YAML block scalar。

## Problem Entry

```yaml
- id: calc-cont-001
  course: 高等数学
  unit: ch01-continuity
  topics:
    - 连续定义
    - 左右极限
  difficulty: 基础掌握
  type: 计算
  source:
    kind: generated
    ref: course-alchemist-example
  style_tags:
    - 分段函数
    - 参数确定
  statement_tex: |
    设
    \[
      f(x)=\begin{cases}
      ax+1, & x<1,\\
      x^2+b, & x\ge 1.
      \end{cases}
    \]
    若 $f$ 在 $x=1$ 处连续，求 $a,b$ 的关系。
  solution_tex: |
    连续要求左极限、右极限与函数值一致。由
    \[
      \lim_{x\to1^-}(ax+1)=a+1,\qquad f(1)=1+b
    \]
    得 $a+1=1+b$，即 $a=b$。
  answer: "$a=b$"
  estimated_time_minutes: 4
  score: 6
  related_notes:
    - tex/main.tex#连续性
```

## Required Labels

难度只使用：

- `基础掌握`：定义、公式、直接计算、标准模型。
- `考试常规`：综合 2 到 3 个知识点，接近期中/期末常规题。
- `拔高区分`：需要技巧、构造、证明、建模或跨章节联系。

题型优先使用：

- `计算`
- `证明`
- `选择`
- `填空`
- `综合`
- `建模`
- `概念`

## Generation Rules

- 先按考点覆盖选题，再调难度比例，最后调整题型和计算量。
- 若用户给了往年题，先总结题型比例、常考点、表述风格和计算量，再生成或改编。
- 生成题必须给完整解析；模拟卷还应给分值和预计用时。
- 题目来自扫描材料或往年题时，`source.kind` 使用 `user_source`，并记录页码或文件名。
- 模型原创题使用 `generated`；改编题使用 `adapted`，并说明参考风格。

## Mock Exam Defaults

用户没有指定时：

```yaml
exam_defaults:
  total_score: 100
  duration_minutes: 120
  difficulty_mix:
    基础掌握: 0.3
    考试常规: 0.5
    拔高区分: 0.2
  answer_policy: full_solutions
```

组卷完成后检查：

- 总分是否相加正确。
- 每题是否有题型、考点、难度、分值和解析。
- 难度比例是否接近目标。
- 是否覆盖用户指定考点，且没有明显重复题。
