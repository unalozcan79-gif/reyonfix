# Reyonfix — içerik katmanı: content/ klasöründeki JSON dosyalarını okur (yönetim paneli bu dosyaları düzenler)
import json, re, os, glob, unicodedata, zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ['tr', 'en', 'de', 'fr', 'ar']

TRMAP = str.maketrans({'ı': 'i', 'İ': 'i', 'ş': 's', 'Ş': 's', 'ğ': 'g', 'Ğ': 'g', 'ü': 'u', 'Ü': 'u',
                       'ö': 'o', 'Ö': 'o', 'ç': 'c', 'Ç': 'c', 'ß': 'ss', 'æ': 'ae', 'œ': 'oe', '&': ' '})
DEMAP = str.maketrans({'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'Ä': 'ae', 'Ö': 'oe', 'Ü': 'ue'})

def slugify(s, lang=None):
    if lang == 'de':
        s = s.translate(DEMAP)
    s = s.translate(TRMAP)
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s.lower()).strip('-')
    return re.sub(r'-{2,}', '-', s)[:70].strip('-') or 'urun'

def _load(folder):
    out = []
    for f in sorted(glob.glob(f'{ROOT}/content/{folder}/*.json')):
        with open(f, encoding='utf-8') as fh:
            d = json.load(fh)
        d['_file'] = os.path.basename(f)
        out.append(d)
    return out

def _clean(d):
    return {L: (d or {}).get(L, '').strip() for L in LANGS if (d or {}).get(L, '') and str(d.get(L)).strip()}

def _abs(p):
    p = (p or '').lstrip('/')
    return f'{ROOT}/{p}' if p else ''

def settings():
    f = f'{ROOT}/content/settings.json'
    return json.load(open(f, encoding='utf-8')) if os.path.exists(f) else {}

def build_categories():
    cats = []
    for d in sorted(_load('categories'), key=lambda d: (d.get('order', 999), d['_file'])):
        names, descs = _clean(d.get('names')), _clean(d.get('descs'))
        if 'tr' not in names or 'en' not in names:
            continue
        slugs = {L: slugify(names[L], L) for L in names if L != 'ar'}
        slugs['ar'] = slugs['en']
        for L in names:
            descs.setdefault(L, '')
        cats.append(dict(key=d['key'], names=names, descs=descs, slugs=slugs, image=_abs(d.get('image')), icon=_abs(d.get('icon')) if d.get('icon') else '', cover=None))
    return cats

def build_products():
    prods, used = [], set()
    for d in _load('products'):
        if d.get('hidden'):
            continue
        names, descs = _clean(d.get('names')), _clean(d.get('descs'))
        if 'tr' not in names or 'en' not in names:
            continue  # Türkçe ve İngilizce ad zorunlu
        pid = d.get('id')
        if not isinstance(pid, int) or pid in used:
            pid = 1000 + zlib.crc32(d['_file'].encode()) % 900000
        used.add(pid)
        for L in list(names):
            descs.setdefault(L, '')
        slugs = {L: (slugify(names[L], L) if L != 'ar' else slugify(names['en'])) for L in names}
        srcs = [_abs(x) for x in (d.get('images') or []) if x]
        srcs = [s for s in srcs if os.path.exists(s)][:6]
        prods.append(dict(id=pid, key=d.get('category', ''), code=(d.get('code') or '').strip(), names=names, descs=descs,
                          slugs=slugs, srcs=srcs, old_url=d.get('old_url', ''), order=d.get('order', 500),
                          tags=d.get('vitrin') or [],
                          details=d.get('details') or {}, features=d.get('features') or {}, uses=d.get('uses') or {},
                          videos=[v for v in (d.get('videos') or []) if isinstance(v, str)]))
    prods.sort(key=lambda p: (p['order'], p['id']))
    # aynı kategoride aynı adres olmasın
    for L in LANGS:
        seen = set()
        for p in prods:
            if L in p['slugs']:
                k = (p['key'], p['slugs'][L])
                if k in seen:
                    p['slugs'][L] += f"-{p['id']}"
                seen.add((p['key'], p['slugs'][L]))
    return prods
