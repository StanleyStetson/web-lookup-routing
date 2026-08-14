# Page-reading examples

Cascade **rules** live only in `SKILL.md` layer 2.

## Short article

```
web_extract(urls=["https://example.com/news"])
```

Truncated + cache footer, need the middle of the **same** page:

```
read_file(path="<path from extract footer>")
```

## Product card (step 1b)

```
terminal(command="python3 scripts/extract_structured.py 'https://example.com/product/123'", timeout=40)
```

Reply with name / price / availability only. Enough fields → stop.

## Long article after a mid-body cut

Long-fetch MCP if that slot exists (`maxCharacters` 10000–15000). Else stay on `read_file` of the extract cache.

## Interactive

```
browser_navigate(url="https://example.com/form")
browser_snapshot()
```

## Catalog API (4b)

Same host, public JSON or GraphQL. Filter in Python. Not a login bypass.

## Blocked live URL (step 6)

`blocked-page-recovery` if installed. Else `web_extract` on a Wayback URL, cite as archived.
