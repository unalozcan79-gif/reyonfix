# Reyonfix statik site üreticisi
# kullanım: python3 build.py [--preview]
import os, sys, json, shutil, posixpath, html
from urllib.parse import quote
from jinja2 import Environment, DictLoader, select_autoescape
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from content import build_products, build_categories, LANGS, settings, ROOT
import imgproc
from wall_i18n import S as ST, WALL_CARDS, PASTEL, X as XT, NEW_IDS, SHELVES, ICONS as ICOSVG
from i18n import T, LANG_NAMES, LOCALE, CATALOG_URL, CONTACT
from yorum import section as review_section

PREVIEW = '--preview' in sys.argv
BASE = 'https://reyonfix.com'
DIST = (sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else ROOT + '/_preview') if PREVIEW else ROOT + '/dist'
CACHE = imgproc.CACHE
NOINDEX = PREVIEW or not settings().get('launched', False)

SEG = {
    'products': dict(tr='urunler', en='products', de='produkte', fr='produits', ar='products'),
    'about': dict(tr='hakkimizda', en='about', de='ueber-uns', fr='a-propos', ar='about'),
    'contact': dict(tr='iletisim', en='contact', de='kontakt', fr='contact', ar='contact'),
    'catalog': dict(tr='katalog', en='catalogue', de='katalog', fr='catalogue', ar='catalogue'),
}

cats = build_categories()
prods = build_products()
IMGMAP = imgproc.process([x for p in prods for x in p['srcs']] + [c['image'] for c in cats if c['image']] + [c['icon'] for c in cats if c['icon']])
CAT = {c['key']: c for c in cats}

# ---------- görseller ----------
SHORT = {}
USED = set()
BIG = {}
def bigimg(im):
    if PREVIEW:
        return BIG.setdefault(im['big'], f'h{len(BIG)}.webp')
    return im['l']
def images(p):
    out = []
    for s in p['srcs']:
        m = IMGMAP.get(s)
        if m:
            sm = m['files']['700']; lg = m['files']['1400']; th = m['files'].get('360', sm)
            USED.update((sm, lg, th))
            if PREVIEW:
                short = SHORT.setdefault(sm, f'{len(SHORT)}.webp')
                sm = lg = short
            out.append(dict(s=sm, l=lg, t=(sm if PREVIEW else th), r=m['ratio'], big=m['files']['1400'], src=s))
    return out
for p in prods:
    p['imgs'] = images(p)
prods = [p for p in prods if p['imgs'] and p['key'] in CAT]
BYID = {p['id']: p for p in prods}
cats = [c for c in cats if any(p['key'] == c['key'] for p in prods)]
for c in cats:
    c['cover'] = next(p['id'] for p in prods if p['key'] == c['key'])
def pick(*ids):
    for i in ids:
        if i in BYID:
            return BYID[i]
    return prods[0]
# ana sayfa rafları: üründeki "vitrin" etiketlerinden (yönetim panelinden seçilir)
TAGGED = {k: [p['id'] for p in prods if k in p['tags']] for k in ['duvar', 'yeni', 'manav', 'firin', 'zeytin', 'market']}

def in_lang(L):
    return [p for p in prods if L in p['names']]

# ---------- yollar ----------
CATIDX = {c['key']: n for n, c in enumerate(cats)}
if PREVIEW:
    def path_home(L): return f'/{L}/index.html'
    def path_products(L): return f'/{L}/all.html'
    def path_cat(L, c): return f"/{L}/k{CATIDX[c['key']]}.html"
    def path_prod(L, p): return f"/{L}/u{p['id']}.html"
    def path_page(L, k): return f'/{L}/{k}.html'
else:
    def path_home(L): return f'/{L}/'
    def path_products(L): return f"/{L}/{SEG['products'][L]}/"
    def path_cat(L, c): return f"/{L}/{c['slugs'][L]}/"
    def path_prod(L, p): return f"/{L}/{CAT[p['key']]['slugs'][L]}/{p['slugs'][L]}/"
    def path_page(L, k): return f"/{L}/{SEG[k][L]}/"

def rel(target, current):
    """site içi mutlak yolu, mevcut sayfaya göre göreli yola çevirir"""
    cur_dir = current if current.endswith('/') else posixpath.dirname(current) + '/'
    if target.endswith('/'):
        r = posixpath.relpath(target, cur_dir)
        r = '' if r == '.' else r + '/'
        return (r + 'index.html') if PREVIEW else (r or './')
    return posixpath.relpath(target, cur_dir)

def absu(path): return BASE + path

# ---------- şablonlar ----------
LOGO = '<svg viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="#ee6510"/><path d="M8.5 10.5h15M8.5 16h15M8.5 21.5h15" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><path d="M8.5 7.5v17M23.5 7.5v17" stroke="#fff" stroke-width="2.2" stroke-linecap="round" opacity=".55"/></svg>'
CHAT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.2a9.8 9.8 0 0 0-8.5 14.7L2.2 21.8l5-1.3A9.8 9.8 0 1 0 12 2.2zm0 1.8a8 8 0 1 1-4.2 14.8l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 0 1 12 4zm-3.1 4.2c-.2 0-.5 0-.7.3-.3.3-.9.9-.9 2.2s1 2.6 1.1 2.7c.1.2 1.9 3 4.7 4.1 2.3.9 2.8.7 3.3.7s1.6-.7 1.8-1.3.2-1.2.2-1.3-.2-.2-.5-.3l-1.7-.8c-.3-.1-.4-.2-.6.1l-.8 1c-.2.2-.3.2-.6.1a6.6 6.6 0 0 1-3.3-2.9c-.2-.4.3-.4.7-1.2.1-.2 0-.3 0-.5l-.8-1.9c-.2-.5-.4-.4-.6-.4z"/></svg>'

SEARCH_T = {
 'tr': dict(open='Ürün ara', ph='Ürün adı, model kodu veya kategori…', none='Sonuç bulunamadı. Farklı bir kelime deneyin ya da bize yazın.', hint='Örnek: zeytin, ayna, OG-2', close='Kapat', n='sonuç'),
 'en': dict(open='Search products', ph='Product name, model code or category…', none='No results. Try another word or message us.', hint='e.g. olive, mirror, OG-2', close='Close', n='results'),
 'de': dict(open='Produkte suchen', ph='Produktname, Modellnummer oder Kategorie…', none='Keine Treffer. Versuchen Sie ein anderes Wort oder schreiben Sie uns.', hint='z. B. Oliven, Spiegel, OG-2', close='Schließen', n='Treffer'),
 'fr': dict(open='Rechercher un produit', ph='Nom du produit, référence ou catégorie…', none='Aucun résultat. Essayez un autre mot ou écrivez-nous.', hint='ex. olive, miroir, OG-2', close='Fermer', n='résultats'),
 'ar': dict(open='ابحث عن منتج', ph='اسم المنتج أو رقم الطراز أو الفئة…', none='لا توجد نتائج. جرّب كلمة أخرى أو راسلنا.', hint='مثال: زيتون، مرآة، OG-2', close='إغلاق', n='نتيجة'),
}
SEARCH_ICO = '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg>'

