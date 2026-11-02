#!/usr/bin/env python3
"""Reconstruct Book 2 TOC (pages 1-22) and scan body title pages (23-478)."""
from __future__ import annotations

import json
import re
import sys

sys.path.insert(0, "/home/z/sal-work")
from b2_analyze import cn2int, cluster_columns  # noqa: E402

DOTS_RE = re.compile(r"[.]{2,}|…+")
NUM_RE = re.compile(r"^([一二三四五六七八九十百零]+)$")


def parse_toc_column(text: str):
    """Split a TOC column into (entry_text, number_int|None)."""
    # normalize
    t = text.strip()
    # find trailing number: optional dot leader then Chinese numerals at end
    m = re.search(r"[.]{2,}\s*([一二三四五六七八九十百零]+)\s*$", t)
    if m:
        title = t[:m.start()].strip()
        num = cn2int(m.group(1))
        return title, num, m.group(1)
    # no dots: trailing numeral run directly (short columns)
    m = re.search(r"([一二三四五六七八九十百零]+)\s*$", t)
    if m and m.start() > 0:
        title = t[:m.start()].rstrip(". ")
        # only treat as number if title ends with a closing bracket/punct
        if title and title[-1] in "︾︶﹂":
            return title, cn2int(m.group(1)), m.group(1)
    return t.rstrip(". "), None, None


def main(pages_json: str) -> None:
    d = json.load(open(pages_json, encoding="utf-8"))
    print("======== TOC RECONSTRUCTION (pages 1-22) ========")
    toc_rows = []
    for pno in range(1, 23):
        pg = d[str(pno)]
        chars = [c for c in pg.get("chars", []) if c["y0"] < 460]  # exclude footer
        cols = cluster_columns(chars, tol=14.0)
        for col in cols:
            title, num, numtxt = parse_toc_column(col["text"])
            toc_rows.append({"pdf_page": pno, "col_x": col["xc"],
                             "title": title, "num": num, "numtxt": numtxt})
            print(f"p{pno:>2} xc={col['xc']:>7}  {title!r:<50} -> {num} ({numtxt})")
    # monotonicity check
    print("\n======== MONOTONICITY ========")
    nums = [r["num"] for r in toc_rows if r["num"] is not None]
    bad = [(i, nums[i-1], nums[i]) for i in range(1, len(nums))
           if nums[i] < nums[i-1]]
    print("rows:", len(toc_rows), "with numbers:", len(nums), "violations:", bad)

    print("\n======== BODY TITLE PAGES (pages 23-478) ========")
    for pno in range(23, 479):
        pg = d.get(str(pno))
        if pg is None:
            continue
        chars = pg.get("chars", [])
        if not chars:
            continue
        big = [c for c in chars if (c["y1"] - c["y0"]) >= 19.0 and
               (ord(c["c"][0]) > 0x2E00 or c["c"].isalnum())]
        if big:
            cols = cluster_columns(big, tol=25.0)
            texts = ["".join(chars[i]["c"] for i in col["idx"]) for col in cols]
            # footer
            foot = [c for c in chars if c["y0"] > 460 and c["y1"] < 485]
            foot.sort(key=lambda c: c["x0"])
            ftxt = "".join(c["c"] for c in foot)
            print(f"p{pno:>3} footer={ftxt:<10} title={' | '.join(texts)!r}")


if __name__ == "__main__":
    main(sys.argv[1])
