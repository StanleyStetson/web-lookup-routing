# Example: Fact / reference lookup

**Query class:** News / fact / reference  
**Layer 1 surface:** `web_search`  
**Layer 2 path:** `web_extract` → `read_file` on the extract cache if truncated

Numbers and quotes below are **illustrative**. Do not cite them as live facts.

---

## User prompt

> Briefly: who is Hermes in ancient Greek mythology? Use only this page: https://en.wikipedia.org/wiki/Hermes

---

## Agent execution trace

### Step 1 — Classify (layer 1)

Object is a mythological figure, not a product, company, technology, or trend. User already supplied the URL → **cheap path**. No `x_search`. No second search provider.

### Step 2 — Read (layer 2, Branch B)

```
web_extract(urls=["https://en.wikipedia.org/wiki/Hermes"])
```

Native parameter is `urls`. Result is long markdown with the article title in the body — **not a fake success**. Footer says the page was truncated and stored on disk.

Need more of **this same page**:

```
read_file(path="<path from extract footer>")
```

Stop. Do not call a long-fetch MCP, JS slot, or browser.

### Step 3 — Cite and answer

Every biographical claim names the Wikipedia URL opened in layer 2. Search snippets are not used.

---

## Final reply (shape, not a live citation)

Hermes is an Olympian messenger god, also associated with travellers, merchants, and as a psychopomp — per [en.wikipedia.org/wiki/Hermes](https://en.wikipedia.org/wiki/Hermes) as read in layer 2.

> **Verification**
> - [x] Class: bare fact / given URL → cheap path, no `x_search`.
> - [x] Read: `web_extract` first; overflow via `read_file` on the extract cache.
> - [x] No invented tools; `web_search` unused because the URL was given.
> - [x] Each claim has a layer-2 URL.
