#!/usr/bin/env python3
"""Derive branded Office reference packages from Pandoc's bundled defaults."""

from __future__ import annotations

import argparse
import io
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
CHILD_ORDER = {
    tag_name: order.split() for tag_name, order in {
        f"{{{W}}}style": "name aliases basedOn next link autoRedefine hidden uiPriority semiHidden unhideWhenUsed qFormat locked personal personalCompose personalReply rsid pPr rPr tblPr trPr tcPr tblStylePr",
        f"{{{W}}}pPr": "pStyle keepNext keepLines pageBreakBefore framePr widowControl numPr suppressLineNumbers pBdr shd tabs suppressAutoHyphens kinsoku wordWrap overflowPunct topLinePunct autoSpaceDE autoSpaceDN bidi adjustRightInd snapToGrid spacing ind contextualSpacing mirrorIndents suppressOverlap jc textDirection textAlignment textboxTightWrap outlineLvl divId cnfStyle rPr sectPr pPrChange",
        f"{{{W}}}rPr": "rStyle rFonts b bCs i iCs caps smallCaps strike dstrike outline shadow emboss imprint noProof snapToGrid vanish webHidden color spacing w kern position sz szCs highlight u effect bdr shd fitText vertAlign rtl cs em lang eastAsianLayout specVanish oMath rPrChange",
        f"{{{W}}}sectPr": "headerReference footerReference footnotePr endnotePr type pgSz pgMar paperSrc pgBorders lnNumType pgNumType cols formProt vAlign noEndnote titlePg textDirection bidi rtlGutter docGrid printerSettings sectPrChange",
        f"{{{W}}}tblPr": "tblStyle tblpPr tblOverlap bidiVisual tblStyleRowBandSize tblStyleColBandSize tblW jc tblCellSpacing tblInd tblBorders shd tblLayout tblCellMar tblLook tblCaption tblDescription tblPrChange",
        f"{{{W}}}tblStylePr": "pPr rPr tblPr trPr tcPr",
        f"{{{A}}}rPr": "ln noFill solidFill gradFill blipFill pattFill grpFill effectLst effectDag highlight latin ea cs sym hlinkClick hlinkMouseOver rtl extLst",
        f"{{{A}}}defRPr": "ln noFill solidFill gradFill blipFill pattFill grpFill effectLst effectDag highlight latin ea cs sym hlinkClick hlinkMouseOver rtl extLst",
        f"{{{P}}}spPr": "xfrm custGeom prstGeom noFill solidFill gradFill blipFill pattFill grpFill ln effectLst effectDag scene3d sp3d extLst",
    }.items()
}


def tag(namespace, name):
    return f"{{{namespace}}}{name}"


def element(parent, namespace, name, **attrs):
    child = parent.find(tag(namespace, name))
    if child is None:
        child = ET.SubElement(parent, tag(namespace, name))
    child.attrib.update({tag(namespace, key) if namespace == W else key: str(value)
                         for key, value in attrs.items()})
    return child


