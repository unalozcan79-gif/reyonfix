"""Reyonfix katalog düzeltmesi: Manav Reyonu marka/URL metinlerini kaldırır,
Reyonfix markası + reyonfix.com + sosyal medya satırı ekler."""
import re, sys, io, pikepdf, pdfplumber, logging
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logging.getLogger('pdfminer').setLevel(logging.ERROR)
F = '/home/claude/katfix/fonts/'
for n, f in [('MR', 'Montserrat-Regular'), ('MB', 'Montserrat-Bold'), ('ML', 'Montserrat-Light'),
             ('IR', 'Inter-Regular'), ('IM', 'Inter-Medium')]:
    pdfmetrics.registerFont(TTFont(n, F + f + '.ttf'))

TITLES = {'tr': 'Reyonfix Ürün Kataloğu 2026', 'en': 'Reyonfix Product Catalogue 2026',
          'de': 'Reyonfix Produktkatalog 2026', 'fr': 'Catalogue Produits Reyonfix 2026',
          'ar': 'كتالوج منتجات Reyonfix 2026'}
SOC_H = {'tr': 'SOSYAL MEDYA · SOCIAL', 'en': 'SOCIAL MEDIA', 'de': 'SOZIALE MEDIEN · SOCIAL',
         'fr': 'RÉSEAUX SOCIAUX · SOCIAL', 'ar': 'SOCIAL MEDIA'}
SOCIAL = [('INSTAGRAM', '@reyonfix.tr', 'https://www.instagram.com/reyonfix.tr/'),
          ('FACEBOOK', 'facebook.com/reyonfix.tr', 'https://www.facebook.com/reyonfix.tr'),
          ('YOUTUBE', '@reyonfix', 'https://www.youtube.com/@reyonfix'),
          ('LINKEDIN', 'linkedin.com/company/reyonfix', 'https://www.linkedin.com/company/reyonfix'),
          ('X', '@Reyonfix', 'https://x.com/Reyonfix')]


# ---------- ToUnicode çözümü ----------
def parse_cmap(data):
    m = {}
    for blk in re.findall(rb'beginbfchar(.*?)endbfchar', data, re.S):
        for a, b in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            m[int(a, 16)] = bytes.fromhex(b.decode()).decode('utf-16-be', 'ignore')
    for blk in re.findall(rb'beginbfrange(.*?)endbfrange', data, re.S):
        for a, b, c in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            s, e, d = int(a, 16), int(b, 16), int(c, 16)
            for i in range(s, e + 1):
                m[i] = chr(d + i - s)
    return m


def strip_page(pdf, page, cache):
    fonts = page.Resources.get('/Font', {})
    maps = {}
    for k in fonts.keys():
        fo = fonts[k]
        key = fo.objgen
        if key not in cache:
            cache[key] = parse_cmap(fo.ToUnicode.read_bytes()) if '/ToUnicode' in fo else {}
        maps[k] = cache[key]
    ops = pikepdf.parse_content_stream(page)
    blocks, cur, font = [], None, None
    for i, (o, op) in enumerate(ops):
        s = str(op)
        if s == 'BT':
            cur = [i, None, '']
        elif s == 'Tf':
            font = str(o[0])
        elif s in ('Tj', 'TJ', "'", '"') and cur is not None:
            items = o[0] if s == 'TJ' else [o[-1]]
            for it in items:
                if isinstance(it, pikepdf.String):
                    cur[2] += ''.join(maps.get(font, {}).get(b, '?') for b in bytes(it))
        elif s == 'ET' and cur is not None:
            cur[1] = i
            blocks.append(cur)
            cur = None
    norm = [re.sub(r'\s+', '', b[2]).upper() for b in blocks]
    kill = set()
    for j, t in enumerate(norm):
        if t in ('MANAVREYONU', 'WWW.MANAVREYONU.COM.TR'):
            kill.add(j)
        elif t == 'REYONU' and j > 0 and norm[j - 1] == 'MANAV':
            kill.update((j - 1, j))
    if not kill:
        return 0
    drop = set()
    for j in kill:
        drop.update(range(blocks[j][0], blocks[j][1] + 1))
    new = [(o, op) for i, (o, op) in enumerate(ops) if i not in drop]
    page.obj.Contents = pdf.make_stream(pikepdf.unparse_content_stream(new))
    return len(kill)


