"""Build the Shopify productSet input from products/<handle>.json.

usage: python3 tools/product_payload.py products/a.json [products/b.json ...]
prints {"p1": ProductSetInput, "p2": ...} for a productSet mutation with aliases.
"""
import json
import sys

TYPES = {
    "hook": "single_line_text_field", "badge": "single_line_text_field",
    "benefits": "list.single_line_text_field", "features_heading": "single_line_text_field",
    "features": "json", "steps_heading": "single_line_text_field", "steps": "json",
    "comparison": "json", "suitable_for": "list.single_line_text_field",
    "suitable_note": "single_line_text_field", "in_box": "list.single_line_text_field",
    "specs": "json", "faq": "json", "offer_note": "single_line_text_field",
    "popular_variant": "number_integer", "closing_cta": "single_line_text_field",
}


def metafields(d):
    out = []
    for key, v in d.items():
        value = v if isinstance(v, str) else str(v) if isinstance(v, int) else json.dumps(v, ensure_ascii=False)
        out.append({"namespace": "page", "key": key, "type": TYPES[key], "value": value})
    return out


def product_input(p):
    if "option_name" in p:
        name = p["option_name"]
        options = [{"name": name, "position": 1, "values": [{"name": v["option"]} for v in p["variants"]]}]
        variants = [{"optionValues": [{"optionName": name, "name": v["option"]}], "price": v["price"]} for v in p["variants"]]
    else:
        options = [{"name": "Title", "position": 1, "values": [{"name": "Default Title"}]}]
        variants = [{"optionValues": [{"optionName": "Title", "name": "Default Title"}], "price": p["variants"][0]["price"]}]
    out = {
        "title": p["title"], "descriptionHtml": p["description_html"], "productType": p["product_type"],
        "vendor": "Must Buy It", "status": "ACTIVE", "productOptions": options, "variants": variants,
        "metafields": metafields(p["metafields"]),
    }
    if p.get("handle"):
        out["handle"] = p["handle"]
    if p.get("seo"):
        out["seo"] = p["seo"]
    if p.get("tags"):
        out["tags"] = p["tags"]
    return out


if __name__ == "__main__":
    payload = {f"p{i}": product_input(json.load(open(f))) for i, f in enumerate(sys.argv[1:], 1)}
    print(json.dumps(payload, ensure_ascii=False))
