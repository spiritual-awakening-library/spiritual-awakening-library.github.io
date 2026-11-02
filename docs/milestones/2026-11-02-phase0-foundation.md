# 2026-11-02 — Project 09 Phase 0 foundation

**Project:** Spiritual Awakening Library／靈性覺醒圖書館

## Decisions
- Separate public-interest project from Living Awakening (selective guide versus full original texts).
- Planned GitHub Organization: `spiritual-awakening-library`; planned Pages repository: `spiritual-awakening-library.github.io`.
- Site design: warm-paper library aesthetics; first-chapter entry plus scrollable TOC, two books.
- Two-language static routes, per-entry SEO, language switch preserves visible paragraph when possible.
- Full source in public Git history only after secrets/rights sanitization; PR-only protected integration.

## Evidence and constraints
- User-provided source: two book interior PDFs and two cover PDFs. Main book's TOC enumerates 82 開悟 chapters. Book 2's full TOC inventory is **not yet complete**.
- User-provided lessons from seven prior technical notes incorporated: independent URLs for locale/content, static HTML SEO, route layout, scroll-aware language switch, full source control, Windows portable checks, and PR/security workflow.
- New GitHub repository is shown as *available* on screenshot; its creation is not confirmed in this deliverable.
- Domain screenshot lists `spiritual-awakening-library.com` at USD 11.81/year, renewing at USD 11.81/year at time shown; purchase is **not confirmed**.
- No code build, translation, copyright clearance, deployment or live testing has been performed for this repository.

## Next decision gates
1. Create repository Public; README On; `.gitignore` Node; No license pending separated rights decisions.
2. Obtain/document online publication + translation permission for both books, cover art, and any incorporated third-party text/images.
3. Verify both complete tables of contents and edition metadata, compile the final entry manifest.
4. Open scoped Phase 1 PR for reusable Next.js shell + one demonstration entry from each book, if publication rights are cleared.
5. Keep PR CI verification-only; merge only after review and checks, then activate deployment.