# ---------- yerleşim bilgisi ----------
PAT_BRAND = r'M\s*A\s*N\s*A\s*V\s*R\s*E\s*Y\s*O\s*N\s*U'
PAT_FOOT = r'W\s*W\s*W\s*\.\s*M\s*A\s*N\s*A\s*V\s*R\s*E\s*Y\s*O\s*N\s*U\s*\.\s*C\s*O\s*M\s*\.\s*T\s*R'
PAT_WEB = r'www\.manavreyonu\.com\.tr'


def rgb(c):
    c = tuple(c or (0, 0, 0))
    return c if len(c) == 3 else (c[0],) * 3


def tracked(cv, x, y, text, font, size, cs):
    t = cv.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(cs)
    t.textOut(text)
    cv.drawText(t)


def width(text, font, size, cs):
    return pdfmetrics.stringWidth(text, font, size) + cs * (len(text) - 1)


def build_overlay(path, lang):
    out = io.BytesIO()
    pl = pdfplumber.open(path)
    W, H = pl.pages[0].width, pl.pages[0].height
    cv = canvas.Canvas(out, pagesize=(W, H))
    stats = dict(brand=0, foot=0, web=0, social=0)
    last = len(pl.pages) - 1
    for pn, p in enumerate(pl.pages):
        H = p.height
        # marka: MANAV REYONU -> REYON FIX
        seen = [(f['x0'], f['top']) for f in p.search(PAT_FOOT, regex=True, case=True)]
        foots = list(seen)
        for m in p.search(PAT_BRAND, regex=True, case=True):
            ch = m['chars']
            if any(abs(m['top'] - b) < 2 and m['x0'] >= a - 1 for a, b in foots):
                continue
            if any(abs(m['x0'] - a) < 2 and abs(m['top'] - b) < 2 for a, b in seen):
                continue
            seen.append((m['x0'], m['top']))
            size = ch[0]['size']
            orig_w = m['x1'] - m['x0']
            cs = (orig_w - width('MANAV', 'ML', size, 0) - width('REYONU', 'MB', size, 0)) / 11
            a, b = 'REYON', 'FIX'
            gap = cs * 1.6
            new_w = width(a, 'ML', size, cs) + gap + width(b, 'MB', size, cs)
            x = m['x0'] if (m['x0'] < W / 2 and lang != 'ar') else m['x1'] - new_w
            base = H - m['bottom'] + size * 0.2
            cv.setFillColorRGB(*rgb(ch[0]['non_stroking_color']))
            tracked(cv, x, base, a, 'ML', size, cs)
            x2 = x + width(a, 'ML', size, cs) + gap
            cv.setFillColorRGB(*rgb(ch[-1]['non_stroking_color']))
            tracked(cv, x2, base, b, 'MB', size, cs)
            cv.linkURL('https://reyonfix.com', (x, base - 2, x + new_w, base + size), relative=0)
            stats['brand'] += 1
        # alt bilgi: WWW.MANAVREYONU.COM.TR -> WWW.REYONFIX.COM
        seen = []
        for m in p.search(PAT_FOOT, regex=True, case=True):
            if any(abs(m['x0'] - a) < 2 and abs(m['top'] - b) < 2 for a, b in seen):
                continue
            seen.append((m['x0'], m['top']))
            ch = m['chars']
            size = ch[0]['size']
            cs = (m['x1'] - m['x0'] - pdfmetrics.stringWidth('WWW.MANAVREYONU.COM.TR', 'IR', size)) / 21
            txt = 'WWW.REYONFIX.COM'
            nw = width(txt, 'IR', size, cs)
            x = m['x0'] if m['x0'] < W / 2 else m['x1'] - nw
            base = H - m['bottom'] + size * 0.2
            cv.setFillColorRGB(*rgb(ch[0]['non_stroking_color']))
            tracked(cv, x, base, txt, 'IR', size, cs)
            cv.linkURL('https://reyonfix.com', (x, base - 2, x + nw, base + size), relative=0)
            stats['foot'] += 1
        # arka kapak: web adresi
        seen = []
        for m in p.search(PAT_WEB, regex=True, case=True):
            if any(abs(m['x0'] - a) < 2 and abs(m['top'] - b) < 2 for a, b in seen):
                continue
            seen.append((m['x0'], m['top']))
            ch = m['chars']
            size = ch[0]['size']
            txt = 'www.reyonfix.com'
            nw = width(txt, 'IR', size, 0)
            x = m['x0'] if lang != 'ar' else m['x1'] - nw
            base = H - m['bottom'] + size * 0.2
            cv.setFillColorRGB(*rgb(ch[0]['non_stroking_color']))
            tracked(cv, x, base, txt, 'IR', size, 0)
            cv.linkURL('https://reyonfix.com', (x, base - 2, x + nw, base + size), relative=0)
            stats['web'] += 1
            if pn == last:
                social_row(cv, p, W, H, lang)
                stats['social'] += 1
        cv.showPage()
    cv.save()
    return out.getvalue(), stats


