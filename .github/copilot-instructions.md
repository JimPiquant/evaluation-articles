# Copilot instructions

## Purpose and structure

This is a customer learning and publishing repository, not a production application.
Organize guidance around **choose, create, run, interpret, manage, and optimize**
AI evaluations in Microsoft Foundry and with Microsoft Agent Framework.
Deployment is supporting material, not a prerequisite for evaluating recorded
responses. There is not an external publishing target.

- `series.json` is the single catalog: stable IDs, order, audience, editorial
  status, source IDs, reviewed date, and plan/article/slide paths.
- `articles/` contains the evaluation lifecycle and specialist/capstone articles.
- `platform/` contains current deployment, identity, and tool-delivery guidance.
- `samples/contoso-evaluation/` is the shared executable teaching scenario.
- `references/` records sources, terminology, compatibility, and discrepancies.
- `templates/` and `scripts/` implement publishing. `build/` contains generated
  snapshots retained in version control.
- `archive/` preserves superseded content and original binary assets. It is
  explicitly non-normative: do not use its claims or code as current grounding,
  publish it through the current catalog, or silently rewrite its provenance.

## Grounding hierarchy

All the material in this repository should be grounded in authoritative sources.  Use this list as a hierarchy:

1. Microsoft Foundry documentation, especially [Foundry Evaluation overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)
   and its linked Evaluation documentation for product behavior, workflows,
   permissions, supported levels, limits, and status.
