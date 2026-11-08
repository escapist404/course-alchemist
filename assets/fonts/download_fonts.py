"""Download fonts into this directory and copy them into its cache directory.

Run from the project root, for example:

    python assets/fonts/download_fonts.py --theme formal-course

Archives are downloaded beside this script, extracted temporarily beside this
script, copied into ``assets/fonts/cache/``, and then removed.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path


FONT_DIR = Path(__file__).parent
CACHE_DIR = FONT_DIR / "cache"


FONT_SOURCES = {
    "source-han-serif": {
        "repository": "adobe-fonts/source-han-serif",
        "archive": re.compile(r"(?i)source.?han.?serif.*\.(?:zip|tar\.gz|tgz|tar\.xz)$"),
        "font": re.compile(r"(?i)(?:source.?han.?serif|notoserifcjk).+\.(?:otf|ttf|ttc)$"),
    },
    "source-han-sans": {
        "repository": "adobe-fonts/source-han-sans",
        "archive": re.compile(r"(?i)source.?han.?sans.*\.(?:zip|tar\.gz|tgz|tar\.xz)$"),
        "font": re.compile(r"(?i)(?:source.?han.?sans|notosanscjk).+\.(?:otf|ttf|ttc)$"),
    },
    "stix-two-text": {
        "repository": "stipub/stixfonts",
        "archive": re.compile(r"(?i)stix.*\.(?:zip|tar\.gz|tgz|tar\.xz)$"),
        "font": re.compile(r"(?i)stixtwo.?text.+\.(?:otf|ttf|ttc)$"),
    },
    "stix-two-math": {
        "repository": "stipub/stixfonts",
        "archive": re.compile(r"(?i)stix.*\.(?:zip|tar\.gz|tgz|tar\.xz)$"),
        "font": re.compile(r"(?i)stixtwo.?math.+\.(?:otf|ttf|ttc)$"),
    },
    "libertinus-serif": {
        "repository": "alerque/libertinus",
        "archive": re.compile(r"(?i)libertinus.*\.(?:zip|tar\.gz|tgz|tar\.xz)$"),
        "font": re.compile(r"(?i)libertinus.?serif.+\.(?:otf|ttf|ttc)$"),
    },
    "libertinus-math": {
        "repository": "alerque/libertinus",
        "archive": re.compile(r"(?i)libertinus.*\.(?:zip|tar\.gz|tgz|tar\.xz)$"),
        "font": re.compile(r"(?i)libertinus.?math.+\.(?:otf|ttf|ttc)$"),
    },
}


THEMES = {
    "formal-course": (
        "source-han-serif",
        "source-han-sans",
        "stix-two-text",
        "stix-two-math",
    ),
    "classic-textbook": (
        "source-han-serif",
        "source-han-sans",
        "libertinus-serif",
        "libertinus-math",
    ),
    "all": tuple(FONT_SOURCES),
}


def latest_release(repository: str) -> dict:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/releases/latest",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "course-alchemist-font-downloader",
        },
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def select_archive(source: dict) -> tuple[str, str]:
    release = latest_release(source["repository"])
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        if source["archive"].search(name):
            return name, asset["browser_download_url"]
    raise RuntimeError(f"no trusted archive found for {source['repository']}")


def download(url: str, target: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "course-alchemist-font-downloader"},
    )
    with urllib.request.urlopen(request) as response, target.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)


def validate_member(name: str) -> None:
    member = Path(name)
    if member.is_absolute() or ".." in member.parts:
        raise RuntimeError(f"unsafe archive member: {name}")


def extract(archive: Path, destination: Path) -> None:
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as zipped:
            for member in zipped.infolist():
                validate_member(member.filename)
            zipped.extractall(destination)
        return

    if tarfile.is_tarfile(archive):
        with tarfile.open(archive) as tar:
            for member in tar.getmembers():
                validate_member(member.name)
            tar.extractall(destination)
        return

    raise RuntimeError(f"unsupported archive format: {archive.name}")


def copy_fonts(source: dict, extracted: Path) -> list[Path]:
    files = sorted(
        path
        for path in extracted.rglob("*")
        if path.is_file() and source["font"].search(path.name)
    )
    if not files:
        raise RuntimeError(f"no matching font files found for {source['repository']}")

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    installed = []
    for file_path in files:
        target = CACHE_DIR / file_path.name
        shutil.copy2(file_path, target)
        installed.append(target)
    return installed


def download_font(font_id: str) -> None:
    source = FONT_SOURCES[font_id]
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    archive_name, archive_url = select_archive(source)
    archive = FONT_DIR / archive_name

    print(f"downloading {font_id}: {archive_name}")
    try:
        download(archive_url, archive)
        with tempfile.TemporaryDirectory(dir=FONT_DIR, prefix=".font-extract-") as temporary:
            extracted = Path(temporary)
            extract(archive, extracted)
            for installed in copy_fonts(source, extracted):
                print(f"installed {installed}")
    finally:
        archive.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--theme", choices=tuple(THEMES), default="formal-course")
    group.add_argument("--font", dest="fonts", action="append", choices=tuple(FONT_SOURCES))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected = args.fonts or THEMES[args.theme]
    try:
        for font_id in selected:
            download_font(font_id)
    except Exception as error:  # noqa: BLE001
        print(f"font download failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
