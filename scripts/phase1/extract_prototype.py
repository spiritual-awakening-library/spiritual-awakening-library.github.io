#!/usr/bin/env python3
"""Phase 1 — prototype entry text extraction from authoritative source PDFs.

Reconstructs vertical-typesetting reading order from PyMuPDF rawdict:
- Split each text line into ordering units:
  * blocks whose entire text is Latin/ASCII (5D, 3D, dimension,
    "Original Source", "Large Hadron Collider", 12, 2015 ...) become ONE
    unit (upright-stacked digits and rotated words must not be interleaved
    with CJK characters),
  * all other blocks contribute one unit per line (vertical CJK blocks
    store one character per line).
- Cluster units into columns by x-center (columns read right-to-left),
- Order units within a column by y-center,
- Paragraph break = column whose top unit starts indented
  (book-1: y0 >= 119 vs 99.7 continuation; book-2: y0 >= 100 vs 86.2)
  and whose first character is not head-forbidden punctuation
  (避頭點 columns pushed one slot down must not be mistaken for indents),
- Exclude running heads / page numbers (book-1 top band y1 < 60,
  book-2 bottom band y0 > 462) and the entry-title column on the
  opening page (titles come from the verified Phase 0.2 inventory).

Output: content/<book>/zh-TW/<entry>.json with stable paragraph IDs.
"""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path

import fitz

WORK = Path(__file__).resolve().parent
B1_PDF = "/home/z/sal-work/book1-print.pdf"
B2_PDF = "/home/z/sal-work/book2-content.pdf"

HEAD_FORBIDDEN = set("，。、；：？！︶︾）」』…— ")
LATIN_OK = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .:%&'/-–—")


def is_latin(text: str) -> bool:
    return bool(text) and all(c in LATIN_OK for c in text)


def page_units(page: "fitz.Page"):
    """Yield units (text, xc, yc, y0) for a page.

    Latin-only blocks collapse to a single unit; other blocks yield
    one unit per line. `skip` filtering happens at block level upstream.
    """
    d = page.get_text("rawdict")
    for block in d["blocks"]:
        if block.get("type") != 0:
            continue
        lines = []
        for line in block.get("lines", []):
            chars = [c for span in line.get("spans", []) for c in span.get("chars", [])]
            if not chars:
                continue
            lines.append((line, chars))
        if not lines:
            continue
        block_text = "".join(
            c["c"] for _, chars in lines for c in chars
        )
        if is_latin(block_text):
            x0 = min(c["bbox"][0] for _, chars in lines for c in chars)
            x1 = max(c["bbox"][2] for _, chars in lines for c in chars)
            y0 = min(c["bbox"][1] for _, chars in lines for c in chars)
            y1 = max(c["bbox"][3] for _, chars in lines for c in chars)
            yield (block_text, (x0 + x1) / 2, (y0 + y1) / 2, y0)
        else:
            for _, chars in lines:
                x0 = min(c["bbox"][0] for c in chars)
                x1 = max(c["bbox"][2] for c in chars)
                y0 = min(c["bbox"][1] for c in chars)
                y1 = max(c["bbox"][3] for c in chars)
                yield ("".join(c["c"] for c in chars), (x0 + x1) / 2, (y0 + y1) / 2, y0)


def block_texts(page: "fitz.Page"):
    """Full text of every block, for title exclusion."""
    d = page.get_text("rawdict")
    for block in d["blocks"]:
        if block.get("type") != 0:
            continue
        txt = ""
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                txt += "".join(c["c"] for c in span.get("chars", [])
                               if c["c"].strip() != "" or True)
        if txt:
            yield txt


def cluster_columns(units, x_threshold):
    """Cluster units into columns by x-center; ordered right-to-left."""
    items = sorted(units, key=lambda u: -u[1])
    cols, cur, cur_xc = [], [items[0]], items[0][1]
    for u in items[1:]:
        if cur_xc - u[1] <= x_threshold:
            cur.append(u)
            cur_xc = (cur_xc * (len(cur) - 1) + u[1]) / len(cur)
        else:
            cols.append((cur_xc, cur))
            cur = [u]
            cur_xc = u[1]
    cols.append((cur_xc, cur))
    return cols


def assemble(columns, para_y_threshold):
    """Build paragraph strings from right-to-left column stream."""
    paragraphs, buf = [], ""
    for i, (_xc, col) in enumerate(columns):
        ordered = sorted(col, key=lambda u: u[2])  # by y-center
        text = "".join(u[0] for u in ordered)
        top_y0 = min(u[3] for u in ordered)
        first = ordered[0][0][:1]
        starts_para = i > 0 and top_y0 >= para_y_threshold and (
            first not in HEAD_FORBIDDEN
        )
        if starts_para and buf:
            paragraphs.append(buf)
            buf = text
        else:
            buf += text
    if buf:
        paragraphs.append(buf)
    return [p.strip() for p in paragraphs if p.strip()]


