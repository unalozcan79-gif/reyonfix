# Görselleri 700 ve 1400 px WebP'ye çevirir (önbellek: .imgcache/)
import os, shutil
from multiprocessing import Pool
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = f'{ROOT}/.imgcache'
SIZES = [(1400, 74), (700, 74), (360, 72)]

def _stem(src):
    rel = os.path.relpath(src, ROOT)
    base = os.path.splitext(os.path.basename(src))[0]
    return base if rel.startswith('media/products/') else 'u-' + base

def _job(src):
    stem = _stem(src)
    out = {W: f'{stem}-{W}.webp' for W, _ in SIZES}
    try:
        im = Image.open(src)
        im = ImageOps.exif_transpose(im)
        w, h = im.size
        if min(w, h) < 300:
            return src, None
        need = [W for W, _ in SIZES if not os.path.exists(f'{CACHE}/{out[W]}')]
        if need:
            im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') and 'A' in im.convert('RGBA').getbands() and im.convert('RGBA').getextrema()[3][0] < 255 else 'RGB')
            for W, q in SIZES:
                if W not in need:
                    continue
                dst = f'{CACHE}/{out[W]}'
                if w <= W and src.lower().endswith('.webp'):
                    shutil.copy(src, dst)
                    continue
                W2 = min(W, w)
                im2 = im if W2 == w else im.resize((W2, round(h * W2 / w)), Image.LANCZOS)
                im2.save(dst, 'WEBP', quality=q, method=4)
        return src, {'files': {'360': out[360], '700': out[700], '1400': out[1400]}, 'ratio': h / w}
    except Exception as e:
        print('görsel atlandı:', src, e)
        return src, None

def process(srcs):
    os.makedirs(CACHE, exist_ok=True)
    srcs = sorted(set(srcs))
    with Pool() as pool:
        res = pool.map(_job, srcs, chunksize=8)
    return {s: m for s, m in res if m}
