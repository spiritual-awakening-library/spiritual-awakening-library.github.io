import type { ReactNode } from "react";
import { notFound } from "next/navigation";
import { SiteFooter } from "@/components/navigation/SiteChrome";
import { isLocale, HTML_LANG, t } from "@/lib/i18n";
import "../../globals.css";

/**
 * Root layout for the localized library tree (`/zh-TW/…`, `/en/…`).
 * The rendered language is derived from the URL path only — never from
 * browser preferences or storage.
 *
 * The site header is rendered by each page (not here) because the
 * language switch target depends on the current book/entry context,
 * which only pages know.
 */
export default async function LocaleLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) {
    notFound();
  }
  const s = t(locale);
  return (
    <html lang={HTML_LANG[locale]} data-scroll-behavior="smooth">
      <body className="flex min-h-screen flex-col">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded focus:bg-accent focus:px-4 focus:py-2 focus:text-white"
        >
          {s.skipToContent}
        </a>
        {children}
        <SiteFooter locale={locale} />
      </body>
    </html>
  );
}
