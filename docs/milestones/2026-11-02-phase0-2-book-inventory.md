# 2026-11-02 — Phase 0.2 兩書完整內容清單（Complete Book Inventory）

**專案：** Spiritual Awakening Library／靈性覺醒圖書館（Project #9）
**分支：** `data/sal-complete-book-inventory-20261102`（基準 `main` @ `355c13b`；未推送 `main`；未建立 PR）

## 目標達成情形

| Phase 0.2 交付項 | 狀態 | 位置 |
| --- | --- | --- |
| 1. book-1 完整清單（CSV） | ✅ 127 列 | `data/inventory/book-1-inventory.csv` |
| 2. book-2 完整清單（CSV） | ✅ 168 列 | `data/inventory/book-2-inventory.csv` |
| 1–2 機器可讀結構化檔 | ✅ | `data/inventory/book-{1,2}-inventory.json`（含證據欄位、來源 SHA-256） |
| 3. 來源驗證報告 | ✅ | `docs/verification/2026-11-02-phase0-2-source-verification.md` |
| 4. 待審清單（不確定事項） | ✅ 21 項 | `docs/verification/2026-11-02-phase0-2-review-ledger.md` |
| 5. 自動驗證腳本 | ✅ 31 項檢查 | `scripts/validate_inventory.py` |
| 6. 驗證結果（實際執行） | ✅ 31/31 通過 | `docs/verification/2026-11-02-phase0-2-validation-results.md` |
| 7. 變更清單 | ✅ | `docs/verification/2026-11-02-phase0-2-change-manifest.md` |
| 8. 公開發布安全性審查 | ✅ | `docs/verification/2026-11-02-phase0-2-release-safety.md` |
| 9. Phase 0.2 里程碑文件 | ✅ | 本檔 |
| 10. 交付 ZIP＋SHA-256 | ✅ | `sal-phase0-2-deliverables-20261102.zip`＋`SHA256SUMS.txt`（隨交付提供） |

## 關鍵數據

- **book-1《要開悟，讀這本書就夠了》**（ISBN 978-957-43-9795-2，2022.04 初版）：82 章 開悟之一～八十二（印刷頁 014–598）＋序文 3 篇＋學員心得 8 篇＋圖版 31 項＋封面／目錄／版權頁；127 個內容單元；印刷頁 000–649 全覆蓋。
- **book-2《靈性覺醒》**（ISBN 978-957-43-9327-5，2022.3 初版）：手札 139 篇（全帶系列註記）＋自序＋感恩篇＋附錄四部（解析／祝福／專訪／心開意解）＋授權聲明與圖版 20 項；168 個內容單元；印刷頁 1–478 全覆蓋。
- 頁面幾何定則：book-1 為右開橫排雙頁拼版（右半＝偶數頁 2N−2）；book-2 直排、PDF 頁序＝印刷頁序（一比一）。二者均經全書頁碼零失配驗證。
- 目錄↔正文交叉核對：book-1 82/82；book-2 146/146 定位頁雙向零遺漏；無單調性違規。

## 決策與界限（本階段嚴守）

- 僅建立結構清單；**未**開始英文翻譯、網站實作或部署（Phase 1+ 工作）。
- 來源 PDF 未納入版本庫；僅記錄 SHA-256 與版面證據。
- 種子清單（Phase 0.1）保留未刪；其待確認項已實證補全（chapter-22＝169 等），差異紀錄於待審清單 D 節。
- 目錄與正文用字差異（ch22 分隔符、ch78「時」、book-2 p91 逗號等）一律保留雙方原文並列於待審清單，未擅自裁斷。
- 圖版頁（無文字層）以 VLM 轉錄並標記 `image-only-vlm-transcribed`；不虛補頁碼，僅記幾何推定位置。

## 驗證與證據

- `python3 scripts/validate_inventory.py` → 31/31 PASS（詳驗證結果文件，含原始輸出）。
- `python3 scripts/verify_foundation.py`（Phase 0.1 回歸）→ PASS，既有驗證未破壞。
- 建置交叉核對輸出：`BOOK1 problems: NONE`、`BOOK2 problems: NONE`、`unassigned pages: NONE`。

## 下一決策閘門

1. 人工複核待審清單 B 節（VLM 轉錄頁）與 A 節（編輯呈現決策）。
2. 書面權利清理（二書公開發布與翻譯許可）——硬性門檻，未完成前不公開全文。
3. 經核准後建立 PR（僅由維護者合併）；再啟動 Phase 1（網站骨架與單篇閱讀原型）。
