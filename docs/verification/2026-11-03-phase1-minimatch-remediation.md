# Phase 1 依賴安全與 minimatch 相容性修正報告

日期：2026-11-03（Australia/Brisbane）。結論：建議採用本次未提交修補，移除全域 minimatch major-version override，保留 Next.js 16.4.4 與既有 ESLint 9 工具鏈，並明確接受及追蹤尚未釐清的開發依賴通告。

## 1. 基準與交付身分

- 唯一實作基準為使用者附件 ZIP，非線上 main 或重新下載的原始碼。
- ZIP SHA-256：`baadc2bf00c21e471d0273b8d411140ab9c269d6dcad50b0858499739d8dda8c`，與附件校驗檔一致；該檔列出的 12 個個別檔案雜湊也全部一致。
- ZIP comment 實際含有 `1e0e20eaefd50a8f20448a1ec97720bcf9d4d279`，與使用者提供的基準 commit 相同。這確認封存檔的來源標記，並非另外對 GitHub 遠端歷史作簽章驗證。
- 基準分支：`feat/sal-phase1-bilingual-reader-20261102`。
- 原始 ZIP 沒有 `.git`。僅在本機測試副本建立暫存 Git index，供原有 `git ls-files` 基礎驗證使用；未建立任何 Git commit。交付為 **相對上述基準的未提交修補**，沒有新的 commit hash。
- 未對公開儲存庫寫入、push、建立 PR、merge 或部署。

## 2. 實作決策與精確範圍

只修改 `package.json`、`package-lock.json`，並新增本報告。其他 78 個原有檔案逐位元組保持一致；完整原始碼包保留原本全部 80 個來源及文件檔案，另含本報告，共 81 個檔案。

`package.json` 唯一實質變更為移除：

```json
"overrides": { "minimatch": "^11.0.4" }
```

未新增其他 override、audit 忽略設定、停用規則或 ESLint 設定變更。使用 `npm install --package-lock-only --ignore-scripts` 重新解析既有 lockfile；沒有刪掉 lockfile 後全面升級，也沒有使用 `npm audit fix --force`。

本機 npm 11.9.0 重新序列化時省略了 38 個未更換套件的 `libc` 限制欄位；已保留基準相同套件的原始完整 metadata，再以最終 lockfile 執行 `npm ci`。最終比較：既有且仍存在的每個 lock package record 均與基準完全一致；新增 26 筆、移除 2 筆，共由 430 筆變為 454 筆（含根專案）。新增項目包含相容的巢狀 minimatch、其依賴，以及 npm 補齊的 optional WASM 依賴；移除全域 minimatch 11 與其專用的 `@isaacs/nonrecursive-glob-match`。這些細節可在 `DEPENDENCY-VERSIONS.csv` 核對。

書籍原文、英文草譯、段落 ID、雙語路由、inventory CSV/JSON、`src/`、`public/`、閱讀器設計、原有腳本與 GitHub Actions 皆未更動。未加入沉浸式閱讀。既有 Phase 0–0.2 文件與歷史依賴升級紀錄原樣保留。

**歷史紀錄更正：** `2026-11-02-phase1-dependency-upgrade.md` 的「全域 override 已完整修復」僅反映當時 scanner 歸零，不能代表外掛 API 相容。本報告取代該紀錄對 override 安全性的判斷；其餘歷史測試並非本次重新執行的證據。

## 3. 版本前後對照

