import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

/**
 * Spiritual Awakening Library — ESLint configuration.
 * Standard Next.js core-web-vitals + TypeScript rules without
 * downgrades. Lint failures are fixed in code, never silenced.
 */
const eslintConfig = [
  ...nextCoreWebVitals,
  ...nextTypescript,
  {
    ignores: ["out/**", ".next/**", "node_modules/**"],
  },
];

export default eslintConfig;
