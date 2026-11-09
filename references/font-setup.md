# Font Setup Reference

读取本文件用于首次安装 Skill 或首次编译讲义时的字体检测与配置。字体设置只在第一次安装或第一次编译时执行，完成后不再重复检测、询问或下载，除非用户明确要求重新配置。

- 模型先判断当前操作系统。
- 根据操作系统选择合适的字体检测命令。
- 检测以下六个字体：
  - 思源宋体 / Noto Serif CJK SC
  - 思源黑体 / Noto Sans CJK SC
  - STIX Two Text
  - STIX Two Math
  - Libertinus Serif
  - Libertinus Math
- 如果所需字体已经存在，直接使用。
- 如果缺少字体，立即停止当前编译流程。
- 询问用户是否下载。
- 用户拒绝时停止，不自动替换、不自动下载。
- 用户同意时，调用 `assets/fonts/` 下的 Python 脚本。
- 模型根据检测结果和用户选择，修改模板中的字体配置。
- 模型修改字体配置时，只能修改 LaTeX 模板中明确标记为 `MODEL_EDIT_REQUIRED` 或“待模型修改”的字体配置注释块；不得修改模板中其他任何行。

正式课程主题使用思源宋体、思源黑体、STIX Two Text 和 STIX Two Math。经典教材主题使用思源宋体、思源黑体、Libertinus Serif 和 Libertinus Math。

