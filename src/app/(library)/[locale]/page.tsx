import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import { buildMetadata } from "@/lib/seo";
import { getBooksFile } from "@/lib/books";
import { getAllEntries } from "@/lib/inventory";
import { listPublished, isPublished } from "@/lib/content";
import { entryRoute } from "@/lib/routing";
import { t, SITE_NAME, type Locale } from "@/lib/i18n";
import { EDITORIAL_NOTES } from "@/components/library/BookCard";
import { SiteHeader } from "@/components/navigation/SiteChrome";

/**
 * Localized library home (`/zh-TW/`, `/en/`).
 */

export function generateStaticParams() {
  return [{ locale: "zh-TW" }, { locale: "en" }];
}

export const dynamicParams = false;

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const zh = locale === "zh-TW";
  return buildMetadata({
    path: `/${locale}/`,
    selfLocale: locale as Locale,
    siblings: [{ locale: zh ? "en" : "zh-TW", href: `/${zh ? "en" : "zh-TW"}/` }],
    title: zh
      ? `${SITE_NAME["zh-TW"]} — 江慶淇著作的雙語數位圖書館`
      : `${SITE_NAME.en} — the works of Jiang Qingqi, bilingually`,
    description: zh
      ? "完整保存《要開悟，讀這本書就夠了》與《靈性覺醒》兩書之驗證目錄與選文，並逐步提供忠實的英文翻譯。"
      : "Complete verified inventories and selected reading entries from two Traditional Chinese works by Jiang Qingqi, with faithful English translations added progressively.",
  });
}

