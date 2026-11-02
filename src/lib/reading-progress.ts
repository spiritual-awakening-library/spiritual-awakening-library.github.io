"use client";

/**
 * Lightweight module-level store for the currently visible paragraph.
 *
 * The reading article updates it via IntersectionObserver as the reader
 * scrolls; the language switcher reads it *at click time* so switching
 * preserves the actually-visible paragraph (never a stale URL hash).
 * A `null` value means "top of page / before the first paragraph".
 */
let currentParagraph: string | null = null;
let currentScrollRatio = 0;

export const readingProgress = {
  get(): string | null {
    return currentParagraph;
  },
  setParagraph(id: string | null): void {
    currentParagraph = id;
  },
  getScrollRatio(): number {
    return currentScrollRatio;
  },
  setScrollRatio(ratio: number): void {
    currentScrollRatio = ratio;
  },
  reset(): void {
    currentParagraph = null;
    currentScrollRatio = 0;
  },
};

/**
 * Debug/testing hook (client only). Exposes the currently tracked
 * paragraph on `window` for end-to-end tests; never used by UI logic.
 */
declare global {
  interface Window {
    __salReadingParagraph?: () => string | null;
  }
}

if (typeof window !== "undefined") {
  window.__salReadingParagraph = () => currentParagraph;
}
