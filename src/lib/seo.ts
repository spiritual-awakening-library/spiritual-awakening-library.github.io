import type { Metadata } from "next";
import { SITE_URL, type Locale } from "./i18n";

/**
 * SEO helpers.
 *
 * - Canonical URLs are self-referencing, with trailing slash.
 * - hreflang alternates are emitted only for language versions that
 *   actually exist (never for unpublished translations).
 * - `x-default` points to the language-neutral landing page `/`
 *   (architecture v1.1).
 */
export function buildMetadata({
  path,
  title,
  description,
  selfLocale,
  siblings = [],
}: {
  /** Full path beginning with "/" (including the locale segment when localized). */
  path: string;
  title: string;
  description: string;
  /** Locale of this page, when localized. Omit for the landing page. */
  selfLocale?: Locale;
  /** Existing same-content pages in other languages (full paths). */
  siblings?: { locale: Locale; href: string }[];
}): Metadata {
  const canonical = `${SITE_URL}${path}`;
  const languages: Record<string, string> = {};

  if (selfLocale) {
    languages[selfLocale] = canonical;
  }
  for (const sibling of siblings) {
    languages[sibling.locale] = `${SITE_URL}${sibling.href}`;
  }
  languages["x-default"] = `${SITE_URL}/`;

  return {
    title,
    description,
    alternates: {
      canonical,
      languages,
    },
    openGraph: {
      title,
      description,
      url: canonical,
      siteName: "Spiritual Awakening Library",
      type: "article",
    },
  };
}
