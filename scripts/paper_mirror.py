"""Discover the author's published Zenodo papers and mirror their latest versions."""

from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

SITE = "https://cirwel.org"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
ORCID = "0009-0006-7544-2374"
API = "https://zenodo.org/api/records"


def curl(url: str, dest: Path | None = None, *, accept: str | None = None) -> str | None:
    cmd = ["curl", "-fsSL", "--proto", "=https", "--proto-redir", "=https",
           "--max-time", "45", "--retry", "2", "--retry-max-time", "60"]
    if dest is not None:
        cmd.extend(["-o", str(dest)])
    if accept:
        cmd.extend(["-H", f"Accept: {accept}"])
    result = subprocess.run([*cmd, "--", url], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else None


def md5_tag(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return "md5:" + digest.hexdigest()


def read_json(url: str, *, accept: str | None = None) -> dict:
    raw = curl(url, accept=accept) if accept else curl(url)
    if raw is None:
        raise ConnectionError(f"Could not fetch {url}")
    return json.loads(raw)


def author_publications(page_size: int = 25) -> dict[str, dict]:
    """Search every page. A search hit alone does not establish authorship."""
    query = f"q=metadata.creators.person_or_org.identifiers.identifier:%22{ORCID}%22"
    publications = {}
    seen_ids = set()
    page = 1
    while True:
        # Relevance ties can change order between page requests for the same ORCID.
        result = read_json(f"{API}?{query}&all_versions=false&sort=mostrecent&size={page_size}&page={page}")
        hits = result["hits"]["hits"]
        ids = {hit["id"] for hit in hits}
        for hit in hits:
            meta = hit["metadata"]
            authors = {str(c.get("orcid", "")).removeprefix("https://orcid.org/") for c in meta.get("creators", [])}
            if (hit.get("status") == "published" and meta["resource_type"]["type"] == "publication"
                    and ORCID in authors):
                if concept := hit.get("conceptdoi"):
                    publications[concept] = hit
                else:
                    print(f"REVIEW  {API}/{hit['id']}: no published concept DOI", file=sys.stderr)
        total = result["hits"]["total"]
        total = total["value"] if isinstance(total, dict) else total
        previous_count = len(seen_ids)
        seen_ids.update(ids)
        if not result.get("links", {}).get("next") and len(seen_ids) >= total:
            return publications
        if len(seen_ids) == previous_count:
            raise ConnectionError(f"Incomplete Zenodo search on page {page}")
        page += 1


def latest_record(concept: str) -> dict:
    match = re.fullmatch(r"10\.5281/zenodo\.([0-9]+)", concept)
    if not match:
        raise ValueError(f"Invalid Zenodo concept DOI {concept!r}")
    url = f"{API}/{match[1]}/versions/latest"
    record = read_json(url)
    if not isinstance(record, dict) or record.get("conceptdoi") != concept or record.get("status") != "published":
        raise ValueError(f"{url} did not return a published version of {concept}")
    if record.get("metadata", {}).get("resource_type", {}).get("type") != "publication":
        raise ValueError(f"{concept} is no longer listed as a publication")
    if not record.get("id") or record.get("doi") != f"10.5281/zenodo.{record['id']}":
        raise ValueError(f"{concept} has no verifiable version DOI")
    return record


def manuscript_file(record: dict, preferred_key: str | None) -> dict:
    pdfs = [f for f in record.get("files", []) if f["key"].lower().endswith(".pdf")]
    for pdf in pdfs:
        if pdf["key"] == preferred_key:
            return pdf
    if len(pdfs) == 1:
        return pdfs[0]
    keys = [pdf["key"] for pdf in pdfs]
    if preferred_key is None:
        raise ValueError(f"select a manuscript for this new publication. Available PDFs: {keys}")
    raise ValueError(f"{record['doi']} has no unique replacement for {preferred_key!r}. "
                     f"Check zenodoKey in papers.json. Available PDFs: {keys}")


def first_entry(record: dict, pdf: dict, occupied: set[str]) -> dict:
    """Seed bibliographic facts once. Later runs preserve the reviewed entry."""
    # This representation has ordered, structured creator names, affiliations and rights URLs.
    source = read_json(f"{API}/{record['id']}", accept="application/vnd.inveniordm.v1+json")
    if (not source.get("is_published") or str(source["id"]) != str(record["id"])
            or str(source["parent"]["id"]) != record["conceptdoi"].rsplit(".", 1)[1]
            or source["pids"]["doi"]["identifier"] != record["doi"] or source["access"]["files"] != "public"):
        raise ValueError("Zenodo has no matching public manuscript record")
    meta = source["metadata"]
    creators = []
    for entry in meta["creators"]:
        person = entry["person_or_org"]
        name = person["name"].strip()
        if not name:
            raise ValueError("a creator has no name")
        display = " ".join(filter(None, (person.get("given_name"), person.get("family_name"))))
        orcid = next((item["identifier"].removeprefix("https://orcid.org/")
                      for item in person.get("identifiers", []) if item["scheme"] == "orcid"), "")
        creators.append({"name": display or name, "citationName": name, "orcid": orcid,
                         "type": "Organization" if person["type"] == "organizational" else "Person",
                         "institutions": [org["name"] for org in entry.get("affiliations", []) if org.get("name")]})
    if not any(c["orcid"] == ORCID for c in creators):
        raise ValueError("the latest record does not credit the catalog ORCID as a creator")
    fallback = f"zenodo-{record['conceptdoi'].rsplit('.', 1)[1]}"
    slug = fallback
    for link in record["metadata"].get("related_identifiers", []):
        match = re.fullmatch(r"https://cirwel\.org/papers/([a-z0-9]+(?:-[a-z0-9]+)*)/?", link["identifier"])
        if match and link["relation"] == "isIdenticalTo" and match[1] not in occupied:
            slug = match[1]
            break
    if slug in occupied:
        raise ValueError(f"catalog path /papers/{slug}/ is already in use")
    title = meta["title"].strip()
    if not title:
        raise ValueError("the published record has no title")
    rights = []
    for right in meta.get("rights", []):
        label = right.get("title", {}).get("en") or right.get("id")
        if label:
            url = right.get("props", {}).get("url") or right.get("link") or ""
            rights.append({"label": label, "url": url if url.startswith(("https://", "http://")) else ""})
    languages = [lang["id"] for lang in meta.get("languages", []) if lang.get("id")]
    return {
        "slug": slug, "section": "papers", "doi": record["doi"], "conceptDoi": record["conceptdoi"],
        "title": title, "researchTitle": title, "creators": creators,
        "publicationType": meta["resource_type"].get("title", {}).get("en") or "Publication",
        "publisher": meta.get("publisher", ""), "rights": rights, "languages": languages,
        "keywords": [s["subject"] for s in meta.get("subjects", []) if s.get("subject")],
        "pdfFile": "paper.pdf", "zenodoKey": pdf["key"], "repo": "", "summary": "", "abstract": [],
    }


def display_version(metadata: dict) -> str:
    raw = metadata.get("version")
    if raw:
        label = raw.removeprefix("paper-") if raw.startswith("paper-v") else raw
        return f"v{label}" if label[:1].isdigit() else label
    for relation in metadata.get("relations", {}).get("version", []):
        index = relation.get("index")
        if isinstance(index, int) and index >= 0:
            return f"v{index + 1}"
    raise ValueError("Zenodo supplied neither a version label nor a version index")


def pdf_matches(path: Path, pdf: dict) -> bool:
    if not path.is_file() or path.stat().st_size != pdf["size"]:
        return False
    with path.open("rb") as stream:
        if b"%PDF-" not in stream.read(1024):
            return False
    return md5_tag(path) == pdf["checksum"]


def update_sitemap(path: Path, papers: list[dict]) -> str | None:
    tree = ET.fromstring(path.read_bytes())
    if tree.tag != f"{{{SITEMAP_NS}}}urlset":
        raise ValueError("Unexpected sitemap root")
    entries = {entry.findtext(f"{{{SITEMAP_NS}}}loc"): entry for entry in tree}
    changed = False
    for paper in papers:
        page = f"{SITE}/papers/{paper['slug']}/"
        for url in (page, page + paper["pdfFile"]):
            entry = entries.get(url)
            if entry is None:
                entry = ET.SubElement(tree, f"{{{SITEMAP_NS}}}url")
                entries[url] = entry
                for key, value in (("loc", url), ("lastmod", paper["publicationDate"]),
                                   ("changefreq", "monthly"), ("priority", "0.8" if url == page else "0.7")):
                    ET.SubElement(entry, f"{{{SITEMAP_NS}}}{key}").text = value
                changed = True
                continue
            date = entry.find(f"{{{SITEMAP_NS}}}lastmod")
            if date is None:
                raise ValueError(f"Missing sitemap lastmod for {url}")
            if date.text != paper["publicationDate"]:
                date.text = paper["publicationDate"]
                changed = True
    if changed:
        ET.register_namespace("", SITEMAP_NS)
        ET.indent(tree, space="  ")
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(tree, encoding="unicode") + "\n"
    return None


def sync_papers(root: Path) -> None:
    catalog = root / "src/data/papers.json"
    sitemap = root / "public/sitemap.xml"
    papers = json.loads(catalog.read_text())
    tracked = {p.get("conceptDoi", p["doi"]): p for p in papers}
    if len(tracked) != len(papers) or len({p["slug"] for p in papers}) != len(papers):
        raise ValueError("Duplicate concept DOI or paper path in papers.json")
    new_concepts = sorted(author_publications().keys() - tracked.keys())
    occupied = {p["slug"] for p in papers}
    occupied.update(path.name for path in (root / "public/papers").glob("*"))
    updated = []
    changed = []
    # Stage on the same filesystem. A failed record or download must leave the checkout intact.
    with tempfile.TemporaryDirectory(dir=root) as tmp:
        stage = Path(tmp)
        replacements = {}
        for concept in [*tracked, *new_concepts]:
            paper = tracked.get(concept)
            try:
                record = latest_record(concept)
                meta = record["metadata"]
                if paper is None and meta.get("access_right") != "open":
                    raise ValueError("the manuscript is not open for public download")
                pdf = manuscript_file(record, paper["zenodoKey"] if paper else None)
                date = datetime.date.fromisoformat(meta["publication_date"])
                label = display_version(meta)
                if paper is None:
                    paper = first_entry(record, pdf, occupied)
                    occupied.add(paper["slug"])
            except (ValueError, KeyError, TypeError) as exc:
                if concept in tracked:
                    raise
                print(f"REVIEW  {concept}: {exc}", file=sys.stderr)
                continue
            slug = paper["slug"]
            next_paper = {
                **paper,
                "conceptDoi": concept,
                "doi": record["doi"],
                "version": meta.get("version"),
                "displayVersion": label,
                "publicationDate": date.isoformat(),
                "citationDate": date.strftime("%Y/%m/%d"),
                "displayDate": f"{date:%B} {date.day}, {date.year}",
                "zenodoKey": pdf["key"],
                "pdfChecksum": pdf["checksum"],
            }
            target = root / "public/papers" / slug / paper["pdfFile"]
            if not pdf_matches(target, pdf):
                download = stage / f"{slug}.pdf"
                if curl(pdf["links"]["self"], download) is None:
                    raise ConnectionError(f"[{slug}] Could not download {pdf['key']!r}")
                if not pdf_matches(download, pdf):
                    raise ValueError(f"[{slug}] Download failed PDF, size or checksum verification")
                replacements[target] = download
            updated.append(next_paper)
            if paper != next_paper or target in replacements:
                changed.append(f"{slug}: {record['doi']} ({next_paper['displayVersion']})")

        xml = update_sitemap(sitemap, updated)
        if xml is not None:
            staged_xml = stage / "sitemap.xml"
            staged_xml.write_text(xml)
            replacements[sitemap] = staged_xml
        if updated != papers:
            staged_catalog = stage / "papers.json"
            staged_catalog.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n")
            replacements[catalog] = staged_catalog
        for target, staged in replacements.items():
            target.parent.mkdir(parents=True, exist_ok=True)
            staged.replace(target)

    if changed:
        print("\n".join(changed))
    print(f"Verified {len(updated)} published Zenodo records. New catalog entries: {len(updated) - len(papers)}. "
          f"Local files updated: {len(replacements)}.")
