# Phase 1 — 公開發布安全審查（Public-Release Safety Review）

**日期：** 2026-11-02（同日最終安全修復版）
**審查範圍：** `feat/sal-phase1-bilingual-reader-20261102` 分支全部 50 個變更檔案
＋交付 ZIP 內容。
（50 依 `git diff --name-only $(git merge-base main HEAD) HEAD | wc -l`
實際輸出；初次紀錄誤植為 48，僅作歷史紀錄保留於變更清單文件，本版更正。）

## 1. 機密與憑證

- ✅ `verify_foundation.py` 之密鑰掃描（GitHub token、fine-grained token、
  OpenAI key、私鑰）對全部 79 個追蹤檔案執行通過。
  （79 依 `git ls-files | wc -l` 與 `verify_foundation.py` 實際輸出
  「PASS: 79 tracked files checked」；初次紀錄誤植為 74，本版更正。）
- ✅ `.gitignore` 排除 `.env*`、`*.log`、`node_modules/`、`.next/`、`out/`。
- ✅ 追蹤檔案中無 `.npmrc`、SSH 金鑰、API 憑證。
- ✅ 工作流無任何 secret 引用；PR 驗證僅 `contents: read`。

## 2. 原始來源檔案

- ✅ 權威來源 PDF（4 個）**未進入**儲存庫或交付 ZIP。
- ✅ 儲存庫僅含：已驗證清單（Phase 0.2）、兩篇選文之轉錄文字、書封 PNG。
- ✅ 選文內容檔記錄來源 SHA-256，與清單證據一致（`validate_content.py` 檢查）。

## 3. 著作權與授權狀態

- 著作權由原作者（江慶淇）保留；網站頁尾明示「原型階段、尚未公開部署、
  正式授權條款以書面授權為準」。
- **書封與選文之納入依據**：計畫主持人於 Phase 1 任務指示中明確要求
  「使用兩本原始書封」與「每書一篇代表性驗證選文」（2026-11-02 對話紀錄）。
  此為計畫主持人的權利決策紀錄；**正式的書面權利清理文件仍未完成**，
  全書出版（Phase 3+）前必須補齊（架構 v1.1 硬性門檻）。
- 本審查不構成法律意見；權利狀態變更時須重新審查。

## 4. 部署隔離（不影響現行發布）

- ✅ 現行 https://spiritual-awakening-library.github.io/ 為 main 分支 Jekyll
  （README 渲染）；本分支未觸碰任何 Pages 設定。
- ✅ `pr-validation.yml`：PR 觸發、唯讀權限、無部署步驟。
- ✅ `deploy-pages-preview.yml`（2026-11-02 最終安全修復後）：**純驗證工作流**
  ——僅 `workflow_dispatch` 手動觸發＋人工輸入 `PREPARE` 確認字串，且僅可於
  核准之 `main` 分支執行（guard 檢查 `github.ref`）。全工作流僅
  `contents: read`；**不含任何部署動作**（已移除 `deploy-pages`、
  `upload-pages-artifact`、`configure-pages`），無 `pages: write`／
  `id-token: write`、無部署 `environment`。即使誤觸發，亦不具備任何
  可影響線上站台之權限。**正式部署日後須另行建立並核准獨立之部署
  工作流**（詳見第 7 節）。
- ✅ 無並行競爭部署：`concurrency` 群組 `pages-deployment-preparation`。
- ✅ 回滾路徑已文件化：Settings → Pages → Source 切回
  「Deploy from a branch（main／root）」，Jekyll 站台即恢復。

## 5. 內容呈現誠實性

- ✅ 草譯（機器輔助、未經人工審閱）於頁面可見警語與 metadata 明確標示，
  不冒充核定譯本（per-entry release gate 未達之項目不標記為已審）。
- ✅ 未出版單元不生成路由、不提供連結、不被 sitemap／hreflang 引用。
- ✅ 編按（館方導讀）標示「草稿・待審」，與原文視覺及文字明確區隔。
- ✅ 作者之靈性主張以第一人稱原文呈現，未經改寫、潤飾或「科學化」轉述；
  客觀性風險由「見證／信念表述」之文體標示處理（見證類單元維持原分類）。

## 6. 交付包裝

- 交付 ZIP 為**去敏原始碼**（working tree，排除 `node_modules/`、`out/`、
  `.next/`、`.git/`、`.env*`、日誌），附 SHA-256。
- ZIP 內含本審查與全部驗證文件，供獨立複核。

## 7. 最終安全修復紀錄（2026-11-02）

應計畫主持人指示進行之窄範圍修復，變更僅及於必要檔案：

1. **移除實際部署能力**：`deploy-pages-preview.yml` 原含
   `actions/deploy-pages@v4`、`pages: write`、`id-token: write`、
   `environment: github-pages`、`configure-pages` 與
   `upload-pages-artifact`，不符「未經核准不得部署」之要求。已全數
   移除，改為純驗證工作流（保留完整驗證與靜態匯出步驟），新增
   `main` 分支限制，確認字串由 `DEPLOY` 改為 `PREPARE` 以免誤導。
   未更動儲存庫 Pages 設定，未建立任何替代部署機制。
2. **更正過時數字**：審查範圍 48→50（git 實際輸出）、密鑰掃描範圍
   74→79（git 與 `verify_foundation.py` 實際輸出）；歷史誤植僅在明確
   標注為歷史紀錄時保留。
3. **回歸複驗**：修復後完整重跑 8 項驗證（`npm ci`、typecheck、lint、
   Phase 0.1／0.2、content、build、validate_static），全數通過且輸出
   與修復前一致（詳見驗證結果文件第 14 節）。
4. **明確聲明：本次修復未發生任何部署**；正式公開部署日後須另行建立
   並核准專屬部署工作流（含 `pages: write`＋`id-token: write`、
   `environment: github-pages` 保護規則，及 Settings → Pages 來源切換），
   該工作流不在本分支範圍內。

## 結論

本分支可安全進入 PR 審閱。**公開部署須另行明確核准**；核准前建議補齊：
(a) 書面權利清理確認；(b) 以本分支於本機或 Actions 產物做最終煙霧測試；
(c) 使用者對 PR 內容之人工審閱。
