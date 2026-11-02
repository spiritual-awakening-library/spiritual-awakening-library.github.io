# Phase 1 — 驗證結果（Validation Results）

**日期：** 2026-11-02（完整複驗）
**分支：** `feat/sal-phase1-bilingual-reader-20261102`
**環境：** Node 20+／npm、Python 3.12、Next.js 16.1.3（靜態匯出模式）

以下所有結果皆為**實際執行**之輸出；無任何檢查被停用或降級以換取通過。
初次紀錄中 `npm ci` 一節留有佔位符數字，本版為全項目重新實際執行後之修訂。

## 1. 乾淨相依安裝

```
$ rm -rf node_modules out .next
$ npm ci --no-fund --no-audit
added 357 packages in 9s

npm warn install-scripts 1 package has install scripts not yet covered by allowScripts:
npm warn install-scripts   sharp@0.34.5 (install: node install/check.js || npm run build)
```

（`sharp` 為 Next.js 之可選影像優化套件；本站靜態匯出採 `images.unoptimized`，
不安裝其建置腳本不影響任何功能。lockfile 版本 3，`npm ci` 可完整重現。）

## 2. TypeScript 型別檢查

```
$ npm run typecheck             # tsc --noEmit
（無輸出，exit 0）
```

## 3. ESLint

```
$ npm run lint                  # eslint .
（無輸出，exit 0；0 errors, 0 warnings）
```

## 4. Phase 0.1 基礎驗證（既有，未修改）

```
$ python3 scripts/verify_foundation.py
PASS: 79 tracked files checked; 10 seed entries structurally valid.
LIMITATION: Not a complete chapter inventory, translation review, or full security audit.
```

## 5. Phase 0.2 清單驗證（既有 31 項，全數保留）

```
$ python3 scripts/validate_inventory.py
checks: 31; pass: 31; fail: 0; warnings: 0
PASS: complete book inventories are structurally valid.
LIMITATION: structural validation only; not transcription review, translation review, or rights clearance.
```

## 6. 內容完整性（Phase 1 新增）

```
$ python3 scripts/validate_content.py
content validation PASSED: 35 checks
```

涵蓋：出版登記 ↔ 清單一致、題名／系列／印刷頁比對、來源 SHA-256 比對、
段落 ID 循序唯一非空、zh↔en 段落集合逐段相等、草譯狀態欄位強制存在、
書封檔案存在。

## 7. Next.js 生產靜態匯出

```
$ npm run build
✓ Compiled successfully
✓ Generating static pages (14/14)

Route (app)
┌ ○ /                        ├ ● /[locale]  → /zh-TW, /en
├ ● /[locale]/books/[bookId] → 4 pages
├ ● /[locale]/books/[bookId]/[entryId] → 3 pages
├ ○ /robots.txt  ├ ○ /sitemap.xml  ├ ○ /_not-found
```

（14 頁：落地頁、兩語首頁、4 書目錄頁、3 閱讀頁〔zh book-1、zh book-2、
en book-1〕、robots.txt、sitemap.xml、_not-found。未出版之
`/en/books/book-2/preface-01/` 不生成路由。）

## 8. 匯出路由與元資料驗證（Phase 1 新增；本複驗已強化）

```
$ python3 scripts/validate_static.py
static export validation PASSED: 107 checks (12 routes)
```

涵蓋：匯出路由集合精確等於預期（含「不存在的英文 book-2 選文路由不得出現」）、
每頁 `lang` 正確（`zh-Hant`／`zh-Hant-TW`／`en`）、canonical 自我參照、
**hreflang 雙向精確集合比對**（見下）、sitemap 與路由集合一致、robots.txt、
閱讀頁全文存在於靜態 HTML（無需 JS）、草譯警語存在於靜態 HTML、書封存在。

### 8.1 hreflang 檢查之強化（本次複驗發現並修正）

