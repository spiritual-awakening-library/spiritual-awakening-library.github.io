import type { Paragraph } from "@/lib/content";
import type { Locale } from "@/lib/i18n";

/**
 * The approved paragraph-block reading presentation.
 *
 * - The full original text is preserved without rewriting, omission,
 *   or reordering; every paragraph keeps its stable ID.
 * - Consecutive paragraphs are grouped ~2–4 per visual block. Blocks
 *   are presentational only — they never define paragraph identity
 *   (the <p id> does), so zh-TW and English blocks may group
 *   differently while paragraph mapping stays exact.
 * - No decorative headings are added; the block <section> carries an
 *   accessibility label only (never visible text).
 */
export function groupParagraphs(paragraphs: Paragraph[]): Paragraph[][] {
  const blocks: Paragraph[][] = [];
  let current: Paragraph[] = [];
  let chars = 0;
  for (const p of paragraphs) {
    current.push(p);
    chars += p.text.length;
    const enough = current.length >= 2 && chars >= 160;
    const tooMany = current.length >= 4;
    if (enough || tooMany) {
      blocks.push(current);
      current = [];
      chars = 0;
    }
  }
  if (current.length > 0) {
    if (current.length === 1 && blocks.length > 0 && blocks[blocks.length - 1].length < 4) {
      // A lone trailing paragraph joins the previous block rather than
      // floating in its own block (still keeps its own identity/ID).
      blocks[blocks.length - 1].push(current[0]);
    } else {
      blocks.push(current);
    }
  }
  return blocks;
}

export function ReadingBlock({
  paragraphs,
  locale,
  firstIndex = 0,
}: {
  paragraphs: Paragraph[];
  locale: Locale;
  firstIndex?: number;
}) {
  const blocks = groupParagraphs(paragraphs);

  // Precompute block ranges before rendering so the JSX stays pure.
  const ranges: Array<{ start: number; end: number }> = [];
  let cursor = firstIndex;
  for (const block of blocks) {
    ranges.push({ start: cursor, end: cursor + block.length - 1 });
    cursor += block.length;
  }

  const paragraphWord = locale === "zh-TW" ? "段落" : "Paragraphs";
  return (
    <div className="reading-surface mx-auto w-full" style={{ maxWidth: "var(--reading-measure)" }}>
      {blocks.map((block, blockIndex) => (
        <section
          key={blockIndex}
          className="reading-block"
          aria-label={`${paragraphWord} ${ranges[blockIndex].start + 1}–${ranges[blockIndex].end + 1}`}
        >
          {block.map((p) => (
            <p
              key={p.id}
              id={p.id}
              data-para-id={p.id}
              lang={locale}
              className="reading-para"
            >
              {p.text}
            </p>
          ))}
        </section>
      ))}
    </div>
  );
}
