"""Regression tests use only fixtures created beneath scripts/.fixtures/."""

from __future__ import annotations

import base64
import io
import json
import shutil
import struct
import subprocess
import sys
import unittest
import uuid
import xml.etree.ElementTree as ET
import zipfile
import zlib
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from content import ContentError, validate
from publish import main, resolve_links

PANDOC = shutil.which("pandoc")
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a9XkAAAAASUVORK5CYII=")


class Fixture(unittest.TestCase):
    def setUp(self):
        self.root = ROOT / "scripts/.fixtures" / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        shutil.copytree(ROOT / "templates", self.root / "templates")
        shutil.copy(ROOT / "mermaid.lua", self.root / "mermaid.lua")
        (self.root / "references").mkdir()
        self.catalog = {
            "schema_version": 1,
            "repository_url": "https://github.com/JimPiquant/evaluation-articles",
            "articles": [],
        }
        self.register = {"sources": [{"id": "F01", "url": "https://learn.microsoft.com/",
                                     "authority": "Microsoft", "reviewed": "2026-11-13"}]}
        for number, folder in [(1, "one"), (2, "two")]:
            directory = self.root / "articles" / folder
            directory.mkdir(parents=True)
            title = f"Evaluation {number}"
            entry = {
                "id": f"E{number:02}", "title": title, "audience": "developers", "status": "draft",
                "article": f"articles/{folder}/{folder}.md",
                "plan": f"articles/{folder}/{folder}.plan.md",
                "slides": f"articles/{folder}/{folder}.slides.md",
                "sources": ["F01"], "reviewed": "2026-11-13", "publication_url": None,
            }
            self.catalog["articles"].append(entry)
            (directory / f"{folder}.md").write_text(
                f'---\ntitle: "{title}"\ndescription: "Practical evaluation."\n'
                'author: "Fixture author"\ndate: 2026-11-13\n---\n'
                '# Evidence\n\n[Guidance](https://learn.microsoft.com/)\n', encoding="utf-8")
            (directory / f"{folder}.slides.md").write_text(
                f'---\ntitle: "{title}"\nsubtitle: "Make evidence actionable"\n'
                'author: "Fixture author"\ndate: 2026-11-13\n---\n'
                '# Evidence\n\n- Start with a decision.\n\n'
                '::: notes\nSpeaker note survives export.\n:::\n\n'
                '# References\n\n[Guidance](https://learn.microsoft.com/)\n', encoding="utf-8")
            (directory / f"{folder}.plan.md").write_text(
                '# Plan\n\n## Purpose\nMake a decision.\n\n## Audience\nDevelopers.\n\n'
                '## Outline\nEvidence and references.\n\n'
                '## References\n[Guidance](https://learn.microsoft.com/)\n', encoding="utf-8")
        self.save()

    def tearDown(self):
        shutil.rmtree(self.root)
        parent = self.root.parent
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()

    def save(self):
        (self.root / "series.json").write_text(json.dumps(self.catalog), encoding="utf-8")
        (self.root / "references/sources.json").write_text(json.dumps(self.register), encoding="utf-8")

    def renderer(self, name, exit_code):
        stub = self.root / name
        stub.write_text(
            "#!/usr/bin/env python3\nimport base64, pathlib, sys\n"
            "if '--version' in sys.argv:\n    print('fixture-renderer 1.0'); sys.exit(0)\n"
            f"png = base64.b64decode({base64.b64encode(PNG).decode()!r})\n"
            "destination = pathlib.Path(sys.argv[sys.argv.index('--output') + 1])\n"
            "destination.write_bytes(png)\n"
            f"sys.exit({exit_code})\n", encoding="utf-8")
        stub.chmod(0o755)
        return stub

    def invoke(self, *options):
        with redirect_stdout(io.StringIO()):
            return main(["--root", str(self.root), *map(str, options)])


