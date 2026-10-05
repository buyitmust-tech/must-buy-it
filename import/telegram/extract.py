"""Extract products from a Telegram channel export (result.json).

How the export is structured (checked against the data):
- Each product is a run of media messages (photos/videos) followed by ONE text
  message with the description. The text comes after the media, not on it.
  Proof: the same video (IMG_2887.MP4) appears before both copies of the
  shoe-box post (7661, 7736).
- Many products were forwarded in bulk, so one timestamp can hold several
  products. Timestamps are therefore used only to split a media run when there
  is a gap of more than GAP_SECONDS inside it.
- A text message right after another text with the same timestamp and no media
  in between is a continuation (e.g. a separate price list) and is merged.

Usage: python3 extract.py <result.json> <out_dir>
"""
import json
import re
import sys
from pathlib import Path

GAP_SECONDS = 60
SKIP_TEXT_MAX_LEN = 25  # very short texts with no price are not products


def text_of(msg):
    t = msg.get("text", "")
    if isinstance(t, str):
        return t
    return "".join(p if isinstance(p, str) else p.get("text", "") for p in t)


def media_of(msg):
    if "photo" in msg:
        return {"type": "photo", "path": msg["photo"], "width": msg.get("width"), "height": msg.get("height"), "message_id": msg["id"]}
    if msg.get("media_type") == "video_file":
        return {"type": "video", "path": msg["file"], "thumbnail": msg.get("thumbnail"), "file_name": msg.get("file_name"), "duration_seconds": msg.get("duration_seconds"), "message_id": msg["id"]}
    if "file" in msg:
        return {"type": "file", "path": msg["file"], "message_id": msg["id"]}
    return None


CURRENCY = r"(?:شيكل|شيقل|شيگل|₪)"
PRICE_HINT = re.compile(r"سعر|" + CURRENCY)


def parse_prices(text):
    """Return a list of {label, price, note} found in the text."""
    lines = [l.strip() for l in text.splitlines()]
    out = []
    for i, line in enumerate(lines):
        if not PRICE_HINT.search(line):
            continue
        work = line
        nums = re.findall(r"\d+", work)
        if not nums and "سعر" in line:
            # price on the next non-empty line ("السعر:" / "🔥 35 شيكل فقط")
            nxt = next((l for l in lines[i + 1:] if l), "")
            if re.search(CURRENCY, nxt) and re.findall(r"\d+", nxt):
                work = nxt
                nums = re.findall(r"\d+", nxt)
        if not nums:
            continue
        before_currency = re.search(r"(\d+)\s*\D{0,4}\s*" + CURRENCY, work)
        price = int(before_currency.group(1)) if before_currency else int(nums[-1])
        if not (5 <= price <= 5000):
            continue
        # "55 شيكل فقط بدل 70" -> compare-at 70
        was = re.search(r"بدل\s*(\d+)", work)
        label = work
        label = re.sub(r"\d+\s*\D{0,4}\s*" + CURRENCY, "", label) if before_currency else label.replace(str(price), "", 1)
        label = re.sub(r"بدل\s*\d+", "", label)
        label = re.sub(r"سعر الجملة|السعر المفاجأة|السعر خرافي|بسعر العرض وحرق بس على|بسعر مميز|بسعر|السعر فقط|السعر|فقط|متوفر|عرض ولا يتفوت|للحجم|\bب\b|بـ", " ", label)
        label = clean(label).strip(" :-–")
        out.append({
            "label": label or None,
            "price": price,
            "compare_at": int(was.group(1)) if was else None,
            "is_wholesale": "الجملة" in line or "الجملة" in work,
            "source_line": line,
        })
    # de-duplicate (a "السعر:" line and the next line can yield the same price)
    seen, uniq = set(), []
    for p in out:
        key = (p["price"], p["label"])
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    return uniq


# keep Arabic diacritics (shadda, tanween...) — \w does not include combining marks
EMOJI = re.compile(r"[^\w\s\u0610-\u061A\u064B-\u065F\u0670\-–()،,.:/%°×+&'\"!؟?]", re.UNICODE)

# Posts that open with an ad headline instead of the product name.
# Keyed by the text message id; names taken from the body of each post.
NAME_OVERRIDES = {
    7443: "جهاز التنظيف بالبخار عالي الضغط",
    7455: "مكواة البخار المحمولة",
    7524: "رف التخزين المربع الدوّار 5 طبقات",
    7536: "رف التخزين الدائري الدوّار 5 طبقات",
    7635: "حوض الاستحمام القابل للنفخ",
    7649: "عربة الرفوف المتعددة الاستخدامات",
    7661: "صندوق تخزين الأحذية القابل للطي",
    7736: "صندوق تخزين الأحذية القابل للطي",
    7687: "سرير هواء مع منفاخ كهربائي",
    7713: "معجون عازل شفاف JAYSUING (100 مل)",
    8699: "كاميرا داش كام مزدوجة HD 1080p",
    8712: "جهاز كشف الدخان الذكي Wi-Fi",
    8723: "مخدة نيام",
    8759: "صندوق حافظة الطعام متعدد الطبقات",
    9672: "حظيرة وقفص ألعاب كبير للأطفال",
    9681: "منظّف فُرش المكياج الذكي",
    9694: "جهاز غسيل السيارات Carwash Rocket",
    9706: "قبعة الصداع",
    9717: "مكواة البخار اليدوية Sokany SK-11046",
    9727: "منظم المطبخ فوق الحوض",
    9738: "طقم دعاسات السيارة (5 قطع)",
    9750: "حزام تثبيت الأطفال على الكرسي",
    9751: "جهاز التمرين المتكامل القابل للطي",
    9819: "الناموسية السحرية للسرير",
    9842: "مكواة البخار المحمولة RAF",
    # names trimmed from "<name> – <slogan>"
    7547: "منشر غسيل حائطي قابل للطي 70 سم",
    7672: "فرشاة تنظيف كهربائية دوارة",
    7746: "ستاند ملابس وجزامة 5 طبقات",
    8690: "مصباح LED مستشعر الحركة",
    8736: "كاميرا السيارة الرباعية Quad Camera",
    8797: "شنطة الكتف الذكية المضادة للسرقة",
    9886: "شنطة الكتف الذكية المضادة للسرقة",
    9764: "بودرة تغطية الشيب Veronni Hairline Powder",
    9794: "مجموعة أداة نقل وترتيب الأثاث",
    9862: "جهاز نشر الروائح والمرطب RAIN FIRE",
    9874: "كورنر تخزين للحمّام",
}

