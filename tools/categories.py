import json
IDS = """movemate=15403362287932 clothes-drying-cabinet=15405998244156 shoe-cabinet=15405990871356 mop-bucket-wringer=15405988086076
sweat-waist-trainer=15406012662076 heated-massage-belt=15406012563772 desk-punching-ball=15405998604604 pop-up-mosquito-net=15406000111932
electric-baby-rocker=15405583663420 heated-neck-pillow=15405999358268 curved-support-pillow=15406011777340 portable-waist-fan=15406000570684
portable-car-ashtray=15406000505148 u-shaped-toothbrush=15406001127740 nasal-breathing-strips=15406012629308 wall-towel-rack-hooks=15406001193276
rotating-shoe-bag-rack=15406000636220 wooden-storage-shelves=15405990740284 car-air-mattress=15405998145852 electric-spice-grinder=15406011842876
smart-car-battery-charger=15406000701756 baby-travel-bed-bag=15406011613500 smart-shoe-cleaner=15406000734524 music-boxing-machine=15405990707516
portable-espresso-maker=15405991395644 led-bubble-machine=15405999915324 mixdor-pressure-washer=15405999980860 portable-pressure-washer=15406000537916
nail-drill-kit=15406000046396 foldable-home-gym=15405998768444 foldable-massage-pad=15405998801212 humane-mouse-trap-6pcs=15405999423804
reading-night-lamp=15405990773052 makeup-brush-cleaner-dryer=15405591494972 slow-juicer-dsp=15406000668988 electric-lice-comb=15406011810108
heated-hair-comb=15405999325500 bathroom-storage-organizer=15405998113084 bed-guard-rail=15406011646268 truck-360-camera-system=15406001094972
foldable-wireless-keyboard=15405991428412 galaxy-projector-nebula=15406012531004 galaxy-star-projector=15405987955004 teddy-bear-mirror=15406000767292
electric-knife-sharpener=15405998670140 hover-ball-shooting-game=15405999391036 kids-splash-pad=15405999849788 camera-smart-glasses=15406011711804
clothes-rack-with-shelves=15405991493948 wall-folding-drying-rack=15405991362876 over-sink-dish-rack=15405591560508 4g-lte-usb-wifi=15405997949244
bag-sealer=15405987987772 powerbank-earbuds-2in1=15406000603452 book-storage-boxes=15405991461180 air-fryer-15l=15405998014780
crystal-coating-polish=15405998571836 car-shine-spray=15406011744572 nano-coating-spray=15406000079164 teeth-colour-corrector-serum=15406012694844
rolling-storage-cart=15405583630652 gray-hair-touch-up-pen=15405999227196 car-scratch-repair-pen=15405998178620 furniture-repair-kit=15405998866748
4k-security-camera-kit=15405997982012 three-compartment-trash-bin=15406001029436 multi-function-cob-flashlight=15406000013628 led-work-light=15405999948092
wireless-video-doorbell=15406001258812 electric-mosquito-killer=15405998735676 wooden-handle-peeler=15406012727612 electric-vegetable-cutter=15405990838588
kids-electric-drift-scooter=15406012596540 handheld-cordless-vacuum=15405999292732 dust-mite-vacuum=15405998637372 kids-study-desk-chair=15405999882556
corner-computer-desk=15405998276924 rolling-bed-table=15405988020540 folding-camping-table=15405988053308 kids-inflatable-punching-bag=15405999489340
freestanding-punching-bag=15405998833980 kids-bee-backpack=15405999456572 anti-theft-sling-bag=15405998047548 vacuum-travel-backpack=15406001160508
travel-duffel-bag=15406001062204 gym-bag-bottle-holder=15405999259964 waterproof-crossbody-bag=15406001226044"""
ID = dict(x.split('=') for x in IDS.split())
assert len(ID) == 87, len(ID)
CATS = [
 ("kitchen", "מטבח", "🍳", "מוצרים חכמים למטבח: מכשירים, כלים ופתרונות שחוסכים זמן בבישול ובסידור.",
  "over-sink-dish-rack bag-sealer air-fryer-15l slow-juicer-dsp portable-espresso-maker electric-knife-sharpener electric-vegetable-cutter electric-spice-grinder wooden-handle-peeler three-compartment-trash-bin"),
 ("cleaning", "ניקיון", "🧽", "מכשירי ניקיון שעושים את העבודה מהר: שואבים, מכונות שטיפה בלחץ, דלי שטיפה חכם ועוד.",
  "mop-bucket-wringer handheld-cordless-vacuum dust-mite-vacuum mixdor-pressure-washer portable-pressure-washer smart-shoe-cleaner"),
 ("storage-organization", "אחסון וסידור", "📦", "פתרונות אחסון וסידור לבית: מדפים, ארונות, מתקני ייבוש ועגלות שמנצלים כל פינה.",
  "shoe-cabinet rotating-shoe-bag-rack wooden-storage-shelves bathroom-storage-organizer clothes-rack-with-shelves wall-folding-drying-rack rolling-storage-cart wall-towel-rack-hooks book-storage-boxes corner-computer-desk rolling-bed-table"),
 ("home", "בית ועיצוב", "🏠", "מוצרים לבית: תאורה ואווירה, ייבוש כביסה, הגנה מיתושים ומזיקים, וכלים לתחזוקה.",
  "movemate clothes-drying-cabinet pop-up-mosquito-net electric-mosquito-killer humane-mouse-trap-6pcs reading-night-lamp galaxy-projector-nebula galaxy-star-projector teddy-bear-mirror furniture-repair-kit curved-support-pillow"),
 ("beauty-care", "טיפוח ויופי", "💆", "מוצרי טיפוח, יופי ורגיעה: לשיער, לציפורניים, לשיניים, ומכשירי חימום ועיסוי.",
  "u-shaped-toothbrush teeth-colour-corrector-serum nail-drill-kit makeup-brush-cleaner-dryer heated-hair-comb gray-hair-touch-up-pen electric-lice-comb heated-neck-pillow heated-massage-belt foldable-massage-pad nasal-breathing-strips"),
 ("kids-baby", "ילדים ותינוקות", "🧸", "מוצרים לתינוקות ולילדים: נדנדה, מיטה ניידת, מעקה למיטה, צעצועים ומשחקי חוץ.",
  "electric-baby-rocker baby-travel-bed-bag bed-guard-rail led-bubble-machine hover-ball-shooting-game kids-splash-pad kids-electric-drift-scooter kids-study-desk-chair kids-inflatable-punching-bag kids-bee-backpack"),
 ("sport-fitness", "ספורט וכושר", "🥊", "ציוד ספורט וכושר לבית: אגרוף, מכשיר כושר מתקפל, חגורת אימון ותיק לחדר הכושר.",
  "music-boxing-machine freestanding-punching-bag desk-punching-ball foldable-home-gym sweat-waist-trainer gym-bag-bottle-holder"),
 ("car", "רכב", "🚗", "מוצרים לרכב: ניקוי וברק, תיקון שריטות, מטען מצברים, מצלמות ואביזרים לנסיעה.",
  "car-shine-spray crystal-coating-polish nano-coating-spray car-scratch-repair-pen smart-car-battery-charger truck-360-camera-system portable-car-ashtray car-air-mattress"),
 ("gadgets", "גאדג׳טים ואלקטרוניקה", "🔌", "גאדג׳טים ואלקטרוניקה: מצלמות אבטחה, פעמון וידאו, אוזניות, מקלדת, תאורת עבודה ועוד.",
  "4k-security-camera-kit wireless-video-doorbell camera-smart-glasses powerbank-earbuds-2in1 foldable-wireless-keyboard 4g-lte-usb-wifi multi-function-cob-flashlight led-work-light portable-waist-fan"),
 ("travel-bags", "טיולים ותיקים", "🎒", "תיקים ומוצרים לטיולים ולנסיעות: תרמילי נסיעה, תיקי צד, שולחן קמפינג ומזרן לרכב.",
  "vacuum-travel-backpack travel-duffel-bag anti-theft-sling-bag waterproof-crossbody-bag folding-camping-table car-air-mattress portable-waist-fan"),
]
used = set()
for c in CATS:
    for h in c[4].split():
        assert h in ID, h
        used.add(h)
print("missing:", set(ID) - used)
for c in CATS: print(c[0], len(c[4].split()))
if __name__ == "__main__":
    v = {}
    for i, (h, t, e, d, ps) in enumerate(CATS, 1):
        seo_t = f"{t} | Must Buy It"
        assert len(seo_t) <= 60 and len(d) <= 160, h
        v[f"c{i}"] = {"title": t, "handle": h, "descriptionHtml": f"<p>{d}</p>", "seo": {"title": seo_t, "description": d},
                      "sortOrder": "MANUAL", "products": [f"gid://shopify/Product/{ID[x]}" for x in ps.split()]}
    json.dump(v, open("colls.json", "w"), ensure_ascii=False)
