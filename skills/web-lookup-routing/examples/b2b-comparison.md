# Example: B2B competitor comparison

**Query class:** Deep / B2B / competitors  
**Layer 1 surface:** semantic search MCP **if present**, else `web_search`  
**Layer 2 path:** each official site through the cascade; prices via step 1b

Table cells below are **illustrative**. Do not treat them as current vendor prices.

---

## User prompt

> Compare Linear, Jira, and Height as project management tools for a 20-person engineering team.

---

## Agent execution trace

### Step 1 — Classify and search (layer 1)

Deep / B2B → if a semantic search MCP exists in this session, use that tool (name varies by MCP prefix — do not hard-code `exa_search`). If the slot is empty:

```
web_search(query="Linear Jira Height project management official sites", limit=8)
```

Drop aggregator / "best of" listicles (`g2.com`, `capterra.com`, …) per `references/competitor-analysis.md`. Keep official product hosts. Dedup before any read.

### Step 2 — Read each official site (layer 2)

For each pricing URL:

```
web_extract(urls=["https://linear.app/pricing"])
terminal(command="python3 scripts/extract_structured.py 'https://linear.app/pricing'", timeout=40)
```

- JSON-LD / OG has offer fields → stop for that competitor's price.
- Script empty, price is JS-only → JS/bulk slot **if that tool exists** (Apify-style browser or `search_actors` + `call_actor`). Otherwise:

```
browser_navigate(url="https://www.atlassian.com/software/jira/pricing")
browser_snapshot()
```

Do not call a made-up `apify_actor` / `exa_search` name.

### Step 3 — Table (`references/competitor-analysis.md`)

Fill only from layer-2 reads. Leave a cell blank if that site did not yield the field.

| Field | Linear | Jira | Height |
|-------|--------|------|--------|
| Positioning | \<from official home/pricing\> | … | … |
| Price | \<1b or later step, or blank\> | … | … |
| Key features | … | … | … |
| Integrations | … | … | … |
| Audience | … | … | … |
| Strengths | … | … | … |
| Gaps | … | … | … |

Synthesis only from filled cells. No invented prices.

---

> **Verification**
> - [x] B2B class → semantic MCP or `web_search`, not a fictional `exa_search`.
> - [x] Aggregators dropped; URLs deduped.
> - [x] Prices via 1b first; JS/browser only if 1b empty.
> - [x] Native tools only (`web_search`, `web_extract`, `terminal`, `browser_*`) plus optional slots that exist in-session.
