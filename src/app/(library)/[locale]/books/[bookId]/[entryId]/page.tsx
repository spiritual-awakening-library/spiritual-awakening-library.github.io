import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { buildMetadata } from "@/lib/seo";
import { getBook } from "@/lib/books";
import { getEntry } from "@/lib/inventory";
import {
  isPublished,
  listPublished,
  loadEntryContent,
  publicationStatus,
} from "@/lib/content";
import { ReadingBlock } from "@/components/reader/ReadingBlock";
import { ReadingProgressTracker } from "@/components/reader/ReadingProgressTracker";
import { FontSizeControl } from "@/components/reader/FontSizeControl";
import { TranslationStatusNotice } from "@/components/reader/TranslationStatusNotice";
import { BookTocPanel, EntryNav } from "@/components/reader/EntryNavigation";
import { SiteHeader } from "@/components/navigation/SiteChrome";
import { t, LOCALES, SITE_NAME, type Locale } from "@/lib/i18n";

/**
 * Reading page for one published entry in one language.
 *
 * - Only entries registered as published in `data/published.json` for
 *   this locale get a route (generateStaticParams); nothing else is
 *   ever generated, so no misleading placeholder pages exist.
 * - The full entry text is rendered into static HTML (no client-side
 *   fetching of primary content).
 */

export const dynamicParams = false;

type Params = Promise<{ locale: string; bookId: string; entryId: string }>;

/**
 * Full param maps are enumerated directly from the publication
 * registry (locale × bookId × entryId): in development mode parent
 * context is not injected, and static export requires every generated
 * route to appear here. Unpublished combinations produce no route.
 */
export function generateStaticParams() {
  const params: Array<{ locale: string; bookId: string; entryId: string }> = [];
  for (const locale of LOCALES) {
    for (const bookId of ["book-1", "book-2"]) {
      for (const entryId of listPublished(bookId, locale)) {
        params.push({ locale, bookId, entryId });
      }
    }
  }
  return params;
}

export async function generateMetadata({
  params,
}: {
  params: Params;
}): Promise<Metadata> {
  const { locale, bookId, entryId } = await params;
  const book = getBook(bookId);
  const inventoryEntry = getEntry(bookId, entryId);
  const content = loadEntryContent(bookId, entryId, locale as Locale);
  if (!book || !inventoryEntry || !content) return {};

  const zh = locale === "zh-TW";
  const status = publicationStatus(bookId, entryId, locale as Locale);
  const isDraft = status?.status === "draft-machine-assisted";

  const title = zh
    ? `${inventoryEntry.parent_series ? `${inventoryEntry.parent_series}｜` : ""}${inventoryEntry.original_title} — 《${book.title["zh-TW"]}》`
    : `${content.series ? `${content.series}: ` : ""}${content.title} — ${book.title.en} (working title)`;

  const baseDescription = zh
    ? `《${book.title["zh-TW"]}》${inventoryEntry.parent_series ?? ""}〈${inventoryEntry.original_title}〉（${inventoryEntry.entry_kind === "chapter" ? "開悟章節" : "選文"}，印刷頁 ${content.printed_pages}）。`
    : `${content.title} from ${book.title.en} (working title) by Jiang Qingqi — printed pages ${content.printed_pages}.`;
  const description = isDraft
    ? `${baseDescription} Machine-assisted draft translation, pending human review; the Traditional Chinese original is authoritative.`
    : baseDescription;

  const siblings = isPublished(bookId, entryId, zh ? "en" : "zh-TW")
    ? [
        {
          locale: (zh ? "en" : "zh-TW") as Locale,
          href: `/${zh ? "en" : "zh-TW"}/books/${bookId}/${entryId}/`,
        },
      ]
    : [];

  return buildMetadata({
    path: `/${locale}/books/${bookId}/${entryId}/`,
    selfLocale: locale as Locale,
    siblings,
    title: `${title} — ${SITE_NAME[locale as Locale]}`,
    description,
  });
}

