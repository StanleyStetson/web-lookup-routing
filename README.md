# web-lookup-routing

A [Hermes Agent](https://hermes-agent.nousresearch.com) skill that classifies a query by type and routes it through web search, extraction, and browser layers in the correct cheapest-first order.

## Install

```bash
# Add this repo as a tap (one-time setup)
hermes skills tap add StanleyStetson/web-lookup-routing

# Install the skill
hermes skills install StanleyStetson/web-lookup-routing/web-lookup-routing
```

Or install directly without adding the tap:

```bash
hermes skills install StanleyStetson/web-lookup-routing/skills/web-lookup-routing
```

## What it does

Instead of blindly calling `web_search` + `web_extract` on every query, this skill:

1. **Classifies** the query into one of five classes (news/fact, deep B2B, product/company/trend, JS/SPA, bulk scrape).
2. **Routes layer 1** to the right search surface — primary search, semantic slot, social (`x_search`), or JS/bulk actor.
3. **Deduplicates** results before any page read (strips UTM params, normalises http/https and www).
4. **Reads pages cheapest-first (layer 2)**: `web_extract` → on-disk cache → long-fetch MCP → JS slot → browser → noisy-HTML slot — advancing only on empty, truncated, JS wall, or fake-success responses.
5. **Extracts structured data** (JSON-LD / Open Graph) for product/price cards via the bundled `scripts/extract_structured.py` — no third-party dependencies, stdlib only.
6. **Cites every claim** to a URL that was actually opened in layer 2, not a search snippet.

Blocked or archived pages are delegated to Hermes' bundled [`blocked-page-recovery`](https://github.com/NousResearch/hermes-agent/tree/main/skills/research/blocked-page-recovery) skill when it is installed.

## Requirements

| Dependency | Type | Notes |
|---|---|---|
| `web_search` | **Required** | Configured via `web.search_backend` |
| `web_extract` | **Required** | Configured via `web.extract_backend` |
| Exa-style search / fetch MCP | Optional | Deep / B2B / semantic queries; long article fetch |
| `x_search` | Optional | Product, company, tech, and trend queries |
| Apify-style browser / actor tools | Optional | JS SPAs, marketplaces, YouTube, social scrapes |
| Tavily-style extract / map / crawl MCP | Optional | Last-resort HTML extract; one-host crawls |
| `browser_navigate`, `browser_snapshot`, `browser_vision` | Optional | Interactive tasks; fallback after cascade |
| Python 3.9+ | Required for `extract_structured.py` | stdlib only, no pip install |

## Slot overlay

Copy `references/slot-overlay.example.md` next to your local install and fill in your vendor names. **Never put API keys in that file.** The published `SKILL.md` stays slot-based so it works with any compatible toolset.

## Files

```
web-lookup-routing/              ← GitHub tap repo root
├── README.md
├── LICENSE
└── skills/
    └── web-lookup-routing/      ← skill slug (install target)
        ├── SKILL.md             # Main skill — routing logic and cascade
        ├── scripts/
        │   └── extract_structured.py  # JSON-LD + Open Graph extractor (stdlib only)
        ├── references/
        │   ├── marketplace-pricing.md    # Class-of-error: multi-tier snippet price traps
        │   ├── competitor-analysis.md    # B2B competitor table template
        │   ├── page-reading.md           # Concrete code examples for every cascade step
        │   └── slot-overlay.example.md   # Local vendor-name override template
        └── examples/
            ├── fact-lookup.md            # Bare fact / reference read
            ├── product-card.md           # Structured product/price extraction
            └── b2b-comparison.md         # Competitor comparison table
```

## License

MIT © StanleyStetson
