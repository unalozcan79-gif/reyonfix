# Kategori ikonu: beyaz zeminli 1-2 ürün fotoğrafından şeffaf, iç içe ikon üretir
# kullanım: python3 tools/make_icon.py cikti.webp on_foto.jpg [arka_foto.jpg]
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

def cutout(path):
    im = Image.open(path).convert('RGB'); im.thumbnail((900, 900))
    w, h = im.size; m = im.copy(); MAG = (255, 0, 255)
    pts = [(x, 0) for x in range(0, w, 15)] + [(x, h - 1) for x in range(0, w, 15)] + [(0, y) for y in range(0, h, 15)] + [(w - 1, y) for y in range(0, h, 15)]
    for p in pts:
        px = m.getpixel(p)
        if px != MAG and min(px) > 225:
            ImageDraw.floodfill(m, p, MAG, thresh=28)
    diff = ImageChops.difference(m, Image.new('RGB', m.size, MAG)).convert('L').point(lambda v: 255 if v > 0 else 0)
    alpha = diff.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert('RGBA'); out.putalpha(alpha)
    return out.crop(alpha.point(lambda v: 255 if v > 40 else 0).getbbox())

def fit(img, mw, mh):
    s = min(mw / img.width, mh / img.height)
    return img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)

def compose(out, a, b=None):
    W, H = 480, 320
    cv = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    A = cutout(a)
    if b:
        B2 = fit(cutout(b), 250, 240); A2 = fit(A, 290, 300)
        cv.alpha_composite(B2, (W - B2.width - 30, H - B2.height - 10))
        cv.alpha_composite(A2, (30, H - A2.height - 4))
    else:
        A2 = fit(A, 400, 300); cv.alpha_composite(A2, ((W - A2.width) // 2, H - A2.height - 4))
    cv.save(out, 'WEBP', quality=88)

if __name__ == '__main__':
    compose(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
