---
name: web-lookup-routing
description: "Use when the task needs live web facts, product or company news, pricing, docs, competitor comparison, a changelog, or reading a given URL. Routes lookup by query type, deduplicates sources, then reads pages cheapest-first (native web_extract, then optional fetch/JS/browser). Skip when the user already supplied the text or file, or the task is purely interactive UI with no link discovery."
version: 0.2.0
author: StanleyStetson
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Web, Search, Extract, Routing]
    related_skills: [blocked-page-recovery]
    requires_toolsets: [web]
    requires_tools: [web_search, web_extract]
---

# Web Lookup Routing Skill

Classify the query, search on the matching surface, then read pages cheapest-first. A search snippet, memory note, or challenge page is not the source.

Native `web_search` + `web_extract` are enough. Extra MCP servers fill optional slots. Archives and WAF copies belong to `blocked-page-recovery` when that skill is installed — this file does not restate that ladder.

## When to Use

- Current facts, docs, changelogs, prices, competitors, products, companies, tech, or trends.
- User pasted a URL to read (article, docs, product card).
- User asked for many pages on **one host**.

Do not use for:

- Pure UI (form, click-path, screenshot) with no link discovery — Branch A only.
- Text or files the user already attached.

**Cheap path:** one changelog URL, or a bare fact whose object is not a product, company, technology, or trend. Still run layer 2 fake-success checks. Do not load B2B/marketplace references or layer 2b. "What's new at \<Vendor\>" is **not** cheap.

## Prerequisites

Required: toolset `web` (`web_search`, `web_extract`). Vendor is whatever the user set in `web.search_backend` / `web.extract_backend`.

Optional slots — call only if the tool exists **in this session**. Empty slot: skip and say so when the task needed it. MCP names vary by install prefix; bind to capability, not a copied `mcp_*` string.

| Slot | Use for | Typical presence |
|------|---------|------------------|
| Primary search | News / fact / reference | `web_search` (always, if this skill loaded) |
| Semantic search | B2B / competitors / similar | Exa-style search MCP, if connected |
| Social | Product / company / tech / trend | `x_search`, if the toolset is on |
| JS / bulk | SPA, marketplaces, YouTube, social scrapes | Apify-style browser or actor tools |
| Long fetch | Mid-article cutoff after extract | Exa-style fetch MCP |
| Noisy HTML extract | Last-resort extract, not step 1 | Tavily-style extract MCP |
| Map / crawl | Layer 2b, one host | Tavily-style map/crawl MCP |
| Browser | Branch A, or live DOM after 1–3 failed | `browser_navigate`, `browser_snapshot`, `browser_vision` |

No customer passwords in a cloud browser. No cookies or `Authorization` through a random web proxy.

## How to Run

Step 1b (price / Product / Offer) from this skill directory:

```
terminal(command="python3 scripts/extract_structured.py 'https://example.com/product/123'", timeout=40)
```

Chat gets `name` / `price` / `availability` (and dates if present), not the HTML.

## Quick Reference

| Query class | Layer 1 |
|-------------|---------|
| News / fact / reference | `web_search`. If it fails and a search MCP exists, one reserve call. |
| Deep / B2B / competitors | Semantic slot if present, else `web_search`. |
| Product / company / tech / trend | `web_search` **and** `x_search` in the same turn (social slot). |
| JS / SPA / dynamic | JS/bulk slot first; do not start with markdown extract. |
| Bulk scrape (marketplaces, social, YouTube) | JS/bulk / actor slot, not `web_search`. |

Query language ≠ answer language.

| Topic | Query language |
|-------|----------------|
| Code, API, GitHub, English-only docs, global SaaS | EN |
| Local market, local currency, local law, local firms | That market's language |
| Mixed | Two queries, not one translation |
| `x_search` | Audience language of the topic |

Do not transliterate product names.

## Procedure

### 1. Classify, then search (layer 1)

Use the Quick Reference table. Browser is not layer 1.

**Social rule:** object is a product, company, technology, or trend **and** `x_search` exists → call it with web search, even on a short prompt. Missing tool → say so. A web hit does not replace social.

After more than one source, **dedup before any read**:

- Lowercase host; strip `#`, `utm_*`, `fbclid`, `gclid`.
- `http` ≈ `https`, `www` ≈ bare host.
- Key = host + path (+ meaningful query).
- Dedup X/Twitter posts on their own id.
- Show unique URLs, not a raw dump.

