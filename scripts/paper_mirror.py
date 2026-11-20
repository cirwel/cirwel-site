"""Mirror the latest published Zenodo version of each paper in the CIRWEL catalog."""

from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

SITE = "https://cirwel.org"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def curl(url: str, dest: Path | None = None) -> str | None:
    cmd = ["curl", "-fsSL", "--proto", "=https", "--proto-redir", "=https",
           "--max-time", "45", "--retry", "2", "--retry-max-time", "60"]
    if dest is not None:
        cmd.extend(["-o", str(dest)])
    result = subprocess.run([*cmd, "--", url], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else None


def md5_tag(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return "md5:" + digest.hexdigest()


def latest_record(concept: str) -> dict:
    match = re.fullmatch(r"10\.5281/zenodo\.([0-9]+)", concept)
    if not match:
        raise ValueError(f"Invalid Zenodo concept DOI {concept!r}")
    url = f"https://zenodo.org/api/records/{match[1]}/versions/latest"
    raw = curl(url)
    if raw is None:
        raise ConnectionError(f"Could not fetch {url}")
    record = json.loads(raw)
    if not isinstance(record, dict) or record.get("conceptdoi") != concept or record.get("status") != "published":
        raise ValueError(f"{url} did not return a published version of {concept}")
    if record.get("metadata", {}).get("resource_type", {}).get("type") != "publication":
        raise ValueError(f"{concept} is no longer listed as a publication")
    if not record.get("id") or record.get("doi") != f"10.5281/zenodo.{record['id']}":
        raise ValueError(f"{concept} has no verifiable version DOI")
    return record


def manuscript_file(record: dict, preferred_key: str) -> dict:
    pdfs = [f for f in record.get("files", []) if f["key"].lower().endswith(".pdf")]
    for pdf in pdfs:
        if pdf["key"] == preferred_key:
            return pdf
    if len(pdfs) == 1:
        return pdfs[0]
    keys = [pdf["key"] for pdf in pdfs]
    raise ValueError(f"{record['doi']} has no unique replacement for {preferred_key!r}. "
                     f"Check zenodoKey in papers.json. Available PDFs: {keys}")


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
    entries = {entry.findtext(f"{{{SITEMAP_NS}}}loc"): entry for entry in tree}
    changed = False
    for paper in papers:
        page = f"{SITE}/papers/{paper['slug']}/"
        for url in (page, page + paper["pdfFile"]):
            entry = entries.get(url)
            date = entry.find(f"{{{SITEMAP_NS}}}lastmod") if entry is not None else None
            if date is None:
                raise ValueError(f"Missing sitemap lastmod for {url}")
            if date.text != paper["publicationDate"]:
                date.text = paper["publicationDate"]
                changed = True
    if changed:
        ET.register_namespace("", SITEMAP_NS)
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(tree, encoding="unicode") + "\n"
    return None


def sync_papers(root: Path) -> None:
    catalog = root / "src/data/papers.json"
    sitemap = root / "public/sitemap.xml"
    papers = json.loads(catalog.read_text())
    updated = []
    changed = []
    # Stage on the same filesystem. A failed record or download must leave the checkout intact.
    with tempfile.TemporaryDirectory(dir=root) as tmp:
        stage = Path(tmp)
        replacements = {}
        for paper in papers:
            slug = paper["slug"]
            concept = paper.get("conceptDoi", paper["doi"])
            record = latest_record(concept)
            meta = record["metadata"]
            pdf = manuscript_file(record, paper["zenodoKey"])
            date = datetime.date.fromisoformat(meta["publication_date"])
            next_paper = {
                **paper,
                "conceptDoi": concept,
                "doi": record["doi"],
                "version": meta.get("version"),
                "displayVersion": display_version(meta),
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
    print(f"Verified {len(papers)} published Zenodo records. Local files updated: {len(replacements)}.")
