import Link from "next/link";
import { LanguageSwitcher } from "@/components/navigation/LanguageSwitcher";
import { entryRoute, homeRoute, bookRoute } from "@/lib/routing";
import { t, type Locale, LOCALES, SITE_NAME } from "@/lib/i18n";
import { isPublished } from "@/lib/content";

/**
 * Locale-aware site header. The language switch target points to the
 * same book/entry in the other language when a published translation
 * exists; otherwise it renders an explicitly unavailable state.
 */
export function SiteHeader({
  locale,
  currentBookId,
  currentEntryId,
}: {
  locale: Locale;
  currentBookId?: string;
  currentEntryId?: string;
}) {
  const s = t(locale);
  const other = LOCALES.find((l) => l !== locale)!;

  let targetHref = homeRoute(other);
  let translationAvailable = true;
  if (currentBookId && currentEntryId) {
    translationAvailable = isPublished(currentBookId, currentEntryId, other);
    targetHref = entryRoute(other, currentBookId, currentEntryId);
  } else if (currentBookId) {
    targetHref = bookRoute(other, currentBookId);
  }

  return (
    <header className="no-print sticky top-0 z-30 border-b border-line bg-paper/92 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3 md:px-6">
        <Link
          href={homeRoute(locale)}
          className="flex items-baseline gap-2 font-serif text-base text-ink md:text-lg"
        >
          <span aria-hidden="true" className="text-accent">
            ◈
          </span>
          <span className="tracking-wide">{SITE_NAME[locale]}</span>
          <span className="hidden text-xs text-ink-faint sm:inline">
            {locale === "zh-TW" ? "Spiritual Awakening Library" : "靈性覺醒圖書館"}
          </span>
        </Link>
        <nav aria-label={locale === "zh-TW" ? "網站導覽" : "Site navigation"} className="ml-auto">
          <ul className="flex flex-wrap items-center gap-x-5 gap-y-1 text-sm">
            <li>
              <Link
                href={homeRoute(locale)}
                className="text-ink-soft transition-colors hover:text-accent-deep"
              >
                {s.navHome}
              </Link>
            </li>
            <li>
              <Link
                href={bookRoute(locale, "book-1")}
                className="text-ink-soft transition-colors hover:text-accent-deep"
              >
                {locale === "zh-TW" ? "《要開悟，讀這本書就夠了》" : "Book 1"}
              </Link>
            </li>
            <li>
              <Link
                href={bookRoute(locale, "book-2")}
                className="text-ink-soft transition-colors hover:text-accent-deep"
              >
                {locale === "zh-TW" ? "《靈性覺醒》" : "Book 2"}
              </Link>
            </li>
            <li>
              <LanguageSwitcher
                currentLocale={locale}
                targetLocale={other}
                targetHref={targetHref}
                translationAvailable={translationAvailable}
                unavailableTitle={s.langSwitchUnavailableTitle}
                targetLabel={s.switchLanguageTo}
              />
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}

export function SiteFooter({ locale }: { locale: Locale }) {
  const s = t(locale);
  return (
    <footer className="mt-auto border-t border-line bg-paper-deep/60">
      <div className="mx-auto max-w-6xl px-4 py-8 text-xs leading-relaxed text-ink-soft md:px-6">
        <p>{s.footerProject}</p>
        <p className="mt-1.5">{s.footerSource}</p>
        <p className="mt-1.5">{s.footerRights}</p>
        <p className="mt-3 text-ink-faint">{s.footerPhase} ・ Phase 1 · 2026-11-02</p>
      </div>
    </footer>
  );
}
