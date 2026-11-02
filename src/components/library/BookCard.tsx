import Link from "next/link";
import { BookCover } from "@/components/library/BookCover";
import { ChapterDirectory } from "@/components/library/ChapterDirectory";
import { getBook } from "@/lib/books";
import { getAllEntries } from "@/lib/inventory";
import { listPublished } from "@/lib/content";
import { bookRoute, entryRoute } from "@/lib/routing";
import { t, type Locale } from "@/lib/i18n";

/**
 * Book overview card + the complete inventory-driven directory.
 * Descriptions shown for prototype entries are library-written
 * editorial drafts, clearly separated from source text.
 */
const EDITORIAL_NOTES: Record<string, Record<Locale, string>> = {
  "book-1/chapter-01": {
    "zh-TW":
      "全書開篇。從內在沉靜與誠實談起，鋪陳作者對「神」與「本源」的界定，再以次元、量子糾纏與希格斯粒子等物理意象，申說「合一」的宇宙觀。",
    en: "The opening chapter of the book. Beginning from inner stillness and honesty, the author sets out his definition of “God” and the “Original Source,” then draws on dimensions, quantum entanglement, and the Higgs particle to unfold a cosmology of oneness.",
  },
  "book-2/preface-01": {
    "zh-TW":
      "作者自序。說明寫作緣起：以覺醒開悟者的親歷，毫無隱瞞地道出靈性開悟此一生命終極議題，並自陳捷運保全員的平凡身分與「傳遞」的使命。",
    en: "The author's preface. He explains the origin of the book: to state, from the lived experience of one who has awakened, the ultimate subject of spiritual enlightenment without concealment — and speaks of his ordinary work as a metro station guard and his mission of “transmission.”",
  },
};

export function BookCard({
  bookId,
  locale,
  showDirectory = false,
}: {
  bookId: string;
  locale: Locale;
  showDirectory?: boolean;
}) {
  const book = getBook(bookId);
  if (!book) return null;
  const s = t(locale);
  const entries = getAllEntries(bookId);
  const published = listPublished(bookId, locale);

  return (
    <article className="rounded-lg border border-line bg-block shadow-[0_1px_3px_rgba(90,70,40,0.06)]">
      <div className="p-4 md:p-6">
        <BookCover
          src={book.cover}
          alt={book.cover_alt[locale]}
          width={1400}
          height={bookId === "book-1" ? 656 : 567}
        />
        <div className="mt-4 flex flex-wrap items-baseline gap-x-3 gap-y-1">
          <h2 className="font-serif text-xl text-ink md:text-2xl">
            《{book.title[locale]}》
            {locale === "en" && (
              <span className="ml-2 align-middle text-xs font-normal text-ink-faint">
                (working title)
              </span>
            )}
          </h2>
        </div>
        <p className="mt-1 text-sm text-ink-soft">
          {book.series_note[locale]} · {entries.length} {s.homeEntriesLabel}
        </p>
        <div className="mt-3 flex flex-wrap gap-3 text-sm">
          <Link
            href={bookRoute(locale, bookId)}
            className="rounded-md border border-line-strong bg-accent-wash px-4 py-2 font-medium text-accent-deep transition-colors hover:bg-block"
          >
            {s.homeBrowseBook}
          </Link>
          {published.length > 0 && (
            <Link
              href={entryRoute(locale, bookId, book.first_published_entry)}
              className="rounded-md bg-accent px-4 py-2 font-medium text-white transition-colors hover:bg-accent-deep"
            >
              {s.homeStartReading}
            </Link>
          )}
        </div>
      </div>
      {showDirectory && (
        <div className="border-t border-line p-4 md:p-6">
          <ChapterDirectory bookId={bookId} locale={locale} />
        </div>
      )}
    </article>
  );
}

export { EDITORIAL_NOTES };