| 套件／路徑 | 基準 | 修正後 |
|---|---|---|
| next | 16.4.4 | 16.4.4 |
| eslint-config-next | 16.4.4 | 16.4.4 |
| eslint | 9.39.5 | 9.39.5 |
| react / react-dom | 19.2.3 / 19.2.3 | 不變 |
| typescript | 5.9.3 | 5.9.3 |
| minimatch，全域 | 11.0.4，強制覆寫所有消費者 | 移除 |
| eslint、@eslint/config-array、@eslint/eslintrc 下的 minimatch | 各被強制為 11.0.4 | 各依 `^3.1.5` 解析為 3.1.5 |
| import、react、jsx-a11y plugins 下的 minimatch | 各被強制為 11.0.4 | 各依 `^3.1.2` 解析為 3.1.5 |
| typescript-estree 下的 minimatch | 被強制為 11.0.4 | 依 `^10.2.2` 解析為 10.2.6 |
| minimatch 3 的 brace-expansion | 無此鏈 | 1.1.21 |
| 現存 brace-expansion 5 | 5.0.12 | 5.0.12 |
| sharp | 0.35.5 | 0.35.5 |
| Next.js 內部 postcss | 8.5.23 | 8.5.23 |
| 根 postcss | 8.5.32 | 8.5.32 |

實際查詢 npm 發布資訊確認上述指定版本存在；當時 minimatch 3 / 10 / 11 各線最新分別為 3.1.5 / 10.2.6 / 11.0.4，沒有可自然解析的 3.x 或 10.x 新修補版。三個外掛最新版本仍為 import 2.32.0、react 7.37.5、jsx-a11y 6.10.2，且 peer 範圍只支援到 ESLint 9 系列。因此未遷移 ESLint 10，也未強推 typescript-estree 至未宣告支援的 minimatch 11。

保留 Next.js 安全修補的證據為：Next.js 與 eslint-config-next、sharp、postcss 的 lock records 完全不變；最終 production audit 為零。Next.js GitHub release tag 頁本次擷取失敗，未據此聲稱讀過該版本 release notes；版本與依賴以實際 npm metadata 及 lockfile 交叉核對。這不表示未來不會有新通告。

## 4. 獨立確認原 override 不安全

先前 GLM 報告的兩個核心發現已獨立動態驗證：

1. minimatch 11 的 CommonJS 模組是物件，不能直接當函式呼叫；頂層 `makeRe` 是 `undefined`。
2. import plugin 的 `no-internal-modules` 初始化 allow/forbid glob 時呼叫頂層 `makeRe`；react plugin 的 `jsx-pascal-case` 使用 `ignore` glob 清單時直接呼叫模組。此規則的實際選項名稱是 **ignore**，不應沿用先前報告部分段落中的 allow 稱呼。
3. jsx-a11y 的 `mayContainChildComponent` 及 `mayHaveAccessibleLabel` 確實直接呼叫 interop 後的 default export。透過 `label-has-associated-control` 的巢狀控制項路徑已動態重現 TypeError，補齊先前未完成的判定。

基準 `npm ls minimatch` 及 `npm explain minimatch` 都 exit 0，仍無法證明 API 相容。基準一般 `npm run lint` 也 exit 0，但上述三個外掛的定向測試均成功重現預期的 TypeError。

修正後使用實際安裝的 ESLint Linter API 執行同樣規則：

| 外掛與測試 | 刻意違規範例 | 合規範例 | 修正後結果 |
|---|---|---|---|
| import/no-internal-modules，forbid `**/internal/**` | `library/internal/item` | `library/public` | 違規被偵測；合規無訊息 |
| react/jsx-pascal-case，ignore `Special*` | `<Bad_name />` | `<Special_name />` | 違規被偵測；glob 例外生效 |
| jsx-a11y/label-has-associated-control，assert nesting | `<label>Name<span /></label>` | `<label>Name<input /></label>` | 違規被偵測；有效巢狀控制項被接受 |

沒有把「沒有拋錯」當作充分測試：每組同時檢查應報錯與不應報錯的結果。定向規則只在外部測試 fixture 啟用，沒有更動應用的 ESLint 設定。

也實測目前 Next.js 設定的檔案選取：`.tsx` 與 `.ts` 來源會被納入，`out/`、`.next/`、`node_modules/` 會被忽略。另用獨立 flat config 驗證 files glob、正向 ignore 與 `!fixture/generated/keep.js` 重新納入；刻意植入 `debugger` 驗證納入／排除確實影響規則執行。

