// Copies the page base from src/ to dist/ and adds the libraries pages load
// from /lib/. Published pages reference these files by absolute path.
import { cpSync, rmSync } from "node:fs";

const libraries = {
  "tailwind.js": "node_modules/@tailwindcss/browser/dist/index.global.js",
  "chart.js": "node_modules/chart.js/dist/chart.umd.min.js",
  "lucide.js": "node_modules/lucide/dist/umd/lucide.min.js",
  "inter.woff2": "node_modules/@fontsource-variable/inter/files/inter-latin-wght-normal.woff2",
};

rmSync("dist", { recursive: true, force: true });
cpSync("src", "dist", { recursive: true });
for (const [name, source] of Object.entries(libraries)) cpSync(source, `dist/lib/${name}`);
console.log("Built dist/");
