# Ana sayfa: Apple tarzı, duvar tezgahı ağırlıklı bölümler
HERO_IDS = [29, 23, 30]          # tam genişlik bölümler
TILE_IDS = [26, 24, 22, 36, 71, 8]  # 2'li karo ızgara (hepsi duvar tipi)

W = {
'tr': dict(
  heroes=[("Duvar tezgahları.", "Mağazanızın her duvarını satış alanına çevirin."),
          ("Uçtan uca duvar dizaynı.", "Ölçünüze göre tasarlanır, fabrikamızda üretilir, yerinde kurulur."),
          ("Aynalı duvar reyonu.", "Aynalı arka panel, reyonu daha dolu ve ferah gösterir.")],
  more="İnceleyin", quote="Teklif alın", more_s="İnceleyin ›", quote_s="Teklif alın ›",
  tiles_h="Her duvara bir reyon.", tiles_p="Manavdan zeytinliğe, fırından şarküteriye.",
  cats_h="Kategoriye göre keşfedin.", why_h="Neden Reyonfix?"),
'en': dict(
  heroes=[("Wall counters.", "Turn every wall of your store into selling space."),
          ("Wall-to-wall design.", "Designed to your measurements, built in our factory, installed on site."),
          ("Mirrored wall displays.", "A mirrored back panel makes every shelf look fuller and brighter.")],
  more="Learn more", quote="Get a quote", more_s="Learn more ›", quote_s="Get a quote ›",
  tiles_h="A display for every wall.", tiles_p="From produce to olives, bakery to deli.",
  cats_h="Shop by category.", why_h="Why Reyonfix?"),
'de': dict(
  heroes=[("Wandtheken.", "Machen Sie jede Wand Ihres Ladens zur Verkaufsfläche."),
          ("Wandgestaltung aus einer Hand.", "Nach Maß geplant, in unserer Fabrik gefertigt, vor Ort montiert."),
          ("Wandregale mit Spiegel.", "Die Spiegelrückwand lässt jedes Regal voller und heller wirken.")],
  more="Mehr erfahren", quote="Angebot anfordern", more_s="Mehr erfahren ›", quote_s="Angebot anfordern ›",
  tiles_h="Für jede Wand das passende Regal.", tiles_p="Obst und Gemüse, Oliven, Backwaren, Feinkost.",
  cats_h="Nach Kategorie entdecken.", why_h="Warum Reyonfix?"),
'fr': dict(
  heroes=[("Comptoirs muraux.", "Faites de chaque mur de votre magasin un espace de vente."),
          ("Aménagement mur à mur.", "Conçu sur mesure, fabriqué dans notre usine, installé sur place."),
          ("Présentoirs muraux à miroir.", "Le fond miroir rend chaque étagère plus pleine et plus lumineuse.")],
  more="En savoir plus", quote="Demander un devis", more_s="En savoir plus ›", quote_s="Demander un devis ›",
  tiles_h="Un présentoir pour chaque mur.", tiles_p="Fruits et légumes, olives, boulangerie, épicerie fine.",
  cats_h="Explorer par catégorie.", why_h="Pourquoi Reyonfix ?"),
'ar': dict(
  heroes=[("طاولات العرض الجدارية.", "حوّل كل جدار في متجرك إلى مساحة للبيع."),
          ("تصميم جداري متكامل.", "يُصمَّم حسب مقاساتك، ويُصنَّع في مصنعنا، ويُركَّب في موقعك."),
          ("رفوف جدارية بمرايا.", "اللوح الخلفي المرآتي يجعل كل رف يبدو أكثر امتلاءً وإشراقًا.")],
  more="اعرف المزيد", quote="اطلب عرض سعر", more_s="اعرف المزيد ‹", quote_s="اطلب عرض سعر ‹",
  tiles_h="رفّ لكل جدار.", tiles_p="من الخضار والفواكه إلى الزيتون والمخبوزات والأجبان.",
  cats_h="تصفّح حسب الفئة.", why_h="لماذا Reyonfix؟"),
}

# ---- Apple Store düzeni ----
WALL_CARDS = [29, 23, 30, 26, 24, 22, 36, 71, 8, 21, 81, 54]
# kategori ikonu: (ürün id, beyaz zeminli kaynak sırası) — yoksa sahne fotoğrafı
PASTEL = ['#fde4cf', '#fbeec8', '#e3ecd9', '#dbe7f3', '#e9e2f4', '#f7e0e4']

