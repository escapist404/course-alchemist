#!/usr/bin/env python3
"""Build structured source assets from a scanned textbook PDF.

The pipeline is intentionally dependency-light. It uses optional local tools
when they are installed:

- PyMuPDF (fitz) for PDF rendering.
- Pillow for image preprocessing and thumbnails.
- pytesseract/Tesseract for local OCR.

When an optional dependency is missing, the script still writes a traceable
manifest, page records, review notes, and chapter placeholders so the course
workflow can continue with vision-model review or manual transcription.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


BLOCK_TYPES = {
    "heading",
    "paragraph",
    "formula",
    "figure",
    "table",
    "example",
    "exercise",
    "footer",
    "unknown",
}

AMBIGUOUS_TEXT_RE = re.compile(r"[Il10Ob6]")
FORMULA_HINT_RE = re.compile(r"(\\|[=+\-*/^_∑∫√≤≥≈∞]|[a-zA-Z]\s*\(|\b(?:sin|cos|tan|lim|log|ln)\b)")
EXERCISE_RE = re.compile(r"^\s*(?:习题|练习|题|例题|例|[0-9]+[.)、])")
HEADING_RE = re.compile(r"^\s*(?:第\s*[一二三四五六七八九十百0-9]+\s*[章节]|§|\d+(?:\.\d+){0,2}\s+)")


@dataclass
class BoundingBox:
    x0: float
    y0: float
    x1: float
    y1: float


@dataclass
class SourceBlock:
    type: str
    bbox: BoundingBox
    text_candidate: str = ""
    latex_candidate: str = ""
    confidence: float = 0.0
    needs_vision_review: bool = True
    source_ref: str = ""
    reading_order: int = 0
    notes: list[str] = field(default_factory=list)


@dataclass
class PageRecord:
    page_id: str
    source_file: str
    page_number: int
    image_path: str = ""
    thumbnail_path: str = ""
    enhanced_image_path: str = ""
    blocks: list[SourceBlock] = field(default_factory=list)
    uncertainties: list[str] = field(default_factory=list)


@dataclass
class Manifest:
    source_file: str
    source_sha256: str
    created_at: str
    output_dir: str
    dpi: int
    page_count: int
    processing_mode: str
    optional_components: dict[str, bool]
    chapter_ranges: list[dict[str, Any]] = field(default_factory=list)


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def optional_components() -> dict[str, bool]:
    return {
        "pymupdf": _can_import("fitz"),
        "pillow": _can_import("PIL.Image"),
        "pytesseract": _can_import("pytesseract") and shutil.which("tesseract") is not None,
    }


def _can_import(module: str) -> bool:
    try:
        __import__(module)
    except Exception:
        return False
    return True


def ensure_dirs(root: Path) -> dict[str, Path]:
    dirs = {
        "pages": root / "pages",
        "enhanced": root / "enhanced",
        "thumbs": root / "thumbs",
        "page_records": root / "page_records",
        "chapters": root / "chapters",
        "crops": root / "crops",
    }
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return dirs


def render_pdf(source: Path, dirs: dict[str, Path], dpi: int) -> tuple[int, list[Path]]:
    try:
        import fitz  # type: ignore
    except Exception:
        return 0, []

    rendered: list[Path] = []
    try:
        document = fitz.open(source)
        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        for index, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            image_path = dirs["pages"] / f"p{index:04d}.png"
            pixmap.save(image_path)
            rendered.append(image_path)
        return len(document), rendered
    except Exception:
        return 0, []


def preprocess_images(image_paths: Iterable[Path], dirs: dict[str, Path]) -> tuple[dict[int, Path], dict[int, Path]]:
    if not _can_import("PIL.Image"):
        return {}, {}

    from PIL import Image, ImageFilter, ImageOps

    enhanced: dict[int, Path] = {}
    thumbs: dict[int, Path] = {}
    for index, image_path in enumerate(image_paths, start=1):
        image = Image.open(image_path)
        gray = ImageOps.grayscale(image)
        normalized = ImageOps.autocontrast(gray).filter(ImageFilter.MedianFilter(size=3))

        enhanced_path = dirs["enhanced"] / f"p{index:04d}.png"
        normalized.save(enhanced_path)
        enhanced[index] = enhanced_path

        thumbnail = image.copy()
        thumbnail.thumbnail((360, 480))
        thumb_path = dirs["thumbs"] / f"p{index:04d}.jpg"
        thumbnail.convert("RGB").save(thumb_path, quality=86)
        thumbs[index] = thumb_path
    return enhanced, thumbs


def run_local_ocr(image_path: Path) -> tuple[str, float, str]:
    try:
        import pytesseract  # type: ignore
    except Exception:
        return "", 0.0, "pytesseract is not installed"

    if shutil.which("tesseract") is None:
        return "", 0.0, "tesseract executable is not available"

    try:
        data = pytesseract.image_to_data(
            str(image_path),
            lang="chi_sim+eng",
            output_type=pytesseract.Output.DICT,
            config="--psm 6",
        )
    except Exception as exc:  # pragma: no cover - depends on local OCR install
        return "", 0.0, f"local OCR failed: {exc}"

    tokens: list[str] = []
    confidences: list[float] = []
    for text, conf in zip(data.get("text", []), data.get("conf", [])):
        text = str(text).strip()
        if not text:
            continue
        tokens.append(text)
        try:
            value = float(conf)
        except ValueError:
            value = -1.0
        if value >= 0:
            confidences.append(value)

    confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.0
    return " ".join(tokens), round(confidence, 3), ""


def classify_block(text: str, confidence: float) -> tuple[str, str, bool, list[str]]:
    stripped = text.strip()
    notes: list[str] = []
    if not stripped:
        return "unknown", "", True, ["no OCR text candidate"]

    block_type = "paragraph"
    latex_candidate = ""
    if HEADING_RE.search(stripped):
        block_type = "heading"
    elif EXERCISE_RE.search(stripped):
        block_type = "example" if stripped.startswith(("例", "例题")) else "exercise"
    elif FORMULA_HINT_RE.search(stripped) and len(stripped) < 180:
        block_type = "formula"
        latex_candidate = stripped

    needs_review = confidence < 0.86 or block_type in {"formula", "figure", "table", "unknown"}
    if confidence < 0.86:
        notes.append(f"low OCR confidence: {confidence:.2f}")
    if AMBIGUOUS_TEXT_RE.search(stripped):
        notes.append("contains visually ambiguous characters")
        needs_review = True
    if block_type == "formula":
        notes.append("formula candidate requires visual/LaTeX review")
    return block_type, latex_candidate, needs_review, notes


def make_page_record(
    source: Path,
    output_root: Path,
    page_number: int,
    page_count: int,
    page_image: Path | None,
    enhanced_image: Path | None,
    thumbnail: Path | None,
) -> PageRecord:
    page_id = f"{source.stem}-p{page_number:04d}"
    source_ref = f"{source.name} p.{page_number}"

    ocr_image = enhanced_image or page_image
    text = ""
    confidence = 0.0
    ocr_note = "page image was not rendered"
    if ocr_image:
        text, confidence, ocr_note = run_local_ocr(ocr_image)

    block_type, latex_candidate, needs_review, notes = classify_block(text, confidence)
    if ocr_note:
        notes.append(ocr_note)

    block = SourceBlock(
        type=block_type,
        bbox=BoundingBox(0, 0, 1, 1),
        text_candidate=text,
        latex_candidate=latex_candidate,
        confidence=confidence,
        needs_vision_review=needs_review,
        source_ref=source_ref,
        reading_order=1,
        notes=notes,
    )

    uncertainties = []
    if needs_review:
        uncertainties.append(f"{source_ref}: visual QA required for {block_type} block")
    if page_number == page_count and page_count == 0:
        uncertainties.append(f"{source.name}: PDF renderer unavailable, page count could not be determined")

    return PageRecord(
        page_id=page_id,
        source_file=str(source),
        page_number=page_number,
        image_path=relpath(page_image, output_root),
        thumbnail_path=relpath(thumbnail, output_root),
        enhanced_image_path=relpath(enhanced_image, output_root),
        blocks=[block],
        uncertainties=uncertainties,
    )


def relpath(path: Path | None, root: Path) -> str:
    if path is None:
        return ""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_review_notes(output_root: Path, page_records: list[PageRecord]) -> None:
    review_dir = output_root / "review_notes"
    review_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Source Audit", ""]
    for page in page_records:
        for uncertainty in page.uncertainties:
            lines.append(f"- [ ] {uncertainty}")
        for block in page.blocks:
            for note in block.notes:
                lines.append(f"- [ ] {block.source_ref}: {note}")
    if len(lines) == 2:
        lines.append("- [x] No automatic source audit issues were detected.")
    (review_dir / "source-audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_chapter_assets(output_root: Path, source: Path, page_records: list[PageRecord]) -> None:
    chapter = {
        "chapter_id": f"{source.stem}-chapter-unknown",
        "title": "待识别章节",
        "source_file": str(source),
        "page_range": [
            min((page.page_number for page in page_records), default=0),
            max((page.page_number for page in page_records), default=0),
        ],
        "definitions": [],
        "theorems": [],
        "examples": [],
        "exercises": [],
        "formulas": [],
        "figures": [],
        "tables": [],
        "review_items": [],
    }

    for page in page_records:
        for block in page.blocks:
            item = {
                "source_ref": block.source_ref,
                "text_candidate": block.text_candidate,
                "latex_candidate": block.latex_candidate,
                "confidence": block.confidence,
                "needs_vision_review": block.needs_vision_review,
            }
            if block.type == "formula":
                chapter["formulas"].append(item)
            elif block.type == "example":
                chapter["examples"].append(item)
            elif block.type == "exercise":
                chapter["exercises"].append(item)
            elif block.type == "figure":
                chapter["figures"].append(item | {"review_policy": "visual_qa_required"})
            elif block.needs_vision_review:
                chapter["review_items"].append(item)

    write_json(output_root / "chapters" / f"{source.stem}.chapter.json", chapter)


def process(args: argparse.Namespace) -> int:
    source = Path(args.source).resolve()
    if not source.exists():
        print(f"source file does not exist: {source}", file=sys.stderr)
        return 2
    if source.suffix.lower() != ".pdf":
        print("initial implementation supports scanned PDF files only", file=sys.stderr)
        return 2

    output_root = Path(args.output).resolve() if args.output else source.parent / "processed" / source.stem
    output_root.mkdir(parents=True, exist_ok=True)
    dirs = ensure_dirs(output_root)

    components = optional_components()
    page_count, rendered_pages = render_pdf(source, dirs, args.dpi)
    enhanced, thumbs = preprocess_images(rendered_pages, dirs)

    if page_count == 0:
        page_count = args.expected_pages or 1

    page_records: list[PageRecord] = []
    for page_number in range(1, page_count + 1):
        page_image = rendered_pages[page_number - 1] if page_number <= len(rendered_pages) else None
        record = make_page_record(
            source=source,
            output_root=output_root,
            page_number=page_number,
            page_count=page_count,
            page_image=page_image,
            enhanced_image=enhanced.get(page_number),
            thumbnail=thumbs.get(page_number),
        )
        page_records.append(record)
        write_json(dirs["page_records"] / f"p{page_number:04d}.json", page_to_json(record))

    manifest = Manifest(
        source_file=str(source),
        source_sha256=sha256_file(source),
        created_at=iso_now(),
        output_dir=str(output_root),
        dpi=args.dpi,
        page_count=page_count,
        processing_mode="hybrid-local-first",
        optional_components=components,
        chapter_ranges=[
            {
                "chapter_id": f"{source.stem}-chapter-unknown",
                "title": "待识别章节",
                "page_start": 1,
                "page_end": page_count,
                "status": "needs_chapter_boundary_review",
            }
        ],
    )
    write_json(output_root / "manifest.json", asdict(manifest))
    write_review_notes(output_root, page_records)
    write_chapter_assets(output_root, source, page_records)

    print(f"processed source: {source}")
    print(f"output dir: {output_root}")
    print(f"pages: {page_count}")
    print("optional components: " + ", ".join(f"{key}={value}" for key, value in components.items()))
    return 0


def page_to_json(page: PageRecord) -> dict[str, Any]:
    data = asdict(page)
    for block in data["blocks"]:
        if block["type"] not in BLOCK_TYPES:
            block["type"] = "unknown"
    return data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Process a scanned textbook PDF into structured source assets.")
    parser.add_argument("source", help="Path to the scanned PDF source.")
    parser.add_argument("--output", help="Output directory. Defaults to <source-dir>/processed/<source-stem>.")
    parser.add_argument("--dpi", type=int, default=360, help="PDF render DPI. Default: 360.")
    parser.add_argument(
        "--expected-pages",
        type=int,
        default=0,
        help="Fallback page count when PyMuPDF is unavailable.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.dpi < 150 or args.dpi > 600:
        parser.error("--dpi must be between 150 and 600")
    if args.expected_pages < 0:
        parser.error("--expected-pages must be non-negative")
    return process(args)


if __name__ == "__main__":
    raise SystemExit(main())
