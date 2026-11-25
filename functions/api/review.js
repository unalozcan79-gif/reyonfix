// Müşteri yorumları — GET ?pid=slug : onaylı yorumlar · POST : yeni yorum (onay bekler)
// KV bağlaması: REVIEWS   anahtarlar: r:<pid> = onaylı dizi, p:<id> = bekleyen
const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
const PID = /^[a-z0-9-]{2,80}$/;
const clean = (s, n) => String(s || "").replace(/[\u0000-\u001f\u007f<>]/g, " ").replace(/\s+/g, " ").trim().slice(0, n);

export async function onRequestGet({ request, env }) {
  const pid = new URL(request.url).searchParams.get("pid") || "";
  if (!PID.test(pid)) return J({ error: "pid" }, 400);
  if (!env.REVIEWS) return J({ reviews: [], setup: false });
  const list = (await env.REVIEWS.get("r:" + pid, "json")) || [];
  return new Response(JSON.stringify({ reviews: list }), { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "public, max-age=60" } });
}

export async function onRequestPost({ request, env }) {
  if (!env.REVIEWS) return J({ error: "setup" }, 503);
  let b; try { b = await request.json(); } catch { return J({ error: "json" }, 400); }
  if (b.hp) return J({ ok: true });                                   // bot tuzağı
  if (!b.t || Date.now() - Number(b.t) < 4000) return J({ error: "fast" }, 400);
  const pid = String(b.pid || ""), rating = Math.round(Number(b.rating));
  const name = clean(b.name, 60), org = clean(b.org, 80), text = clean(b.text, 1500), pname = clean(b.pname, 160);
  const lang = ["tr", "en", "de", "fr", "ar"].includes(b.lang) ? b.lang : "tr";
  if (!PID.test(pid) || !(rating >= 1 && rating <= 5) || name.length < 2 || text.length < 10) return J({ error: "invalid" }, 400);
  if ((text.match(/https?:\/\//g) || []).length > 1) return J({ error: "links" }, 400);
  const ip = request.headers.get("cf-connecting-ip") || "x";
  const ipk = "ip:" + ip, n = Number(await env.REVIEWS.get(ipk)) || 0;
  if (n >= 5) return J({ error: "limit" }, 429);
  await env.REVIEWS.put(ipk, String(n + 1), { expirationTtl: 86400 });
  const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  const rec = { id, pid, pname, name, org, rating, text, lang, date: new Date().toISOString().slice(0, 10), country: request.cf && request.cf.country || "" };
  await env.REVIEWS.put("p:" + id, JSON.stringify(rec), { expirationTtl: 60 * 60 * 24 * 90 });
  return J({ ok: true });
}
