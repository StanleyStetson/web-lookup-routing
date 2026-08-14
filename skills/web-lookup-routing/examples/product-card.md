# Example: Product / price card

**Query class:** Product / company / tech / trend  
**Layer 1 surface:** `web_search` + `x_search` (if `x_search` exists)  
**Layer 2 path:** step 1b `extract_structured.py` first

Prices in this file are **illustrative**. Never copy them into a user answer.

---

## User prompt

> How much does the Notion AI add-on cost right now?

---

## Agent execution trace

### Step 1 — Classify and search (layer 1)

Object is a product → `web_search` and `x_search` in the same turn. If `x_search` is missing, say so; do not pretend web results cover social.

```
web_search(query="Notion AI add-on official pricing", limit=5)
x_search(query="Notion AI pricing")
```

`web_search` uses `limit` (not `num_results`). `x_search` takes `query` (no `max_results`).

Dedup: strip `utm_*`. Keep the official pricing URL. Keep X posts on their own ids.

### Step 2 — Read the card (layer 2, step 1b first)

Price target → script first. Markdown `web_extract` strips `<script>` (JSON-LD).

```
terminal(command="python3 scripts/extract_structured.py 'https://www.notion.so/pricing'", timeout=40)
```

Illustrative script shape (values are fake):

```json
{
  "url": "https://www.notion.so/pricing",
  "title": "Notion – Pricing",
  "json_ld": [
    {
      "@type": "Product",
      "name": "Notion AI",
      "offers": {
        "@type": "Offer",
        "price": "<from JSON-LD>",
        "priceCurrency": "USD",
        "availability": "https://schema.org/InStock"
      }
    }
  ],
  "open_graph": {}
}
```

If `name` / `price` / `availability` are present → **stop**. Do not switch vendors.

If JSON-LD is empty and the price is JS-only → JS/bulk slot if that tool exists in **this** session; else `browser_navigate` + `browser_snapshot`. Do not invent an `apify_actor` tool.

**Pitfall:** a search snippet that shows a lower "$N/month" is often the cheapest SKU on a multi-tier page, not the add-on the user named. Quote offer fields from layer 2, or say the field is not in the HTML.

### Step 3 — Cite and answer

Name the pricing URL you opened. Do not quote the snippet price.

---

## Final reply (shape)

Notion AI add-on: **\<price and currency from JSON-LD or from a later cascade step\>** per [notion.so/pricing](https://www.notion.so/pricing), read in layer 2. If social posts only confirm the model and give no number, say that; the page is authoritative.

> **Verification**
> - [x] Product class → `web_search` + `x_search` (or `x_search` named unavailable).
> - [x] Real Hermes params: `limit` on `web_search`; `query` only on `x_search` here.
> - [x] Price started at step 1b. Snippet price not used.
> - [x] No invented tool names.
