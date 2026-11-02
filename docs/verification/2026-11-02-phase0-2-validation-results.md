# Phase 0.2 — 驗證結果紀錄（Validation Results）

**日期：** 2026-11-02
**分支：** `data/sal-complete-book-inventory-20261102`（自 `main` @ `355c13b` 分出）
**範圍：** 兩書完整內容單元清單之自動化驗證；不含全文轉錄審查、翻譯審查或權利清理。

## 一、執行環境

| 項目 | 值 |
| --- | --- |
| 作業系統 | Linux（沙箱環境）；腳本以 POSIX 路徑撰寫，相容 Windows |
| Python | 3.12.16（`/home/z/.venv/bin/python3`） |
| 第三方依賴（分析用） | PyMuPDF 1.26.7、pdfplumber 0.11.9、poppler-utils（pdftotext / pdfinfo / pdftoppm） |
| 驗證腳本依賴 | 無（僅標準庫） |

## 二、實際執行指令與結果

### 1. Phase 0.2 清單驗證（本次新增）

```
$ python3 scripts/validate_inventory.py
PASS: book-1-schema
PASS: book-1-unique-ids
PASS: book-1-required-fields
PASS: book-1-book-refs
PASS: book-1-order-consistent
PASS: book-1-order-reproducible
PASS: book-1-entry-types
PASS: book-1-page-formats
PASS: book-1-missing-info
PASS: book-1-status-consistency
PASS: book-1-no-overlaps
PASS: book-1-json-count
PASS: book-1-json-csv-match
PASS: book-1-page-coverage
PASS: book-2-schema
PASS: book-2-unique-ids
PASS: book-2-required-fields
PASS: book-2-book-refs
PASS: book-2-order-consistent
PASS: book-2-order-reproducible
PASS: book-2-entry-types
PASS: book-2-page-formats
PASS: book-2-missing-info
PASS: book-2-status-consistency
PASS: book-2-no-overlaps
PASS: book-2-json-count
PASS: book-2-json-csv-match
PASS: book-2-page-coverage
PASS: sources-not-committed
PASS: book-1-single-source
PASS: book-2-single-source

checks: 31; pass: 31; fail: 0; warnings: 0
PASS: complete book inventories are structurally valid.
LIMITATION: structural validation only; not transcription review, translation review, or rights clearance.
EXIT=0
```

**結果：31 項檢查全數通過，0 項失敗，0 項警告。**

涵蓋之檢查類別（對應 Phase 0.2 需求第七節）：

| 需求檢查類別 | 對應檢查項 |
| --- | --- |
| 唯一 ID | `book-N-unique-ids` |
| 必填欄位 | `book-N-required-fields`、`book-N-schema` |
| 有效書籍引用 | `book-N-book-refs`、`book-N-single-source` |
| 順序一致 | `book-N-order-consistent`（1..N 嚴格遞增）、`book-N-order-reproducible`（印刷頁序單調） |
| 允許的單元類型 | `book-N-entry-types`（封閉集合） |
| 頁碼格式 | `book-N-page-formats`（book-1 三位數零填充；book-2 中文數字；PDF 幾何映射核對） |
| 資訊缺失 | `book-N-missing-info`（language、source_file、review_notes、essay 之 parent_series） |
| 驗證狀態一致性 | `book-N-status-consistency`（toc_status / body_status / translation_status 之封閉集合與組合規則） |
| 重複或重疊條目 | `book-N-no-overlaps`（同一印刷頁不得有兩個起始條目）、重複標題警告 |

另含跨檔一致性（`book-N-json-csv-match`）與**分頁覆蓋完整性**（`book-N-page-coverage`）：
book-1 印刷頁 000–649 全數指派；book-2 印刷頁 1–478 全數指派；無未歸屬頁面。

### 2. Phase 0.1 基礎驗證（回歸測試，確認未破壞既有驗證）

```
$ python3 scripts/verify_foundation.py
PASS: 9 tracked files checked; 10 seed entries structurally valid.
LIMITATION: Not a complete chapter inventory, translation review, or full security audit.
EXIT=0
```

既有 `data/chapter-inventory-SEED-INCOMPLETE.csv` 與 PR 驗證工作流均未更動。

### 3. 分析管線重現指令（供審查者重跑）

來源 PDF（未納入儲存庫）置於工作目錄後：

```
$ python3 scripts/phase0-2/extract_pages.py "<來源>/印刷全文-要開悟讀這本書就夠了 (2).pdf" book1-pages.json
$ python3 scripts/phase0-2/extract_pages.py "<來源>/內文-靈性覺醒 (2).pdf" book2-pages.json
$ python3 scripts/phase0-2/build_inventory.py --outdir data/inventory
$ python3 scripts/validate_inventory.py
```

`build_inventory.py` 內建交叉核對（目錄↔正文），任何不一致會列入 `build-report.txt`；本次建置輸出為 `BOOK1 problems: NONE`、`BOOK2 problems: NONE`、`unassigned pages: NONE`。

## 三、建置交叉核對摘要（來源驗證證據）

| 核對項 | book-1 結果 | book-2 結果 |
| --- | --- | --- |
| 目錄條目頁碼 ↔ 正文起始頁 | 82／82 章全符（odd 頁眉法） | 146／146 定位頁全符（大字標題頁法） |
| 目錄頁碼單調性 | 通過 | 通過（214 列零違規） |
| 正文單元頁 ↔ 目錄頁（雙向） | 無單向遺漏 | 無單向遺漏（146＝146） |
| 頁碼連續性（頁腳/頁眉 vs 頁序） | book-1：全書 325 個 PDF 頁面之頁碼零失配 | book-2：頁腳頁碼＝PDF 頁序（一比一），標題頁 146 頁全符 |
| 分頁覆蓋 | 印刷頁 000–649 全覆蓋 | 印刷頁 1–478 全覆蓋 |

## 四、已知的限制

1. **圖片頁之正文狀態為 VLM 轉錄**（`image-only-vlm-transcribed`）：兩書末之照片／語錄／示意圖頁無文字層，其標題與內容由視覺模型（GLM-5V）多次高解析度轉錄並經頁面幾何定位交叉核對，仍需人工目視複核（見待審清單）。
2. 手寫簽名（book-2 第 458 頁授權聲明）之辨識結果為「江慶淇」「江嘉祁」，已以 300 DPI 高解析複核；唯簽名非印刷文字，建議權利文件面以原件為準。
3. 本驗證為結構性驗證；**不含**逐字轉錄校對（Phase 3 工作）、翻譯審查（Phase 4 工作）與權利清理（Phase 0 前置條件）。