SOCIAL_SVG = {
 'Instagram': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17.3" cy="6.7" r="1.2" fill="currentColor"/></svg>',
 'Facebook': '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M13.5 21v-7.5h2.5l.4-3h-2.9V8.6c0-.9.3-1.5 1.5-1.5h1.5V4.4c-.3 0-1.2-.1-2.2-.1-2.2 0-3.7 1.3-3.7 3.8v2.4H8v3h2.6V21z"/></svg>',
 'X': '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M17.8 3h3l-6.6 7.6L22 21h-6.1l-4.8-6.3L5.6 21h-3l7.1-8.1L2.3 3h6.2l4.3 5.7zm-1 16.2h1.7L7.3 4.7H5.5z"/></svg>',
 'YouTube': '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4a2.5 2.5 0 0 0-1.8 1.8C2 8.8 2 12 2 12s0 3.2.4 4.8a2.5 2.5 0 0 0 1.8 1.8c1.6.4 7.8.4 7.8.4s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8c.4-1.6.4-4.8.4-4.8s0-3.2-.4-4.8zM10 15.1V8.9l5.2 3.1z"/></svg>',
 'LinkedIn': '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zm6.5 0h3.8v1.6h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.1c0-1.2 0-2.8-1.7-2.8s-2 1.3-2 2.7V21h-4z"/></svg>',
 'WhatsApp': CHAT,
}
SOCIAL_SVG = {k: v.replace('<svg viewBox="0 0 24 24"', '<svg width="18" height="18" viewBox="0 0 24 24"', 1) for k, v in SOCIAL_SVG.items()}
TPL = {}
TPL['base'] = r'''<!doctype html>
<html lang="{{ L }}" dir="{{ 'rtl' if L=='ar' else 'ltr' }}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{{ title }}</title>
<meta name="description" content="{{ desc }}">
{% if noindex %}<meta name="robots" content="noindex,nofollow">{% else %}<meta name="robots" content="index,follow,max-image-preview:large">{% endif %}
<link rel="canonical" href="{{ canonical }}">
{% for hl, href in alts %}<link rel="alternate" hreflang="{{ hl }}" href="{{ href }}">
{% endfor %}<meta property="og:type" content="{{ ogtype }}">
<meta property="og:site_name" content="Reyonfix">
<meta property="og:title" content="{{ title }}">
<meta property="og:description" content="{{ desc }}">
<meta property="og:url" content="{{ canonical }}">
<meta property="og:locale" content="{{ locale }}">
{% if ogimg %}<meta property="og:image" content="{{ ogimg }}">{% endif %}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="{{ r('/favicon.svg') }}" type="image/svg+xml">
<link rel="stylesheet" href="{{ r('/static/style.css') }}?v={{ css_v }}">
{% if L=='ar' %}<link rel="preload" href="{{ r('/static/fonts/cairo-ar.woff2') }}" as="font" type="font/woff2" crossorigin>{% endif %}
{% for j in jsonld %}<script type="application/ld+json">{{ j|safe }}</script>
{% endfor %}</head>
<body>
<a class="skip" href="#main">{{ t.nav_products }}</a>
<header class="nav" id="nav"><div class="wrap">
<a class="logo" href="{{ r(home) }}" aria-label="Reyonfix">{{ logo|safe }}<span>Reyon<b>fix</b></span></a>
<button class="burger" aria-label="Menu" aria-expanded="false" onclick="var n=document.getElementById('nav');n.classList.toggle('open');this.setAttribute('aria-expanded',n.classList.contains('open'))"><span></span><span></span><span></span></button>
<nav aria-label="Main"><ul>
<li><a href="{{ r(p_products) }}"{% if active=='products' %} aria-current="page"{% endif %}>{{ t.nav_products }}</a></li>
<li><a href="{{ r(p_about) }}"{% if active=='about' %} aria-current="page"{% endif %}>{{ t.nav_about }}</a></li>
<li><a href="{{ r(p_catalog) }}"{% if active=='catalog' %} aria-current="page"{% endif %}>{{ t.nav_catalog }}</a></li>
<li><a href="{{ r(p_contact) }}"{% if active=='contact' %} aria-current="page"{% endif %}>{{ t.nav_contact }}</a></li>
</ul></nav>
<div class="srch" id="srch" role="search" data-idx="{{ r('/' ~ L ~ '/search.json') }}?v={{ idx_v }}" data-root="{{ r('/') }}" data-none="{{ st.none }}" data-n="{{ st.n }}">
<label class="srch-f">{{ srch_ico|safe }}<span class="sr">{{ st.open }}</span><input id="srch-q" type="search" placeholder="{{ st.open }}…" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="srch-res" aria-autocomplete="list" enterkeyhint="search"><kbd>Ctrl K</kbd><button type="button" class="srch-x" aria-label="{{ st.close }}" hidden>✕</button></label>
<div class="srch-pop" hidden><div class="srch-hint">{{ st.hint }}</div><ul class="srch-res" id="srch-res" role="listbox"></ul></div></div>
<details class="langsel"><summary aria-label="{{ t.lang_l }}"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="9.2"/><path d="M2.8 12h18.4M12 2.8c2.6 2.6 3.9 5.6 3.9 9.2s-1.3 6.6-3.9 9.2M12 2.8C9.4 5.4 8.1 8.4 8.1 12s1.3 6.6 3.9 9.2"/></svg>{{ L|upper }}</summary>
<div class="menu">{% for l2, href in langlinks %}<a href="{{ href }}" hreflang="{{ l2 }}" lang="{{ l2 }}"{% if l2==L %} aria-current="true"{% endif %}>{{ langnames[l2] }}</a>{% endfor %}</div></details>
<a class="btn btn-p btn-sm" href="{{ wa_general }}" target="_blank" rel="noopener">{{ t.nav_quote }}</a>
</div></header>
<main id="main">
{% block main %}{% endblock %}
</main>
<script src="{{ r('/static/search.js') }}?v={{ js_v }}" defer></script>
<footer><div class="wrap">
<div class="fgrid">
<div><a class="logo" href="{{ r(home) }}">{{ logo|safe }}<span>Reyon<b>fix</b></span></a><p style="margin-top:12px;max-width:320px">{{ t.footer_about }}</p></div>
<div><h2>{{ t.nav_products }}</h2><ul>{% for c in fcats %}<li><a href="{{ r(c.path) }}">{{ c.name }}</a></li>{% endfor %}</ul></div>
<div><h2>Reyonfix</h2><ul><li><a href="{{ r(p_products) }}">{{ t.all_products }}</a></li><li><a href="{{ r(p_about) }}">{{ t.nav_about }}</a></li><li><a href="{{ r(p_catalog) }}">{{ t.nav_catalog }}</a></li><li><a href="{{ r(p_contact) }}">{{ t.nav_contact }}</a></li></ul></div>
<div><h2>{{ t.nav_contact }}</h2><ul><li>{{ c.street }}, {{ c.postal }} {{ c.city }} / {{ c.region }}</li><li><a class="ltr" href="tel:{{ c.phone1|replace(' ','') }}">{{ c.phone1 }}</a></li><li><a class="ltr" href="{{ wa_general }}" target="_blank" rel="noopener">{{ c.mobile }}</a></li><li><a href="mailto:{{ c.email }}">{{ c.email }}</a></li></ul>
<div class="social">{% for n, u in c.social %}<a class="s-{{ n|lower }}" href="{{ u }}" target="_blank" rel="noopener me" aria-label="{{ n }}" title="{{ n }}">{{ social_svg[n]|safe }}</a>{% endfor %}<a class="s-whatsapp" href="{{ wa_general }}" target="_blank" rel="noopener" aria-label="WhatsApp" title="WhatsApp">{{ social_svg['WhatsApp']|safe }}</a></div></div>
</div>
<div class="bottom"><span>© 2026 Reyonfix · Huzur Pano. {{ t.rights }}</span><span class="langs">{% for l2, href in langlinks %}<a href="{{ href }}" hreflang="{{ l2 }}" lang="{{ l2 }}">{{ langnames[l2] }}</a>{% endfor %}</span></div>
</div></footer>
<a class="wa" href="{{ wa_link or wa_general }}" target="_blank" rel="noopener" aria-label="WhatsApp">{{ chat|safe }}</a>
<script>document.addEventListener('click',function(e){var b=e.target.closest('.st-pad');if(!b)return;var r=b.parentNode.previousElementSibling,rtl=getComputedStyle(r).direction=='rtl';r.scrollBy({left:(+b.dataset.d)*(rtl?-1:1)*r.clientWidth*.8,behavior:'smooth'})});</script><script>document.querySelectorAll('.st-icons').forEach(function(n){var c=n.querySelector('a.cur');if(c){n.scrollLeft+=c.getBoundingClientRect().left-n.getBoundingClientRect().left-(n.clientWidth-c.offsetWidth)/2}});document.addEventListener('click',function(e){var a=e.target.closest('.st-icons a');if(a&&!a.classList.contains('cur'))a.classList.add('go')});window.addEventListener('pageshow',function(){document.querySelectorAll('.st-icons a.go').forEach(function(a){a.classList.remove('go')})});</script><script>(function(){if(location.hash!=='#modeller')return;var h=document.getElementById('modeller');if(!h)return;if('scrollRestoration' in history)history.scrollRestoration='manual';var d=document.documentElement;function go(){var o=(document.querySelector('.nav')||{}).offsetHeight||60;d.style.scrollBehavior='auto';window.scrollTo(0,h.getBoundingClientRect().top+window.pageYOffset-o-12);d.style.scrollBehavior=''}go();requestAnimationFrame(go);window.addEventListener('load',go);setTimeout(go,250);setTimeout(go,700);var u=function(){window.removeEventListener('touchstart',u);window.removeEventListener('wheel',u);go=function(){}};window.addEventListener('touchstart',u,{passive:true});window.addEventListener('wheel',u,{passive:true})})();</script>
{% block js %}{% endblock %}
</body></html>'''

