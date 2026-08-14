# Example: Fact / News Lookup

**Query class:** News / fact / reference  
**Layer 1 surface:** `web_search`  
**Layer 2 path:** `web_extract` → on-disk cache (if truncated)

---

## User prompt

> What are the main changes in the Python 3.13 release?

---

## Agent execution trace

### Step 1 — Classify and search (layer 1)

Query class: **reference / changelog** → `web_search`, single query in EN (global docs topic).

```
web_search(query="Python 3.13 release notes changes", num_results=5)
```

Results returned:
- `https://docs.python.org/3.13/whatsnew/3.13.html`
- `https://realpython.com/python313-new-features/`
- `https://github.com/python/cpython/releases/tag/v3.13.0`

Dedup: three unique hosts, no duplicates. Proceed.

### Step 2 — Read the best source (layer 2, Branch B)

Primary candidate: official docs URL.

```
web_extract(urls=["https://docs.python.org/3.13/whatsnew/3.13.html"])
```

Result: 14 200 chars, contains "What's New" in the title. **Not a fake success.** Footer says content truncated — cache path returned.

Need the rest of the same page:

```
read_file(path="<path from extract footer>")
```

Enough content retrieved. **Stop — do not call another vendor.**

### Step 3 — Cite and answer

Every listed change names the docs URL opened in layer 2. No claims sourced from search snippets.

---

## Final reply (summary form)

Python 3.13 highlights (source: [docs.python.org/3.13/whatsnew/3.13.html](https://docs.python.org/3.13/whatsnew/3.13.html)):

- **Improved error messages** — more precise `SyntaxError` and `NameError` suggestions.
- **Free-threaded CPython (experimental)** — opt-in build without the GIL (`--disable-gil`).
- **New REPL** — multiline editing, coloured output, history across sessions.
- **`typing.TypeVar` improvements** — PEP 695 type parameter syntax.
- **`copy.replace()`** — generic shallow-replace helper for dataclasses, `datetime`, etc.

> **Verification checklist (internal)**  
> - [x] Class from layer-1 table (reference → `web_search`).  
> - [x] URLs deduped before read.  
> - [x] Read: `web_extract` first; `read_file` cache used for overflow, no vendor switch.  
> - [x] Every claim has a layer-2 URL.  
> - [x] Answer language = user language (EN); query language = EN (global docs).