初版腳本對 hreflang 僅做單向檢查（「存在的 alternate 必須指向已匯出路由」），
若頁面完全沒有輸出 hreflang 亦會空轉通過。網站實際輸出經人工核對為正確
（React 將屬性序列化為 `hrefLang`，HTML 屬性不分大小寫，功能正常），但檢查
強度低於宣稱，故已改寫為**逐路由精確集合比對**：

- 有譯文之頁面（落地頁、首頁、目錄頁、book-1 選文）：必須宣告完整
  reciprocal 集合（self + sibling + `x-default`）。
- 未出版譯文之頁面（book-2 選文）：**不得**出現 `en` alternate。

**負面測試證據**（證明檢查不再空轉）：

```
（情境一：自 en 選文頁移除 zh-TW alternate）
FAIL: /en/books/book-1/chapter-01/: hreflang set mismatch —
      missing={'zh-TW': 'https://…/zh-TW/books/book-1/chapter-01/'} unexpected={}
static export validation FAILED: 1 failure(s) across 107 checks

（情境二：在 book-2 選文頁偽造 en alternate）
FAIL: /zh-TW/books/book-2/preface-01/: hreflang set mismatch —
      missing={} unexpected={'en': 'https://…/en/books/book-2/preface-01/'}
static export validation FAILED: 1 failure(s) across 107 checks

（還原後）
static export validation PASSED: 107 checks (12 routes)
```

## 9. 瀏覽器檢查（agent-browser；開發模式 `next dev` :3000 與純靜態 `out/` :4173）

| 項目 | 結果 |
| --- | --- |
| 落地頁雙語入口 | ✅ `/zh-TW/`、`/en/` 連結可檢索且可達；`lang="zh-Hant"` |
| 本地化首頁（zh／en） | ✅ 導覽、館藏卡、書封（描述性 alt）、關於本館／來源與驗證區塊 |
| 目錄頁 | ✅ book-1 127 項完整目錄、分區標題、可捲動容器、已出版連結 |
| 閱讀頁段落分塊 | ✅ 24 段（book-1）／21 段（book-2）；視覺分塊 2–4 段；`<p id>` 承載段落身分 |
| 段落保留語言切換（zh→en，開發模式） | ✅ 焦區段落 `p-018` → `/en/…#p-018`，落地後 `p-018` 仍在閱讀焦區（12–45% 帶） |
| 段落保留語言切換（en→zh，純靜態） | ✅ `p-016` → `/zh-TW/…#p-016`，內容對應（"Are you any different from your own tongue?" ↔ 「你跟你身上的舌頭有沒有兩樣？」） |
| 未出版譯文之切換鈕 | ✅ `aria-disabled` 停用狀態＋提示「本篇英文翻譯尚未完成，無法切換。」；頁首無任何誤導性 `/en/` 連結 |
| 未出版路由 | ✅ `/en/books/book-2/preface-01/` → 404 頁（開發與靜態模式皆確認） |
| 字型調整 | ✅ `--reading-size` 1.0625rem → 1.5rem；`localStorage[sal-reading-size-index]` 持久；跨重載與跨語言切換後仍生效 |
| 全書目錄（閱讀頁） | ✅ 原生 `<details>` 摺疊，展開後 127 項，現行單元 `aria-current` |
| 行動版（390×844） | ✅ 無水平溢出（scrollW 390 = clientW 390） |
| Sticky footer | ✅ 1280×4000 視窗實測 footer 貼底（footerBottom = 4000 = innerHeight）；內容溢出時自然推下 |
| 主控台錯誤 | ✅ 逐頁檢查，無 error／warning（僅開發模式固有之 HMR／DevTools 訊息） |
| 空導覽地標（本複驗修正） | ✅ 原型階段每書僅一篇選文、無前後單元時，`EntryNav` 不再輸出空 `<nav>` 地標 |

## 10. 視覺設計審查（VLM 截圖審視：落地頁／首頁／閱讀頁／行動版）

- 總評：「完成度非常高、美學素養極佳」；暖紙配色、字級層級、留白與
  行動版邊距均獲正面評價。
