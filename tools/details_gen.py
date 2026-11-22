# Ürün detay açıklamaları üretici (bir kerelik): ürün adı/tanımındaki gerçek özelliklerden 5 dilde metin
# Çıktı: content/products/*.json içine "details" (paragraf) ve "features" (madde listesi) alanları
import json, glob, re, sys

LANGS = ['tr', 'en', 'de', 'fr', 'ar']

# ---- özellik algılama (yalnızca ürün adı + eski başlık + kısa tanım) ----
def detect(text):
    t = text.lower()
    a = []
    def has(*w): return any(x in t for x in w)
    if has('aynalı') and not has('aynasız'): a.append('aynali')
    if has('aynasız'): a.append('aynasiz')
    if has('duvar'): a.append('duvar')
    if has('orta alan', 'meyve adası', 'ada '): a.append('orta')
    if has('tekerl', 'tekerli', 'seyyar', 'taşınabilir', 'taşınan'): a.append('tekerli')
    m = re.search(r'(\d)\s*katlı', t)
    if m: a.append('kat' + m.group(1))
    if has('tablalı', 'tabla'): a.append('tablali')
    if has('sepetli', 'sepet'): a.append('sepetli')
    if has('kapaklı'): a.append('kapakli')
    if has('çekmece'): a.append('cekmeceli')
    if has('çatılı'): a.append('catili')
    if has('paslanmaz'): a.append('paslanmaz')
    if has('ahşap', 'ahsap'): a.append('ahsap')
    if has('metal'): a.append('metal')
    if has('dış mekan', 'dış alan', 'dış manav', 'dükkan önü', 'dükkan önleri', 'cadde', 'sokak', 'sahil', 'park'): a.append('dis')
    if has('çift taraflı'): a.append('cift')
    if has('modüler'): a.append('moduler')
    if has('dönen'): a.append('donen')
    if has('yaylı', 'yay sistem'): a.append('yayli')
    if has('sisleme'): a.append('sisleme')
    if has('havuz', 'hazne'): a.append('hazneli')
    if has('kilitli'): a.append('kilitli')
    if has('pleksi'): a.append('pleksi')
    if has(' led', 'ışıklı'): a.append('isikli')
    if has('mermer'): a.append('mermer')
    if has('soğutmalı'): a.append('sogutmali')
    if has('ayar'): a.append('ayarli')
    m = re.search(r'(\d+)\s*ünite', t)
    if m: a.append('unite' + m.group(1))
    return a

