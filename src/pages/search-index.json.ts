import type { APIRoute } from "astro";
import { getCollection } from "astro:content";

// Build-time search index: title + description + content chunks per post.
// Consumed by the client-side "Tanya AI" assistant (no backend needed).

const stripMd = (md: string) =>
  md
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`[^`]*`/g, " ")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/[*_>~#-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();

export const GET: APIRoute = async () => {
  const posts = await getCollection("blog");
  const idx = posts.map((p) => ({
    id: p.id,
    title: p.data.title,
    description: p.data.description ?? "",
    date: p.data.date.toISOString(),
    url: `/blog/${p.id}/`,
    text: stripMd(p.body ?? "").slice(0, 4000),
  }));

  return new Response(JSON.stringify(idx), {
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
};