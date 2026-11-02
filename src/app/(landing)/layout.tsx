import type { ReactNode } from "react";
import "../globals.css";

/**
 * Root layout for the language-neutral landing page.
 * The landing page itself is bilingual; localized trees live under
 * (library)/[locale] with their own root layout.
 */
export default function LandingLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="zh-Hant" data-scroll-behavior="smooth">
      <body className="flex min-h-screen flex-col">{children}</body>
    </html>
  );
}