def xml_edit(data, edit):
    namespaces = dict(value for _, value in ET.iterparse(io.BytesIO(data), events=["start-ns"]))
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)
    root = ET.fromstring(data)
    edit(root)
    # Office schemas prescribe child order even when XML parsers accept anything.
    for node in root.iter():
        if node.tag in CHILD_ORDER:
            order = CHILD_ORDER[node.tag]
            node[:] = sorted(node, key=lambda child:
                             order.index(child.tag.split("}")[-1])
                             if child.tag.split("}")[-1] in order else len(order))
    serialized = ET.tostring(root, encoding="unicode")
    for prefix, uri in namespaces.items():
        if prefix and f'xmlns:{prefix}=' not in serialized:
            root.set(f"xmlns:{prefix}", uri)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def word_styles(root, config):
    settings, colors = config["word"], config["colors"]
    defaults = element(root, W, "docDefaults")
    normal = element(element(defaults, W, "rPrDefault"), W, "rPr")
    element(normal, W, "rFonts", ascii=config["font"], hAnsi=config["font"])
    element(normal, W, "sz", val=int(settings["body_points"] * 2))
    element(normal, W, "color", val=colors["ink"])
    styles = {s.get(tag(W, "styleId")): s for s in root.findall(tag(W, "style"))}
    for name, points, color in [
        ("Normal", settings["body_points"], colors["ink"]),
        ("BodyText", settings["body_points"], colors["ink"]),
        ("Title", settings["title_points"], colors["ink"]),
        ("Subtitle", 14, colors["muted"]),
        ("Author", 11, colors["muted"]), ("Date", 11, colors["muted"]),
        ("Heading1", settings["heading_points"][0], colors["ink"]),
        ("Heading2", settings["heading_points"][1], colors["accent"]),
        ("Heading3", settings["heading_points"][2], colors["ink"]),
    ]:
        style = styles[name]
        rpr = element(style, W, "rPr")
        element(rpr, W, "rFonts", ascii=config["font"], hAnsi=config["font"])
        element(rpr, W, "sz", val=int(points * 2))
        element(rpr, W, "color", val=color)
        ppr = element(style, W, "pPr")
        if name.startswith("Heading"):
            element(rpr, W, "b")
            element(ppr, W, "keepNext")
            element(ppr, W, "spacing", before=240, after=120)
        else:
            element(ppr, W, "spacing", after=140, line=276, lineRule="auto")
        element(ppr, W, "widowControl")
    source = ET.SubElement(root, tag(W, "style"),
                           {tag(W, "type"): "paragraph", tag(W, "styleId"): "SourceCode"})
    element(source, W, "name", val="Source Code")
    element(source, W, "basedOn", val="Normal")
    ppr = element(source, W, "pPr")
    element(ppr, W, "shd", val="clear", fill=colors["surface"])
    element(ppr, W, "spacing", before=80, after=80, line=240, lineRule="auto")
    for style in (source, styles["VerbatimChar"]):
        rpr = element(style, W, "rPr")
        element(rpr, W, "rFonts", ascii=config["code_font"], hAnsi=config["code_font"],
                eastAsia=config["code_font"], cs=config["code_font"])
        element(rpr, W, "sz", val=int(settings["code_points"] * 2))
    rpr = element(styles["Hyperlink"], W, "rPr")
    element(rpr, W, "color", val=colors["link"])
    element(rpr, W, "u", val="single")
    table = styles["Table"]
    rpr = element(table, W, "rPr")
    element(rpr, W, "sz", val=20)
    table_properties = element(table, W, "tblPr")
    borders = element(table_properties, W, "tblBorders")
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element(borders, W, side, val="single", sz=4, color="D6E0E8")
    first = next((child for child in table.findall(tag(W, "tblStylePr"))
                  if child.get(tag(W, "type")) == "firstRow"), None)
    if first is None:
        first = ET.SubElement(table, tag(W, "tblStylePr"), {tag(W, "type"): "firstRow"})
    element(element(first, W, "tcPr"), W, "shd", val="clear", fill=colors["surface"])
    element(element(first, W, "rPr"), W, "b")


def word_document(root, config):
    section = root.find(f".//{tag(W, 'sectPr')}")
    margin = config["word"]["margin_twips"]
    element(section, W, "pgSz", w=12240, h=15840)
    element(section, W, "pgMar", top=margin, right=margin, bottom=margin,
            left=margin, header=720, footer=720, gutter=0)
    ET.SubElement(section, tag(W, "footerReference"),
                  {tag(W, "type"): "default", tag(R, "id"): "rIdFieldGuideFooter"})


def footer(config):
    root = ET.Element(tag(W, "ftr"))
    paragraph = ET.SubElement(root, tag(W, "p"))
    tabs = element(element(paragraph, W, "pPr"), W, "tabs")
    ET.SubElement(tabs, tag(W, "tab"), {tag(W, "val"): "right", tag(W, "pos"): "9360"})
    run = ET.SubElement(paragraph, tag(W, "r"))
    rpr = element(run, W, "rPr")
    element(rpr, W, "rFonts", ascii=config["font"], hAnsi=config["font"])
    element(rpr, W, "sz", val=16)
    element(rpr, W, "color", val=config["colors"]["muted"])
    ET.SubElement(run, tag(W, "t")).text = config["brand"]
    ET.SubElement(ET.SubElement(paragraph, tag(W, "r")), tag(W, "tab"))
    field = ET.SubElement(paragraph, tag(W, "fldSimple"), {tag(W, "instr"): " PAGE "})
    ET.SubElement(ET.SubElement(field, tag(W, "r")), tag(W, "t")).text = "1"
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def theme(root, config):
    colors = config["colors"]
    scheme = root.find(f".//{tag(A, 'clrScheme')}")
    scheme.set("name", config["brand"])
    for name, color in {"dk1": colors["ink"], "dk2": colors["ink"], "lt1": "FFFFFF",
                        "lt2": colors["surface"], "accent1": colors["accent"],
                        "accent2": colors["link"], "accent3": "6B8F71",
                        "accent4": "8B6DA8", "accent5": "D98E32", "accent6": "C45A52",
                        "hlink": colors["link"], "folHlink": "765B93"}.items():
        slot = scheme.find(tag(A, name))
        slot.clear()
        ET.SubElement(slot, tag(A, "srgbClr"), {"val": color})
    font_scheme = root.find(f".//{tag(A, 'fontScheme')}")
    font_scheme.set("name", config["brand"])
    for latin in font_scheme.findall(f".//{tag(A, 'latin')}"):
        latin.set("typeface", config["font"])


