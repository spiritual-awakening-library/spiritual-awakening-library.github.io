/**
 * Locale definitions and UI strings.
 *
 * The rendered language always comes from the URL path — never from
 * browser storage (architecture v1.1). `zh-TW` is the source language.
 */
export const LOCALES = ["zh-TW", "en"] as const;

export type Locale = (typeof LOCALES)[number];

export function isLocale(value: string): value is Locale {
  return (LOCALES as readonly string[]).includes(value);
}

export const SOURCE_LOCALE: Locale = "zh-TW";

/** BCP-47 lang attributes emitted on <html>. */
export const HTML_LANG: Record<Locale, string> = {
  "zh-TW": "zh-Hant-TW",
  en: "en",
};

export const SITE_URL = "https://spiritual-awakening-library.github.io";

export const SITE_NAME: Record<Locale, string> = {
  "zh-TW": "靈性覺醒圖書館",
  en: "Spiritual Awakening Library",
};

type Strings = {
  siteTagline: string;
  navHome: string;
  navBooks: string;
  switchLanguage: string;
  switchLanguageTo: string;
  skipToContent: string;
  footerProject: string;
  footerSource: string;
  footerRights: string;
  footerPhase: string;
  homeHeroKicker: string;
  homeHeroTitle: string;
  homeHeroBody: string;
  homeStartReading: string;
  homeBrowseBook: string;
  homeBooksHeading: string;
  homeEntriesLabel: string;
  homeSeriesLabel: string;
  homeReadingNowHeading: string;
  homeReadingNowNote: string;
  homeAboutHeading: string;
  homeAboutBody: string[];
  homeAboutSourceTitle: string;
  homeAboutSourceBody: string;
  bookChaptersHeading: string;
  bookAllEntriesHeading: string;
  bookPrintedPagesLabel: string;
  bookPdfPagesLabel: string;
  bookEntriesCountLabel: string;
  bookPublishedBadge: string;
  bookDraftBadge: string;
  bookUnavailableBadge: string;
  bookReadEntry: string;
  bookEditorialNoteLabel: string;
  bookDirectoryNote: string;
  kindLabels: Record<string, string>;
  sectionLabels: Record<string, string>;
  readerSeriesLabel: string;
  readerSourceInfo: string;
  readerPrintedPages: string;
  readerOriginal: string;
  readerTranslationDraft: string;
  readerTranslationDraftBody: string;
  readerTranslationOriginalBody: string;
  readerFontSize: string;
  readerFontSmaller: string;
  readerFontLarger: string;
  readerFontReset: string;
  readerTocHeading: string;
  readerTocOpen: string;
  readerPrevious: string;
  readerNext: string;
  readerBackToDirectory: string;
  readerNotPublished: string;
  readerParagraphLabel: string;
  langSwitchUnavailable: string;
  langSwitchUnavailableTitle: string;
  landingTitle: string;
  landingLead: string;
  landingEnter: string;
  landingEnterSub: string;
  landingBooksHeading: string;
  landingAuthor: string;
  landingNote: string;
  pageNote: string;
};

