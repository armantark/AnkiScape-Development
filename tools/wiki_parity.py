#!/usr/bin/env python3
"""Pin the RuneScape Wiki to its pre-EOC (2012) state and pull parity data.

`runescape.wiki` (weirdgloop) imported the full Fandom edit history, so every
article carries revisions back to ~2005. That means we can view any page exactly
as it read *just before* the Evolution of Combat launched on 2012-11-20 — the
last coherent snapshot of the pre-EOC game — by resolving the newest revision
before that date and reading its wikitext by ``oldid``.

This is the grunt-work tool referenced by the `ankiscape-skill-expansion` skill
(see `wiki-parity-scrape.md`). It exists so agents do not re-derive the same
curl + JSON dance every time they need a number game-main never implemented.

Usage:
    # Resolve the last pre-EOC revision id + timestamp for a page
    python3 tools/wiki_parity.py resolve "Ancient Curses"

    # Print the pre-EOC wikitext of a page (auto-resolves the revid)
    python3 tools/wiki_parity.py content "Ancient Curses"

    # Print only the wikitext sections whose heading/body matches a regex
    python3 tools/wiki_parity.py content "Prayer" --grep "drain|point every"

    # Read a specific revision you already have (skips resolution)
    python3 tools/wiki_parity.py content --revid 6535713

    # Override the cutoff (defaults to EOC, 2012-11-20T00:00:00Z)
    python3 tools/wiki_parity.py resolve "Gilded altar" --before 2011-10-04

The default cutoff is EOC. game-main (2011Scape rev 667, 2011-10-04) stays the
primary source for anything it actually implements; this tool fills gaps for
authentic pre-EOC content the emulator only stubbed. Always cite the returned
``oldid`` in the parity ledger next to any value taken from here.
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://runescape.wiki/api.php"
EOC = "2012-11-20T00:00:00Z"
UA = "AnkiScape-parity-audit/1.0 (personal project; contact chuck67322@berkeley.edu)"


def _get(params):
    params = {**params, "format": "json"}
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def _normalize_cutoff(before):
    """Accept a bare date (2012-11-20) or a full ISO timestamp."""
    if "T" in before:
        return before
    return before + "T23:59:59Z"


def resolve(title, before):
    """Return (revid, timestamp, resolved_title) of the newest rev before cutoff."""
    data = _get({
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvlimit": 1,
        "rvprop": "ids|timestamp",
        "rvstart": _normalize_cutoff(before),
        "rvdir": "older",
        "redirects": 1,
    })
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        if "missing" in page:
            return None
        revs = page.get("revisions")
        if not revs:
            return None
        rev = revs[0]
        return rev["revid"], rev["timestamp"], page["title"]
    return None


def content_by_revid(revid):
    data = _get({
        "action": "query",
        "prop": "revisions",
        "revids": revid,
        "rvprop": "content|timestamp",
    })
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        rev = page["revisions"][0]
        return rev["*"], rev["timestamp"], page["title"]
    return None


def _grep_sections(text, pattern):
    """Keep only wikitext blocks (split on == headings ==) matching pattern."""
    rx = re.compile(pattern, re.IGNORECASE)
    blocks = re.split(r"(?m)^(?==+[^=].*?=+\s*$)", text)
    kept = [b for b in blocks if rx.search(b)]
    return "\n".join(kept) if kept else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("resolve", help="print the pre-EOC revid + timestamp")
    r.add_argument("title")
    r.add_argument("--before", default=EOC)

    c = sub.add_parser("content", help="print pre-EOC wikitext")
    c.add_argument("title", nargs="?")
    c.add_argument("--revid", type=int)
    c.add_argument("--before", default=EOC)
    c.add_argument("--grep", help="only sections matching this regex")

    args = ap.parse_args()

    if args.cmd == "resolve":
        res = resolve(args.title, args.before)
        if not res:
            print(f"NOT FOUND: {args.title!r} before {args.before}", file=sys.stderr)
            sys.exit(1)
        revid, ts, title = res
        print(f"title={title}\nrevid={revid}\ntimestamp={ts}\n"
              f"url=https://runescape.wiki/w/{urllib.parse.quote(title.replace(' ', '_'))}?oldid={revid}")
        return

    if args.cmd == "content":
        if args.revid:
            got = content_by_revid(args.revid)
        elif args.title:
            res = resolve(args.title, args.before)
            if not res:
                print(f"NOT FOUND: {args.title!r} before {args.before}", file=sys.stderr)
                sys.exit(1)
            got = content_by_revid(res[0])
        else:
            print("content needs a title or --revid", file=sys.stderr)
            sys.exit(2)
        if not got:
            print("no content returned", file=sys.stderr)
            sys.exit(1)
        text, ts, title = got
        if args.grep:
            text = _grep_sections(text, args.grep) or f"(no sections matched {args.grep!r})"
        print(f"# {title}  (pre-EOC snapshot {ts})\n")
        print(text)
        return


if __name__ == "__main__":
    main()
