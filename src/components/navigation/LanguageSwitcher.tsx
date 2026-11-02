"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback } from "react";
import { readingProgress } from "@/lib/reading-progress";
import type { Locale } from "@/lib/i18n";

/**
 * Paragraph-preserving language switch.
 *
 * - Target URL is computed at click time from the actually-visible
 *   paragraph (observed while scrolling), not from a stale hash.
 * - When no translation exists for the current entry, the switch is
 *   rendered as an explicitly unavailable state (never a silent
 *   redirect to a different page).
 * - Browser language preferences never override the explicit URL.
 */
export function LanguageSwitcher({
  currentLocale,
  targetLocale,
  targetHref,
  translationAvailable,
  unavailableTitle,
  targetLabel,
}: {
  currentLocale: Locale;
  targetLocale: Locale;
  targetHref: string;
  translationAvailable: boolean;
  unavailableTitle: string;
  targetLabel: string;
}) {
  const router = useRouter();

  const handleClick = useCallback(
    (event: React.MouseEvent<HTMLAnchorElement>) => {
      if (!translationAvailable) return; // rendered as non-link below
      const paragraph = readingProgress.get();
      if (paragraph) {
        event.preventDefault();
        router.push(`${targetHref}#${paragraph}`);
      }
      // No visible paragraph (top of page): default navigation keeps
      // the reader at the top of the translated entry.
    },
    [translationAvailable, targetHref, router],
  );

  if (currentLocale === targetLocale) {
    return null;
  }

  if (!translationAvailable) {
    return (
      <span
        aria-disabled="true"
        title={unavailableTitle}
        className="inline-flex cursor-not-allowed items-center gap-1.5 rounded-full border border-line bg-paper-deep/60 px-3 py-1.5 text-sm text-ink-faint"
      >
        <span aria-hidden="true">◦</span>
        {targetLabel}
        <span className="sr-only"> — {unavailableTitle}</span>
      </span>
    );
  }

  return (
    <Link
      href={targetHref}
      onClick={handleClick}
      lang={targetLocale}
      className="inline-flex items-center gap-1.5 rounded-full border border-line-strong bg-block px-3 py-1.5 text-sm text-accent-deep transition-colors hover:bg-accent-wash"
    >
      <span aria-hidden="true">◇</span>
      {targetLabel}
    </Link>
  );
}
