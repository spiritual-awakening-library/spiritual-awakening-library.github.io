import type { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";
import { buildMetadata } from "@/lib/seo";
import { getBooksFile } from "@/lib/books";

/**
 * Language-selecting landing page (`/`).
 *
 * - Stable, crawlable links to both localized libraries (never an
 *   automatic redirect, never localStorage-driven).
 * - Shows both original book covers unaltered.
 */
export const metadata: Metadata = buildMetadata({
  path: "/",
  title: "靈性覺醒圖書館 · Spiritual Awakening Library",
  description:
    "江慶淇傳統中文著作的雙語數位圖書館原型：完整驗證目錄與選文閱讀。A bilingual digital library prototype preserving the Traditional Chinese works of Jiang Qingqi, with complete verified inventories and selected reading entries.",
  siblings: [
    { locale: "zh-TW", href: "/zh-TW/" },
    { locale: "en", href: "/en/" },
  ],
});

export default function LandingPage() {
  const { books, author } = getBooksFile();
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col items-center px-5 py-16 md:py-24">
      <p aria-hidden="true" className="text-accent">
        ◈
      </p>
      <h1 className="mt-4 text-center font-serif text-3xl tracking-wide text-ink md:text-4xl">
        靈性覺醒圖書館
      </h1>
      <p
        lang="en"
        className="mt-2 text-center font-serif text-lg text-ink-soft md:text-xl"
      >
        Spiritual Awakening Library
      </p>
      <p className="mt-4 max-w-xl text-center text-sm leading-relaxed text-ink-soft">
        江慶淇著作的雙語數位圖書館原型——完整驗證目錄，每書一篇選文。
        <br lang="zh-Hant" />
        <span lang="en">
          A bilingual reading prototype for the works of Jiang Qingqi — complete
          verified inventories, one reading entry per book.
        </span>
      </p>

      <div className="mt-10 grid w-full gap-4 sm:grid-cols-2">
        <Link
          href="/zh-TW/"
          lang="zh-Hant"
          className="group rounded-lg border border-line-strong bg-block px-6 py-6 text-center transition-colors hover:border-accent hover:bg-accent-wash"
        >
          <span className="block font-serif text-xl text-ink group-hover:text-accent-deep">
            進入繁體中文版
          </span>
          <span className="mt-1.5 block text-xs text-ink-faint">
            原文版本 · Source language
          </span>
        </Link>
        <Link
          href="/en/"
          lang="en"
          className="group rounded-lg border border-line bg-block px-6 py-6 text-center transition-colors hover:border-accent hover:bg-accent-wash"
        >
          <span className="block font-serif text-xl text-ink group-hover:text-accent-deep">
            Enter the English Library
          </span>
          <span className="mt-1.5 block text-xs text-ink-faint">
            Working language of the translations
          </span>
        </Link>
      </div>

      <section aria-labelledby="collection" className="mt-14 w-full">
        <h2
          id="collection"
          className="text-center text-sm font-medium tracking-widest text-ink-faint"
        >
          館藏兩書 · The Collection
        </h2>
        <p className="mt-2 text-center text-sm text-ink-soft">{author["zh-TW"]} 著 · by {author.en}</p>
        <div className="mt-6 grid gap-6 sm:grid-cols-2">
          {books.map((book) => (
            <figure key={book.id} className="overflow-hidden rounded-md border border-line bg-paper-deep">
              <Image
                src={book.cover}
                alt={book.cover_alt["zh-TW"]}
                width={1400}
                height={book.id === "book-1" ? 656 : 567}
                sizes="(min-width: 640px) 288px, 92vw"
                className="h-auto w-full object-contain"
              />
              <figcaption className="px-3 py-2.5 text-center text-xs text-ink-soft">
                《{book.title["zh-TW"]}》
                <span lang="en" className="ml-1.5 text-ink-faint">
                  · {book.title.en}
                </span>
              </figcaption>
            </figure>
          ))}
        </div>
      </section>

      <p className="mt-12 max-w-lg text-center text-[11px] leading-relaxed text-ink-faint">
        原型階段：尚未公開部署；正式授權條款以書面授權為準。
        <br lang="zh-Hant" />
        <span lang="en">Prototype — not yet publicly deployed; publication is subject to written authorization.</span>
      </p>
    </main>
  );
}