目前設定沒有啟用上述三個特定規則；jsx-a11y/alt-text 則有啟用。這解釋一般 lint 能通過，不能推論未來啟用其他規則也安全。完整相容性 harness：基準 7/7 通過（其中三組成功重現預期失敗），修正後 7/7 通過（執行正反案例）。

另對 minimatch 3.1.5 與 11.0.4 做 1,536 組有限樣本比較，涵蓋 dot、allowWindowsEscape、flipNegate、matchBase、noglobstar 與 `.match(path, true)` partial；1,530 組相同、6 組不同。差異集中於帶 `..` 的 glob 正規化，例如 `src/**/a/../*.js`。14 個明確預期值斷言也通過。不能把舊選項名稱仍被接受誤當完整語意等價；同時，本次沒有證據顯示 flipNegate、matchBase 或 allowWindowsEscape 在所測案例本身失效，不沿用未經證實的全面不支援說法。

## 5. GHSA-g3hv-75wg-m249：分開看公告、實作與可達性

### 公告現況

- 通告：GHSA-g3hv-75wg-m249 / CVE-2026-118764，moderate。
- 維護者通告列受影響版本 10.2.6、修補版 11.0.1，描述惡意 glob 於 `optimizationLevel >= 2` 造成預處理放大及後續平方比較。
- GitHub Reviewed 資料庫卻列 `<11.0.1`，因此 npm 將 3.1.5 也納入。
- github/advisory-database #10811 公開質疑 3.1.5 適用性；查閱時仍 Open，不能把提問者的分析當維護者已正式排除或撤回通告。

### 本次獨立原始碼證據

minimatch 3.1.5 的安裝檔 `minimatch.js` SHA-256 為 `746849f267c4868a53729225bd85c7dccd387712136fb305fcc0a3eadd4a3d9d`，與公開議題引用的版本原始碼雜湊一致。實際檢查該檔不存在 `firstPhasePreProcess`、`secondPhasePreProcess` 或 `optimizationLevel`。因此，**這則通告所描述的特定 optimizer 機制在所檢查的 3.1.5 實作中不存在**。這是有原始碼支持的適用性疑慮，不是宣告 minimatch 3 沒有其他 DoS 或其他風險。保留 npm finding，不標記為已正式修復。

minimatch 10.2.6 確實含公告描述的兩個預處理函式，預設 `optimizationLevel = 1`；只有 `>=2` 才進入該組流程。`@typescript-eslint/typescript-estree` 的實際 minimatch 呼叫位於 `useProgramFromProjectService.js` 的 allowDefaultProject matching，只傳 `{ dot: true }`，沒有開啟 level 2。專案目前亦未設定 projectService/allowDefaultProject。

### 本專案可達性與殘留風險

| 情境 | 判斷 |
|---|---|
| GitHub Pages 靜態網站訪客 | 不執行 Node 或 ESLint；minimatch 全部屬 dev 依賴。沒有從訪客輸入到該 matcher 的路徑。 |
| 目前 lint / PR CI | glob 主要來自受版本控制的設定。3.x 缺乏該 optimizer；10.x 呼叫使用預設 level 1；未找到本通告必要的 level 2 可達路徑。 |
| 未來新增工具或設定 | 如果把不可信 glob 傳給 10.x 並啟用 level 2，就可能暴露已確認存在的漏洞機制，必須重評。 |
| 不可信 PR 修改驗證腳本／設定 | CI 本來就會執行 PR 程式碼，仍需審查；目前 job timeout 提供上限，但不等於防止 CPU／記憶體耗用，也不是本漏洞已修補的證據。 |

結論是目前已檢查流程中的可利用性低、未找到該機制的可達觸發條件；不是形式證明，也不是把開發依賴一概視為無風險。沒有執行資源耗盡攻擊。有限小型 glob 樣本僅供行為觀察，不用來證明抗 DoS。

