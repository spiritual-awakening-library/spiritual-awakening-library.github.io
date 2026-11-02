import Link from "next/link";
import { ChapterDirectory } from "@/components/library/ChapterDirectory";
import type { Locale } from "@/lib/i18n";
import { t } from "@/lib/i18n";

/**
 * Collapsible book table of contents for reading pages.
 * Uses the native <details> element (no JavaScript required) so the
 * primary content remains fully accessible without JS.
 */
export function BookTocPanel({
  bookId,
  locale,
  currentEntryId,
}: {
  bookId: string;
  locale: Locale;
  currentEntryId: string;
}) {
  const s = t(locale);
  return (
    <details className="no-print group rounded-lg border border-line bg-block">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-2 px-4 py-3 text-sm font-medium text-ink-soft transition-colors hover:text-accent-deep">
        <span className="flex items-center gap-2">
          <span aria-hidden="true" className="text-accent">
            ☰
          </span>
          {s.readerTocHeading}
        </span>
        <span className="text-xs text-ink-faint group-open:hidden">
          {s.readerTocOpen}
        </span>
        <span aria-hidden="true" className="hidden text-xs text-ink-faint group-open:inline">
          ▾
        </span>
      </summary>
      <div className="border-t border-line px-4 py-4">
        <ChapterDirectory
          bookId={bookId}
          locale={locale}
          compact
          currentEntryId={currentEntryId}
        />
      </div>
    </details>
  );
}

/** Previous / next navigation among published entries of the same book. */
export function EntryNav({
  locale,
  bookId,
  previous,
  next,
}: {
  locale: Locale;
  bookId: string;
  previous: { entryId: string; title: string; series: string } | null;
  next: { entryId: string; title: string; series: string } | null;
}) {
  const s = t(locale);
  if (!previous && !next) {
    // No published neighbours yet (prototype: one entry per book) —
    // avoid an empty navigation landmark for assistive technology.
    return null;
  }
  return (
    <nav
      aria-label={locale === "zh-TW" ? "單元導覽" : "Entry navigation"}
      className="no-print mt-8 flex flex-col gap-3 border-t border-line pt-6 sm:flex-row sm:items-stretch sm:justify-between"
    >
      {previous ? (
        <Link
          href={`/${locale}/books/${bookId}/${previous.entryId}/`}
          className="group flex-1 rounded-md border border-line bg-block px-4 py-3 transition-colors hover:border-line-strong"
        >
          <span className="block text-xs text-ink-faint">← {s.readerPrevious}</span>
          <span className="mt-1 block font-serif text-sm text-ink group-hover:text-accent-deep">
            {previous.series ? `${previous.series}｜` : ""}
            {previous.title}
          </span>
        </Link>
      ) : (
        <span className="flex-1" aria-hidden="true" />
      )}
      {next ? (
        <Link
          href={`/${locale}/books/${bookId}/${next.entryId}/`}
          className="group flex-1 rounded-md border border-line bg-block px-4 py-3 text-right transition-colors hover:border-line-strong"
        >
          <span className="block text-xs text-ink-faint">{s.readerNext} →</span>
          <span className="mt-1 block font-serif text-sm text-ink group-hover:text-accent-deep">
            {next.series ? `${next.series}｜` : ""}
            {next.title}
          </span>
        </Link>
      ) : (
        <span className="flex-1" aria-hidden="true" />
      )}
    </nav>
  );
}
