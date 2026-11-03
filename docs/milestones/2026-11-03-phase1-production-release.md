# Spiritual Awakening Library — Phase 1 正式發布里程碑

- **日期：** 2026-11-03（Australia/Brisbane）
- **專案：** Spiritual Awakening Library／靈性覺醒圖書館
- **網站：** https://spiritual-awakening-library.github.io/
- **儲存庫：** https://github.com/spiritual-awakening-library/spiritual-awakening-library.github.io
- **里程碑狀態：** Phase 1 雙語閱讀原型已正式部署；兩本書的全文出版及完整英譯尚未完成
- **整合方式：** 經 Pull Request 審查及 GitHub Actions 驗證後合併；正式發布由專案負責人明確授權並手動執行

## 1. 里程碑摘要

2026 年 11 月 3 日，Spiritual Awakening Library 完成 Phase 1 雙語數位閱讀原型的正式發布。專案從原先由 GitHub Pages 顯示的 README 說明頁，轉為透過 Next.js 靜態匯出及 GitHub Actions 發布的實際網站。

本階段的核心成果是建立可持續擴充的繁體中文／英文閱讀介面、兩本書的書目入口與完整結構性章節清單，以及清楚區分已發布內容和待完成翻譯的機制。**本里程碑不表示兩本書的完整正文或全部英文翻譯已公開。**

## 2. 功能交付範圍

- 建立繁體中文及英文首頁、兩本書的書目及目錄頁。
- 建立以段落識別碼為基礎的閱讀器、字級調整及閱讀位置保留機制。
- 初期內容包含《要開悟，讀這本書就夠了》一篇繁中閱讀原型及其標示為草譯的英文版本，以及《靈性覺醒》一篇繁中閱讀原型；尚未完成的英文版本不提供誤導性的切換連結。
- 提供兩本書的完整**結構性**目錄資料：第一本 127 個內容單元（其中 82 個編號章節）；第二本 168 個內容單元。這些數量代表清單盤點與結構驗證，不代表全文已刊載。
- 保留書籍封面、雙語導航、網站地圖、robots.txt 及靜態頁面輸出。
- 保留 Phase 0–0.2 已建立的來源盤點、結構資料與文件，不任意重寫書籍內容或翻譯。

## 3. 程式整合與部署紀錄

### PR #4 — Phase 1 雙語閱讀器與依賴相容性修復

- **PR：** https://github.com/spiritual-awakening-library/spiritual-awakening-library.github.io/pull/4
- **標題：** `feat: Phase 1 bilingual reader and dependency compatibility remediation`
- **功能分支：** `feat/sal-phase1-bilingual-reader-20261102`
- **實作 Commit：** `794b8c5`
- **合併 Commit（main）：** `d385e7b`
- **變更：** 51 個檔案（50 個新增、1 個既有檔案修改）
- **PR 驗證：** `validate-app` 及 `validate-foundation` 皆通過；無合併衝突。

### PR #5 — 正式 GitHub Pages 部署工作流

- **PR：** https://github.com/spiritual-awakening-library/spiritual-awakening-library.github.io/pull/5
- **標題：** `ci: add gated GitHub Pages production deployment workflow`
- **功能分支：** `feat/sal-pages-production-deploy-20261103`
- **實作 Commit：** `0cc475f`
- **變更：** 僅新增 `.github/workflows/deploy-pages.yml`（79 行）
- **PR 驗證：** `validate-app` 及 `validate-foundation` 皆通過；無合併衝突。

### 正式發布

專案負責人明確授權將 Phase 1 網站取代原有的 README 說明頁。GitHub Pages 的 **Build and deployment → Source** 改為 **GitHub Actions**，再從 `main` 手動執行 `Deploy Spiritual Awakening Library (Next.js static)`，輸入確認字串 `DEPLOY`。

提供的 GitHub Actions 執行畫面顯示 **build 與 deploy 均成功**，部署產物為 1 項；公開網站的截圖已顯示全站入口、繁體中文及英文首頁和兩本書封面，不再只是 README 說明頁。

**證據來源與核驗限制：** 本文件依專案負責人提供的本機指令輸出、PR／CI 畫面及正式部署截圖整理；原始日誌、完整截圖與當次工作流快照未隨本文附上，因此讀者無法僅憑本文獨立核驗全部結果。記錄中的測試與安全掃描結果僅適用於所列版本、執行環境、檢查範圍及當時的通告資料，不構成全面安全認證。

## 4. 發布前驗證紀錄

以下紀錄綜合 Windows 本機指令輸出、PR CI 畫面及正式部署畫面；不同驗證來源分別標示，不將其中一項的結果冒充另一項。