def paint_run(run, config, points, *, title=False):
    run.set("sz", str(int(points * 100)))
    if title:
        run.set("b", "1")
    fill = element(run, A, "solidFill")
    fill.clear()
    ET.SubElement(fill, tag(A, "srgbClr"), {"val": config["colors"]["ink"]})
    element(run, A, "latin", typeface=config["font"])


def slide_typography(root, config):
    settings = config["slides"]
    cover = any(node.get("type") == "ctrTitle" for node in root.findall(f".//{tag(P, 'ph')}"))
    for shape in root.findall(f".//{tag(P, 'sp')}"):
        placeholder = shape.find(f".//{tag(P, 'ph')}")
        if placeholder is None:
            continue
        kind = placeholder.get("type", "body")
        if kind in {"title", "ctrTitle"}:
            points = settings["cover_points"] if kind == "ctrTitle" else settings["title_points"]
        elif kind == "subTitle":
            points = settings["subtitle_points"]
        elif kind == "dt" and cover:
            points = settings["review_points"]
        elif kind in {"dt", "ftr", "sldNum"}:
            points = 10
        else:
            points = settings["body_points"]
        for run in shape.findall(f".//{tag(A, 'defRPr')}") + shape.findall(f".//{tag(A, 'rPr')}"):
            paint_run(run, config, points, title=kind in {"title", "ctrTitle"})
        if kind in {"title", "ctrTitle"}:
            transform = element(element(shape, P, "spPr"), A, "xfrm")
            element(transform, A, "off", x=548640, y=1097280 if kind == "ctrTitle" else 292608)
            element(transform, A, "ext", cx=8046720, cy=1463040 if kind == "ctrTitle" else 804672)
        rectangle = None
        if cover:
            rectangle = {
                "ctrTitle": settings["cover_title_inches"],
                "subTitle": settings["cover_subtitle_inches"],
                "dt": settings["cover_review_inches"],
            }.get(kind)
        if rectangle:
            x, y, width, height = [round(value * 914400) for value in rectangle]
            transform = element(element(shape, P, "spPr"), A, "xfrm")
            element(transform, A, "off", x=x, y=y)
            element(transform, A, "ext", cx=width, cy=height)
            body = element(shape, P, "txBody")
            properties = element(body, A, "bodyPr", wrap="square", anchor="ctr",
                                 lIns=0, rIns=0, tIns=0, bIns=0)
            for child in list(properties):
                if child.tag in {tag(A, "noAutofit"), tag(A, "normAutofit"), tag(A, "spAutoFit")}:
                    properties.remove(child)
            ET.SubElement(properties, tag(A, "noAutofit"))
            level = element(element(body, A, "lstStyle"), A, "lvl1pPr", algn="ctr")
            paint_run(element(level, A, "defRPr"), config, points, title=kind == "ctrTitle")
    styles = root.find(tag(P, "txStyles"))
    if styles is not None:
        for style in styles:
            for run in style.findall(f".//{tag(A, 'defRPr')}"):
                paint_run(run, config, settings["title_points"] if style.tag == tag(P, "titleStyle")
                          else settings["body_points"], title=style.tag == tag(P, "titleStyle"))