def social_row(cv, p, W, H, lang):
    # sütun hizası ve altın etiket rengi iletişim tablosundan
    words = p.extract_words()
    labels = [w for w in p.chars if abs(w['size'] - 6.795) < 0.3 and rgb(w['non_stroking_color'])[0] > 0.6
              and rgb(w['non_stroking_color'])[2] < 0.4]
    gold = rgb(labels[0]['non_stroking_color']) if labels else (0.7216, 0.5373, 0.2902)
    top_lbl = min(c['top'] for c in labels) if labels else 254
    xs = sorted({round(c['x0']) for c in labels})
    left = min(xs) if xs else 62.4
    # bilgi bloğunun alt sınırı: etiketin altındaki beyaz 9.5pt satırlar
    body = [c for c in p.chars if abs(c['size'] - 9.495) < 0.3 and c['top'] > top_lbl]
    bottom = max(c['bottom'] for c in body) if body else 310
    right = W - left
    if lang == 'ar':
        right = max(c['x1'] for c in body)
        left = W - right
    y_rule = H - (bottom + 22)
    cv.setStrokeColorRGB(1, 1, 1, alpha=0.18)
    cv.setLineWidth(0.5)
    cv.line(left, y_rule, right, y_rule)
    y_lbl = y_rule - 20
    cv.setFillColorRGB(*gold)
    lbl_cs = 1.55
    head = SOC_H[lang]
    hx = left if lang != 'ar' else right - width(head, 'IR', 6.795, lbl_cs)
    tracked(cv, hx, y_lbl, head, 'IR', 6.795, lbl_cs)
    items = SOCIAL if lang != 'ar' else list(reversed(SOCIAL))
    ws = [max(width(n, 'IM', 6.3, 1.2), width(h, 'IR', 9.0, 0)) for n, h, _ in items]
    gap = min(60, (right - left - sum(ws)) / (len(items) - 1))
    x = left if lang != 'ar' else right - (sum(ws) + gap * (len(items) - 1))
    for (name, handle, url), w in zip(items, ws):
        y1 = y_lbl - 18
        cv.setFillColorRGB(*gold)
        tracked(cv, x, y1, name, 'IM', 6.3, 1.2)
        cv.setFillColorRGB(1, 1, 1)
        tracked(cv, x, y1 - 13, handle, 'IR', 9.0, 0)
        cv.linkURL(url, (x, y1 - 16, x + w, y1 + 8), relative=0)
        x += w + gap


def fix(src, dst, lang):
    ov_bytes, stats = build_overlay(src, lang)
    pdf = pikepdf.open(src)
    cache, removed = {}, 0
    for pg in pdf.pages:
        removed += strip_page(pdf, pg, cache)
    ov = pikepdf.open(io.BytesIO(ov_bytes))
    for pg, op in zip(pdf.pages, ov.pages):
        pg.add_overlay(op)
        if '/Annots' in op.obj:
            ann = pdf.make_indirect(pikepdf.Array([pdf.copy_foreign(a) for a in op.obj.Annots]))
            pg.obj.Annots = ann
    with pdf.open_metadata() as meta:
        meta['dc:title'] = TITLES[lang]
    pdf.docinfo['/Title'] = TITLES[lang]
    pdf.docinfo['/Author'] = 'Reyonfix · Huzur Pano'
    pdf.save(dst, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
    print(lang, 'silinen blok', removed, stats)


if __name__ == '__main__':
    fix(sys.argv[1], sys.argv[2], sys.argv[3])
