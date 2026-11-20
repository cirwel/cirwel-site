"""Offline regression tests for the publication mirror."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from paper_mirror import SITE, SITEMAP_NS, display_version, manuscript_file, sync_papers


class PaperMirrorTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.catalog = self.root / "src/data/papers.json"
        self.catalog.parent.mkdir(parents=True)
        self.sitemap = self.root / "public/sitemap.xml"
        self.target = self.root / "public/papers/nlip/report.pdf"
        self.target.parent.mkdir(parents=True)
        self.old = b"%PDF-1.7\nold"
        self.new = b"%PDF-1.7\nnew"
        self.target.write_bytes(self.old)
        self.paper = {
            "slug": "nlip", "doi": "10.5281/zenodo.100", "version": "v1.0",
            "pdfFile": "report.pdf", "zenodoKey": "report.pdf", "summary": "Curated.",
            "pdfChecksum": "md5:" + hashlib.md5(self.old).hexdigest(),
            "publicationDate": "2026-11-15", "displayVersion": "v1.0",
            "citationDate": "2026/11/15", "displayDate": "November 15, 2026",
        }
        self.catalog.write_text(json.dumps([self.paper]))
        locations = (f"{SITE}/papers/nlip/", f"{SITE}/papers/nlip/report.pdf")
        self.sitemap.write_text(f'<urlset xmlns="{SITEMAP_NS}">' + "".join(
            f"<url><loc>{url}</loc><lastmod>2026-11-15</lastmod></url>" for url in locations
        ) + "</urlset>")
        self.record = {
            "id": 102, "doi": "10.5281/zenodo.102", "conceptdoi": self.paper["doi"],
            "status": "published",
            "metadata": {"publication_date": "2026-11-19", "resource_type": {"type": "publication"},
                         "relations": {"version": [{"index": 1}]}},
            "files": [{"key": "report (2).pdf", "size": len(self.new),
                       "checksum": "md5:" + hashlib.md5(self.new).hexdigest(),
                       "links": {"self": "https://zenodo.org/example/content"}}],
        }
        self.downloads = []

    def fetch(self, url, dest=None):
        if dest is None:
            self.assertEqual(url, "https://zenodo.org/api/records/100/versions/latest")
            return json.dumps(self.record)
        self.assertEqual(url, self.record["files"][0]["links"]["self"])
        self.downloads.append(url)
        dest.write_bytes(self.new)
        return ""

    def files(self):
        return [p.read_bytes() for p in (self.target, self.catalog, self.sitemap)]

    def test_rename_pin_sitemap_and_repeat(self):
        with patch("paper_mirror.curl", side_effect=self.fetch):
            sync_papers(self.root)
            [updated] = json.loads(self.catalog.read_text())
            self.assertEqual(updated, {
                **self.paper, "conceptDoi": self.paper["doi"], "doi": self.record["doi"],
                "zenodoKey": "report (2).pdf", "pdfChecksum": self.record["files"][0]["checksum"],
                "version": None, "displayVersion": "v2", "publicationDate": "2026-11-19",
                "displayDate": "November 19, 2026", "citationDate": "2026/11/19",
            })
            self.assertEqual(self.target.read_bytes(), self.new)
            self.assertEqual(self.sitemap.read_text().count("<lastmod>2026-11-19</lastmod>"), 2)
            snapshot = self.files()
            with patch.object(Path, "replace", side_effect=AssertionError("unexpected write")):
                sync_papers(self.root)
            self.assertEqual(len(self.downloads), 1)
            self.assertEqual(self.files(), snapshot)

    def test_refuses_wrong_bytes_and_interrupted_download(self):
        before = self.files()
        for payload, result, error in ((b"%PDF-incomplete", None, ConnectionError),
                                       (self.old, "", ValueError)):
            def bad_download(url, dest=None):
                if dest is None:
                    return self.fetch(url)
                dest.write_bytes(payload)
                return result
            with self.subTest(payload=payload), patch("paper_mirror.curl", side_effect=bad_download):
                with self.assertRaises(error):
                    sync_papers(self.root)
                self.assertEqual(self.files(), before)

    def test_later_failure_does_not_promote_staged_paper(self):
        self.catalog.write_text(json.dumps([self.paper, {**self.paper, "doi": "10.5281/zenodo.999"}]))
        before = self.files()
        def second_concept_unavailable(url, dest=None):
            if "/999/" in url:
                return None
            return self.fetch(url, dest)
        with patch("paper_mirror.curl", side_effect=second_concept_unavailable):
            with self.assertRaises(ConnectionError):
                sync_papers(self.root)
        self.assertEqual(len(self.downloads), 1)
        self.assertEqual(self.files(), before)

    def test_draft_or_wrong_family(self):
        for field, value in (("status", "draft"), ("conceptdoi", "10.5281/zenodo.99")):
            with self.subTest(field=field), patch.dict(self.record, {field: value}):
                with patch("paper_mirror.curl", side_effect=self.fetch):
                    with self.assertRaises(ValueError):
                        sync_papers(self.root)
        self.assertEqual(self.downloads, [])

    def test_multiple_pdfs_require_known_key(self):
        self.record["files"].append({"key": "supplement.PDF"})
        with self.assertRaisesRegex(ValueError, "no unique replacement"):
            manuscript_file(self.record, "report.pdf")
        self.assertEqual(manuscript_file(self.record, "report (2).pdf"), self.record["files"][0])

    def test_display_versions(self):
        for raw, want in (("paper-v6.9.4", "v6.9.4"), ("1.3", "v1.3"), ("v2.0.1", "v2.0.1")):
            self.assertEqual(display_version({"version": raw}), want)
        with self.assertRaises(ValueError):
            display_version({})


if __name__ == "__main__":
    unittest.main()