TPL['home'] = r'''{% extends "base" %}{% block main %}
{% macro pcard(p, eb, cls='') %}<a class="st-card {{ cls }}" href="{{ r(p.path) }}"{% if p.bg %} style="background:{{ p.bg }}"{% endif %}>
<div class="tx">{% if eb %}<span class="eb">{{ eb }}</span>{% endif %}<h3>{{ p.name }}</h3>{% if p.code %}<p class="pr">{{ x.code }}: {{ p.code }}</p>{% else %}<p>{{ p.desc }}</p>{% endif %}</div>
<img src="{{ r(p.img) }}" alt="{{ p.name }}" loading="lazy"></a>{% endmacro %}
<div class="st">
<div class="wrap st-top">
<h1 class="st-h1">Reyonfix<span class="vh"> · {{ t.tagline }}</span></h1>
<div class="st-intro"><p>{{ s.intro }}</p>
<a href="{{ wa_general }}" target="_blank" rel="noopener">{{ s.l1 }} ↗</a><a href="{{ catalog_url }}" target="_blank" rel="noopener">{{ s.l2 }} ↗</a></div>
</div>

<nav class="st-icons" aria-label="{{ t.nav_products }}">{% for c in icons %}<a href="{{ r(c.path) }}"><span class="ic{% if not c.cut %} ph{% endif %}"><img src="{{ r(c.img) }}" alt="" loading="{{ 'eager' if loop.index < 8 else 'lazy' }}"></span><b>{{ c.name }}</b></a>{% endfor %}</nav><div class="wrap st-pads st-pads-ic"><button type="button" class="st-pad" data-d="-1" aria-label="‹">‹</button><button type="button" class="st-pad" data-d="1" aria-label="›">›</button></div>

<section class="st-sec st-acc">
<h2 class="wrap st-h2"><em>{{ s.cat_a }}</em> {{ s.cat_b }}</h2>
<div class="st-row">{% for c in ccards %}
<a class="st-card" href="{{ r(c.path) }}" style="background:{{ c.bg }}">
<div class="tx"><span class="eb">{{ c.count }} {{ t.models }}</span><h3>{{ c.name }}</h3><p>{{ c.desc }}</p></div>
<img src="{{ r(c.img) }}" alt="{{ c.name }}" loading="{{ 'eager' if loop.index < 4 else 'lazy' }}">
</a>{% endfor %}
<a class="st-card st-more" href="{{ r(p_products) }}"><div class="tx"><h3>{{ s.all }}</h3><p>{{ t.all_products_p }}</p></div><span class="arr">→</span></a>
</div><div class="wrap st-pads"><button type="button" class="st-pad" data-d="-1" aria-label="‹">‹</button><button type="button" class="st-pad" data-d="1" aria-label="›">›</button></div></section>

<section class="st-sec st-acc">
<h2 class="wrap st-h2"><em>{{ s.wall_a }}</em> {{ s.wall_b }}</h2>
<div class="st-row">{% for p in wcards %}{{ pcard(p, s.eyebrow) }}{% endfor %}</div><div class="wrap st-pads"><button type="button" class="st-pad" data-d="-1" aria-label="‹">‹</button><button type="button" class="st-pad" data-d="1" aria-label="›">›</button></div>
</section>

{% if newc|length > 2 %}<section class="st-sec">
<h2 class="wrap st-h2"><em>{{ x.new_a }}</em> {{ x.new_b }}</h2>
<div class="st-row">{% for p in newc %}{{ pcard(p, x.new_eb) }}{% endfor %}</div><div class="wrap st-pads"><button type="button" class="st-pad" data-d="-1" aria-label="‹">‹</button><button type="button" class="st-pad" data-d="1" aria-label="›">›</button></div>
</section>{% endif %}

{% for sh in shelves %}<section class="st-sec">
<h2 class="wrap st-h2"><em>{{ sh.a }}</em> {{ sh.b }}</h2>
<div class="st-row">{% for p in sh.plist %}{{ pcard(p, '', 'st-sm') }}{% endfor %}</div><div class="wrap st-pads"><button type="button" class="st-pad" data-d="-1" aria-label="‹">‹</button><button type="button" class="st-pad" data-d="1" aria-label="›">›</button></div>
</section>{% endfor %}

<div class="wrap"><a class="st-banner" href="{{ catalog_url }}" target="_blank" rel="noopener">
<div><span class="eb">PDF</span><h3>{{ t.catalog_h }}</h3><p>{{ t.catalog_p }}</p><span class="lnk">{{ t.btn_catalog }} ↗</span></div>
<div class="st-bk" aria-hidden="true"><img class="p3" src="{{ r('/katalog/' ~ L ~ '-3.webp') }}" alt="" loading="lazy" width="819" height="579"><img class="p2" src="{{ r('/katalog/' ~ L ~ '-2.webp') }}" alt="" loading="lazy" width="819" height="579"><img class="p1" src="{{ r('/katalog/' ~ L ~ '-1.webp') }}" alt="" loading="lazy" width="819" height="579"><img class="p0" src="{{ r('/katalog/' ~ L ~ '-0.webp') }}" alt="{{ t.catalog_h }}" loading="lazy" width="819" height="579"></div></a></div>

<section class="st-sec">
<h2 class="wrap st-h2"><em>{{ x.only_a }}</em> {{ x.only_b }}</h2>
<div class="st-row">{% for eb, h, l in x.only %}<div class="st-card st-tc"><div class="tx"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true">{{ icons_svg[loop.index0]|safe }}</svg><span class="eb">{{ eb }}</span><h3>{{ h }}</h3>{% if l %}<a href="{{ wa_general }}" target="_blank" rel="noopener">{{ l }} ›</a>{% endif %}</div></div>{% endfor %}</div><div class="wrap st-pads"><button type="button" class="st-pad" data-d="-1" aria-label="‹">‹</button><button type="button" class="st-pad" data-d="1" aria-label="›">›</button></div>
</section>

<section class="st-sec">
<h2 class="wrap st-h2"><em>{{ s.proc_a }}</em> {{ s.proc_b }}</h2>
<div class="st-row">{% for h, p in t.process %}<div class="st-card st-tc"><div class="tx"><span class="num">{{ loop.index }}</span><h3>{{ h }}</h3><p>{{ p }}</p></div></div>{% endfor %}</div><div class="wrap st-pads"><button type="button" class="st-pad" data-d="-1" aria-label="‹">‹</button><button type="button" class="st-pad" data-d="1" aria-label="›">›</button></div>
</section>

<section class="st-sec"><div class="wrap">
<h2 class="st-h2"><em>{{ x.ql }}</em></h2>
<div class="st-ql"><a href="{{ r(p_products) }}">{{ t.all_products }}</a><a href="{{ r(p_catalog) }}">{{ t.nav_catalog }}</a><a href="{{ r(p_about) }}">{{ t.nav_about }}</a><a href="{{ r(p_contact) }}">{{ t.nav_contact }}</a><a href="{{ wa_general }}" target="_blank" rel="noopener">{{ t.nav_quote }} ↗</a></div>
</div></section>

<section class="st-sec st-faq"><div class="wrap">
<h2 class="st-h2"><em>{{ t.faq_h }}</em></h2>
<div class="faq">{% for q, a in t.faq %}<details{% if loop.first %} open{% endif %}><summary>{{ q }}</summary><p>{{ a }}</p></details>{% endfor %}</div>
</div></section>
</div>
{{ ctabox() }}
{% endblock %}'''

