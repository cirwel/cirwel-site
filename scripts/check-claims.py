#!/usr/bin/env python3
"""Verify every cited claim on cirwel.org still exists in the source it cites.

Written 2026-08-26. The page carried "0 of 7 streams beat a last-value
persistence baseline at predicting negative task outcomes" for 14 days, with a
link to a document that contains zero occurrences of "0/7", "0 of 7", or even
the word "persistence". The citation was right there and pointed at the wrong
place. A substring assertion would have caught it the day it shipped.

Checks the LIVE site against the LIVE sources, not the working tree, because
what is published is the thing that can be wrong.

Three checks per run:

1. Each claim's source still contains every string the claim rests on. The
   claim NAME is asserted alongside the figure -- pinning the document alone is
   what let a figure be borrowed from one claim and published as another.
2. Each retired phrasing is absent from the site. A correction that gets
   re-asserted by a later session is the failure mode this file exists for.
3. Each claim is still on the page it says it is. A manifest entry for copy
   that no longer exists is stale, not a defect -- reported as WARN.

Report-only by design. Exit 1 on drift, 2 on UNKNOWN. Never exits 0 because a
fetch failed: an instrument that fails toward "healthy" is worse than none.

    scripts/check-claims.py                # check the live site
    scripts/check-claims.py --manifest P   # alternate manifest
    scripts/check-claims.py --self-test    # negative control, no network
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import subprocess
import sys

TIMEOUT = 20
UA = "cirwel-site-claims-check/1 (+https://cirwel.org)"

RED = "\033[31m"
YEL = "\033[33m"
GRN = "\033[32m"
DIM = "\033[2m"
OFF = "\033[0m"


def fetch(url: str) -> str:
    """Fetch via curl, not urllib.

    Deliberate: the python.org build this runs under ships no CA bundle
    (`ssl.get_default_verify_paths().cafile` is None), so urllib raises
    CERTIFICATE_VERIFY_FAILED on every https URL and the whole run degrades to
    UNKNOWN. curl uses the system trust store and is guaranteed present, which
    also keeps this job independent of whichever python3 launchd resolves.
    """
    out = subprocess.run(
        ["curl", "--fail", "--silent", "--show-error", "--location",
         "--max-time", str(TIMEOUT), "--user-agent", UA, url],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise RuntimeError((out.stderr.strip() or f"curl exit {out.returncode}"))
    return out.stdout


def page_text(raw: str) -> str:
    """Rendered HTML to normalized visible text.

    Whitespace is collapsed because the source wraps prose at ~70 columns; a
    claim that spans a line break must still match as one string.
    """
    raw = re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)
    return flatten(html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def flatten(text: str) -> str:
    """Collapse whitespace so a match can straddle a line break.

    Load-bearing for the markdown sources too, not just HTML: the contract
    wraps at ~80 columns, so an assertion like "BENCHMARK FAIL for the
    cold-start reconstruction; UNIDENTIFIED for the warmed deployed EMA" sits
    across two lines in the file. Matching raw text reported that as DRIFT on
    the first live run -- a false positive, and the fastest way to teach
    everyone to ignore this report.
    """
    return re.sub(r"\s+", " ", text)


def run(manifest: dict, get) -> int:
    sources, pages = manifest["sources"], manifest["pages"]
    fails: list[str] = []
    warns: list[str] = []
    unknown: list[str] = []

    cache: dict[str, str | None] = {}

    def load(url: str, render: bool) -> str | None:
        if url not in cache:
            try:
                body = get(url)
                cache[url] = page_text(body) if render else flatten(body)
            except Exception as exc:  # network, DNS, 404, decode
                unknown.append(f"could not fetch {url}: {exc}")
                cache[url] = None
        return cache[url]

    print(f"{DIM}sources{OFF}")
    for key, src in sources.items():
        body = load(src["url"], render=False)
        state = f"{GRN}ok{OFF}" if body else f"{YEL}UNKNOWN{OFF}"
        print(f"  {key:<12} {state}  {DIM}{src['url']}{OFF}")

    print(f"\n{DIM}claims{OFF}")
    for c in manifest["claims"]:
        src = sources[c["source"]]
        body = load(src["url"], render=False)
        site = load(pages[c["page"]], render=True)

        missing = [s for s in c["must_contain"] if body is not None and s not in body]
        if body is not None and missing:
            fails.append(
                f"{c['id']}: source `{c['source']}` no longer contains "
                + " / ".join(repr(m) for m in missing)
                + f"\n      site says: {c['site_says']!r}"
                + f"\n      source:    {src['human']}"
                + f"\n      why it matters: {c['why']}"
            )
            mark = f"{RED}DRIFT{OFF}"
        elif body is None:
            mark = f"{YEL}UNKNOWN{OFF}"
        else:
            mark = f"{GRN}ok{OFF}"

        if site is not None and c["site_says"] not in site:
            warns.append(
                f"{c['id']}: the site no longer says {c['site_says']!r} "
                f"on {c['page']} -- manifest entry is stale, not a defect"
            )
            mark += f" {YEL}(stale entry){OFF}"

        print(f"  {c['id']:<24} {mark}")

    print(f"\n{DIM}retired phrasings{OFF}")
    for r in manifest.get("retired_phrasings", []):
        hits = []
        for name, url in pages.items():
            site = load(url, render=True)
            if site is None:
                continue
            if r["text"] in site:
                hits.append(name)
        if hits:
            fails.append(
                f"RE-ASSERTED: {r['text']!r} is back on {', '.join(hits)}\n"
                f"      retired {r['retired']} in {r['commit']}\n"
                f"      why: {r['why']}"
            )
            print(f"  {r['text'][:44]:<44} {RED}RE-ASSERTED{OFF}")
        else:
            print(f"  {r['text'][:44]:<44} {GRN}absent{OFF}")

    skipped = manifest.get("not_mechanically_checked", [])
    if skipped:
        print(f"\n{DIM}not mechanically checked (stated, not inferred){OFF}")
        for s in skipped:
            print(f"  {DIM}- {', '.join(s['claims'])} -> {s['anchor']}{OFF}")

    print()
    for w in warns:
        print(f"{YEL}WARN{OFF}  {w}")
    for u in unknown:
        print(f"{YEL}UNKNOWN{OFF}  {u}")
    for f in fails:
        print(f"{RED}FAIL{OFF}  {f}")

    if fails:
        print(f"\n{RED}{len(fails)} claim(s) no longer check out.{OFF}")
        return 1
    if unknown:
        print(f"\n{YEL}Could not verify {len(unknown)} source(s). Not a pass.{OFF}")
        return 2
    print(f"{GRN}All {len(manifest['claims'])} cited claims check out.{OFF}")
    return 0


def self_test() -> int:
    """Negative control: prove the checker fails on the bug it was built for.

    Replays 2026-08-13. The site cites the stop-rule doc beside a figure that
    document never contained, and the retired phrasing is on the page.
    """
    manifest = {
        "sources": {"stop-rule": {"url": "mem://stop-rule", "human": "-", "role": "-"}},
        "pages": {"home": "mem://home"},
        "claims": [
            {
                "id": "as-shipped-2026-08-13",
                "page": "home",
                "site_says": "none of the seven candidate state streams",
                "source": "stop-rule",
                "must_contain": ["0/7 streams beat persistence"],
                "why": "negative control",
            }
        ],
        "retired_phrasings": [
            {
                "text": "at predicting negative task outcomes",
                "retired": "2026-08-26",
                "commit": "3ed9cde",
                "why": "negative control",
            }
        ],
    }
    corpus = {
        # The real stop-rule doc: no 0/7, no "persistence" anywhere in it.
        "mem://stop-rule": "The confirmatory read is pre-registered for 2026-12-01 "
        "with a written kill criterion.",
        "mem://home": "<p>none of the seven candidate state streams beat a "
        "last-value persistence baseline at predicting negative task outcomes</p>",
    }
    rc = run(manifest, lambda u: corpus[u])
    ok = rc == 1
    print(
        f"\n{GRN}self-test PASSED{OFF}: the checker fails (rc=1) on the 2026-08-13 page."
        if ok
        else f"\n{RED}self-test FAILED{OFF}: expected rc=1, got rc={rc}. "
        "The checker would NOT have caught the bug it exists for."
    )
    return 0 if ok else 1


def main() -> int:
    here = pathlib.Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", default=str(here / "src/data/claims.json"))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    manifest = json.loads(pathlib.Path(args.manifest).read_text())
    return run(manifest, fetch)


if __name__ == "__main__":
    sys.exit(main())
