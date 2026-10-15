// OG image generator — runs on the VPS (sharp + DejaVu fonts available).
// Scans src/content/blog/*.md, generates public/og/<slug>.png for any post
// missing an OG image (or when content changed). Idempotent.

import sharp from "sharp";
import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const BLOG = join(ROOT, "src/content/blog");
const OG_DIR = join(ROOT, "public/og");

const W = 1200;
const H = 630;
const FONT = "DejaVu Sans, Noto Sans, Liberation Sans, sans-serif";

// Gradient themes per category (top-left -> bottom-right)
const THEMES = {
  ai: ["#4f46e5", "#0ea5e9"],
  coding: ["#0f172a", "#334155"],
  laptop: ["#1e293b", "#0f766e"],
  security: ["#111827", "#7c3aed"],
  school: ["#0369a1", "#0891b2"],
  education: ["#065f46", "#0d9488"],
  data: ["#312e81", "#2563eb"],
  tech: ["#1e3a8a", "#3b82f6"],
};

function categorize(title) {
  const t = title.toLowerCase();
  const words = new Set(t.split(/[^a-z0-9]+/));
  if (words.has("ai") || /kecerdasan buatan|neural|machine learning|deep learning|robot|chatbot|computer vision/.test(t)) return "ai";
  if (t.includes("laptop")) return "laptop";
  if (/password|keamanan|security|bobol|privasi|hacking|cyber/.test(t)) return "security";
  if (/website sekolah|gerbang pendidikan/.test(t)) return "school";
  if (/coding|programming|developer|programmer|koding/.test(t)) return "coding";
  if (/data|analisis|analytics|data science/.test(t)) return "data";
  if (/belajar|guru|siswa|modul ajar|pendidikan|pelajar|sekolah|kelas|kuliah/.test(t)) return "education";
  return "tech";
}

const esc = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");

function wrapTitle(title, maxChars = 26, maxLines = 4) {
  const words = title.split(/\s+/);
  const lines = [];
  let cur = "";
  for (const w of words) {
    if ((cur + " " + w).trim().length > maxChars && cur) {
      lines.push(cur.trim());
      cur = w;
    } else {
      cur = (cur + " " + w).trim();
    }
    if (lines.length === maxLines) break;
  }
  if (cur && lines.length < maxLines) lines.push(cur.trim());
  if (lines.length === maxLines && (lines.join(" ").length < title.length)) {
    lines[maxLines - 1] = lines[maxLines - 1].replace(/\s+\S*$/, "") + "…";
  }
  return lines;
}

function slugToFile(p) {
  return p.replace(/\.md$/, "");
}

function readMeta(file) {
  const raw = readFileSync(join(BLOG, file), "utf8");
  const fm = raw.split("---")[1] ?? "";
  const titleM = fm.match(/^title:\s*"?(.+?)"?\s*$/m);
  const descM = fm.match(/^description:\s*"?(.+?)"?\s*$/m);
  const title = titleM ? titleM[1].trim().replace(/^"|"$/g, "") : file.replace(/\.md$/, "");
  const desc = descM ? descM[1].trim().replace(/^"|"$/g, "") : "";
  return { title, desc, raw };
}

function buildSvg(title, category) {
  const [c1, c2] = THEMES[category] ?? THEMES.tech;
  const lines = wrapTitle(title);
  const lineH = 74;
  const startY = H / 2 - ((lines.length - 1) * lineH) / 2 + 10;
  const tspans = lines
    .map((l, i) => `<tspan x="80" y="${startY + i * lineH}">${esc(l)}</tspan>`)
    .join("");

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="${c1}"/>
      <stop offset="100%" stop-color="${c2}"/>
    </linearGradient>
  </defs>
  <rect width="${W}" height="${H}" fill="url(#bg)"/>
  <circle cx="1080" cy="120" r="220" fill="#ffffff" opacity="0.06"/>
  <circle cx="120" cy="560" r="160" fill="#ffffff" opacity="0.05"/>
  <rect x="80" y="70" width="56" height="56" rx="14" fill="#ffffff" opacity="0.16"/>
  <text x="80" y="150" font-family="${FONT}" font-size="30" font-weight="bold" fill="#ffffff" opacity="0.95">Sekolah AI</text>
  <text font-family="${FONT}" font-size="60" font-weight="bold" fill="#ffffff">${tspans}</text>
  <text x="80" y="${H - 60}" font-family="${FONT}" font-size="26" fill="#ffffff" opacity="0.85">sekolah-ai.my.id</text>
  <text x="${W - 80}" y="${H - 60}" font-family="${FONT}" font-size="26" fill="#ffffff" opacity="0.7" text-anchor="end">Belajar Kecerdasan Buatan</text>
</svg>`;
}

async function main() {
  if (!existsSync(OG_DIR)) mkdirSync(OG_DIR, { recursive: true });
  const files = readdirSync(BLOG).filter((f) => f.endsWith(".md"));
  let made = 0;
  for (const file of files) {
    const slug = slugToFile(file);
    const out = join(OG_DIR, `${slug}.png`);
    if (existsSync(out)) continue; // idempotent: skip existing
    const { title } = readMeta(file);
    const svg = buildSvg(title, categorize(title));
    await sharp(Buffer.from(svg)).png().toFile(out);
    made++;
    console.log(`  🖼️  OG: ${slug}.png`);
  }
  console.log(`OG images: ${made} generated, ${files.length - made} already existed.`);
}

main().catch((e) => {
  console.error("OG generation failed:", e);
  process.exit(1);
});