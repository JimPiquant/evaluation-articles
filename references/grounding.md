# Grounding, terminology, and compatibility

## Source authority

The [Evaluation overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)
owns the workflow: choose what to evaluate, select evaluators, run, review and
improve. [sources.json](sources.json) assigns stable IDs to primary sources.
Plans map claims to these IDs; articles cite direct URLs so references survive
export.

Official Foundry Agents/Projects SDK documentation is approved implementation
grounding. Versioned maintainer samples outrank old local snippets. Architecture
guidance supports recommendations but cannot establish an undocumented API,
permission, feature status, or guarantee.

Review dates describe source inspection, not Azure execution. Sources inspected
November 12 remain dated November 12; selected pages were rechecked November 13.
Recheck applicability, API surface, status, and parameters before a release.

## Terms and boundaries

| Term | Meaning in this series |
|---|---|
| Turn evaluation | Scores an individual response with its relevant context |
| Conversation evaluation | Scores an entire interaction; requires compatible messages/evaluation level |
| Recorded output | What the application actually produced, not a reference answer |
| Reference / expected outcome | Independent evidence of the intended result |
| Rubric | Business-specific judge criteria; not an authorization mechanism |
| Gate | Declared release policy with required coverage, attribution, and limits |
| Continuous evaluation | Operational evaluation of sampled traffic, not simply a nightly batch |
| Simulation | Generated user-agent interaction, not proof of production representativeness |
| Golden dataset | Curated versioned regression evidence, not an infallible or universally required artifact |

Use "Microsoft Foundry" for current guidance. Historical product names remain in
quoted source titles and preserved archives. CAF and WAF are different frameworks.

## SDK and feature-status register

| Surface | Grounding / boundary |
|---|---|
| Projects SDK | Current `azure-ai-projects` 2.x versioned agents, Responses and Evals. A stable package includes preview capabilities; use the sample's exact dependency pin and integration notes. |
| Companion's tested package set | Projects 2.2.0, Identity 1.25.1, OpenAI 2.29.0; import/type/mock-transport checks, not live Azure validation. See `samples/contoso-evaluation/sdk-status.json` for release-tag commits, complete pins, and installation constraints. |
| Standalone Agents SDK | `azure-ai-agents` threads/messages/runs. Approved legacy grounding, but no mixing into the current Projects sample. |
| Evaluation CLI | `azure.ai.evaluations`, independently versioned from `microsoft.foundry` and agent/dataset extensions. The cited CLI article labels it preview. Recipe: `evals/azure.eval.yaml`. |
| Conversation workflow | `evaluation_level` defaults to turn. Check catalog compatibility; unsupported evaluators can be skipped. |
| Trace/simulation/optimizer workflows | Check each linked source's preview flags, target support, region, and limits at implementation time. No series-wide GA/preview inference. |
| Synthetic dataset generation | The cited current guide requires Projects SDK >=2.8.0. A dependency set for recorded-output Evals is not proof that this newer workflow is compatible. |

Pin reproducible code to a tested package set and source revision. Record imports
and local tests separately from live-cloud validation. Do not carry product
model lists, pricing, connector counts, or universal latency promises into prose.

## Known source discrepancy

The [built-in catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)
lists Quality Grader, while the
[conversation guide](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations)
calls `builtin.quality_grader` deprecated. This series does not recommend it as a
new default. Resolve the exact surface/version with maintained documentation or
support before adopting it. No assumption that both statements imply the same
availability.

The red-teaming concept page lists five cloud regions, while the general
[region/limit reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-regions-limits-virtual-network)
lists two red-teaming regions. Do not merge those lists into an invented guarantee.
Confirm availability for the exact local/cloud risk category and target before
execution; seek current service guidance when the pages disagree.

The custom-evaluator reference describes exception/timeout results as score 0
with an error state. Preserve the state and treat required errors as invalid
evidence, rather than converting them into successful scoring or a silent fallback.

Projects release examples use `model` for some evaluator initialization, while
the groundedness-specific release example uses `deployment_name`. The companion
follows the latter for its sole advisory groundedness evaluator. Do not replace
all evaluator initialization with a uniform key; verify the exact evaluator and
service interface. Newer release metadata was found, but that package set was
not installable/validated in this environment; the selected pins are not "latest."

The current Projects SDK README says to verify version >=2.3.0, while the cloud
evaluation setup example uses >=2.2.0. The companion validates the narrower
release-pinned 2.2.0 recorded-output API; it does not claim compatibility with all
features in the current README. For new workflows follow the capability-specific
minimum, select an installable release, and repeat import/type plus live checks
before production use. The latest README's Python minimum also must not be
inherited by the standard-library offline fixture.

## Claim classes and maintenance

Label product behavior through a source, organizational advice as a recommendation,
and example thresholds as illustrative policy. Content-harm default threshold 3
means >3 fails; a stricter policy is not a Foundry default.

Before a release, review every registered source for changed meaning, not just
HTTP success. Update impacted plans/articles/slides together. Mark unresolved
affected articles `needs-refresh`. Keep review notes, SDK tests, output provenance,
and publication URLs; a release is not a claim of legal compliance or zero risk.
