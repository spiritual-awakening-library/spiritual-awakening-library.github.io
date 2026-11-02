"use client";

import { useEffect, useSyncExternalStore } from "react";

/**
 * Adjustable reading font size.
 *
 * The preference is persisted in the browser and applied only to the
 * reading surface — it never changes the requested language or route.
 * Uses `useSyncExternalStore` (the SSR-safe pattern for client-
 * persisted state): the server snapshot is always the default, so
 * hydration stays consistent.
 */
const SIZES = [0.9375, 1, 1.0625, 1.1875, 1.3125, 1.5]; // rem
const DEFAULT_INDEX = 2;
const STORAGE_KEY = "sal-reading-size-index";

let cachedIndex: number | null = null;
const listeners = new Set<() => void>();

function readIndex(): number {
  if (cachedIndex === null) {
    try {
      const saved = window.localStorage.getItem(STORAGE_KEY);
      const n = saved === null ? DEFAULT_INDEX : Number(saved);
      cachedIndex =
        Number.isInteger(n) && n >= 0 && n < SIZES.length ? n : DEFAULT_INDEX;
    } catch {
      cachedIndex = DEFAULT_INDEX;
    }
  }
  return cachedIndex;
}

function writeIndex(next: number): void {
  cachedIndex = next;
  try {
    window.localStorage.setItem(STORAGE_KEY, String(next));
  } catch {
    /* storage unavailable — keep in-memory only */
  }
  document.documentElement.style.setProperty(
    "--reading-size",
    `${SIZES[next]}rem`,
  );
  for (const listener of listeners) {
    listener();
  }
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

function getSnapshot(): number {
  return readIndex();
}

function getServerSnapshot(): number {
  return DEFAULT_INDEX;
}

export function FontSizeControl({
  labels,
}: {
  labels: { group: string; smaller: string; larger: string; reset: string };
}) {
  const index = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  // Apply the persisted size to the reading surface after mount.
  useEffect(() => {
    document.documentElement.style.setProperty(
      "--reading-size",
      `${SIZES[readIndex()]}rem`,
    );
  }, []);

  const change = (delta: number) => {
    const next = Math.min(SIZES.length - 1, Math.max(0, index + delta));
    if (next !== index) {
      writeIndex(next);
    }
  };

  return (
    <div
      role="group"
      aria-label={labels.group}
      className="no-print inline-flex items-center gap-1 rounded-full border border-line bg-block p-1"
    >
      <button
        type="button"
        onClick={() => change(-1)}
        disabled={index === 0}
        aria-label={labels.smaller}
        title={labels.smaller}
        className="h-8 w-8 rounded-full text-sm text-ink-soft transition-colors hover:bg-accent-wash hover:text-accent-deep disabled:opacity-35"
      >
        <span aria-hidden="true">A−</span>
      </button>
      <button
        type="button"
        onClick={() => writeIndex(DEFAULT_INDEX)}
        aria-label={labels.reset}
        title={labels.reset}
        className="h-8 min-w-12 rounded-full text-xs text-ink-soft transition-colors hover:bg-accent-wash hover:text-accent-deep"
      >
        <span aria-hidden="true">A</span>
      </button>
      <button
        type="button"
        onClick={() => change(1)}
        disabled={index === SIZES.length - 1}
        aria-label={labels.larger}
        title={labels.larger}
        className="h-8 w-8 rounded-full text-base text-ink-soft transition-colors hover:bg-accent-wash hover:text-accent-deep disabled:opacity-35"
      >
        <span aria-hidden="true">A+</span>
      </button>
    </div>
  );
}