class ContentTests(Fixture):
    def test_catalog_rejects_ambiguous_manifest_and_missing_metadata(self):
        self.assertEqual(validate(self.root)[2], [])
        self.catalog["articles"][1]["id"] = "E01"
        self.catalog["articles"][0]["status"] = "published"
        self.catalog["articles"][0]["sources"] = ["F99"]
        self.save()
        article = self.root / self.catalog["articles"][0]["article"]
        article.write_text(article.read_text().replace('author: "Fixture author"\n', ""))
        errors = "\n".join(validate(self.root)[2])
        for message in ("duplicate article ID", "published status requires",
                        "unknown source ID", "missing metadata author"):
            self.assertIn(message, errors)

    def test_paths_and_required_plans_fail_closed(self):
        self.catalog["articles"][0]["article"] = "../outside.md"
        self.catalog["articles"][1]["slides"] = "articles/two/missing.slides.md"
        (self.root / self.catalog["articles"][0]["plan"]).write_text("# Plan\n## Purpose\nOnly.")
        self.save()
        errors = "\n".join(validate(self.root)[2])
        self.assertIn("unsafe or excluded source path", errors)
        self.assertIn("missing source", errors)
        self.assertIn("missing plan sections", errors)

    def test_links_check_paths_and_anchors_but_ignore_code_and_archive(self):
        article = self.root / self.catalog["articles"][0]["article"]
        with article.open("a") as stream:
            stream.write("\n## Inspect `metrics` and **coverage**\n")
        (self.root / "README.md").write_text(
            "[Valid](articles/one/one.md#evidence)\n"
            "[Code heading](articles/one/one.md#inspect-metrics-and-coverage)\n"
            "[Missing](articles/one/one.md#not-a-heading)\n"
            "[Broken][unknown]\n"
            "```markdown\n[Not a link to validate](missing.md)\n```\n")
        (self.root / "archive").mkdir()
        (self.root / "archive/legacy.md").write_text("[Old](missing.md)")
        (self.root / "build").mkdir()
        (self.root / "build/generated.md").write_text("[Export](missing.md)")
        for excluded in (".venv", ".sdk-cache"):
            cache = self.root / "samples" / excluded
            cache.mkdir(parents=True)
            (cache / "vendor.md").write_text("[Dependency link](missing.md)")
        errors = "\n".join(validate(self.root)[2])
        self.assertIn("missing heading anchor", errors)
        self.assertIn("undefined reference 'unknown'", errors)
        self.assertNotIn("missing local target", errors)
        self.assertNotIn("legacy.md", errors)
        self.assertNotIn("generated.md", errors)
        self.assertNotIn("#inspect-metrics-and-coverage", errors)

    def test_duplicate_source_ids_and_invalid_dates_are_errors(self):
        self.register["sources"].append(self.register["sources"][0].copy())
        self.register["sources"][0]["reviewed"] = "2026-02-30"
        self.save()
        errors = "\n".join(validate(self.root)[2])
        self.assertIn("duplicate source ID", errors)
        self.assertIn("ISO calendar date", errors)

    def test_relative_markdown_links_become_explicit_repository_main_urls(self):
        ast = {"blocks": [{"t": "Para", "c": [
            {"t": "Link", "c": [["", [], []], [{"t": "Str", "c": "Next"}],
                               ["../two/two.md#evidence", ""]]},
            {"t": "Link", "c": [["", [], []], [{"t": "Str", "c": "Here"}],
                               ["#evidence", ""]]},
        ]}]}
        resolve_links(ast, self.root / "articles/one/one.md", self.root,
                      self.catalog["repository_url"])
        self.assertEqual(ast["blocks"][0]["c"][0]["c"][2][0],
                         "https://github.com/JimPiquant/evaluation-articles/blob/main/"
                         "articles/two/two.md#evidence")
        self.assertEqual(ast["blocks"][0]["c"][1]["c"][2][0], "#evidence")


