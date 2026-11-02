#!/usr/bin/env python3
"""Phase 1 — static export verification.

Run after `npm run build`. Verifies the exported `out/` directory:

1. the exported route set exactly equals the expected route set
   (landing, localized homes, book directories, published reading
   pages — and nothing else, e.g. no English route for untranslated
   entries);
2. every HTML file declares the correct `lang` attribute;
3. every HTML file carries a self-referencing canonical URL;
4. hreflang alternates exactly match the expected reciprocal set per
   route (existing sibling languages required, untranslated languages
   forbidden, x-default present);
5. the sitemap lists exactly the exported routes;
6. robots.txt exists and references the sitemap;
7. reading pages contain their full paragraph text in static HTML
   (primary content requires no JavaScript);
8. cover images are present in the export.

Exit code 0 = all checks passed. Any failure prints details and exits 1.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
SITE = "https://spiritual-awakening-library.github.io"
FAILURES: list[str] = []
CHECKS = 0


def check(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        FAILURES.append(message)
        print(f"  FAIL: {message}")


def expected_routes() -> list[str]:
    routes = ["/"]
    registry = json.loads((ROOT / "data" / "published.json").read_text("utf-8"))
    books = [b["id"] for b in json.loads((ROOT / "data" / "books.json").read_text("utf-8"))["books"]]
    for locale in ("zh-TW", "en"):
        routes.append(f"/{locale}/")
        for book_id in books:
            routes.append(f"/{locale}/books/{book_id}/")
            for entry in registry["entries"]:
                if entry["book_id"] == book_id and locale in entry["locales"]:
                    routes.append(f"/{locale}/books/{book_id}/{entry['entry_id']}/")
    return routes


def expected_alternates(route: str) -> dict[str, str]:
    """The exact hreflang set each exported page must declare.

    - Landing and localized homes/directories: both languages.
    - Reading pages: only the locales the entry is actually published
      in (an untranslated entry must NOT announce an English page).
    - x-default always points to the language-neutral landing page.
    """
    registry = json.loads((ROOT / "data" / "published.json").read_text("utf-8"))
    alts: dict[str, str] = {"x-default": f"{SITE}/"}
    if route == "/":
        alts["zh-TW"] = f"{SITE}/zh-TW/"
        alts["en"] = f"{SITE}/en/"
        return alts
    parts = route.strip("/").split("/")
    locale = parts[0]
    other = "en" if locale == "zh-TW" else "zh-TW"
    alts[locale] = f"{SITE}{route}"
    if len(parts) == 1:
        # localized homepage — both exist
        alts[other] = f"{SITE}/{other}/"
    elif len(parts) == 3 and parts[1] == "books":
        # book directory — both exist
        alts[other] = f"{SITE}/{other}/books/{parts[2]}/"
    elif len(parts) == 4 and parts[1] == "books":
        # reading page — only published locales
        for entry in registry["entries"]:
            if entry["book_id"] == parts[2] and entry["entry_id"] == parts[3]:
                for sibling in entry["locales"]:
                    alts[sibling] = f"{SITE}/{sibling}/books/{parts[2]}/{parts[3]}/"
    return alts


def exported_routes() -> list[str]:
    routes = []
    for index in OUT.rglob("index.html"):
        relative = index.parent.relative_to(OUT).as_posix()
        routes.append("/" if relative == "." else f"/{relative}/")
    return sorted(set(routes))


# Next.js always emits these system routes/files; they are not part of
# the content route contract (out/404.html is the GitHub Pages 404).
SYSTEM_ROUTES = {"/_not-found/", "/404/"}


def main() -> int:
    if not OUT.is_dir():
        print("FAIL: out/ directory not found — run `npm run build` first")
        return 1

    expected = sorted(expected_routes())
    exported = exported_routes()

    # 1. exact route set (system routes excluded from the contract)
    content_routes = sorted(set(exported) - SYSTEM_ROUTES)
    check(content_routes == expected,
          f"route set mismatch: missing={sorted(set(expected) - set(content_routes))} "
          f"unexpected={sorted(set(content_routes) - set(expected))}")

    # 2-4. per-page HTML checks (system routes excluded)
    for route in sorted(set(exported) - SYSTEM_ROUTES):
        index_dir = OUT if route == "/" else OUT / route.strip("/")
        html = (index_dir / "index.html").read_text("utf-8")

        expected_lang = None
        if route == "/":
            expected_lang = 'lang="zh-Hant"'
        elif route.startswith("/zh-TW/"):
            expected_lang = 'lang="zh-Hant-TW"'
        elif route.startswith("/en/"):
            expected_lang = 'lang="en"'
        check(expected_lang is not None and expected_lang in html,
              f"{route}: wrong or missing lang attribute")

        canonical = f'<link rel="canonical" href="{SITE}{route}"/>'
        check(canonical in html or canonical.replace("/>", ">") in html,
              f"{route}: missing self-referencing canonical ({canonical})")

        # 4. exact reciprocal hreflang set (case covers both React
        #    serializations: hrefLang / hreflang — HTML is case-insensitive)
        actual_alts: dict[str, str] = {}
        for match in re.finditer(r'hrefLang="([^"]+)"\s+href="([^"]+)"', html, re.IGNORECASE):
            actual_alts[match.group(1)] = match.group(2)
        expected_alts = expected_alternates(route)
        check(actual_alts == expected_alts,
              f"{route}: hreflang set mismatch — "
              f"missing={ {k: v for k, v in expected_alts.items() if k not in actual_alts or actual_alts[k] != v} } "
              f"unexpected={ {k: v for k, v in actual_alts.items() if expected_alts.get(k) != v} }")

    # 5. sitemap
    sitemap_path = OUT / "sitemap.xml"
    check(sitemap_path.is_file(), "sitemap.xml missing in export")
    if sitemap_path.is_file():
        sitemap = sitemap_path.read_text("utf-8")
        sitemap_routes = sorted(re.findall(r"<loc>([^<]+)</loc>", sitemap))
        sitemap_local = sorted(r.removeprefix(SITE) for r in sitemap_routes)
        check(sitemap_local == expected,
              f"sitemap mismatch: missing={sorted(set(expected) - set(sitemap_local))} "
              f"unexpected={sorted(set(sitemap_local) - set(expected))}")

    # 6. robots.txt
    robots = OUT / "robots.txt"
    check(robots.is_file(), "robots.txt missing in export")
    if robots.is_file():
        check("Sitemap: https://spiritual-awakening-library.github.io/sitemap.xml"
              in robots.read_text("utf-8"), "robots.txt missing sitemap reference")

    # 7. no-JS content on reading pages
    registry = json.loads((ROOT / "data" / "published.json").read_text("utf-8"))
    for entry in registry["entries"]:
        for locale, pub in entry["locales"].items():
            content = json.loads((ROOT / pub["content"]).read_text("utf-8"))
            route = f"/{locale}/books/{entry['book_id']}/{entry['entry_id']}/"
            html = (OUT / route.strip("/") / "index.html").read_text("utf-8")
            for para in content["paragraphs"]:
                # static HTML must embed the paragraph text (React escapes
                # nothing in plain CJK/latin prose; check a stable prefix)
                prefix = para["text"][:24]
                check(prefix in html, f"{route}: paragraph {para['id']} text "
                                      f"not found in static HTML")
            # draft translation notice must be visible in static HTML
            if locale == "en":
                check("machine-assisted" in html,
                      f"{route}: draft translation notice missing")

    # 8. covers
    for book in json.loads((ROOT / "data" / "books.json").read_text("utf-8"))["books"]:
        cover = OUT / book["cover"].lstrip("/")
        check(cover.is_file(), f"cover missing in export: {book['cover']}")

    print()
    if FAILURES:
        print(f"static export validation FAILED: {len(FAILURES)} failure(s) "
              f"across {CHECKS} checks")
        return 1
    print(f"static export validation PASSED: {CHECKS} checks "
          f"({len(exported)} routes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
