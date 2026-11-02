# Phase 1 — 內容與翻譯狀態報告（Content / Translation Status）

**日期：** 2026-11-02
**性質：** 原型選文之來源驗證與翻譯狀態紀錄。所有狀態如實標示，未虛報任何
人工審定。

## 一、原始選文（zh-TW）

### 抽取方法

兩篇選文均以 **座標感知直欄重建法**（`scripts/phase1/extract_prototype.py`，
PyMuPDF rawdict）自權威來源 PDF 抽取：

- 直排文字依 x 座標中心聚類成欄（book-1 欄距 18pt、book-2 24pt），欄序右至左；
  欄內依 y 中心排序。
- **拉丁混排處理**：直欄中內嵌的直立堆疊數字（3D/5D/2015…）與旋轉英文單字
  （dimension、Higgs boson、Large Hadron Collider…）以「整塊為單一排序單元」
  處理，避免與漢字交錯亂序。
- **段落邊界**：以欄首縮排判定（book-1：y0≥119 且首字非避頭點符號；
  book-2：y0≥100）。
- **過濾**：書眉、頁碼（book-1 頂部水平帶；book-2 底部中文數字）與開篇
  題名欄（題名一律採用 Phase 0.2 清單之驗證值）。

### 交叉驗證（VLM 頁面影像核對）

| 位置 | 核對項目 | 結果 |
| --- | --- | --- |
| book-1 PDF 9L（印刷 017） | 「百分之九八」原文用字（非「九十八」） | ✅ 確認原書即印「百分之九八」，如實保留 |
| book-1 PDF 12R（印刷 022） | 霍金段落之重複語句（霍金×2、發佈消息×2、十一次元×2） | ✅ 三欄逐字吻合，重複確為原文所有 |
| book-1 PDF 8L（印刷 015） | ︵dimension︶ 括號順序、Original Source、5D、6D、7D 直排混排 | ✅ 逐字吻合 |
| book-2 PDF 30（印刷 30） | 12小時／24天／2年／2015年8月︱2020年11月 數字序列 | ✅ 逐字吻合（「2年」經 16 倍放大影像複核確認） |

### 選文明細

| 欄位 | book-1/chapter-01 | book-2/preface-01 |
| --- | --- | --- |
| 題名 | 本源與宇宙次元 | 一份真實的路徑 |
| 系列 | 開悟之一 | 慶淇悟得手札自序 |
| 印刷頁 | 014–022 | 25–31 |
| PDF 頁 | 8R–12R | 25–31 |
| 段落數 | 24 | 21 |
| 字數 | 5,456 | 2,024 |
| 來源 SHA-256 | `a1f2f8…f901`（與清單一致） | `653dfb…d985`（與清單一致） |
| 狀態 | `source-verified-prototype` | `source-verified-prototype` |

**限制聲明**：以上驗證為「座標抽取 + 影像抽查 + 全文通讀」等級，尚未達
翻譯政策所訂「人工逐字校對核定」之發布門檻；此為 Phase 1 原型之明確定位。

## 二、英文翻譯（en）

| 欄位 | 值 |
| --- | --- |
| 範圍 | 僅 book-1/chapter-01（24 段，約 3,396 英文字） |
| 狀態 | `draft-machine-assisted`（機器輔助草譯） |
| 審閱 | `needs-human-review`（**未經人工譯者審閱**） |
| 段落對映 | 與 zh-TW 逐段 1:1（p-001…p-024，無拆併） |
| 術語 | 依 translation-policy v1.0 草案詞彙表（本源＝Original Source 等） |

- 草譯於頁面頂部以可見警語標示，並於 meta description 載明狀態。
- book-2/preface-01 **無英文版**：閱讀頁切換鈕呈明確停用狀態、不生成
  `/en/books/book-2/preface-01/` 路由、無 hreflang 指向。
- 譯者資訊：本階段為機器輔助產出，無人工譯者署名；正式署名待審校後補。

## 三、編按（館方導讀文字）

`EDITORIAL_NOTES`（BookCard 元件內）為館方草擬之單元導讀，均標示
「編按（草稿・待審）」，與原文明確區隔，非原作者文字。

## 四、書封圖像

兩書書封（完整展開圖，未裁切、未改動任何文字或視覺內容）依計畫主持人
Phase 1 明確指示納入原型展示（1400px PNG，`public/covers/`）。原始 PDF
檔案不入庫；權利狀態以書面授權為準（見 release-safety 文件）。

## 五、英文書名（工作譯名）

`data/books.json` 之英文書名標示 `draft-working-translation`：
- book-1：To Become Enlightened, This Book Is Enough（暫譯）
- book-2：Spiritual Awakening（依詞彙表提案）
僅供介面導覽，不作定稿譯名。
