/* Reyonfix ürün araması: dizin ilk açılışta yüklenir, arama tarayıcıda yapılır. */
(function () {
  var box = document.getElementById('srch');
  if (!box) return;
  var q = document.getElementById('srch-q');
  var list = document.getElementById('srch-res');
  var hint = box.querySelector('.srch-hint');
  var root = box.getAttribute('data-root') || '';
  var data = null, loading = null, sel = -1, items = [], lastFocus = null;

  // Harf/aksan farklarını yok say: İ/ı/ş/ğ/ü/ö/ç/é/ß…
  function norm(s) {
    return (s || '').toLocaleLowerCase('tr').replace(/ı/g, 'i').replace(/ß/g, 'ss')
      .normalize('NFD').replace(/[̀-ًͯ-ٟ]/g, '');
  }
  function compact(s) { return s.replace(/[\s\-_.\/]+/g, ''); }

  function load() {
    if (data) return Promise.resolve(data);
    if (!loading) {
      loading = fetch(box.getAttribute('data-idx')).then(function (r) { return r.json(); }).then(function (rows) {
        data = rows.map(function (r) {
          var n = norm(r[0]), c = norm(r[1]), k = norm(r[2]), d = norm(r[5]);
          return { name: r[0], code: r[1], cat: r[2], url: root + r[3].replace(/^\//, ''), img: root + r[4].replace(/^\//, ''),
                   n: n, c: compact(c), k: k, d: d, all: n + ' ' + c + ' ' + compact(c) + ' ' + k + ' ' + d };
        });
        return data;
      }).catch(function () { loading = null; return []; });
    }
    return loading;
  }

  function score(it, terms, full) {
    var s = 0;
    for (var i = 0; i < terms.length; i++) {
      var t = terms[i], tc = compact(t);
      if (it.all.indexOf(t) < 0 && (!tc || it.c.indexOf(tc) < 0)) return -1;
      if (tc && it.c && it.c === tc) s += 120;
      else if (tc && it.c && it.c.indexOf(tc) === 0) s += 60;
      if (it.n.indexOf(t) === 0) s += 40;
      else if ((' ' + it.n).indexOf(' ' + t) >= 0) s += 30;
      else if (it.n.indexOf(t) >= 0) s += 20;
      if (it.k.indexOf(t) >= 0) s += 8;
      if (it.d.indexOf(t) >= 0) s += 2;
    }
    if (it.n.indexOf(full) >= 0) s += 25;
    return s;
  }

  function esc(s) { return String(s).replace(/[&<>"]/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[m]; }); }

  function render() {
    var raw = q.value.trim(), full = norm(raw);
    var terms = full.split(/\s+/).filter(Boolean);
    sel = -1;
    if (!terms.length) { list.innerHTML = ''; items = []; hint.hidden = false; return; }
    hint.hidden = true;
    load().then(function (rows) {
      if (q.value.trim() !== raw) return;
      var res = [];
      rows.forEach(function (it) { var s = score(it, terms, full); if (s >= 0) res.push([s, it]); });
      res.sort(function (a, b) { return b[0] - a[0] || a[1].name.localeCompare(b[1].name); });
      res = res.slice(0, 24);
      if (!res.length) { list.innerHTML = '<li class="srch-none">' + esc(box.getAttribute('data-none')) + '</li>'; items = []; return; }
      list.innerHTML = '<li class="srch-cnt" aria-hidden="true">' + res.length + (res.length === 24 ? '+' : '') + ' ' + esc(box.getAttribute('data-n')) + '</li>' +
        res.map(function (r, i) {
          var it = r[1];
          return '<li role="option" id="srch-o' + i + '"><a href="' + esc(it.url) + '"><img src="' + esc(it.img) + '" alt="" loading="lazy" width="56" height="56">' +
            '<span class="t"><b>' + esc(it.name) + '</b><small>' + esc(it.cat) + (it.code ? ' · ' + esc(it.code) : '') + '</small></span><span class="go" aria-hidden="true">›</span></a></li>';
        }).join('');
      items = list.querySelectorAll('a');
    });
  }

  function mark(i) {
    if (!items.length) return;
    sel = (i + items.length) % items.length;
    items.forEach(function (a, k) { a.classList.toggle('on', k === sel); });
    items[sel].scrollIntoView({ block: 'nearest' });
    q.setAttribute('aria-activedescendant', 'srch-o' + sel);
  }

  var pop = box.querySelector('.srch-pop'), x = box.querySelector('.srch-x');
  function show() { pop.hidden = false; q.setAttribute('aria-expanded', 'true'); load(); }
  function hide() { pop.hidden = true; q.setAttribute('aria-expanded', 'false'); sel = -1; }
  function sync() { var v = q.value.length > 0; x.hidden = !v; box.classList.toggle('has', v); }

  q.addEventListener('focus', show);
  q.addEventListener('input', function () {
    sync(); show(); clearTimeout(timer); timer = setTimeout(render, 60);
  });
  x.addEventListener('click', function (e) { e.preventDefault(); q.value = ''; sync(); render(); q.focus(); });
  document.addEventListener('mousedown', function (e) { if (!box.contains(e.target)) hide(); });
  document.addEventListener('focusin', function (e) { if (!box.contains(e.target)) hide(); });

  document.addEventListener('keydown', function (e) {
    var k = e.key;
    if ((k === 'k' || k === 'K') && (e.ctrlKey || e.metaKey)) { e.preventDefault(); q.focus(); q.select(); return; }
    if (k === '/' && document.activeElement !== q && !/input|textarea|select/i.test(e.target.tagName || '') && !e.target.isContentEditable) { e.preventDefault(); q.focus(); return; }
    if (document.activeElement !== q && !box.contains(document.activeElement)) return;
    if (k === 'Escape') { e.preventDefault(); if (!pop.hidden) hide(); else q.blur(); }
    else if (k === 'ArrowDown') { e.preventDefault(); show(); mark(sel + 1); }
    else if (k === 'ArrowUp') { e.preventDefault(); mark(sel - 1); }
    else if (k === 'Enter' && e.target === q) {
      var a = items[sel >= 0 ? sel : 0];
      if (a) { e.preventDefault(); location.href = a.href; }
    }
  });
  var timer;
  if (q.value) { sync(); }
})();
