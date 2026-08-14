# Personal slot overlay (do not publish with secrets)

Copy this next to your local install if you want named vendors without forking the hub skill. The published `SKILL.md` stays slot-based.

```
primary search:     web_search   (backend: <search_backend>)
extract step 1:     web_extract  (backend: <extract_backend>)
semantic search:    <exa MCP or empty>
social:             x_search or empty
JS / bulk:          <apify tools or empty>
long fetch:         <exa fetch or empty>
noisy HTML extract: <tavily extract or empty>
map / crawl:        <tavily map/crawl or empty>
browser:            browser_* if the toolset is on
```

Fill from `hermes tools` / MCP list. Never put API keys in this file.