const zhStrings: Strings = {
  siteTagline: "江慶淇著作的雙語數位圖書館",
  navHome: "首頁",
  navBooks: "館藏",
  switchLanguage: "切換語言",
  switchLanguageTo: "English",
  skipToContent: "跳至主要內容",
  footerProject:
    "本館為非營利之公共利益數位保存計畫，旨在完整保存並推廣江慶淇先生的傳統中文著作，並提供忠實的英文翻譯。",
  footerSource:
    "來源依據：兩本紙本著作之掃描 PDF（SHA-256 檔案指紋已建檔於內部證據清單）；全書目錄經逐頁驗證（Phase 0.2，31 項自動檢查）。",
  footerRights:
    "著作權利由原作者保留。本站目前為原型階段，尚未正式公開部署；正式授權條款與發布範圍以書面授權為準。",
  footerPhase: "Phase 1 原型・目錄完整收錄，每書一篇代表性驗證選文",
  homeHeroKicker: "江慶淇著作・雙語閱讀",
  homeHeroTitle: "靈性覺醒圖書館",
  homeHeroBody:
    "完整保存兩部傳統中文著作——《要開悟，讀這本書就夠了》與《靈性覺醒》——並逐步提供忠實、可審閱的英文翻譯。全書目錄已逐頁驗證。",
  homeStartReading: "開始閱讀",
  homeBrowseBook: "瀏覽全書目錄",
  homeBooksHeading: "館藏兩書",
  homeEntriesLabel: "個內容單元",
  homeSeriesLabel: "全書",
  homeReadingNowHeading: "率先收錄",
  homeReadingNowNote: "各書首篇已完成來源驗證的選文",
  homeAboutHeading: "關於本館",
  homeAboutBody: [
    "本館收錄江慶淇先生兩部靈性著作的完整內容清單與選文。Phase 0 已建立架構與編輯政策；Phase 0.2 完成兩書共 295 個內容單元的逐頁驗證清單。",
    "Phase 1 提供本頁所見的閱讀原型：完整目錄導覽、段落分塊閱讀版面，以及中英對照的語言切換（草譯狀態均明確標示）。",
    "全書正文之逐字轉錄、校對與正式翻譯，將於後續階段依審校進度逐步發布；未經審核的內容不會以定稿形式呈現。",
  ],
  homeAboutSourceTitle: "來源與驗證",
  homeAboutSourceBody:
    "兩本書之印刷頁碼、PDF 頁序與章題均已對照原始掃描 PDF 逐項驗證；不確定事項記錄於公開審閱帳本。書封圖像依計畫主持人指示納入原型展示，原始 PDF 檔案不入庫。",
  bookChaptersHeading: "全書目錄",
  bookAllEntriesHeading: "全部內容單元",
  bookPrintedPagesLabel: "印刷頁",
  bookPdfPagesLabel: "PDF 頁",
  bookEntriesCountLabel: "個單元",
  bookPublishedBadge: "已收錄",
  bookDraftBadge: "草譯",
  bookUnavailableBadge: "尚未收錄",
  bookReadEntry: "閱讀本篇",
  bookEditorialNoteLabel: "編按（草稿・待審）",
  bookDirectoryNote:
    "目錄依 Phase 0.2 驗證清單之原始順序完整列出；標示「已收錄」者可連至閱讀頁，其餘單元待後續階段整理出版。編按為館方草擬之導讀文字，非原作者原文。",
  kindLabels: {
    cover: "封面",
    preface: "序文",
    foreword: "序文",
    toc: "目錄",
    "title-page": "書名頁",
    acknowledgment: "誌謝",
    chapter: "章",
    essay: "手札",
    analysis: "解析",
    blessing: "祝福",
    interview: "專訪",
    "testimony-story": "心開意解",
    testimonial: "見證",
    "quote-plate": "語錄",
    "photo-plate": "照片",
    "diagram-plate": "示意圖",
    "rights-statement": "權利聲明",
    colophon: "版權頁",
  },
  sectionLabels: {
    front: "前言與書首",
    main: "正文",
    plates: "圖版與語錄",
    back: "書末",
  },
  readerSeriesLabel: "所屬系列",
  readerSourceInfo: "資訊",
  readerPrintedPages: "印刷頁",
  readerOriginal: "原文（繁體中文）",
  readerTranslationDraft: "英文草譯（機器輔助・待人工審閱）",
  readerTranslationDraftBody:
    "本頁為機器輔助產生之草譯，尚未經人工譯者審閱核定，僅供預覽與對照。內容以繁體中文原文為準；如與原文有所出入，一律以原文為準。",
  readerTranslationOriginalBody:
    "本頁為繁體中文原文，經座標式逐欄轉錄並對照原始書頁影像核驗。英文版另有機器輔助草譯（待人工審閱）可供對照。",
  readerFontSize: "字型大小",
  readerFontSmaller: "縮小字型",
  readerFontLarger: "放大字型",
  readerFontReset: "回復預設字型",
  readerTocHeading: "本書目錄",
  readerTocOpen: "展開目錄",
  readerPrevious: "上一個已出版單元",
  readerNext: "下一個已出版單元",
  readerBackToDirectory: "回到全書目錄",
  readerNotPublished: "尚未出版",
  readerParagraphLabel: "段落",
  langSwitchUnavailable: "English",
  langSwitchUnavailableTitle: "本篇英文翻譯尚未完成，無法切換。",
  landingTitle: "靈性覺醒圖書館",
  landingLead: "Jiang Qingqi's works, in Traditional Chinese and English",
  landingEnter: "進入繁體中文版",
  landingEnterSub: "原文版本・Source language",
  landingBooksHeading: "館藏兩書 / The Collection",
  landingAuthor: "江慶淇 著 / by Jiang Qingqi",
  landingNote:
    "Prototype — complete verified inventories; one verified reading entry per book. English draft translation available for one entry.",
  pageNote: "",
};

