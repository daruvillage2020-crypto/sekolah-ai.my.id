// Cloudflare Pages Function: LLM backend untuk "Tanya AI".
// Env: AI_BASE_URL + AI_API_KEY (gateway OpenAI-compatible), AI_MODEL.
// Fallback: GEMINI_API_KEY (Google Gemini langsung).

const SYSTEM = `Kamu adalah asisten ramah website Sekolah AI Indonesia (sekolah-ai.my.id).
Jawab pertanyaan pengunjung HANYA berdasarkan konteks artikel yang diberikan.
Jika konteks tidak cukup, katakan dengan jujur dan sarankan membaca blog di /blog.
Jawab singkat (maks 120 kata), dalam Bahasa Indonesia, ramah, tanpa emoji berlebihan.`;

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
  });

async function viaGateway(base, key, model, prompt) {
  const res = await fetch(`${base.replace(/\/$/, "")}/chat/completions`, {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      model,
      messages: [
        { role: "system", content: SYSTEM },
        { role: "user", content: prompt },
      ],
      temperature: 0.6,
      max_tokens: 700,
    }),
  });
  const data = await res.json().catch(() => ({}));
  return data?.choices?.[0]?.message?.content?.trim() || null;
}

async function viaGemini(key, prompt) {
  const model = "gemini-2.5-flash";
  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: `${SYSTEM}\n\n${prompt}` }] }],
        generationConfig: {
          temperature: 0.6,
          maxOutputTokens: 1024,
          thinkingConfig: { thinkingBudget: 0 },
        },
      }),
    }
  );
  const data = await res.json().catch(() => ({}));
  return data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || null;
}

export async function onRequestPost({ request, env }) {
  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "Bad JSON" }, 400);
  }

  const { question = "", context = "" } = body || {};
  if (!question.trim()) return json({ answer: null });

  const prompt = `KONTEKS ARTIKEL:\n${context.slice(0, 12000)}\n\nPERTANYAAN: ${question}\n\nJAWABAN:`;

  const base = env.AI_BASE_URL;
  const aiKey = env.AI_API_KEY;
  const model = env.AI_MODEL || "deepseek-v4.1-flash:netra";
  const gemKey = env.GEMINI_API_KEY;

  try {
    let answer = null;
    if (base && aiKey) answer = await viaGateway(base, aiKey, model, prompt);
    if (!answer && gemKey) answer = await viaGemini(gemKey, prompt);
    return json({ answer });
  } catch (e) {
    return json({ answer: null, error: String(e) }, 500);
  }
}

export const onRequestOptions = () =>
  new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
