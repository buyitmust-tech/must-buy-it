"""Add retail prices to products.json.

Rule agreed with the store owner: retail = wholesale + ₪170–200, ending in 9.
Inside that range, prefer a price ending in 99 or 49; otherwise the lowest
price ending in 9. A variant with a higher wholesale price gets a higher
retail price when the range allows it. Every listed price in the channel is treated as wholesale.
"""
import json
from pathlib import Path

MARKUP_MIN, MARKUP_MAX = 170, 200


def retail(wholesale, above=0):
    """Retail price for a wholesale price; `above` keeps bigger variants priced higher."""
    candidates = [p for p in range(wholesale + MARKUP_MIN, wholesale + MARKUP_MAX + 1) if p % 10 == 9]
    higher = [p for p in candidates if p > above] or candidates[-1:]
    preferred = [p for p in higher if p % 100 in (49, 99)]
    return (preferred or higher)[0]


path = Path(__file__).with_name("products.json")
data = json.loads(path.read_text(encoding="utf-8"))
for p in data["products"]:
    prev_wholesale, prev_retail = None, 0
    for opt in sorted(p["prices"], key=lambda o: o["price"]):
        above = prev_retail if prev_wholesale is not None and opt["price"] > prev_wholesale else 0
        opt["retail"] = retail(opt["price"], above)
        prev_wholesale, prev_retail = opt["price"], max(prev_retail, opt["retail"])
    p["retail_price"] = min((o["retail"] for o in p["prices"]), default=None)
data["pricing_rule"] = f"retail = wholesale + ₪{MARKUP_MIN}–{MARKUP_MAX}, ending in 9 (prefer 49/99)"
path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

for p in data["products"]:
    if p["duplicate_of"]:
        continue
    opts = " / ".join(f"{o['label'] or ''} ₪{o['price']}→₪{o['retail']}".strip() for o in p["prices"])
    print(f"{p['id']:>2} | {p['name'][:42]:<42} | {opts}")
