import type { APIRoute } from "astro";
import { getCollection } from "astro:content";

const SITE = "https://sekolah-ai.my.id";

const esc = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

export const GET: APIRoute = async () => {
  const posts = (await getCollection("blog")).sort(
    (a, b) => b.data.date.valueOf() - a.data.date.valueOf()
  );

  const items = posts
    .map(
      (p) => `    <item>
      <title>${esc(p.data.title)}</title>
      <link>${SITE}/blog/${p.id}/</link>
      <guid>${SITE}/blog/${p.id}/</guid>
      <description>${esc(p.data.description)}</description>
      <pubDate>${p.data.date.toUTCString()}</pubDate>
    </item>`
    )
    .join("\n");

  const body = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Sekolah AI</title>
    <link>${SITE}/</link>
    <description>Artikel, tutorial, dan wawasan seputar kecerdasan buatan.</description>
    <language>id-ID</language>
${items}
  </channel>
</rss>
`;

  return new Response(body, {
    headers: { "Content-Type": "application/rss+xml; charset=utf-8" },
  });
};