export default async function EntryPage({ params }: { params: Params }) {
  const { locale: localeRaw, bookId, entryId } = await params;
  const locale = localeRaw as Locale;
  const zh = locale === "zh-TW";

  const book = getBook(bookId);
  const inventoryEntry = getEntry(bookId, entryId);
  const content = loadEntryContent(bookId, entryId, locale);
  if (!book || !inventoryEntry || !content) {
    notFound();
  }

  const s = t(locale);
  const status = publicationStatus(bookId, entryId, locale);
  const isDraft = status?.status === "draft-machine-assisted";
  const other = LOCALES.find((l) => l !== locale)!;
  const otherPublished = isPublished(bookId, entryId, other);

  // Previous/next navigation among published entries of this book.
  const published = listPublished(bookId, locale);
  const index = published.indexOf(entryId);
  const prevId = index > 0 ? published[index - 1] : null;
  const nextId = index >= 0 && index < published.length - 1 ? published[index + 1] : null;
  const metaOf = (id: string) => getEntry(bookId, id);
  const prev = prevId ? metaOf(prevId) : null;
  const next = nextId ? metaOf(nextId) : null;

  return (
    <>
      <SiteHeader locale={locale} currentBookId={bookId} currentEntryId={entryId} />
      <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-8 md:px-6 md:py-12">
      <ReadingProgressTracker />

      <nav aria-label="breadcrumb" className="text-xs text-ink-faint">
        <ol className="flex flex-wrap items-center gap-1.5">
          <li>
            <Link href={`/${locale}/`} className="hover:text-accent-deep">
              {s.navHome}
            </Link>
          </li>
          <li aria-hidden="true">›</li>
          <li>
            <Link
              href={`/${locale}/books/${bookId}/`}
              className="hover:text-accent-deep"
            >
              《{book.title[locale]}》
            </Link>
          </li>
          <li aria-hidden="true">›</li>
          <li aria-current="page" className="text-ink-soft">
            {zh ? inventoryEntry.original_title : content.title}
          </li>
        </ol>
      </nav>

      <article className="mt-6">
        <header>
          <p className="text-xs font-medium tracking-[0.2em] text-ink-faint">
            {content.series || inventoryEntry.parent_series}
          </p>
          <h1 className="mt-2 font-serif text-2xl leading-snug text-ink md:text-[1.75rem]">
            {zh ? inventoryEntry.original_title : content.title}
          </h1>
          <p className="mt-2.5 text-xs leading-relaxed text-ink-faint">
            {zh ? "作者" : "Author"}：{zh ? "江慶淇" : "Jiang Qingqi"} ・{" "}
            {zh ? "出處" : "Source"}：《{book.title[locale]}
            》・ {s.readerPrintedPages} {content.printed_pages} ・ PDF{" "}
            {content.pdf_pages}
          </p>
          <TranslationStatusNotice
            locale={locale}
            variant={isDraft ? "draft-translation" : "original"}
          />
        </header>

        <div className="no-print mt-6 flex flex-wrap items-center justify-between gap-3">
          <FontSizeControl
            labels={{
              group: s.readerFontSize,
              smaller: s.readerFontSmaller,
              larger: s.readerFontLarger,
              reset: s.readerFontReset,
            }}
          />
          {!otherPublished && (
            <p className="text-xs text-ink-faint">
              {zh
                ? "◇ 本篇英文翻譯尚未完成（切換鈕停用中）"
                : "◇ The other-language version of this entry is not yet available."}
            </p>
          )}
        </div>

        <div className="mt-7">
          <ReadingBlock paragraphs={content.paragraphs} locale={locale} />
        </div>

        <EntryNav
          locale={locale}
          bookId={bookId}
          previous={
            prev ? { entryId: prev.entry_id, title: prev.original_title, series: prev.parent_series } : null
          }
          next={
            next ? { entryId: next.entry_id, title: next.original_title, series: next.parent_series } : null
          }
        />

        <div className="no-print mt-6">
          <Link
            href={`/${locale}/books/${bookId}/`}
            className="text-sm text-accent-deep underline decoration-line-strong underline-offset-4 hover:text-accent"
          >
            ← {s.readerBackToDirectory}
          </Link>
        </div>
      </article>

      <div className="mt-10">
        <BookTocPanel
          bookId={bookId}
          locale={locale}
          currentEntryId={entryId}
        />
      </div>
      </main>
    </>
  );
}
