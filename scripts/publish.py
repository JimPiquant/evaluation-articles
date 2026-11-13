#!/usr/bin/env python3
"""Publish catalog articles to reproducible, provenance-bearing Office bundles."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from content import ContentError, load_json, source_path, validate
from build_templates import W, A, P, element, xml_edit, write_package


class PublishError(RuntimeError):
    pass


def run(command, *, cwd: Path, env=None, input_text=None) -> str:
    try:
        result = subprocess.run(command, cwd=cwd, env=env, input=input_text,
                                text=True, capture_output=True, check=True)
    except OSError as exc:
        raise PublishError(f"Cannot run {command[0]}: {exc}") from exc
    except subprocess.CalledProcessError as exc:
        diagnostic = (exc.stderr or exc.stdout or "").strip()
        raise PublishError(f"{command[0]} failed (exit {exc.returncode}): {diagnostic}") from exc
    return result.stdout


def tool(name: str, root: Path) -> tuple[str, str]:
    executable = shutil.which(name)
    if not executable:
        raise PublishError(f"Required tool is missing: {name}")
    version = run([executable, "--version"], cwd=root).strip()
    if not version:
        raise PublishError(f"Tool did not report a version: {name}")
    return executable, version.splitlines()[0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from nodes(child)


def inline_text(inlines: list) -> str:
    result = []
    for inline in inlines:
        kind, value = inline.get("t"), inline.get("c")
        if kind in {"Str", "MetaString"}:
            result.append(value)
        elif kind in {"Space", "SoftBreak", "LineBreak"}:
            result.append(" ")
        elif kind in {"Code", "Math"}:
            result.append(value[1])
        elif kind in {"Link", "Image", "Span", "Quoted"}:
            result.append(inline_text(value[1]))
        elif isinstance(value, list):
            result.append(inline_text(value))
    return "".join(result)


def remove_repeated_word_title(ast: dict, title: str):
    blocks = ast["blocks"]
    if blocks and blocks[0].get("t") == "Header" and blocks[0]["c"][0] == 1:
        heading = inline_text(blocks[0]["c"][2])
        if " ".join(heading.split()).casefold() == " ".join(title.split()).casefold():
            blocks.pop(0)


def metadata_text(value: dict) -> str:
    return value.get("c", "") if value.get("t") == "MetaString" else inline_text(value.get("c", []))


def slide_metadata(ast: dict, entry: dict):
    subtitle = metadata_text(ast["meta"].get("subtitle", {})).strip()
    labels = []
    if not re.search(r"\b" + re.escape(entry["id"]) + r"\b", subtitle, re.IGNORECASE):
        labels.append(entry["id"])
    if not re.search(r"\b" + re.escape(entry["status"]) + r"\b", subtitle, re.IGNORECASE):
        labels.append(entry["status"].capitalize())
    ast["meta"]["subtitle"] = {"t": "MetaString", "c": " | ".join([subtitle, *labels])}
    authored = metadata_text(ast["meta"].get("date", {}))
    review = f"Sources reviewed {entry['reviewed']}"
    if authored and authored != entry["reviewed"]:
        review = f"Authored {authored} · {review}"
    ast["meta"]["date"] = {"t": "MetaString", "c": review}


def word_code_fonts(path: Path, config: dict):
    """Explicit code fonts also cover viewers that ignore character inheritance."""
    font = config["code_font"]
    points = round(config["word"]["code_points"] * 2)
    with zipfile.ZipFile(path) as package:
        members = {name: package.read(name) for name in package.namelist()}
    code_styles = {"SourceCode", "VerbatimChar"}

    def fonts(rpr):
        rfonts = element(rpr, W, "rFonts")
        rfonts.attrib.clear()
        for name in ("ascii", "hAnsi", "eastAsia", "cs"):
            rfonts.set(f"{{{W}}}{name}", font)
        element(rpr, W, "sz", val=points)
        element(rpr, W, "szCs", val=points)

    def styles(root):
        rows = root.findall(f"{{{W}}}style")
        for _ in rows:
            previous = len(code_styles)
            for row in rows:
                parent = row.find(f"{{{W}}}basedOn")
                if parent is not None and parent.get(f"{{{W}}}val") in code_styles:
                    code_styles.add(row.get(f"{{{W}}}styleId"))
            if len(code_styles) == previous:
                break
        for row in rows:
            if row.get(f"{{{W}}}styleId") in code_styles:
                fonts(element(row, W, "rPr"))

    def document(root):
        for paragraph in root.findall(f".//{{{W}}}p"):
            style = paragraph.find(f"{{{W}}}pPr/{{{W}}}pStyle")
            block_code = style is not None and style.get(f"{{{W}}}val") in code_styles
            for run in paragraph.findall(f"{{{W}}}r"):
                rstyle = run.find(f"{{{W}}}rPr/{{{W}}}rStyle")
                if block_code or (rstyle is not None and rstyle.get(f"{{{W}}}val") in code_styles):
                    fonts(element(run, W, "rPr"))

    members["word/styles.xml"] = xml_edit(members["word/styles.xml"], styles)
    members["word/document.xml"] = xml_edit(members["word/document.xml"], document)
    write_package(path, members)


def pptx_image_geometry(path: Path, layout: Path):
    """Correct Pandoc's placeholder expansion and whole-point image rounding."""
    if not layout.exists():
        return
    records = {row["source"]: row for row in
               (json.loads(line) for line in layout.read_text(encoding="utf-8").splitlines())}
    with zipfile.ZipFile(path) as package:
        members = {name: package.read(name) for name in package.namelist()}

    def pictures(root):
        for picture in root.findall(f".//{{{P}}}pic"):
            description = picture.find(f"{{{P}}}nvPicPr/{{{P}}}cNvPr")
            record = records.get(description.get("descr"))
            if record is None:
                raise PublishError("PowerPoint image has no matching proportional layout record")
            transform = picture.find(f"{{{P}}}spPr/{{{A}}}xfrm")
            offset, extent = transform.find(f"{{{A}}}off"), transform.find(f"{{{A}}}ext")
            old_width, old_height = int(extent.get("cx")), int(extent.get("cy"))
            width, height = record["width"] * 914400, record["height"] * 914400
            if min(width, height, old_width, old_height) <= 0:
                raise PublishError("PowerPoint image has invalid geometry")
            scale = min(1, old_width / width, old_height / height)
            width, height = round(width * scale), round(height * scale)
            offset.set("x", str(int(offset.get("x")) + round((old_width - width) / 2)))
            offset.set("y", str(int(offset.get("y")) + round((old_height - height) / 2)))
            extent.set("cx", str(width))
            extent.set("cy", str(height))
            fill = picture.find(f"{{{P}}}blipFill")
            crop = fill.find(f"{{{A}}}srcRect")
            if crop is not None:
                fill.remove(crop)
            description.set("descr", record["alt"])

    for name in members:
        if name.startswith("ppt/slides/slide") and name.endswith(".xml"):
            members[name] = xml_edit(members[name], pictures)
    write_package(path, members)


