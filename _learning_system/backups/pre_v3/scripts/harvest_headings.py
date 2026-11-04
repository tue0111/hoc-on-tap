# -*- coding: utf-8 -*-
"""Harvest outlines and first-page headings from extract files."""
from __future__ import annotations
import json
import re
from pathlib import Path

EXT = Path(r"D:\Hoc\_learning_system\extracts")
OUT = Path(r"D:\Hoc\_learning_system\inventory\headings.json")

HEADING_RE = re.compile(
    r"(?i)^\s*(chương\s*\d+|chuong\s*\d+|chủ đề|chude|mục lục|noi dung|nội dung|"
    r"mục tiêu|muc tieu|learning objective|nội dung môn|đề cương|"
    r"phần\s*\d+|bài\s*\d+|topic\s*\d+).{0,160}$"
)


def parse_extract(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    header, _, body = text.partition("## TEXT")
    meta = {}
    for line in header.splitlines():
        if ":" in line and not line.startswith("#") and not line.startswith("  -"):
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    outline = []
    in_outline = False
    for line in header.splitlines():
        if line.strip() == "outline:":
            in_outline = True
            continue
        if in_outline:
            if line.startswith("  - "):
                outline.append(line[4:].strip())
            elif line.strip() and not line.startswith(" "):
                in_outline = False
    body_headings = []
    for line in body.splitlines():
        s = line.strip()
        if not s:
            continue
        if HEADING_RE.match(s) or (len(s) <= 80 and s.isupper() and any(c.isalpha() for c in s)):
            body_headings.append(s)
        if len(body_headings) >= 40:
            break
    # first meaningful lines
    preview = []
    for line in body.splitlines():
        s = line.strip()
        if s and s != "----- PAGE 1 -----" and not s.startswith("----- PAGE"):
            preview.append(s)
        if len(preview) >= 25:
            break
    return {
        "extract_path": str(path.as_posix()),
        "source_id": meta.get("source_id") or path.name.split("__")[0],
        "relative_path": meta.get("relative_path"),
        "course_id": meta.get("course_id"),
        "source_role": meta.get("source_role"),
        "filename": meta.get("filename"),
        "page_count": meta.get("page_count"),
        "char_count": meta.get("char_count"),
        "likely_scanned": meta.get("likely_scanned"),
        "extract_ok": meta.get("extract_ok"),
        "outline": outline,
        "body_headings": body_headings[:30],
        "preview": preview,
    }


def main():
    items = []
    for p in sorted(EXT.rglob("*.extract.md")):
        items.append(parse_extract(p))
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    with_outline = sum(1 for x in items if x["outline"])
    print(f"harvested {len(items)} extracts; {with_outline} have PDF bookmarks")


if __name__ == "__main__":
    main()