### 後續修正條件

追蹤 #10811 的正式範圍更正，以及 minimatch 3.x / 10.x 相容修補或 ESLint／外掛宣告支援新版的正式發布。有支援範圍內更新時，在獨立分支重跑本次測試及 audit。三個 plugin 尚無較新的支援版本，故沒有可直接採用且已核實的窄範圍升級。

沒有為 typescript-estree 單獨強推 minimatch 11：雖然它使用具名函式可避免 CommonJS TypeError，仍違反其宣告的 `^10.2.2`，且已有 glob 語意差異證據。沒有為消除通告而自行 backport 或引入未核實的 fork。

## 6. 實際 npm audit 結果

| 對象 | 完整 audit | omit=dev | exit code |
|---|---|---|---|
| 基準全域 override | 0 | 0 | 0 / 0 |
| 最終修補 | **16 moderate；0 high；0 critical** | **0** | **1 / 0** |

16 是 npm 依相依傳播計數的受標記套件數，**不是 16 個獨立 CVE**。唯一直接 advisory 為 minimatch 的 GHSA-g3hv-75wg-m249；七個安裝路徑為六份 3.1.5 及一份 10.2.6。

完整 16 個被標記套件：`minimatch`、`@eslint/config-array`、`@eslint/eslintrc`、`@eslint-community/eslint-utils`、`eslint`、`@next/eslint-plugin-next`、`eslint-config-next`、`@typescript-eslint/typescript-estree`、`@typescript-eslint/utils`、`@typescript-eslint/parser`、`@typescript-eslint/eslint-plugin`、`@typescript-eslint/type-utils`、`typescript-eslint`、`eslint-plugin-import`、`eslint-plugin-react`、`eslint-plugin-jsx-a11y`。它們均為 dev 鏈；並未出現新的 Next.js、sharp 或 postcss finding。

npm 建議的 force 修復包含降為 eslint 4.0.0，會破壞現行 ESLint 9 flat config 及 Next.js 工具鏈，故沒有執行。audit JSON 與文字輸出均原樣交付，未隱藏 finding，也沒有把 audit exit 1 改稱通過。所有結果只代表本次查詢時點。

## 7. 實際回歸結果與限制

環境：Linux x64、Node 24.22.1、npm 11.9.0、Python 3.12.14。未修改 engine 或工作流 Node 20 設定；沒有在原生 Windows 或 Node 20 另跑一輪。

| 實際執行命令 | 結果 |
|---|---|
| npm ci | exit 0；安裝 382 個套件，無 ERESOLVE |
| npm ls minimatch | exit 0；七條消費鏈回到宣告範圍 |
| npm explain minimatch | exit 0；完整解析路徑留存 |
| npm ls --all | exit 0；無 invalid 相依樹 |
| npm run typecheck | exit 0 |
| npm run lint | exit 0 |
| python scripts/verify_foundation.py | exit 0；最終 81 個 index 檔案，10 個 seed entries |
| python scripts/validate_inventory.py | exit 0；31/31，0 warnings |
| python scripts/validate_content.py | exit 0；35 checks |
| npm run build | exit 0；Next.js 16.4.4；14/14 靜態頁面產生完成 |
| python scripts/validate_static.py | exit 0；107 checks，12 routes |
| npm audit | exit 1；16 moderate，已記錄及分析 |
| npm audit --omit=dev | exit 0；0 vulnerabilities |
| 外掛、API、忽略及負向模式 harness | 修正後 7/7；基準成功重現三個預期 TypeError |
| minimatch 有限行為比較 | 1,536 組；6 個差異如上；14 個預期值斷言通過 |
| 封裝與內容保留檢查 | 原 80 個檔案全部保留；僅 2 個原檔改動、1 個新報告；78 個原檔雜湊相同 |