# ---- özellik maddeleri ----
F = {
 'aynali':   ['Aynalı arka panel', 'Mirrored back panel', 'Spiegelrückwand', 'Fond miroir', 'لوح خلفي مرآتي'],
 'aynasiz':  ['Aynasız, sade gövde', 'Clean design without mirror', 'Schlichte Ausführung ohne Spiegel', 'Design épuré sans miroir', 'تصميم بسيط بدون مرآة'],
 'duvar':    ['Duvar boyunca kullanım', 'Runs along the wall', 'Für die Wandaufstellung', 'Installation le long du mur', 'يُركَّب على امتداد الجدار'],
 'orta':     ['Orta alan (ada) kullanımı', 'Island / mid-floor use', 'Für die Raummitte (Insel)', 'Utilisation en îlot central', 'للاستخدام في وسط المتجر'],
 'tekerli':  ['Tekerlekli, kolay taşınır', 'On castors, easy to move', 'Auf Rollen, leicht zu verschieben', 'Sur roulettes, facile à déplacer', 'بعجلات وسهل التنقل'],
 'kat2':     ['2 katlı sunum', '2-tier display', '2 Etagen', 'Présentation sur 2 niveaux', 'عرض على طابقين'],
 'kat3':     ['3 katlı sunum', '3-tier display', '3 Etagen', 'Présentation sur 3 niveaux', 'عرض على 3 طوابق'],
 'kat4':     ['4 katlı sunum', '4-tier display', '4 Etagen', 'Présentation sur 4 niveaux', 'عرض على 4 طوابق'],
 'kat5':     ['5 katlı sunum', '5-tier display', '5 Etagen', 'Présentation sur 5 niveaux', 'عرض على 5 طوابق'],
 'tablali':  ['Tablalı sunum yüzeyleri', 'Display trays', 'Präsentationstablare', 'Plateaux de présentation', 'صوانٍ للعرض'],
 'sepetli':  ['Sepetli bölmeler', 'Basket compartments', 'Korbfächer', 'Compartiments à paniers', 'حجيرات بسلال'],
 'kapakli':  ['Kapaklı, korunaklı yapı', 'Lidded, protected design', 'Mit Deckeln, geschützt', 'Avec couvercles, protégé', 'بأغطية وتصميم محمي'],
 'cekmeceli':['Çekmeceli bölmeler', 'Drawer compartments', 'Schubladenfächer', 'Compartiments à tiroirs', 'حجيرات بأدراج'],
 'catili':   ['Çatılı üst yapı', 'Canopy top', 'Mit Überdachung', 'Avec auvent', 'بمظلة علوية'],
 'paslanmaz':['Paslanmaz çelik detaylar', 'Stainless steel details', 'Edelstahl-Elemente', 'Éléments en inox', 'تفاصيل من الستانلس ستيل'],
 'ahsap':    ['Ahşap görünüm ve kaplama', 'Wood finish', 'Holzoptik / Holzverkleidung', 'Finition bois', 'تشطيب خشبي'],
 'metal':    ['Metal gövde', 'Metal frame', 'Metallgestell', 'Structure métallique', 'هيكل معدني'],
 'dis':      ['Dış mekân ve dükkân önü kullanımına uygun', 'Suitable for outdoor and shopfront use', 'Für Außenbereich und Ladenfront geeignet', 'Adapté à l’extérieur et aux devantures', 'مناسب للخارج وواجهات المحلات'],
 'cift':     ['Çift taraflı kullanım', 'Double-sided', 'Beidseitig nutzbar', 'Double face', 'استخدام من الجهتين'],
 'moduler':  ['Modüler, uzatılabilir yapı', 'Modular, extendable', 'Modular erweiterbar', 'Modulaire et extensible', 'تصميم معياري قابل للتمديد'],
 'donen':    ['Dönen sunum', 'Rotating display', 'Drehbare Präsentation', 'Présentation rotative', 'عرض دوّار'],
 'yayli':    ['Yaylı sistem: ürün hep önde', 'Spring system keeps produce at the front', 'Federsystem hält die Ware vorne', 'Système à ressorts: produits toujours à l’avant', 'نظام نوابض يُبقي المنتج في الأمام'],
 'sisleme':  ['Sisleme (nemlendirme) sistemi', 'Misting system', 'Sprühnebelsystem', 'Système de brumisation', 'نظام رذاذ للترطيب'],
 'hazneli':  ['Derin hazneler', 'Deep bins', 'Tiefe Behälter', 'Bacs profonds', 'أحواض عميقة'],
 'kilitli':  ['Kilitli yapı', 'Lockable', 'Abschließbar', 'Verrouillable', 'قابل للقفل'],
 'pleksi':   ['Şeffaf pleksi bölmeler', 'Clear acrylic compartments', 'Transparente Acrylfächer', 'Compartiments en plexiglas transparent', 'حجيرات أكريليك شفافة'],
 'isikli':   ['Işıklı uygulama', 'Illuminated', 'Beleuchtet', 'Éclairé', 'مضيء'],
 'mermer':   ['Mermer tezgah üstü', 'Marble top', 'Marmorplatte', 'Plateau en marbre', 'سطح رخامي'],
 'sogutmali':['Soğutmalı vitrin', 'Refrigerated display', 'Gekühlte Vitrine', 'Vitrine réfrigérée', 'واجهة عرض مبردة'],
 'ayarli':   ['Ayarlanabilir yapı', 'Adjustable', 'Verstellbar', 'Réglable', 'قابل للتعديل'],
}
def unite(n): return [f'{n} ayrı ürün haznesi', f'{n} separate product wells', f'{n} getrennte Behälter', f'{n} bacs séparés', f'{n} حجيرات منفصلة']

