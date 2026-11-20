"""Offline regression tests for the publication mirror."""

import hashlib
import io
import json
from contextlib import redirect_stderr
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from paper_mirror import ORCID, SITE, SITEMAP_NS, author_publications, display_version, manuscript_file, sync_papers


class PaperMirrorTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        search = patch("paper_mirror.author_publications", return_value={})
        self.search = search.start()
        self.addCleanup(search.stop)
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
        self.catalog.write_text(json.dumps([self.paper, {**self.paper, "slug": "other", "doi": "10.5281/zenodo.999"}]))
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

    def test_new_publication_then_curated_repeat(self):
        self.catalog.write_text("[]")
        self.record["metadata"].update({"access_right": "open", "related_identifiers": [
            {"identifier": f"{SITE}/papers/nlip/", "relation": "isIdenticalTo"},
        ]})
        # The preferred path already contains a file. It belongs to the existing checkout.
        self.search.return_value = {self.record["conceptdoi"]: self.record}
        source = {
            "id": "102", "is_published": True, "access": {"files": "public"}, "parent": {"id": "100"},
            "pids": {"doi": {"identifier": self.record["doi"]}},
            "metadata": {
                "title": "A & B", "publisher": "Zenodo", "resource_type": {"title": {"en": "Report"}},
                "creators": [
                    {"person_or_org": {"name": "Example Ensemble", "type": "organizational"}},
                    {"person_or_org": {"name": "Wang, Kenny", "type": "personal", "given_name": "Kenny",
                                       "family_name": "Wang", "identifiers": [{"scheme": "orcid", "identifier": ORCID}]},
                     "affiliations": [{"name": "CIRWEL Research"}]},
                ],
                "rights": [{"id": "cc-by-4.0", "title": {"en": "CC BY 4.0"},
                            "props": {"url": "https://creativecommons.org/licenses/by/4.0/"}}],
            },
        }
        def fetch(url, dest=None, *, accept=None):
            if accept:
                self.assertEqual(url, "https://zenodo.org/api/records/102")
                return json.dumps(source)
            return self.fetch(url, dest)
        with patch("paper_mirror.curl", side_effect=fetch):
            sync_papers(self.root)
            [paper] = json.loads(self.catalog.read_text())
            self.assertEqual(paper["slug"], "zenodo-100")
            self.assertEqual(self.target.read_bytes(), self.old)
            self.assertEqual([c["citationName"] for c in paper["creators"]], ["Example Ensemble", "Wang, Kenny"])
            self.assertEqual(paper["creators"][0]["type"], "Organization")
            self.assertEqual(paper["creators"][1]["orcid"], ORCID)
            self.assertEqual(paper["rights"][0]["label"], "CC BY 4.0")
            self.assertEqual(paper["doi"], self.record["doi"])
            self.assertEqual(paper["summary"], "")
            self.assertEqual((self.root / "public/papers/zenodo-100/paper.pdf").read_bytes(), self.new)
            xml = self.sitemap.read_text()
            for suffix in ("", "paper.pdf"):
                self.assertEqual(xml.count(f"<loc>{SITE}/papers/zenodo-100/{suffix}</loc>"), 1)
            paper["summary"] = "Reviewed editorial summary."
            self.catalog.write_text(json.dumps([paper]))
            with patch.object(Path, "replace", side_effect=AssertionError("unexpected rewrite")):
                sync_papers(self.root)
            self.assertEqual(len(self.downloads), 1)
            # A current record that dropped the ORCID must not be proposed on a stale search hit.
            self.catalog.write_text("[]")
            source["metadata"]["creators"].pop()
            with redirect_stderr(io.StringIO()) as log:
                sync_papers(self.root)
            self.assertIn("does not credit", log.getvalue())
            self.assertEqual(json.loads(self.catalog.read_text()), [])

    def test_review_only_candidates_allow_tracked_updates(self):
        extra = "10.5281/zenodo.200"
        self.search.return_value = {extra: {"conceptdoi": extra}}
        def fetch(url, dest=None):
            if "/200/" in url:
                return json.dumps({**self.record, "conceptdoi": extra, "id": 201, "doi": "10.5281/zenodo.201",
                                   "metadata": {**self.record["metadata"], "access_right": "open"},
                                   "files": [{"key": "one.pdf"}, {"key": "two.pdf"}]})
            return self.fetch(url, dest)
        with redirect_stderr(io.StringIO()) as log, patch("paper_mirror.curl", side_effect=fetch):
            sync_papers(self.root)
        self.assertIn("REVIEW  " + extra, log.getvalue())
        self.assertIn("two.pdf", log.getvalue())
        self.assertEqual([p["slug"] for p in json.loads(self.catalog.read_text())], ["nlip"])
        self.assertEqual(self.target.read_bytes(), self.new)

    def test_display_versions(self):
        for raw, want in (("paper-v6.9.4", "v6.9.4"), ("1.3", "v1.3"), ("v2.0.1", "v2.0.1")):
            self.assertEqual(display_version({"version": raw}), want)
        with self.assertRaises(ValueError):
            display_version({})


class AuthorSearchTest(unittest.TestCase):
    def test_search_all_pages_and_deduplicate_by_family(self):
        def hit(number, concept, kind="publication", status="published", creator=ORCID):
            return {"id": number, "status": status, "conceptdoi": f"10.5281/zenodo.{concept}",
                    "metadata": {"resource_type": {"type": kind},
                                 "creators": [{"name": "Coauthor"}, {"orcid": creator}]}}
        pages = [
            [hit(1, 10), hit(2, 20, "software")],
            [hit(3, 30, status="draft"), hit(4, 40, creator="someone-else")],
            [hit(5, 10), hit(6, 60, creator=f"https://orcid.org/{ORCID}")],
        ]
        responses = [{"hits": {"hits": items, "total": 6}, "links": {"next": "next"} if i < 2 else {}}
                     for i, items in enumerate(pages)]
        with patch("paper_mirror.read_json", side_effect=responses) as fetch:
            papers = author_publications(page_size=2)
        self.assertEqual(list(papers), ["10.5281/zenodo.10", "10.5281/zenodo.60"])
        for index, call in enumerate(fetch.call_args_list, 1):
            self.assertIn(f"size=2&page={index}", call.args[0])

    def test_truncated_search_cannot_report_a_clean_run(self):
        with patch("paper_mirror.read_json", return_value={"hits": {"hits": [], "total": 4}, "links": {}}):
            with self.assertRaisesRegex(ConnectionError, "Incomplete"):
                author_publications()


if __name__ == "__main__":
    unittest.main()