TPL['macros'] = r'''{% macro card(p) %}<a class="card" href="{{ r(p.path) }}"><div class="im"><img src="{{ r(p.img.s) }}" alt="{{ p.name }}" loading="lazy" width="700" height="525"></div><div class="tx"><h3>{{ p.name }}</h3><p>{{ p.desc }}</p>{% if p.code %}<span class="code">{{ p.code }}</span>{% endif %}</div></a>{% endmacro %}
{% macro stcard(p, eb='', cls='st-sm') %}<a class="st-card {{ cls }}" href="{{ r(p.path) }}">
<div class="tx">{% if eb %}<span class="eb">{{ eb }}</span>{% endif %}<h3>{{ p.name }}</h3>{% if p.code %}<p class="pr">{{ x.code }}: <span class="ltr">{{ p.code }}</span></p>{% else %}<p>{{ p.desc }}</p>{% endif %}</div>
<img src="{{ r(p.img.s) }}" alt="{{ p.name }}" loading="lazy"></a>{% endmacro %}
{% macro pads() %}<div class="wrap st-pads"><button type="button" class="st-pad" data-d="-1" aria-label="‹">‹</button><button type="button" class="st-pad" data-d="1" aria-label="›">›</button></div>{% endmacro %}
{% macro catnavbar(curkey='') %}<nav class="st-icons" aria-label="{{ t.nav_products }}">{% for c in catnav %}<a href="{{ r(c.path) }}#modeller"{% if c.key == curkey %} aria-current="page" class="cur"{% endif %}><span class="ic{% if not c.cut %} ph{% endif %}"><img src="{{ r(c.img) }}" alt="" loading="lazy"></span><b>{{ c.name }}</b></a>{% endfor %}</nav>{{ pads() }}{% endmacro %}
{% macro onlyrow() %}<section class="st-sec">
<h2 class="wrap st-h2"><em>{{ x.only_a }}</em> {{ x.only_b }}</h2>
<div class="st-row">{% for eb, h, l in x.only %}<div class="st-card st-tc"><div class="tx"><svg class="ico" viewBox="0 0 24 24" aria-hidden="true">{{ icons_svg[loop.index0]|safe }}</svg><span class="eb">{{ eb }}</span><h3>{{ h }}</h3>{% if l %}<a href="{{ wa_general }}" target="_blank" rel="noopener">{{ l }} ›</a>{% endif %}</div></div>{% endfor %}</div>{{ pads() }}
</section>{% endmacro %}'''

TPL['products'] = r'''{% extends "base" %}{% block main %}
<div class="st">
<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{{ r(home) }}">{{ t.home }}</a></li><li aria-current="page">{{ t.all_products }}</li></ol></nav></div>
<div class="wrap st-top st-top-s">
<h1 class="st-h1 ink">{{ t.all_products }}</h1>
<div class="st-intro"><p>{{ t.all_products_p }}</p><a href="{{ wa_general }}" target="_blank" rel="noopener">{{ s.l1 }} ↗</a><a href="{{ catalog_url }}" target="_blank" rel="noopener">{{ s.l2 }} ↗</a></div>
</div>
{{ catnavbar() }}
{% for c in blocks %}<section class="st-sec">
<h2 class="wrap st-h2 st-hl"><em>{{ c.name }}.</em> <span>{{ c.plist|length }} {{ t.models }}</span> <a href="{{ r(c.path) }}">{{ t.see_all }} ›</a></h2>
<div class="st-row">{% for p in c.plist[:14] %}{{ stcard(p) }}{% endfor %}
<a class="st-card st-more st-sm" href="{{ r(c.path) }}"><div class="tx"><h3>{{ t.see_all }}</h3><p>{{ c.name }} · {{ c.plist|length }} {{ t.models }}</p></div><span class="arr">→</span></a></div>{{ pads() }}
</section>{% endfor %}
{{ onlyrow() }}
</div>
{{ ctabox() }}
{% endblock %}'''

TPL['category'] = r'''{% extends "base" %}{% block main %}
<div class="st">
<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{{ r(home) }}">{{ t.home }}</a></li><li><a href="{{ r(p_products) }}">{{ t.nav_products }}</a></li><li aria-current="page">{{ cat.name }}</li></ol></nav></div>
<div class="wrap st-top st-top-s">
<h1 class="st-h1 ink">{{ cat.name }}</h1>
<div class="st-intro"><p>{{ cat.desc }}</p><span class="cnt">{{ items|length }} {{ t.models }}</span><a href="{{ wa_general }}" target="_blank" rel="noopener">{{ s.l1 }} ↗</a><a href="{{ catalog_url }}" target="_blank" rel="noopener">{{ s.l2 }} ↗</a></div>
</div>
{{ catnavbar(cat.key) }}
<section class="st-sec"><div class="wrap">
<h2 class="st-h2" id="modeller"><em>{{ x.all_models }}</em> {{ cat.name }}</h2>
<div class="st-grid">{% for p in items %}{{ stcard(p) }}{% endfor %}</div>
</div></section>
{{ onlyrow() }}
</div>
{{ ctabox() }}
{% endblock %}'''

