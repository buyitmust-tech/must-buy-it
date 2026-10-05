# Must Buy It — Shopify theme + store content

- This repo is the **MustBuy** theme (Online Store 2.0, Hebrew, RTL) of the store `8bwvfe-za.myshopify.com`.
- The product page is built from metafields in the `page` namespace — the full workflow for adding a product is in `.claude/skills/add-product/SKILL.md`.
- Each product's content is saved in `products/<handle>.json`.
- Before uploading theme changes, run theme-check (`@shopify/theme-check-node`) and make sure there are 0 errors.
- Theme changes are uploaded to the unpublished theme (writes to the live theme are blocked); the user publishes it themselves in the admin.
- Don't invent social proof (reviews, ratings, viewers, recent purchases) or fake prices.
