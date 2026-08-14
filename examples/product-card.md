# Example: Product / Price Card Extraction

**Query class:** Product / offer  
**Layer 1 surface:** `web_search` + `x_search` (social slot — product topic)  
**Layer 2 path:** Step 1b `extract_structured.py` → JS slot if price is JS-only

---

## User prompt

> How much does the Notion AI Pro plan cost right now?

---

## Agent execution trace

### Step 1 — Classify and search (layer 1)

Query class: **product / offer** → `web_search` AND `x_search` in the same turn (social rule: product topic + `x_search` exists).

```
web_search(query="Notion AI Pro plan price 2024", num_results=5)
x_search(query="Notion AI Pro pricing", max_results=10)
```

`web_search` results:
- `https://www.notion.so/pricing`
- `https://www.notion.so/blog/notion-ai`
- `https://techcrunch.com/2024/…/notion-ai-pricing/`

`x_search` results: 3 posts from @NotionHQ, 2 user reports.

Dedup: strip `utm_*`. Keep `notion.so/pricing`, `techcrunch.com/…`. Social posts kept separately.

### Step 2 — Read the product card (layer 2, step 1b first)

Price target → start with `scripts/extract_structured.py`, not markdown `web_extract`.

```
terminal(command="python3 scripts/extract_structured.py 'https://www.notion.so/pricing'", timeout=40)
```

Output:

```json
{
  "url": "https://www.notion.so/pricing",
  "html_chars": 183420,
  "title": "Notion – Pricing",
  "json_ld": [
    {
      "@type": "Product",
      "name": "Notion AI",
      "offers": {
        "@type": "Offer",
        "price": "10.00",
        "priceCurrency": "USD",
        "availability": "https://schema.org/InStock"
      }
    }
  ],
  "open_graph": {
    "og:title": "Notion – Simple, powerful, beautiful"
  }
}
```

Structured data returned `price: 10.00 USD` with `InStock`. **Sufficient — stop. Do not call `web_extract`.**

> **Pitfall avoided:** The `web_search` snippet showed "$8/month" — the cheapest tier from a multi-SKU index, not the AI Pro add-on. The JSON-LD on the actual page gave the correct add-on price.

### Step 3 — Cite and answer

Price sourced from the JSON-LD object read at `notion.so/pricing` (layer 2, step 1b). Search snippet not quoted.

---

## Final reply

Notion AI is available as an add-on to any Notion plan for **$10/user/month** (billed monthly), per the structured data on [notion.so/pricing](https://www.notion.so/pricing) as of the time of lookup.

Social posts from @NotionHQ on X confirm the add-on pricing model but do not give a numeric figure — the page source is authoritative.

> **Verification checklist (internal)**  
> - [x] Class: product → `web_search` + `x_search` both ran.  
> - [x] URLs deduped (UTM stripped).  
> - [x] Price: started at step 1b (script), not markdown extract.  
> - [x] Snippet price not quoted as the asked tier.  
> - [x] Claim names a layer-2 URL (the pricing page).
