#!/usr/bin/env python3
"""Book 1: TOC extraction (vertical columns, pages 5-7) + running-head scan."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict

sys.path.insert(0, "/home/z/sal-work")
from b2_analyze import cluster_columns  # noqa: E402

d = json.load(open(sys.argv[1], encoding="utf-8"))
MID = 839.055 / 2


def toc_page(pno):
    """Extract TOC text of one PDF page as vertical columns per half."""
    pg = d[str(pno)]
    out = []
    for name, cond in (("even", lambda c: (c["x0"] + c["x1"]) / 2 >= MID),
                       ("odd", lambda c: (c["x0"] + c["x1"]) / 2 < MID)):
        chs = [c for c in pg["chars"] if cond(c)]
        if not chs:
            continue
        cols = cluster_columns(chs, tol=12.0)
        for col in cols:
            txt = "".join(chs[i]["c"] for i in col["idx"])
            txt = re.sub(r"[.]{2,}", "…", txt)
            txt = txt.replace("ʊ", "·").replace("樬", "｜").replace("︐", "，")
            out.append((pno, name, col["xc"], txt))
    return out


print("======== BOOK 1 TOC (PDF pages 5-7, vertical columns R->L per half) ========")
for pno in (5, 6, 7):
    for p, half, xc, txt in toc_page(pno):
        print(f"p{p} {half} xc={xc:7.1f} : {txt!r}")

print("\n======== RUNNING-HEAD SEQUENCE (odd halves; label|title) ========")
seq = []
for pno in sorted(d, key=int):
    n = int(pno)
    pg = d[str(pno)]
    if not pg.get("chars"):
        continue
    chs = pg["chars"]
    odd = [c for c in chs if (c["x0"] + c["x1"]) / 2 < MID]
    if not odd:
        continue
    lab = [c for c in odd if 25 <= c["y0"] < 38]
    ttl = [c for c in odd if 38 <= c["y0"] < 60 and (c["x0"] + c["x1"]) / 2 >= 60]
    lab_s = "".join(c["c"] for c in sorted(lab, key=lambda c: c["x0"])).strip()
    ttl_s = "".join(c["c"] for c in sorted(ttl, key=lambda c: c["x0"])).strip()
    if lab_s or ttl_s:
        seq.append((2 * n - 1, lab_s, ttl_s))
# compress consecutive identical (label,title)
runs = []
for pgno, lab, ttl in seq:
    if runs and runs[-1][1] == lab and runs[-1][2] == ttl:
        runs[-1][0].append(pgno)
    else:
        runs.append([[pgno], lab, ttl])
for pages, lab, ttl in runs:
    print(f"odd {pages[0]:03d}-{pages[-1]:03d} ({len(pages)} pg): lab={lab!r} ttl={ttl!r}")
