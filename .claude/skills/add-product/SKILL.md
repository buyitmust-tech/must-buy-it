---
name: add-product
description: Add a new product (or redesign an existing one) in the Must Buy It store with a high-converting product page. Use whenever the user brings a product — a link, photos, a name, or a description — and wants it on the site.
---

# Adding a product with a converting product page

The theme (MustBuy) builds the product page automatically from **metafields in the `page` namespace**.
Each section is hidden when its field is empty, so every product gets a full, consistent landing page just by filling in its fields.
You don't need to touch the theme code for a new product.

## The workflow

1. **Gather the input** from the user: name, what it does, price (and a bundle price if there is one), images (public HTTPS URLs), what's in the box, technical details, and a supplier link if there is one.
   Whatever is missing and needed for the price or specs — **ask**. Don't invent prices, dimensions, materials, or load capacity.
2. **Write the copy** following the rules below, and save it as `products/<handle>.json` in the repo (the source of truth + a backup).
3. **Create or update the product** in Shopify (`create-product` / `update-product`):
   - A clear title in Hebrew: `<brand/name> – <what it does>`.
   - **SEO** (required for every product):
     - `handle` short in English with dashes (`over-sink-dish-rack`). Hebrew in the URL turns into %D7… when shared.
       When changing the handle of an existing product: `productUpdate` with `redirectNewHandle: true`, so the old address redirects.
     - `seo.title` up to 60 characters: the main search phrase in Hebrew first, then ` | Must Buy It`.
     - `seo.description` up to 155 characters: what it is + 2–3 benefits, with the search phrase.
     - `tags`: 2–4 topic tags in Hebrew; `productType` = the category (מטבח / טיפוח ויופי / תינוקות / אחסון וסידור — kitchen / grooming & beauty / babies / storage & organizing).
     - Image alt: a **different** description for each image, around the search phrase (not the same text 12 times).
   - `tools/product_payload.py products/<handle>.json` builds the `productSet` input (including handle, seo, tags) from the file.
   - `tools/attach_payload.py <file_ids.json> <handle>=<productGID> ...` builds `fileUpdate` for the images: a square, high-quality main image, small images last, and a different alt for each image (from the product file's `alts` list).
   - `descriptionHtml`: only 2–3 short opening paragraphs (the rest lives in the metafields — don't duplicate it).
   - Bundles: one option named "כמות" ("Quantity") with values like `ערכה אחת` / `2 ערכות – חוסכים ₪49` (the text after the `–` shows up as a green savings tag).
     `compareAtPrice` for a bundle = unit price × quantity (only a real price, never an inflated one).
   - Images: the first is the main image; after it come usage, close-up, and before/after images. Write a Hebrew alt text for each.
     If the images are already in Content → Files (e.g., from the Telegram import), **don't** upload them again: find them with `files(query: "filename:<name>")`
     (Shopify replaces `@` in the name with `_`) and attach them with `fileUpdate` + `referencesToAdd: [productId]`, in the order you want.
   - The images on cdn.shopify.com are not reachable from this environment, so you can't see their content. Keep the source order and tell the user they can drag the main image in the admin.
4. **Fill the metafields** with `metafieldsSet` (see the table). JSON fields are passed as a JSON string.
5. **Publish to the online store**: `publishablePublish` with the "חנות מקוונת" ("Online Store") publication (`publications` query). Without this the product is ACTIVE but has no page.
6. **Add to a collection** (`add-to-collection`) — at least the relevant collection, and the homepage collection if it's a bestseller.
7. **Check**: query the product back with `graphql_query` and confirm every field was saved. Give the user the link to the product page (`https://8bwvfe-za.myshopify.com/products/<handle>`; with an unpublished theme, add `?preview_theme_id=<id>`).

## Displaying prices
The store's currency format is `{{amount}} NIS`. The theme displays prices through `snippets/money.liquid` (`{% render 'money', cents: X %}` → ₪249).
**Don't use** `| money` in theme code; it will show "249.00 NIS".

## Theme changes
The MustBuy theme is live (MAIN), and writes to the live theme are blocked.
**Watch out:** the user (or an app) can edit the live theme directly; for example, a ChatMaxima widget was added to `layout/theme.liquid`. Before uploading a file, compare its size/content against the live theme and merge their changes; don't overwrite them.
**Watch out 2:** `themeFilesUpsert` with `body.type: URL` runs in the background and **fails silently** on a Liquid error. After every upload, check the file size in the theme (or upload with `TEXT`, which returns errors immediately).
Shopify's Liquid doesn't allow a `}` character inside a string inside `{{ }}` (e.g. `'?q={x}'`); use `capture` with plain text instead. For a theme change: `themeDuplicate` the live theme → check that `templates/*.json` and `config/settings_data.json` in the copy weren't changed by the user in the editor (don't erase their changes) → `themeFilesUpsert` to the copy → the user publishes it.

## Fields (namespace `page`)

| key | type | what it shows | rule |
|---|---|---|---|
| `hook` | single_line_text_field | Sentence below the title | Benefit + pain, up to ~12 words. "Lift the sofa yourself in 10 seconds" |
| `badge` | single_line_text_field | Red tag above the title | Only if true: "🔥 רב מכר" ("Bestseller") only for a product that actually sells |
| `benefits` | list.single_line_text_field | ✓ lines next to the button | 3–5 lines, each up to ~8 words, result-focused |
| `features` | json | Benefit rows with images | `[{"icon":"💪","title":"…","text":"…","media":2}]` 3–6 items. `media` = the product image number (1-based) to show next to the row; leave it out if there's no matching image בפועל: שימו `media` ב-2 הפיצ׳רים הראשונים (למשל 2 ו-3) כדי שיוצגו כשורות תמונה+טקסט; השאר יוצגו ככרטיסים, והגלריה בהמשך הדף מדלגת על התמונות שכבר הוצגו |
| `features_heading` | single_line_text_field | Benefits section heading | Optional |
| `steps` | json | "How it works" | `[{"title":"מרימים","text":"…"}]` ("Lift") 3 steps (up to 4) |
| `steps_heading` | single_line_text_field | Heading | Optional |
| `comparison` | json | Comparison table | `{"heading":"…","us":"שם המוצר","them":"החלופה","rows":[{"feature":"…","us":true,"them":false}]}` — compare against **the alternative** (doing it by hand / a regular product), not against a named competitor |
| `suitable_for` | list.single_line_text_field | Chips for "Suitable for" | 4–10 short items |
| `suitable_note` | single_line_text_field | Sentence below the chips | Optional |
| `in_box` | list.single_line_text_field | "What's in the box" | Exactly what arrives |
| `specs` | json | Technical specs | `[{"label":"משקל","value":"1.2 ק״ג"}]` ("Weight", "1.2 kg") — **real data only** |
| `faq` | json | Product FAQ | `[{"q":"…","a":"…"}]` 3–6 objection-handling questions (does it work on X, does it damage, is assembly required) |
| `offer_note` | single_line_text_field | Note below the button | A real offer only (e.g., bundle savings) |
| `popular_variant` | number_integer | Marks a bundle as "⭐ הכי משתלם" ("⭐ Best value") | The variant number (1-based), usually 2 |
| `closing_cta` | single_line_text_field | Big heading at the bottom of the page | "Ready to stop hauling?" |

## Copywriting rules (Hebrew)

- Speak to the customer in plural/neutral form ("מזיזים", "תקבלו" — "you move", "you'll get"), short sentences, without heavy marketing jargon.
- Structure: pain → solution → how → proof → objections → call to action.
- Every claim needs to be true about the product. **Never** invent: reviews, ratings, number of customers, sales numbers, "X people are viewing", scarcity, timers, certifications, or medical claims.
- No inflated "before discount" prices. A strikethrough price is only a real price (or unit price × quantity in a bundle).
- Emojis in moderation: one per line at most, mainly in `icon` and `benefits`.

## Example

`products/movemate-pro.json` — a complete example to copy the format from.
