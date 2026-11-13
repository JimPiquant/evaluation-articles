# Catalog-driven publishing

The catalog in `series.json` is the sole publication inventory. An entry registers
an article, its companion plan, and a separately maintained presentation outline.
Archived material and generated exports are not current editorial sources.

## Validate and publish

```sh
python3 scripts/check_content.py
python3 -m unittest discover -s scripts/tests -v
python3 scripts/publish.py
python3 scripts/publish.py --article E02 --format all --output build
./generate-docx.sh --article E02
```

Python 3.9+ is sufficient for validation and orchestration; no Python packages
are required. Publishing additionally requires [Pandoc](https://pandoc.org/) and,
for Mermaid blocks, [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli) with
a working Chromium/Puppeteer installation. Local development was exercised with
Pandoc 3.13 and Mermaid CLI 11.12.0. The CI workflow records its actual versions.
If tools are not on `PATH`, use `--pandoc /path/to/pandoc` and
`--mmdc /path/to/mmdc`, or the `PANDOC` and `MMDC` environment variables.

`--article` accepts stable IDs and may be repeated. `--format` accepts `docx`,
`pptx`, or `all` (the default); omitting a selection publishes every catalog entry,
including clearly labeled drafts. The compatibility wrapper always selects Word
and otherwise forwards publisher flags; old numbered-folder arguments are retired.
Run the validator before sharing exports. Exporting a draft is not publication
approval and never changes catalog status or a publication URL.

## Validation contract

- Schema version 1; unique `E00`–`E99` / `P00`–`P99` IDs and registered source
  paths; audiences `leaders`, `developers`, `operators`, or `architects`.
- Statuses `planned`, `draft`, `review`, `ready`, or `published`. Published
  entries require a real, explicitly supplied `publication_url`; other entries
  record it as `null` until known.
- Every entry has an existing Markdown article, `.plan.md`, and `.slides.md`.
  Plans contain Purpose, Audience, Outline, and References headings.
- Article frontmatter requires title, description, author, and date. Presentation
  frontmatter requires title, subtitle, author, and date. Frontmatter uses
  one-line scalar fields, with JSON-style double quotes or YAML-style single
  quotes when needed; lists and multiline YAML are not supported by the checker.
  Dates and source-review dates are ISO calendar dates. Article/catalog titles match.
- Source IDs refer to unique IDs in `references/sources.json`; each source has
  a URL, authority, and review date. Optional source `revision` fields are
  retained in release provenance.
- Maintained Markdown links resolve to local files and heading anchors.
  Fenced/inline code is ignored. `archive/`, `build/`, `generated/`, legacy
  `docx/`, dependency directories (including `.venv/` and `.sdk-cache/`), and
  test fixtures are excluded and are not traversed.

Checks are **offline**: HTTP(S) URL syntax is checked, but external availability,
the truth of product claims, and live publication URLs are not certified.
Publishing checks registered content only; the standalone validator also scans
other maintained Markdown. For isolated fixtures both commands accept `--root`.

## Export and release policy

Each article gets `build/<ID>/<ID>.docx`, `<ID>.pptx`, and `metadata.json`.
`build/release-manifest.json` describes **only the requested selection and
formats**, not old bundles left by other selections. Its source inventory includes
the catalog, source register, selected article/plan/slides, local images, filters,
publishing scripts, and template/configuration hashes, plus the Git commit and
source-dirty flag when available. A dirty checkout is recorded honestly with a
content hash; the commit alone is not claimed to identify uncommitted sources.
Every Office output has its size, SHA-256 checksum, and package-check results.
Protect or distribute the manifest alongside the files it describes.

`build/` is versioned to preserve exact generated snapshots; running the same
sources and commands does not guarantee byte-identical outputs. Keep Office
files, required rendered assets, metadata/manifests, distributable archives,
review previews, and approved sanitized evaluation evidence together. Publishing
staging directories (`build/.publish-*/`) and operating-system debris are ignored;
never add browser profiles, credentials, or unapproved customer traces.

Do not rebuild just to restore or verify an existing snapshot. Verify retained
files against their recorded checksums and inspect their packages directly.
Historical source hashes and Git metadata describe the original generation;
they may differ from the current checkout and must not be rewritten to imply
regeneration. Before claiming an output is current, compare its source hashes.
When intentionally regenerating, review the affected outputs and refresh their
metadata, any containing archives, and associated previews in the same commit.
The publisher does not refresh separately assembled ZIP bundles or review
previews automatically. CI uploads candidate artifacts for review rather than
automatically committing replacements.

Relative Markdown/file links become explicit
`<repository_url>/blob/main/<path>#<anchor>` links (`tree/main` for directories).
They point to the maintained repository, **not invented future publication URLs**,
and are not checked against GitHub during export. Local anchors remain local.
If publishing newly added, uncommitted sources, repository links become live only
after those files land on `main`; provenance still records the exact local source.
External references remain hyperlinks or visible reference URLs in both formats.
Images must be reviewed local assets; publishing never fetches remote images.

H1 headings divide slides; Pandoc adds a metadata/title slide. `::: notes` blocks
become presenter notes. Word and slides display the catalog status and source-review
date. Use short bullet lists, modest tables, and focused examples on slides, not a
copy of the entire article. Word omits an initial H1 that repeats the frontmatter
title, retaining the metadata title once without changing the maintained source.
Slide subtitles do not repeat ID/status labels that are already present.
The cover review date has a dedicated box above the field-guide footer.
Give diagrams a neighboring explanation; an optional
Mermaid block attribute `alt="..."` supplies descriptive image text.
All images, including Mermaid results, are fitted proportionally within the
Word/page and slide image bounds in `templates/style.json`. Oversized source
dimensions are clamped without cropping or stretching. This prevents overflow,
but a dense diagram may still need editorial simplification for readable labels.

Exports are staged in fresh per-article/per-format directories; diagram names
include a source-content digest. Renderer exits and invalid/missing images are fatal.
Successful bundles are installed only after all selected conversions and source
stability checks pass. Once a valid selection begins, conversion failures remove
the current release manifest and staging directory; a previously successful bundle
may remain but is not a new release. Invalid catalog/selection errors stop before
changing outputs.
Output must be a dedicated directory inside the repository, never a source tree.
Do not run concurrent publishers against the same output directory.

Office checks cover ZIP CRCs, XML parsing, reference URL retention, slide count,
and 16:9 aspect ratio. They do **not** certify visual layout. Before customer
distribution, open Word and PowerPoint (or render with a separately installed
Office-compatible tool) and inspect page breaks, clipping, font substitution,
table width, code wrapping, diagram contrast, and alt text. Review speaker notes
for material unsuitable for distribution. Successful conversion is not visual
acceptance; `visual_review` remains `not_performed` in automated metadata.

For custom Chromium installations use `--puppeteer-config path/to/config.json`.
The publisher always keeps browser profiles inside its staging assets and removes
them afterward. `templates/puppeteer-ci.json` disables the browser sandbox only for
the isolated GitHub-hosted runner; do not apply that setting to routine local use.
