# Phase 1 — 雙語閱讀原型與安全部署準備（里程碑紀錄）

**日期：** 2026-11-02
**分支：** `feat/sal-phase1-bilingual-reader-20261102`（自最新驗證 `main` @ `1c514e2` 建立）
**狀態：** 實作完成，待獨立審閱；**未經核准不得部署**。

## 本階段完成事項

1. **雙模式 Next.js 應用**（App Router、TypeScript、`output: 'export'`）：
   - 開發模式：`next dev` 正常運行（GLM 預覽環境驗證通過）。
   - 生產模式：`next build` 完整靜態匯出至 `out/`（14 個頁面，GitHub Pages 相容）。
   - 不使用任何需要伺服器運行的功能（無 route handlers／server actions／runtime redirects）。
2. **資訊架構**（依 architecture v1.1 URL 契約）：
   - `/` 語言選擇落地頁（可檢索的雙語入口連結，不自動轉址）。
   - `/zh-TW/`、`/en/` 本地化首頁；`/{locale}/books/{bookId}/` 全書目錄；
     `/{locale}/books/{bookId}/{entryId}/` 閱讀頁（僅已出版內容生成路由）。
3. **清單驅動導覽**：兩書完整目錄（book-1 127 項、book-2 168 項）依 Phase 0.2
   驗證清單原始順序呈現，含單元類型、印刷頁碼、分區標題；未出版單元明確標示
   「尚未收錄」，不提供死連結。
4. **代表性閱讀選文**（每書一篇，均經來源驗證）：
   - book-1 `chapter-01`〈本源與宇宙次元〉（開悟之一；印刷頁 014–022；24 段）。
   - book-2 `preface-01`〈一份真實的路徑〉（慶淇悟得手札自序；印刷頁 25–31；21 段）。
5. **段落分塊閱讀版面**（`ReadingBlock`）：2–4 段落分組、暖紙配色、可調字型、
   可摺疊全書目錄、前後單元導覽；段落身分由 `<p id>` 承載，視覺分塊不定義段落
   身分；未新增任何原文不存在的裝飾性標題。
6. **段落保留語言切換**：切換目標於點擊當下依「閱讀焦區重疊最大」原則計算實際
   可見段落（非過時 hash）；zh↔en 段落 1:1 對映；未出版譯文顯示明確停用狀態，
   絕不靜默轉址。瀏覽器語言偏好不覆蓋明確的 URL 語言。
7. **英文草譯原型**（僅 book-1 chapter-01）：機器輔助草稿，標示
   `draft-machine-assisted` / `needs-human-review`，頁面可見警語；未冒充人工審定譯本。
8. **SEO 與靜態 HTML**：每頁正確 `lang`、自我參照 canonical、 reciprocal hreflang
   （僅指向實際存在的語言版本）、sitemap.xml（與匯出路由精確一致）、robots.txt；
   全文內嵌靜態 HTML（主內容不需 JavaScript）。
9. **CI 與部署安全**：
   - `pr-validation.yml` 擴充：PR 只讀權限、絕不部署；新增 npm ci → typecheck →
     lint → 內容驗證 → 靜態匯出 → 匯出驗證，並保留 Phase 0.1/0.2 全部既有檢查。
   - 新增 `deploy-pages-preview.yml`：**僅 `workflow_dispatch` 手動觸發＋`PREPARE`
     確認字串，且僅限 `main` 分支**，未啟用；為**純驗證工作流**（完整驗證＋
     靜態匯出，無任何部署動作、無 Pages 寫入權限）；現行 Jekyll 發布
     （main 分支 README）保持不變；文件載明日後須另行核准之獨立部署工作流
     與回滾路徑。

## 驗證證據摘要

| 檢查 | 結果 |
| --- | --- |
| `npm ci`（乾淨安裝） | 通過（added 357 packages；lockfileVersion 3） |
| `tsc --noEmit` | 通過（0 錯誤） |
| `eslint .` | 通過（0 錯誤 0 警告） |
| Phase 0.1 foundation validation | 通過（79 tracked files） |
| Phase 0.2 inventory validation | 通過（31/31 checks） |
| Phase 1 content validation | 通過（35 checks） |
| `next build`（靜態匯出） | 通過（14 pages） |
| Phase 1 static export validation | 通過（107 checks；hreflang 為雙向精確集合比對，含負面測試證據） |
| 瀏覽器 E2E（開發模式） | 通過（語言切換保留段落、字型持續、404、無主控台錯誤） |
| 瀏覽器 E2E（純靜態 `out/`） | 通過（段落切換 `#p-016` zh↔en、草譯警語可見） |

詳見 `docs/verification/2026-11-02-phase1-validation-results.md`。

### 複驗補充（2026-11-02）

完整重跑驗證套件時發現兩項問題並已修正：

1. 驗證結果文件初次紀錄含佔位符數字（`npm ci` 套件數、Phase 0.1 檔案數），
   已以實際輸出全數更正。
2. `validate_static.py` 的 hreflang 檢查為單向（可能空轉通過），已強化為
   逐路由雙向精確集合比對，並以兩個負面測試（移除必要 alternate、偽造
   未出版語言 alternate）證明檢查確實會失敗。
3. `EntryNav` 於無前後已出版單元時不再輸出空 `<nav>` 地標（無障礙語意改善）。
4. （最終安全修復）`deploy-pages-preview.yml` 移除 `deploy-pages@v4`、
   `pages: write`／`id-token: write`、`environment: github-pages`、
   `configure-pages` 與 `upload-pages-artifact`，成為純驗證工作流並新增
   `main` 分支限制；release-safety 文件過時數字（48→50、74→79）依 git
   實際輸出更正。修復後 8 項驗證全數重跑通過（見驗證結果第 14 節），
   未發生任何部署。

網站實際輸出（hreflang 集合、路由、內容）經人工核對皆正確；上述均為
驗證工具與語意品質之強化，非網站功能缺陷。

## 未完成／後續階段事項

- 全書正文逐字轉錄與校對（Phase 3）；全部英譯與人工審校（Phase 4）。
- Book 2 選文之英文版（本階段為明確停用狀態）。
- 客製網域未確認，一切以 `spiritual-awakening-library.github.io` 為基準。
- 正式公開部署：待書面授權與使用者明確核准（見 release-safety 文件）。
- 深色模式刻意未實作（核定閱讀風格為單一暖紙淺色主題）。

## 停止條件觸發紀錄

本階段未觸發任何停止條件：無覆蓋已驗證內容、未替換現行部署、所有靜態路由均
可生成、譯文段落對映可靠、無未解決來源差異影響出版內容、所有必要測試通過、
無機密進入公開包。
