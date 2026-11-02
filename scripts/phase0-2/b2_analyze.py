#!/usr/bin/env python3
"""Book 2 structural analyzer: per-page footer number, title detection, columns."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict

CN_NUM = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7,
          '八': 8, '九': 9, '十': 10, '百': 100, '千': 1000, '零': 0}


def cn2int(s: str) -> int | None:
    """Convert Chinese numeral like 二十三 / 百十四 / 二百四十九 to int."""
    if not s or any(ch not in CN_NUM for ch in s):
        return None
    total, section, num = 0, 0, 0
    for ch in s:
        v = CN_NUM[ch]
        if v >= 10:
            if num == 0:
                num = 1
            if v >= 100:
                section = (section + num) * v
                num = 0
            else:
                section += num * v
                num = 0
        else:
            num = v
    total = section + num
    return total if total > 0 else None


def cluster_columns(chars, tol=14.0):
    """Cluster chars into visual columns by x-center; sort cols right-to-left,
    chars top-to-bottom."""
    if not chars:
        return []
    xs = sorted(((c["x0"] + c["x1"]) / 2, i) for i, c in enumerate(chars))
    cols, cur, cur_cx = [], [xs[0][1]], xs[0][0]
    for cx, i in xs[1:]:
        if cx - cur_cx <= tol:
            cur.append(i)
            cur_cx = (cur_cx * (len(cur) - 1) + cx) / len(cur)
        else:
            cols.append(cur)
            cur, cur_cx = [i], cx
    cols.append(cur)
    out = []
    for grp in cols:
        gs = sorted(grp, key=lambda i: (chars[i]["y0"], chars[i]["x0"]))
        xc = round(sum((chars[i]["x0"] + chars[i]["x1"]) / 2 for i in grp) / len(grp), 2)
        out.append({"xc": xc, "idx": gs,
                    "text": "".join(chars[i]["c"] for i in gs),
                    "y_min": min(chars[i]["y0"] for i in gs),
                    "y_max": max(chars[i]["y1"] for i in gs)})
    out.sort(key=lambda c: -c["xc"])
    return out


def footer_number(chars):
    """Detect printed page number in the footer line (y0 > 460).
    Footer numerals are set horizontally at bottom-left (odd) or bottom-right
    (even). Join by x and parse as one Chinese-numeral (or digit) token."""
    foot = [c for c in chars if c["y0"] > 460 and c["y1"] < 485]
    if not foot:
        return None, ""
    foot.sort(key=lambda c: c["x0"])
    t = "".join(c["c"] for c in foot).strip(" .")
    t = t.replace("︐", "").replace("︑", "").strip()
    if not t:
        return None, ""
    if re.fullmatch(r"[一二三四五六七八九十百千零]+", t):
        return cn2int(t), t
    if re.fullmatch(r"\d+", t):
        return int(t), t
    return None, t


def title_chars(chars):
    """Large glyph chars (height >= 19pt) — chapter/section titles."""
    big = [c for c in chars if (c["y1"] - c["y0"]) >= 19.0 and
           (ord(c["c"][0]) > 0x2E00 or c["c"].isalnum())]
    return big


def main(pages_json: str, out_json: str) -> None:
    d = json.load(open(pages_json, encoding="utf-8"))
    summary = {}
    for pno in sorted(d, key=int):
        pg = d[pno]
        chars = pg.get("chars", [])
        info = {"page": int(pno), "mode": pg["mode"], "n_chars": len(chars), "n_big": 0}
        if not chars:
            summary[pno] = info
            continue
        fv, ft = footer_number(chars)
        info["footer"] = fv
        info["footer_text"] = ft
        big = title_chars(chars)
        info["n_big"] = len(big)
        if big:
            # reconstruct big-char text: cluster into columns, right-to-left
            cols = cluster_columns(big, tol=25.0)
            info["title_text"] = " | ".join(
                "".join(chars[i]["c"] for i in col["idx"]) for col in cols)
        # first body column text (rightmost col of non-footer chars)
        body = [c for c in chars if c["y0"] <= 440]
        cols = cluster_columns(body, tol=14.0)
        info["n_cols"] = len(cols)
        if cols:
            info["first_col"] = cols[0]["text"][:60]
            info["col_xc"] = [c["xc"] for c in cols[:3]]
        summary[pno] = info
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=1)
    # console digest
    for pno in sorted(d, key=int):
        i = summary[pno]
        t = i.get("title_text", "")
        ft = i.get("footer_text", "")
        fc = (i.get("first_col", "") or "")[:36]
        print(f"p{int(pno):>3} footer={ft:<8} big={i['n_big']:>3} "
              f"cols={i.get('n_cols', 0):>2} first={fc!r} title={t[:44]!r}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
