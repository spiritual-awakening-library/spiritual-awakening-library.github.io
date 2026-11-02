#!/usr/bin/env python3
"""Book 1 structural analyzer.

Model (verified on PDF p2, p3, p4, p8, p9, p10):
- Each PDF page N is a 2-up landscape spread (839.055 x 595.276pt).
- RIGHT half = printed page 2N-2 (even; read first, RTL binding).
- LEFT  half = printed page 2N-1 (odd).
- Even-page header: book title running head + 3-digit page number at far right.
- Odd-page header: section label (y~36) + 3-digit page number at far left +
  section title (y~45).
- Chapter opening pages carry a vertical sidebar near the outer edge.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict

import fitz  # noqa: F401  (data already extracted via extract_pages.py)


def load(pages_json: str):
    return json.load(open(pages_json, encoding="utf-8"))


def split_halves(chars, mid):
    right = [c for c in chars if (c["x0"] + c["x1"]) / 2 >= mid]
    left = [c for c in chars if (c["x0"] + c["x1"]) / 2 < mid]
    return {"even": right, "odd": left}  # even = 2N-2 (right), odd = 2N-1 (left)


def yline(chars, y0, y1):
    return sorted([c for c in chars if y0 <= c["y0"] < y1], key=lambda c: c["x0"])


def num_at(chars, x_min, x_max):
    s = "".join(c["c"] for c in yline(chars, 25, 60)
                if x_min <= (c["x0"] + c["x1"]) / 2 <= x_max)
    m = re.fullmatch(r"(\d{3})", s.strip())
    return int(m.group(1)) if m else None


def analyze_half(chars, side):
    """side='even' (right half, number far right, book-title header) or
    'odd' (left half, number far left, label+title header)."""
    out = {"side": side, "n_chars": len(chars)}
    if not chars:
        return out
    if side == "even":
        out["page_number"] = num_at(chars, 770, 839)
        head = yline(chars, 25, 60)
        rest = [c for c in head if not (770 <= (c["x0"] + c["x1"]) / 2 <= 839)]
        out["header"] = "".join(c["c"] for c in rest).strip()
        # vertical sidebar near outer edge (x>730), below header (y>60)
        edge = [c for c in chars if (c["x0"] + c["x1"]) / 2 > 730 and c["y0"] > 60]
    else:
        out["page_number"] = num_at(chars, 0, 60)
        lab = yline(chars, 25, 38)
        ttl = yline(chars, 38, 60)
        out["label"] = "".join(c["c"] for c in lab).strip()
        ttl_no_num = [c for c in ttl if not (0 <= (c["x0"] + c["x1"]) / 2 <= 60)]
        out["header"] = "".join(c["c"] for c in ttl_no_num).strip()
        # vertical sidebar near outer edge (x<80), below header
        edge = [c for c in chars if (c["x0"] + c["x1"]) / 2 < 80 and c["y0"] > 60]
    if edge:
        # group by x (columns), vertical text
        cols = defaultdict(list)
        for c in edge:
            cols[round((c["x0"] + c["x1"]) / 2 / 18.0)].append(c)
        texts = []
        for k in sorted(cols, reverse=(side == "even")):
            grp = sorted(cols[k], key=lambda c: c["y0"])
            texts.append("".join(c["c"] for c in grp))
        out["sidebar"] = " | ".join(texts)
    return out


def main(pages_json: str, out_json: str):
    d = load(pages_json)
    res = {}
    bad = []
    for pno in sorted(d, key=int):
        n = int(pno)
        pg = d[pno]
        if pg.get("mode") == "empty" or not pg.get("chars"):
            res[pno] = {"page": n, "empty": True}
            continue
        mid = pg["width"] / 2
        halves = split_halves(pg["chars"], mid)
        even = analyze_half(halves["even"], "even")   # printed 2N-2
        odd = analyze_half(halves["odd"], "odd")       # printed 2N-1
        even["expected"] = 2 * n - 2
        odd["expected"] = 2 * n - 1
        for half in (even, odd):
            if half.get("page_number") is not None and \
                    half["page_number"] != half["expected"]:
                bad.append((n, half["side"], half["page_number"], half["expected"]))
        res[pno] = {"page": n, "even": even, "odd": odd}
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
    print("page-number mismatches:", bad if bad else "NONE")
    # text digest
    for pno in sorted(res, key=int):
        r = res[pno]
        if r.get("empty"):
            print(f"p{r['page']:>3} [EMPTY]")
            continue
        ev, od = r["even"], r["odd"]
        print(f"p{r['page']:>3} R({ev['expected']:03d}) num={ev.get('page_number')} "
              f"hdr={ev.get('header','')!r:<16} sb={ev.get('sidebar','')!r:<24} | "
              f"L({od['expected']:03d}) num={od.get('page_number')} "
              f"lab={od.get('label','')!r} ttl={od.get('header','')!r} sb={od.get('sidebar','')!r}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