def extract_book1(pdf_path, pages, skip_texts_on):
    """pages: [(pdf_page, 'R'|'L')]; skip_texts_on: {pdf_page: {block texts}}."""
    doc = fitz.open(pdf_path)
    all_columns = []
    for pno, half in pages:
        page = doc[pno - 1]
        mid = page.rect.width / 2
        skip = skip_texts_on.get(pno, set())
        units = []
        for btxt in block_texts(page):
            pass  # block_texts used separately below
        # rebuild units with block-level skip
        d = page.get_text("rawdict")
        for block in d["blocks"]:
            if block.get("type") != 0:
                continue
            blines = []
            for line in block.get("lines", []):
                chars = [c for span in line.get("spans", []) for c in span.get("chars", [])]
                if chars:
                    blines.append(chars)
            if not blines:
                continue
            block_text = "".join(c["c"] for chars in blines for c in chars)
            if block_text in skip:
                continue
            y1_all = max(c["bbox"][3] for chars in blines for c in chars)
            y0_all = min(c["bbox"][1] for chars in blines for c in chars)
            if y1_all < 60:  # top running head + page numbers (book 1)
                continue
            if is_latin(block_text):
                all_x0 = min(c["bbox"][0] for chars in blines for c in chars)
                all_x1 = max(c["bbox"][2] for chars in blines for c in chars)
                cx, cy = (all_x0 + all_x1) / 2, (y0_all + y1_all) / 2
                if half == "R" and cx < mid:
                    continue
                if half == "L" and cx > mid:
                    continue
                units.append((block_text, cx, cy, y0_all))
            else:
                for chars in blines:
                    x0 = min(c["bbox"][0] for c in chars)
                    x1 = max(c["bbox"][2] for c in chars)
                    y0 = min(c["bbox"][1] for c in chars)
                    y1 = max(c["bbox"][3] for c in chars)
                    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                    if half == "R" and cx < mid:
                        continue
                    if half == "L" and cx > mid:
                        continue
                    units.append(("".join(c["c"] for c in chars), cx, cy, y0))
        all_columns.extend(cluster_columns(units, 12.0))
    return all_columns


def extract_book2(pdf_path, pages, skip_texts_on):
    doc = fitz.open(pdf_path)
    all_columns = []
    for pno in pages:
        page = doc[pno - 1]
        skip = skip_texts_on.get(pno, set())
        units = []
        d = page.get_text("rawdict")
        for block in d["blocks"]:
            if block.get("type") != 0:
                continue
            blines = []
            for line in block.get("lines", []):
                chars = [c for span in line.get("spans", []) for c in span.get("chars", [])]
                if chars:
                    blines.append(chars)
            if not blines:
                continue
            block_text = "".join(c["c"] for chars in blines for c in chars)
            if block_text in skip:
                continue
            y0_all = min(c["bbox"][1] for chars in blines for c in chars)
            if y0_all > 462:  # bottom page number (Chinese numerals)
                continue
            if is_latin(block_text):
                all_x0 = min(c["bbox"][0] for chars in blines for c in chars)
                all_x1 = max(c["bbox"][2] for chars in blines for c in chars)
                y1_all = max(c["bbox"][3] for chars in blines for c in chars)
                units.append((block_text, (all_x0 + all_x1) / 2,
                              (y0_all + y1_all) / 2, y0_all))
            else:
                for chars in blines:
                    x0 = min(c["bbox"][0] for c in chars)
                    x1 = max(c["bbox"][2] for c in chars)
                    y0 = min(c["bbox"][1] for c in chars)
                    y1 = max(c["bbox"][3] for c in chars)
                    units.append(("".join(c["c"] for c in chars),
                                  (x0 + x1) / 2, (y0 + y1) / 2, y0))
        all_columns.extend(cluster_columns(units, 10.0))
    return all_columns


def write_entry(path: Path, meta, paragraphs):
    entry = {
        "schema": "sal-phase1-entry/1.0",
        **meta,
        "paragraphs": [{"id": f"p-{i+1:03d}", "text": t} for i, t in enumerate(paragraphs)],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)
    print(f"{meta['book_id']}/{meta['entry_id']}: {len(paragraphs)} paragraphs, "
          f"{sum(len(p) for p in paragraphs)} chars -> {path}")


def main():
    out = WORK / "content"

    # Book 1 — chapter-01 本源與宇宙次元 (printed 014-022; PDF 8R..12R)
    cols = extract_book1(
        B1_PDF,
        [(8, "R"), (8, "L"), (9, "R"), (9, "L"), (10, "R"), (10, "L"),
         (11, "R"), (11, "L"), (12, "R")],
        skip_texts_on={8: {"開悟之一", "本源與宇宙次元"}},
    )
    paras = assemble(cols, para_y_threshold=119.0)
    write_entry(
        out / "book-1/zh-TW/chapter-01.json",
        {
            "book_id": "book-1",
            "entry_id": "chapter-01",
            "title": "本源與宇宙次元",
            "series": "開悟之一",
            "language": "zh-TW",
            "printed_pages": "014-022",
            "pdf_pages": "8R-12R",
            "source_sha256": "a1f2f831e07f3505fb78fa9f7a5d90112a8ee23dc6eba8eaf04d6a1eaff2f901",
            "extraction_method": "char-coordinate column reconstruction (PyMuPDF rawdict)",
        },
        paras,
    )

    # Book 2 — preface-01 一份真實的路徑 (printed 25-31; PDF 25-31)
    cols2 = extract_book2(
        B2_PDF,
        list(range(25, 32)),
        skip_texts_on={25: {"︽一份真實的路徑︾︵慶淇悟得手札自序︶"}},
    )
    paras2 = assemble(cols2, para_y_threshold=100.0)
    write_entry(
        out / "book-2/zh-TW/preface-01.json",
        {
            "book_id": "book-2",
            "entry_id": "preface-01",
            "title": "一份真實的路徑",
            "series": "慶淇悟得手札自序",
            "language": "zh-TW",
            "printed_pages": "25-31",
            "pdf_pages": "25-31",
            "source_sha256": "653dfb125851a20e7740cea7e5bc3c34eb36b585a0141b96dd512023c9b1d985",
            "extraction_method": "char-coordinate column reconstruction (PyMuPDF rawdict)",
        },
        paras2,
    )


if __name__ == "__main__":
    main()
