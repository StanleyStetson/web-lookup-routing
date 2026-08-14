# Marketplace pricing — class of error

Search snippets and markdown extracts on multi-tier digital marketplaces often show the **minimum / starting price**, not the SKU the user named.

## Pattern

- Title lists several tiers (`PLUS | PRO | GO`).
- Indexed price is the cheapest tier.
- Real price sits behind a JS selector or a different listing.

## What to do

1. If the title has more than one tier, do not quote the snippet price as the asked tier.
2. Prefer a listing whose title is only the asked tier.
3. Read the card through layer 2 step **1b** (JSON-LD / OG). If the price is JS-only, use the JS/browser slot — do not stop at `web_extract`.
4. Say “from …” only when you mean a floor, and name the tier it belongs to.

This file is the class rule. It does not contain live price tables; those go stale.