COMMON = ['Ölçü, renk ve malzeme projeye göre belirlenir', 'Size, colour and materials tailored to your project',
          'Maße, Farbe und Material nach Projekt', 'Dimensions, couleurs et matériaux selon votre projet', 'المقاس واللون والخامات حسب مشروعك']

# ---- kısa cümleler (paragrafta en fazla 2 tane) ----
S = {
 'aynali':   ['Aynalı arka panel, reyonu daha dolu ve ferah gösterir.', 'The mirrored back panel makes the display look fuller and brighter.', 'Die Spiegelrückwand lässt die Auslage voller und heller wirken.', 'Le fond miroir donne une présentation plus pleine et plus lumineuse.', 'اللوح الخلفي المرآتي يُظهر العرض أكثر امتلاءً وإشراقًا.'],
 'tekerli':  ['Tekerlekleri sayesinde mağaza içinde ya da dükkân önünde kolayca yer değiştirir.', 'Its castors let you move it easily around the store or out to the shopfront.', 'Dank der Rollen lässt sie sich im Laden oder vor dem Geschäft leicht versetzen.', 'Grâce à ses roulettes, il se déplace facilement dans le magasin ou devant la vitrine.', 'بفضل عجلاته يمكن نقله بسهولة داخل المتجر أو أمامه.'],
 'kapakli':  ['Kapaklı yapısı ürünleri toz ve dış etkenlerden korur.', 'Its lids protect products from dust and the elements.', 'Die Deckel schützen die Ware vor Staub und Witterung.', 'Ses couvercles protègent les produits de la poussière et des intempéries.', 'تحمي الأغطية المنتجات من الغبار والعوامل الخارجية.'],
 'cekmeceli':['Çekmeceli bölmeleri ürünleri düzenli ve temiz tutar.', 'Drawer compartments keep products tidy and clean.', 'Schubladenfächer halten die Ware ordentlich und sauber.', 'Les tiroirs gardent les produits rangés et propres.', 'تحافظ الأدراج على المنتجات مرتبة ونظيفة.'],
 'paslanmaz':['Paslanmaz çelik detaylar hijyenik ve kolay temizlenir.', 'Stainless steel details are hygienic and easy to clean.', 'Edelstahl-Elemente sind hygienisch und leicht zu reinigen.', 'Les éléments en inox sont hygiéniques et faciles à nettoyer.', 'تفاصيل الستانلس ستيل صحية وسهلة التنظيف.'],
 'ahsap':    ['Ahşap görünümü mağazaya sıcak ve doğal bir hava katar.', 'The wood finish gives the store a warm, natural feel.', 'Die Holzoptik verleiht dem Geschäft eine warme, natürliche Atmosphäre.', 'La finition bois apporte une ambiance chaleureuse et naturelle.', 'يمنح التشطيب الخشبي المتجر أجواء دافئة وطبيعية.'],
 'cift':     ['Çift taraflı yapısı sayesinde iki yönden de ürüne erişilir.', 'Being double-sided, it can be shopped from both sides.', 'Beidseitig nutzbar – die Ware ist von zwei Seiten erreichbar.', 'Double face, il est accessible des deux côtés.', 'بفضل تصميمه ذي الوجهين يمكن الوصول إلى المنتجات من الجهتين.'],
 'moduler':  ['Modüler yapısıyla alanınıza göre uzatılabilir.', 'Its modular build can be extended to fit your space.', 'Durch den modularen Aufbau an Ihre Fläche anpassbar.', 'Sa conception modulaire s’adapte à votre surface.', 'تصميمه المعياري يتيح تمديده حسب مساحتك.'],
 'dis':      ['Dükkân önü ve dış alanlarda kullanıma uygundur.', 'It is suitable for shopfronts and outdoor areas.', 'Geeignet für Ladenfront und Außenbereich.', 'Il convient aux devantures et aux espaces extérieurs.', 'مناسب لواجهات المحلات والمساحات الخارجية.'],
 'yayli':    ['Yaylı sistemi ürünü önde tutar, ezilme ve fireyi azaltır.', 'Its spring system keeps produce at the front and reduces bruising and waste.', 'Das Federsystem hält die Ware vorne und reduziert Druckstellen und Verluste.', 'Son système à ressorts garde les produits à l’avant et limite les pertes.', 'نظام النوابض يُبقي المنتج في الأمام ويقلل التلف والهدر.'],
 'sisleme':  ['Sisleme sistemi yeşilliklerin tazeliğini daha uzun korur.', 'The misting system keeps greens fresh for longer.', 'Das Sprühnebelsystem hält Blattgemüse länger frisch.', 'La brumisation garde les légumes verts frais plus longtemps.', 'يحافظ نظام الرذاذ على نضارة الخضار الورقية لفترة أطول.'],
 'donen':    ['Dönen yapısı ürünü her açıdan görünür kılar.', 'Its rotating design shows products from every angle.', 'Die Drehfunktion zeigt die Ware von allen Seiten.', 'Sa rotation montre les produits sous tous les angles.', 'تصميمه الدوّار يُظهر المنتجات من كل الجهات.'],
 'pleksi':   ['Şeffaf pleksi bölmeler ürünü hijyenik ve görünür şekilde sunar.', 'Clear acrylic compartments keep products visible and hygienic.', 'Transparente Acrylfächer präsentieren die Ware sichtbar und hygienisch.', 'Les compartiments en plexiglas gardent les produits visibles et protégés.', 'تعرض حجيرات الأكريليك الشفافة المنتجات بشكل واضح وصحي.'],
 'catili':   ['Çatılı üst yapısı sunuma vitrin etkisi katar.', 'The canopy top gives the display a shopfront feel.', 'Die Überdachung verleiht der Auslage Marktstand-Charakter.', 'L’auvent donne à la présentation un effet d’échoppe.', 'تضفي المظلة العلوية طابع الكشك على العرض.'],
 'kat':      ['Katlı yapısı dar alanda yüksek sunum kapasitesi sağlar.', 'Its tiered layout gives high display capacity in a small footprint.', 'Die Etagen bieten viel Präsentationsfläche auf wenig Raum.', 'Ses niveaux offrent une grande capacité sur peu de surface.', 'يوفر تصميمه المتعدد الطوابق سعة عرض كبيرة في مساحة صغيرة.'],
}
ORDER = ['aynali', 'yayli', 'sisleme', 'tekerli', 'kapakli', 'cekmeceli', 'pleksi', 'donen', 'cift', 'kat', 'catili', 'paslanmaz', 'moduler', 'dis', 'ahsap']

