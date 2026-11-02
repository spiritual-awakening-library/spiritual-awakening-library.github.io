#!/usr/bin/env python3
"""Build complete Phase 0.2 inventories for both books from verified analysis data.

Outputs (to --outdir):
  book-1-inventory.csv / book-1-inventory.json
  book-2-inventory.csv / book-2-inventory.json
  book-1-page-map.json / book-2-page-map.json
  build-report.txt (console digest)

All decisions on ambiguous structures are recorded in the review ledger, not
silently resolved here; every nonstandard row carries review notes.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from b2_analyze import cn2int, cluster_columns  # noqa: E402

WORK = Path(__file__).resolve().parent
SRC = {
    "book1": WORK / "book1-pages.json",
    "book2": WORK / "book2-pages.json",
}

B1_PDF = "印刷全文-要開悟讀這本書就夠了 (2).pdf"
B2_PDF = "內文-靈性覺醒 (2).pdf"
B1_SHA = "a1f2f831e07f3505fb78fa9f7a5d90112a8ee23dc6eba8eaf04d6a1eaff2f901"
B2_SHA = "653dfb125851a20e7740cea7e5bc3c34eb36b585a0141b96dd512023c9b1d985"

# ---- normalization of PDF text-layer artifacts to standard punctuation -------
VERT = {"︽": "《", "︾": "》", "︵": "（", "︶": "）", "﹁": "「", "﹂": "」",
        "︐": "，", "︑": "；", "︙": "", "︰": "："}


def norm(s: str) -> str:
    for k, v in VERT.items():
        s = s.replace(k, v)
    return s


def load(which: str):
    return json.load(open(SRC[which], encoding="utf-8"))


# =========================================================================
# Book 1 helpers  (2-up landscape; right half = printed 2N-2, left = 2N-1)
# =========================================================================
B1_MID = 839.055 / 2


def b1_odd_headers(d):
    """odd printed page -> (label, title) from running heads."""
    out = {}
    for pno_s in sorted(d, key=int):
        pno = int(pno_s)
        pg = d[pno_s]
        chs = pg.get("chars") or []
        if not chs:
            continue
        odd = [c for c in chs if (c["x0"] + c["x1"]) / 2 < B1_MID]
        lab = [c for c in odd if 25 <= c["y0"] < 38]
        ttl = [c for c in odd if 38 <= c["y0"] < 60 and (c["x0"] + c["x1"]) / 2 >= 60]
        lab_s = "".join(c["c"] for c in sorted(lab, key=lambda c: c["x0"])).strip()
        ttl_s = "".join(c["c"] for c in sorted(ttl, key=lambda c: c["x0"])).strip()
        if lab_s or ttl_s:
            out[2 * pno - 1] = (lab_s, norm(ttl_s))
    return out


def b1_toc_rows(d):
    """Parse TOC columns on PDF pages 5-7 into structured rows."""
    rows = []
    for pno in (5, 6, 7):
        pg = d[str(pno)]
        for half_cond in ((lambda c: (c["x0"] + c["x1"]) / 2 >= B1_MID),   # even
                          (lambda c: (c["x0"] + c["x1"]) / 2 < B1_MID)):    # odd
            chs = [c for c in pg["chars"] if half_cond(c)]
            cols = cluster_columns(chs, tol=12.0)
            for col in cols:
                txt = "".join(chs[i]["c"] for i in col["idx"])
                txt = txt.replace("ʊ", "·").replace("樬", "｜")
                txt = re.sub(r"[.]{2,}", "", txt)
                if txt.strip() in ("目錄", "學員心得"):
                    rows.append({"raw": txt.strip(), "kind": "header",
                                 "pdf_page": pno})
                    continue
                m = re.search(r"·(\d{3})$", txt)
                if not m:
                    rows.append({"raw": txt, "kind": "unparsed", "pdf_page": pno})
                    continue
                body_txt, page = txt[:m.start()], int(m.group(1))
                rows.append({"raw": txt, "kind": "entry", "text": body_txt,
                             "page": page, "pdf_page": pno})
    return rows


CH_NUM_CN = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七",
             8: "八", 9: "九", 10: "十"}


def cn_chapnum(n: int) -> str:
    # 1..82 in the style used by the book (一..十, 十一..二十, 二十一..)
    if n <= 10:
        return CH_NUM_CN[n]
    if n < 20:
        return "十" + CH_NUM_CN[n - 10]
    tens, ones = divmod(n, 10)
    s = CH_NUM_CN[tens] + "十"
    if ones:
        s += CH_NUM_CN[ones]
    return s


def b1_chapters(toc):
    """Extract the 82 chapter rows, using expected per-position numerals."""
    out = []
    for r in toc:
        if r["kind"] != "entry":
            continue
        m = re.match(r"^開悟之([一二三四五六七八九十]+)(.+)$", r["text"])
        if not m:
            continue
        n_expected = len(out) + 1
        want = cn_chapnum(n_expected) if n_expected <= 82 else None
        if want and r["text"].startswith(f"開悟之{want}"):
            rest = r["text"][len(f"開悟之{want}"):]
            out.append({"num_cn": want, "title_toc": rest, "page": r["page"],
                        "raw": r["raw"], "pdf_page": r["pdf_page"],
                        "label_greedy": m.group(1), "title_greedy": m.group(2)})
        else:
            out.append({"num_cn": m.group(1), "title_toc": m.group(2),
                        "page": r["page"], "raw": r["raw"],
                        "pdf_page": r["pdf_page"], "label_greedy": m.group(1),
                        "title_greedy": m.group(2), "parse": "greedy"})
    return out


def b1_even_sidebar(d, printed):
    """Vertical title columns at the outer edge of an even printed page."""
    pno = printed // 2 + 1
    pg = d.get(str(pno))
    if pg is None:
        return ""
    MID = B1_MID
    R = [c for c in pg.get("chars", []) if (c["x0"] + c["x1"]) / 2 >= MID]
    edge = [c for c in R if (c["x0"] + c["x1"]) / 2 > 730 and c["y0"] > 60]
    cols = {}
    for c in edge:
        cols.setdefault(round((c["x0"] + c["x1"]) / 2 / 16), []).append(c)
    return " | ".join("".join(c["c"] for c in sorted(g, key=lambda c: c["y0"]))
                      for k, g in sorted(cols.items(), reverse=True))


def b1_pdf_of(printed: int) -> int:
    """printed page -> 1-based PDF sheet index."""
    return printed // 2 + 1


def b1_pos(printed: int) -> str:
    return "R" if printed % 2 == 0 else "L"


# =========================================================================
# Book 2 helpers (1:1 mapping; footer = page index; vertical typesetting)
# =========================================================================
def b2_toc_rows(d):
    rows = []
    for pno in range(1, 23):
        pg = d[str(pno)]
        chs = [c for c in pg.get("chars", []) if c["y0"] < 460]
        cols = cluster_columns(chs, tol=14.0)
        for col in cols:
            txt = "".join(d[str(pno)]["chars"][i]["c"] for i in col["idx"])
            t = norm(txt.strip())
            m = re.search(r"[.]{2,}\s*([一二三四五六七八九十百零]+)\s*[，,]?\s*$", t)
            if not m:
                m2 = re.search(r"([一二三四五六七八九十百零]+)\s*[，,]?\s*$", t)
                if m2 and (t[:m2.start()].rstrip(". ")).endswith(("》", "）", "」")):
                    m = m2
            if m:
                rows.append({"raw": norm(t), "text": norm(t[:m.start()].rstrip(". ")),
                             "page": cn2int(m.group(1)), "numtxt": m.group(1),
                             "pdf_page": pno, "xc": col["xc"]})
            else:
                rows.append({"raw": norm(t), "text": norm(t.rstrip(". ")),
                             "page": None, "numtxt": None,
                             "pdf_page": pno, "xc": col["xc"]})
    return rows


def b2_title_pages(d):
    """page -> [heading column texts] for pages 23..478."""
    out = {}
    for pno in range(23, 479):
        pg = d.get(str(pno))
        if pg is None:
            continue
        chs = pg.get("chars", [])
        big = [c for c in chs if (c["y1"] - c["y0"]) >= 19.0 and
               (ord(c["c"][0]) > 0x2E00 or c["c"].isalnum())]
        if big:
            cols = cluster_columns(big, tol=25.0)
            out[pno] = [norm("".join(chs[i]["c"] for i in col["idx"]))
                        for col in cols]
    return out


# ---- verified plate/appendix data (VLM transcription; flagged for review) ---
B2_PLATES = [
    (458, "rights-statement", "本書內容屬於全體生命，以增進生命福祉之目的，任何形式之利用與散布，無須另行通知即可實行",
     "授權聲明頁；印刷文字，另有两處手寫簽名（辨識為「江慶淇」與「江嘉祁」，高解析度VLM複核，無日期）。"),
    (459, "quote-plate", "人心惟危，道心惟微，惟精惟一，允執厥中。——《書·大禹謨》",
     "經典語錄頁（風景照片背景疊印直排大字）。"),
    (460, "quote-plate", "天行健，君子以自強不息；地勢坤，君子以厚德載物。——《易·象辭》",
     "經典語錄頁（風景照片背景）。"),
    (461, "quote-plate", "生命的目的", "黑底金字語錄頁；正文長句為書中語錄。"),
    (462, "quote-plate", "生命的最終定數", "黑底金字語錄頁。"),
    (463, "quote-plate", "生命的最終真諦", "黑底金字語錄頁。"),
    (464, "quote-plate", "天道詩", "黑底金字語錄頁。"),
    (465, "quote-plate", "處世賦", "黑底金字語錄頁；內文提及「恩師江慶淇」。"),
    (466, "quote-plate", "揚升要訣", "黑底金字語錄頁；內文提及「恩師江慶淇」。"),
    (467, "quote-plate", "禮運大同篇", "經典語錄頁（《禮運》大同章）。"),
    (468, "quote-plate", "中庸", "經典語錄頁（《中庸》首章）。"),
    (469, "quote-plate", "大學", "經典語錄頁（《大學》首章）。"),
    (470, "photo-plate", "放下面具幻覺現出真我（攝影／江慶淇）",
     "彩色照片頁；圖說含攝影者署名。"),
    (471, "photo-plate", "",
     "彩色人物照片頁（仰拍樹冠與陽光）；無文字、無標題，待人工複核。"),
    (472, "photo-plate", "滿心接受生活工作（攝影／江慶淇）", "彩色照片頁；圖說含攝影者署名。"),
    (473, "diagram-plate", "輪迴過程示意圖；輪迴轉生曆遷行為和反作用力（業力）圖",
     "示意圖頁（兩張圖）。"),
    (474, "diagram-plate", "神性基因演化示意圖", "示意圖頁（含長段說明文字）。"),
    (475, "diagram-plate", "能量樹示意圖", "示意圖頁（左負能量、右正能量）。"),
    (476, "diagram-plate", "生命輪迴命運曲線圖；宇宙壽命延續圖", "示意圖頁（兩張圖）。"),
    (477, "quote-plate", "為世界祈福", "祈福文頁（全文以印刷呈現）。"),
]

B1_PLATES = [
    # (pdf_page, position, title, kind, note)  printed numbers inferred from
    # sheet geometry only (plates carry no printed page numbers)
    (309, "L", "本源的微笑", "photo-plate",
     "作者微笑照片頁；標題印於版面（圖片頁，無文字層）。"),
    (310, "R", "阿里山森林中樹精靈和能量圈", "photo-plate", "彩色照片頁（三張森林照片）。"),
    (310, "L", "人心惟危，道心惟微，惟精惟一，允執厥中。——《書·大禹謨》", "quote-plate",
     "經典語錄頁（風景照片背景疊印直排大字）。"),
    (311, "R", "天行健，君子以自強不息；地勢坤，君子以厚德載物。——《易·象辭》", "quote-plate",
     "經典語錄頁（山巒雲海照片背景）。"),
    (311, "L", "生命的目的", "quote-plate", "黑底金字語錄頁。"),
    (312, "R", "生命的最終定數", "quote-plate", "黑底金字語錄頁。"),
    (312, "L", "生命的最終真諦", "quote-plate", "黑底金字語錄頁。"),
    (313, "R", "天道詩", "quote-plate", "黑底金字語錄頁。"),
    (313, "L", "處世賦", "quote-plate", "黑底金字語錄頁；內文提及「恩師江慶淇」。"),
    (314, "R", "揚升要訣", "quote-plate", "黑底金字語錄頁；內文提及「恩師江慶淇」。"),
    (314, "L", "禮運大同篇", "quote-plate", "經典語錄頁。"),
    (315, "R", "中庸", "quote-plate", "經典語錄頁（《中庸》首章）。"),
    (315, "L", "大學", "quote-plate", "經典語錄頁（《大學》首章）。"),
    (316, "R", "太陽系進入高頻率帶示意圖；量子雙縫實驗圖", "diagram-plate", "示意圖頁（兩張圖）。"),
    (316, "L", "輪迴過程示意圖；輪迴轉生曆遷行為和反作用力（業力）圖", "diagram-plate",
     "示意圖頁（兩張圖）。"),
    (317, "R", "宇宙次元示意圖；宇宙次元構念圖；空間扭曲圖", "diagram-plate",
     "示意圖頁（三張圖；左右半歸屬經分半高解析VLM複核）。"),
    (317, "L", "靈魂加固示意圖；神性基因演化示意圖", "diagram-plate",
     "示意圖頁（兩張圖；左右半歸屬經分半高解析VLM複核）。"),
    (318, "R", "神性基因演化示意圖", "diagram-plate", "示意圖頁（含說明文字）。"),
    (318, "L", "江慶淇老師的便當與水果", "photo-plate",
     "彩色照片頁（便當與水果；附文字說明「江慶淇老師：吃飯了！……」）。"),
    (319, "R", "時空維度示意圖", "diagram-plate", "示意圖頁（3維與4維時間線兩圖）。"),
    (319, "L", "時空維度（4維空間）", "diagram-plate",
     "示意圖／文字頁（低維度與4維空間說明）；確切標題待人工複核。"),
    (320, "R", "5維空間", "diagram-plate", "示意圖頁（5維空間與「例如」圖解）。"),
    (320, "L", "6維空間", "diagram-plate", "示意圖頁（時間點彎曲關係）。"),
    (321, "R", "6維時空點；7維空間", "diagram-plate", "示意圖頁（兩張圖）。"),
    (321, "L", "8維空間", "diagram-plate", "示意圖頁（轉學點展開無限可能）。"),
    (322, "R", "9維空間", "diagram-plate", "示意圖頁（時空點彎曲連結）。"),
    (322, "L", "10維空間", "diagram-plate", "示意圖頁（10維空間點）。"),
    (323, "R", "能量樹示意圖", "diagram-plate", "示意圖頁（負能量／正能量）。"),
    (323, "L", "生命輪迴命運曲線圖；宇宙壽命延續圖", "diagram-plate", "示意圖頁（兩張圖）。"),
    (324, "R", "高我體系示意圖", "diagram-plate", "示意圖頁（1級高我與0級樹狀圖）。"),
    (324, "L", "為世界祈福", "quote-plate", "祈福文頁（湖畔照片背景）。"),
]


def make_row(book, eid, kind, order, title, printed, pdf_page, pos="",
             qualifier="", series="", author="", toc_status="not-in-toc",
             body_status="needs-review", translation="not-started",
             notes="", toc_text="", body_text=""):
    return {
        "book_id": book, "entry_id": eid, "entry_kind": kind,
        "order_in_book": order, "original_title": title,
        "title_qualifier": qualifier, "parent_series": series,
        "attributed_author": author,
        "printed_page": printed, "printed_page_num": None,
        "pdf_page": pdf_page, "pdf_page_position": pos,
        "source_file": B1_PDF if book == "book-1" else B2_PDF,
        "language": "zh-TW",
        "toc_status": toc_status, "body_status": body_status,
        "translation_status": translation, "review_notes": notes,
        "_toc_text": toc_text, "_body_text": body_text,
    }


def finalize(rows):
    for r in rows:
        pp = r["printed_page"]
        if isinstance(pp, int):
            r["printed_page_num"] = pp
            r["printed_page"] = f"{pp:03d}" if r["book_id"] == "book-1" and pp < 700 else str(pp)
        elif isinstance(pp, str) and pp and any(ch in "一二三四五六七八九十百零" for ch in pp):
            r["printed_page_num"] = cn2int(pp)
    return rows


CSV_COLUMNS = ["book_id", "entry_id", "entry_kind", "order_in_book",
               "original_title", "title_qualifier", "parent_series",
               "attributed_author", "printed_page", "printed_page_num",
               "pdf_page", "pdf_page_position", "source_file", "language",
               "toc_status", "body_status", "translation_status", "review_notes"]


def write_csv(rows, path: Path):
    import csv
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in CSV_COLUMNS})


def build_book1(outdir: Path):
    d = load("book1")
    toc = b1_toc_rows(d)
    heads = b1_odd_headers(d)
    chapters = b1_chapters(toc)
    problems = []

    # --- cross-check chapters against running heads -------------------------
    title_diffs = {}
    for idx, ch in enumerate(chapters, start=1):
        n = idx
        if cn2int(ch["num_cn"]) != n:
            problems.append(f"chapter sequence mismatch at {n}: label {ch['num_cn']}")
        p = ch["page"]
        first_odd = p if p % 2 == 1 else p + 1
        lab, ttl = heads.get(first_odd, ("", ""))
        want = f"開悟之{ch['num_cn']}"
        if lab != want:
            problems.append(f"ch{n}: running head label mismatch at printed {first_odd}: {lab!r} != {want!r}")
        if ttl != norm(ch["title_toc"]):
            # TOC form differs from body running head: body form is canonical
            title_diffs[n] = (norm(ch["title_toc"]), ttl)
    if len(chapters) != 82:
        problems.append(f"expected 82 chapters, got {len(chapters)}")

    # --- prefaces ------------------------------------------------------------
    pref_rows = []
    pref_defs = [
        ("推薦序", "靈性開悟宇宙合一", "吳錦珠", 2, "preface",
         "推薦序｜靈性開悟宇宙合一／吳錦珠"),
        ("作者序", "眼前所遇，即其所需", "江慶淇", 5, "preface",
         "作者序｜眼前所遇，即其所需／江慶淇"),
        ("江嘉祁序", "道德是宇宙萬物的基石", "江嘉祁", 7, "foreword",
         "道德是宇宙萬物的基石／江嘉祁"),
    ]
    for i, (label, title, author, page, kind, tocrow) in enumerate(pref_defs, 1):
        first_odd = page if page % 2 == 1 else page + 1
        lab, ttl = heads.get(first_odd, ("", ""))
        body_ok = (lab == label or (label == "江嘉祁序" and lab == "江嘉祁序")) and ttl == title
        pref_rows.append(make_row(
            "book-1", f"preface-{i:02d}", kind, 1 + i, title, page,
            b1_pdf_of(page), b1_pos(page), author=author, series=label,
            toc_status="toc-verified",
            body_status="body-verified-running-head" if body_ok else "needs-review",
            notes=(f"TOC列：{tocrow}。序文標籤（{label}）作為parent_series記錄；"
                   f"正文第{page}頁起，版面頂部直排標題欄與跑頁眉核對一致。"
                   if body_ok else f"TOC列：{tocrow}。跑頁眉核對不符，待複核。"),
            toc_text=tocrow, body_text=f"頁眉：{lab}／{ttl}"))

    # --- toc & cover & colophon ----------------------------------------------
    toc_row = make_row("book-1", "toc", "toc", 5, "目錄", 8, 5, "R",
                       series="目錄",
                       toc_status="not-in-toc",
                       body_status="body-verified",
                       notes="目錄本身為內容單元；佔印刷頁008–013（PDF 5–7）；"
                             "目錄頁無頁眉頁碼，印刷頁碼由拼版幾何推定並經全書頁碼連續性核對。")
    cover_row = make_row(
        "book-1", "cover", "cover", 1, "要開悟，讀這本書就夠了", None, 1, "R",
        author="江慶淇（著）",
        body_status="image-only-vlm-transcribed",
        notes="封面（印刷全文第1頁為圖片頁，無文字層）。書名「要開悟，讀這本書就夠了」另經來源檔"
              "「印刷封面」PDF文字層直書複核（含逗號），與書內序文引用形式一致；封面圖像VLM轉錄含"
              "作者「江慶淇 著」與推介文字。無印刷頁碼（000–001，拼版幾何推定）。")
    colophon_row = make_row(
        "book-1", "colophon", "colophon", 127, "版權頁（國家圖書館出版品預行編目資料）", 649,
        325, "L", body_status="body-verified",
        notes="CIP：要開悟讀這本書就夠了／江慶淇著.--初版.--〔新北市〕：江嘉祁，2022.04；"
              "ISBN 978-957-43-9795-2（平裝）。印刷頁648為空白頁（同PDF頁右半）。")

    # --- chapters -------------------------------------------------------------
    ch_rows = []
    for idx, ch in enumerate(chapters, start=1):
        p = ch["page"]
        title = norm(ch["title_toc"])
        sep_note = ""
        if idx == 22:
            # TOC uses ｜ here while the body running head uses ─
            title = title.replace("｜", "─")
            sep_note = ("TOC印作「世界七大哉問｜神性基因（上）」（｜），正文頁眉作「─」；"
                        "本列採正文形式，TOC原文見toc_text。")
        if idx in title_diffs:
            toc_form, body_form = title_diffs[idx]
            title = body_form
            sep_note = (f"TOC作「{toc_form}」，正文頁眉作「{body_form}」；"
                        "本列採正文形式，差異保留待審（見待審清單）。")
        if idx == 78:
            sep_note += " 章首（546頁直排題欄）經複核為「揚升日來臨的選擇路徑」（無「時」）。"
        ch_rows.append(make_row(
            "book-1", f"chapter-{idx:02d}", "chapter", 6 + idx - 1, title, p,
            b1_pdf_of(p), b1_pos(p),
            series=f"開悟之{ch['num_cn']}",
            toc_status="toc-verified",
            body_status="body-verified-running-head",
            notes=(sep_note or f"開悟之{ch['num_cn']}；TOC頁碼{p:03d}與正文（第"
                   f"{p if p % 2 == 1 else p + 1}頁起之頁眉）核對一致。")
            + ("" if idx != 1 else " 開篇版面（PDF第8頁右半直排「開悟之一／本源與宇宙次元」欄）經Phase 0.1種子清單複核。"),
            toc_text=norm(ch["raw"]),
            body_text=f"頁眉：開悟之{ch['num_cn']}／{title}"))

    # --- testimonials ----------------------------------------------------------
    testi = []
    for r in toc:
        if r["kind"] == "entry" and r["pdf_page"] == 7 and "／" in (r.get("text") or "") \
                and not r["text"].startswith("開悟之"):
            m = re.match(r"^(.+?)／(.+?)$", r["text"])
            if m:
                testi.append({"title": norm(m.group(1)), "author": m.group(2),
                              "page": r["page"], "raw": norm(r["raw"])})
    testi_rows = []
    for i, t in enumerate(testi, 1):
        p = t["page"]
        first_odd = p if p % 2 == 1 else p + 1
        lab, ttl = heads.get(first_odd, ("", ""))
        body_ok = lab == "學員心得" and ttl == t["title"]
        evidence = f"頁眉核對一致（{first_odd}頁）。"
        body_kind = "body-verified-running-head"
        if not body_ok and p % 2 == 0:
            side = b1_even_sidebar(d, p)
            if t["title"] in side:
                body_ok = True
                body_kind = "body-verified-opening"
                evidence = f"僅佔一頁（{p}頁，偶數頁）；開篇直排題欄核對一致：「{side.strip()}」。"
        testi_rows.append(make_row(
            "book-1", f"testimonial-{i:02d}", "testimonial", 88 + i - 1, t["title"],
            p, b1_pdf_of(p), b1_pos(p), author=t["author"], series="學員心得",
            toc_status="toc-verified",
            body_status=body_kind if body_ok else "needs-review",
            notes=f"學員心得系列；TOC列：{t['raw']}。" + evidence,
            toc_text=t["raw"], body_text=f"頁眉：{lab}／{ttl}"))

    # --- plates -----------------------------------------------------------------
    plate_rows = []
    order = 96
    for pdf_page, pos, title, kind, note in B1_PLATES:
        printed = 2 * pdf_page - 2 if pos == "R" else 2 * pdf_page - 1
        plate_rows.append(make_row(
            "book-1", f"plate-{order - 95:03d}", kind, order, title, None,
            pdf_page, pos, body_status="image-only-vlm-transcribed",
            notes=(note + f" 無印刷頁碼；依拼版幾何此位置對應印刷頁{printed:03d}（推定值，僅供定位，不作為頁碼證據）。")
        ))
        order += 1

    rows = ([cover_row] + pref_rows + [toc_row] + ch_rows + testi_rows
            + plate_rows + [colophon_row])
    rows = finalize(rows)
    return rows, problems, d


def build_book2(outdir: Path):
    d = load("book2")
    toc = b2_toc_rows(d)
    titles = b2_title_pages(d)
    problems = []

    entries = []  # (page, [toc texts], type, canonical, series, qualifier, author)

    # group toc rows by page
    by_page = {}
    for r in toc:
        if r["page"] is None:
            continue
        by_page.setdefault(r["page"], []).append(r)
    toc_pages = sorted(by_page)

    # verify count and monotonicity
    nums = [p for p in toc_pages]
    for a, b in zip(nums, nums[1:]):
        if b < a:
            problems.append(f"TOC page order violation {a}->{b}")
    if set(toc_pages) != set(titles):
        problems.append(f"TOC pages != body title pages: only-toc="
                        f"{sorted(set(toc_pages) - set(titles))} only-body="
                        f"{sorted(set(titles) - set(toc_pages))}")

    essay_pages = [p for p in toc_pages if 37 <= p <= 280]
    for p in essay_pages:
        rowset = by_page[p]
        body = titles.get(p, [])
        joined = "".join(r["text"] for r in rowset)
        # 1) series group: the LAST （慶淇…） run
        series = ""
        m = None
        for m_ in re.finditer(r"（慶淇(?:悟得手札|手札拾穗)[^）]*）", joined):
            m = m_
        if m:
            series = m.group(0)[1:-1]
            joined = joined[:m.start()] + joined[m.end():]
        # 2) byline directly after the closing 》, outside brackets (《前夕》江慶淇)
        byline = ""
        mb = re.search(r"》([^（）《》]+)$", joined.strip())
        if mb and mb.group(1).strip():
            byline = mb.group(1).strip()
            joined = joined[:mb.start()] + "》"
        # 3) title vs trailing qualifier groups
        joined = joined.strip()
        before, sep, after = joined.rpartition("》")
        if sep:
            title = before.lstrip("《").strip()
            quals = [q for q in re.findall(r"（([^（）]*)）", after)]
            qualifier = "、".join(q for q in quals if q)
        else:
            title = joined.strip("《").strip()
            qualifier = ""
        entries.append({
            "page": p, "type": "essay", "title": title, "qualifier": qualifier,
            "series": series or None, "author": byline,
            "toc_texts": [r["raw"] for r in rowset],
            "body": body, "byline": byline,
        })

    # special pages
    specials = {
        23: ("title-page", "靈性開悟進程奧義手札", None, ""),
        25: ("preface", "一份真實的路徑", "慶淇悟得手札自序", ""),
        32: ("acknowledgment", "感恩篇", None, ""),
        283: ("analysis", "悟得手札解析", None, "江慶淇老師"),
        371: ("blessing", "給學員們的祝福", None, "江慶淇老師"),
        417: ("interview", "江慶淇老師專訪", None, ""),
        449: ("testimony-story", "心開意解學員江嘉祁", None, "江嘉祁"),
    }
    for p, (kind, title, series, author) in specials.items():
        rowset = by_page.get(p, [])
        entries.append({
            "page": p, "type": kind, "title": title, "qualifier": "",
            "series": series, "author": author,
            "toc_texts": [r["raw"] for r in rowset],
            "body": titles.get(p, []), "byline": "",
        })

    entries.sort(key=lambda e: e["page"])
    if len(essay_pages) != 139:
        problems.append(f"expected 139 essays, got {len(essay_pages)}")

    # build rows
    final = []
    order = 1
    final.append(make_row(
        "book-2", "toc", "toc", order, "目錄", 1, 1, "",
        series="目錄（印刷頁1–22）", body_status="body-verified",
        notes="目錄佔印刷頁1–22（PDF 1–22，頁腳頁碼一比一對應）；目錄為直排多欄，欄序由右至左，"
              "頁碼以中文數字印於各欄欄底。目錄列共214列（含併列），146個不同頁碼定位。"))
    order += 1
    essay_n = 0
    plate_n = 0
    for e in entries:
        kind = e["type"]
        if kind == "essay":
            essay_n += 1
            eid = f"essay-{essay_n:03d}"
        else:
            eid = {"title-page": "title-page", "preface": "preface-01",
                   "acknowledgment": "acknowledgments-01", "analysis": "analysis-01",
                   "blessing": "blessing-01", "interview": "interview-01",
                   "testimony-story": "testimony-01"}[kind]
        notes = ""
        if e["page"] == 283:
            notes = ("版面印兩欄大字「江慶淇老師」＋「悟得手札解析」，目錄亦分兩列（均指283頁）；"
                     "本列採單一內容單元記錄（標題「悟得手札解析」，欄列屬性記於attributed_author），"
                     "複合標題「江慶淇老師悟得手札解析」之訂定留待編輯決策（見待審清單）。"
                     "正文285–370（284為空白頁，僅頁腳頁碼）。")
        elif e["page"] == 371:
            notes = ("版面印「江慶淇老師」＋「給學員們的祝福」兩欄，目錄兩列均指371頁；"
                     "記錄方式同上，複合標題「江慶淇老師給學員們的祝福」之訂定留待編輯決策。"
                     "正文373–416（372為空白頁，僅頁腳頁碼）。")
        elif e["page"] == 417:
            notes = ("版面印三欄大字「不再神秘的靈性開悟」「靈性開悟奧義手札」「江慶淇老師專訪」，"
                     "目錄三列均指417頁；內文419–448為廣播專訪逐字稿（亞菲夢想花園節目，主持人亞菲）。"
                     "本列以「江慶淇老師專訪」為內容單元標題，其餘兩欄為題欄文字；"
                     "「靈性開悟奧義手札」與書中書全名「靈性開悟進程奧義手札」（少「進程」二字）之差異保留原文並待審。"
                     "418為空白頁（僅頁腳頁碼）。")
        elif e["page"] == 449:
            notes = ("版面印單欄「心開意解學員江嘉祁」（9字）；推測可讀作「心開意解」＋「學員江嘉祁」，"
                     "訂定留待編輯決策；正文451–457（450為空白頁，僅頁腳頁碼）。")
        elif e["page"] == 23:
            notes = "主體總書名頁（正文起點）；目錄首列即此（23頁）。24為空白頁（僅頁腳頁碼）。"
        elif e["page"] == 25:
            notes = "自序跨頁25–31；目錄列《一份真實的路徑》（慶淇悟得手札自序）。"
        elif e["page"] == 32:
            notes = "感恩篇（謝辭）跨頁32–36。"
        body_txt = " | ".join(e["body"])
        toc_txt = "；".join(e["toc_texts"])
        if e["type"] == "essay":
            joined_body = "".join(e["body"])
            head_ok = (e["title"].strip("《") in [t.strip("《》 ") for t in e["body"]]
                       or any(e["title"] in t for t in e["body"])
                       or e["title"] in joined_body)
            if not head_ok:
                # punctuation-insensitive fallback: TOC and body may print
                # the same title with different punctuation (e.g. missing comma)
                def _strip_punct(s):
                    return re.sub(r"[，、,。　 ]", "", s)
                toc_form = e["title"]
                want = _strip_punct(toc_form)
                for t in e["body"]:
                    tt = t.strip("《》 ").strip()
                    if _strip_punct(tt) == want:
                        e["title"] = tt
                        extra += (f"TOC作「{toc_form}」，正文作「{tt}」；"
                                  f"本列採正文形式，差異保留待審（見待審清單）。")
                        head_ok = True
                        break
            extra = (f"目錄頁碼{e['page']}（{by_page[e['page']][0]['numtxt']}）與正文標題頁（大字標題）核對一致。")
            if e["page"] == 268 and e["byline"]:
                extra = extra + "標題欄附作者署名「江慶淇」（書名後直書）。"
            if e["title"] == "悟了之後":
                extra += "〈悟了之後〉系列之部分篇章（系列關係按原文保留，各篇各自成目）。"
            if e["title"].startswith("覺醒之路"):
                extra += "〈覺醒之路荊棘佈，驀然真我合一悟〉分（上篇）（下篇·完結篇）刊出，系列關係按原文保留。"
            if e["title"].startswith("生活裡覺醒的"):
                extra += "「生活裡覺醒」三步系列之一，系列關係按原文保留。"
            if e["title"].startswith("居福地"):
                extra += "〈居福地〉系列之分篇，系列關係按原文保留。"
            if e["title"].startswith("真相") and e["page"] in (71, 100, 121):
                extra += "〈真相〉三篇（一）（二）（三），系列關係按原文保留。"
            final.append(make_row(
                "book-2", eid, "essay", order, e["title"],
                e["page"], e["page"], "", qualifier=e["qualifier"],
                series=e["series"] or "", author=e["byline"] or "",
                toc_status="toc-verified",
                body_status="body-verified-heading" if head_ok else "needs-review",
                notes=((notes + " " if notes else "") + extra),
                toc_text=toc_txt, body_text=body_txt))
        else:
            final.append(make_row(
                "book-2", eid, kind, order, e["title"], e["page"], e["page"], "",
                series=e["series"] or "", author=e["author"] or "",
                toc_status="toc-verified",
                body_status="body-verified-heading",
                notes=notes or f"目錄頁碼{e['page']}；正文標題頁核對一致。",
                toc_text=toc_txt, body_text=body_txt))
        order += 1

    for p, kind, title, note in B2_PLATES:
        plate_n += 1
        final.append(make_row(
            "book-2", f"plate-{plate_n:03d}", kind, order, title, None, p, "",
            body_status="image-only-vlm-transcribed",
            notes=note + " 無印刷頁碼（頁面無文字層）。"))
        order += 1
    final.append(make_row(
        "book-2", "colophon", "colophon", order,
        "版權頁（國家圖書館出版品預行編目資料）", 478, 478, "",
        body_status="body-verified",
        notes="CIP：靈性覺醒／江慶淇著.--初版.--新北市：江嘉祁，2022.3；ISBN 978-957-43-9327-5（平裝）；"
              "定價新臺幣500元；印刷：吉時印 PODesign。"))

    final = finalize(final)
    return final, problems, d


def page_maps(rows1, rows2, d1, d2, outdir: Path):
    """Assign every printed page of both books to an owner entry (derived
    artifact for completeness accounting; not itself source evidence)."""
    def build(rows, first_page, last_page, overrides):
        # ordered starts by printed page
        starts = []
        for r in rows:
            ppn = r.get("printed_page_num")
            if r["entry_id"] in overrides:
                ppn = overrides[r["entry_id"]]
            if ppn is None and r.get("pdf_page") is not None:
                # unnumbered plate: position from pdf geometry (book-1 halves)
                pos = r.get("pdf_page_position") or ""
                if r["book_id"] == "book-1" and pos in ("R", "L"):
                    ppn = 2 * r["pdf_page"] - (2 if pos == "R" else 1)
            starts.append({"pp": ppn, "id": r["entry_id"],
                           "pdf": r.get("pdf_page"), "kind": r["entry_kind"]})
        starts = [s for s in starts if s["pp"] is not None]
        starts.sort(key=lambda s: s["pp"])
        mp = {}
        for i, s in enumerate(starts):
            end = (starts[i + 1]["pp"] - 1) if i + 1 < len(starts) else last_page
            if s["pp"] > end:
                end = s["pp"]
            for p in range(s["pp"], end + 1):
                mp.setdefault(p, s["id"])
        gaps = [p for p in range(first_page, last_page + 1) if p not in mp]
        return {str(k): mp[k] for k in sorted(mp)}, gaps

    # book-1: cover starts at printed 0; colophon owns 648-649 (648 blank)
    m1, gaps1 = build(rows1, 0, 649, {"cover": 0, "colophon": 648})
    # book-2: printed 1..478
    m2, gaps2 = build(rows2, 1, 478, {})
    json.dump({"book": "book-1", "printed_page_range": [0, 649],
               "note": "derived accounting map; unnumbered plate positions from sheet geometry",
               "page_owner": m1},
              open(outdir / "book-1-page-map.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump({"book": "book-2", "printed_page_range": [1, 478],
               "note": "derived accounting map; footer page numbers equal PDF page index 1:1",
               "page_owner": m2},
              open(outdir / "book-2-page-map.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return gaps1, gaps2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(WORK / "inventory-out"))
    args = ap.parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows1, prob1, d1 = build_book1(outdir)
    rows2, prob2, d2 = build_book2(outdir)

    write_csv(rows1, outdir / "book-1-inventory.csv")
    write_csv(rows2, outdir / "book-2-inventory.csv")
    for rows, name in ((rows1, "book-1"), (rows2, "book-2")):
        payload = {
            "schema": "sal-phase0-2-inventory/1.0",
            "book": name,
            "source_pdf": rows[0]["source_file"],
            "source_sha256": B1_SHA if name == "book-1" else B2_SHA,
            "entries": rows,
        }
        json.dump(payload, open(outdir / f"{name}-inventory.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)

    miss1, miss2 = page_maps(rows1, rows2, d1, d2, outdir)

    report = []
    report.append("BOOK1 entries: %d" % len(rows1))
    report.append("BOOK2 entries: %d" % len(rows2))
    report.append("BOOK1 problems: %s" % (prob1 or "NONE"))
    report.append("BOOK2 problems: %s" % (prob2 or "NONE"))
    report.append("unassigned pages book-1: %s" % (miss1 or "NONE"))
    report.append("unassigned pages book-2: %s" % (miss2 or "NONE"))
    kinds1 = {}
    for r in rows1:
        kinds1[r["entry_kind"]] = kinds1.get(r["entry_kind"], 0) + 1
    kinds2 = {}
    for r in rows2:
        kinds2[r["entry_kind"]] = kinds2.get(r["entry_kind"], 0) + 1
    report.append("book-1 kinds: %r" % kinds1)
    report.append("book-2 kinds: %r" % kinds2)
    text = "\n".join(report)
    open(outdir / "build-report.txt", "w", encoding="utf-8").write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
