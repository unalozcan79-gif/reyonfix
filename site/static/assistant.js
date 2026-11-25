/* Reyonfix yapay zekâ asistanı — tarayıcıda çalışır, ürün verisi /{dil}/search.json */
(function () {
  const T = window.AIT; if (!T) return;
  const $ = s => document.querySelector(s);
  const box = $("#ai"), body = $("#aib"), form = $("#aif"), inp = $("#aii"); if (!box) return;
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const norm = s => String(s).toLocaleLowerCase(T.lang).replace(/ı/g, "i").normalize("NFD").replace(/[̀-ًͯ-ٰٟ]/g, "")
    .replace(/ß/g, "ss").replace(/[أإآ]/g, "ا").replace(/ة/g, "ه").replace(/ى/g, "ي").replace(/[^\p{L}\p{N}]+/gu, " ").trim();
  const STOP = new Set("ve ile icin bir bu su o da de mi mu ne nasil var yok cok en gibi olan olarak istiyorum lazim arıyorum ariyorum the a an and or for of to in with i need want my is are der die das und fur mit ein eine ich le la les des et pour avec un une je".split(" "));
  const SYN = { manav: "sebze meyve", sebze: "manav meyve", meyve: "manav sebze", ekmek: "firin unlu", firin: "ekmek", zeytin: "zeytinlik", raf: "reyon", reyon: "raf",
    kasa: "banko", banko: "kasa tezgah", tezgah: "banko", dolap: "kabin", sarkuteri: "peynir", kuruyemis: "lokum" };
  let DATA = null;
  const load = () => DATA ? Promise.resolve(DATA) : fetch("/" + T.lang + "/search.json").then(r => r.json()).then(d => {
    DATA = d.map(x => ({ name: x[0], code: x[1], cat: x[2], path: x[3], img: x[4], desc: x[5], n: norm(x[0]), all: norm(x.join(" ")) })); return DATA; }).catch(() => (DATA = []));
  function search(q) {
    let t = norm(q).split(" ").filter(w => w.length > 1 && !STOP.has(w));
    if (T.lang === "tr") { const ex = []; t.forEach(w => { const k = Object.keys(SYN).find(s => w.startsWith(s)); if (k) ex.push(...SYN[k].split(" ")); }); t = t.concat(ex.map(w => "~" + w)); }
    if (!t.length) return [];
    return DATA.map(p => {
      let s = 0;
      t.forEach(w => { const syn = w[0] === "~", x = syn ? w.slice(1) : w, st = x.length > 4 ? x.slice(0, x.length - 1) : x;
        if (p.n.includes(st)) s += syn ? 2 : 5; else if (p.all.includes(st)) s += syn ? 1 : 2; });
      return [s, p];
    }).filter(a => a[0] > 0).sort((a, b) => b[0] - a[0]).slice(0, 4).map(a => a[1]);
  }
  const history = []; let greeted = false, last = [];
  const add = (html, who = "bot") => { const d = document.createElement("div"); d.className = "ai-m " + who; d.innerHTML = html; body.appendChild(d); body.scrollTop = body.scrollHeight; return d; };
  const pcard = p => `<a class="ai-p" href="${esc(p.path)}"><img src="${esc(p.img)}" alt="" loading="lazy"><span><b>${esc(p.name)}</b><small>${p.code ? `<span dir="ltr">${esc(p.code)}</span> · ` : ""}${esc(p.desc)}</small></span></a>`;
  const waLink = txt => `<a class="ai-wa" href="https://wa.me/${T.wa}?text=${encodeURIComponent(txt)}" target="_blank" rel="noopener">${esc(T.wa_btn)}</a>`;
  const chips = arr => `<div class="ai-chips">${arr.map(c => `<button type="button" data-chip="${esc(c)}">${esc(c)}</button>`).join("")}</div>`;
  function openAI(text) {
    box.hidden = false; document.body.classList.add("ai-open"); load();
    if (!greeted) { greeted = true; add(`<p>${esc(T.hi)}</p>` + chips(T.chips || [])); }
    if (text) ask(text); else setTimeout(() => inp.focus(), 50);
  }
  const closeAI = () => { box.hidden = true; document.body.classList.remove("ai-open"); };
  document.addEventListener("click", ev => {
    const t = ev.target.closest("[data-ai]"); if (t) { ev.preventDefault(); openAI(t.dataset.ai || ""); }
    const c = ev.target.closest("[data-chip]"); if (c) ask(c.dataset.chip);
  });
  $("#aifab").addEventListener("click", () => openAI());
  $("#aix").addEventListener("click", closeAI);
  document.addEventListener("keydown", ev => { if (ev.key === "Escape" && !box.hidden) closeAI(); });
  form.addEventListener("submit", ev => { ev.preventDefault(); const v = inp.value.trim(); if (v) { inp.value = ""; ask(v); } });
  function reply(text) {
    const n = " " + norm(text) + " ", out = { html: "", products: [] };
    const has = k => (T[k] || []).some(x => n.includes(norm(x)));
    if (has("k_price")) out.html = `<p>${T.price}</p>`;
    else if (has("k_contact")) out.html = `<p><b>${esc(T.phone)}:</b> <span dir="ltr">${esc(T.phone_v)}</span><br><b>WhatsApp:</b> <span dir="ltr">${esc(T.mobile_v)}</span><br><b>${esc(T.email)}:</b> ${esc(T.email_v)}<br><b>${esc(T.address)}:</b> ${esc(T.address_v)}</p>`;
    else if (has("k_ship")) out.html = `<p>${esc(T.ship)}</p>`;
    else if (has("k_draw")) out.html = `<p>${esc(T.draw)}</p>`;
    const prods = search(text);
    if (prods.length) {
      out.products = prods;
      out.html += `<p>${esc(out.html ? T.more : T.best)}</p>` + prods.map(pcard).join("");
      const tips = []; if (has("k_ss")) tips.push(T.t_ss); if (has("k_wood")) tips.push(T.t_wood);
      if (tips.length) out.html += tips.map(x => `<p>${esc(x)}</p>`).join("");
      out.html += `<p>${esc(T.measure)}</p>`;
    }
    if (!out.html) out.html = `<p>${esc(T.none)}</p>` + chips((T.chips || []).slice(0, 5));
    return out;
  }
  async function ask(text) {
    add(esc(text), "me"); history.push(text);
    const t = add(`<span class="ai-dot"></span><span class="ai-dot"></span><span class="ai-dot"></span>`);
    await load(); await new Promise(s => setTimeout(s, 300));
    const r = reply(text); if (r.products.length) last = r.products;
    const asks = history.slice(-3).map(x => "• " + x).join("\n");
    const prodLine = last.length ? "\n" + T.wa_prod + " " + last.map(p => p.name + (p.code ? ` (${p.code})` : "")).join(", ") : "";
    r.html += waLink(`${T.wa_intro}\n${asks}${prodLine}\n${T.wa_tail}`);
    t.innerHTML = r.html; body.scrollTop = body.scrollHeight;
  }
})();