class FailureTests(Fixture):
    def test_unknown_selection_and_missing_source_return_nonzero(self):
        self.assertEqual(self.invoke("--article", "E99"), 1)
        wrapper = subprocess.run([str(ROOT / "generate-docx.sh"), "--root", str(self.root),
                                  "--article", "E99"], capture_output=True)
        self.assertNotEqual(wrapper.returncode, 0)
        (self.root / self.catalog["articles"][0]["article"]).unlink()
        self.assertEqual(self.invoke("--article", "E01"), 1)
        self.assertFalse((self.root / "build/release-manifest.json").exists())

    def test_converter_failure_cannot_publish_or_keep_a_release_manifest(self):
        stub = self.root / "failed-pandoc"
        stub.write_text("#!/usr/bin/env python3\nimport sys\n"
                        "if '--version' in sys.argv:\n    print('fixture-pandoc'); sys.exit(0)\n"
                        "print('converter rejected input', file=sys.stderr)\nsys.exit(42)\n")
        stub.chmod(0o755)
        (self.root / "build").mkdir()
        (self.root / "build/release-manifest.json").write_text("{}")
        self.assertEqual(self.invoke("--pandoc", stub), 1)
        self.assertFalse((self.root / "build/release-manifest.json").exists())


@unittest.skipUnless(PANDOC, "Pandoc is required for Office integration checks")
class OfficeTests(Fixture):
    def diagrams(self):
        for entry in self.catalog["articles"]:
            for kind in ("article", "slides"):
                path = self.root / entry[kind]
                with path.open("a") as stream:
                    stream.write(f"\n```mermaid\nflowchart LR\nA --> {entry['id']}\n```\n")

    def test_successful_bundles_have_provenance_links_notes_and_isolated_diagrams(self):
        self.diagrams()
        renderer = self.renderer("successful-renderer", 0)
        for kind in ("article", "slides"):
            path = self.root / self.catalog["articles"][0][kind]
            with path.open("a") as stream:
                stream.write("\n[Next article](../two/two.md#evidence)\n")
        self.assertEqual(self.invoke("--pandoc", PANDOC, "--mmdc", renderer), 0)
        manifest = json.loads((self.root / "build/release-manifest.json").read_text())
        self.assertEqual(manifest["selection"], ["E01", "E02"])
        self.assertEqual(len(manifest["source"]["source_bundle_sha256"]), 64)
        self.assertEqual(sum(len(row["outputs"]) for row in manifest["articles"]), 4)
        diagram_paths = [diagram["path"] for row in manifest["articles"]
                         for diagram in row["diagrams"]]
        self.assertEqual(len(diagram_paths), 4)
        self.assertEqual(len(set(diagram_paths)), 4)
        with zipfile.ZipFile(self.root / "build/E01/E01.pptx") as package:
            notes = " ".join(package.read(name).decode() for name in package.namelist()
                             if name.startswith("ppt/notesSlides/") and name.endswith(".xml"))
            self.assertIn("Speaker note survives export.", notes)
        for extension in ("docx", "pptx"):
            with zipfile.ZipFile(self.root / f"build/E01/E01.{extension}") as package:
                relations = " ".join(package.read(name).decode() for name in package.namelist()
                                     if name.endswith(".rels"))
                self.assertIn("/blob/main/articles/two/two.md#evidence", relations)

    def test_renderer_failure_is_fatal_even_when_it_writes_an_image(self):
        self.diagrams()
        good = self.renderer("successful-renderer", 0)
        self.assertEqual(self.invoke("--article", "E01", "--format", "docx",
                                     "--pandoc", PANDOC, "--mmdc", good), 0)
        old = (self.root / "build/E01/E01.docx").read_bytes()
        bad = self.renderer("failing-renderer", 7)
        self.assertEqual(self.invoke("--article", "E01", "--format", "docx",
                                     "--pandoc", PANDOC, "--mmdc", bad), 1)
        self.assertEqual((self.root / "build/E01/E01.docx").read_bytes(), old)
        self.assertFalse((self.root / "build/release-manifest.json").exists())
        self.assertFalse(any((self.root / "build").glob(".publish-*")))

    def test_sources_changing_during_export_cannot_be_labeled_as_a_release(self):
        self.diagrams()
        renderer = self.renderer("mutating-renderer", 0)
        source = self.root / self.catalog["articles"][0]["article"]
        script = renderer.read_text().replace(
            "destination.write_bytes(png)\n", "destination.write_bytes(png)\n"
            f"pathlib.Path({str(source)!r}).write_text('changed during export')\n")
        renderer.write_text(script)
        self.assertEqual(self.invoke("--article", "E01", "--format", "docx",
                                     "--pandoc", PANDOC, "--mmdc", renderer), 1)
        self.assertFalse((self.root / "build/release-manifest.json").exists())
        self.assertFalse((self.root / "build/E01").exists())

    def test_word_does_not_duplicate_a_matching_initial_article_title(self):
        entry = self.catalog["articles"][0]
        source = self.root / entry["article"]
        source.write_text(source.read_text().replace(
            "# Evidence", f"# {entry['title']}\n\n# Evidence", 1))
        self.assertEqual(self.invoke("--article", "E01", "--format", "docx",
                                     "--pandoc", PANDOC), 0)
        with zipfile.ZipFile(self.root / "build/E01/E01.docx") as package:
            document = ET.fromstring(package.read("word/document.xml"))
            words = [element.text for element in document.iter()
                     if element.tag.endswith("}t")]
            self.assertEqual(words.count(entry["title"]), 1)
            self.assertIn("Evidence", words)

    def test_cover_review_date_has_its_own_box_without_duplicate_subtitle_labels(self):
        entry = self.catalog["articles"][0]
        slides = self.root / entry["slides"]
        subtitle = "E01 | Hands-on lab | Draft"
        slides.write_text(slides.read_text().replace("Make evidence actionable", subtitle))
        self.assertEqual(self.invoke("--article", "E01", "--format", "pptx",
                                     "--pandoc", PANDOC), 0)
        ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
              "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
        with zipfile.ZipFile(self.root / "build/E01/E01.pptx") as package:
            cover = ET.fromstring(package.read("ppt/slides/slide1.xml"))
            master = ET.fromstring(package.read("ppt/slideMasters/slideMaster1.xml"))
        shapes = {}
        for shape in cover.findall(".//p:sp", ns):
            placeholder = shape.find(".//p:ph", ns)
            if placeholder is not None:
                shapes[placeholder.get("type")] = shape
        text = lambda shape: " ".join(node.text or "" for node in shape.findall(".//a:t", ns))
        self.assertIn(subtitle, text(shapes["subTitle"]))
        self.assertEqual(text(shapes["subTitle"]).count("E01"), 1)
        self.assertEqual(text(shapes["subTitle"]).casefold().count("draft"), 1)
        self.assertEqual(text(shapes["dt"]), "Sources reviewed 2026-11-13")
        footer = next(shape for shape in master.findall(".//p:sp", ns)
                      if shape.find("p:nvSpPr/p:cNvPr", ns).get("name") == "Field guide footer")

        def rectangle(shape):
            transform = shape.find("p:spPr/a:xfrm", ns)
            offset, extent = transform.find("a:off", ns), transform.find("a:ext", ns)
            return tuple(int(value) for value in
                         (offset.get("x"), offset.get("y"), extent.get("cx"), extent.get("cy")))

        title, description, review, brand = map(rectangle,
                                               (shapes["ctrTitle"], shapes["subTitle"],
                                                shapes["dt"], footer))
        self.assertLess(title[1] + title[3], description[1])
        self.assertLess(description[1] + description[3], review[1])
        self.assertLess(review[1] + review[3], brand[1])
        self.assertLessEqual(review[0] + review[2], 9144000)
        self.assertGreater(review[2], description[2] * 0.9)

    def test_wide_and_tall_images_fit_page_and_slide_without_aspect_distortion(self):
        def png(width, height):
            def chunk(name, data):
                return (struct.pack("!I", len(data)) + name + data
                        + struct.pack("!I", zlib.crc32(name + data)))
            header = struct.pack("!IIBBBBB", width, height, 8, 2, 0, 0, 0)
            pixels = (b"\x00" + b"\xFF\xFF\xFF" * width) * height
            return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
                    + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b""))

        entry = self.catalog["articles"][0]
        directory = self.root / "articles/one/images"
        directory.mkdir()
        for label, width, height in (("Tall", 200, 1600), ("Wide", 1600, 200)):
            (directory / f"{label}.png").write_bytes(png(width, height))
            for kind in ("article", "slides"):
                source = self.root / entry[kind]
                with source.open("a") as stream:
                    heading = "##" if kind == "article" else "#"
                    stream.write(f"\n{heading} {label} image\n\n"
                                 f"![{label}](images/{label}.png){{width=20in height=20in}}\n")
        self.assertEqual(self.invoke("--article", "E01", "--format", "all",
                                     "--pandoc", PANDOC), 0)
        config = json.loads((self.root / "templates/style.json").read_text())
        with zipfile.ZipFile(self.root / "build/E01/E01.docx") as package:
            document = ET.fromstring(package.read("word/document.xml"))
            extents = document.findall(
                ".//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent")
            sizes = [(int(node.get("cx")), int(node.get("cy"))) for node in extents]
        self.assertEqual(len(sizes), 2)
        for (width, height), ratio in zip(sizes, (0.125, 8)):
            self.assertLessEqual(width, config["word"]["image_max_width_inches"] * 914400 + 1)
            self.assertLessEqual(height, config["word"]["image_max_height_inches"] * 914400 + 1)
            self.assertAlmostEqual(width / height, ratio, places=4)
        ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
              "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
        sizes = []
        with zipfile.ZipFile(self.root / "build/E01/E01.pptx") as package:
            for name in package.namelist():
                if name.startswith("ppt/slides/slide") and name.endswith(".xml"):
                    slide = ET.fromstring(package.read(name))
                    for picture in slide.findall(".//p:pic", ns):
                        extent = picture.find("p:spPr/a:xfrm/a:ext", ns)
                        sizes.append((int(extent.get("cx")), int(extent.get("cy"))))
                        crop = picture.find(".//a:srcRect", ns)
                        self.assertTrue(crop is None or all(int(v) == 0 for v in crop.attrib.values()))
        self.assertEqual(len(sizes), 2)
        for (width, height), ratio in zip(sizes, (0.125, 8)):
            self.assertLessEqual(width, config["slides"]["image_max_width_inches"] * 914400 + 1)
            self.assertLessEqual(height, config["slides"]["image_max_height_inches"] * 914400 + 1)
            self.assertAlmostEqual(width / height, ratio, places=4)

    def test_highlighted_code_styles_and_runs_have_explicit_monospace_fonts(self):
        entry = self.catalog["articles"][0]
        source = self.root / entry["article"]
        with source.open("a") as stream:
            stream.write("\n```python\ndef score(response):\n    return len(response)\n```\n")
        self.assertEqual(self.invoke("--article", "E01", "--format", "docx",
                                     "--pandoc", PANDOC), 0)
        w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        font = json.loads((self.root / "templates/style.json").read_text())["code_font"]
        with zipfile.ZipFile(self.root / "build/E01/E01.docx") as package:
            document = ET.fromstring(package.read("word/document.xml"))
            styles = ET.fromstring(package.read("word/styles.xml"))
        tokens = set()
        for paragraph in document.findall(".//" + w + "p"):
            style = paragraph.find(w + "pPr/" + w + "pStyle")
            if style is None or style.get(w + "val") != "SourceCode":
                continue
            for run in paragraph.findall(w + "r"):
                rfonts = run.find(w + "rPr/" + w + "rFonts")
                self.assertIsNotNone(rfonts)
                self.assertEqual(rfonts.get(w + "ascii"), font)
                token = run.find(w + "rPr/" + w + "rStyle")
                if token is not None:
                    tokens.add(token.get(w + "val"))
        self.assertTrue(tokens)
        for row in styles.findall(w + "style"):
            if row.get(w + "styleId") in tokens | {"SourceCode", "VerbatimChar"}:
                self.assertEqual(row.find(w + "rPr/" + w + "rFonts").get(w + "ascii"), font)


if __name__ == "__main__":
    unittest.main()
