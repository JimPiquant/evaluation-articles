"""Shared, dependency-free catalog and Markdown checks."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import unicodedata
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

STATUSES = {"planned", "draft", "review", "ready", "published"}
AUDIENCES = {"leaders", "developers", "operators", "architects"}
EXCLUDED = {"archive", "archived", "build", "generated", "docx", "node_modules",
            ".git", "__pycache__", ".fixtures", ".venv", "venv", ".sdk-cache",
            ".cache", ".pytest_cache", ".ruff_cache", "site-packages"}
PLAN_HEADINGS = {"purpose", "audience", "outline", "references"}


class ContentError(ValueError):
    pass


def load_json(path: Path) -> dict:
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ContentError(f"{path}: duplicate JSON key {key!r}")
            result[key] = value
        return result

    try:
        data = json.loads(path.read_text(encoding="utf-8"),
                          object_pairs_hook=unique_object)
    except (OSError, json.JSONDecodeError) as exc:
        raise ContentError(f"{path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ContentError(f"{path}: expected a JSON object")
    return data


def valid_date(value) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        dt.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def valid_url(value) -> bool:
    if not isinstance(value, str) or re.search(r"\s", value):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme in {"https", "http"} and bool(parsed.hostname)
    except ValueError:
        return False


def source_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ContentError("source path must be a nonempty repository-relative string")
    path = PurePosixPath(value)
    if (path.is_absolute() or ".." in path.parts or "\\" in value
            or any(part in EXCLUDED for part in path.parts)):
        raise ContentError(f"unsafe or excluded source path: {value}")
    resolved = (root / value).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ContentError(f"source path escapes the repository: {value}")
    if not resolved.is_file():
        raise ContentError(f"missing source: {value}")
    return resolved


def frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Accept the repository's scalar frontmatter, not arbitrary YAML."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ContentError("missing opening frontmatter delimiter")
    end = next((i for i in range(1, len(lines))
                if lines[i].strip() in {"---", "..."}), None)
    if end is None:
        raise ContentError("unclosed frontmatter")
    metadata = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z][\w-]*):\s*(.*?)\s*", line)
        if not match:
            raise ContentError("frontmatter must use one-line scalar key: value fields")
        key, value = match.groups()
        if key in metadata:
            raise ContentError(f"duplicate frontmatter field: {key}")
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ContentError(f"invalid quoted frontmatter field: {key}") from exc
            if not isinstance(value, str):
                raise ContentError(f"frontmatter field must be a string: {key}")
        elif value.startswith("'"):
            if not value.endswith("'") or len(value) < 2:
                raise ContentError(f"unclosed quoted frontmatter field: {key}")
            value = value[1:-1].replace("''", "'")
        else:
            value = re.split(r"\s+#", value, maxsplit=1)[0].strip()
        metadata[key] = value
    return metadata, "\n".join(lines[end + 1:])


def prose(text: str, *, mask_inline_code: bool = True) -> str:
    """Ignore frontmatter and code when looking for headings and links."""
    if text.startswith("---\n"):
        _, text = frontmatter(text)
    result = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            result.append("")
        elif fence is None and not line.startswith(("    ", "\t")):
            result.append(re.sub(r"(`+).*?\1", "", line) if mask_inline_code else line)
        else:
            result.append("")
    return "\n".join(result)


def headings(text: str) -> list[tuple[int, str]]:
    return [(len(match.group(1)), match.group(2).rstrip("# ").strip())
            for match in re.finditer(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$",
                                     prose(text, mask_inline_code=False), re.MULTILINE)]


def anchors(text: str) -> set[str]:
    result, counts = set(), {}
    for _, heading in headings(text):
        explicit = re.search(r"\{#([\w-]+)(?:\s[^}]*)?\}\s*$", heading)
        if explicit:
            result.add(explicit.group(1))
            heading = heading[:explicit.start()]
        heading = re.sub(r"!?\[([^\]]+)\]\([^)]*\)", r"\1", heading)
        heading = re.sub(r"\[([^\]]+)\]\[[^\]]*\]", r"\1", heading)
        heading = re.sub(r"(`+)(.*?)\1", r"\2", heading)
        heading = re.sub(r"(\*{1,2}|_{1,2}|~~)(.*?)\1", r"\2", heading)
        heading = re.sub(r"<[^>]+>", "", heading).lower().strip()
        slug = "".join(c for c in heading
                       if c in {"-", "_", " "} or unicodedata.category(c)[0] in {"L", "N"})
        slug = slug.replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        result.add(f"{slug}-{count}" if count else slug)
    result.update(re.findall(r"\b(?:id|name)=[\"']([^\"']+)[\"']", prose(text)))
    return result


def markdown_links(text: str) -> tuple[list[str], list[str]]:
    """Extract inline/reference/autolinks, including balanced URL parentheses."""
    text = prose(text)
    links, undefined = [], []
    definitions = {}
    for match in re.finditer(r"^\s{0,3}\[([^\]\n]+)\]:\s*(<[^>\n]+>|\S+)",
                             text, re.MULTILINE):
        label, target = match.groups()
        if not label.startswith("^"):
            definitions[label.casefold()] = target.strip("<>")
            links.append(target.strip("<>"))
    for match in re.finditer(r"!?\[[^\]\n]*\]\(", text):
        start, depth, end = match.end(), 1, match.end()
        while end < len(text) and depth:
            if text[end] == "\\":
                end += 2
                continue
            if text[end] == "(":
                depth += 1
            elif text[end] == ")":
                depth -= 1
            end += 1
        if depth:
            undefined.append("unclosed inline link")
            continue
        target = text[start:end - 1].strip()
        if target.startswith("<"):
            close = target.find(">")
            target = target[1:close] if close >= 0 else target
        else:
            target = re.split(r"\s+[\"']", target, maxsplit=1)[0]
        links.append(target)
    for match in re.finditer(r"!?\[([^\]\n]+)\]\[([^\]\n]*)\]", text):
        label = (match.group(2) or match.group(1)).casefold()
        if label not in definitions and not label.startswith("^"):
            undefined.append(label)
    links.extend(re.findall(r"<((?:https?://|mailto:)[^>\n]+)>", text))
    links.extend(re.findall(r"\b(?:href|src)=[\"']([^\"']+)[\"']", text))
    return links, undefined


def validate_links(root: Path, path: Path) -> list[str]:
    errors = []
    if not path.resolve().is_relative_to(root):
        return [f"{path.relative_to(root)}: Markdown symlink escapes the repository"]
    text = path.read_text(encoding="utf-8")
    links, undefined = markdown_links(text)
    errors.extend(f"{path.relative_to(root)}: undefined reference {label!r}"
                  for label in undefined)
    for target in links:
        label = f"{path.relative_to(root)}: link {target!r}"
        try:
            parsed = urlsplit(target)
        except ValueError:
            errors.append(f"{label}: malformed URL")
            continue
        if not target or re.search(r"\s", target):
            errors.append(f"{label}: empty or whitespace-containing target")
        elif parsed.scheme in {"http", "https"}:
            if not valid_url(target):
                errors.append(f"{label}: malformed external URL")
        elif parsed.scheme == "mailto":
            if "@" not in parsed.path:
                errors.append(f"{label}: malformed email address")
        elif parsed.scheme or parsed.netloc:
            errors.append(f"{label}: unsupported URL scheme")
        else:
            local = unquote(parsed.path)
            destination = ((root / local.lstrip("/")) if local.startswith("/")
                           else path.parent / local).resolve() if local else path
            if not destination.is_relative_to(root):
                errors.append(f"{label}: target escapes the repository")
            elif any(part in EXCLUDED for part in destination.relative_to(root).parts):
                continue
            elif not destination.exists():
                errors.append(f"{label}: missing local target")
            elif parsed.fragment and destination.suffix == ".md":
                if unquote(parsed.fragment) not in anchors(destination.read_text(encoding="utf-8")):
                    errors.append(f"{label}: missing heading anchor")
    return errors


def validate_catalog(root: Path) -> tuple[dict, dict, list[str]]:
    root = root.resolve()
    catalog = load_json(root / "series.json")
    register = load_json(root / "references/sources.json")
    errors = []
    if type(catalog.get("schema_version")) is not int or catalog["schema_version"] != 1:
        errors.append("series.json: schema_version must be 1")
    if not valid_url(catalog.get("repository_url")):
        errors.append("series.json: repository_url must be an HTTP(S) repository URL")
    elif urlsplit(catalog["repository_url"]).query or urlsplit(catalog["repository_url"]).fragment:
        errors.append("series.json: repository_url must not have a query or fragment")
    sources = register.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("references/sources.json: sources must be a nonempty list")
        sources = []
    known_sources = set()
    for source in sources:
        if not isinstance(source, dict):
            errors.append("references/sources.json: each source must be an object")
            continue
        sid = source.get("id")
        if not isinstance(sid, str) or not re.fullmatch(r"[A-Z]\d{2,}", sid):
            errors.append(f"references/sources.json: invalid source ID {sid!r}")
            continue
        if sid in known_sources:
            errors.append(f"references/sources.json: duplicate source ID {sid}")
        known_sources.add(sid)
        if not valid_url(source.get("url")):
            errors.append(f"{sid}: missing or invalid source URL")
        if not isinstance(source.get("authority"), str) or not source["authority"].strip():
            errors.append(f"{sid}: missing source authority")
        if not valid_date(source.get("reviewed")):
            errors.append(f"{sid}: reviewed must be an ISO calendar date")
    entries = catalog.get("articles")
    if not isinstance(entries, list) or not entries:
        errors.append("series.json: articles must be a nonempty list")
        entries = []
    ids, paths = set(), set()
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("series.json: each article must be an object")
            continue
        eid = entry.get("id")
        if not isinstance(eid, str) or not re.fullmatch(r"[EP]\d{2}", eid):
            errors.append(f"series.json: invalid article ID {eid!r}")
        elif eid in ids:
            errors.append(f"series.json: duplicate article ID {eid}")
        else:
            ids.add(eid)
        if not isinstance(entry.get("title"), str) or not entry["title"].strip():
            errors.append(f"{eid}: missing title")
        if not isinstance(entry.get("audience"), str) or entry["audience"] not in AUDIENCES:
            errors.append(f"{eid}: audience must be one of {sorted(AUDIENCES)}")
        if not isinstance(entry.get("status"), str) or entry["status"] not in STATUSES:
            errors.append(f"{eid}: status must be one of {sorted(STATUSES)}")
        if not valid_date(entry.get("reviewed")):
            errors.append(f"{eid}: reviewed must be an ISO calendar date")
        publication_url = entry.get("publication_url")
        if "publication_url" not in entry:
            errors.append(f"{eid}: publication_url must be explicitly null or a URL")
        elif publication_url is not None and not valid_url(publication_url):
            errors.append(f"{eid}: invalid publication_url")
        if entry.get("status") == "published" and not valid_url(publication_url):
            errors.append(f"{eid}: published status requires a publication_url")
        source_ids = entry.get("sources")
        if not isinstance(source_ids, list) or not source_ids:
            errors.append(f"{eid}: sources must be a nonempty list of registered IDs")
        else:
            if not all(isinstance(sid, str) for sid in source_ids):
                errors.append(f"{eid}: every source ID must be a string")
            else:
                if len(set(source_ids)) != len(source_ids):
                    errors.append(f"{eid}: duplicate source IDs")
                for sid in source_ids:
                    if sid not in known_sources:
                        errors.append(f"{eid}: unknown source ID {sid!r}")
        for kind in ("article", "plan", "slides"):
            value = entry.get(kind)
            try:
                path = source_path(root, value)
                if path in paths:
                    errors.append(f"{eid}: duplicate registered source path {value}")
                paths.add(path)
                if path.suffix != ".md":
                    errors.append(f"{eid}: {kind} must be Markdown: {value}")
                if kind == "plan" and not value.endswith(".plan.md"):
                    errors.append(f"{eid}: plan path must end with .plan.md")
                if kind == "slides" and not value.endswith(".slides.md"):
                    errors.append(f"{eid}: slides path must end with .slides.md")
                text = path.read_text(encoding="utf-8")
                if kind == "plan":
                    missing = PLAN_HEADINGS - {h.casefold() for _, h in headings(text)}
                    if missing:
                        errors.append(f"{eid}: {value}: missing plan sections {sorted(missing)}")
                else:
                    metadata, body = frontmatter(text)
                    required = {"title", "author", "date",
                                "description" if kind == "article" else "subtitle"}
                    for field in sorted(required):
                        if not metadata.get(field, "").strip():
                            errors.append(f"{eid}: {value}: missing metadata {field}")
                    if not valid_date(metadata.get("date")):
                        errors.append(f"{eid}: {value}: date must be an ISO calendar date")
                    if kind == "article" and metadata.get("title") != entry.get("title"):
                        errors.append(f"{eid}: article and catalog titles differ")
                    if not headings(body):
                        errors.append(f"{eid}: {value}: missing headings")
                    if kind == "slides" and not any(level == 1 for level, _ in headings(body)):
                        errors.append(f"{eid}: slide boundaries must be H1 headings")
            except (ContentError, OSError, UnicodeError) as exc:
                errors.append(f"{eid}: {kind}: {exc}")
    return catalog, register, errors


def validate(root: Path, *, all_markdown: bool = True) -> tuple[dict, dict, list[str]]:
    root = root.resolve()
    catalog, register, errors = validate_catalog(root)
    if all_markdown:
        files = []
        for directory, folders, names in os.walk(root):
            folders[:] = sorted(folder for folder in folders if folder not in EXCLUDED)
            files.extend(Path(directory) / name for name in sorted(names)
                         if name.endswith(".md"))
    else:
        files = []
        for entry in catalog.get("articles", []):
            if isinstance(entry, dict):
                for kind in ("article", "plan", "slides"):
                    try:
                        files.append(source_path(root, entry.get(kind)))
                    except ContentError:
                        pass
    for path in files:
        try:
            errors.extend(validate_links(root, path))
        except (ContentError, OSError, UnicodeError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
    return catalog, register, errors