def brand_master(root, config):
    slide_typography(root, config)
    tree = root.find(f".//{tag(P, 'spTree')}")
    ids = [int(node.get("id", "0")) for node in tree.findall(f".//{tag(P, 'cNvPr')}")]
    next_id = max(ids, default=0) + 1
    for name, x, y, width, height, color, text in [
        ("Field guide accent", 0, 0, 9144000, 73152, config["colors"]["accent"], None),
        ("Field guide footer", 548640, 4882896, 8046720, 219456, None, config["brand"]),
    ]:
        shape = ET.SubElement(tree, tag(P, "sp"))
        nv = ET.SubElement(shape, tag(P, "nvSpPr"))
        ET.SubElement(nv, tag(P, "cNvPr"), {"id": str(next_id), "name": name})
        ET.SubElement(nv, tag(P, "cNvSpPr"))
        ET.SubElement(nv, tag(P, "nvPr"))
        next_id += 1
        properties = ET.SubElement(shape, tag(P, "spPr"))
        transform = ET.SubElement(properties, tag(A, "xfrm"))
        ET.SubElement(transform, tag(A, "off"), {"x": str(x), "y": str(y)})
        ET.SubElement(transform, tag(A, "ext"), {"cx": str(width), "cy": str(height)})
        geom = ET.SubElement(properties, tag(A, "prstGeom"), {"prst": "rect"})
        ET.SubElement(geom, tag(A, "avLst"))
        if color:
            fill = ET.SubElement(properties, tag(A, "solidFill"))
            ET.SubElement(fill, tag(A, "srgbClr"), {"val": color})
        else:
            ET.SubElement(properties, tag(A, "noFill"))
        line = ET.SubElement(properties, tag(A, "ln"))
        ET.SubElement(line, tag(A, "noFill"))
        if text:
            body = ET.SubElement(shape, tag(P, "txBody"))
            ET.SubElement(body, tag(A, "bodyPr"), {"lIns": "0", "rIns": "0",
                                                 "tIns": "0", "bIns": "0"})
            ET.SubElement(body, tag(A, "lstStyle"))
            paragraph = ET.SubElement(body, tag(A, "p"))
            run = ET.SubElement(paragraph, tag(A, "r"))
            paint_run(ET.SubElement(run, tag(A, "rPr")), config, 9)
            ET.SubElement(run, tag(A, "t")).text = text


def write_package(path: Path, members: dict[str, bytes]):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            package.writestr(info, data)


def build(root: Path, pandoc: str):
    config = json.loads((root / "templates/style.json").read_text(encoding="utf-8"))
    for fmt in ("docx", "pptx"):
        data = subprocess.run([pandoc, "--print-default-data-file", f"reference.{fmt}"],
                              check=True, capture_output=True).stdout
        with zipfile.ZipFile(io.BytesIO(data)) as package:
            members = {name: package.read(name) for name in package.namelist()}
        if fmt == "docx":
            members["word/styles.xml"] = xml_edit(
                members["word/styles.xml"], lambda r: word_styles(r, config))
            members["word/document.xml"] = xml_edit(
                members["word/document.xml"], lambda r: word_document(r, config))
            members["word/footer-field-guide.xml"] = footer(config)
            members["word/_rels/document.xml.rels"] = xml_edit(
                members["word/_rels/document.xml.rels"], lambda r: ET.SubElement(
                    r, tag(REL, "Relationship"), {"Id": "rIdFieldGuideFooter",
                                                "Type": f"{R}/footer",
                                                "Target": "footer-field-guide.xml"}))
            members["[Content_Types].xml"] = xml_edit(
                members["[Content_Types].xml"], lambda r: ET.SubElement(
                    r, tag(CT, "Override"), {"PartName": "/word/footer-field-guide.xml",
                                            "ContentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"}))
        else:
            for name in list(members):
                if name.startswith("ppt/theme/") and name.endswith(".xml"):
                    members[name] = xml_edit(members[name], lambda r: theme(r, config))
                elif name.startswith("ppt/slideMasters/") and name.endswith(".xml"):
                    members[name] = xml_edit(members[name], lambda r: brand_master(r, config))
                elif name.startswith("ppt/slideLayouts/") and name.endswith(".xml"):
                    members[name] = xml_edit(members[name], lambda r: slide_typography(r, config))
            def size(r):
                element(r, P, "sldSz", cx=config["slides"]["width_emu"],
                        cy=config["slides"]["height_emu"], type="screen16x9")
            members["ppt/presentation.xml"] = xml_edit(members["ppt/presentation.xml"], size)
        destination = root / "templates" / f"reference.{fmt}"
        write_package(destination, members)
        print(f"Built {destination.relative_to(root)}")
    version = subprocess.run([pandoc, "--version"], check=True, capture_output=True,
                             text=True).stdout.splitlines()[0]
    (root / "templates/provenance.json").write_text(
        json.dumps({"pandoc": version, "generator": "scripts/build_templates.py",
                    "configuration": "templates/style.json",
                    "upstream": "Pandoc bundled reference.docx/reference.pptx",
                    "zip_member_timestamp": "2000-01-01T00:00:00"}, indent=2) + "\n",
        encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--pandoc", default="pandoc")
    args = parser.parse_args(argv)
    executable = shutil.which(args.pandoc)
    if not executable:
        parser.error(f"Required tool is missing: {args.pandoc}")
    try:
        build(args.root.resolve(), executable)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: template generation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
