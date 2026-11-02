import fs from "node:fs";
import path from "node:path";

/**
 * Loader for the verified Phase 0.2 inventories.
 *
 * The inventories are the single source of truth for book structure:
 * original titles, entry kinds, order, printed pages, PDF pages, and
 * verification statuses. They are read from `data/inventory/` at build
 * time (this module is only imported by server components).
 */

export type EntryKind =
  | "cover"
  | "preface"
  | "foreword"
  | "toc"
  | "title-page"
  | "acknowledgment"
  | "chapter"
  | "essay"
  | "analysis"
  | "blessing"
  | "interview"
  | "testimony-story"
  | "testimonial"
  | "quote-plate"
  | "photo-plate"
  | "diagram-plate"
  | "rights-statement"
  | "colophon";

export type InventoryEntry = {
  book_id: string;
  entry_id: string;
  entry_kind: EntryKind;
  order_in_book: number;
  original_title: string;
  title_qualifier: string;
  parent_series: string;
  attributed_author: string;
  printed_page: string | null;
  printed_page_num: number | null;
  pdf_page: number;
  pdf_page_position: string;
  source_file: string;
  language: string;
  toc_status: string;
  body_status: string;
  translation_status: string;
  review_notes: string;
};

export type Inventory = {
  schema: string;
  book: string;
  source_pdf: string;
  source_sha256: string;
  entries: InventoryEntry[];
};

/** Coarse grouping used for directory section headers. */
export type SectionKey = "front" | "main" | "plates" | "back";

const SECTION_BY_KIND: Record<EntryKind, SectionKey> = {
  cover: "front",
  preface: "front",
  foreword: "front",
  toc: "front",
  "title-page": "front",
  acknowledgment: "front",
  chapter: "main",
  essay: "main",
  analysis: "main",
  blessing: "main",
  interview: "main",
  "testimony-story": "main",
  testimonial: "main",
  "quote-plate": "plates",
  "photo-plate": "plates",
  "diagram-plate": "plates",
  "rights-statement": "back",
  colophon: "back",
};

export function sectionOf(entry: InventoryEntry): SectionKey {
  return SECTION_BY_KIND[entry.entry_kind] ?? "main";
}

function loadInventory(bookId: string): Inventory {
  const file = path.join(
    process.cwd(),
    "data",
    "inventory",
    `${bookId}-inventory.json`,
  );
  const raw = fs.readFileSync(file, "utf-8");
  const data = JSON.parse(raw) as Inventory;
  if (data.book !== bookId) {
    throw new Error(`inventory book mismatch: ${data.book} != ${bookId}`);
  }
  return data;
}

export function getInventory(bookId: string): Inventory {
  return loadInventory(bookId);
}

export function getEntry(
  bookId: string,
  entryId: string,
): InventoryEntry | undefined {
  return loadInventory(bookId).entries.find((e) => e.entry_id === entryId);
}

export function getAllEntries(bookId: string): InventoryEntry[] {
  return [...loadInventory(bookId).entries].sort(
    (a, b) => a.order_in_book - b.order_in_book,
  );
}
