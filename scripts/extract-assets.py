import re
import json
import base64
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")
IMAGES_DIR = os.path.join(ROOT, "images")
PRODUCTS_JSON = os.path.join(ROOT, "products.json")

with open(INDEX, "r", encoding="utf-8") as f:
    html = f.read()

imgs_match = re.search(r"const IMGS = (\{.*?\});\s*\nconst PRODUCTS", html, re.DOTALL)
if not imgs_match:
    raise SystemExit("IMGS not found")

imgs = json.loads(imgs_match.group(1))
os.makedirs(IMAGES_DIR, exist_ok=True)

key_map = {}
for key, data_uri in imgs.items():
    if not data_uri.startswith("data:"):
        continue
    header, b64 = data_uri.split(",", 1)
    if "jpeg" in header or "jpg" in header:
        ext = "jpg"
    elif "png" in header:
        ext = "png"
    elif "webp" in header:
        ext = "webp"
    else:
        ext = "jpg"
    out = os.path.join(IMAGES_DIR, f"{key}.{ext}")
    with open(out, "wb") as img:
        img.write(base64.b64decode(b64))
    key_map[key] = f"images/{key}.{ext}"
    print(f"Wrote {out}")

products_match = re.search(r"const PRODUCTS = (\[.*?\]);", html, re.DOTALL)
products = json.loads(products_match.group(1))
for product in products:
    product["img"] = key_map.get(product["img"], product["img"])

with open(PRODUCTS_JSON, "w", encoding="utf-8") as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"products.json written with {len(products)} products")
