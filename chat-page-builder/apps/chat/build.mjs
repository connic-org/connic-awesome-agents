// Copies the chat app from src/ to dist/ and adds the libraries it loads from /vendor/.
import { cpSync, rmSync } from "node:fs";

const vendor = {
  "marked.js": "node_modules/marked/lib/marked.esm.js",
  "purify.js": "node_modules/dompurify/dist/purify.es.mjs",
  "inter.woff2": "node_modules/@fontsource-variable/inter/files/inter-latin-wght-normal.woff2",
};

rmSync("dist", { recursive: true, force: true });
cpSync("src", "dist", { recursive: true });
for (const [name, source] of Object.entries(vendor)) cpSync(source, `dist/vendor/${name}`);
console.log("Built dist/");
