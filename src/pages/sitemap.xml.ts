import type { APIRoute } from "astro";
import { getCollection } from "astro:content";

const SITE = "https://sekolah-ai.my.id";

export const GET: APIRoute = async () => {
  const posts = await getCollection("blog");
  const events = await getCollection("events");
  const staticPages = ["", "tentang", "produk", "komunitas", "kontak", "blog", "newsletter", "agenda"];

  const urls = [
    ...staticPages.map((p) => (p === "" ? `${SITE}/` : `${SITE}/${p}/`)),
    ...posts.map((p) => `${SITE}/blog/${p.id}/`),
    ...events.map((e) => `${SITE}/agenda/${e.id}/`),
  ];

  const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map((u) => `  <url><loc>${u}</loc></url>`).join("\n")}
</urlset>
`;

  return new Response(body, {
    headers: { "Content-Type": "application/xml; charset=utf-8" },
  });
};