# Example: B2B Competitor Comparison

**Query class:** Deep / B2B / competitors  
**Layer 1 surface:** Semantic slot (Exa-style) if present, else `web_search`  
**Layer 2 path:** Each official site through full cascade; prices via step 1b

---

## User prompt

> Compare Linear, Jira, and Height as project management tools for a 20-person engineering team.

---

## Agent execution trace

### Step 1 — Classify and search (layer 1)

Query class: **deep / B2B / competitors** → semantic slot first (present in session); `web_search` as fallback if empty.

```
exa_search(query="Linear vs Jira vs Height project management engineering teams comparison", num_results=8)
```

Results: mix of review aggregators and official pages.

Dedup before reading:
- Drop `g2.com`, `capterra.com`, `getapp.com` (aggregators / "best of" listicles per `references/competitor-analysis.md`).
- Keep: `linear.app`, `atlassian.com/software/jira`, `height.app`.

Three unique official domains. Proceed.

### Step 2 — Read each official site (layer 2)

Read each competitor through the full cascade. Prices start at step 1b.

**Linear:**
```
web_extract(urls=["https://linear.app/pricing"])
terminal(command="python3 scripts/extract_structured.py 'https://linear.app/pricing'", timeout=40)
```
→ Markdown extract: positioning and features. Script: `{"price": "8.00", "priceCurrency": "USD"}` per seat/month.

**Jira:**
```
web_extract(urls=["https://www.atlassian.com/software/jira/pricing"])
terminal(command="python3 scripts/extract_structured.py 'https://www.atlassian.com/software/jira/pricing'", timeout=40)
```
→ Script returns empty `json_ld` (price rendered in JS). Advance to JS slot:
```
apify_actor(actor="apify/web-scraper", url="https://www.atlassian.com/software/jira/pricing")
```
→ Price: $8.15/user/month (Standard, up to 35 000 users).

**Height:**
```
web_extract(urls=["https://height.app/pricing"])
terminal(command="python3 scripts/extract_structured.py 'https://height.app/pricing'", timeout=40)
```
→ Markdown extract: sufficient. Script: no JSON-LD price found. Price visible in extract text: $8.50/member/month (Business).

### Step 3 — Fill the competitor table (references/competitor-analysis.md template)

| Field | Linear | Jira | Height |
|---|---|---|---|
| **Positioning** | Speed-first issue tracker for eng teams | Enterprise-grade, fully customisable PM | Async-first, AI-native PM |
| **Price** | $8/seat/mo (Business) | $8.15/user/mo (Standard) | $8.50/member/mo (Business) |
| **Key features** | Cycles, triage, git sync, roadmaps | Epics, sprints, 3 000+ integrations, Confluence | Tasks, chat, docs in one surface; AI summaries |
| **Integrations** | GitHub, GitLab, Figma, Slack | 3 000+ via Marketplace | GitHub, Slack, Figma, Zapier |
| **Audience** | Eng-focused startups and scale-ups | Enterprises, large cross-functional teams | Remote async teams, early-stage startups |
| **Strengths** | Speed, UX, keyboard-first | Breadth, compliance, reporting | Unified surface, AI-native |
| **Gaps** | Light on non-eng PM features | Steep learning curve, slower UX | Smaller integration ecosystem |

**Synthesis (from filled cells only):**
- **Linear** wins on UX and velocity for pure engineering work.
- **Jira** wins on compliance, reporting depth, and org-wide adoption in enterprises.
- **Height** wins for teams that want chat + tasks + docs in one place with AI summaries.
- For a 20-person eng team without enterprise compliance needs, **Linear** or **Height** present the lowest friction.

---

> **Verification checklist (internal)**  
> - [x] Class: deep B2B → semantic slot ran first.  
> - [x] Aggregators / "best of" listicles dropped.  
> - [x] Dedup before read.  
> - [x] Each official site read through layer 2; prices via step 1b.  
> - [x] Gaps listed as explicit blanks (none needed here — all cells filled from actual reads).  
> - [x] Synthesis only from filled cells.
