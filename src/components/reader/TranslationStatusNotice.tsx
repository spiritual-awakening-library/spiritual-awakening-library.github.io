import type { Locale } from "@/lib/i18n";
import { t } from "@/lib/i18n";

/**
 * Visible translation/source status notice for a reading page.
 * Keeps original text, translation, and editorial framing explicitly
 * separated. Draft translations are never presented as approved.
 */
export function TranslationStatusNotice({
  locale,
  variant,
}: {
  locale: Locale;
  variant: "original" | "draft-translation";
}) {
  const s = t(locale);
  if (variant === "draft-translation") {
    return (
      <aside
        role="note"
        aria-label={s.readerTranslationDraft}
        className="no-print mt-5 rounded-md border border-line-strong bg-accent-wash/70 px-4 py-3.5 text-[13px] leading-relaxed text-accent-deep"
      >
        <p className="font-medium">{s.readerTranslationDraft}</p>
        <p className="mt-1">{s.readerTranslationDraftBody}</p>
      </aside>
    );
  }
  return (
    <aside
      role="note"
      aria-label={s.readerOriginal}
      className="no-print mt-5 rounded-md border border-line bg-paper-deep/70 px-4 py-3.5 text-[13px] leading-relaxed text-ink-soft"
    >
      <p className="font-medium">{s.readerOriginal}</p>
      <p className="mt-1">{s.readerTranslationOriginalBody}</p>
    </aside>
  );
}