const enStrings: Strings = {
  siteTagline: "A bilingual library of Jiang Qingqi's works",
  navHome: "Home",
  navBooks: "Collection",
  switchLanguage: "Switch language",
  switchLanguageTo: "繁體中文",
  skipToContent: "Skip to main content",
  footerProject:
    "A nonprofit digital preservation project in the public interest, conserving and presenting the complete Traditional Chinese works of Jiang Qingqi with faithful English translations.",
  footerSource:
    "Sources: scanned PDFs of the two print books (SHA-256 fingerprints recorded in the internal evidence manifest); full table-of-contents inventories verified page by page (Phase 0.2, 31 automated checks).",
  footerRights:
    "Copyright retained by the author. This prototype is not yet publicly deployed; the formal license and publication scope are subject to written authorization.",
  footerPhase: "Phase 1 prototype — complete inventories, one verified reading entry per book",
  homeHeroKicker: "Jiang Qingqi's works ・ bilingual reading",
  homeHeroTitle: "Spiritual Awakening Library",
  homeHeroBody:
    "Conserving two complete Traditional Chinese works — To Become Enlightened, This Book Is Enough (working title) and Spiritual Awakening — with faithful, reviewable English translations added progressively. The full tables of contents have been verified page by page.",
  homeStartReading: "Start reading",
  homeBrowseBook: "Browse the full table of contents",
  homeBooksHeading: "The Collection",
  homeEntriesLabel: "content units",
  homeSeriesLabel: "whole book",
  homeReadingNowHeading: "First published entries",
  homeReadingNowNote: "One source-verified reading entry from each book",
  homeAboutHeading: "About this library",
  homeAboutBody: [
    "This library conserves the complete content inventories and selected reading entries of two spiritual works by Jiang Qingqi. Phase 0 established the architecture and editorial policies; Phase 0.2 completed page-verified inventories of all 295 content units across the two books.",
    "Phase 1 delivers the reading prototype you are viewing: complete inventory-driven navigation, the approved paragraph-block reading presentation, and paragraph-preserving language switching (draft translation states are always clearly labeled).",
    "Full-book transcription, proofreading, and formal translations will be published progressively in later phases; unreviewed material is never presented as approved.",
  ],
  homeAboutSourceTitle: "Sources and verification",
  homeAboutSourceBody:
    "Printed page numbers, PDF page order, and every entry title were verified against the original scanned PDFs; open questions are recorded in the public review ledger. Cover images are included in this prototype at the project owner's direction; the original PDF files are kept out of the repository.",
  bookChaptersHeading: "Table of Contents",
  bookAllEntriesHeading: "All content units",
  bookPrintedPagesLabel: "printed p.",
  bookPdfPagesLabel: "PDF p.",
  bookEntriesCountLabel: "units",
  bookPublishedBadge: "Published",
  bookDraftBadge: "Draft translation",
  bookUnavailableBadge: "Not yet published",
  bookReadEntry: "Read this entry",
  bookEditorialNoteLabel: "Editor's note (draft, pending review)",
  bookDirectoryNote:
    "The directory lists every unit in the verified Phase 0.2 inventory order. Units marked “Published” link to reading pages; the rest will be prepared in later phases. Editor's notes are library-written draft descriptions, not the author's original text.",
  kindLabels: {
    cover: "Cover",
    preface: "Preface",
    foreword: "Foreword",
    toc: "Contents",
    "title-page": "Title page",
    acknowledgment: "Acknowledgments",
    chapter: "Chapter",
    essay: "Essay",
    analysis: "Analysis",
    blessing: "Blessing",
    interview: "Interview",
    "testimony-story": "Testimony",
    testimonial: "Testimonial",
    "quote-plate": "Quotations",
    "photo-plate": "Photograph",
    "diagram-plate": "Diagram",
    "rights-statement": "Rights statement",
    colophon: "Colophon",
  },
  sectionLabels: {
    front: "Front matter",
    main: "Main contents",
    plates: "Plates and quotations",
    back: "Back matter",
  },
  readerSeriesLabel: "Series",
  readerSourceInfo: "Source",
  readerPrintedPages: "printed pages",
  readerOriginal: "Original (Traditional Chinese)",
  readerTranslationDraft: "English draft (machine-assisted, pending human review)",
  readerTranslationDraftBody:
    "This page is a machine-assisted draft translation. It has not been reviewed or approved by a human translator and is provided for preview and comparison only. The Traditional Chinese original is authoritative; in any discrepancy, the original prevails.",
  readerTranslationOriginalBody:
    "This page presents the Traditional Chinese original text, transcribed by coordinate-aware column reconstruction and cross-checked against page images. A machine-assisted English draft (pending human review) is available for comparison.",
  readerFontSize: "Font size",
  readerFontSmaller: "Decrease font size",
  readerFontLarger: "Increase font size",
  readerFontReset: "Reset font size",
  readerTocHeading: "Book contents",
  readerTocOpen: "Open contents",
  readerPrevious: "Previous published entry",
  readerNext: "Next published entry",
  readerBackToDirectory: "Back to the table of contents",
  readerNotPublished: "Not yet published",
  readerParagraphLabel: "Paragraph",
  langSwitchUnavailable: "繁體中文",
  langSwitchUnavailableTitle: "The English translation of this entry is not yet available.",
  landingTitle: "Spiritual Awakening Library",
  landingLead: "江慶淇著作・繁體中文與英文",
  landingEnter: "Enter the English library",
  landingEnterSub: "Working language of the translations",
  landingBooksHeading: "館藏兩書 / The Collection",
  landingAuthor: "江慶淇 著 / by Jiang Qingqi",
  landingNote:
    "原型——完整驗證目錄；每書一篇驗證選文。其中一篇附英文草譯（待人工審閱）。",
  pageNote: "",
};

const STRINGS: Record<Locale, Strings> = {
  "zh-TW": zhStrings,
  en: enStrings,
};

export function t(locale: Locale): Strings {
  return STRINGS[locale];
}