foundation 初次執行為 80 檔案；新增報告後已另執行最終 81 檔案檢查。暫存 index 不在交付包內。原始驗證器維持不變，沒有改成跳過 Git 檢查。

本次未重做瀏覽器視覺、行動觸控或 localStorage 手動測試；沒有把先前報告的瀏覽器結果冒稱本次執行。沒有驗證全部書稿、翻譯品質或著作權。既有來源檔逐位元組不變，加上原有 Phase 0–1 全套命令及靜態路由檢查通過，是此次依賴修補的回歸依據。Windows 路徑與 escaping 的有限選項測試在 Linux 執行，不代表原生 Windows 實測。

static export 保持 `output: "export"`、`trailingSlash: true`、`images.unoptimized: true`；現有 route/metadata/no-JS HTML 驗證通過，維持 GitHub Pages 相容。沒有啟用部署或更改權限。

## 8. 交付與重現

- `sal-phase1-dependency-remediation-20261103.zip`：完整原始碼，81 檔案；不含 `.git`、node_modules、.next、out、next-env.d.ts、tsbuildinfo、環境檔、認證、暫存 log。
- `SAL-Dependency-Remediation-Evidence-20261103.zip`：實際命令紀錄、兩個可重跑測試 harness、audit JSON、版本資料與完整內容比對結果。
- `CHANGED-FILES.json`：精確列出兩個修改與一個新增，含前後 SHA-256。
- `DEPENDENCY-VERSIONS.csv`：每個 lock package 路徑的前後版本與狀態。
- `WINDOWS-GIT-BASH-INTEGRATION.md`：只複製上述三檔的整合指令。
- `SHA256SUMS.txt`：所有交付檔案的校驗值。

若重現定向測試，將 evidence ZIP 解壓在專案外，對已 npm ci 的專案執行：

```bash
node /path/to/evidence/compatibility.cjs /path/to/project fixed
```

雙版本比較另外需要安裝過原始基準依賴的副本：

```bash
node /path/to/evidence/compatibility.cjs /path/to/baseline baseline
node /path/to/evidence/compare-minimatch.cjs /path/to/fixed /path/to/baseline
```

不要把測試 fixture 移入 src 或更動生產 ESLint 規則。完整整合前置檢查、預期的 audit 非零處理與停止條件見 Windows 指引。

## 9. 原始來源與查閱限制

以下於本次作業查閱，報告日期採 Brisbane 2026-11-03；套件實際發布資訊另留 `registry-release-metadata.json`，不以搜尋摘要推算版本。

1. 維護者通告：https://github.com/isaacs/minimatch/security/advisories/GHSA-g3hv-75wg-m249
2. GitHub Reviewed 記錄：https://github.com/advisories/GHSA-g3hv-75wg-m249
3. 適用範圍爭議（仍為提問，非正式裁定）：https://github.com/github/advisory-database/issues/10811
4. 3.1.5 原始碼：https://github.com/isaacs/minimatch/blob/v3.1.5/minimatch.js
5. optimizer 修補：https://github.com/isaacs/minimatch/commit/77a0f5c4b80bdc641c3c930a1d9edf5ad2db57f8
6. minimatch 發布紀錄：https://github.com/isaacs/minimatch/releases/tag/v11.0.1
7. changelog：https://github.com/isaacs/minimatch/blob/main/changelog.md
8. brace-expansion 相容修補線討論：https://github.com/isaacs/minimatch/issues/327
9. Next.js ESLint 文件：https://nextjs.org/docs/app/api-reference/config/eslint
10. 實際 npm 查詢：next@16.4.4、eslint-config-next@16.4.4、eslint@9.39.5、minimatch 各主版本線與三個 plugin / typescript-eslint 的 version、dependencies、peerDependencies、engines。

未取得的 release tag 頁不作證據；對通告適用性未作無條件安全宣告。建議以相容性正確且風險透明的本修補取代原全域 override，日後依正式上游修補重新評估。