def resolve_links(ast: dict, source: Path, root: Path, repository_url: str) -> set[Path]:
    """Use explicit repository/main links, never invent publication URLs."""
    resources = set()
    for node in nodes(ast):
        if node.get("t") not in {"Link", "Image"}:
            continue
        target, title = node["c"][2]
        parsed = urlsplit(target)
        if node["t"] == "Image" and (parsed.scheme or parsed.netloc):
            raise PublishError(f"{source.relative_to(root)}: external images are not "
                               "fetched during publishing; keep reviewed assets locally")
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        local = unquote(parsed.path)
        destination = ((root / local.lstrip("/")) if local.startswith("/")
                       else source.parent / local).resolve()
        if not destination.is_relative_to(root) or not destination.exists():
            raise PublishError(f"{source.relative_to(root)}: invalid resource {target!r}")
        if node["t"] == "Image":
            if not destination.is_file():
                raise PublishError(f"Image is not a file: {target}")
            resources.add(destination)
            node["c"][2] = [str(destination), title]
        else:
            kind = "tree" if destination.is_dir() else "blob"
            url = (repository_url.rstrip("/") + f"/{kind}/main/"
                   + quote(destination.relative_to(root).as_posix(), safe="/"))
            suffix = urlsplit(url)
            node["c"][2] = [urlunsplit((suffix.scheme, suffix.netloc, suffix.path,
                                       parsed.query, parsed.fragment)), title]
    return resources


