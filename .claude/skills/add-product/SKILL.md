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
   - `descriptionHtml`: only 2–3 short opening paragraphs (the rest lives in the metafields — don't duplicate it).
   - Bundles: one option named "כמות" ("Quantity") with values like `ערכה אחת` / `2 ערכות – חוסכים ₪49` (the text after the `–` shows up as a green savings tag).
     `compareAtPrice` for a bundle = unit price × quantity (only a real price, never an inflated one).
   - Images: the first is the main image; after it come usage, close-up, and before/after images. Write a Hebrew alt text for each.
4. **Fill the metafields** with `metafieldsSet` (see the table). JSON fields are passed as a JSON string.
5. **Add to a collection** (`add-to-collection`) — at least the relevant collection, and the homepage collection if it's a bestseller.
6. **Check**: query the product back with `graphql_query` and confirm every field was saved. Give the user the link to the product page (`https://8bwvfe-za.myshopify.com/products/<handle>`; with an unpublished theme, add `?preview_theme_id=<id>`).

## Fields (namespace `page`)

| key | type | what it shows | rule |
|---|---|---|---|
| `hook` | single_line_text_field | Sentence below the title | Benefit + pain, up to ~12 words. "Lift the sofa yourself in 10 seconds" |
| `badge` | single_line_text_field | Red tag above the title | Only if true: "🔥 רב מכר" ("Bestseller") only for a product that actually sells |
| `benefits` | list.single_line_text_field | ✓ lines next to the button | 3–5 lines, each up to ~8 words, result-focused |
| `features` | json | Benefit rows with images | `[{"icon":"💪","title":"…","text":"…","media":2}]` 3–6 items. `media` = the product image number (1-based) to show next to the row; leave it out if there's no matching image |
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