export default async function LocaleHomePage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const s = t(locale as Locale);
  const { books, author } = getBooksFile();
  const zh = locale === "zh-TW";

  const publishedEntries = books
    .map((book) => {
      const published = listPublished(book.id, locale as Locale);
      return { book, published };
    })
    .filter(({ published }) => published.length > 0);

  return (
    <>
      <SiteHeader locale={locale as Locale} />
      <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-10 md:px-6 md:py-14">
      <section aria-labelledby="hero">
        <p className="text-xs font-medium tracking-[0.25em] text-ink-faint">
          {s.homeHeroKicker}
        </p>
        <h1
          id="hero"
          className="mt-2.5 font-serif text-3xl tracking-wide text-ink md:text-4xl"
        >
          {s.homeHeroTitle}
        </h1>
        <p className="mt-1.5 text-sm text-ink-soft">{author[locale as Locale]} 著 · {s.siteTagline}</p>
        <p className="mt-5 max-w-2xl text-[15px] leading-relaxed text-ink-soft">
          {s.homeHeroBody}
        </p>
        {publishedEntries.length > 0 && (
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href={entryRoute(
                locale as Locale,
                publishedEntries[0].book.id,
                publishedEntries[0].book.first_published_entry,
              )}
              className="rounded-md bg-accent px-5 py-2.5 font-medium text-white transition-colors hover:bg-accent-deep"
            >
              {s.homeStartReading} →
            </Link>
          </div>
        )}
      </section>

      <section aria-labelledby="books" className="mt-12">
        <h2
          id="books"
          className="text-sm font-medium tracking-widest text-ink-faint"
        >
          {s.homeBooksHeading}
        </h2>
        <div className="mt-5 grid gap-6 lg:grid-cols-2">
          {books.map((book) => {
            const entryCount = getAllEntries(book.id).length;
            const published = isPublished(
              book.id,
              book.first_published_entry,
              locale as Locale,
            );
            return (
              <article
                key={book.id}
                className="flex flex-col rounded-lg border border-line bg-block p-4 shadow-[0_1px_3px_rgba(90,70,40,0.06)] md:p-5"
              >
                <Link href={`/${locale}/books/${book.id}/`} className="block overflow-hidden rounded-md border border-line bg-paper-deep">
                  <Image
                    src={book.cover}
                    alt={book.cover_alt[locale as Locale]}
                    width={1400}
                    height={book.id === "book-1" ? 656 : 567}
                    priority={book.id === "book-1"}
                    loading={book.id === "book-1" ? undefined : "lazy"}
                    sizes="(min-width: 1024px) 440px, 92vw"
                    className="h-auto w-full object-contain"
                  />
                </Link>
                <h3 className="mt-4 font-serif text-xl text-ink">
                  《{book.title[locale as Locale]}》
                  {locale === "en" && (
                    <span className="ml-2 align-middle text-xs font-normal text-ink-faint">
                      (working title)
                    </span>
                  )}
                </h3>
                <p className="mt-1.5 text-[13px] leading-relaxed text-ink-soft">
                  {book.series_note[locale as Locale]}
                </p>
                <p className="mt-1 text-xs tabular-nums text-ink-faint">
                  {entryCount} {s.homeEntriesLabel} · {s.bookPrintedPagesLabel}{" "}
                  {book.printed_page_range}
                </p>
                <div className="mt-4 flex flex-wrap gap-2.5 text-sm">
                  <Link
                    href={`/${locale}/books/${book.id}/`}
                    className="rounded-md border border-line-strong bg-accent-wash px-4 py-2 font-medium text-accent-deep transition-colors hover:bg-block"
                  >
                    {s.homeBrowseBook}
                  </Link>
                  {published && (
                    <Link
                      href={entryRoute(locale as Locale, book.id, book.first_published_entry)}
                      className="rounded-md bg-accent px-4 py-2 font-medium text-white transition-colors hover:bg-accent-deep"
                    >
                      {s.homeStartReading}
                    </Link>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      </section>

      {publishedEntries.length > 0 && (
        <section aria-labelledby="now" className="mt-12">
          <h2
            id="now"
            className="text-sm font-medium tracking-widest text-ink-faint"
          >
            {s.homeReadingNowHeading}
          </h2>
          <p className="mt-1 text-xs text-ink-faint">{s.homeReadingNowNote}</p>
          <ul className="mt-4 grid gap-4 md:grid-cols-2">
            {publishedEntries.map(({ book, published }) => {
              const firstId = book.first_published_entry;
              const note =
                EDITORIAL_NOTES[`${book.id}/${firstId}`]?.[locale as Locale];
              return (
                <li
                  key={book.id}
                  className="rounded-lg border border-line bg-block p-4 md:p-5"
                >
                  <Link
                    href={entryRoute(locale as Locale, book.id, firstId)}
                    className="font-serif text-lg text-ink transition-colors hover:text-accent-deep"
                  >
                    《{book.title[locale as Locale]}》—{" "}
                    {zh ? "開卷首篇" : "opening entry"}
                  </Link>
                  {note && (
                    <p className="mt-2 border-l-2 border-line-strong pl-3 text-[13px] leading-relaxed text-ink-soft">
                      <span className="mr-1.5 text-xs text-ink-faint">
                        〔{s.bookEditorialNoteLabel}〕
                      </span>
                      {note}
                    </p>
                  )}
                  <p className="mt-2.5 text-xs text-ink-faint">
                    {published.length} {zh ? "個已出版單元" : "published unit(s)"}
                  </p>
                </li>
              );
            })}
          </ul>
        </section>
      )}

      <section aria-labelledby="about" className="mt-12">
        <h2
          id="about"
          className="text-sm font-medium tracking-widest text-ink-faint"
        >
          {s.homeAboutHeading}
        </h2>
        <div className="mt-4 space-y-3 text-[14px] leading-relaxed text-ink-soft">
          {s.homeAboutBody.map((paragraph, i) => (
            <p key={i}>{paragraph}</p>
          ))}
          <div className="rounded-lg border border-line bg-block p-4 md:p-5">
            <h3 className="text-sm font-medium text-ink">
              {s.homeAboutSourceTitle}
            </h3>
            <p className="mt-1.5 text-[13px] leading-relaxed">
              {s.homeAboutSourceBody}
            </p>
          </div>
        </div>
      </section>
      </main>
    </>
  );
}
