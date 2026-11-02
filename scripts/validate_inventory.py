#!/usr/bin/env python3
"""Phase 0.2: automated validation for the complete book inventories.

Validates data/inventory/book-{1,2}-inventory.{csv,json} against the Phase 0.2
inventory contract. Dependency-free; Python 3.12+; Windows and Linux.

Check classes (per Phase 0.2 requirements):
  1. unique entry IDs                     6. page-number format
  2. required fields                      7. missing information
  3. valid book references                8. verification-status consistency
  4. consistent order                     9. duplicate / overlapping entries
  5. allowed entry types                     requiring review
Extra: page-coverage completeness of the derived page maps.

This script validates structural integrity and internal consistency only.
It does NOT claim transcription completeness, translation correctness, or
legal clearance.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
INV_DIR = ROOT / "data" / "inventory"

ALLOWED_KINDS = {
    "cover", "toc", "preface", "foreword", "chapter", "essay", "testimonial",
    "title-page", "acknowledgment", "analysis", "blessing", "interview",
    "testimony-story", "rights-statement", "photo-plate", "quote-plate",
    "diagram-plate", "colophon",
}
ALLOWED_TOC_STATUS = {"toc-verified", "not-in-toc", "toc-needs-review"}
ALLOWED_BODY_STATUS = {
    "body-verified", "body-verified-heading", "body-verified-running-head",
    "body-verified-opening", "image-only-vlm-transcribed", "needs-review",
}
ALLOWED_TRANSLATION = {"not-started", "in-progress", "needs-review", "approved"}
ALLOWED_LANGUAGE = {"zh-TW", "en"}
EXPECTED_PDF_PAGES = {"book-1": 325, "book-2": 478}
PRINTED_MAX = {"book-1": 649, "book-2": 478}
CN_NUMERALS = "一二三四五六七八九十百千零"
REQUIRED = ["book_id", "entry_id", "entry_kind", "order_in_book",
            "original_title", "pdf_page", "source_file", "language",
            "toc_status", "body_status", "translation_status", "review_notes"]
ERRORS: list[str] = []
WARNINGS: list[str] = []
CHECKS: list[tuple[str, str]] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


def check(code: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((code, "PASS" if ok else "FAIL"))
    if not ok:
        err(f"{code}: {detail}")


def load_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, strict=True)
        if reader.fieldnames is None:
            raise ValueError(f"{path.name}: no header")
        rows = list(reader)
    for i, row in enumerate(rows, start=2):
        if None in row:  # extra columns
            err(f"{path.name} row {i}: more fields than header columns")
    return rows, reader.fieldnames


def cn2int(s: str) -> int | None:
    vals = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7,
            "八": 8, "九": 9, "零": 0}
    if not s:
        return None
    total = section = num = 0
    for ch in s:
        if ch == "十":
            section += (num or 1) * 10
            num = 0
        elif ch == "百":
            section = (section + (num or 1)) * 100
            num = 0
        elif ch == "千":
            section = (section + num or 1) * 1000
            num = 0
        elif ch in vals:
            num = vals[ch]
        else:
            return None
    return section + num or None


def validate_book(book: str, rows: list[dict], fields: list[str]) -> None:
    tag = book
    # (1) unique IDs
    ids = [r.get("entry_id", "") for r in rows]
    dup = {i for i in ids if ids.count(i) > 1}
    check(f"{tag}-unique-ids", not dup, f"duplicates: {sorted(dup)}")
    # (2) required fields
    missing = []
    for i, r in enumerate(rows, 1):
        for col in REQUIRED:
            v = (r.get(col) or "").strip()
            if col in ("original_title",):
                continue  # allowed empty only for untitled plates (checked below)
            if not v:
                missing.append(f"row {i} (order {r.get('order_in_book')}): {col} empty")
    check(f"{tag}-required-fields", not missing, "; ".join(missing[:6]))
    # empty titles only for image-only plates with an untitled note
    for i, r in enumerate(rows, 1):
        if not (r.get("original_title") or "").strip():
            if r.get("body_status") == "image-only-vlm-transcribed" and \
                    "無標題" in (r.get("review_notes") or ""):
                continue
            err(f"{tag} row {i}: empty original_title without untitled-plate note")
    # (3) valid book refs
    bad_book = [r["entry_id"] for r in rows if r.get("book_id") != book]
    check(f"{tag}-book-refs", not bad_book, f"foreign book_id rows: {bad_book[:4]}")
    # (4) consistent order: strictly increasing, 1..N
    orders = []
    for r in rows:
        v = (r.get("order_in_book") or "").strip()
        orders.append(int(v) if v.isdecimal() else None)
    ok = all(o is not None for o in orders) and orders == list(range(1, len(rows) + 1))
    check(f"{tag}-order-consistent", ok,
          f"orders not 1..{len(rows)}: first problems "
          f"{[(i, o) for i, o in enumerate(orders) if o != i + 1][:5]}")
    # reproducible original order: printed/pdf monotonic within book
    seq = []
    for r in rows:
        ppn = r.get("printed_page_num") or ""
        pdfp = r.get("pdf_page") or ""
        seq.append((int(ppn) if ppn.isdecimal() else None,
                    int(pdfp) if pdfp.isdecimal() else None))
    nonmono = [i for i in range(1, len(seq))
               if seq[i][0] is not None and seq[i - 1][0] is not None
               and seq[i][0] <= seq[i - 1][0]
               and rows[i].get("entry_kind") not in ("plate",)]
    check(f"{tag}-order-reproducible", not nonmono,
          f"printed page order violations at rows {nonmono[:5]}")
    # (5) allowed entry types
    badk = sorted({r.get("entry_kind") for r in rows} - ALLOWED_KINDS)
    check(f"{tag}-entry-types", not badk, f"unknown kinds: {badk}")
    # (6) page-number format
    fmt_bad = []
    for i, r in enumerate(rows, 1):
        pp = (r.get("printed_page") or "").strip()
        ppn = (r.get("printed_page_num") or "").strip()
        pdfp = (r.get("pdf_page") or "").strip()
        pos = (r.get("pdf_page_position") or "").strip()
        if pp:
            if book == "book-1":
                if not re.fullmatch(r"(0\d{2}|\d{3})", pp):
                    fmt_bad.append(f"row {i}: printed_page {pp!r} not 3-digit")
            else:
                if not (pp.isdecimal() or all(c in CN_NUMERALS for c in pp)):
                    fmt_bad.append(f"row {i}: printed_page {pp!r} not numeric/Chinese numeral")
            if ppn:
                v = int(ppn)
                if not 0 <= v <= PRINTED_MAX[book]:
                    fmt_bad.append(f"row {i}: printed_page_num {v} out of range")
                # cross-check the numeral form vs the numeric form
                if book == "book-1":
                    if v >= 10 and pp != f"{v:03d}":
                        fmt_bad.append(f"row {i}: {pp!r} != {v:03d}")
                else:
                    if all(c in CN_NUMERALS for c in pp) and cn2int(pp) != v:
                        fmt_bad.append(f"row {i}: {pp!r} parses to {cn2int(pp)} != {v}")
            else:
                fmt_bad.append(f"row {i}: printed_page set but printed_page_num empty")
        elif r.get("entry_kind") not in ("cover",) and \
                r.get("body_status") != "image-only-vlm-transcribed":
            fmt_bad.append(f"row {i}: printed_page empty for {r.get('entry_kind')}")
        if pdfp:
            if not pdfp.isdecimal() or not 1 <= int(pdfp) <= EXPECTED_PDF_PAGES[book]:
                fmt_bad.append(f"row {i}: pdf_page {pdfp!r} invalid")
        else:
            fmt_bad.append(f"row {i}: pdf_page empty")
        if pos and pos not in ("R", "L"):
            fmt_bad.append(f"row {i}: pdf_page_position {pos!r} not R/L")
        # mapping consistency: printed page must match pdf geometry
        if ppn.isdecimal() and pdfp.isdecimal():
            v, p = int(ppn), int(pdfp)
            if book == "book-1":
                want = v // 2 + 1
                if p != want:
                    fmt_bad.append(f"row {i}: pdf_page {p} != sheet {want} for printed {v:03d}")
                exp_pos = "R" if v % 2 == 0 else "L"
                if pos and pos != exp_pos:
                    fmt_bad.append(f"row {i}: position {pos} != expected {exp_pos} for printed {v:03d}")
            else:
                if p != v:
                    fmt_bad.append(f"row {i}: pdf_page {p} != printed {pp} (must be 1:1)")
    check(f"{tag}-page-formats", not fmt_bad, "; ".join(fmt_bad[:6]))
    # (7) missing information
    info_bad = []
    for i, r in enumerate(rows, 1):
        if not (r.get("language") or ""):
            info_bad.append(f"row {i}: language missing")
        elif r["language"] not in ALLOWED_LANGUAGE:
            info_bad.append(f"row {i}: language {r['language']!r} invalid")
        if not (r.get("source_file") or "").strip():
            info_bad.append(f"row {i}: source_file missing")
        if not (r.get("review_notes") or "").strip():
            info_bad.append(f"row {i}: review_notes missing")
        if not (r.get("parent_series") or "").strip() and r.get("entry_kind") == "essay":
            info_bad.append(f"row {i}: essay without parent_series")
    check(f"{tag}-missing-info", not info_bad, "; ".join(info_bad[:6]))
    # (8) verification-status consistency
    stat_bad = []
    for i, r in enumerate(rows, 1):
        if r.get("toc_status") not in ALLOWED_TOC_STATUS:
            stat_bad.append(f"row {i}: toc_status {r.get('toc_status')!r}")
        if r.get("body_status") not in ALLOWED_BODY_STATUS:
            stat_bad.append(f"row {i}: body_status {r.get('body_status')!r}")
        if r.get("translation_status") not in ALLOWED_TRANSLATION:
            stat_bad.append(f"row {i}: translation_status {r.get('translation_status')!r}")
        if r.get("toc_status") == "toc-verified" and not (r.get("printed_page") or "").strip():
            stat_bad.append(f"row {i}: toc-verified but no printed page")
        if r.get("toc_status") == "not-in-toc" and "目錄" not in (r.get("review_notes") or ""):
            # notes must explain why it is not in the TOC (plates etc.)
            if r.get("entry_kind") not in ("cover", "colophon", "toc",
                                           "rights-statement", "photo-plate",
                                           "quote-plate", "diagram-plate"):
                stat_bad.append(f"row {i}: not-in-toc without explanatory note")
        if r.get("body_status", "").startswith("needs-review") and \
                "待" not in (r.get("review_notes") or ""):
            stat_bad.append(f"row {i}: needs-review without review note")
    check(f"{tag}-status-consistency", not stat_bad, "; ".join(stat_bad[:6]))
    # (9) duplicate / overlapping entries requiring review
    overlap = []
    keyed = {}
    for i, r in enumerate(rows, 1):
        ppn = (r.get("printed_page_num") or "").strip()
        if not ppn:
            continue
        v = int(ppn)
        keyed.setdefault(v, []).append(r["entry_id"])
    for v, ids in sorted(keyed.items()):
        if len(ids) > 1:
            overlap.append(f"printed {v} shared by {ids}")
    check(f"{tag}-no-overlaps", not overlap, "; ".join(overlap[:6]))
    # duplicate title+qualifier pairs (distinct parts share base titles by design)
    seen_tq = {}
    for r in rows:
        if r.get("entry_kind") != "essay":
            continue
        k = (r.get("original_title"), r.get("title_qualifier"))
        if k in seen_tq:
            warn(f"{tag}: duplicate essay title+qualifier {k} "
                 f"({seen_tq[k]} / {r['entry_id']})")
        seen_tq[k] = r["entry_id"]
    # CSV/JSON equivalence
    return rows


def validate_json_matches_csv(book: str, csv_rows: list[dict]) -> None:
    payload = json.loads((INV_DIR / f"{book}-inventory.json").read_text(encoding="utf-8"))
    entries = payload.get("entries", [])
    check(f"{book}-json-count", len(entries) == len(csv_rows),
          f"json {len(entries)} vs csv {len(csv_rows)}")
    mismatch = []
    for c, j in zip(csv_rows, entries):
        for k in ("entry_id", "order_in_book", "original_title", "printed_page_num"):
            if (c.get(k) or "") != str(j.get(k) if j.get(k) is not None else ""):
                mismatch.append(f"{c.get('entry_id')}: {k}")
                break
    check(f"{book}-json-csv-match", not mismatch, "; ".join(mismatch[:5]))
    for key in ("schema", "source_pdf", "source_sha256"):
        if not payload.get(key):
            err(f"{book}-inventory.json missing {key}")


def validate_page_map(book: str) -> None:
    path = INV_DIR / f"{book}-page-map.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    owners = data.get("page_owner", {})
    lo, hi = data.get("printed_page_range", [None, None])
    missing = [p for p in range(lo, hi + 1) if str(p) not in owners]
    check(f"{book}-page-coverage", not missing,
          f"unassigned printed pages: {missing[:8]}"
          f"{'...' if len(missing) > 8 else ''}")


def validate_source_records() -> None:
    # source PDFs must NOT be committed
    inv_dir = PurePosixPath("data/inventory")
    committed = subprocess_ls_files()
    for name in ("印刷全文-要開悟讀這本書就夠了", "內文-靈性覺醒",
                 "封面-要開悟讀這本書就夠了", "封面-靈性覺醒"):
        for rel in committed:
            if name in rel:
                err(f"source PDF appears tracked: {rel}")
    check("sources-not-committed", not any(
        name in rel for rel in committed for name in
        ("印刷全文", "內文-靈性覺", "封面-")), "source PDF tracked")
    # inventory references the source files consistently
    for book in ("book-1", "book-2"):
        rows, _ = load_csv(INV_DIR / f"{book}-inventory.csv")
        srcs = {r["source_file"] for r in rows}
        check(f"{book}-single-source", len(srcs) == 1, f"multiple sources: {srcs}")


def subprocess_ls_files() -> list[str]:
    import subprocess
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, check=True,
                             capture_output=True).stdout
        return [x.decode("utf-8") for x in out.split(b"\n") if x]
    except Exception:
        return []


def main() -> int:
    for book in ("book-1", "book-2"):
        path = INV_DIR / f"{book}-inventory.csv"
        if not path.is_file():
            print(f"FAIL: missing {PurePosixPath(path.relative_to(ROOT)).as_posix()}")
            return 1
        rows, fields = load_csv(path)
        need = {"book_id", "entry_id", "entry_kind", "order_in_book",
                "original_title", "title_qualifier", "parent_series",
                "attributed_author", "printed_page", "printed_page_num",
                "pdf_page", "pdf_page_position", "source_file", "language",
                "toc_status", "body_status", "translation_status", "review_notes"}
        check(f"{book}-schema", set(fields or []) >= need,
              f"missing columns: {sorted(need - set(fields or []))}")
        validate_book(book, rows, fields)
        validate_json_matches_csv(book, rows)
        validate_page_map(book)
    validate_source_records()

    for code, status in CHECKS:
        print(f"{status}: {code}")
    for w in WARNINGS:
        print(f"WARN: {w}")
    print(f"\nchecks: {len(CHECKS)}; pass: {sum(1 for _, s in CHECKS if s == 'PASS')}; "
          f"fail: {len(ERRORS)}; warnings: {len(WARNINGS)}")
    if ERRORS:
        print("FAIL: inventory validation failed")
        for e in ERRORS:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("PASS: complete book inventories are structurally valid.")
    print("LIMITATION: structural validation only; not transcription review, "
          "translation review, or rights clearance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