S = {
'tr': dict(cat_a="Kategoriler.", cat_b="Her reyon için doğru çözüm.", intro="Mağazanız için ölçüye özel reyonlar.", l1="Bir uzmanla görüşün", l2="Kataloğu indirin",
  wall_a="Duvar tezgahları.", wall_b="Her duvarı satış alanına çevirin.", eyebrow="DUVAR TİPİ",
  why_a="Reyonfix farkı.", why_b="Tasarımdan montaja tek elden.",
  proc_a="Nasıl çalışıyoruz.", proc_b="Dört adımda yeni reyonunuz.", all="Tüm ürünler"),
'en': dict(cat_a="Categories.", cat_b="The right fixture for every department.", intro="Made-to-measure displays for your store.", l1="Talk to a specialist", l2="Download the catalogue",
  wall_a="Wall counters.", wall_b="Turn every wall into selling space.", eyebrow="WALL TYPE",
  why_a="The Reyonfix difference.", why_b="From design to installation, all in one place.",
  proc_a="How we work.", proc_b="Your new store fixtures in four steps.", all="All products"),
'de': dict(cat_a="Kategorien.", cat_b="Die passende Lösung für jede Abteilung.", intro="Maßgefertigte Ladeneinrichtung für Ihr Geschäft.", l1="Mit einem Experten sprechen", l2="Katalog herunterladen",
  wall_a="Wandtheken.", wall_b="Jede Wand wird zur Verkaufsfläche.", eyebrow="WANDMODELL",
  why_a="Der Reyonfix-Unterschied.", why_b="Planung, Fertigung und Montage aus einer Hand.",
  proc_a="So arbeiten wir.", proc_b="In vier Schritten zur neuen Einrichtung.", all="Alle Produkte"),
'fr': dict(cat_a="Catégories.", cat_b="La bonne solution pour chaque rayon.", intro="Des présentoirs sur mesure pour votre magasin.", l1="Parler à un spécialiste", l2="Télécharger le catalogue",
  wall_a="Comptoirs muraux.", wall_b="Chaque mur devient un espace de vente.", eyebrow="MODÈLE MURAL",
  why_a="La différence Reyonfix.", why_b="De la conception à l’installation, un seul interlocuteur.",
  proc_a="Notre méthode.", proc_b="Votre nouvel agencement en quatre étapes.", all="Tous les produits"),
'ar': dict(cat_a="الفئات.", cat_b="الحل المناسب لكل قسم.", intro="تجهيزات عرض مصنوعة حسب مقاس متجرك.", l1="تحدّث مع مختص", l2="حمّل الكتالوج",
  wall_a="طاولات العرض الجدارية.", wall_b="حوّل كل جدار إلى مساحة للبيع.", eyebrow="طراز جداري",
  why_a="ما يميّز Reyonfix.", why_b="من التصميم إلى التركيب، جهة واحدة.",
  proc_a="كيف نعمل.", proc_b="تجهيزات متجرك الجديدة في أربع خطوات.", all="جميع المنتجات"),
}

# kategori kartı görseli (duvar tipi tercih)
CAT_IMG = {'Manav Ekipmanları': 29, 'Unlu Mamul & Fırın Ekipmanları': 104, 'Şarküteri Ekipmanlari': 157, 'Cafe Pastane Ekipmanları': 8}

