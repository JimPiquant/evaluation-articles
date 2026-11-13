# Create, manage, use, and optimize AI evaluations

A practitioner learning series grounded in the
[Microsoft Foundry Evaluation documentation](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)
and official Foundry Agents/Projects SDK references.

Start with the decision you need to make, not a list of evaluators. Choose a turn
or a complete conversation, identify the evidence, measure the outcomes, and use
the results to improve the application.

**Readiness:** these are fresh, source-grounded drafts. The local sample and
publishing checks are executable; cloud recipes require your authorized project
and live validation. Generated Word/PowerPoint files still require visual and
domain review before customer publication.

## Reading paths

| Reader | Start here |
|---|---|
| New developer | [Choose a workflow](articles/choose-workflow/choose-workflow.md) -> [First evaluation](articles/first-evaluation/first-evaluation.md) -> [Datasets](articles/datasets/datasets.md) -> [Results](articles/results/results.md) |
| Leader / architect | [Evaluation practice](articles/strategy/strategy.md) -> [Architecture](articles/reference-architecture/reference-architecture.md) -> [Operating model](articles/operations/operations.md) |
| RAG developer | [Evaluators](articles/evaluators/evaluators.md) -> [Model and RAG responses](articles/rag-responses/rag-responses.md) |
| Agent developer | [Conversation evaluation](articles/agent-conversations/agent-conversations.md) -> [Release gates](articles/release-gates/release-gates.md) |
| Operator | [Identity and networking](platform/identity/identity.md) -> [Operations runbook](articles/operations/operations.md) -> [Optimization](articles/optimization/optimization.md) |
| Safety reviewer | [Safety evaluations](articles/safety/safety.md) -> [Adversarial testing](articles/red-teaming/red-teaming.md) |

## Complete series

| ID | Article | Companion presentation |
|---|---|---|
| E00 | [Establish an evaluation practice](articles/strategy/strategy.md) | [Slides](articles/strategy/strategy.slides.md) |
| E01 | [Choose your workflow](articles/choose-workflow/choose-workflow.md) | [Slides](articles/choose-workflow/choose-workflow.slides.md) |
| E02 | [Run your first evaluation](articles/first-evaluation/first-evaluation.md) | [Slides](articles/first-evaluation/first-evaluation.slides.md) |
| E03 | [Create and manage datasets](articles/datasets/datasets.md) | [Slides](articles/datasets/datasets.slides.md) |
| E04 | [Define and calibrate evaluators](articles/evaluators/evaluators.md) | [Slides](articles/evaluators/evaluators.slides.md) |
| E05 | [Evaluate model and RAG responses](articles/rag-responses/rag-responses.md) | [Slides](articles/rag-responses/rag-responses.slides.md) |
| E06 | [Evaluate agents and conversations](articles/agent-conversations/agent-conversations.md) | [Slides](articles/agent-conversations/agent-conversations.slides.md) |
| E07 | [Interpret results and compare versions](articles/results/results.md) | [Slides](articles/results/results.slides.md) |
| E08 | [Automate release decisions](articles/release-gates/release-gates.md) | [Slides](articles/release-gates/release-gates.slides.md) |
| E09 | [Operate and govern evaluations](articles/operations/operations.md) | [Slides](articles/operations/operations.slides.md) |
| E10 | [Optimize with evaluation evidence](articles/optimization/optimization.md) | [Slides](articles/optimization/optimization.slides.md) |
| E11 | [Evaluate safety](articles/safety/safety.md) | [Slides](articles/safety/safety.slides.md) |
| E12 | [Run adversarial testing](articles/red-teaming/red-teaming.md) | [Slides](articles/red-teaming/red-teaming.slides.md) |
| E13 | [Integrate the reference architecture](articles/reference-architecture/reference-architecture.md) | [Slides](articles/reference-architecture/reference-architecture.slides.md) |
| P01 | [Deploy an evaluation target](platform/deployment/deployment.md) | [Slides](platform/deployment/deployment.slides.md) |
| P02 | [Secure evaluation identities and networks](platform/identity/identity.md) | [Slides](platform/identity/identity.slides.md) |
| P03 | [Deliver and evaluate agent tools](platform/tools/tools.md) | [Slides](platform/tools/tools.slides.md) |

Each article has a same-folder `.plan.md`. [series.json](series.json) owns order,
status, source IDs, and export selection. [ProjectScope.md](ProjectScope.md)
defines boundaries; [references/grounding.md](references/grounding.md) defines
authority, compatibility, and maintenance.

## Try the shared example

The [Contoso companion](samples/contoso-evaluation/README.md) is a small offline
fixture harness with working tools and an optional Foundry integration. It
demonstrates evidence and gate mechanics without uploading data or incurring
cloud charges.

```bash
python3 -m unittest discover -s samples/contoso-evaluation/tests
python3 samples/contoso-evaluation/run.py --candidate baseline --output build/evaluation/baseline.json
python3 samples/contoso-evaluation/gate.py build/evaluation/baseline.json
python3 samples/contoso-evaluation/run.py --candidate regressed --output build/evaluation/regressed.json
python3 samples/contoso-evaluation/gate.py build/evaluation/regressed.json
```

The last command **must fail**: a successfully executed evaluation does not mean
the candidate passed. Follow the companion README for the exact optional cloud
dependencies, credentials, integration boundaries, and cost considerations.

## Generate Word and PowerPoint

Install [Pandoc](https://pandoc.org/installing.html). For Mermaid diagrams also
install [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli) and its supported
browser. Then:

```bash
python3 scripts/check_content.py
python3 -m unittest discover -s scripts/tests
python3 scripts/publish.py --article E02 --format all
python3 scripts/publish.py --format all
```

Outputs and release metadata are versioned under `build/` to preserve the exact
generated files; byte-identical rebuilds are not guaranteed. Article Markdown
produces Word; deliberately authored slide Markdown produces PowerPoint.
Markdown remains the editable source, not the Office files. Templates and
publishing instructions are in [templates/README.md](templates/README.md).
`generate-docx.sh` remains a compatibility entry point. CI uploads candidate
artifacts for review rather than automatically replacing committed snapshots.
Check the recorded source hashes before treating a snapshot as current; retained
artifacts may predate later source changes.

## What changed

The old pipeline-centered articles, deployment material, notes, images, sample,
and Office files are preserved under [archive/](archive/README.md), outside the
current learning path. The [migration map](references/migration.md) records their
successors. Do not use archived code or claims as current customer guidance.
