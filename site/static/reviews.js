/* ---------- müşteri yorumları ---------- */
(function () {
  const box = document.getElementById("reviews"); if (!box) return;
  const R = window.RV || (window.T && T.rv) || {}, pid = box.dataset.pid, L = box.dataset.lang;
  const list = document.getElementById("rvlist"), sum = document.getElementById("rvsum"), form = document.getElementById("rvform"), msg = document.getElementById("rvmsg");
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const st = n => '<span class="rv-st" aria-hidden="true">' + "★★★★★".slice(0, n) + '<i>' + "★★★★★".slice(n) + "</i></span>";
  const fmt = d => { try { return new Date(d + "T12:00:00").toLocaleDateString(L, { year: "numeric", month: "long", day: "numeric" }); } catch (e) { return d; } };
  const started = Date.now();
  function schema(rs, avg) {
    const s = [...document.querySelectorAll('script[type="application/ld+json"]')].find(x => { try { return JSON.parse(x.textContent)["@type"] === "Service"; } catch (e) { return false; } });
    if (!s) return;
    const o = JSON.parse(s.textContent);
    const p = { "@context": "https://schema.org", "@type": "Product", name: o.name, description: o.description, image: o.image, category: o.category, url: o.url,
      sku: o.identifier, mpn: o.identifier, brand: o.brand, manufacturer: o.provider, countryOfOrigin: "TR", additionalProperty: o.additionalProperty,
      aggregateRating: { "@type": "AggregateRating", ratingValue: avg.toFixed(1), reviewCount: rs.length, bestRating: 5, worstRating: 1 },
      review: rs.slice(0, 10).map(r => ({ "@type": "Review", author: { "@type": "Person", name: r.name }, datePublished: r.date, reviewBody: r.text, inLanguage: r.lang,
        reviewRating: { "@type": "Rating", ratingValue: r.rating, bestRating: 5, worstRating: 1 } })) };
    s.textContent = JSON.stringify(p);
  }
  fetch("/api/review?pid=" + encodeURIComponent(pid)).then(r => r.ok ? r.json() : { reviews: [] }).then(d => {
    const rs = d.reviews || []; if (!rs.length) return;
    const avg = rs.reduce((a, r) => a + r.rating, 0) / rs.length;
    sum.hidden = false;
    sum.innerHTML = `<b>${avg.toFixed(1)}</b>${st(Math.round(avg))}<span>${esc((R.avg || "{a}").replace("{a}", avg.toFixed(1)))} · ${esc((R.count || "{n}").replace("{n}", rs.length))}</span>`;
    list.innerHTML = rs.map(r => `<article class="rv-item"><div class="rv-h">${st(r.rating)}<b dir="auto">${esc(r.name)}</b>${r.org ? `<span dir="auto">${esc(r.org)}</span>` : ""}</div>
      <p lang="${esc(r.lang)}" dir="auto">${esc(r.text)}</p><small>${esc(R.verified || "")} · <time datetime="${esc(r.date)}">${esc(fmt(r.date))}</time></small></article>`).join("");
    schema(rs, avg);
  }).catch(() => {});
  form.addEventListener("submit", ev => {
    ev.preventDefault();
    const f = new FormData(form), b = form.querySelector("button");
    if (!form.checkValidity()) { form.reportValidity(); return; }
    b.disabled = true; msg.className = "rv-msg"; msg.textContent = R.sending || "…";
    fetch("/api/review", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({
      pid, pname: box.dataset.pname, lang: L, rating: f.get("rating"), name: f.get("name"), org: f.get("org"), text: f.get("text"), hp: f.get("hp"), t: started }) })
      .then(r => r.json().then(j => [r.status, j])).then(([s, j]) => {
        if (j.ok) { form.reset(); msg.className = "rv-msg ok"; msg.textContent = R.thanks; }
        else { msg.className = "rv-msg bad"; msg.textContent = s === 429 ? R.limit : R.err; b.disabled = false; }
      }).catch(() => { msg.className = "rv-msg bad"; msg.textContent = R.err; b.disabled = false; });
  });
})();
