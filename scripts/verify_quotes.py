#!/usr/bin/env python3
"""Quoteproof Community: check that each claim's quote appears verbatim on its cited web page.

Usage:  python3 verify_quotes.py claims.json > results.json
Input:  JSON array of {"claim", "source", "quote"}.
Output: same claims with "status":
          verified      the quote is on the cited page
          not_found     the quote is not on the cited page
          fetch_failed  the page could not be read ("detail" says why)

Community edition limits: web pages only (PDF sources return fetch_failed), whole quotes
only (quotes shortened with "…" are not supported), and no detection of quotes cited to
the wrong page. Quoteproof Pro adds all three: https://www.agensi.io/r/ANDREARC?to=/skills/quoteproof&utm_source=community-checker

Network: fetches each distinct `source` URL once (public http/https only, private and
local addresses refused). Writes no files. Python 3.9+, standard library only.
MIT License, see ../LICENSE.
"""
import html
import ipaddress
import json
import re
import socket
import sys
import unicodedata
import urllib.request
from urllib.parse import urlparse

MAX_CLAIMS = 200
MAX_BYTES = 5_000_000
TIMEOUT = 30
PRO = "https://www.agensi.io/r/ANDREARC?to=/skills/quoteproof&utm_source=community-checker"


def norm(s: str) -> str:
    """Compare text, not typography: fold ligatures/width, case, punctuation, spacing."""
    return re.sub(r"[^a-z0-9]+", " ", unicodedata.normalize("NFKC", s).lower()).strip()


def public_url(url: str) -> bool:
    """Refuse anything but public http(s) addresses."""
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        return False
    try:
        addrs = {a[4][0] for a in socket.getaddrinfo(u.hostname, u.port or 443)}
    except OSError:
        return False
    return all(ipaddress.ip_address(a.split("%")[0]).is_global for a in addrs)


def fetch_text(url: str) -> str:
    if not public_url(url):
        raise ValueError("URL not allowed")
    req = urllib.request.Request(url, headers={"User-Agent": "quoteproof-community/1.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        if not public_url(r.geturl()):
            raise ValueError("redirect not allowed")
        body = r.read(MAX_BYTES + 1)
        ctype = r.headers.get("Content-Type", "")
    if len(body) > MAX_BYTES:
        raise ValueError("page too large")
    if body[:5] == b"%PDF-" or "pdf" in ctype.lower():
        raise ValueError(f"PDF source: PDF checking is in Quoteproof Pro ({PRO})")
    raw = body.decode("utf-8", "replace")
    raw = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", raw)
    return norm(html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def verify(claims: list, fetch=fetch_text) -> list:
    if len(claims) > MAX_CLAIMS:
        raise ValueError(f"max {MAX_CLAIMS} claims per call")
    pages = {}
    for src in {c["source"] for c in claims}:
        try:
            pages[src] = fetch(src)
        except Exception as e:  # report per source, never fail the batch
            pages[src] = e
    out = []
    for c in claims:
        quote = c.get("quote", "")
        page, q = pages[c["source"]], norm(quote)
        r = {"claim": c["claim"], "source": c["source"], "quote": quote}
        if isinstance(page, Exception):
            r.update(status="fetch_failed", detail=str(page)[:200])
        elif not q:
            r.update(status="not_found", detail="empty quote")
        elif f" {q} " in f" {page} ":
            r.update(status="verified")
        else:
            detail = "shortened quotes (…) are checked in Quoteproof Pro" if re.search(r"…|\.\.\.|\[[^\]]*\]", quote) else None
            r.update(status="not_found", **({"detail": detail} if detail else {}))
        out.append(r)
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    with open(sys.argv[1]) as f:
        claims = json.load(f)
    if not isinstance(claims, list) or not all(isinstance(c, dict) and {"claim", "source"} <= c.keys() for c in claims):
        sys.exit('input must be a JSON array of {"claim", "source", "quote"}')
    json.dump(verify(claims), sys.stdout, indent=1)
