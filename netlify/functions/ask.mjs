// Netlify Function: optional LLM upgrade untuk "Tanya AI".
// Aktif otomatis kalau env GEMINI_API_KEY diset di Netlify.
// Tanpa key, widget tetap jalan pakai search lokal (client-side).

export default async (request) => {
  if (request.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  const key = process.env.GEMINI_API_KEY;
  if (!key) {
    return new Response(JSON.stringify({ answer: null, reason: "no_key" }), {
      headers: { "Content-Type": "application/json" },
    });
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: "Bad JSON" }), { status: 400 });
  }

  const { question = "", context = "" } = body || {};
  if (!question.trim()) {
    return new Response(JSON.stringify({ answer: null }), {
      headers: { "Content-Type": "application/json" },
    });
  }

  const model = "gemini-2.5-flash";
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`;

  const prompt = `Kamu adalah asisten ramah website Sekolah AI Indonesia (sekolah-ai.my.id).
Jawab pertanyaan pengunjung HANYA berdasarkan konteks artikel berikut. Jika konteks tidak cukup, katakan dengan jujur dan sarankan mencari di blog.
Jawab singkat (maks 120 kata), dalam Bahasa Indonesia, ramah, tanpa emoji berlebihan.

KONTEKS ARTIKEL:
${context.slice(0, 12000)}

PERTANYAAN: ${question}

JAWABAN:`;

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: {
          temperature: 0.6,
          maxOutputTokens: 1024,
          // Matikan "thinking" — kalau tidak, budget output habis & jawaban kosong.
          thinkingConfig: { thinkingBudget: 0 },
        },
      }),
    });
    const data = await res.json();
    const answer =
      data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || null;
    return new Response(JSON.stringify({ answer }), {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });
  } catch (e) {
    return new Response(JSON.stringify({ answer: null, error: String(e) }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
};

export const config = { path: "/api/ask" };