# ---- Apple Store mantığı: tematik raflar ----
NEW_IDS = [88, 89, 86, 85, 207, 90, 91, 93, 94, 95, 97, 87]
SHELVES = [  # (anahtar, ürün id'leri)
  ('manav', [52, 57, 44, 34, 79, 76, 40, 42, 50, 55, 58, 63, 65, 68, 74, 77, 78, 80, 47, 38]),
  ('firin', [100, 98, 103, 107, 104, 102, 106, 9, 10, 0, 105, 108]),
  ('zeytin', [147, 141, 142, 138, 140, 143, 144, 145, 146, 151, 152, 153, 135]),
  ('market', [174, 192, 183, 194, 197, 198, 199, 206, 208, 159, 160, 180, 179]),
]
X = {
'tr': dict(feat_h="Öne çıkan özellikler", uses_h="Kullanım alanları", about_h="Ürün hakkında", all_models="Tüm modeller.", made="Ölçüye özel üretim", made_p="Bu ürün mağazanızın ölçüsüne, rengine ve konseptine göre kendi fabrikamızda üretilir.", new_a="En yeniler.", new_b="Mağazanıza yeni soluk.", new_eb="YENİ", code="Model",
  sh={'manav': ("Manavınız için.", "Orta alandan sepetli rafa."), 'firin': ("Fırın ve pastaneniz için.", "Ekmek, simit ve pasta için."),
      'zeytin': ("Zeytinlik ve şarküteri.", "Lezzeti en güzel haliyle sunun."), 'market': ("Market ve kampanya alanları.", "Kuruyemişten kasa önüne.")},
  only_a="Yalnızca Reyonfix’te.", only_b="Fabrikadan mağazanıza.",
  only=[("UZMAN DESTEĞİ", "Bir uzmanla görüşün. Doğru reyonu birlikte seçelim.", "WhatsApp’tan yazın"),
        ("1994’TEN BERİ", "Otuz yılı aşkın üretim deneyimi.", ""),
        ("KENDİ FABRİKAMIZ", "İstanbul Sancaktepe’deki 2.000 m² fabrikamızda üretim.", ""),
        ("ÖLÇÜYE ÖZEL", "Her ürün mağazanızın ölçüsüne, rengine ve konseptine göre üretilir.", ""),
        ("MONTAJ", "Tasarım, üretim ve montaj kendi ekibimizle.", ""),
        ("YURT DIŞI", "Yurt dışındaki projeler için de teklif veriyoruz.", "Teklif isteyin")],
  ql="Hızlı bağlantılar"),
'en': dict(feat_h="Key features", uses_h="Where it’s used", about_h="About this product", all_models="All models.", made="Made to measure", made_p="Built in our own factory to your store’s dimensions, colours and concept.", new_a="The latest.", new_b="A fresh look for your store.", new_eb="NEW", code="Model",
  sh={'manav': ("For your greengrocer.", "From island units to basket shelves."), 'firin': ("For your bakery and café.", "For bread, simit and cakes."),
      'zeytin': ("Olive bar and deli.", "Present flavour at its best."), 'market': ("Supermarket and promotions.", "From nuts to the checkout.")},
  only_a="Only at Reyonfix.", only_b="From our factory to your store.",
  only=[("SPECIALIST HELP", "Talk to a specialist. Let’s choose the right fixture together.", "Message us on WhatsApp"),
        ("SINCE 1994", "More than thirty years of manufacturing experience.", ""),
        ("OUR OWN FACTORY", "Made in our 2,000 m² factory in Sancaktepe, Istanbul.", ""),
        ("MADE TO MEASURE", "Every piece is built to your store’s size, colours and concept.", ""),
        ("INSTALLATION", "Design, production and installation by our own team.", ""),
        ("INTERNATIONAL", "We also quote for projects outside Turkey.", "Request a quote")],
  ql="Quick links"),
'de': dict(feat_h="Merkmale", uses_h="Einsatzbereiche", about_h="Über das Produkt", all_models="Alle Modelle.", made="Nach Maß gefertigt", made_p="Wird in unserer eigenen Fabrik nach Maß, Farbe und Konzept Ihres Geschäfts gefertigt.", new_a="Das Neueste.", new_b="Frischer Wind für Ihr Geschäft.", new_eb="NEU", code="Modell",
  sh={'manav': ("Für Ihren Obst- und Gemüsehandel.", "Vom Mittelraum bis zum Korbregal."), 'firin': ("Für Bäckerei und Café.", "Für Brot, Simit und Kuchen."),
      'zeytin': ("Olivenbar und Feinkost.", "Genuss bestens präsentiert."), 'market': ("Supermarkt und Aktionsflächen.", "Von Nüssen bis zur Kasse.")},
  only_a="Nur bei Reyonfix.", only_b="Aus unserer Fabrik in Ihr Geschäft.",
  only=[("BERATUNG", "Sprechen Sie mit einem Experten. Wir finden gemeinsam die richtige Lösung.", "Per WhatsApp schreiben"),
        ("SEIT 1994", "Über dreißig Jahre Fertigungserfahrung.", ""),
        ("EIGENE FABRIK", "Gefertigt in unserer 2.000 m² großen Fabrik in Sancaktepe, Istanbul.", ""),
        ("NACH MASS", "Jedes Stück nach Maß, Farbe und Konzept Ihres Geschäfts.", ""),
        ("MONTAGE", "Planung, Fertigung und Montage durch unser eigenes Team.", ""),
        ("INTERNATIONAL", "Wir erstellen auch Angebote für Projekte im Ausland.", "Angebot anfordern")],
  ql="Schnellzugriff"),
'fr': dict(feat_h="Points forts", uses_h="Utilisations", about_h="À propos du produit", all_models="Tous les modèles.", made="Fabriqué sur mesure", made_p="Fabriqué dans notre usine selon les dimensions, couleurs et concept de votre magasin.", new_a="Les nouveautés.", new_b="Un nouveau souffle pour votre magasin.", new_eb="NOUVEAU", code="Modèle",
  sh={'manav': ("Pour votre primeur.", "Des îlots centraux aux étagères à paniers."), 'firin': ("Pour votre boulangerie et café.", "Pour le pain, les simits et les gâteaux."),
      'zeytin': ("Bar à olives et épicerie fine.", "Mettez les saveurs en valeur."), 'market': ("Supermarché et promotions.", "Des fruits secs jusqu’aux caisses.")},
  only_a="Seulement chez Reyonfix.", only_b="De notre usine à votre magasin.",
  only=[("CONSEIL", "Parlez à un spécialiste. Choisissons ensemble le bon présentoir.", "Écrire sur WhatsApp"),
        ("DEPUIS 1994", "Plus de trente ans d’expérience en fabrication.", ""),
        ("NOTRE USINE", "Fabriqué dans notre usine de 2 000 m² à Sancaktepe, Istanbul.", ""),
        ("SUR MESURE", "Chaque pièce selon les dimensions, couleurs et concept de votre magasin.", ""),
        ("INSTALLATION", "Conception, fabrication et installation par notre propre équipe.", ""),
        ("INTERNATIONAL", "Nous établissons aussi des devis pour les projets à l’étranger.", "Demander un devis")],
  ql="Liens rapides"),
'ar': dict(feat_h="المزايا الرئيسية", uses_h="مجالات الاستخدام", about_h="عن المنتج", all_models="جميع الطرازات.", made="مصنوع حسب المقاس", made_p="يُصنع في مصنعنا حسب مقاسات متجرك وألوانه وتصميمه.", new_a="الأحدث.", new_b="روح جديدة لمتجرك.", new_eb="جديد", code="الطراز",
  sh={'manav': ("لمحل الخضار والفواكه.", "من وحدات الوسط إلى رفوف السلال."), 'firin': ("للمخبز والمقهى.", "للخبز والسميت والحلويات."),
      'zeytin': ("ركن الزيتون والأطعمة الفاخرة.", "قدّم المذاق بأفضل صورة."), 'market': ("السوبرماركت ومساحات العروض.", "من المكسرات حتى منطقة الدفع.")},
  only_a="فقط لدى Reyonfix.", only_b="من مصنعنا إلى متجرك.",
  only=[("دعم المختصين", "تحدّث مع مختص، ولنختر معًا التجهيز المناسب.", "راسلنا عبر واتساب"),
        ("منذ 1994", "أكثر من ثلاثين عامًا من خبرة التصنيع.", ""),
        ("مصنعنا الخاص", "إنتاج في مصنعنا بمساحة 2000 م² في سنجق تبه، إسطنبول.", ""),
        ("حسب المقاس", "كل قطعة تُصنع حسب مقاس متجرك وألوانه وتصميمه.", ""),
        ("التركيب", "التصميم والتصنيع والتركيب بفريقنا الخاص.", ""),
        ("مشاريع دولية", "نقدّم عروض أسعار للمشاريع خارج تركيا أيضًا.", "اطلب عرض سعر")],
  ql="روابط سريعة"),
}
ICONS = [
 '<path d="M4 5h16v11H9l-5 4z"/>',
 '<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/>',
 '<path d="M3 20V10l6 4V10l6 4V6h6v14z"/>',
 '<path d="M3 15 15 3l6 6L9 21z"/><path d="M7 11l2 2M10 8l2 2M13 5l2 2"/>',
 '<path d="M14 6a4 4 0 0 0 5 5L11 19a2.1 2.1 0 0 1-3-3z"/>',
 '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
]

