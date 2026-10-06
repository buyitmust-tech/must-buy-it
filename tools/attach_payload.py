"""Build a fileUpdate payload that attaches already-uploaded images to products.

usage: python3 tools/attach_payload.py <file_ids.json> <handle>=<productGID> ...
- file_ids.json maps Shopify filename -> {id, w, h}
- main image: the largest roughly-square image (ratio 0.85–1.15); images under
  500px go last; otherwise the source album order is kept.
- alt text: cycles through the product's "alts" list, adding " – תמונה N" on repeats.
"""
import json
import sys

ids = json.load(open(sys.argv[1]))
files = []
for arg in sys.argv[2:]:
    handle, gid = arg.split("=", 1)
    p = json.load(open(f"products/{handle}.json"))
    imgs = [n for n in p["images"] if n in ids]
    missing = [n for n in p["images"] if n not in ids]
    if missing:
        print(f"{handle}: missing {missing}", file=sys.stderr)
    square = [n for n in imgs if 0.85 <= ids[n]["w"] / ids[n]["h"] <= 1.15 and ids[n]["w"] >= 500]
    main = max(square, key=lambda n: ids[n]["w"]) if square else (imgs[0] if imgs else None)
    rest = [n for n in imgs if n != main]
    small = [n for n in rest if ids[n]["w"] < 500]
    order = ([main] if main else []) + [n for n in rest if n not in small] + small
    alts = p["alts"]
    for i, n in enumerate(order):
        alt = alts[i % len(alts)] + (f" – תמונה {i + 1}" if i >= len(alts) else "")
        files.append({"id": ids[n]["id"], "alt": alt, "referencesToAdd": [gid]})
    print(f"{handle}: {len(order)} images, main={main}", file=sys.stderr)
print(json.dumps({"files": files}, ensure_ascii=False))
