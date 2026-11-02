import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { buildMetadata } from "@/lib/seo";
import { getBook } from "@/lib/books";
import { getAllEntries } from "@/lib/inventory";
import { listPublished, isPublished } from "@/lib/content";
import { BookCover } from "@/components/library/BookCover";
import { ChapterDirectory } from "@/components/library/ChapterDirectory";
import { getAuthor } from "@/lib/books";
import { t, SITE_NAME, LOCALES, type Locale } from "@/lib/i18n";
import { entryRoute } from "@/lib/routing";
import { SiteHeader } from "@/components/navigation/SiteChrome";

/**
 * Book overview + complete inventory-driven directory.
 */

/**
 * Full param maps (locale × bookId) are enumerated explicitly: in
 * development mode parent context is not injected, and static export
 * requires every generated route to appear here.
 */
export function generateStaticParams() {
  return LOCALES.flatMap((locale) =>
    ["book-1", "book-2"].map((bookId) => ({ locale, bookId })),
  );
}

export const dynamicParams = false;

type Params = Promise<{ locale: string; bookId: string }>;

export async function generateMetadata({
  params,
}: {
  params: Params;
}): Promise<Metadata> {
  const { locale, bookId } = await params;
  const book = getBook(bookId);
  if (!book) return {};
  const zh = locale === "zh-TW";
  const title = zh
    ? `《${book.title["zh-TW"]}》目錄 — ${SITE_NAME["zh-TW"]}`
    : `${book.title.en} (working title) — contents — ${SITE_NAME.en}`;
  return buildMetadata({
    path: `/${locale}/books/${bookId}/`,
    selfLocale: locale as Locale,
    siblings: [
      { locale: zh ? "en" : "zh-TW", href: `/${zh ? "en" : "zh-TW"}/books/${bookId}/` },
    ],
    title,
    description: zh
      ? `《${book.title["zh-TW"]}》全書 ${getAllEntries(bookId).length} 個內容單元的驗證目錄，含印刷頁碼與單元類型；已出版單元可線上閱讀。`
      : `The verified table of contents for ${book.title.en} (working title) — ${getAllEntries(bookId).length} content units with printed page numbers and unit types; published entries are readable online.`,
  });
}

export default async function BookPage({ params }: { params: Params }) {
  const { locale: localeRaw, bookId } = await params;
  const locale = localeRaw as Locale;
  const book = getBook(bookId);
  if (!book) {
    notFound();
  }
  const s = t(locale);
  const zh = locale === "zh-TW";
  const entries = getAllEntries(bookId);
  const published = listPublished(bookId, locale);
  const author = getAuthor();
  const firstPublished = isPublished(bookId, book.first_published_entry, locale);

  return (
    <>
      <SiteHeader locale={locale} currentBookId={bookId} />
      <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-10 md:px-6 md:py-14">
      <nav aria-label="breadcrumb" className="text-xs text-ink-faint">
        <ol className="flex flex-wrap items-center gap-1.5">
          <li>
            <Link href={`/${locale}/`} className="hover:text-accent-deep">
              {s.navHome}
            </Link>
          </li>
          <li aria-hidden="true">›</li>
          <li aria-current="page" className="text-ink-soft">
            《{book.title[locale]}》
          </li>
        </ol>
      </nav>

      <header className="mt-6">
        <div className="grid gap-6 md:grid-cols-[minmax(0,5fr)_minmax(0,7fr)] md:items-start">
          <BookCover
            src={book.cover}
            alt={book.cover_alt[locale]}
            width={1400}
            height={bookId === "book-1" ? 656 : 567}
            priority
            sizes="(min-width: 768px) 380px, 92vw"
          />
          <div>
            <h1 className="font-serif text-2xl leading-snug text-ink md:text-3xl">
              《{book.title[locale]}》
              {locale === "en" && (
                <span className="ml-2 align-middle text-sm font-normal text-ink-faint">
                  (working title)
                </span>
              )}
            </h1>
            {book.title_page_title && zh && (
              <p className="mt-1 text-sm text-ink-faint">
                書名頁題名：《{book.title_page_title}》
              </p>
            )}
            <p className="mt-2 text-sm text-ink-soft">
              {author[locale]} {zh ? "著" : ""}
            </p>
            <p className="mt-3 text-[14px] leading-relaxed text-ink-soft">
              {book.series_note[locale]}
            </p>
            <dl className="mt-4 grid grid-cols-2 gap-x-6 gap-y-2 text-xs text-ink-faint sm:grid-cols-3">
              <div>
                <dt className="inline">{zh ? "內容單元" : "Units"}： </dt>
                <dd className="inline tabular-nums">{entries.length}</dd>
              </div>
              <div>
                <dt className="inline">{zh ? "印刷頁" : "Printed pages"}： </dt>
                <dd className="inline tabular-nums">{book.printed_page_range}</dd>
              </div>
              <div>
                <dt className="inline">{zh ? "已出版" : "Published"}： </dt>
                <dd className="inline tabular-nums">{published.length}</dd>
              </div>
            </dl>
            {firstPublished && (
              <div className="mt-5">
                <Link
                  href={entryRoute(locale, bookId, book.first_published_entry)}
                  className="inline-block rounded-md bg-accent px-5 py-2.5 font-medium text-white transition-colors hover:bg-accent-deep"
                >
                  {s.homeStartReading} →
                </Link>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="mt-10">
        <ChapterDirectory bookId={bookId} locale={locale} />
      </div>
      </main>
    </>
  );
}
