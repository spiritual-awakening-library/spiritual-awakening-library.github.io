import Link from "next/link";
import { EDITORIAL_NOTES } from "@/components/library/BookCard";
import { getAllEntries, sectionOf, type InventoryEntry, type SectionKey } from "@/lib/inventory";
import { isPublished, publicationStatus } from "@/lib/content";
import { entryRoute } from "@/lib/routing";
import { t, type Locale } from "@/lib/i18n";

/**
 * Complete inventory-driven directory for one book.
 *
 * - Lists every unit in the verified Phase 0.2 inventory order.
 * - Only published entries link to reading pages; the rest display a
 *   "not yet published" state (never a dead or misleading link).
 * - Editorial descriptions (draft, pending approval) are visually and
 *   verbally separated from source titles.
 */
export function ChapterDirectory({
  bookId,
  locale,
  compact = false,
  currentEntryId,
}: {
  bookId: string;
  locale: Locale;
  compact?: boolean;
  currentEntryId?: string;
}) {
  const s = t(locale);
  const entries = getAllEntries(bookId);

  const sections: { key: SectionKey; label: string; entries: InventoryEntry[] }[] = [];
  for (const entry of entries) {
    const key = sectionOf(entry);
    let section = sections.find((sec) => sec.key === key);
    if (!section) {
      section = { key, label: s.sectionLabels[key], entries: [] };
      sections.push(section);
    }
    section.entries.push(entry);
  }

  return (
    <section aria-labelledby="dir-heading">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 id="dir-heading" className="font-serif text-lg text-ink">
          {s.bookAllEntriesHeading}
          <span className="ml-2 text-sm font-normal text-ink-faint">
            {entries.length} {s.bookEntriesCountLabel}
          </span>
        </h2>
      </div>
      <p className="mt-1.5 text-xs leading-relaxed text-ink-faint">
        {s.bookDirectoryNote}
      </p>

      <div
        className={`scroll-calm mt-4 overflow-y-auto rounded-lg border border-line bg-block ${
          compact ? "max-h-[65vh]" : "max-h-[75vh]"
        }`}
      >
        {sections.map((section) => (
          <div key={section.key}>
            <div className="sticky top-0 z-10 border-b border-line bg-paper-deep/95 px-4 py-2 text-xs font-medium tracking-wider text-ink-soft">
              {section.label}
            </div>
            <ul className="divide-y divide-line/70">
              {section.entries.map((entry) => {
                const key = `${entry.book_id}/${entry.entry_id}`;
                const note = EDITORIAL_NOTES[key]?.[locale];
                const published = isPublished(bookId, entry.entry_id, locale);
                const isCurrent = entry.entry_id === currentEntryId;
                const status = publicationStatus(bookId, entry.entry_id, locale);
                const draftTranslation =
                  published && status?.status === "draft-machine-assisted";
                return (
                  <li key={entry.entry_id} className="px-4 py-3">
                    <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                      {published ? (
                        <Link
                          href={entryRoute(locale, bookId, entry.entry_id)}
                          aria-current={isCurrent ? "page" : undefined}
                          className={`font-serif text-[15px] leading-snug transition-colors hover:text-accent-deep ${
                            isCurrent ? "text-accent-deep underline decoration-line-strong underline-offset-4" : "text-ink"
                          }`}
                        >
                          {entry.parent_series && (
                            <span className="mr-1.5 text-xs text-ink-faint">
                              {entry.parent_series}
                            </span>
                          )}
                          {entry.original_title}
                        </Link>
                      ) : (
                        <span className="font-serif text-[15px] leading-snug text-ink-soft">
                          {entry.parent_series && (
                            <span className="mr-1.5 text-xs text-ink-faint">
                              {entry.parent_series}
                            </span>
                          )}
                          {entry.original_title}
                        </span>
                      )}
                      <span className="text-[11px] uppercase tracking-wide text-ink-faint">
                        {s.kindLabels[entry.entry_kind] ?? entry.entry_kind}
                      </span>
                      {published ? (
                        <span className="rounded-full border border-line-strong bg-accent-wash px-2 py-0.5 text-[11px] text-accent-deep">
                          {s.bookPublishedBadge}
                          {draftTranslation ? ` · ${s.bookDraftBadge}` : ""}
                        </span>
                      ) : (
                        <span className="rounded-full border border-line px-2 py-0.5 text-[11px] text-ink-faint">
                          {s.bookUnavailableBadge}
                        </span>
                      )}
                      <span className="ml-auto text-xs tabular-nums text-ink-faint">
                        {entry.printed_page
                          ? `${s.bookPrintedPagesLabel} ${entry.printed_page}`
                          : `PDF ${entry.pdf_page}${entry.pdf_page_position ? ` ${entry.pdf_page_position}` : ""}`}
                      </span>
                    </div>
                    {note && published && (
                      <p className="mt-1.5 border-l-2 border-line-strong pl-3 text-xs leading-relaxed text-ink-soft">
                        <span className="mr-1.5 font-medium text-ink-faint">
                          〔{s.bookEditorialNoteLabel}〕
                        </span>
                        {note}
                      </p>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}