2. [Agent Framework Evaluation](https://learn.microsoft.com/en-us/agent-framework/agents/evaluation)
   and its linked documentation for additional, complementary guidance.
   Developers use Microsoft Agent Framework to integrate evaluation into the
   agent development lifecycle.
3. Anthropic articles on evaluation methodologies, and best practices, including
[Demystifying Evals for AI Agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) (primary source),
and [Building Strong Safety Evaluations](https://www.anthropic.com/research/building-strong-safety-evaluations),
and [Develop Tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests).
4. Official Foundry Agents/Projects SDK references, release notes, and samples
   are approved grounding for implementation. Use a release tag/commit for code;
   record package versions and the exact API generation.
5. Microsoft Cloud Adoption Framework, the Azure Well-Architected Framework, and Architecture Center for support
   architectural recommendations, not undocumented evaluation requirements.

Consult `references/sources.json` and `references/grounding.md`. In reader-facing
articles and slides, refer to grounding sources by their linked article title or
documentation section title, not by source ID. Reserve source IDs for plans and
the catalog. Include direct URLs where claims appear. Record the actual
verification date; do not imply that a link check verifies product behavior.
Recheck volatile APIs and feature status before release.

Do not combine standalone `azure-ai-agents` threads/runs with versioned
`azure-ai-projects` agents/Responses/Evals in one recipe. A stable SDK can include
preview features. Label status per capability and interface, never by blanket
inheritance. If sources conflict, record the discrepancy and constrain the
recommendation; do not invent reconciliation or prescribe "latest" as a pin.
Known discrepancies and capability-specific SDK minimums are recorded in
`references/grounding.md`; expand that register when discovering another conflict.

## Writing and planning

Create or review `<slug>.plan.md` before drafting or substantially revising
`<slug>.md` or `<slug>.slides.md`. Every plan includes Purpose, Audience, Outline,
References, customer outcome, prerequisites, grounding boundaries, and acceptance
criteria. Keep these three sources adjacent and register them in `series.json`.

Article frontmatter includes `title`, `description`, `author`, and `date`. Slides
include `title`, `subtitle`, `author`, and `date`; use level-one slide headings
and `::: notes` for presenter notes. Write a curated narrative, not a prose dump.
Markdown is canonical; Office files are generated, not separately edited masters.

In articles and PowerPoint decks, introduce each topic and present its main points
before explaining the details. In decks, sequence the slides so this progression
is clear to the audience.

Treat topic content as reusable knowledge and presentations as curated adaptations.
Keep technical facts, executable examples, and diagrams canonical wherever
practical. Reuse an article body for Word and full-length blog publication rather
than maintaining independent copies. Adapt wording and sequencing for audience
and purpose, while preserving citations, limitations, and validation boundaries.
Document publishing capabilities as implemented, not merely planned.

Version intended `build/` deliverables with their metadata and release manifest:
Office outputs, rendered assets, distributable archives, review previews, and
sanitized evaluation evidence. Byte-identical rebuilds are not guaranteed.
Preserve existing artifact bytes and provenance; do not rebuild merely to restore
or validate a snapshot, and never edit generated files as content masters.
Regeneration is an intentional update: review affected outputs, refresh their
metadata and any containing archives/previews together, and commit them together.
Historical provenance may precede current sources; do not rewrite it to imply a
rebuild occurred. Check source hashes before claiming an artifact is current.
Do not commit temporary publishing directories, browser profiles, credentials,
or unapproved customer traces. CI uploads candidate artifacts for review; it does
not automatically commit or replace the versioned snapshots.

Write practitioner-to-practitioner for developers by default, with concrete,
honestly labeled examples. Leaders/architects get decisions, tradeoffs, and
checklists without code. Use the Contoso Support scenario consistently: knowledge
retrieval, customer-authorized order lookup, and confirmed ticket creation.
Separate product fact, editorial recommendation, and illustrative policy.

Use professional, clear language rather than shortening sentences at the
expense of meaning. Prefer precise verbs and complete objects over vague
shorthand: write "services integrate with a VNet" rather than "services meet a
VNet", and "verify DNS returns the expected IP address" rather than "prove DNS".
Avoid vague or unnecessary caveats that distract from the point. For example,
when defining evaluation terms from a methodology source, cite the source
directly instead of adding "it is not a Foundry request schema" unless that
distinction is relevant to the reader.

Make guidance decision-oriented: explain when a recommendation applies, why it
matters, and what tradeoffs affect the choice. Keep evaluation purpose, grading
method, application architecture, and evaluation level distinct. Connect
general methodology to documented Foundry capabilities without assuming a
one-to-one mapping. Use concise examples and reserve tip callouts for practical
advice readers might otherwise miss.

For a structured editorial and grounding review, use the
[evaluation article review skill](skills/evaluation-article-review/SKILL.md).

Use only the catalog statuses `planned`, `draft`, `review`, `ready`, and `published`.
`draft` means authored, not customer-validated or externally published. `review`
means technical/editorial review is pending or in progress. `ready` means the
required reviews for the intended deliverable are complete, not that live Azure
execution has been validated.
Record publication URL separately; never claim CAF/AAC publication without it.

## Evaluation invariants

- Choose the evaluation unit (turn/conversation), evidence source, compatible
  evaluators, and decision before selecting execution tooling.
- Complete conversations require appropriate `messages` data and explicit
  supported evaluation level. A skipped evaluator is not passing evidence.
- Reference answers are not actual responses; groundedness needs independent
  context. Fixture checks are not LLM-judged quality or safety evaluation.
- Verify actual candidate attribution; no default to the requested version.
- Gates fail closed on missing/invalid metrics, zero counts, skips/errors,
  incomplete pagination, or incompatible result contracts.
- Centralize sample policy and adapt real SDK results explicitly. Do not invent
  uniform score scales or equate averages with pass rates.
- For documented content-harm threshold 3, scores <=3 pass and >3 fail.
  Stricter boundaries must be labeled customer policy.
- No fixed row count guarantees confidence or safety. Explain coverage,
  uncertainty, judge calibration, and held-out acceptance data.
- Preserve dataset/evaluator/target/judge lineage and review evidence. Do not
  auto-delete cloud runs, disable production routing for tests, or upload
  sensitive traces without authorization/redaction.
- Label local validation, SDK import checks, and live-cloud validation separately.
  Do not call the companion a production agent or a validated Azure deployment.

## Commands and validation

From the repository root:

```bash
python3 scripts/check_content.py
python3 -m unittest discover -s scripts/tests
python3 -m unittest discover -s samples/contoso-evaluation/tests
python3 samples/contoso-evaluation/run.py --candidate baseline --output build/evaluation/baseline.json
python3 samples/contoso-evaluation/gate.py build/evaluation/baseline.json
python3 scripts/publish.py --article E02 --format all
python3 scripts/publish.py --format all
```

The regressed fixture must fail the gate. `generate-docx.sh` is a compatibility
entry point, not a separate publishing implementation. Publishing requires
Pandoc; Mermaid diagrams additionally require Mermaid CLI and its browser.
Python checks and offline sample tests use the standard library. Cloud sample
dependencies and commands are documented in its README.

Run targeted checks for changed content/code and full catalog/export checks for
publishing changes. Converter/renderer failures must return nonzero and cannot
reuse stale assets. Output metadata records source hashes, tool versions, and
checksums. Office ZIP integrity is not visual acceptance: inspect pages/slides
before marking a bundle customer-ready. Never provision Azure resources merely
to validate prose without an explicit deployment task.