# kategori: (paragraf girişi, kullanım alanları)
CAT = {
 'Manav Ekipmanları': (['meyve ve sebzeyi taze, bol ve düzenli göstermek için tasarlandı.', 'is designed to show fruit and vegetables fresh, plentiful and tidy.', 'wurde entwickelt, um Obst und Gemüse frisch, üppig und ordentlich zu präsentieren.', ': une solution conçue pour présenter fruits et légumes de façon fraîche, abondante et ordonnée.', 'صُمِّم لعرض الخضار والفواكه بشكل طازج ووفير ومرتب.'],
   [['Manavlar', 'Süpermarketler', 'Marketlerin meyve-sebze bölümleri', 'Organik ürün mağazaları'],
    ['Greengrocers', 'Supermarkets', 'Produce sections', 'Organic food stores'],
    ['Obst- und Gemüseläden', 'Supermärkte', 'Obst- und Gemüseabteilungen', 'Bioläden'],
    ['Primeurs', 'Supermarchés', 'Rayons fruits et légumes', 'Magasins bio'],
    ['محلات الخضار والفواكه', 'السوبرماركت', 'أقسام الخضار والفواكه', 'متاجر المنتجات العضوية']]),
 'Zeytinlik Reyonu': (['zeytin, meze ve salata çeşitlerini hijyenik ve iştah açıcı şekilde sunmak için tasarlandı.', 'is designed to present olives, meze and salads hygienically and appetisingly.', 'wurde entwickelt, um Oliven, Meze und Salate hygienisch und appetitlich zu präsentieren.', ': une solution conçue pour présenter olives, mezzés et salades de façon hygiénique et appétissante.', 'صُمِّم لعرض الزيتون والمقبلات والسلطات بشكل صحي وفاتح للشهية.'],
   [['Zeytin dükkanları', 'Şarküteriler', 'Süpermarketler', 'Otel ve açık büfeler'],
    ['Olive shops', 'Delicatessens', 'Supermarkets', 'Hotels and buffets'],
    ['Olivengeschäfte', 'Feinkostläden', 'Supermärkte', 'Hotels und Buffets'],
    ['Boutiques d’olives', 'Épiceries fines', 'Supermarchés', 'Hôtels et buffets'],
    ['محلات الزيتون', 'محلات الأطعمة الفاخرة', 'السوبرماركت', 'الفنادق والبوفيهات']]),
 'Unlu Mamul & Fırın Ekipmanları': (['ekmek ve unlu mamulleri taze, temiz ve göz önünde tutmak için tasarlandı.', 'is designed to keep bread and baked goods fresh, clean and in view.', 'wurde entwickelt, um Brot und Backwaren frisch, sauber und sichtbar zu halten.', ': une solution conçue pour garder le pain et les viennoiseries frais, propres et bien visibles.', 'صُمِّم للحفاظ على الخبز والمخبوزات طازجة ونظيفة وظاهرة للزبائن.'],
   [['Fırınlar', 'Marketlerin ekmek reyonları', 'Pastaneler', 'Unlu mamul dükkanları'],
    ['Bakeries', 'Supermarket bread sections', 'Patisseries', 'Bakery shops'],
    ['Bäckereien', 'Brotabteilungen in Supermärkten', 'Konditoreien', 'Backshops'],
    ['Boulangeries', 'Rayons pain des supermarchés', 'Pâtisseries', 'Points chauds'],
    ['المخابز', 'أقسام الخبز في السوبرماركت', 'محلات الحلويات', 'محلات المعجنات']]),
 'Market Ekipmanlari': (['market düzenini ve satış alanının verimini artırmak için tasarlandı.', 'is designed to improve store layout and sales-floor efficiency.', 'wurde entwickelt, um Ordnung und Effizienz auf der Verkaufsfläche zu verbessern.', ': une solution conçue pour améliorer l’organisation et l’efficacité de la surface de vente.', 'صُمِّم لتحسين تنظيم المتجر وكفاءة مساحة البيع.'],
   [['Süpermarketler', 'Mahalle marketleri', 'Şarküteriler', 'Mağazalar'],
    ['Supermarkets', 'Convenience stores', 'Delicatessens', 'Retail stores'],
    ['Supermärkte', 'Nachbarschaftsläden', 'Feinkostläden', 'Einzelhandel'],
    ['Supermarchés', 'Commerces de proximité', 'Épiceries fines', 'Magasins'],
    ['السوبرماركت', 'متاجر الأحياء', 'محلات الأطعمة الفاخرة', 'متاجر التجزئة']]),
 'Yeni Market Ekipmanları': (['satış alanında fark yaratan, dikkat çekici bir sunum için tasarlandı.', 'is designed for an eye-catching display that sets your sales floor apart.', 'wurde für eine auffällige Präsentation entwickelt, die Ihre Verkaufsfläche hervorhebt.', ': une solution conçue pour une présentation remarquable qui distingue votre surface de vente.', 'صُمِّم لعرض لافت يميّز مساحة البيع لديك.'],
   [['Süpermarketler', 'Manavlar', 'Şarküteriler', 'Konsept mağazalar'],
    ['Supermarkets', 'Greengrocers', 'Delicatessens', 'Concept stores'],
    ['Supermärkte', 'Obst- und Gemüseläden', 'Feinkostläden', 'Konzeptläden'],
    ['Supermarchés', 'Primeurs', 'Épiceries fines', 'Concept stores'],
    ['السوبرماركت', 'محلات الخضار والفواكه', 'محلات الأطعمة الفاخرة', 'المتاجر المفاهيمية']]),
 'Şarküteri Ekipmanlari': (['gurme ve şarküteri ürünlerini düzenli ve satışı artıracak şekilde sergilemek için tasarlandı.', 'is designed to display gourmet and deli products neatly and to boost sales.', 'wurde entwickelt, um Feinkost ordentlich und verkaufsfördernd zu präsentieren.', ': une solution conçue pour présenter les produits fins de façon ordonnée et vendeuse.', 'صُمِّم لعرض المنتجات الفاخرة والأطعمة الباردة بشكل منظم يزيد المبيعات.'],
   [['Şarküteriler', 'Gurme dükkanları', 'Süpermarketler', 'Köy ürünleri mağazaları'],
    ['Delicatessens', 'Gourmet shops', 'Supermarkets', 'Farm produce shops'],
    ['Feinkostläden', 'Gourmetläden', 'Supermärkte', 'Hofläden'],
    ['Épiceries fines', 'Boutiques gourmet', 'Supermarchés', 'Boutiques de produits fermiers'],
    ['محلات الأطعمة الفاخرة', 'متاجر الذواقة', 'السوبرماركت', 'متاجر منتجات المزارع']]),
 'Vitamin Bar & Kiosk Bar': (['taze meyve suyu, kahve ya da ürün satışını her yerde mümkün kılmak için tasarlandı.', 'is designed to make fresh juice, coffee or product sales possible almost anywhere.', 'wurde entwickelt, um Saft-, Kaffee- oder Warenverkauf fast überall zu ermöglichen.', ': une solution conçue pour vendre jus frais, café ou produits presque partout.', 'صُمِّم لإتاحة بيع العصائر الطازجة أو القهوة أو المنتجات في أي مكان تقريبًا.'],
   [['Alışveriş merkezleri', 'Süpermarketler', 'Oteller', 'Cadde ve sahil noktaları'],
    ['Shopping malls', 'Supermarkets', 'Hotels', 'Streets and seafronts'],
    ['Einkaufszentren', 'Supermärkte', 'Hotels', 'Straßen und Promenaden'],
    ['Centres commerciaux', 'Supermarchés', 'Hôtels', 'Rues et fronts de mer'],
    ['مراكز التسوق', 'السوبرماركت', 'الفنادق', 'الشوارع والواجهات البحرية']]),
 'Bakliyat ve Kuruyemiş Standları': (['bakliyat, çerez ve kuruyemişi taze görünümlü ve düzenli sunmak için tasarlandı.', 'is designed to present pulses, nuts and dried fruit neatly and fresh-looking.', 'wurde entwickelt, um Hülsenfrüchte, Nüsse und Trockenobst ordentlich und frisch zu präsentieren.', ': une solution conçue pour présenter légumineuses, fruits secs et noix de façon nette et attrayante.', 'صُمِّم لعرض البقوليات والمكسرات والفواكه المجففة بشكل مرتب وجذاب.'],
   [['Kuruyemişçiler', 'Süpermarketler', 'Şarküteriler', 'Kuru gıda mağazaları'],
    ['Nut shops', 'Supermarkets', 'Delicatessens', 'Dry food stores'],
    ['Nussläden', 'Supermärkte', 'Feinkostläden', 'Trockenwarengeschäfte'],
    ['Boutiques de fruits secs', 'Supermarchés', 'Épiceries fines', 'Magasins de produits secs'],
    ['محلات المكسرات', 'السوبرماركت', 'محلات الأطعمة الفاخرة', 'متاجر المواد الجافة']]),
 'Promosyon Stand': (['kampanya ve mevsim ürünlerini öne çıkarmak için tasarlandı.', 'is designed to put promotions and seasonal products in the spotlight.', 'wurde entwickelt, um Aktions- und Saisonware hervorzuheben.', ': une solution conçue pour mettre en avant promotions et produits de saison.', 'صُمِّم لإبراز العروض الترويجية والمنتجات الموسمية.'],
   [['Süpermarketler', 'Manavlar', 'Mağaza girişleri', 'Kasa önleri'],
    ['Supermarkets', 'Greengrocers', 'Store entrances', 'Checkout areas'],
    ['Supermärkte', 'Obst- und Gemüseläden', 'Ladeneingänge', 'Kassenbereiche'],
    ['Supermarchés', 'Primeurs', 'Entrées de magasin', 'Zones de caisse'],
    ['السوبرماركت', 'محلات الخضار والفواكه', 'مداخل المتاجر', 'مناطق الدفع']]),
 'Cafe Pastane Ekipmanları': (['kafe ve pastanelerde hem şık hem kullanışlı bir sunum için tasarlandı.', 'is designed for a stylish yet practical setting in cafés and patisseries.', 'wurde für eine stilvolle und praktische Einrichtung in Cafés und Konditoreien entwickelt.', ': une solution conçue pour un aménagement élégant et pratique en café et pâtisserie.', 'صُمِّم لتجهيز أنيق وعملي في المقاهي ومحلات الحلويات.'],
   [['Kafeler', 'Pastaneler', 'Fırınlar', 'Restoranlar'],
    ['Cafés', 'Patisseries', 'Bakeries', 'Restaurants'],
    ['Cafés', 'Konditoreien', 'Bäckereien', 'Restaurants'],
    ['Cafés', 'Pâtisseries', 'Boulangeries', 'Restaurants'],
    ['المقاهي', 'محلات الحلويات', 'المخابز', 'المطاعم']]),
 'Tekel Rafları': (['tekel ve içecek ürünlerini düzenli, güvenli ve şık sergilemek için tasarlandı.', 'is designed to display tobacco and beverages neatly, securely and elegantly.', 'wurde entwickelt, um Tabakwaren und Getränke ordentlich, sicher und elegant zu präsentieren.', ': une solution conçue pour présenter tabac et boissons de façon ordonnée, sûre et élégante.', 'صُمِّم لعرض منتجات التبغ والمشروبات بشكل منظم وآمن وأنيق.'],
   [['Tekel bayileri', 'Süpermarketler', 'Kasa arkaları', 'İçecek reyonları'],
    ['Tobacconists', 'Supermarkets', 'Behind the checkout', 'Beverage sections'],
    ['Tabakläden', 'Supermärkte', 'Hinter der Kasse', 'Getränkeabteilungen'],
    ['Bureaux de tabac', 'Supermarchés', 'Derrière la caisse', 'Rayons boissons'],
    ['محلات التبغ', 'السوبرماركت', 'خلف منطقة الدفع', 'أقسام المشروبات']]),
 'Dekorasyon Uygulamaları': (['mağazaya kimlik kazandırmak ve reyonları öne çıkarmak için tasarlandı.', 'is designed to give the store its identity and make each section stand out.', 'wurde entwickelt, um dem Geschäft Identität zu geben und Abteilungen hervorzuheben.', ': une solution conçue pour donner une identité au magasin et mettre chaque rayon en valeur.', 'صُمِّم لمنح المتجر هوية مميزة وإبراز كل قسم.'],
   [['Süpermarketler', 'Kasap ve şarküteriler', 'Fırınlar', 'Manavlar'],
    ['Supermarkets', 'Butchers and delis', 'Bakeries', 'Greengrocers'],
    ['Supermärkte', 'Metzgereien und Feinkost', 'Bäckereien', 'Obst- und Gemüseläden'],
    ['Supermarchés', 'Boucheries et traiteurs', 'Boulangeries', 'Primeurs'],
    ['السوبرماركت', 'محلات اللحوم والأجبان', 'المخابز', 'محلات الخضار والفواكه']]),
 'Çicek Dükkanı Dizaynı': (['çiçek ve bitkileri canlı ve düzenli sunmak için tasarlandı.', 'is designed to present flowers and plants vividly and neatly.', 'wurde entwickelt, um Blumen und Pflanzen lebendig und ordentlich zu präsentieren.', ': une solution conçue pour présenter fleurs et plantes de façon vivante et ordonnée.', 'صُمِّم لعرض الزهور والنباتات بشكل حيوي ومرتب.'],
   [['Çiçekçiler', 'Restoran ve kafeler', 'Alışveriş merkezleri', 'Otel girişleri'],
    ['Florists', 'Restaurants and cafés', 'Shopping malls', 'Hotel entrances'],
    ['Blumenläden', 'Restaurants und Cafés', 'Einkaufszentren', 'Hoteleingänge'],
    ['Fleuristes', 'Restaurants et cafés', 'Centres commerciaux', 'Entrées d’hôtel'],
    ['محلات الزهور', 'المطاعم والمقاهي', 'مراكز التسوق', 'مداخل الفنادق']]),
}
CLOSE = ['Ürün, mağazanızın ölçüsüne, rengine ve konseptine göre İstanbul’daki fabrikamızda üretilir; teslimat ve montajı kendi ekibimiz yapar.',
         'It is built in our Istanbul factory to your store’s dimensions, colours and concept, and delivered and installed by our own team.',
         'Gefertigt in unserer Fabrik in Istanbul nach Maß, Farbe und Konzept Ihres Geschäfts; Lieferung und Montage übernimmt unser eigenes Team.',
         'Il est fabriqué dans notre usine d’Istanbul selon les dimensions, couleurs et concept de votre magasin, puis livré et installé par notre équipe.',
         'يُصنع في مصنعنا في إسطنبول حسب مقاسات متجرك وألوانه وتصميمه، ويتولى فريقنا التسليم والتركيب.']
