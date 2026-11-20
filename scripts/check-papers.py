#!/usr/bin/env python3
"""Verify that hosted paper pages and PDFs match Zenodo and Google Scholar rules.

Google Scholar does not index Zenodo directly and ignores Schema.org JSON-LD.
To be indexed from cirwel.org, each paper needs:
  1. An HTML landing page with Highwire Press meta tags (`citation_title`,
     `citation_author`, `citation_publication_date`, `citation_pdf_url`,
     `citation_doi`, `citation_abstract_html_url`).
  2. A full-text PDF hosted in the SAME subdirectory as the HTML landing page
     (`https://cirwel.org/papers/<slug>/<file>.pdf`).
  3. Parity with Zenodo's latest record for ORCID 0009-0006-7544-2374 so a
     hosted PDF never lags a new deposit.

Exit codes match scripts/check-claims.py:
  0  ok
  1  DRIFT / contract violation
  2  UNVERIFIABLE (network failure)

Usage:
    scripts/check-papers.py              # check local tree + dist against live Zenodo
    scripts/check-papers.py --offline    # check local files + dist without network
    scripts/check-papers.py --sync       # discover ORCID publications and update PDFs, citations and sitemap
    scripts/check-papers.py --live       # check the actual production pages and PDF downloads
    scripts/check-papers.py --self-test  # offline negative control
"""

from __future__ import annotations

import argparse
from html import unescape
import json
import pathlib
import re
import sys
import tempfile
import xml.etree.ElementTree as ET

from paper_mirror import SITE, author_publications, curl, md5_tag, sync_papers
DRIFT, UNVERIFIABLE = 1, 2


def extract_meta(html_text: str) -> dict[str, list[str]]:
    tags: dict[str, list[str]] = {}
    for m in re.finditer(r"<meta\s+[^>]*>", html_text, flags=re.I):
        tag = m.group(0)
        nm = re.search(r'\bname="([^"]+)"', tag, flags=re.I)
        ct = re.search(r'\bcontent="([^"]*)"', tag, flags=re.I)
        if nm and ct:
            tags.setdefault(nm.group(1), []).append(unescape(ct.group(1)))
    return tags


def check_scholar_html(slug: str, paper: dict, html_text: str) -> list[str]:
    failures: list[str] = []
    meta = extract_meta(html_text)
    required = [
        "citation_title",
        "citation_author",
        "citation_publication_date",
        "citation_pdf_url",
        "citation_abstract_html_url",
    ]
    for key in required:
        if not meta.get(key):
            failures.append(f"[{slug}] missing required meta tag: {key}")
    authors = [c["citationName"] for c in paper["creators"]] if "creators" in paper else [paper.get("citationAuthor")]
    if any(authors) and meta.get("citation_author") != authors:
        failures.append(f"[{slug}] citation_author tags do not match the ordered creator list")
    if paper.get("doi") and meta.get("citation_doi") != [paper["doi"]]:
        failures.append(f"[{slug}] citation_doi should be {paper['doi']!r}, got {meta.get('citation_doi')!r}")
    if paper.get("citationDate") and meta.get("citation_publication_date") != [paper["citationDate"]]:
        failures.append(f"[{slug}] citation_publication_date should be {paper['citationDate']!r}")

    pdf_urls = meta.get("citation_pdf_url", [])
    abs_urls = meta.get("citation_abstract_html_url", [])
    expected_dir = f"{SITE}/papers/{slug}/"
    expected_pdf = f"{expected_dir}{paper['pdfFile']}"

    if pdf_urls and pdf_urls[0] != expected_pdf:
        failures.append(
            f"[{slug}] citation_pdf_url is {pdf_urls[0]!r}, want {expected_pdf!r}"
        )
    if abs_urls and abs_urls[0] != expected_dir:
        failures.append(
            f"[{slug}] citation_abstract_html_url is {abs_urls[0]!r}, want {expected_dir!r}"
        )
    if pdf_urls and abs_urls:
        pdf_dir = pdf_urls[0].rsplit("/", 1)[0] + "/"
        if not pdf_dir.startswith(abs_urls[0]):
            failures.append(
                f"[{slug}] Google Scholar subdirectory violation: PDF {pdf_urls[0]!r} "
                f"is not in the same directory as abstract {abs_urls[0]!r}"
            )
    return failures


def papers_by_concept_doi(papers: list[dict]) -> dict[str, dict]:
    return {p.get("conceptDoi", p["doi"]): p for p in papers}


def verify_against_zenodo(papers: list[dict], zenodo_hits: list[dict]) -> list[str]:
    failures: list[str] = []
    by_doi = papers_by_concept_doi(papers)

    for hit in zenodo_hits:
        meta = hit.get("metadata", {})
        if (meta.get("resource_type") or {}).get("type") != "publication":
            continue
        cdoi = hit.get("conceptdoi")
        if cdoi not in by_doi:
            failures.append(f"[zenodo] publication deposit {cdoi} ({meta.get('title')}) missing from papers.json")
            continue
        p = by_doi[cdoi]
        if p.get("conceptDoi") and hit.get("doi") != p["doi"]:
            failures.append(f"[{p['slug']}] version DOI {p['doi']!r} != Zenodo {hit.get('doi')!r}")
        if meta.get("publication_date") != p["publicationDate"]:
            failures.append(
                f"[{p['slug']}] publicationDate {p['publicationDate']!r} != Zenodo {meta.get('publication_date')!r}"
            )
        if meta.get("version") != p["version"]:
            failures.append(
                f"[{p['slug']}] version {p['version']!r} != Zenodo {meta.get('version')!r}"
            )
        files = {f["key"]: f for f in hit.get("files", [])}
        zfile = files.get(p["zenodoKey"])
        if not zfile:
            failures.append(f"[{p['slug']}] zenodoKey {p['zenodoKey']!r} not found in Zenodo record {cdoi}")
        elif zfile.get("checksum") != p["pdfChecksum"]:
            failures.append(
                f"[{p['slug']}] pdfChecksum {p['pdfChecksum']!r} != Zenodo {zfile.get('checksum')!r}"
            )
    return failures


