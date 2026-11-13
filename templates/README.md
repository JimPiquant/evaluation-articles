# Office reference templates

`reference.docx` and `reference.pptx` are publishing inputs, not edited copies of
articles. They are derived from [Pandoc's bundled reference
packages](https://pandoc.org/MANUAL.html#option--reference-doc) using standard-library
ZIP/XML transformations. Keep these small template binaries in source control;
customer exports belong in release artifacts, not the source tree.

```sh
python3 scripts/build_templates.py
```

The generator uses `style.json` as the editable brand/typography source and
records the Pandoc version in `provenance.json`. It preserves Pandoc's expected
style IDs and PowerPoint layout names. ZIP entries have stable names/order and
fixed timestamps, so regenerating with the same Pandoc version and configuration
produces identical template packages. Regenerate deliberately when upgrading
Pandoc and review the resulting packages in Office.

## Design

- **Brand:** AI Evaluation Field Guide; navy text, teal accents, blue hyperlinks,
  pale neutral table/code backgrounds. No Microsoft logos or affiliation claims.
- **Word:** US Letter, one-inch margins, Arial 11 pt, clear 20/16/13 pt heading
  hierarchy, 30 pt cover title, readable monospace code, table borders/header
  treatment, and field-guide/page-number footer.
- **PowerPoint:** 16:9, 10 × 5.625 inches, Arial 22 pt body and 28 pt slide titles,
  larger cover title, master-level teal accent and field-guide footer. Short
  customer-facing outlines are required; automatic font shrinking is not a
  substitute for editing an overcrowded slide.
- **Metadata:** the publisher supplies missing ID/status labels without
  duplicating labels already in the subtitle. Source-review date has its own
  centered cover box above the footer, separate from title, subtitle, and author.
- **Diagrams:** `mermaid.json` uses a light, high-contrast palette and strict
  Mermaid security settings. Diagrams become embedded PNGs rather than raw code.

Images are fitted proportionally within 6.5 × 5.75 inches in Word and
8.8 × 3.5 inches on slides; oversized explicit dimensions are clamped too.
There is no cropping or aspect-ratio stretching. Very tall or wordy diagrams
may still need editorial simplification to stay legible.

Arial and Courier New are requested, not embedded. Courier New is installed on
the tested macOS system; Consolas is not. SourceCode, VerbatimChar, highlighted
token styles, and the actual code runs receive explicit monospace fonts so
viewers need not infer the font through character-style inheritance.
Office or another viewer may
substitute fonts when unavailable, so verify layout on the intended platform.
Automated ZIP/XML checks cannot establish rendering quality or accessibility.
Visual customer-release review remains mandatory.