def office_checks(path: Path, ast: dict) -> dict:
    try:
        with zipfile.ZipFile(path) as package:
            bad_member = package.testzip()
            if bad_member:
                raise PublishError(f"{path.name}: corrupt ZIP member {bad_member}")
            names = package.namelist()
            xml = {}
            for name in names:
                if name.endswith((".xml", ".rels")):
                    xml[name] = ET.fromstring(package.read(name))
            required = "word/document.xml" if path.suffix == ".docx" else "ppt/presentation.xml"
            if required not in xml:
                raise PublishError(f"{path.name}: missing {required}")
            targets = {relation.get("Target") for name, root in xml.items()
                       if name.endswith(".rels") for relation in root
                       if relation.get("Type", "").endswith("/hyperlink")}
            text = " ".join(element.text or "" for root in xml.values()
                            for element in root.iter() if element.tag.endswith("}t"))
            expected = {node["c"][2][0] for node in nodes(ast)
                        if node.get("t") == "Link" and
                        urlsplit(node["c"][2][0]).scheme in {"http", "https", "mailto"}}
            missing = {url for url in expected if url not in targets and url not in text}
            if missing:
                raise PublishError(f"{path.name}: export lost reference URLs: {sorted(missing)}")
            result = {
                "zip_crc_and_xml": "passed",
                "reference_urls": len(expected),
                "hyperlinks": len(targets),
                "embedded_media": sum("/media/" in name for name in names),
                "visual_review": "not_performed",
            }
            if path.suffix == ".pptx":
                slides = [name for name in names if name.startswith("ppt/slides/slide")
                          and name.endswith(".xml")]
                expected_slides = 1 + sum(node.get("t") == "Header" and node["c"][0] == 1
                                          for node in nodes(ast["blocks"]))
                if len(slides) < expected_slides:
                    raise PublishError(f"{path.name}: expected at least {expected_slides} "
                                       f"slides; found {len(slides)}")
                size = xml[required].find("{http://schemas.openxmlformats.org/presentationml/2006/main}sldSz")
                if size is None or int(size.get("cx", "0")) * 9 != int(size.get("cy", "0")) * 16:
                    raise PublishError(f"{path.name}: presentation is not 16:9")
                result["slides"] = len(slides)
            return result
    except (OSError, zipfile.BadZipFile, ET.ParseError) as exc:
        raise PublishError(f"{path.name}: invalid Office package: {exc}") from exc


def source_provenance(root: Path, paths: set[Path], snapshot: dict[Path, str]) -> dict:
    files = [{"path": path.relative_to(root).as_posix(), "sha256": snapshot[path]}
             for path in sorted(paths)]
    digest = hashlib.sha256(json.dumps(files, sort_keys=True,
                                      separators=(",", ":")).encode()).hexdigest()
    commit, dirty = None, None
    try:
        top = Path(run(["git", "rev-parse", "--show-toplevel"], cwd=root).strip()).resolve()
        if top == root:
            commit = run(["git", "rev-parse", "HEAD"], cwd=root).strip()
            dirty = bool(run(["git", "status", "--porcelain", "--untracked-files=all",
                              "--", *[row["path"] for row in files]], cwd=root).strip())
    except PublishError:
        pass  # A fixture or a downloaded source archive need not have Git metadata.
    return {"commit": commit, "dirty": dirty, "source_bundle_sha256": digest, "files": files}


