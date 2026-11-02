import type { MetadataRoute } from "next";
import { SITE_URL, LOCALES } from "@/lib/i18n";
import { getBooksFile } from "@/lib/books";
import { listPublished } from "@/lib/content";

/**
 * Static sitemap. Lists exactly the routes that exist in the export:
 * the landing page, both localized homes, book directory pages for
 * both books in both locales, and reading pages for every published
 * (book, entry, locale) combination. Nothing else is listed.
 */
export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date("2026-11-02T00:00:00Z");
  const urls: MetadataRoute.Sitemap = [
    {
      url: `${SITE_URL}/`,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 1,
    },
  ];

  for (const locale of LOCALES) {
    urls.push({
      url: `${SITE_URL}/${locale}/`,
      lastModified: now,
      changeFrequency: "monthly",
      priority: 0.9,
    });
  }

  for (const book of getBooksFile().books) {
    for (const locale of LOCALES) {
      urls.push({
        url: `${SITE_URL}/${locale}/books/${book.id}/`,
        lastModified: now,
        changeFrequency: "monthly",
        priority: 0.8,
      });
      for (const entryId of listPublished(book.id, locale)) {
        urls.push({
          url: `${SITE_URL}/${locale}/books/${book.id}/${entryId}/`,
          lastModified: now,
          changeFrequency: "monthly",
          priority: 0.7,
        });
      }
    }
  }

  return urls;
}