TPL['product'] = r'''{% extends "base" %}{% block main %}
<div class="st">
<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{{ r(home) }}">{{ t.home }}</a></li><li><a href="{{ r(p_products) }}">{{ t.nav_products }}</a></li><li><a href="{{ r(cat.path) }}">{{ cat.name }}</a></li><li aria-current="page">{{ p.name }}</li></ol></nav></div>
<article class="wrap pd">
<div class="pd-gal">
<div class="pd-main"><img id="gmain" src="{{ r(p.imgs[0].l) }}" alt="{{ p.name }}" width="1400" height="{{ (1400*p.imgs[0].r)|int }}" fetchpriority="high"></div>
{% if p.imgs|length > 1 %}<div class="thumbs" role="tablist">{% for im in p.imgs %}<button type="button" data-src="{{ r(im.l) }}" aria-current="{{ 'true' if loop.first else 'false' }}" aria-label="{{ p.name }} {{ loop.index }}"><img src="{{ r(im.s) }}" alt="" loading="lazy" width="84" height="64"></button>{% endfor %}</div>{% endif %}
</div>
<div class="pd-info">
<a class="pd-eb" href="{{ r(cat.path) }}">{{ cat.name }}</a>
<h1>{{ p.name }}</h1>
{% if p.code %}<p class="pd-code">{{ t.code }}: <span class="ltr">{{ p.code }}</span></p>{% endif %}
<p class="pd-sum">{{ p.desc }}</p>
<div class="pd-box"><b>{{ x.made }}</b><span>{{ x.made_p }}</span></div>
<div class="pd-btns"><a class="btn btn-p" href="{{ wa_link }}" target="_blank" rel="noopener">{{ t.quote_product }}</a><a class="btn btn-s" href="tel:{{ c.phone1|replace(' ','') }}">{{ t.call }}</a></div>
{% if p.features %}<h2 class="pd-h">{{ x.feat_h }}</h2>
<ul class="pd-hl">{% for h in p.features %}<li>{{ h }}</li>{% endfor %}</ul>{% else %}<h2 class="pd-h">{{ t.highlights_h }}</h2>
<ul class="pd-hl">{% for h in t.highlights %}<li>{{ h }}</li>{% endfor %}</ul>{% endif %}
<p class="note">{{ t.img_note }}</p>
</div>
</article>
{% if p.details %}<section class="wrap pd-more">
<div class="pd-about"><h2 class="st-h2"><em>{{ x.about_h }}</em></h2>{% for para in p.details %}<p>{{ para }}</p>{% endfor %}</div>
{% if p.uses %}<div class="pd-uses"><h3>{{ x.uses_h }}</h3><ul>{% for u in p.uses %}<li>{{ u }}</li>{% endfor %}</ul></div>{% endif %}
</section>{% endif %}
{{ reviews_html|safe }}
{% if related %}<section class="st-sec">
<h2 class="wrap st-h2 st-hl"><em>{{ t.related_h }}.</em> <a href="{{ r(cat.path) }}">{{ t.see_all }} ›</a></h2>
<div class="st-row">{% for q in related %}{{ stcard(q) }}{% endfor %}</div>{{ pads() }}
</section>{% endif %}
{{ onlyrow() }}
</div>
{{ ctabox() }}
{% endblock %}
{% block js %}<script src="{{ r('/static/reviews.js') }}?v={{ rv_v }}" defer></script><script>(function(){var m=document.getElementById('gmain'),b=document.querySelectorAll('.thumbs button');b.forEach(function(x){x.addEventListener('click',function(){m.src=x.dataset.src;b.forEach(function(y){y.setAttribute('aria-current','false')});x.setAttribute('aria-current','true')})})})();</script>{% endblock %}'''

TPL['about'] = r'''{% extends "base" %}{% block main %}
<div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{{ r(home) }}">{{ t.home }}</a></li><li aria-current="page">{{ t.about_h }}</li></ol></nav>
<div class="phead"><p class="eyebrow">Reyonfix · Huzur Pano</p><h1 class="h1">{{ t.about_lead }}</h1></div>
<div class="hero-img" style="margin-top:0"><img src="{{ r(img.l) }}" alt="{{ t.about_h }}" width="1400" height="{{ (1400*img.r)|int }}"></div>
<div class="prose" style="padding:clamp(40px,6vw,72px) 0">{% for para in t.about_p %}<p>{{ para }}</p>{% endfor %}</div>
</div>
<section class="dark"><div class="wrap"><div class="stats center" style="margin-top:0">{% for b, s in t.stats %}<div class="stat"><b>{{ b }}</b><span>{{ s }}</span></div>{% endfor %}</div></div></section>
<section><div class="wrap"><div class="sec-head center"><h2 class="h2">{{ t.process_h }}</h2></div>
<ol class="steps">{% for h, p in t.process %}<li><h3>{{ h }}</h3><p>{{ p }}</p></li>{% endfor %}</ol></div></section>
{{ ctabox() }}
{% endblock %}'''

TPL['contact'] = r'''{% extends "base" %}{% block main %}
<div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{{ r(home) }}">{{ t.home }}</a></li><li aria-current="page">{{ t.contact_h }}</li></ol></nav>
<div class="phead"><h1 class="h1">{{ t.contact_h }}</h1><p class="lead">{{ t.contact_lead }}</p></div>
<div class="cgrid">
<div class="cbox"><h2>{{ t.mobile_l }}</h2><a class="ltr" href="{{ wa_general }}" target="_blank" rel="noopener">{{ c.mobile }}</a><p style="margin-top:14px"><a class="btn btn-p" href="{{ wa_general }}" target="_blank" rel="noopener" style="display:inline-flex;font-size:15px">{{ t.btn_whatsapp }}</a></p></div>
<div class="cbox"><h2>{{ t.phone_l }}</h2><a class="ltr" href="tel:{{ c.phone1|replace(' ','') }}">{{ c.phone1 }}</a><a class="ltr" href="tel:{{ c.phone2|replace(' ','') }}">{{ c.phone2 }}</a></div>
<div class="cbox"><h2>{{ t.email_l }}</h2><a href="mailto:{{ c.email }}">{{ c.email }}</a></div>
<div class="cbox" style="grid-column:1/-1"><h2>{{ t.address_l }}</h2><p>{{ c.street }}<br>{{ c.postal }} {{ c.city }} / {{ c.region }}, Türkiye</p><p style="margin-top:12px"><a href="{{ c.maps }}" target="_blank" rel="noopener" style="font-size:16px;color:var(--acc)">{{ t.map_l }} ›</a></p></div>
</div>
<div style="height:100px"></div></div>
{% endblock %}'''

TPL['catalog'] = r'''{% extends "base" %}{% block main %}
<div class="st">
<div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{{ r(home) }}">{{ t.home }}</a></li><li aria-current="page">{{ t.nav_catalog }}</li></ol></nav></div>
<div class="wrap kat">
<a class="kat-cover" href="{{ r(catalog_url) }}" target="_blank" rel="noopener"><img src="{{ r('/katalog/' ~ L ~ '-0.webp') }}" alt="{{ t.catalog_page_h }}" width="1000" height="707"></a>
<div class="kat-tx"><p class="pd-eb">{{ t.nav_catalog }} · PDF · 43 {{ x.pages }}</p><h1>{{ t.catalog_page_h }}</h1><p class="pd-sum">{{ t.catalog_page_lead }}</p>
<div class="pd-btns"><a class="btn btn-p" href="{{ r(catalog_url) }}" target="_blank" rel="noopener" download>{{ t.btn_catalog }}</a><a class="btn btn-s" href="{{ r(catalog_url) }}" target="_blank" rel="noopener">{{ x.open_pdf }}</a></div>
<p class="note">{{ x.other_langs }}: {% for l2 in langs %}{% if l2 != L %}<a href="{{ r(catalogs[l2]) }}" target="_blank" rel="noopener" lang="{{ l2 }}">{{ langnames[l2] }}</a>{% if not loop.last %} · {% endif %}{% endif %}{% endfor %}</p></div>
</div>
<section class="st-sec"><h2 class="wrap st-h2"><em>{{ x.inside }}</em></h2>
<div class="wrap kat-pages">{% for n in [1,2,3] %}<a href="{{ r(catalog_url) }}" target="_blank" rel="noopener"><img src="{{ r('/katalog/' ~ L ~ '-' ~ n ~ '.webp') }}" alt="{{ t.catalog_page_h }} {{ n + 1 }}" loading="lazy" width="1000" height="707"></a>{% endfor %}</div>
</section>
</div>
{{ ctabox() }}
{% endblock %}'''

