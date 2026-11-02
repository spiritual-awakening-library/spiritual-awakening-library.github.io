import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/i18n";

/**
 * robots.txt — allow all crawlers, point at the sitemap.
 */
export const dynamic = "force-static";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
      },
    ],
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
