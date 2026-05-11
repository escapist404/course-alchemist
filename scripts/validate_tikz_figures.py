"""Validate Course Alchemist TikZ figure snippets.

Each ``figures/tikz/*.tex`` file gets a minimal standalone wrapper, an
independent compile/export attempt, and a compact QA report. Static checks
always run, so the script still produces useful output when TeX tools are not
available locally.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as etree
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
STYLE_DIR = REPO_ROOT / "assets" / "templates"
WRAPPER_TEMPLATE = STYLE_DIR / "tikz-standalone-wrapper.tex"

NODE_RE = re.compile(r"\\node(?:\[[^\]]*])?(?:\s+at\s*\([^)]*\))?\s*\{(?P<label>.*?)\}\s*;", re.DOTALL)
COLOR_RE = re.compile(r"\bCA[A-Za-z]+\b")
COMMAND_RE = re.compile(r"\\([A-Za-z@]+)")
CHINESE_SENTENCE_RE = re.compile(r"[\u4e00-\u9fff]{8,}|[，。；：]")
COMPLEX_FORMULA_RE = re.compile(r"\\(?:frac|sum|int|lim|sqrt|begin)\b|[=<>]")


@dataclass
class StaticIssue:
    severity: str
    message: str


@dataclass
class ToolState:
    xelatex: str | None
    dvisvgm: str | None
    qlmanage: str | None
    pdfcrop: str | None
    pdftocairo: str | None


@dataclass
class FigureResult:
    source: str
    status: str
    wrapper: str | None = None
    svg: str | None = None
    preview: str | None = None
    width: str | None = None
    height: str | None = None
    colors: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    static_errors: list[str] = field(default_factory=list)
    qa_items: list[str] = field(default_factory=list)
    semantic_errors: list[str] = field(default_factory=list)
    semantic_checks: list[str] = field(default_factory=list)
    compile_log: str | None = None
    dvisvgm_log: str | None = None


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def relpath(path: Path, root: Path = REPO_ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def discover_figure_files(inputs: Iterable[Path | str]) -> list[Path]:
    paths: list[Path] = []
    for item in inputs:
        path = Path(item)
        if path.is_file() and path.suffix == ".tex":
            paths.append(path)
            continue
        if not path.is_dir():
            continue

        candidates = [
            path / "figures" / "tikz",
            path / "tex" / "figures",
            path / "figures",
        ]
        if path.name in {"tikz", "figures"}:
            candidates.insert(0, path)

        for candidate in candidates:
            if candidate.is_dir():
                paths.extend(sorted(candidate.glob("*.tex")))

    return sorted(dict.fromkeys(p.resolve() for p in paths))


def default_output_dir(first: Path | None) -> Path:
    if first is None:
        return Path("build") / "tikz"
    parents = [first] + list(first.parents)
    for parent in parents:
        if (parent / "course.yml").exists() or (parent / "figures").is_dir():
            return parent / "build" / "tikz"
    return first.parent / "build" / "tikz"


def detect_tools() -> ToolState:
    return ToolState(
        xelatex=shutil.which("xelatex"),
        dvisvgm=shutil.which("dvisvgm"),
        qlmanage=shutil.which("qlmanage"),
        pdfcrop=shutil.which("pdfcrop"),
        pdftocairo=shutil.which("pdftocairo"),
    )


def find_default_ir(inputs: Iterable[Path | str]) -> Path | None:
    for item in inputs:
        path = Path(item)
        candidates: list[Path] = []
        if path.is_dir():
            candidates.extend([
                path / "source" / "figure-ir.json",
                path / "sources" / "figure-ir.json",
                path / "figures" / "figure-ir.json",
            ])
        elif path.is_file():
            candidates.extend([
                path.parent.parent / "source" / "figure-ir.json",
                path.parent.parent / "sources" / "figure-ir.json",
                path.parent / "figure-ir.json",
            ])
        for candidate in candidates:
            if candidate.exists():
                return candidate
    return None


def load_ir(ir_path: Path | None) -> dict[str, dict]:
    if ir_path is None:
        return {}
    data = json.loads(ir_path.read_text(encoding="utf-8"))
    figures = data.get("figures", [])
    if not isinstance(figures, list):
        raise ValueError("IR file must contain a list at key 'figures'")
    index: dict[str, dict] = {}
    for item in figures:
        figure_id = item.get("id")
        if not figure_id:
            raise ValueError("Each IR figure must contain an 'id'")
        index[str(figure_id)] = item
    return index


def regex_matches(content: str, pattern: str) -> bool:
    return re.search(pattern, content, flags=re.DOTALL) is not None


def semantic_analyze(content: str, figure_id: str, ir_index: dict[str, dict]) -> tuple[list[str], list[str]]:
    if not ir_index:
        return [], []

    item = ir_index.get(figure_id)
    if item is None:
        return [f"missing IR entry for figure id: {figure_id}"], []

    errors: list[str] = []
    checks: list[str] = []

    purpose = str(item.get("purpose", "")).strip()
    if purpose:
        checks.append(f"IR purpose: {purpose}")
    else:
        errors.append("IR purpose is empty")

    entities = item.get("entities", [])
    if isinstance(entities, list) and entities:
        checks.append("IR entities: " + ", ".join(str(entity) for entity in entities))
    else:
        errors.append("IR entities are missing")

    required = item.get("required_semantics", [])
    if not isinstance(required, list) or not required:
        errors.append("IR required_semantics are missing")
    else:
        for check in required:
            check_id = str(check.get("id", "unnamed"))
            statement = str(check.get("statement", check_id))
            evidence_all = [str(pattern) for pattern in check.get("evidence_all", [])]
            evidence_any = [str(pattern) for pattern in check.get("evidence_any", [])]
            all_ok = all(regex_matches(content, pattern) for pattern in evidence_all)
            any_ok = True if not evidence_any else any(regex_matches(content, pattern) for pattern in evidence_any)
            if all_ok and any_ok:
                checks.append(f"required pass [{check_id}]: {statement}")
            else:
                errors.append(f"required evidence missing [{check_id}]: {statement}")

    forbidden = item.get("forbidden_semantics", [])
    if isinstance(forbidden, list):
        for check in forbidden:
            check_id = str(check.get("id", "unnamed"))
            statement = str(check.get("statement", check_id))
            evidence_any = [str(pattern) for pattern in check.get("evidence_any", [])]
            found = any(regex_matches(content, pattern) for pattern in evidence_any)
            if found:
                errors.append(f"forbidden evidence found [{check_id}]: {statement}")
            else:
                checks.append(f"forbidden absent [{check_id}]: {statement}")

    return errors, checks


def build_wrapper_content(figure_path: Path, template_path: Path = WRAPPER_TEMPLATE) -> str:
    template = template_path.read_text(encoding="utf-8")
    figure_input = f"\\input{{{figure_path.resolve().as_posix()}}}"
    content = figure_path.read_text(encoding="utf-8")
    if "\\begin{axis}" in content and "\\begin{tikzpicture}" not in content:
        figure_input = "\\begin{tikzpicture}\n" + figure_input + "\n\\end{tikzpicture}"
    return template.replace("__FIGURE_BODY__", figure_input)


def extract_node_labels(content: str) -> list[str]:
    return [" ".join(match.group("label").split()) for match in NODE_RE.finditer(content)]


def static_analyze(content: str) -> tuple[list[StaticIssue], list[str], list[str]]:
    issues: list[StaticIssue] = []
    if "\\begin{tikzpicture}" not in content and "\\begin{axis}" not in content:
        issues.append(StaticIssue("error", "missing tikzpicture or axis environment"))
    if "\\begin{figure}" in content or "\\caption" in content:
        issues.append(StaticIssue("error", "figure snippets must not include figure/caption wrappers"))
    if "\\begin{axis}" in content and "\\begin{tikzpicture}" not in content:
        issues.append(StaticIssue("info", "PGFPlots axis snippet relies on the standalone wrapper tikzpicture context"))
    if "\\begin{axis}" in content and "clip=false" not in content:
        issues.append(StaticIssue("qa", "PGFPlots figure should be checked for label clipping; consider clip=false when labels extend outside axes"))
    if "\\begin{tikzpicture}" in content and ">=Latex" not in content:
        issues.append(StaticIssue("qa", "tikzpicture options do not set >=Latex; confirm arrowhead style is intentional"))

    for label in extract_node_labels(content):
        cleaned = re.sub(r"\$.*?\$", "", label)
        if CHINESE_SENTENCE_RE.search(cleaned):
            issues.append(StaticIssue("qa", f"long or explanatory node label: {label}"))
        if COMPLEX_FORMULA_RE.search(label):
            issues.append(StaticIssue("qa", f"complex formula in node label should move to caption/body: {label}"))

    colors = sorted(set(COLOR_RE.findall(content)))
    if len(colors) > 3:
        issues.append(StaticIssue("qa", f"uses {len(colors)} CA colors; check palette restraint"))

    if content.count("\\begin{scope}") != content.count("\\end{scope}"):
        issues.append(StaticIssue("error", "scope environment is not closed"))

    known_private = {
        "CADef",
        "CAInk",
        "CALem",
        "CAThm",
        "CAExam",
        "CAHint",
        "CANote",
        "CAMethod",
        "CAExample",
        "CAPitfall",
    }
    commands = sorted(set(COMMAND_RE.findall(content)))
    likely_private = [
        command
        for command in commands
        if command.startswith("CA") and command not in known_private
    ]
    for command in likely_private:
        issues.append(StaticIssue("qa", f"possible document-local command or color dependency: \\{command}"))

    if "right=of" in content or "left=of" in content or "above=of" in content or "below=of" in content:
        issues.append(StaticIssue("info", "uses positioning-style node placement; standalone wrapper loads positioning"))
    if "$(" in content:
        issues.append(StaticIssue("info", "uses calc coordinates; standalone wrapper loads calc"))
    if "pattern=" in content:
        issues.append(StaticIssue("info", "uses patterns; standalone wrapper loads patterns"))
    if "name intersections" in content:
        issues.append(StaticIssue("info", "uses intersections; standalone wrapper loads intersections"))

    return issues, colors, commands


def run_command(command: Sequence[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False, env=env)


def parse_svg_size(svg_path: Path) -> tuple[str | None, str | None]:
    if not svg_path.exists():
        return None, None
    try:
        root = etree.parse(svg_path).getroot()
    except etree.ParseError:
        return None, None
    return root.attrib.get("width"), root.attrib.get("height")


def validate_figure(
    figure: Path,
    output_dir: Path,
    tools: ToolState,
    preview: bool = True,
    ir_index: dict[str, dict] | None = None,
) -> FigureResult:
    wrapper_dir = output_dir / "wrappers"
    svg_dir = output_dir / "svg"
    preview_dir = output_dir / "previews"
    wrapper_dir.mkdir(parents=True, exist_ok=True)
    svg_dir.mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)

    content = figure.read_text(encoding="utf-8")
    static_issues, colors, commands = static_analyze(content)
    semantic_errors, semantic_checks = semantic_analyze(content, figure.stem, ir_index or {})
    wrapper_path = wrapper_dir / f"{figure.stem}.wrapper.tex"
    wrapper_path.write_text(build_wrapper_content(figure), encoding="utf-8")

    result = FigureResult(
        source=relpath(figure),
        status="passed",
        wrapper=relpath(wrapper_path),
        colors=colors,
        commands=commands,
        static_errors=[issue.message for issue in static_issues if issue.severity == "error"],
        qa_items=[issue.message for issue in static_issues if issue.severity != "error"],
        semantic_errors=semantic_errors,
        semantic_checks=semantic_checks,
    )

    if result.static_errors or result.semantic_errors:
        result.status = "failed"
        return result

    missing = [name for name in ("xelatex", "dvisvgm") if getattr(tools, name) is None]
    if missing:
        result.status = "static-only"
        result.qa_items.append("static-only validation because required tool(s) are unavailable: " + ", ".join(missing))
        return result

    env = os.environ.copy()
    texinputs = [STYLE_DIR.as_posix(), REPO_ROOT.as_posix(), ""]
    env["TEXINPUTS"] = os.pathsep.join(texinputs)

    xelatex_cmd = [
        tools.xelatex or "xelatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={wrapper_dir.as_posix()}",
        wrapper_path.as_posix(),
    ]
    compile_result = run_command(xelatex_cmd, env=env)
    result.compile_log = (compile_result.stdout + compile_result.stderr).strip()
    pdf_path = wrapper_dir / f"{figure.stem}.wrapper.pdf"
    if compile_result.returncode != 0 or not pdf_path.exists():
        result.status = "failed"
        result.static_errors.append("xelatex standalone compilation failed")
        return result

    export_pdf = pdf_path
    if tools.pdfcrop:
        cropped_pdf = wrapper_dir / f"{figure.stem}.wrapper-crop.pdf"
        crop_result = run_command([
            tools.pdfcrop,
            "--margins",
            "8 8 8 8",
            pdf_path.as_posix(),
            cropped_pdf.as_posix(),
        ], env=env)
        if crop_result.returncode == 0 and cropped_pdf.exists():
            export_pdf = cropped_pdf
        else:
            result.qa_items.append("pdfcrop failed; SVG export used the uncropped PDF page")

    svg_path = svg_dir / f"{figure.stem}.svg"
    dvisvgm_cmd = [
        tools.dvisvgm or "dvisvgm",
        "--pdf",
        "--no-fonts",
        "--exact",
        "--bbox=min",
        export_pdf.as_posix(),
        "-o",
        svg_path.as_posix(),
    ]
    dvisvgm_result = run_command(dvisvgm_cmd, env=env)
    result.dvisvgm_log = (dvisvgm_result.stdout + dvisvgm_result.stderr).strip()

    if dvisvgm_result.returncode != 0 or not svg_path.exists():
        if tools.pdftocairo:
            fallback = run_command([tools.pdftocairo, "-svg", export_pdf.as_posix(), svg_path.as_posix()], env=env)
            result.dvisvgm_log = (result.dvisvgm_log or "") + "\n" + (fallback.stdout + fallback.stderr).strip()
            if fallback.returncode == 0 and svg_path.exists():
                result.qa_items.append("dvisvgm PDF export failed; used pdftocairo SVG fallback")
            else:
                result.status = "failed"
                result.static_errors.append("SVG export failed")
                return result
        else:
            result.status = "failed"
            result.static_errors.append("SVG export failed")
            return result

    result.svg = relpath(svg_path)
    result.width, result.height = parse_svg_size(svg_path)

    if preview and tools.qlmanage:
        preview_result = run_command([
            tools.qlmanage,
            "-t",
            "-s",
            "1200",
            "-o",
            preview_dir.as_posix(),
            svg_path.as_posix(),
        ])
        preview_path = preview_dir / f"{svg_path.name}.png"
        if preview_result.returncode == 0 and preview_path.exists():
            result.preview = relpath(preview_path)
        else:
            result.qa_items.append("preview thumbnail skipped because qlmanage did not produce a PNG")
    elif preview:
        result.qa_items.append("preview thumbnail skipped because qlmanage is unavailable")

    return result


def write_manifest(output_dir: Path, results: Sequence[FigureResult], tools: ToolState, ir_path: Path | None = None) -> Path:
    manifest = {
        "created_at": iso_now(),
        "toolchain": asdict(tools),
        "ir": relpath(ir_path) if ir_path else None,
        "figure_count": len(results),
        "failed_count": sum(1 for result in results if result.status == "failed"),
        "static_only_count": sum(1 for result in results if result.status == "static-only"),
        "qa_item_count": sum(len(result.qa_items) for result in results),
        "semantic_error_count": sum(len(result.semantic_errors) for result in results),
        "semantic_check_count": sum(len(result.semantic_checks) for result in results),
        "figures": [asdict(result) for result in results],
    }
    path = output_dir / "manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def write_report(output_dir: Path, results: Sequence[FigureResult], tools: ToolState, ir_path: Path | None = None) -> Path:
    lines = [
        "# TikZ Figure Validation Report",
        "",
        f"- Created at: {iso_now()}",
        f"- Figures: {len(results)}",
        f"- Failed: {sum(1 for result in results if result.status == 'failed')}",
        f"- Static-only: {sum(1 for result in results if result.status == 'static-only')}",
        f"- QA items: {sum(len(result.qa_items) for result in results)}",
        f"- Semantic errors: {sum(len(result.semantic_errors) for result in results)}",
        f"- Semantic checks: {sum(len(result.semantic_checks) for result in results)}",
        f"- IR: `{relpath(ir_path)}`" if ir_path else "- IR: none",
        f"- Tools: xelatex={bool(tools.xelatex)}, dvisvgm={bool(tools.dvisvgm)}, pdfcrop={bool(tools.pdfcrop)}, pdftocairo={bool(tools.pdftocairo)}, qlmanage={bool(tools.qlmanage)}",
        "",
    ]
    for result in results:
        lines.extend([
            f"## {Path(result.source).stem}",
            "",
            f"- Source: `{result.source}`",
            f"- Status: `{result.status}`",
        ])
        if result.svg:
            lines.append(f"- SVG: `{result.svg}`")
        if result.preview:
            lines.append(f"- Preview: `{result.preview}`")
        if result.width or result.height:
            lines.append(f"- Size: `{result.width}` x `{result.height}`")
        if result.colors:
            lines.append("- Colors: " + ", ".join(f"`{color}`" for color in result.colors))
        if result.static_errors:
            lines.append("- Errors:")
            lines.extend(f"  - {message}" for message in result.static_errors)
        if result.semantic_errors:
            lines.append("- Semantic errors:")
            lines.extend(f"  - {message}" for message in result.semantic_errors)
        if result.semantic_checks:
            lines.append("- Semantic checks:")
            lines.extend(f"  - {message}" for message in result.semantic_checks)
        if result.qa_items:
            lines.append("- QA checklist:")
            lines.extend(f"  - {message}" for message in result.qa_items)
        lines.append("")

    path = output_dir / "report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate TikZ/PGFPlots figure snippets independently.")
    parser.add_argument("inputs", nargs="+", help="A course project, figures directory, or one or more .tex figure files.")
    parser.add_argument("--ir", help="Optional figure IR JSON. Defaults to source/figure-ir.json when a project directory is supplied.")
    parser.add_argument("--output", help="Output directory. Defaults to <project>/build/tikz.")
    parser.add_argument("--no-preview", action="store_true", help="Skip qlmanage thumbnail generation.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_paths = [Path(item) for item in args.inputs]
    figures = discover_figure_files(input_paths)
    output_dir = Path(args.output) if args.output else default_output_dir(figures[0] if figures else None)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not figures:
        (output_dir / "report.md").write_text("# TikZ Figure Validation Report\n\nNo figure files were found.\n", encoding="utf-8")
        print("validated figures: 0")
        print(f"report: {relpath(output_dir / 'report.md')}")
        return 0

    tools = detect_tools()
    ir_path = Path(args.ir) if args.ir else find_default_ir(input_paths)
    ir_index = load_ir(ir_path)
    results = [
        validate_figure(figure, output_dir, tools, preview=not args.no_preview, ir_index=ir_index)
        for figure in figures
    ]
    manifest = write_manifest(output_dir, results, tools, ir_path=ir_path)
    report = write_report(output_dir, results, tools, ir_path=ir_path)
    print(f"validated figures: {len(results)}")
    print(f"manifest: {relpath(manifest)}")
    print(f"report: {relpath(report)}")
    return 1 if any(result.status == "failed" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
