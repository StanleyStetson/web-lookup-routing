#!/usr/bin/env python3
"""Pull JSON-LD and Open Graph fields from a live HTML page (layer 2 step 1b).

Stdlib only. Prints compact JSON to stdout. Not a login bypass.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional

_LD_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.I | re.S,
)


class _OgParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.og: Dict[str, str] = {}
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        if tag != "meta":
            if tag == "title":
                self._in_title = True
            return
        props = {k.lower(): (v or "") for k, v in attrs}
        key = props.get("property") or props.get("name") or ""
        content = props.get("content") or ""
        if key.startswith("og:") or key.startswith("product:"):
            if key not in self.og:
                self.og[key] = content

    def handle_data(self, data: str) -> None:
        if self._in_title and not self.title:
            self.title = data.strip()

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False


def _fetch(url: str, timeout: float) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; HermesSkill/web-lookup-routing)",
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read(2_000_000)
        ctype = resp.headers.get("Content-Type", "")
        charset = "utf-8"
        if "charset=" in ctype.lower():
            charset = ctype.split("charset=", 1)[1].split(";")[0].strip() or charset
        return raw.decode(charset, errors="replace")


def _load_ld(blob: str) -> Optional[Any]:
    blob = blob.strip()
    if not blob:
        return None
    try:
        return json.loads(blob)
    except json.JSONDecodeError:
        return None


def _walk(node: Any, acc: List[dict]) -> None:
    if isinstance(node, list):
        for item in node:
            _walk(item, acc)
        return
    if isinstance(node, dict):
        acc.append(node)
        for key in ("@graph", "hasVariant", "offers", "itemOffered"):
            if key in node:
                _walk(node[key], acc)


def _pick_fields(blocks: List[dict]) -> List[dict]:
    out: List[dict] = []
    for block in blocks:
        types = block.get("@type", "")
        if isinstance(types, list):
            type_l = " ".join(str(t) for t in types).lower()
        else:
            type_l = str(types).lower()
        interesting = (
            "product" in type_l
            or "offer" in type_l
            or "organization" in type_l
            or "article" in type_l
            or any(k in block for k in ("offers", "price", "priceCurrency", "availability"))
        )
        if not interesting:
            continue
        slim = {
            k: block.get(k)
            for k in (
                "@type",
                "name",
                "brand",
                "sku",
                "price",
                "priceCurrency",
                "lowPrice",
                "highPrice",
                "availability",
                "url",
                "datePublished",
                "dateModified",
            )
            if block.get(k) is not None
        }
        offers = block.get("offers")
        if isinstance(offers, dict):
            slim["offers"] = {
                k: offers.get(k)
                for k in ("@type", "price", "priceCurrency", "availability", "url")
                if offers.get(k) is not None
            }
        elif isinstance(offers, list) and offers:
            first = offers[0] if isinstance(offers[0], dict) else {}
            slim["offers"] = {
                k: first.get(k)
                for k in ("@type", "price", "priceCurrency", "availability", "url")
                if first.get(k) is not None
            }
        if slim:
            out.append(slim)
    return out


def extract(url: str, timeout: float) -> dict:
    html = _fetch(url, timeout=timeout)
    ld_raw = []
    for match in _LD_RE.finditer(html):
        parsed = _load_ld(match.group(1))
        if parsed is not None:
            ld_raw.append(parsed)
    blocks: List[dict] = []
    for node in ld_raw:
        _walk(node, blocks)
    og_parser = _OgParser()
    try:
        og_parser.feed(html)
    except Exception:
        pass
    return {
        "url": url,
        "html_chars": len(html),
        "title": og_parser.title or og_parser.og.get("og:title", ""),
        "json_ld": _pick_fields(blocks),
        "open_graph": og_parser.og,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="http(s) page to read")
    parser.add_argument("--timeout", type=float, default=25.0)
    args = parser.parse_args()
    if not args.url.startswith(("http://", "https://")):
        print("url must be http(s)", file=sys.stderr)
        return 2
    try:
        payload = extract(args.url, timeout=args.timeout)
    except urllib.error.HTTPError as exc:
        print(json.dumps({"url": args.url, "error": f"HTTP {exc.code}"}, ensure_ascii=False))
        return 1
    except Exception as exc:  # noqa: BLE001 — CLI boundary
        print(json.dumps({"url": args.url, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
