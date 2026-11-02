import fs from "node:fs";
import path from "node:path";
import type { Locale } from "./i18n";

/**
 * Content loader for published reading entries.
 *
 * Entry text lives in `content/{bookId}/{locale}/{entryId}.json` with
 * stable paragraph IDs (`p-001` …) shared across languages, enabling
 * paragraph-preserving language switching. This module is only imported
 * by server components; text is embedded into static HTML at build time
 * (no client fetching of primary content).
 */

export type Paragraph = { id: string; text: string };

export type EntryContent = {
  schema: string;
  book_id: string;
  entry_id: string;
  title: string;
  series: string;
  language: string;
  printed_pages: string;
  pdf_pages: string;
  source_sha256?: string;
  extraction_method?: string;
  translated_from?: string;
  translation_status?: string;
  translation_review?: string;
  translation_note?: string;
  paragraphs: Paragraph[];
};

type PublishedLocale = {
  status: string;
  review?: string;
  status_note: string;
  content: string;
};

type PublishedEntry = {
  book_id: string;
  entry_id: string;
  locales: Partial<Record<Locale, PublishedLocale>>;
};

type PublishedRegistry = {
  schema: string;
  note: string;
  entries: PublishedEntry[];
};

let registryCache: PublishedRegistry | null = null;

function getRegistry(): PublishedRegistry {
  let registry = registryCache;
  if (!registry) {
    const file = path.join(process.cwd(), "data", "published.json");
    registry = JSON.parse(fs.readFileSync(file, "utf-8")) as PublishedRegistry;
    registryCache = registry;
  }
  return registry;
}

export function getPublishedEntry(
  bookId: string,
  entryId: string,
): PublishedEntry | undefined {
  return getRegistry().entries.find(
    (e) => e.book_id === bookId && e.entry_id === entryId,
  );
}

export function isPublished(
  bookId: string,
  entryId: string,
  locale: Locale,
): boolean {
  return Boolean(getPublishedEntry(bookId, entryId)?.locales[locale]);
}

/** All published (bookId, entryId) pairs for a locale, in inventory order. */
export function listPublished(bookId: string, locale: Locale): string[] {
  return getRegistry()
    .entries.filter((e) => e.book_id === bookId && e.locales[locale])
    .map((e) => e.entry_id);
}

export function loadEntryContent(
  bookId: string,
  entryId: string,
  locale: Locale,
): EntryContent | null {
  const published = getPublishedEntry(bookId, entryId);
  const loc = published?.locales[locale];
  if (!loc) return null;
  const file = path.join(process.cwd(), loc.content);
  const data = JSON.parse(fs.readFileSync(file, "utf-8")) as EntryContent;
  if (data.book_id !== bookId || data.entry_id !== entryId) {
    throw new Error(
      `content mismatch: ${data.book_id}/${data.entry_id} != ${bookId}/${entryId}`,
    );
  }
  return data;
}

export function publicationStatus(
  bookId: string,
  entryId: string,
  locale: Locale,
): PublishedLocale | undefined {
  return getPublishedEntry(bookId, entryId)?.locales[locale];
}
