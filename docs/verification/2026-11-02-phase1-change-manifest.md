# Phase 1 — 變更清單（Change Manifest）

**日期：** 2026-11-02
**分支：** `feat/sal-phase1-bilingual-reader-20261102`（基準：`main` @ `1c514e2`）
**變更總數：** 50 個檔案（49 新增、1 修改、0 刪除）
（初次紀錄誤植為 48／46／2，本版依 `git diff --diff-filter` 實際輸出更正。）

## 修改既有檔案（1）

| 檔案 | 變更內容 |
| --- | --- |
| `.github/workflows/pr-validation.yml` | 擴充：保留原有兩項 Python 檢查（Phase 0.1 foundation、Phase 0.2 inventory）於 `validate-foundation` job；新增 `validate-app` job（npm ci → typecheck → lint → content 驗證 → 靜態匯出 → 匯出驗證）。仍為 PR 觸發、`contents: read` 唯讀權限、絕不部署。 |

## 新增檔案（49）

### 應用原始碼（Next.js App Router）

- `next.config.ts` — 雙模式配置（`output: 'export'`、`trailingSlash`、unoptimized images）
- `tsconfig.json` — 嚴格 TypeScript（strict、noImplicitAny）
- `eslint.config.mjs` — Next.js 標準規則（未降級）
- `postcss.config.mjs` — Tailwind CSS 4
- `package.json` / `package-lock.json` — 固定版本相依＋完整鎖定檔
- `.gitignore` — 排除 `out/`、`.next/`、`node_modules/`、機密與日誌
- `src/app/(landing)/layout.tsx`、`page.tsx` — 語言選擇落地頁（多根 layout A）
- `src/app/(library)/[locale]/layout.tsx` — 本地化樹根 layout B（lang 依 URL）
- `src/app/(library)/[locale]/page.tsx` — 本地化首頁
- `src/app/(library)/[locale]/books/[bookId]/page.tsx` — 全書目錄頁
- `src/app/(library)/[locale]/books/[bookId]/[entryId]/page.tsx` — 閱讀頁
- `src/app/globals.css` — 暖紙設計系統（Tailwind 4 @theme）
- `src/app/sitemap.ts`、`src/app/robots.ts` — 靜態 SEO 檔案
- `src/components/reader/ReadingBlock.tsx` — 核定段落分塊閱讀版面
- `src/components/reader/ReadingProgressTracker.tsx` — 可見段落追蹤（IO＋scroll）
- `src/components/reader/FontSizeControl.tsx` — 可調字型（useSyncExternalStore）
- `src/components/reader/EntryNavigation.tsx` — 目錄面板與前後導覽
  （無前後已出版單元時不輸出空 `<nav>` 地標）
- `src/components/reader/TranslationStatusNotice.tsx` — 原文／草譯狀態警語
- `src/components/library/BookCard.tsx`、`BookCover.tsx`、`ChapterDirectory.tsx`
- `src/components/navigation/SiteChrome.tsx`、`LanguageSwitcher.tsx`
- `src/lib/`：`i18n.ts`（UI 字串）、`routing.ts`、`seo.ts`（canonical/hreflang）、
  `inventory.ts`（Phase 0.2 清單載入）、`content.ts`（出版登記與內容載入）、
  `books.ts`、`reading-progress.ts`（客戶端段落 store）

### 內容與資料

- `content/book-1/zh-TW/chapter-01.json` —〈本源與宇宙次元〉24 段（來源驗證）
- `content/book-1/en/chapter-01.json` — 英文草譯 24 段（機器輔助、待人工審閱）
- `content/book-2/zh-TW/preface-01.json` —〈一份真實的路徑〉21 段（來源驗證）
- `data/books.json` — 書籍層展示元資料（僅驗證事實）
- `data/published.json` — 出版登記冊（路由生成之唯一依據）
- `public/covers/book-1-cover.png`、`book-2-cover.png` — 書封（未改動原樣）

### 驗證腳本

- `scripts/validate_content.py` — 內容完整性（35 checks）
- `scripts/validate_static.py` — 匯出路由／元資料／無 JS 內容（107 checks；
  hreflang 已強化為逐路由**雙向精確集合比對**，並附負面測試證據，
  見驗證結果 8.1）
- `scripts/phase1/extract_prototype.py` — 選文抽取程式（溯源保留）

### 工作流

- `.github/workflows/deploy-pages-preview.yml` — **未啟用**之純驗證工作流
  （僅 `workflow_dispatch`＋`PREPARE` 確認字串、僅限 `main` 分支、
  `contents: read`；完整驗證與靜態匯出步驟，**無任何部署動作或
  Pages 寫入權限**；文件載明日後須另行核准獨立部署工作流及回滾路徑）

### 文件

- `docs/milestones/2026-11-02-phase1-bilingual-reader.md` — 里程碑紀錄
- `docs/verification/2026-11-02-phase1-content-status.md` — 內容／翻譯狀態報告
- `docs/verification/2026-11-02-phase1-validation-results.md` — 驗證結果
- `docs/verification/2026-11-02-phase1-change-manifest.md` — 本文件
- `docs/verification/2026-11-02-phase1-release-safety.md` — 公開發布安全審查

## 分支內修訂（2026-11-02 最終安全修復）

上述清單之檔案總數不變（50：49 新增、1 修改）；本修復僅修訂分支內既有
檔案，未新增或刪除任何檔案：

- `.github/workflows/deploy-pages-preview.yml` — 移除
  `actions/deploy-pages@v4`、`upload-pages-artifact`、`configure-pages`、
  `pages: write`／`id-token: write` 與 `environment: github-pages`；
  新增 `main` 分支限制；確認字串 `DEPLOY`→`PREPARE`；保留完整驗證與
  靜態匯出步驟。詳見 release-safety 文件第 7 節。
- `docs/verification/2026-11-02-phase1-release-safety.md` — 更正過時數字
  （48→50、74→79，依 git 與驗證實際輸出）並同步工作流描述。
- `docs/verification/2026-11-02-phase1-change-manifest.md` — 本文件（同步工作流描述）。
- `docs/milestones/2026-11-02-phase1-bilingual-reader.md` — 同步工作流描述。
- `docs/verification/2026-11-02-phase1-validation-results.md` — 增列第 14 節修復後回歸複驗實際輸出。

## 未變更之既有資產（明確確認）

Phase 0–0.2 之全部文件、清單（`data/inventory/*`）、種子 CSV、既有腳本
（`verify_foundation.py`、`validate_inventory.py`、`scripts/phase0-2/*`）、
README，以及 GitHub Pages 之現行部署設定（main 分支 Jekyll）皆未更動。