QUOTE = ['Teklif için ürün kodunu, ölçülerinizi ve varsa mağaza fotoğraflarınızı WhatsApp’tan gönderebilirsiniz.',
         'For a quote, send us the product code, your measurements and any store photos via WhatsApp.',
         'Für ein Angebot senden Sie uns Produktcode, Maße und gern Fotos Ihres Geschäfts per WhatsApp.',
         'Pour un devis, envoyez-nous le code produit, vos dimensions et des photos du magasin via WhatsApp.',
         'للحصول على عرض سعر، أرسل لنا رمز المنتج والمقاسات وصور المتجر إن وُجدت عبر واتساب.']

# eski sayfada ürüne özel yazan, doğrulanmış ek özellikler
EXTRA = {135: ['paslanmaz', 'unite15'], 207: ['pleksi', 'kat3', 'ahsap'], 52: ['ahsap', 'paslanmaz']}

def build(d, old_title):
    attrs = detect(d['names']['tr'] + ' | ' + old_title + ' | ' + d['descs'].get('tr', ''))
    if 'aynali' in attrs and 'aynasiz' in attrs: attrs.remove('aynasiz')
    for a in EXTRA.get(d['id'], []):
        if a not in attrs: attrs.append(a)
    intro, uses = CAT.get(d['category'], CAT['Market Ekipmanlari'])
    out_d, out_f = {}, {}
    sent_keys = []
    for k in ORDER:
        if k == 'kat' and any(a.startswith('kat') for a in attrs): sent_keys.append('kat')
        elif k in attrs: sent_keys.append(k)
    sent_keys = sent_keys[:2]
    for i, L in enumerate(LANGS):
        if L not in d['names']: continue
        name = d['names'][L]
        p1 = f"{name} {intro[i]}" if L != 'ar' else f"{name}: {intro[i]}"
        if L == 'tr': p1 = f"{name}, {intro[i]}"
        desc = d['descs'].get(L, '').strip()
        sents = [S[k][i] for k in sent_keys]
        para1 = ' '.join([p1] + ([desc] if desc else []) + sents)
        para2 = CLOSE[i] + ' ' + QUOTE[i]
        out_d[L] = para1 + '\n\n' + para2
        feats = []
        for a in attrs:
            if a.startswith('unite'): feats.append(unite(a[5:])[i])
            elif a in F: feats.append(F[a][i])
        feats = list(dict.fromkeys(feats))[:6] + [COMMON[i]]
        out_f[L] = {'features': feats, 'uses': uses[i]}
    return out_d, out_f, attrs

if __name__ == '__main__':
    OLD = {p['i']: p for p in json.load(open('/home/claude/kat/products.json'))}
    stats = {}
    for f in sorted(glob.glob('content/products/*.json')):
        d = json.load(open(f))
        det, ff, attrs = build(d, OLD.get(d['id'], {}).get('title', ''))
        d['details'] = det
        d['features'] = {L: v['features'] for L, v in ff.items()}
        d['uses'] = {L: v['uses'] for L, v in ff.items()}
        json.dump(d, open(f, 'w'), ensure_ascii=False, indent=2)
        stats[d['id']] = attrs
    if '-v' in sys.argv:
        for k, v in stats.items(): print(k, v)
