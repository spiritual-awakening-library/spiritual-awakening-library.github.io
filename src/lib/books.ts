import fs from "node:fs";
import path from "node:path";
import type { Locale } from "@/lib/i18n";

/** Book-level display metadata (data/books.json). */
export type BookMeta = {
  id: string;
  title: Record<Locale, string>;
  title_en_status: string;
  title_page_title?: string;
  series_note: Record<Locale, string>;
  printed_page_range: string;
  pdf_pages: number;
  entry_count: number;
  cover: string;
  cover_alt: Record<Locale, string>;
  first_published_entry: string;
};

type BooksFile = {
  schema: string;
  author: Record<Locale, string>;
  books: BookMeta[];
};

let cache: BooksFile | null = null;

export function getBooksFile(): BooksFile {
  if (!cache) {
    const file = path.join(process.cwd(), "data", "books.json");
    cache = JSON.parse(fs.readFileSync(file, "utf-8")) as BooksFile;
  }
  return cache;
}

export function getBook(bookId: string): BookMeta | undefined {
  return getBooksFile().books.find((b) => b.id === bookId);
}

export function getAuthor(): Record<Locale, string> {
  return getBooksFile().author;
}
