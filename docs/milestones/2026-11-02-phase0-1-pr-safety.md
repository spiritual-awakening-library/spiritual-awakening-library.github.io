# Phase 0.1 — PR-only Validation & Repository Safety Foundation

**Status:** proposed; merge and CI execution not yet verified.

This change introduces `.github/workflows/pr-validation.yml` and
`scripts/verify_foundation.py`. The validator checks tracked-file hygiene,
common credential patterns, and the **structure only** of the intentionally
incomplete `data/chapter-inventory-SEED-INCOMPLETE.csv`.

## Explicit boundaries
- `pull_request` only; never `pull_request_target`; no deploy or secrets.
- Read-only GitHub token permissions (`contents: read`); checkout does not persist credentials.
- Does not alter the book source, translation, existing README, or Pages settings.
- Does not assert complete inventory, translation correctness, legal rights, or web app quality.
- Static site TypeScript/build/SEO/browser tests are future Phase 1 work, once app source exists.

## Verification before merge
- Run `python scripts/verify_foundation.py` on the proposed branch.
- Review added files and staged diff (`git diff --cached --check`).
- Confirm PR checks pass on GitHub's clean Ubuntu runner.
- Review workflow permissions and ensure no deployment runs on the PR.

## Additional controls to consider
Pin GitHub Actions by reviewed full commit SHA as part of dependency hardening;
add automated tests for intentionally malformed fixture inventories. These are
not presented as already complete in Phase 0.1.
