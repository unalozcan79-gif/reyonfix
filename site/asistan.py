"""Reyonfix yapay zekâ asistanı (metursan'daki asistanın uyarlaması). Ürün verisi: /{dil}/search.json"""
import json
from html import escape as e

SPARK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/></svg>'

A = {
 "tr": dict(fab="Asistana sor", title="Reyonfix Asistan", sub="Ürün bulma ve teklif hazırlama", close="Kapat", ph="Mağazanız için ne arıyorsunuz?", send="Gönder", dialog="Reyonfix yapay zekâ asistanı",
   hi="Merhaba! Ben Reyonfix asistanıyım. Mağazanızı ve ihtiyacınızı anlatın; uygun reyon ve ekipmanları bulup teklif mesajınızı hazırlayayım.",
   chips=["Manav tezgahı", "Zeytin reyonu", "Ekmek dolabı", "Market rafı", "Kasa bankosu", "Fiyat nasıl belirleniyor?"],
   price="Ürünler mağazanıza göre ölçüye özel üretildiği için fiyat; <b>ölçü, malzeme (ahşap / paslanmaz / boyalı sac), adet ve aksesuarlara</b> göre hesaplanır. Ölçü ve adedi yazarsanız teklif mesajınızı hemen hazırlarım.",
   ship="Üretim, paketleme ve sevkiyatı biz yapıyoruz; istenirse mağazanızda montaj da yapılır. Türkiye geneline ve yurt dışına gönderim yapıyoruz. Teslim süresi ürün ve adede göre teklifte belirtilir.",
   draw="Evet, mağaza planınızdan veya çiziminizden (DWG, PDF, fotoğraf) ölçüye özel üretim yapıyoruz. Komple mağaza projesi de hazırlayabiliriz.",
   best="İhtiyacınıza en uygun ürünler:", more="İlginizi çekebilecek ürünler:",
   t_ss="Hijyen gereken reyonlarda (zeytin, şarküteri, ekmek) paslanmaz çelik yüzey önerilir.", t_wood="Doğal ve sıcak bir görünüm için ahşap kaplamalı modeller tercih edilebilir.",
   measure="Teklif için mağaza ölçüsü veya ürün ölçüsü (G×Y×D), adet ve malzeme tercihini yazabilirsiniz.",
   none="Bunu tam eşleştiremedim. Biraz daha anlatır mısınız: hangi reyon için, ne sergilenecek, yaklaşık ölçüsü ne?",
   wa_btn="WhatsApp’tan teklif iste", wa_intro="Merhaba, Reyonfix sitesinden yazıyorum.", wa_prod="İlgilendiğim ürün(ler):", wa_tail="Ölçü: …\nAdet: …",
   phone="Telefon", email="E-posta", address="Adres",
   k_price=["fiyat", "ucret", "kac para", "maliyet", "ne kadar"], k_contact=["adres", "nerede", "konum", "telefon", "iletisim", "mail", "ulas"],
   k_ship=["montaj", "teslim", "kargo", "sevkiyat", "yurt disi", "ihracat"], k_draw=["cizim", "plan", "proje", "ozel olcu", "dwg"],
   k_ss=["paslanmaz", "inox", "hijyen", "zeytin", "sarkuteri", "et"], k_wood=["ahsap", "dogal", "tahta"]),
 "en": dict(fab="Ask the assistant", title="Reyonfix Assistant", sub="Find products and prepare a quote", close="Close", ph="What do you need for your store?", send="Send", dialog="Reyonfix AI assistant",
   hi="Hi! I’m the Reyonfix assistant. Tell me about your store and what you need; I’ll find suitable fixtures and prepare your quote message.",
   chips=["Produce display", "Olive bar", "Bread cabinet", "Supermarket shelving", "Checkout counter", "How is pricing set?"],
   price="All products are made to measure for your store, so the price depends on <b>dimensions, material (wood / stainless / powder-coated steel), quantity and accessories</b>. Send me sizes and quantity and I’ll prepare your quote message.",
   ship="We manufacture, pack and ship; on-site installation is available. We deliver across Türkiye and abroad. Lead time is stated in the quote depending on product and quantity.",
   draw="Yes, we build to your store layout or drawings (DWG, PDF, photos). We can also plan a complete store project.",
   best="Best matches for your needs:", more="You may also like:",
   t_ss="For hygiene-critical areas (olives, deli, bakery) a stainless steel surface is recommended.", t_wood="For a warm, natural look, wood-clad models are a good choice.",
   measure="For a quote, share the store or product dimensions (W×H×D), quantity and preferred material.",
   none="I couldn’t match that exactly. Could you tell me more: which department, what will be displayed, approximate size?",
   wa_btn="Request a quote on WhatsApp", wa_intro="Hello, I’m writing from the Reyonfix website.", wa_prod="Product(s) I’m interested in:", wa_tail="Size: …\nQuantity: …",
   phone="Phone", email="Email", address="Address",
   k_price=["price", "cost", "how much", "quote"], k_contact=["address", "where", "location", "phone", "contact", "email"],
   k_ship=["install", "delivery", "shipping", "export", "abroad"], k_draw=["drawing", "layout", "plan", "custom", "dwg"],
   k_ss=["stainless", "inox", "hygien", "olive", "deli", "meat"], k_wood=["wood", "natural", "timber"]),
 "de": dict(fab="Assistent fragen", title="Reyonfix Assistent", sub="Produkte finden und Angebot vorbereiten", close="Schließen", ph="Was brauchen Sie für Ihren Laden?", send="Senden", dialog="Reyonfix KI-Assistent",
   hi="Hallo! Ich bin der Reyonfix-Assistent. Beschreiben Sie Ihren Laden und Ihren Bedarf; ich finde passende Einrichtungen und bereite Ihre Angebotsanfrage vor.",
   chips=["Obst- und Gemüsestand", "Olivenbar", "Brotregal", "Supermarktregal", "Kassentheke", "Wie entsteht der Preis?"],
   price="Alle Produkte werden für Ihren Laden nach Maß gefertigt; der Preis richtet sich nach <b>Maßen, Material (Holz / Edelstahl / pulverbeschichtetes Blech), Stückzahl und Zubehör</b>. Nennen Sie Maße und Stückzahl, dann bereite ich Ihre Anfrage vor.",
   ship="Wir fertigen, verpacken und versenden; Montage vor Ort ist möglich. Lieferung in die Türkei und ins Ausland. Die Lieferzeit steht im Angebot.",
   draw="Ja, wir fertigen nach Ihrem Ladenplan oder Ihrer Zeichnung (DWG, PDF, Fotos) und planen auch komplette Ladenprojekte.",
   best="Am besten passende Produkte:", more="Das könnte Sie auch interessieren:",
   t_ss="Für hygienekritische Bereiche (Oliven, Feinkost, Backwaren) empfehlen wir Edelstahloberflächen.", t_wood="Für eine warme, natürliche Optik eignen sich Modelle mit Holzverkleidung.",
   measure="Für ein Angebot nennen Sie bitte Laden- oder Produktmaße (B×H×T), Stückzahl und Material.",
   none="Das konnte ich nicht genau zuordnen. Erzählen Sie mehr: welche Abteilung, was wird präsentiert, ungefähre Größe?",
   wa_btn="Angebot per WhatsApp anfragen", wa_intro="Hallo, ich schreibe über die Reyonfix-Website.", wa_prod="Interessante Produkte:", wa_tail="Maße: …\nStückzahl: …",
   phone="Telefon", email="E-Mail", address="Adresse",
   k_price=["preis", "kosten", "wie viel", "angebot"], k_contact=["adresse", "wo ", "standort", "telefon", "kontakt", "mail"],
   k_ship=["montage", "lieferung", "versand", "export", "ausland"], k_draw=["zeichnung", "plan", "nach mass", "dwg"],
   k_ss=["edelstahl", "inox", "hygien", "oliven", "feinkost", "fleisch"], k_wood=["holz", "natur"]),
 "fr": dict(fab="Demander à l’assistant", title="Assistant Reyonfix", sub="Trouver des produits et préparer un devis", close="Fermer", ph="De quoi avez-vous besoin pour votre magasin ?", send="Envoyer", dialog="Assistant IA Reyonfix",
   hi="Bonjour ! Je suis l’assistant Reyonfix. Décrivez votre magasin et vos besoins ; je trouve le mobilier adapté et je prépare votre demande de devis.",
   chips=["Étal fruits et légumes", "Bar à olives", "Vitrine à pain", "Rayonnage supermarché", "Comptoir caisse", "Comment le prix est-il fixé ?"],
   price="Tous les produits sont fabriqués sur mesure pour votre magasin ; le prix dépend des <b>dimensions, du matériau (bois / inox / tôle thermolaquée), de la quantité et des accessoires</b>. Indiquez dimensions et quantité et je prépare votre demande.",
   ship="Nous fabriquons, emballons et expédions ; l’installation sur site est possible. Livraison en Turquie et à l’international. Le délai figure dans le devis.",
   draw="Oui, nous fabriquons d’après votre plan de magasin ou vos dessins (DWG, PDF, photos) et pouvons concevoir un projet complet.",
   best="Produits les plus adaptés :", more="Vous aimerez peut-être aussi :",
   t_ss="Pour les rayons exigeant une hygiène stricte (olives, traiteur, boulangerie), l’inox est recommandé.", t_wood="Pour un rendu chaleureux et naturel, choisissez les modèles habillés de bois.",
   measure="Pour un devis, indiquez les dimensions (L×H×P), la quantité et le matériau souhaité.",
   none="Je n’ai pas trouvé de correspondance exacte. Pouvez-vous préciser : quel rayon, quels produits exposés, quelle taille approximative ?",
   wa_btn="Demander un devis sur WhatsApp", wa_intro="Bonjour, je vous écris depuis le site Reyonfix.", wa_prod="Produit(s) qui m’intéressent :", wa_tail="Dimensions : …\nQuantité : …",
   phone="Téléphone", email="E-mail", address="Adresse",
   k_price=["prix", "tarif", "combien", "cout", "devis"], k_contact=["adresse", "ou etes", "telephone", "contact", "mail"],
   k_ship=["installation", "livraison", "expedition", "export", "etranger"], k_draw=["dessin", "plan", "sur mesure", "dwg"],
   k_ss=["inox", "hygien", "olive", "traiteur", "viande"], k_wood=["bois", "naturel"]),
 "ar": dict(fab="اسأل المساعد", title="مساعد ريونفيكس", sub="إيجاد المنتجات وتجهيز عرض السعر", close="إغلاق", ph="ماذا تحتاج لمتجرك؟", send="إرسال", dialog="مساعد ريونفيكس الذكي",
   hi="مرحبًا! أنا مساعد ريونفيكس. أخبرني عن متجرك واحتياجك، وسأجد لك التجهيزات المناسبة وأجهّز رسالة طلب عرض السعر.",
   chips=["ستاند خضار وفواكه", "ركن الزيتون", "خزانة خبز", "رفوف سوبرماركت", "كاونتر كاشير", "كيف يُحدَّد السعر؟"],
   price="تُصنع جميع المنتجات حسب مقاس متجرك، لذا يُحسب السعر وفق <b>الأبعاد والمادة (خشب / ستانلس / صاج مطلي) والكمية والملحقات</b>. اكتب الأبعاد والكمية وسأجهّز رسالتك فورًا.",
   ship="نتولى التصنيع والتغليف والشحن، ويمكن التركيب في موقعك. نشحن داخل تركيا وإلى الخارج. تُذكر مدة التسليم في عرض السعر.",
   draw="نعم، نصنّع وفق مخطط متجرك أو رسوماتك (DWG، PDF، صور)، ويمكننا تصميم مشروع متجر كامل.",
   best="أنسب المنتجات لاحتياجك:", more="قد يهمك أيضًا:",
   t_ss="للأقسام التي تتطلب نظافة عالية (الزيتون، الأجبان، المخبوزات) يُنصح بسطح من الستانلس.", t_wood="للحصول على مظهر طبيعي ودافئ يمكن اختيار الطرازات المكسوّة بالخشب.",
   measure="لطلب عرض سعر اكتب أبعاد المتجر أو المنتج (العرض×الارتفاع×العمق) والكمية والمادة المفضلة.",
   none="لم أجد تطابقًا دقيقًا. هل يمكنك التوضيح أكثر: أي قسم، وماذا سيُعرض، وما المقاس التقريبي؟",
   wa_btn="اطلب عرض سعر عبر واتساب", wa_intro="مرحبًا، أكتب إليكم من موقع ريونفيكس.", wa_prod="المنتجات التي تهمني:", wa_tail="المقاس: …\nالكمية: …",
   phone="الهاتف", email="البريد الإلكتروني", address="العنوان",
   k_price=["سعر", "اسعار", "كم", "تكلفة", "عرض سعر"], k_contact=["عنوان", "اين", "موقع", "هاتف", "تواصل", "بريد"],
   k_ship=["تركيب", "تسليم", "شحن", "تصدير", "الخارج"], k_draw=["رسم", "مخطط", "مقاس خاص", "dwg"],
   k_ss=["ستانلس", "ستانلس ستيل", "نظافة", "زيتون", "لحوم"], k_wood=["خشب", "طبيعي"]),
}

def markup(L, contact):
    a = A[L]
    data = dict(a, lang=L, wa=contact["wa"], phone_v=contact["phone1"], mobile_v=contact["mobile"], email_v=contact["email"],
                address_v=f"{contact['street']}, {contact['postal']} {contact['city']} / {contact['region']}")
    return (f'<button class="ai-fab" id="aifab" aria-haspopup="dialog">{SPARK}<span>{e(a["fab"])}</span></button>'
            f'<section class="ai" id="ai" role="dialog" aria-label="{e(a["dialog"])}" hidden>'
            f'<div class="ai-h"><div class="av">{SPARK}</div><div><b>{e(a["title"])}</b><small>{e(a["sub"])}</small></div><button id="aix" aria-label="{e(a["close"])}">✕</button></div>'
            f'<div class="ai-b" id="aib" aria-live="polite"></div>'
            f'<form class="ai-f" id="aif"><input id="aii" placeholder="{e(a["ph"])}" autocomplete="off" aria-label="{e(a["ph"])}"><button aria-label="{e(a["send"])}">↑</button></form></section>'
            f'<script>window.AIT={json.dumps(data, ensure_ascii=False)}</script>')