def self_test() -> int:
    paper = {
        "slug": "unitares",
        "doi": "10.5281/zenodo.19647159",
        "publicationDate": "2026-10-13",
        "version": "paper-v6.9.4",
        "pdfFile": "unitares-v6.pdf",
        "zenodoKey": "unitares-v6.pdf",
        "pdfChecksum": "md5:a92d2c1aedceee052703192b8c70cc1a",
    }
    good_html = (
        '<meta name="citation_title" content="UNITARES">'
        '<meta name="citation_author" content="Wang, Kenny">'
        '<meta name="citation_publication_date" content="2026/10/13">'
        '<meta name="citation_pdf_url" content="https://cirwel.org/papers/unitares/unitares-v6.pdf">'
        '<meta name="citation_abstract_html_url" content="https://cirwel.org/papers/unitares/">'
        '<meta name="citation_doi" content="10.5281/zenodo.19647159">'
    )
    if check_scholar_html("unitares", paper, good_html):
        print("FAIL: self-test rejected valid Scholar HTML")
        return DRIFT

    # Negative control 1: cross-directory PDF URL (rejected by Google Scholar)
    bad_dir_html = good_html.replace(
        "https://cirwel.org/papers/unitares/unitares-v6.pdf",
        "https://cirwel.org/pdfs/unitares-v6.pdf",
    )
    if not check_scholar_html("unitares", paper, bad_dir_html):
        print("FAIL: self-test did not catch cross-directory citation_pdf_url")
        return DRIFT

    # Negative control 2: stale checksum on Zenodo
    stale_hit = {
        "conceptdoi": "10.5281/zenodo.19647159",
        "metadata": {
            "resource_type": {"type": "publication"},
            "publication_date": "2026-10-13",
            "version": "paper-v6.9.5",
        },
        "files": [{"key": "unitares-v6.pdf", "checksum": "md5:0000"}],
    }
    if not verify_against_zenodo([paper], [stale_hit]):
        print("FAIL: self-test did not catch Zenodo version/checksum drift")
        return DRIFT

    print("self-test PASSED: Scholar tag rules and Zenodo drift controls fired as expected.")
    return 0


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--sync", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if args.sync and not args.offline:
        try:
            sync_papers(root)
        except ConnectionError as exc:
            print(f"UNVERIFIABLE: {exc}", file=sys.stderr)
            return UNVERIFIABLE
        except (ValueError, KeyError, TypeError, ET.ParseError) as exc:
            print(f"FAIL  {exc}", file=sys.stderr)
            return DRIFT
        if not args.live:
            return 0  # dist may still contain pages from before this update

    papers_path = root / "src/data/papers.json"
    papers = json.loads(papers_path.read_text())
    failures: list[str] = []

    if not args.offline:
        try:
            hits = author_publications()
        except (ConnectionError, ValueError, KeyError, TypeError) as exc:
            print(f"UNVERIFIABLE: could not read Zenodo search: {exc}")
            return UNVERIFIABLE
        failures.extend(verify_against_zenodo(papers, list(hits.values())))

    for p in papers:
        pdf_path = root / "public/papers" / p["slug"] / p["pdfFile"]
        if not pdf_path.exists():
            failures.append(f"[{p['slug']}] missing PDF at {pdf_path}")
        else:
            actual = md5_tag(pdf_path)
            if actual != p["pdfChecksum"]:
                failures.append(
                    f"[{p['slug']}] local PDF checksum {actual} != papers.json {p['pdfChecksum']}"
                )

        if args.live:
            live_html = curl(f"{SITE}/papers/{p['slug']}/")
            if live_html is None:
                print(f"UNVERIFIABLE: could not fetch {SITE}/papers/{p['slug']}/")
                return UNVERIFIABLE
            failures.extend(check_scholar_html(p["slug"], p, live_html))
            with tempfile.TemporaryDirectory() as tmp:
                downloaded = pathlib.Path(tmp) / "paper.pdf"
                url = f"{SITE}/papers/{p['slug']}/{p['pdfFile']}"
                if curl(url, downloaded) is None:
                    print(f"UNVERIFIABLE: could not fetch {url}")
                    return UNVERIFIABLE
                if md5_tag(downloaded) != p["pdfChecksum"]:
                    failures.append(f"[{p['slug']}] deployed PDF checksum differs from papers.json at {url}")
        else:
            dist_html = root / "dist/papers" / p["slug"] / "index.html"
            if dist_html.exists():
                failures.extend(check_scholar_html(p["slug"], p, dist_html.read_text()))

    if failures:
        for f in failures:
            print(f"FAIL  {f}")
        return DRIFT

    checks = ["local PDF checksums"]
    if not args.offline:
        checks.append("Zenodo catalog check")
    if args.live:
        checks.append("live Scholar tags and PDF downloads")
    else:
        checks.append("Scholar tags in available builds")
    print(f"All {len(papers)} papers verified ({', '.join(checks)}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