TPL['ctabox'] = r'''{% macro ctabox() %}<section style="padding-top:0"><div class="wrap"><div class="cta-box"><h2 class="h2">{{ t.cta_h }}</h2><p class="lead">{{ t.cta_p }}</p><div class="btns"><a class="btn btn-w" href="{{ wa_general }}" target="_blank" rel="noopener">{{ t.btn_whatsapp }}</a><a class="btn btn-s" href="tel:{{ c.phone1|replace(' ','') }}">{{ t.btn_call }}</a><a class="btn btn-s" href="mailto:{{ c.email }}">{{ t.btn_mail }}</a></div></div></div></section>{% endmacro %}'''

TPL['404'] = r'''{% extends "base" %}{% block main %}<section class="center"><div class="wrap"><h1 class="h1">404</h1><p class="lead" style="margin:16px auto 28px">{{ t.not_found }}</p><a class="btn btn-p" href="{{ r(home) }}">{{ t.back_home }}</a></div></section>{% endblock %}'''

# makroları her şablona ekle
for k in ['home', 'products', 'category', 'product', 'about', 'catalog']:
    TPL[k] = TPL[k].replace('{% extends "base" %}', '{% extends "base" %}{% from "macros" import card, stcard, pads, catnavbar, onlyrow with context %}{% from "ctabox" import ctabox with context %}', 1)
for k in ['contact', '404']:
    TPL[k] = TPL[k].replace('{% extends "base" %}', '{% extends "base" %}{% from "ctabox" import ctabox with context %}', 1)

env = Environment(loader=DictLoader(TPL), autoescape=select_autoescape(['html']), trim_blocks=True, lstrip_blocks=True)
import hashlib
CSS_V = hashlib.md5(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'style.css'), 'rb').read()).hexdigest()[:8]
env.globals['css_v'] = CSS_V
env.globals['rv_v'] = hashlib.md5(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'reviews.js'), 'rb').read()).hexdigest()[:8]
env.globals['js_v'] = hashlib.md5(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'search.js'), 'rb').read()).hexdigest()[:8]
env.globals['srch_ico'] = SEARCH_ICO
env.globals['idx_v'] = '0'

def wa(text):
    return f"https://wa.me/{CONTACT['wa']}?text={quote(text)}"

def ld(o):
    return json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

ORG = {"@type": ["Organization", "LocalBusiness"], "@id": BASE + "/#org", "name": "Reyonfix", "legalName": "Huzur Pano",
       "url": BASE + "/", "logo": BASE + "/favicon.svg", "foundingDate": "1994", "email": CONTACT['email'],
       "telephone": CONTACT['phone1'],
       "address": {"@type": "PostalAddress", "streetAddress": CONTACT['street'], "addressLocality": CONTACT['city'],
                   "addressRegion": CONTACT['region'], "postalCode": CONTACT['postal'], "addressCountry": "TR"},
       "contactPoint": [{"@type": "ContactPoint", "telephone": CONTACT['mobile'], "contactType": "sales",
                         "availableLanguage": ["tr", "en", "de", "fr", "ar"]}],
       "sameAs": ["https://manavreyonu.com.tr/"] + [u for _, u in CONTACT["social"]],
       "geo": {"@type": "GeoCoordinates", "latitude": CONTACT["geo"][0], "longitude": CONTACT["geo"][1]}, "hasMap": CONTACT["maps"]}

def caticon(c):
    if c['icon'] and c['icon'] in IMGMAP:
        im = images(dict(srcs=[c['icon']]))[0]
        return '/img/' + im['t'], True
    return favimg(c, True), False

def favimg(c, small=False):
    if c['image'] and c['image'] in IMGMAP:
        im = images(dict(srcs=[c['image']]))[0]
    else:
        im = BYID[c['cover']]['imgs'][0]
    return '/img/' + (im['t'] if small else im['s'])

_NAV = {}
def navicons(L):
    if L not in _NAV:
        _NAV[L] = [dict(key=c['key'], name=c['names'][L], path=path_cat(L, c), img=caticon(c)[0], cut=caticon(c)[1],
                        count=sum(1 for p in in_lang(L) if p['key'] == c['key']))
                   for c in cats if any(p['key'] == c['key'] for p in in_lang(L))]
    return _NAV[L]

def page_ctx(L, cur, alts_paths, title, desc, active=None, ogimg=None, ogtype='website', jsonld=None, wa_link=None):
    t = T[L]
    r = lambda target: rel(target, cur)
    alts = [(l2, absu(alts_paths[l2])) for l2 in LANGS if l2 in alts_paths]
    if 'en' in alts_paths:
        alts.append(('x-default', absu(alts_paths['en'])))
    langlinks = [(l2, r(alts_paths.get(l2, path_home(l2)))) for l2 in LANGS]
    fcats = [dict(name=c['names'][L], path=path_cat(L, c)) for c in cats if any(p['key'] == c['key'] for p in in_lang(L))]
    return dict(L=L, t=t, c=CONTACT, r=r, title=title, desc=desc[:158], canonical=absu(cur), alts=alts, langlinks=langlinks,
                langnames=LANG_NAMES, locale=LOCALE[L], ogimg=ogimg, ogtype=ogtype, jsonld=[ld(j) for j in (jsonld or [])],
                noindex=NOINDEX, active=active, logo=LOGO, chat=CHAT, home=path_home(L), p_products=path_products(L),
                p_about=path_page(L, 'about'), p_contact=path_page(L, 'contact'), p_catalog=path_page(L, 'catalog'),
                wa_general=wa(t['wa_general']), wa_link=wa_link, fcats=fcats,
                x=XT[L], s=ST[L], icons_svg=ICOSVG, catnav=navicons(L), social_svg=SOCIAL_SVG)

def write(path, htmltext):
    fp = DIST + path + ('index.html' if path.endswith('/') else '')
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w').write(htmltext)

def pview(L, p):
    return dict(id=p['id'], name=p['names'][L], desc=p['descs'][L], code=p['code'], path=path_prod(L, p), img=p['imgs'][0], imgs=p['imgs'])

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": absu(u)} for i, (n, u) in enumerate(items)]}

