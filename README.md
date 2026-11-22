# Reyonfix — reyonfix.com

Huzur Pano'nun 5 dilli (TR · EN · DE · FR · AR) ürün sitesi. Site, `content/` klasöründeki ürün ve kategori dosyalarından otomatik üretilir.

## Ürün eklemek / düzenlemek
1. `https://reyonfix.com/admin/` adresini açın.
2. **Sign In with Token** ile giriş yapın (GitHub'da oluşturulan erişim anahtarı; *Contents: Read and write* izni yeterli).
3. **Ürünler → Yeni** ile ürün ekleyin: kategori, ad (en az Türkçe ve İngilizce), kısa açıklama, fotoğraflar.
4. **Kaydet**'e basın. Cloudflare siteyi 1–3 dakika içinde yeniden yayınlar.

## Klasörler
- `content/products/` — her ürün bir dosya
- `content/categories/` — 13 kategori
- `content/settings.json` — `launched: true` olunca site Google'a açılır
- `media/products/`, `media/uploads/` — fotoğraflar (panelden yüklenenler `uploads`'a gider)
- `site/` — site üreticisi (Python), tasarım (`site/static/style.css`), arayüz metinleri (`site/i18n.py`, `site/wall_i18n.py`)
- `admin/` — yönetim paneli (Sveltia CMS)

## Cloudflare Pages ayarları
- Build command: `pip install -r requirements.txt && python3 site/build.py`
- Build output directory: `dist`
- Environment variable: `PYTHON_VERSION = 3.12`

## Yayına alma (manavreyonu.com.tr ile rekabet olmaması için)
1. Site önce `launched: false` ile yayına çıkar (Google listelemez).
2. `dist/redirects-manavreyonu.csv` dosyasındaki eski → yeni adres eşleşmeleriyle manavreyonu.com.tr'de 301 yönlendirme kurulur.
3. Ardından panelde **Ayarlar → Site yayında** açılır.
