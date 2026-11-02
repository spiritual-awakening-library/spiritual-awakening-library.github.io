"use client";

import { useEffect } from "react";
import { readingProgress } from "@/lib/reading-progress";

/**
 * Tracks the currently visible paragraph for language switching.
 *
 * - An IntersectionObserver (rootMargin matching the reading focus
 *   zone) maintains the set of paragraphs intersecting the zone.
 * - Because `threshold: 0` only fires on enter/leave, a passive
 *   scroll listener recomputes the winner on every scroll event so
 *   the tracked paragraph reflects the settled position after smooth
 *   scrolling, not a stale intermediate one.
 * - On arrival with a paragraph hash (e.g. after a language switch),
 *   the target paragraph is scrolled into view.
 */
export function ReadingProgressTracker() {
  useEffect(() => {
    const paragraphs = Array.from(
      document.querySelectorAll<HTMLElement>("[data-para-id]"),
    );

    // Arrive-from-language-switch: scroll to the hashed paragraph.
    const hash = window.location.hash.replace(/^#/, "");
    if (hash) {
      const target = paragraphs.find((p) => p.dataset.paraId === hash);
      if (target) {
        requestAnimationFrame(() => {
          target.scrollIntoView({ block: "start" });
        });
      }
    }

    const visible = new Set<Element>();
    const update = () => {
      // Reading focus zone: upper-middle band of the viewport.
      const zoneTop = window.innerHeight * 0.12;
      const zoneBottom = window.innerHeight * 0.45;
      let best: { id: string; overlap: number } | null = null;
      for (const el of visible) {
        const rect = el.getBoundingClientRect();
        const overlap =
          Math.min(rect.bottom, zoneBottom) - Math.max(rect.top, zoneTop);
        if (overlap > 0 && (!best || overlap > best.overlap)) {
          best = { id: (el as HTMLElement).dataset.paraId!, overlap };
        }
      }
      readingProgress.setParagraph(best ? best.id : null);
      const doc = document.documentElement;
      const ratio =
        window.scrollY /
        Math.max(1, doc.scrollHeight - window.innerHeight);
      readingProgress.setScrollRatio(ratio);
    };

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            visible.add(entry.target);
          } else {
            visible.delete(entry.target);
          }
        }
        update();
      },
      { rootMargin: "-12% 0px -55% 0px", threshold: 0 },
    );

    for (const p of paragraphs) {
      observer.observe(p);
    }

    const onScroll = () => update();
    window.addEventListener("scroll", onScroll, { passive: true });

    update();

    return () => {
      observer.disconnect();
      window.removeEventListener("scroll", onScroll);
      readingProgress.reset();
    };
  }, []);

  return null;
}