- VLM 回報行動版左下角懸浮按鈕遮字——經查為 **Next.js 開發模式專屬之
  Dev Tools 指示器**，純靜態匯出（:4173）實測 `floatingButtons: 0`，
  不存在於生產環境；判定為開發環境誤報，非產品缺陷。
- 追蹤觀察（非缺陷）：書封卡片左側作者簡介區在小螢幕縮放下偏小；
  閱讀頁導覽刻意精簡（可經 Logo 返回首頁）。

## 11. 基本無障礙檢查

- 語意結構：`main`／`nav`／`header`／`footer`／`article`／`section`／`details`。
- 跳至內容連結（skip link）、麵包屑、現行單元 `aria-current`。
- 圖片均有描述性 alt（含書封內容描述）；裝飾符號 `aria-hidden`。
- 鍵盤可達：互動元素皆為原生 `a`／`button`／`details`；focus-visible 樣式。
- 對比：正文 `#35312a` 於 `#fffdf6`（≈12:1）；次要文字 `#6f6555`（≈6.4:1）。
- 語言切換停用狀態不具 href（鍵盤自然跳過），附 `sr-only` 說明。
- `lang` 屬性：zh 樹 `zh-Hant-TW`、en 樹 `en`、落地頁 `zh-Hant`（皆為有效
  BCP-47 標籤，且由靜態 HTML 直接宣告，無需 JS）。

## 12. 公開發布安全審查

見 `2026-11-02-phase1-release-safety.md`（無機密、無原始 PDF、授權狀態、
部署隔離）。

## 13. 變更檔案範圍檢查

```
$ git diff origin/main...feat/sal-phase1-bilingual-reader-20261102 --name-only | wc -l
50
（49 新增、1 修改〔僅 .github/workflows/pr-validation.yml〕、0 刪除）
```

見 `2026-11-02-phase1-change-manifest.md`。Phase 0–0.2 全部檔案、清單、
腳本與 README 均未更動；GitHub Pages 現行部署設定未更動。

## 14. 最終安全修復後之回歸複驗（2026-11-02）

修復內容：`deploy-pages-preview.yml` 移除全部部署能力（詳見
release-safety 文件第 7 節）。修復後自乾淨狀態完整重跑第 1–8 節全部
驗證，實際輸出如下，與修復前紀錄**逐項一致**（證明內容、翻譯、閱讀器
行為、雙語路由與 SEO 元資料均未變動）：

```
$ rm -rf node_modules out .next && npm ci --no-fund --no-audit
added 357 packages in 9s

$ npm run typecheck                 # tsc --noEmit
（無輸出，exit 0）

$ npm run lint                      # eslint .
（無輸出，exit 0；0 errors, 0 warnings）

$ python3 scripts/verify_foundation.py
PASS: 79 tracked files checked; 10 seed entries structurally valid.

$ python3 scripts/validate_inventory.py
checks: 31; pass: 31; fail: 0; warnings: 0
PASS: complete book inventories are structurally valid.

$ python3 scripts/validate_content.py
content validation PASSED: 35 checks

$ npm run build
✓ Compiled successfully
✓ Generating static pages (14/14)   ／靜態匯出至 out/

$ python3 scripts/validate_static.py
static export validation PASSED: 107 checks (12 routes)
```

工作流安檢（本節新增，非 YAMl 註釋之活動指令為零）：

```
$ grep -vE "^\s*#" .github/workflows/deploy-pages-preview.yml \
    | grep -cE "deploy-pages@|upload-pages-artifact|configure-pages|pages:\s*write|id-token|environment:"
0        # 非註釋行中無任何部署動作／寫入權限／environment

$ grep -h "uses:" .github/workflows/*.yml | sort -u
        uses: actions/checkout@v4
        uses: actions/setup-node@v4
        uses: actions/setup-python@v5
        # 僅三個唯讀準備動作，無 deploy-pages／upload-pages-artifact／configure-pages
```

**明確聲明：本次修復未執行任何部署、未上傳任何成品、未更動儲存庫
Pages 設定。**
