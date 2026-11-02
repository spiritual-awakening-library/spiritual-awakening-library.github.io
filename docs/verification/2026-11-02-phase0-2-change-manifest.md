# Phase 0.2 — 變更清單（Change Manifest）

**日期：** 2026-11-02　**分支：** `data/sal-complete-book-inventory-20261102`　**基準：** `main` @ `355c13b`

## 一、新增檔案（All new files; no existing file modified except the protocol addendum）

| 路徑 | 內容 | 大小 |
| --- | --- | --- |
| `data/inventory/book-1-inventory.csv` | book-1 完整內容單元清單（127 列，UTF-8 BOM） | ~40 KB |
| `data/inventory/book-1-inventory.json` | 同上（機器可讀結構化檔，含 toc/body 證據欄位與來源 SHA-256） | ~106 KB |
| `data/inventory/book-1-page-map.json` | book-1 印刷頁 000–649 逐頁歸屬（衍生核算檔） | ~15 KB |
| `data/inventory/book-2-inventory.csv` | book-2 完整內容單元清單（168 列） | ~46 KB |
| `data/inventory/book-2-inventory.json` | 同上（結構化檔） | ~147 KB |
| `data/inventory/book-2-page-map.json` | book-2 印刷頁 1–478 逐頁歸屬 | ~11 KB |
| `scripts/validate_inventory.py` | Phase 0.2 自動驗證腳本（31 項檢查；無第三方依賴） | — |
| `scripts/phase0-2/README.md` | 分析管線說明 | — |
| `scripts/phase0-2/extract_pages.py` | 逐頁座標文字層萃取（PyMuPDF；直排分欄重排） | — |
| `scripts/phase0-2/b2_analyze.py` | book-2 頁腳頁碼／大字標題／欄位分析函式庫 | — |
| `scripts/phase0-2/b2_toc_body.py` | book-2 目錄重建與正文標題頁掃描 | — |
| `scripts/phase0-2/b2_crosscheck.py` | book-2 目錄↔正文交叉核對 | — |
| `scripts/phase0-2/b1_analyze.py` | book-1 拼版半頁／頁眉分析 | — |
| `scripts/phase0-2/b1_toc_scan.py` | book-1 直排目錄解析與頁眉序列掃描 | — |
| `scripts/phase0-2/build_inventory.py` | 兩書清單建置（內建交叉核對與分頁覆蓋核算） | — |
| `docs/verification/2026-11-02-phase0-2-source-verification.md` | 來源驗證報告 | — |
| `docs/verification/2026-11-02-phase0-2-review-ledger.md` | 待審清單與不確定事項 | — |
| `docs/verification/2026-11-02-phase0-2-validation-results.md` | 驗證結果（實際執行指令與輸出） | — |
| `docs/verification/2026-11-02-phase0-2-change-manifest.md` | 本檔 | — |
| `docs/verification/2026-11-02-phase0-2-release-safety.md` | 公開發布安全性審查 | — |
| `docs/milestones/2026-11-02-phase0-2-book-inventory.md` | Phase 0.2 里程碑文件 | — |

## 二、修改檔案（僅一項，附加式；未刪除或改寫任何既有內容）

| 路徑 | 變更 | 理由 |
| --- | --- | --- |
| `docs/editorial/source-inventory-protocol.md` | 文末**附加**〈Phase 0.2 狀態附記〉一節（原全文保留未動） | 原文「No complete book-2 chapter inventory has been verified yet」於本階段完成後需更新狀態；採附加而非改寫，以保留協議沿革 |

## 三、未變更項目（明示）

- `data/chapter-inventory-SEED-INCOMPLETE.csv` — 依協議保留（Phase 0.1 驗證依賴其存在；已驗證未破壞）。
- `scripts/verify_foundation.py`、`.github/workflows/pr-validation.yml`、GitHub Pages 部署設定、README — 完全未動。
- 來源 PDF 與封面檔 — 未納入儲存庫（僅記錄 SHA-256 於 JSON 與報告）。
- 無任何既有檔案被刪除或重新命名。

## 四、交付 ZIP（審查用封存）

- `sal-phase0-2-deliverables-20261102.zip`（分支內容之 sanitized 封存，不含來源 PDF；含本清單、驗證報告、資料檔與腳本）。
- SHA-256：見封存旁之 `SHA256SUMS.txt`（隨交付一併提供；值記錄於交付說明）。

## 五、Git 操作紀錄

- 分支 `data/sal-complete-book-inventory-20261102` 自 `main`（`355c13b`）建立。
- 僅提交至此分支；**未**推送 `main`、**未**建立或合併 Pull Request（依任務指示，PR 需明確核准後方可建立）。
