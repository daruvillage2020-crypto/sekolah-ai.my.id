// Lightweight TF-IDF related-post finder (build-time, no deps).
// Finds semantically similar articles by shared significant keywords.

export interface PostLike {
  id: string;
  data: {
    title: string;
    description?: string;
    date: Date;
  };
}

const STOPWORDS = new Set([
  "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "pada", "adalah", "ini",
  "itu", "atau", "juga", "akan", "bisa", "dapat", "tidak", "dalam", "sebagai",
  "kita", "anda", "mereka", "saya", "kami", "agar", "oleh", "harus", "lebih",
  "the", "a", "an", "of", "to", "in", "for", "and", "or", "is", "are", "be",
  "with", "on", "by", "as", "at", "it", "this", "that", "from", "how", "what",
]);

function tokens(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\u00c0-\u024f\s-]/gi, " ")
    .split(/[\s-]+/)
    .filter((w) => w.length > 2 && !STOPWORDS.has(w) && !/^\d+$/.test(w));
}

export function tokenSet(p: PostLike): string[] {
  return tokens(`${p.data.title} ${p.data.description ?? ""}`.repeat(3));
}

/** Return top-N most similar posts (excluding `current`). */
export function relatedPosts(current: PostLike, all: PostLike[], n = 3): PostLike[] {
  const docs = all.map((p) => ({ post: p, toks: tokenSet(p) }));
  const N = docs.length;
  if (N <= 1) return [];

  // Document frequency per term
  const df = new Map<string, number>();
  for (const d of docs) {
    for (const t of new Set(d.toks)) df.set(t, (df.get(t) ?? 0) + 1);
  }

  const curToks = tokenSet(current);
  const curTf = new Map<string, number>();
  for (const t of curToks) curTf.set(t, (curTf.get(t) ?? 0) + 1);

  const idf = (t: string) => Math.log((N + 1) / ((df.get(t) ?? 0) + 1)) + 1;

  const scored = docs
    .filter((d) => d.post.id !== current.id)
    .map((d) => {
      const dTf = new Map<string, number>();
      for (const t of d.toks) dTf.set(t, (dTf.get(t) ?? 0) + 1);
      // cosine-ish overlap weighted by idf
      let score = 0;
      for (const [t, c] of curTf) {
        const occ = dTf.get(t);
        if (occ) score += (c * occ) * idf(t) * idf(t);
      }
      // gentle recency nudge so fresh posts surface on ties
      const days = Math.abs(d.post.data.date.valueOf() - current.data.date.valueOf()) / 86400000;
      score += 0.5 / (1 + days / 30);
      return { post: d.post, score };
    })
    .sort((a, b) => b.score - a.score);

  return scored.slice(0, n).map((s) => s.post);
}