At most **three** search calls, then analyze.

### 2. Read one page (layer 2)

| Task | Start |
|------|--------|
| Interactive (form, click, screenshot, pagination, UI) | Branch A |
| Read (article, docs, visible text, price) | Branch B |

#### Branch A — interactive

`browser_navigate` → `browser_snapshot` → click/type/scroll → `browser_vision` only if a screenshot is required. Fail: `browser_console`, one retry, then tell the user.

#### Branch B — read

Advance only on empty, error, truncate, JS wall, or **fake success**.

**Fake success** (treat as empty even on HTTP 200): interstitial / challenge / "just a moment" / "no connection" / "enable JavaScript" / "attention required"; body that is only nav or cookie banner; extract shorter than ~2k characters with none of the title words from the search hit. Byte size alone is not success. Archive fakes (AMP stub, dead Google Cache) — follow `blocked-page-recovery`.

1. `web_extract` on the URL (configured extract backend).
1a. Footer says truncated + cache path, and you still need more of **this page** → `read_file` that path **before** another extract vendor.
1b. Price or product card: `scripts/extract_structured.py` via `terminal` (markdown extract strips `<script>`). Enough `name` / `price` / `availability` → **stop**. May run in parallel with step 1 on a product URL.
2. Long-fetch slot only if the article is long or step 1 cut off mid-body (`maxCharacters` 10000–15000 when the tool has that param).
3. JS/bulk slot for SPA / bot wall.
4. Browser + `browser_snapshot(full=true)` if 1–3 are empty and the URL should be live.
4b. Catalog / infinite scroll / virtualized table: public JSON / XHR / GraphQL on the **same host** via `terminal`. Not a login bypass. No megabyte dumps in chat.
5. Noisy HTML extract slot — last resort, **different channel from step 1**. Skip ahead of 4 only when step 3 was empty, the task is text-only, and a browser session adds nothing.
6. Live URL blocked (403 / captcha / WAF): `blocked-page-recovery` if installed; else Wayback (`web.archive.org`) or a first-party raw mirror (GitHub raw, registry JSON). Label the copy **archived**. 2FA / account wall → user. After the whole cascade fails: say you did not read the page; offer a user-side screenshot. Do not invent from snippets.

Price/card: 1b beats markdown extract. Catalog/table: 4b. **1b ≠ 4b.**

If one server exposes `search`, `extract`, `map`, and `crawl`, do not mix those verbs.

### 3. One-host section (layer 2b)

Only when the user asked for many pages on one domain. Not a stand-in for 1–3 URLs. Not a digest.

Map, then crawl with a small budget (depth 1–2, tens of pages). Ask before larger limits. Weak on JS → JS/bulk slot. Do not add a crawl vendor without an explicit yes.

### 4. Stop and cite

| Task | Done when |
|------|-----------|
| Fact / changelog | One confirming **read** source |
| Product / "what's new" | Date + primary source + social slot ran or named unavailable |
| Comparison / B2B | Table, or a named gap per competitor |
| Price | Offer fields, or "not in the HTML" |

**Claims:** every number, date, quote, or price in the reply names a URL you opened in layer 2 (or an archive labeled as such). Search snippets and memory notes may pick URLs; they may not supply the fact. Multi-tier marketplace index price is the floor — `references/marketplace-pricing.md`.

B2B: semantic (or `web_search`) → dedup → each official site through layer 2 (prices via 1b) → `references/competitor-analysis.md`.

## Pitfalls

- Markdown extract ≠ HTML. Offers live in JSON-LD / OG (1b).
- Fake success looks like a page. Continue the cascade; do not quote the interstitial.
- Multi-SKU snippet price is usually the cheapest variant, not the named tier.
- Memory and old notes lose to this file.
- Browser does not replace layer 1.
- `web_extract` head+tail + on-disk full text is still step 1a, not a vendor switch.

## Verification

- [ ] Class from the layer-1 table, not the nearest tool.
- [ ] Product / company / tech / trend: `web_search` and `x_search` both ran, or `x_search` named unavailable.
- [ ] URLs deduped before read.
- [ ] Read: `web_extract` first; later slots only on empty / truncate / JS / fake success. Price started at 1b (script).
- [ ] Same-page overflow used `read_file` on the extract cache.
- [ ] Each claim in the reply has a layer-2 URL (archive labeled).
- [ ] Answer language follows the user; query language follows the table.
