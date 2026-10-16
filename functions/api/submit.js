// Cloudflare Pages Function: handler form (kontak & newsletter).
// Menyimpan submission ke KV (binding FORMS) + opsional kirim notifikasi Telegram.
//
// Env opsional:
//   TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID  -> notifikasi tiap submission
//   FORMS (KV binding)                     -> arsip submission
//
// Netlify Forms diganti fungsi ini. Form HTML pakai name="kontak"/"newsletter".

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
  });

const esc = (s = "") => String(s).replace(/[<>&]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[c]));

export async function onRequestPost({ request, env }) {
  let form;
  const ct = request.headers.get("content-type") || "";
  try {
    if (ct.includes("application/json")) {
      form = await request.json();
    } else {
      const fd = await request.formData();
      form = Object.fromEntries(fd.entries());
    }
  } catch {
    return json({ ok: false, error: "Bad payload" }, 400);
  }

  // honeypot
  if (form["bot-field"]) return json({ ok: true });

  const kind = form["form-name"] || form.formName || "unknown";
  delete form["bot-field"];
  delete form["form-name"];

  const entry = { kind, at: new Date().toISOString(), ...form };

  // 1) Arsip ke KV
  if (env.FORMS) {
    try {
      const key = `${kind}:${Date.now()}:${Math.random().toString(36).slice(2, 8)}`;
      await env.FORMS.put(key, JSON.stringify(entry));
    } catch (e) {
      console.error("KV put failed", e);
    }
  }

  // 2) Notifikasi Telegram
  const tg = env.TELEGRAM_BOT_TOKEN;
  const chat = env.TELEGRAM_CHAT_ID;
  if (tg && chat) {
    const lines = Object.entries(form).map(([k, v]) => `<b>${esc(k)}</b>: ${esc(v)}`);
    const text = `📬 <b>Form ${esc(kind)}</b>\n${lines.join("\n")}`;
    try {
      await fetch(`https://api.telegram.org/bot${tg}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: chat, text, parse_mode: "HTML" }),
      });
    } catch (e) {
      console.error("TG notify failed", e);
    }
  }

  return json({ ok: true });
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