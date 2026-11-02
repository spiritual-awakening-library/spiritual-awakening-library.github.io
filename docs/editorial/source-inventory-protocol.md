# Full-text inventory protocol

**No complete book-2 chapter inventory has been verified yet.** The accompanying CSV is an initial evidence-backed seed, not the full table of contents.

## Supplied source materials
- `印刷全文-要開悟讀這本書就夠了 (2)(2).pdf` — 325 PDF pages (visible PDF table of contents identifies 82 numbered 開悟 chapters; additional prefaces and testimonials).
- `內文-靈性覺醒 (2)(2).pdf` — 478 PDF pages (large, often vertically laid out table of contents; needs full sequential verification).
- `封面-要開悟讀這本書就夠了 (2)(2).pdf` — 1 PDF page of print cover art.
- `封面-靈性覺醒 (2)(2).pdf` — 1 PDF page of print cover art.

Do not copy original PDFs or cover art into a public repository before permission is recorded. Record SHA-256 and edition details in controlled source records.

## Inventory columns
`book_id,entry_id,entry_kind,order,original_title,printed_page,pdf_page,language,source_status,translation_status,review_notes`

All entries must be inventoried, **including** prefaces, interludes, subheadings, appendices and testimonies, not just numbered main chapters. PDF physical page != printed page; do not infer one from the other across an entire volume.

## Procedure
1. Record exact edition/publication details, rights and SHA-256.
2. Extract table of contents and original printed pages. For vertical/multi-column pages, manually compare PDF page images to extracted text; do not trust auto-order.
3. Record every entry with stable ID and explicit `entry_kind`, original title and exact evidence location.
4. Check TOC against page headings in the body, verify starts/ends and identify split or continued essays.
5. Run monotonic order and unique-ID checks, plus independent human completeness review.
6. Only after full verified inventory, begin transcription and bilingual publishing; never fabricate entries or pages to hit an expected total.

## Current verified *examples* (not exhaustive)
- Book 1: chapter 01 `本源與宇宙次元`, printed page 014, PDF page 8; TOC lists numbered chapter sequence through 82 `生命之流` (printed page 598, different from PDF physical page count because of printed 2-up layout).
- Book 1: chapters 22–24 include the three `神性基因` parts (printed pages need detailed mapping); chapter 14 is `生活才是你修行的重心`.
- Book 2: TOC includes `悟了之後` continuation series and `生活裡覺醒的第一步`, `生活裡覺醒的第二步`, `生活裡覺醒的第三步`.

## Explicit exclusions from 'verified complete'
Book 2 entry count, every printed page, every section break, and translation status remain **unverified** until comprehensive original PDF page review.
