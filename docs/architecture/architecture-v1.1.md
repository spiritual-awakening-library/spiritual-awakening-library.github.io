# Spiritual Awakening Library — Architecture v1.1

**Status:** approved planning baseline; not an implementation or test result. Date: 2026-11-02.

## Intended experience
- An elegant, calm, warm-paper library home page with two original book covers and entry links.
- Each book has a scannable contents page with descriptions and a direct link to its opening entry.
- Every published chapter/entry has its own page, previous/next navigation, table of contents, and zh-TW/English toggle.
- Read-only, static, no account, no database; keyboard, touch and screen-reader friendly.

## URL contract
- `/`: language-selecting library landing page with stable crawlable links to both localized libraries (do not automatically redirect based on localStorage).
- `/zh-TW/`, `/en/`: localized home pages.
- `/{locale}/books/{bookId}/`: complete book TOC in that language.
- `/{locale}/books/{bookId}/{entryId}/`: one published chapter or original entry.
- Stable bookId values `book-1`, `book-2`; stable content/entry IDs independent of translated titles. Use `trailingSlash: true` consistently.
- A route only exists if that language's content is actually approved. No empty English placeholder pages; no hreflang to nonexistent equivalents.

## Suggested Next.js code layout (implementation is not included)
```
src/
  app/
    (landing)/layout.tsx
    (landing)/page.tsx
    [locale]/layout.tsx
    [locale]/page.tsx
    [locale]/books/[bookId]/page.tsx
    [locale]/books/[bookId]/[entryId]/page.tsx
    sitemap.ts
    robots.ts
  components/{reader,library,navigation,seo}/
  content/{book-1,book-2}/{zh-TW,en}/
  data/{books,entries,terminology}/
  lib/{content,i18n,routing,seo}/
scripts/{validate-content,validate-static,validate-security}/
tests/{content,i18n,routes,e2e}/
public/covers/
docs/{architecture,editorial,milestones,verification}/
.github/workflows/{pr-validation,deploy}.yml
```

## Rendering and language
- Pre-generate routes using `generateStaticParams` for locale, bookId and entryId combinations; pre-render all approved main text into static HTML, not only client JavaScript.
- Generate localized HTML `lang`, `title`, `description`, canonical (self) and reciprocal `hreflang` for *existing* equivalents. `x-default` may point to the language-neutral library landing page.
- Source of truth for rendered language is URL path, never browser `localStorage`.
- Maintain canonical entry ID and paragraph ID mapping across languages. At switch time, identify the **actually visible** paragraph via observation/scroll tracking, not only a stale hash. Preserve top-of-page cases. If missing equivalent, present a non-breaking status message.
- Use one shared content renderer and route-aware localized data; keep reader state distinct from source text. Avoid hydration mismatch.

## Content contracts
- Book and entry registry is immutable-ID-based and ordered. Include original title, original printed page, author, source/version ID, editorial type (preface/chapter/essay/testimonial/etc.), source review status, English translation status and license/publication status.
- Paragraph IDs are stable and unique within an entry; translation paragraphs map to original IDs with explicit notes for splits/merges. Never silently alter the zh-TW source text to accommodate translation.
- Keep a SHA-256 checksum for each immutable source PDF and publication/edition details in an internal evidence manifest; only publish rights-cleared references.
- Store correction ledgers, terminology decisions, source/translation version IDs and reviewer notes. Preserve accurate provenance of spiritual/scientific statements without recasting belief claims as verified science.

## Deployment and security
- Full Next.js development source belongs in Git; generated `out/`, `.next/`, `node_modules/`, local credentials, AI sandbox logs and caches do not.
- PR checks: `npm ci` → TypeScript → ESLint → content schema & source tests → i18n parity/route tests → clean static export → inspect every generated HTML, canonical, hreflang and sitemap link → security inspection.
- PR CI grants only minimum read permissions and **never deploys**; deploy on reviewed/merged `main`, from a fresh verified build. Use branch protection and required CI reviews.
- Normalize path checks across Windows and Linux via POSIX paths (`Path.as_posix()` or equivalent), and test on both where feasible.
- Compare actual and expected rendered routes, including only reviewed/published languages. No disabling checks to make a build pass.
- Release requires smoke tests: direct URL, reload, back/forward, language switch in scrolled state, phone touch, keyboard, accessibility, structured metadata, 404s, and link integrity.

## Phases and stop-gates
0. Rights clearance; cryptographic source evidence; full inventory (no publication yet).
1. Scaffold and two one-entry reader prototypes, no large content import.
2. i18n, paragraph location, metadata and hard PR CI gates.
3. Correct and independently proofread complete zh-TW source.
4. Translate and review every corresponding English entry.
5. Public release verification, Search Console and documented milestone.

**Hard gate:** until written rights clearance is confirmed, no full text, translation or cover materials are posted publicly.