# ---------- üret ----------
def build():
    if PREVIEW and os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST, exist_ok=True)
    if PREVIEW:
        os.makedirs(DIST + '/img', exist_ok=True)
        for big, short in SHORT.items():
            shutil.copy(CACHE + '/' + big, DIST + '/img/' + short)
    if os.path.exists(DIST):
        for x in os.listdir(DIST):
            if x != 'img':
                shutil.rmtree(f'{DIST}/{x}') if os.path.isdir(f'{DIST}/{x}') else os.remove(f'{DIST}/{x}')
    shutil.copytree(HERE + '/static', DIST + '/static')
    open(DIST + '/favicon.svg', 'w').write(LOGO.replace(' aria-hidden="true"', ' xmlns="http://www.w3.org/2000/svg"'))
    sitemap = []  # (path, {lang: path})
    for L in LANGS:
        t = T[L]
        LP = in_lang(L)
        lcats = [c for c in cats if any(p['key'] == c['key'] for p in LP)]
        idx = [[p['names'][L], p['code'] or '', CAT[p['key']]['names'][L], path_prod(L, p), '/img/' + p['imgs'][0]['t'], p['descs'][L]] for p in LP]
        idx_json = json.dumps(idx, ensure_ascii=False, separators=(',', ':'))
        os.makedirs(DIST + '/' + L, exist_ok=True)
        open(DIST + '/' + L + '/search.json', 'w').write(idx_json)
        env.globals['idx_v'] = hashlib.md5(idx_json.encode()).hexdigest()[:8]
        env.globals['st'] = SEARCH_T[L]
        # ana sayfa
        cur = path_home(L)
        alts = {l2: path_home(l2) for l2 in LANGS}
        hero = pick(52)['imgs'][0]
        jl = [{"@context": "https://schema.org", **ORG},
              {"@context": "https://schema.org", "@type": "WebSite", "@id": BASE + "/#web", "url": BASE + "/", "name": "Reyonfix",
               "inLanguage": L, "publisher": {"@id": BASE + "/#org"}},
              {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": L,
               "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t['faq']]}]
        ctx = page_ctx(L, cur, alts, f"Reyonfix · {t['tagline']}", t['meta_home'], ogimg=BASE + '/img/' + hero['l'], jsonld=jl)
        ctx.update(catimg=dict(s='/img/' + pick(54)['imgs'][0]['s'], r=pick(54)['imgs'][0]['r']), catalog_url=CATALOG_URL[L])
        icons = [dict(name=c['names'][L], path=path_cat(L, c), img=caticon(c)[0], cut=caticon(c)[1]) for c in lcats]
        ccards = []
        for c in lcats:
            ccards.append(dict(name=c['names'][L], desc=c['descs'][L], path=path_cat(L, c), img=favimg(c),
                               count=sum(1 for p in LP if p['key'] == c['key']), bg=PASTEL[len(ccards) % len(PASTEL)]))
        def pc(ids, pastel=False):
            out = []
            for i in ids:
                p = BYID.get(i)
                if not p or L not in p['names']: continue
                v = pview(L, p); v['img'] = '/img/' + p['imgs'][0]['s']; v['bg'] = PASTEL[len(out) % len(PASTEL)] if pastel else ''
                out.append(v)
            return out
        x = XT[L]
        wc = pc(TAGGED['duvar'], True)
        shelves = []
        for k, _ in SHELVES:
            it = pc(TAGGED[k])
            if len(it) >= 3: shelves.append(dict(a=x["sh"][k][0], b=x["sh"][k][1], plist=it))
        ctx.update(s=ST[L], icons=icons, wcards=wc, ccards=ccards, x=x, newc=pc(TAGGED['yeni'], True), shelves=shelves, icons_svg=ICOSVG)
        write(cur, env.get_template('home').render(**ctx)); sitemap.append((cur, alts))

        # tüm ürünler
        cur = path_products(L)
        alts = {l2: path_products(l2) for l2 in LANGS}
        blocks = []
        for c in lcats:
            items = [pview(L, p) for p in LP if p['key'] == c['key']]
            for it in items: it['img'] = dict(s='/img/' + it['img']['s'])
            blocks.append(dict(key=c['key'], name=c['names'][L], path=path_cat(L, c), plist=items))
        ctx = page_ctx(L, cur, alts, f"{t['all_products']} · Reyonfix", f"{t['all_products_p']} {t['cats_p']}", active='products',
                       jsonld=[crumbs_ld([(t['home'], path_home(L)), (t['all_products'], cur)])])
        ctx.update(blocks=blocks, catalog_url=CATALOG_URL[L])
        write(cur, env.get_template('products').render(**ctx)); sitemap.append((cur, alts))

        # kategoriler
        for c in lcats:
            cur = path_cat(L, c)
            alts = {l2: path_cat(l2, c) for l2 in LANGS if any(p['key'] == c['key'] for p in in_lang(l2))}
            items = [pview(L, p) for p in LP if p['key'] == c['key']]
            for it in items: it['img'] = dict(s='/img/' + it['img']['s'])
            name = c['names'][L]
            jl = [crumbs_ld([(t['home'], path_home(L)), (t['nav_products'], path_products(L)), (name, cur)]),
                  {"@context": "https://schema.org", "@type": "CollectionPage", "name": name, "description": c['descs'][L], "inLanguage": L,
                   "url": absu(cur), "mainEntity": {"@type": "ItemList", "numberOfItems": len(items),
                   "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": absu(it['path']), "name": it['name']} for i, it in enumerate(items)]}}]
            ctx = page_ctx(L, cur, alts, f"{name} · Reyonfix", f"{c['descs'][L]} {len(items)} {t['models']}.", active='products',
                           ogimg=BASE + '/img/' + items[0]['img']['s'], jsonld=jl)
            ctx.update(cat=dict(key=c['key'], name=name, desc=c['descs'][L]), items=items, catalog_url=CATALOG_URL[L],
                       allcats=[dict(key=x['key'], name=x['names'][L], path=path_cat(L, x)) for x in lcats])
            write(cur, env.get_template('category').render(**ctx)); sitemap.append((cur, alts))

        # ürünler
        for p in LP:
            c = CAT[p['key']]
            cur = path_prod(L, p)
            alts = {l2: path_prod(l2, p) for l2 in LANGS if l2 in p['names']}
            pv = pview(L, p)
            pv['imgs'] = [dict(s='/img/' + im['s'], l='/img/' + im['l'], r=im['r']) for im in p['imgs']]
            name, cname = pv['name'], c['names'][L]
            msg = (t['wa_msg'] if p['code'] else t['wa_msg_nocode']).format(name=name, code=p['code'])
            # Fiyat yayımlanmadığı için Product yerine Service (ölçüye özel imalat): Search Console "ürün snippet'i" hatası üretmez
            prod_ld = {"@context": "https://schema.org", "@type": "Service", "serviceType": cname, "name": name, "description": pv['desc'],
                       "image": [absu(im['l']) for im in pv['imgs']], "category": cname, "url": absu(cur), "inLanguage": L,
                       "brand": {"@type": "Brand", "name": "Reyonfix"}, "provider": {"@id": BASE + "/#org"},
                       "areaServed": ["TR", "EU", "Middle East"], "additionalProperty": [{"@type": "PropertyValue", "name": "Made to measure", "value": "true"}]}
            if p['code']:
                prod_ld['identifier'] = p['code']
            jl = [prod_ld, crumbs_ld([(t['home'], path_home(L)), (t['nav_products'], path_products(L)), (cname, path_cat(L, c)), (name, cur)])]
            rel_items = [pview(L, q) for q in LP if q['key'] == p['key'] and q['id'] != p['id']][:12]
            for it in rel_items: it['img'] = dict(s='/img/' + it['img']['s'])
            desc = f"{pv['desc']}" + (f" {t['code']}: {p['code']}." if p['code'] else '')
            ctx = page_ctx(L, cur, alts, f"{name} · {cname} · Reyonfix", desc, active='products', ogtype='product',
                           ogimg=absu(pv['imgs'][0]['l']), jsonld=jl, wa_link=wa(msg))
            pv['details'] = [x.strip() for x in (p['details'].get(L) or '').split('\n\n') if x.strip()]
            pv['features'] = p['features'].get(L) or []
            pv['uses'] = p['uses'].get(L) or []
            if pv['details']:
                prod_ld['description'] = pv['details'][0]
            jl[0] = prod_ld
            ctx.update(p=pv, cat=dict(name=cname, path=path_cat(L, c)), related=rel_items, reviews_html=review_section(L, str(p['id']), name))
            write(cur, env.get_template('product').render(**ctx)); sitemap.append((cur, alts))

        # hakkımızda, iletişim, katalog
        for key, tpl, title in [('about', 'about', t['about_h']), ('contact', 'contact', t['contact_h']), ('catalog', 'catalog', t['catalog_page_h'])]:
            cur = path_page(L, key)
            alts = {l2: path_page(l2, key) for l2 in LANGS}
            jl = [crumbs_ld([(t['home'], path_home(L)), (title, cur)])]
            if key in ('about', 'contact'):
                jl.append({"@context": "https://schema.org", **ORG})
            lead = {'about': t['about_p'][0], 'contact': t['contact_lead'], 'catalog': t['catalog_page_lead']}[key]
            ctx = page_ctx(L, cur, alts, f"{title} · Reyonfix", lead, active=key, jsonld=jl)
            img = pick({'about': 103, 'contact': 52, 'catalog': 147}[key])['imgs'][0]
            ctx.update(img=dict(l='/img/' + img['l'], r=img['r']), catalog_url=CATALOG_URL[L], catalogs=CATALOG_URL, langs=LANGS)
            write(cur, env.get_template(tpl).render(**ctx)); sitemap.append((cur, alts))

        # 404
        ctx = page_ctx(L, f'/{L}/404.html', {l2: path_home(l2) for l2 in LANGS}, f"404 · Reyonfix", t['not_found'])
        ctx['noindex'] = True
        write(f'/{L}/404.html', env.get_template('404').render(**ctx))

    write_root(sitemap)
    write_ai_files()
    if PREVIEW:
        for big, short in BIG.items():
            shutil.copy(CACHE + '/' + big, DIST + '/img/' + short)
        for big, short in SHORT.items():
            if not os.path.exists(DIST + '/img/' + short):
                shutil.copy(CACHE + '/' + big, DIST + '/img/' + short)
    else:
        os.makedirs(DIST + '/img', exist_ok=True)
        keep = set(USED)
        for f in os.listdir(DIST + '/img'):
            if f not in keep:
                os.remove(DIST + '/img/' + f)
        for f in keep:
            if not os.path.exists(DIST + '/img/' + f):
                shutil.copy(CACHE + '/' + f, DIST + '/img/' + f)
        if os.path.isdir(ROOT + '/katalog'):
            shutil.copytree(ROOT + '/katalog', DIST + '/katalog')
        if os.path.isdir(ROOT + '/admin'):
            shutil.copytree(ROOT + '/admin', DIST + '/admin')
        if os.path.isdir(ROOT + '/yonetim'):
            shutil.copytree(ROOT + '/yonetim', DIST + '/yonetim')
    write_redirects()
    print('pages:', len(sitemap))

