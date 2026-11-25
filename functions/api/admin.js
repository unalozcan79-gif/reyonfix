// Yorum yönetimi — başlık: X-Admin-Key = ADMIN_KEY (Cloudflare'de gizli değişken)
const J = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
async function auth(request, env) {
  const k = request.headers.get("x-admin-key") || "";
  if (!env.ADMIN_KEY || env.ADMIN_KEY.length < 8) return "nokey";
  const a = new TextEncoder().encode(k), b = new TextEncoder().encode(env.ADMIN_KEY);
  if (a.length !== b.length) return "bad";
  let d = 0; for (let i = 0; i < a.length; i++) d |= a[i] ^ b[i];
  return d === 0 ? "" : "bad";
}
async function listAll(kv, prefix) {
  const out = []; let cursor;
  do { const r = await kv.list({ prefix, cursor }); out.push(...r.keys.map(k => k.name)); cursor = r.list_complete ? null : r.cursor; } while (cursor);
  return out;
}
export async function onRequestGet({ request, env }) {
  if (!env.REVIEWS) return J({ error: "setup" }, 503);
  const a = await auth(request, env); if (a) return J({ error: a }, a === "nokey" ? 503 : 401);
  const pk = await listAll(env.REVIEWS, "p:");
  const pending = (await Promise.all(pk.map(k => env.REVIEWS.get(k, "json")))).filter(Boolean).sort((x, y) => x.id < y.id ? 1 : -1);
  const rk = await listAll(env.REVIEWS, "r:");
  const approved = [];
  for (const k of rk) for (const r of (await env.REVIEWS.get(k, "json")) || []) approved.push(r);
  approved.sort((x, y) => x.date < y.date ? 1 : -1);
  return J({ pending, approved });
}
export async function onRequestPost({ request, env }) {
  if (!env.REVIEWS) return J({ error: "setup" }, 503);
  const a = await auth(request, env); if (a) return J({ error: a }, a === "nokey" ? 503 : 401);
  const { action, id, pid } = await request.json().catch(() => ({}));
  if (action === "approve") {
    const rec = await env.REVIEWS.get("p:" + id, "json"); if (!rec) return J({ error: "notfound" }, 404);
    const key = "r:" + rec.pid, list = (await env.REVIEWS.get(key, "json")) || [];
    const { country, ...pub } = rec;
    list.unshift(pub); await env.REVIEWS.put(key, JSON.stringify(list.slice(0, 200)));
    await env.REVIEWS.delete("p:" + id); return J({ ok: true });
  }
  if (action === "reject") { await env.REVIEWS.delete("p:" + id); return J({ ok: true }); }
  if (action === "remove") {
    const key = "r:" + pid, list = ((await env.REVIEWS.get(key, "json")) || []).filter(r => r.id !== id);
    if (list.length) await env.REVIEWS.put(key, JSON.stringify(list)); else await env.REVIEWS.delete(key);
    return J({ ok: true });
  }
  return J({ error: "action" }, 400);
}
