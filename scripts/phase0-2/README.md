# Phase 0.2 分析管線（Analysis Pipeline）

重現 `data/inventory/` 內容所需之腳本。執行順序：

```
1. extract_pages.py   # 逐頁座標文字層萃取 → book{1,2}-pages.json（中介檔，不入庫；約 36/12 MB）
2. b2_analyze.py       # book-2 頁腳頁碼／大字標題分析（函式庫＋摘要輸出）
3. b2_toc_body.py      # book-2 目錄重建（直欄右起左訖）＋正文標題頁掃描
4. b2_crosscheck.py    # book-2 目錄↔正文交叉核對（146/146 雙向）
5. b1_analyze.py       # book-1 拼版半頁（右＝偶數頁 2N−2）／頁眉／頁碼分析
6. b1_toc_scan.py      # book-1 直排目錄解析＋全書奇數頁頁眉序列
7. build_inventory.py  # 建置 CSV/JSON/分頁映射（內建交叉核對；輸出 build-report.txt）
8. ../validate_inventory.py  # 31 項結構驗證
```

## 環境

- Python 3.12+；分析依賴：PyMuPDF（`fitz`）。`b2_analyze.py` 之 `cn2int`、`cluster_columns` 為 `b2_toc_body.py`／`build_inventory.py` 所引用。
- 來源 PDF（不可入庫）：
  - `印刷全文-要開悟讀這本書就夠了 (2).pdf`（SHA-256 見 `data/inventory/book-1-inventory.json`）
  - `內文-靈性覺醒 (2).pdf`（SHA-256 見 `data/inventory/book-2-inventory.json`）

## 已驗證之版面定則

- **book-1**：橫向雙頁拼版（839.055×595.276 pt）；**右半＝印刷偶數頁 2N−2、左半＝奇數頁 2N−1**（右開本）。頁碼三位數零填充，印於頁眉外側；偶數頁頁眉＝書名、奇數頁頁眉＝「開悟之N」＋章名。
- **book-2**：A5 直排；**PDF 頁序＝印刷頁序（1:1）**，頁腳中文數字（奇數頁左下、偶數頁右下）；目錄直欄右起左訖，頁碼置欄底虛線後。
- 直排頁以 x 座標分欄（容差 14pt）、欄內自上而下重排；PDF 直式碼位（U+FE10、FE30–FE42）標準化為橫式標點（見 `build_inventory.py` 之 `norm()`）。

## 注意

- `build_inventory.py` 內含 VLM 轉錄之圖版資料（`B1_PLATES`／`B2_PLATES`）與已驗證之結構定則；待審事項見 `docs/verification/2026-11-02-phase0-2-review-ledger.md`。
- 本管線為**研究重現用**；正式驗證以 `scripts/validate_inventory.py` 為準。