def write_root(sitemap):
    # dil seçici kök sayfa
    links = ''.join(f'<a href="{(L + "/index.html") if PREVIEW else (L + "/")}" hreflang="{L}" lang="{L}">{LANG_NAMES[L]}</a>' for L in LANGS)
    alts = ''.join(f'<link rel="alternate" hreflang="{L}" href="{BASE}/{L}/">' for L in LANGS) + f'<link rel="alternate" hreflang="x-default" href="{BASE}/en/">'
    js = '' if PREVIEW else '<script>try{if(!sessionStorage.getItem("rf")){sessionStorage.setItem("rf",1);var l=(navigator.language||"en").slice(0,2).toLowerCase();var m={tr:1,en:1,de:1,fr:1,ar:1};location.replace("/"+(m[l]?l:"en")+"/")}}catch(e){}</script>'
    robots = '<meta name="robots" content="noindex,nofollow">' if NOINDEX else ''
    open(DIST + '/index.html', 'w').write(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reyonfix · Market & store fixtures · Since 1994</title><meta name="description" content="Reyonfix (Huzur Pano, Istanbul): made-to-measure produce displays, olive bars, bakery cabinets, market shelving and store fixtures since 1994.">{robots}
<link rel="canonical" href="{BASE}/">{alts}<link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="static/style.css?v={CSS_V}">{js}</head>
<body><main class="chooser"><div><a class="logo" href="./">{LOGO}<span>Reyon<b>fix</b></span></a>
<p class="lead" style="margin:18px auto 0">Market &amp; store fixtures · Since 1994</p>
<div class="list">{links}</div></div></main></body></html>''')
    # sitemap.xml
    xs = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for path, alts in sitemap:
        xs.append(f'<url><loc>{absu(path)}</loc>' + ''.join(f'<xhtml:link rel="alternate" hreflang="{l2}" href="{absu(a)}"/>' for l2, a in alts.items()) + '</url>')
    xs.append('</urlset>')
    open(DIST + '/sitemap.xml', 'w').write('\n'.join(xs))
    rb = 'User-agent: *\n' + ('Disallow: /\n' if NOINDEX else 'Allow: /\nDisallow: /yonetim/\nDisallow: /api/\n') + f'\nSitemap: {BASE}/sitemap.xml\n'
    open(DIST + '/robots.txt', 'w').write(rb)
    open(DIST + '/_headers', 'w').write('/img/*\n  Cache-Control: public, max-age=31536000, immutable\n/static/*\n  Cache-Control: public, max-age=604800\n/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n')

def write_ai_files():
    # llms.txt — yapay zekâ asistanları için özet
    L = 'en'
    lines = ['# Reyonfix', '',
             '> Reyonfix is the brand of Huzur Pano (Istanbul, Turkey, founded 1994). It designs, manufactures and installs made-to-measure fixtures for supermarkets, greengrocers, olive and deli counters, bakeries, cafés and specialty stores. 200+ models in 13 categories. Production in its own 2,000 m² factory in Sancaktepe, Istanbul. Website available in Turkish, English, German, French and Arabic.',
             '', '## Key facts', '',
             '- Manufacturer: Huzur Pano (brand: Reyonfix), founded 1994, Istanbul, Turkey',
             '- Products are made to measure; materials, colours and accessories are chosen per project',
             '- Design, production and installation by the company’s own team; quotes for projects in Turkey and abroad',
             f"- Contact: {CONTACT['phone1']} · WhatsApp {CONTACT['mobile']} · {CONTACT['email']}",
             f"- Address: {CONTACT['street']}, {CONTACT['postal']} {CONTACT['city']} / {CONTACT['region']}, Turkey",
             '- Product images on the site show example installations; each unit is built to the customer’s dimensions',
             '- Prices are not published; quotes are prepared per project',
             '', '## Main pages', '']
    for l2 in LANGS:
        lines.append(f"- [{LANG_NAMES[l2]}]({absu(path_home(l2))}): {T[l2]['tagline']}")
    lines += [f"- [All products (EN)]({absu(path_products('en'))})", f"- [Contact (EN)]({absu(path_page('en', 'contact'))})",
              f"- [Product catalogue 2026 (PDF)]({CATALOG_URL['en']})", '', '## Categories', '']
    for c in cats:
        lines.append(f"- [{c['names']['en']}]({absu(path_cat('en', c))}): {c['descs']['en']}")
    lines += ['', '## Products', '']
    for c in cats:
        lines += [f"### {c['names']['en']} ({c['names']['tr']})", '']
        for p in prods:
            if p['key'] == c['key']:
                code = f" Code: {p['code']}." if p['code'] else ''
                lines.append(f"- [{p['names']['en']}]({absu(path_prod('en', p))}): {p['descs']['en']}{code} TR: {p['names']['tr']}")
        lines.append('')
    open(DIST + '/llms.txt', 'w').write('\n'.join(lines))

def write_redirects():
    # eski manavreyonu.com.tr ürün adresleri -> yeni Türkçe sayfalar (yayına alırken 301 için)
    rows = ['old_url,new_url']
    for p in prods:
        rows.append(f"{p['old_url']},{absu(path_prod('tr', p))}")
    open(DIST + '/redirects-manavreyonu.csv', 'w').write('\n'.join(rows))

if __name__ == '__main__':
    build()
