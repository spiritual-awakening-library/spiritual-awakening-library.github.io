#!/usr/bin/env python3
"""Coordinate-aware page text extraction for SAL source analysis.

For each PDF page, extract word boxes (PyMuPDF), classify orientation,
and reconstruct reading order:
- Vertical typesetting: cluster characters/words into columns by x-center,
  sort columns right-to-left, and within each column top-to-bottom.
- Horizontal typesetting: sort by y-band, then left-to-right.

Outputs JSON: {page: {"width":..,"height":..,"mode":"vertical|horizontal|mixed|empty",
  "chars":[...], "columns":[[...]], "hlines":[[...]]}}
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict

import fitz  # PyMuPDF


def extract_page(page: "fitz.Page") -> dict:
    w, h = page.rect.width, page.rect.height
    raw = page.get_text("rawdict")
    words = []
    for block in raw["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                for ch in span.get("chars", []):
                    c = ch["c"]
                    if c.strip() == "":
                        continue
                    words.append({
                        "c": c,
                        "x0": round(ch["bbox"][0], 2),
                        "y0": round(ch["bbox"][1], 2),
                        "x1": round(ch["bbox"][2], 2),
                        "y1": round(ch["bbox"][3], 2),
                        "dir": (line.get("dir") or (1, 0))[0],
                    })
    if not words:
        return {"width": round(w, 2), "height": round(h, 2), "mode": "empty",
                "chars": [], "columns": [], "hlines": []}

    # orientation: use span direction of text lines (dir[0]==0 => vertical)
    vert_chars = sum(1 for wd in words if wd["dir"] == 0)
    horiz_chars = sum(1 for wd in words if wd["dir"] != 0)
    if vert_chars and horiz_chars:
        mode = "mixed"
    elif vert_chars:
        mode = "vertical"
    else:
        mode = "horizontal"

    columns = []
    hlines = []
    if mode in ("vertical", "mixed"):
        # cluster into columns by x-center
        xs = sorted(((wd["x0"] + wd["x1"]) / 2, i) for i, wd in enumerate(words))
        cols = []
        cur = [xs[0][1]]
        cur_cx = xs[0][0]
        for cx, i in xs[1:]:
            if cx - cur_cx <= 14.0:  # same visual column cluster
                cur.append(i)
                cur_cx = (cur_cx * (len(cur) - 1) + cx) / len(cur)
            else:
                cols.append(cur)
                cur = [i]
                cur_cx = cx
        cols.append(cur)
        col_objs = []
        for grp in cols:
            grp_sorted = sorted(grp, key=lambda i: (words[i]["y0"], words[i]["x0"]))
            xs_ = [(words[i]["x0"] + words[i]["x1"]) / 2 for i in grp]
            col_objs.append({
                "xc": round(sum(xs_) / len(xs_), 2),
                "chars": [words[i]["c"] for i in grp_sorted],
                "bbox": [round(min(words[i]["x0"] for i in grp), 2),
                         round(min(words[i]["y0"] for i in grp), 2),
                         round(max(words[i]["x1"] for i in grp), 2),
                         round(max(words[i]["y1"] for i in grp), 2)],
            })
        col_objs.sort(key=lambda c: -c["xc"])  # right to left
        columns = col_objs
    if mode in ("horizontal", "mixed"):
        # group by y-bands
        bands = defaultdict(list)
        for i, wd in enumerate(words):
            key = round(wd["y0"] / 6.0)  # ~6pt banding
            bands[key].append(i)
        hlist = []
        for key in sorted(bands):
            grp = sorted(bands[key], key=lambda i: (words[i]["x0"], words[i]["y0"]))
            hlist.append({
                "y": round(words[grp[0]]["y0"], 2),
                "chars": [words[i]["c"] for i in grp],
                "bbox": [round(min(words[i]["x0"] for i in grp), 2),
                         round(min(words[i]["y0"] for i in grp), 2),
                         round(max(words[i]["x1"] for i in grp), 2),
                         round(max(words[i]["y1"] for i in grp), 2)],
            })
        hlines = hlist

    return {
        "width": round(w, 2), "height": round(h, 2), "mode": mode,
        "chars": words, "columns": columns, "hlines": hlines,
    }


def main(pdf_path: str, out_path: str, page_from: int = 1, page_to: int | None = None) -> None:
    doc = fitz.open(pdf_path)
    if page_to is None:
        page_to = doc.page_count
    out = {}
    for pno in range(page_from - 1, min(page_to, doc.page_count)):
        page = doc[pno]
        out[str(pno + 1)] = extract_page(page)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
    print(f"pages {page_from}..{min(page_to, doc.page_count)} -> {out_path}")
    modes = defaultdict(int)
    for v in out.values():
        modes[v["mode"]] += 1
    print("modes:", dict(modes))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2],
         int(sys.argv[3]) if len(sys.argv) > 3 else 1,
         int(sys.argv[4]) if len(sys.argv) > 4 else None)
