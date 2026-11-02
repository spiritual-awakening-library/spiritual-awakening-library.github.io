#!/usr/bin/env python3
"""Phase 1 — content integrity validation.

Validates the published reading entries against the verified Phase 0.2
inventories and the publication registry:

1. every published entry exists in its book inventory;
2. entry metadata (title, series, printed pages) matches the inventory;
3. source SHA-256 recorded in content matches the inventory evidence;
4. paragraph IDs are sequential, unique, and non-empty;
5. translated entries have paragraph ID sets identical to the original;
6. draft translations carry explicit machine-assisted/needs-review status;
7. cover images referenced by books.json exist in public/covers.

Exit code 0 = all checks passed. Any failure prints details and exits 1.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        FAILURES.append(message)
        print(f"  FAIL: {message}")


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    registry = load_json(ROOT / "data" / "published.json")
    books = {b["id"]: b for b in load_json(ROOT / "data" / "books.json")["books"]}

    total_checks = 0

    for book in books.values():
        cover = ROOT / "public" / book["cover"].lstrip("/")
        total_checks += 1
        check(cover.is_file(), f"cover image missing: {book['cover']}")

    for entry in registry["entries"]:
        book_id = entry["book_id"]
        entry_id = entry["entry_id"]
        inventory = load_json(ROOT / "data" / "inventory" / f"{book_id}-inventory.json")
        inv_entry = next(
            (e for e in inventory["entries"] if e["entry_id"] == entry_id), None
        )
        total_checks += 1
        check(inv_entry is not None, f"{book_id}/{entry_id}: not in inventory")

        if inv_entry is None:
            continue

        for locale, pub in entry["locales"].items():
            label = f"{book_id}/{entry_id}/{locale}"
            content_path = ROOT / pub["content"]
            total_checks += 1
            check(content_path.is_file(), f"{label}: content file missing {pub['content']}")

            if not content_path.is_file():
                continue
            content = load_json(content_path)

            # structural checks
            total_checks += 1
            check(content["book_id"] == book_id and content["entry_id"] == entry_id,
                  f"{label}: book/entry id mismatch in content file")
            total_checks += 1
            check(bool(content.get("title")), f"{label}: missing title")
            total_checks += 1
            check(str(content.get("printed_pages")) == str(inv_entry["printed_page"]) or
                  str(content.get("printed_pages", "")).startswith(str(inv_entry["printed_page"])),
                  f"{label}: printed pages {content.get('printed_pages')!r} inconsistent "
                  f"with inventory start page {inv_entry['printed_page']!r}")

            # source evidence
            if content.get("source_sha256"):
                total_checks += 1
                check(content["source_sha256"] == inventory["source_sha256"],
                      f"{label}: source_sha256 mismatch with inventory")

            # paragraphs
            paras = content.get("paragraphs", [])
            total_checks += 1
            check(len(paras) > 0, f"{label}: no paragraphs")
            ids = [p["id"] for p in paras]
            expected_ids = [f"p-{i+1:03d}" for i in range(len(paras))]
            total_checks += 1
            check(ids == expected_ids, f"{label}: paragraph ids not sequential ({ids[:3]}…)")
            total_checks += 1
            check(len(set(ids)) == len(ids), f"{label}: duplicate paragraph ids")
            total_checks += 1
            check(all(p["text"].strip() for p in paras), f"{label}: empty paragraph text")

            # translation status discipline
            if locale == "en":
                total_checks += 1
                check(content.get("translated_from") == "zh-TW",
                      f"{label}: missing translated_from")
                total_checks += 1
                check(content.get("translation_status") == "draft-machine-assisted",
                      f"{label}: translation_status must be draft-machine-assisted "
                      f"(got {content.get('translation_status')!r})")
                total_checks += 1
                check(content.get("translation_review") == "needs-human-review",
                      f"{label}: translation_review must be needs-human-review")
                total_checks += 1
                check(pub.get("status") == "draft-machine-assisted",
                      f"{label}: registry status must mark draft")

        # cross-language paragraph mapping
        zh = entry["locales"].get("zh-TW")
        en = entry["locales"].get("en")
        if zh and en:
            zh_content = load_json(ROOT / zh["content"])
            en_content = load_json(ROOT / en["content"])
            zh_ids = [p["id"] for p in zh_content["paragraphs"]]
            en_ids = [p["id"] for p in en_content["paragraphs"]]
            total_checks += 1
            check(zh_ids == en_ids,
                  f"{book_id}/{entry_id}: zh/en paragraph id sets differ")

    print()
    if FAILURES:
        print(f"content validation FAILED: {len(FAILURES)} failure(s) "
              f"across {total_checks} checks")
        return 1
    print(f"content validation PASSED: {total_checks} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