| 驗證項目 | 證據／結果 |
| --- | --- |
| Windows Node.js / npm / Python | Node.js v24.14.1、npm 10.6.0、Python 3.10.11 |
| `npm ci` | Windows 本機成功；依據 lockfile 安裝套件 |
| `npm run typecheck` | Windows 本機通過 |
| `npm run lint` | Windows 本機通過 |
| `python scripts/verify_foundation.py` | Windows 暫存後通過：80 個追蹤檔案、10 個 seed entries |
| `python scripts/validate_inventory.py` | 31/31 通過，0 warnings |
| `python scripts/validate_content.py` | 35 checks 通過 |
| `npm run build` | Next.js 16.4.4；14/14 靜態頁面產生完成 |
| `python scripts/validate_static.py` | 107 checks / 12 routes 通過 |
| `npm audit --omit=dev` | Windows 本機回報 0 vulnerabilities |
| PR #4 / #5 GitHub CI | 各有 2 項成功檢查，無合併衝突 |
| 正式發布工作流 | `build` 成功、`deploy` 成功 |
| 公開站點畫面 | 已顯示全站入口、繁中／英文首頁、兩本書封面及導覽內容 |

**驗證限制：** Inventory 和 Content 檢查是結構及程式規則檢查，不等於逐頁原著轉錄校對、英文翻譯審定或著作權審核；本里程碑也不宣稱完成全面滲透測試、全部瀏覽器及裝置的互動測試。

## 5. 依賴安全與相容性處理

- Next.js 和 `eslint-config-next` 升級至 **16.4.4**，ESLint 使用 **9.39.5**。
- 一度為使安全掃描歸零而加入的全域 minimatch 11 override，經獨立檢查發現會破壞若干 ESLint 外掛的舊 API 呼叫，因此已移除。
- 修正後按上游宣告的版本範圍解析 minimatch **3.1.5** 和 **10.2.6**；外掛定向相容性測試回報通過。
- **Production audit：** 0 項已知通告；**完整 npm audit：** 保留 16 項 Moderate 開發依賴警告，均與 `GHSA-g3hv-75wg-m249` 的相依傳播有關。
- 已記錄 minimatch 通告適用範圍與實際可達性的疑慮；**不將這 16 項警告描述為已修補或不存在**，也不以不相容的強制覆寫掩蓋警告。

參考紀錄：`docs/verification/2026-11-03-phase1-minimatch-remediation.md`。

## 6. 部署安全邊界

正式部署工作流 `.github/workflows/deploy-pages.yml` 採取以下限制：

1. 僅提供 `workflow_dispatch` 手動觸發。
2. `build` 和 `deploy` 都限制於 `refs/heads/main` 且輸入必須精確為 `DEPLOY`。
3. 工作流預設 `contents: read`；`pages: write` 與 `id-token: write` 僅授予 `deploy` job。
4. `deploy` 必須等待 `build` 成功；`build` 包含型別、lint、inventory、內容、production audit、靜態建置與路由驗證。
5. 發布 `out/` 靜態產物至 `github-pages` environment；不需要常駐 Next.js 伺服器。
6. 工作流加入 concurrency 控制，且未引入由普通 push 直接觸發正式部署的機制。

上述是設定及當次部署驗證結果，不代表未來所有部署都無需重新審查。

## 7. 已知限制與後續事項

- **全文內容：** 目前只發布初期示範閱讀篇章；逐步加入兩本書的完整繁中內容及經校對的忠實英譯。
- **文案狀態：** 已發布的全站入口頁仍出現「尚未公開部署／Prototype — not yet publicly deployed」等過時提示，應以獨立小型 PR 更新，避免與實際公開狀態矛盾。
- **翻譯標記：** 保留草譯警語與未完成翻譯的停用提示，直到完成內容校對及發布授權。
- **相依通告：** 持續追蹤 `GHSA-g3hv-75wg-m249` 的上游處理及相容修補；不要在未回歸測試前強推跨主要版本依賴。
- **使用者驗收：** 後續補充手機操作、字級儲存、語言切換保留段落位置、實際章節閱讀及跨瀏覽器檢查的發布後驗收紀錄。
- **發布流程：** 之後的章節與功能更新仍採隔離功能分支、PR、CI、人工審核與必要時明確授權的部署流程。

## 8. 里程碑結論

**Phase 1 已成功從程式原型進展到公開可存取的雙語數位圖書館網站。** 本階段交付的是經驗證的靜態閱讀介面、書目及章節結構與可控的發布管線；書籍全文、全部英文翻譯和全面的內容審校則留待後續階段完成。

本文件僅記錄已完成的工作與已知限制，不應被解讀為原著全文及英文翻譯皆已出版的聲明。
