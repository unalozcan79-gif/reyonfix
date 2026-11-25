"""Ürün sayfası yorum bölümü (5 dil). Veriler /api/review üzerinden gelir; static/app.js işler."""
from html import escape as e
import json

RV = {
 "tr": dict(h="Müşteri yorumları", none="Bu ürün için henüz yorum yok. İlk yorumu siz yazın.", write="Yorum yazın", name="Adınız", org="Firma / şehir (isteğe bağlı)",
            rating="Puanınız", text="Yorumunuz", send="Yorumu gönder", sending="Gönderiliyor…", thanks="Teşekkürler! Yorumunuz onaylandıktan sonra yayınlanacak.",
            err="Gönderilemedi. Lütfen bilgileri kontrol edip tekrar deneyin.", limit="Bugün çok fazla yorum gönderildi. Lütfen yarın tekrar deneyin.",
            note="Yorumlar onaydan sonra yayınlanır. Adınız ve yorumunuz sayfada görünür; e-posta veya telefon istemiyoruz.",
            count="{n} yorum", avg="5 üzerinden {a}", stars=["Çok kötü", "Kötü", "Orta", "İyi", "Mükemmel"], verified="Müşteri yorumu"),
 "en": dict(h="Customer reviews", none="No reviews for this product yet. Be the first to write one.", write="Write a review", name="Your name", org="Company / city (optional)",
            rating="Your rating", text="Your review", send="Submit review", sending="Sending…", thanks="Thank you! Your review will be published after approval.",
            err="Could not send. Please check the details and try again.", limit="Too many reviews sent today. Please try again tomorrow.",
            note="Reviews are published after moderation. Your name and review are shown on the page; we never ask for email or phone.",
            count="{n} reviews", avg="{a} out of 5", stars=["Terrible", "Poor", "Average", "Good", "Excellent"], verified="Customer review"),
 "de": dict(h="Kundenbewertungen", none="Für dieses Produkt gibt es noch keine Bewertungen. Schreiben Sie die erste.", write="Bewertung schreiben", name="Ihr Name", org="Firma / Stadt (optional)",
            rating="Ihre Bewertung", text="Ihr Kommentar", send="Bewertung senden", sending="Wird gesendet…", thanks="Vielen Dank! Ihre Bewertung wird nach Prüfung veröffentlicht.",
            err="Senden fehlgeschlagen. Bitte Angaben prüfen und erneut versuchen.", limit="Heute wurden zu viele Bewertungen gesendet. Bitte morgen erneut versuchen.",
            note="Bewertungen werden nach Prüfung veröffentlicht. Name und Kommentar sind öffentlich sichtbar; wir fragen weder E-Mail noch Telefon ab.",
            count="{n} Bewertungen", avg="{a} von 5", stars=["Sehr schlecht", "Schlecht", "Mittel", "Gut", "Ausgezeichnet"], verified="Kundenbewertung"),
 "fr": dict(h="Avis clients", none="Aucun avis pour ce produit pour l’instant. Soyez le premier à en écrire un.", write="Donner un avis", name="Votre nom", org="Société / ville (facultatif)",
            rating="Votre note", text="Votre avis", send="Envoyer l’avis", sending="Envoi…", thanks="Merci ! Votre avis sera publié après validation.",
            err="Échec de l’envoi. Vérifiez les informations et réessayez.", limit="Trop d’avis envoyés aujourd’hui. Réessayez demain.",
            note="Les avis sont publiés après modération. Votre nom et votre avis sont visibles ; nous ne demandons ni e-mail ni téléphone.",
            count="{n} avis", avg="{a} sur 5", stars=["Très mauvais", "Mauvais", "Moyen", "Bon", "Excellent"], verified="Avis client"),
 "ar": dict(h="آراء العملاء", none="لا توجد آراء لهذا المنتج بعد. كن أول من يكتب رأيه.", write="اكتب رأيك", name="اسمك", org="الشركة / المدينة (اختياري)",
            rating="تقييمك", text="رأيك", send="إرسال الرأي", sending="جارٍ الإرسال…", thanks="شكرًا لك! سيُنشر رأيك بعد المراجعة.",
            err="تعذّر الإرسال. يُرجى التحقق من البيانات والمحاولة مرة أخرى.", limit="أُرسلت آراء كثيرة اليوم. يُرجى المحاولة غدًا.",
            note="تُنشر الآراء بعد المراجعة. يظهر اسمك ورأيك في الصفحة؛ ولا نطلب بريدًا إلكترونيًا أو رقم هاتف.",
            count="{n} آراء", avg="{a} من 5", stars=["سيئ جدًا", "سيئ", "متوسط", "جيد", "ممتاز"], verified="رأي عميل"),
}

def section(L, pid, pname):
    R = RV[L]
    stars = "".join(f'<input type="radio" name="rating" id="rv{i}" value="{i}" required><label for="rv{i}" title="{e(R["stars"][i-1])}">★</label>' for i in range(5, 0, -1))
    return f'''<section class="st-sec rv" id="reviews" data-pid="{pid}" data-pname="{e(pname)}" data-lang="{L}"><div class="wrap">
<div class="rv-top"><h2 class="st-h2"><em>{e(R["h"])}</em></h2><div class="rv-sum" id="rvsum" hidden></div></div>
<div class="rv-grid"><div class="rv-list" id="rvlist"><p class="rv-none">{e(R["none"])}</p></div>
<form class="rv-form" id="rvform" novalidate><h3>{e(R["write"])}</h3>
<fieldset class="rv-stars"><legend>{e(R["rating"])}</legend><div class="st5">{stars}</div></fieldset>
<label>{e(R["name"])}<input name="name" maxlength="60" required autocomplete="name"></label>
<label>{e(R["org"])}<input name="org" maxlength="80" autocomplete="organization"></label>
<label>{e(R["text"])}<textarea name="text" rows="4" maxlength="1500" minlength="10" required></textarea></label>
<input name="hp" class="rv-hp" tabindex="-1" autocomplete="off" aria-hidden="true">
<button class="btn btn-p">{e(R["send"])}</button><p class="rv-msg" id="rvmsg" role="status"></p><p class="rv-note">{e(R["note"])}</p></form></div>
</div></section><script>window.RV={json.dumps(js_strings(L), ensure_ascii=False)}</script>'''

def js_strings(L):
    R = RV[L]
    return {k: R[k] for k in ("sending", "thanks", "err", "limit", "count", "avg", "verified", "stars")}