# Same product posted more than once with a different text.
SAME_PRODUCT = {8678: 7623, 9794: 7623}


def clean(s):
    s = EMOJI.sub(" ", s)
    s = s.replace("_", " ").replace("#", " ")
    return re.sub(r"\s+", " ", s).strip()


def guess_name(text):
    for line in text.splitlines():
        c = clean(line).strip(" !.:-–")
        if len(c) >= 4 and not re.match(r"^(توفر لدينا|جديد)$", c):
            return c[:90]
    return None


def main(src, out_dir):
    data = json.loads(Path(src).read_text(encoding="utf-8"))
    msgs = [m for m in data["messages"] if m.get("type") == "message"]

    products, skipped = [], []
    pending_media = []      # media waiting for their caption text
    last_product = None

    def flush_orphans(reason):
        nonlocal pending_media
        if pending_media:
            skipped.append({
                "reason": reason,
                "message_ids": [m["message_id"] for m in pending_media],
                "dates": sorted({m["_date"] for m in pending_media}),
                "media": [{k: v for k, v in m.items() if k != "_date" and k != "_ts"} for m in pending_media],
                "text": None,
            })
            pending_media = []

    for msg in msgs:
        ts = int(msg["date_unixtime"])
        media = media_of(msg)
        text = text_of(msg).strip()

        if media:
            if pending_media and ts - pending_media[-1]["_ts"] > GAP_SECONDS:
                flush_orphans(f"מדיה בלי טקסט (פער של יותר מ-{GAP_SECONDS} שניות עד ההודעה הבאה)")
            media["_ts"], media["_date"] = ts, msg["date"]
            pending_media.append(media)

        if not text:
            continue

        # Continuation: text right after a product text, same timestamp, no media in between
        if (not media and not pending_media and last_product
                and last_product["_ts"] == ts):
            last_product["description"] += "\n\n" + text
            last_product["source_message_ids"].append(msg["id"])
            continue

        prices = parse_prices(text)
        if not pending_media and not media and len(text) <= SKIP_TEXT_MAX_LEN and not prices:
            skipped.append({"reason": "הודעת טקסט קצרה שאינה מוצר", "message_ids": [msg["id"]], "dates": [msg["date"]], "media": [], "text": text})
            continue

        if pending_media and ts - pending_media[-1]["_ts"] > GAP_SECONDS:
            flush_orphans(f"מדיה בלי טקסט (פער של יותר מ-{GAP_SECONDS} שניות עד הטקסט)")

        product = {
            "source_message_ids": [m["message_id"] for m in pending_media] + ([msg["id"]] if not media else []),
            "text_message_id": msg["id"],
            "date": msg["date"],
            "name": NAME_OVERRIDES.get(msg["id"]) or guess_name(text),
            "description": text,
            "prices": prices,
            "images": [m["path"] for m in pending_media if m["type"] == "photo"],
            "videos": [m["path"] for m in pending_media if m["type"] == "video"],
            "_ts": ts,
        }
        products.append(product)
        last_product = product
        pending_media = []

    flush_orphans("מדיה בסוף הייצוא בלי טקסט")

    # Mark reposts of the same product (same opening text, or listed in SAME_PRODUCT)
    first_by_key, id_by_msg = {}, {}
    for i, p in enumerate(products, 1):
        p["id"] = i
        id_by_msg[p["text_message_id"]] = i
        p["prices"] = parse_prices(p["description"])  # re-parse: continuations may add a price list
        key = clean(p["description"])[:60]
        if key in first_by_key:
            p["duplicate_of"] = first_by_key[key]
        elif p["text_message_id"] in SAME_PRODUCT:
            p["duplicate_of"] = id_by_msg[SAME_PRODUCT[p["text_message_id"]]]
        else:
            first_by_key[key] = i
            p["duplicate_of"] = None
        p["price"] = min((x["price"] for x in p["prices"]), default=None)
        p["price_is_wholesale"] = any(x["is_wholesale"] for x in p["prices"])
        p["needs_review"] = []
        if not p["images"] and not p["videos"]:
            p["needs_review"].append("אין תמונות")
        if p["price"] is None:
            p["needs_review"].append("לא נמצא מחיר")
        del p["_ts"]

    ordered = ["id", "name", "price", "price_is_wholesale", "prices", "description", "images", "videos",
               "duplicate_of", "needs_review", "date", "text_message_id", "source_message_ids"]
    products = [{k: p[k] for k in ordered} for p in products]

    out = Path(out_dir)
    meta = {"source_channel": data.get("name"), "source_file": "result.json", "media_base": "ChatExport_2026-10-05/"}
    (out / "products.json").write_text(json.dumps({**meta, "count": len(products), "products": products}, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "skipped.json").write_text(json.dumps({**meta, "count": len(skipped), "skipped": skipped}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"products: {len(products)}  skipped: {len(skipped)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