def publish(args) -> dict:
    root = args.root.resolve()
    initial_catalog = {root / name: sha256(root / name)
                       for name in ("series.json", "references/sources.json")}
    catalog, register, errors = validate(root, all_markdown=False)
    if errors:
        raise PublishError("Content validation failed:\n" + "\n".join(errors))
    selected = catalog["articles"]
    if args.article:
        requested = set(args.article)
        available = {entry["id"] for entry in selected}
        unknown = requested - available
        if unknown:
            raise PublishError(f"Unknown article selection: {', '.join(sorted(unknown))}")
        selected = [entry for entry in selected if entry["id"] in requested]
    if not selected:
        raise PublishError("The catalog selection is empty")
    output = (root / args.output).resolve()
    if (output == root or not output.is_relative_to(root)
            or output.relative_to(root).parts[0] in
            {"articles", "platform", "archive", "references", "scripts", "templates", ".github",
             ".git", "node_modules"}):
        raise PublishError("Output must be a dedicated generated directory inside the repository")
    for entry in catalog["articles"]:
        for kind in ("article", "plan", "slides"):
            if source_path(root, entry[kind]).is_relative_to(output):
                raise PublishError("Output cannot contain registered sources")
    output.mkdir(parents=True, exist_ok=True)
    for entry in selected:
        final = output / entry["id"]
        if final.is_symlink() or (final.exists() and not final.is_dir()):
            raise PublishError(f"Refusing to replace an unexpected output path: {final}")
    manifest_path = output / "release-manifest.json"
    manifest_path.unlink(missing_ok=True)
    formats = ("docx", "pptx") if args.format == "all" else (args.format,)
    references = {fmt: root / "templates" / f"reference.{fmt}" for fmt in formats}
    style_config = load_json(root / "templates/style.json")
    for reference in references.values():
        if not reference.is_file():
            raise PublishError(f"Missing template {reference}; run python3 scripts/build_templates.py")
    pandoc, pandoc_version = tool(args.pandoc, root)
    prepared, paths = {}, {root / "series.json", root / "references/sources.json",
                           root / "mermaid.lua", *references.values()}
    paths.update((root / "scripts").glob("*.py"))
    paths.update((root / "templates").glob("*.json"))
    for entry in selected:
        for kind in ("article", "plan", "slides"):
            paths.add(source_path(root, entry[kind]))
    snapshot = {path: sha256(path) for path in paths}
    if any(snapshot[path] != digest for path, digest in initial_catalog.items()):
        raise PublishError("The catalog/source register changed during validation; retry")
    mermaid_needed = False
    for entry in selected:
        for fmt in formats:
            kind = "article" if fmt == "docx" else "slides"
            source = source_path(root, entry[kind])
            try:
                ast = json.loads(run([pandoc, "--from=markdown+fenced_divs", "--to=json",
                                      str(source)], cwd=root))
            except json.JSONDecodeError as exc:
                raise PublishError(f"Pandoc returned invalid JSON for {source}") from exc
            resources = resolve_links(ast, source, root, catalog["repository_url"])
            for resource in resources - paths:
                snapshot[resource] = sha256(resource)
            paths.update(resources)
            mermaid_needed |= any(node.get("t") == "CodeBlock" and
                                  "mermaid" in node["c"][0][1] for node in nodes(ast))
            review = f"Sources reviewed {entry['reviewed']}"
            if fmt == "docx":
                remove_repeated_word_title(ast, entry["title"])
                ast["meta"]["subtitle"] = {"t": "MetaString", "c":
                                          f"{entry['id']} · {entry['status']} · {review}"}
            else:
                slide_metadata(ast, entry)
            prepared[entry["id"], fmt] = ast
    mmdc, mmdc_version = tool(args.mmdc, root) if mermaid_needed else (None, "not used")
    provenance = source_provenance(root, paths, snapshot)
    tools = {"python": sys.version.split()[0], "pandoc": pandoc_version, "mmdc": mmdc_version}
    stage = output / f".publish-{uuid.uuid4().hex}"
    stage.mkdir()
    manifest = {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "formats": list(formats),
        "selection": [entry["id"] for entry in selected],
        "repository_url": catalog["repository_url"],
        "repository_link_policy": "blob/main (repository links, not verified publication URLs)",
        "source": provenance,
        "tools": tools,
        "articles": [],
    }
    try:
        for entry in selected:
            article_dir = stage / entry["id"]
            article_dir.mkdir()
            record = {
                "id": entry["id"], "title": entry["title"], "audience": entry["audience"],
                "status": entry["status"], "reviewed": entry["reviewed"],
                "publication_url": entry["publication_url"],
                "sources": [source for source in register["sources"]
                            if source["id"] in entry["sources"]],
                "outputs": [],
            }
            for fmt in formats:
                assets = article_dir / "assets" / fmt
                assets.mkdir(parents=True)
                env = os.environ.copy()
                env.update({"PUBLISH_ASSET_DIR": str(assets),
                            "PUBLISH_MERMAID_CONFIG": str(root / "templates/mermaid.json"),
                            "PUBLISH_MMDC": mmdc or args.mmdc})
                limits = style_config["word" if fmt == "docx" else "slides"]
                env["PUBLISH_IMAGE_MAX_WIDTH"] = str(limits["image_max_width_inches"])
                env["PUBLISH_IMAGE_MAX_HEIGHT"] = str(limits["image_max_height_inches"])
                image_layout = assets / "image-layout.jsonl"
                env["PUBLISH_IMAGE_LAYOUT"] = str(image_layout)
                browser_settings = {}
                if args.puppeteer_config:
                    config = (root / args.puppeteer_config).resolve()
                    if not config.is_file():
                        raise PublishError(f"Missing Puppeteer configuration: {config}")
                    browser_settings = json.loads(config.read_text(encoding="utf-8"))
                    if not isinstance(browser_settings, dict):
                        raise PublishError("Puppeteer configuration must be a JSON object")
                browser_settings["userDataDir"] = str(assets / "browser-profile")
                browser_config = assets / "puppeteer.json"
                browser_config.write_text(json.dumps(browser_settings), encoding="utf-8")
                env["PUBLISH_PUPPETEER_CONFIG"] = str(browser_config)
                ast = prepared[entry["id"], fmt]
                name = f"{entry['id']}.{fmt}"
                destination = article_dir / name
                command = [pandoc, "--from=json", f"--to={fmt}", "--standalone",
                           f"--reference-doc={references[fmt]}",
                           f"--lua-filter={root / 'mermaid.lua'}", f"--output={destination}"]
                if fmt == "pptx":
                    command.append("--slide-level=1")
                run(command, cwd=article_dir, env=env, input_text=json.dumps(ast))
                if fmt == "docx":
                    try:
                        word_code_fonts(destination, style_config)
                    except (zipfile.BadZipFile, ET.ParseError) as exc:
                        raise PublishError(f"Invalid Word package before code formatting: {exc}") from exc
                else:
                    pptx_image_geometry(destination, image_layout)
                image_layout.unlink(missing_ok=True)
                if (assets / "browser-profile").exists():
                    shutil.rmtree(assets / "browser-profile")
                browser_config.unlink()
                checks = office_checks(destination, ast)
                record["outputs"].append({
                    "path": f"{entry['id']}/{name}", "sha256": sha256(destination),
                    "bytes": destination.stat().st_size, "checks": checks,
                })
                print(f"Published {entry['id']}/{name}")
            record["diagrams"] = [
                {"path": f"{entry['id']}/{p.relative_to(article_dir).as_posix()}",
                 "sha256": sha256(p)}
                for p in sorted(article_dir.rglob("*.png"))
            ]
            (article_dir / "metadata.json").write_text(
                json.dumps({**record, "source": provenance, "tools": tools}, indent=2) + "\n",
                encoding="utf-8")
            manifest["articles"].append(record)
        changed = [row["path"] for row in provenance["files"]
                   if sha256(root / row["path"]) != row["sha256"]]
        if changed:
            raise PublishError(f"Sources changed during export; retry a stable snapshot: {changed}")
        staged_manifest = stage / "release-manifest.json"
        staged_manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        for entry in selected:
            final = output / entry["id"]
            if final.is_symlink() or (final.exists() and not final.is_dir()):
                raise PublishError(f"Refusing to replace an unexpected output path: {final}")
            if final.exists():
                shutil.rmtree(final)
            (stage / entry["id"]).replace(final)
        staged_manifest.replace(manifest_path)
    finally:
        shutil.rmtree(stage)
    print(f"Release manifest: {manifest_path.relative_to(root)}")
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--article", action="append", help="Stable catalog ID; may be repeated")
    parser.add_argument("--format", choices=("docx", "pptx", "all"), default="all")
    parser.add_argument("--output", type=Path, default=Path("build"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--pandoc", default=os.environ.get("PANDOC", "pandoc"))
    parser.add_argument("--mmdc", default=os.environ.get("MMDC", "mmdc"))
    parser.add_argument("--puppeteer-config", type=Path,
                        help="Optional local Chromium/Puppeteer configuration JSON")
    args = parser.parse_args(argv)
    try:
        publish(args)
    except (ContentError, PublishError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
