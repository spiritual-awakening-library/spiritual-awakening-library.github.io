import type { Locale } from "./i18n";

/**
 * Route builders. Every internal route uses a trailing slash, matching
 * `trailingSlash: true` and the static-export directory layout
 * (`/zh-TW/books/book-1/chapter-01/` → `.../chapter-01/index.html`).
 */
export function homeRoute(locale: Locale): string {
  return `/${locale}/`;
}

export function bookRoute(locale: Locale, bookId: string): string {
  return `/${locale}/books/${bookId}/`;
}

export function entryRoute(
  locale: Locale,
  bookId: string,
  entryId: string,
): string {
  return `/${locale}/books/${bookId}/${entryId}/`;
}

export const LANDING_ROUTE = "/";
