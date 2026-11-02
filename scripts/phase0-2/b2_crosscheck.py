#!/usr/bin/env python3
"""Cross-check Book 2: TOC entry numbers vs body title pages."""
from __future__ import annotations

import json
import sys

sys.path.insert(0, "/home/z/sal-work")
from b2_analyze import cluster_columns  # noqa: E402


def toc_numbers(pages_json):
    d = json.load(open(pages_json, encoding="utf-8"))
    import re
    rows = []
    for pno in range(1, 23):
        pg = d[str(pno)]
        chars = [c for c in pg.get("chars", []) if c["y0"] < 460]
        cols = cluster_columns(chars, tol=14.0)
        for col in cols:
            t = col["text"].strip()
            m = re.search(r"[.]{2,}\s*([一二三四五六七八九十百零]+)\s*$", t)
            if not m:
                m = re.search(r"([一二三四五六七八九十百零]+)\s*$", t)
                if m and not (t[:m.start()].rstrip(". ") or "").endswith(("︾", "︶", "﹂")):
                    m = None
            if m:
                from b2_analyze import cn2int
                rows.append((pno, col["xc"], t[:m.start()].rstrip(". "), cn2int(m.group(1))))
    return rows


def body_title_pages(pages_json):
    d = json.load(open(pages_json, encoding="utf-8"))
    out = {}
    for pno in range(23, 479):
        pg = d.get(str(pno))
        if pg is None:
            continue
        chars = pg.get("chars", [])
        big = [c for c in chars if (c["y1"] - c["y0"]) >= 19.0 and
               (ord(c["c"][0]) > 0x2E00 or c["c"].isalnum())]
        if big:
            cols = cluster_columns(big, tol=25.0)
            out[pno] = ["".join(chars[i]["c"] for i in col["idx"]) for col in cols]
    return out


def main(pages_json: str) -> None:
    rows = toc_numbers(pages_json)
    body = body_title_pages(pages_json)
    toc_pages = sorted({r[3] for r in rows if r[3]})
    body_pages = sorted(body)
    print("TOC entry pages:", len(toc_pages))
    print("Body title pages:", len(body_pages))
    only_toc = [p for p in toc_pages if p not in body]
    only_body = [p for p in body_pages if p not in toc_pages]
    print("In TOC but no body title page:", only_toc)
    print("Body title page but not in TOC:", only_body)
    # footer consistency for body title pages
    d = json.load(open(pages_json, encoding="utf-8"))
    bad_footer = []
    for p in body_pages:
        pg = d[str(p)]
        foot = [c for c in pg.get("chars", []) if c["y0"] > 460 and c["y1"] < 485]
        foot.sort(key=lambda c: c["x0"])
        ft = "".join(c["c"] for c in foot).strip()
        from b2_analyze import cn2int
        v = cn2int(ft) if ft and all(ch in "一二三四五六七八九十百零" for ch in ft) else None
        if v != p:
            bad_footer.append((p, ft, v))
    print("Footer mismatches on title pages:", bad_footer)
    # page coverage: pages 23-478 without any text
    empties = [p for p in range(1, 479)
               if not d.get(str(p), {}).get("chars")]
    print("Pages with no text layer:", empties)
    # per-page accounting 23..478: has title? body? footer?
    print("\nSegment map (title pages with gaps > 2):")
    prev = 22
    for p in body_pages:
        if p - prev > 2:
            print(f"  gap: pages {prev+1}..{p-1} belong to previous entry")
        prev = p
    print("last title page:", body_pages[-1], "; PDF ends at 478")


if __name__ == "__main__":
    main(sys.argv[1])
