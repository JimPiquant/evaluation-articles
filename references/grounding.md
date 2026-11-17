# Grounding, terminology, and compatibility

## Source authority

Follow the hierarchy in
[the repository instructions](../.github/copilot-instructions.md#grounding-hierarchy),
with authority scoped to the claim:

1. Microsoft Foundry Evaluation documentation owns service behavior, workflows,
   permissions, supported evaluation levels, evaluator availability, limits, and
   capability status.
2. Microsoft Agent Framework documentation adds framework-specific evaluation
   APIs and integration guidance.
3. Anthropic's evaluation articles ground methodology and best practices, with
   M01 as the primary agent-evaluation methodology source.
4. Official Foundry Agents/Projects SDK references, release notes, and
   release-pinned samples ground implementation for the selected API generation.
5. Microsoft Cloud Adoption Framework (CAF), Azure Well-Architected Framework
   (WAF), and Architecture Center support architectural recommendations, not
   undocumented evaluation requirements.

This is not a rule that methodology prose overrides an SDK contract. Use the
authority for the specific product, interface, and claim; record conflicting
sources and constrain recommendations rather than inventing a reconciliation.

The [Evaluation overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)
owns the workflow: choose what to evaluate, select evaluators, run, review and
improve. [sources.json](sources.json) assigns stable IDs to primary sources.
Plans and the catalog map claims to these IDs. Reader-facing articles and slides
refer to sources by their linked article or documentation-section titles, not
the IDs, and include direct URLs so citations remain meaningful and survive
export.

The [Agent Framework Evaluation](https://learn.microsoft.com/en-us/agent-framework/agents/evaluation)
guide (A01) complements Foundry guidance with framework-specific evaluation APIs,
local checks, orchestration, and Foundry integration. Foundry Evaluation
documentation remains authoritative for service behavior, evaluator availability,
supported levels, permissions, limits, and feature status. Do not generalize
framework-specific defaults, score thresholds, or result contracts to other
interfaces. Pin framework code examples to the relevant language's package
versions and source revisions.

### Evaluation methodology

The following sources complement Microsoft product documentation. Their
recommendations are attributed methodology, not Foundry feature promises,
required thresholds, or proof that this repository's sample implements them.

| Source | Use for | Boundary |
|---|---|---|
| M01: [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) | Task/trial/grader terminology, transcript and outcome evidence, grader selection, capability versus regression evals, repeated trials, suite maintenance, and the coding-agent example pairing unit tests for correctness with an LLM rubric for overall code quality | Primary agent-evaluation methodology source; its illustrative schemas and metrics are not Foundry request or result contracts |
| M02: [Building strong safety evaluations](https://www.anthropic.com/research/building-strong-safety-evaluations) | Construct validity, realistic and balanced safety scenarios, human calibration, preregistration, uncertainty, and reproducible reporting | Anthropic's safety methodology and internal practices, not Foundry risk categories, thresholds, permissions, or operational requirements |
| M03: [Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests) | Specific, measurable, achievable, relevant success criteria; task-specific tests, edge cases, and grading examples | The instructions call this link "Develop Tests"; use the page's actual title when citing it. Claude API examples and illustrative numeric targets are not portable Foundry recipes |

### Supplementary ML learning resource

M04, [Google Machine Learning](https://developers.google.com/machine-learning),
is a directory of foundational and advanced courses and guides on machine
learning concepts, problem framing, project management, and related practice.
Use it for general ML education when relevant; it is not a primary source for
agent-evaluation methodology and does not establish Foundry behavior, evaluators,
schemas, or APIs.

Official Foundry Agents/Projects SDK documentation is approved implementation
grounding. Versioned maintainer samples outrank old local snippets. Architecture
guidance supports recommendations but cannot establish an undocumented API,
permission, feature status, or guarantee.

Maintainer documentation grounds publishing and other external tools, including
Pandoc (T01) and Mermaid CLI (T02). Internal research, older articles, and archived
material are discovery leads, not independent authority for current claims.

Review dates describe content inspection, not just HTTP success or Azure
execution. M01-M03 were inspected on November 16, 2026; M04's resource directory
was inspected on November 17, 2026. No immutable revision is recorded for these
web pages; recheck their content before release. Adding them does not establish
that existing articles have been reviewed against them. Recheck applicability,
API surface, status, and parameters before a release.

## Terms and boundaries

Use concepts and their established phrases from the grounding documentation.
Explain a documented term in plain language at first use and link its source;
do not invent a similar label when the source already names the concept.
Preserve interface-specific names in code. When sources use different terms,
attribute them and explain the relationship rather than treating them as
interchangeable product or API names.

| Term | Meaning in this series |
|---|---|
| Turn evaluation | Scores an individual response with its relevant context |
| Conversation evaluation | Scores an entire interaction; requires compatible messages/evaluation level |
| Precomputed responses | Answers already produced and saved, evaluated without generating new answers; [Foundry dataset evaluation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-datasets) (F28). "Recorded output" elsewhere in the sample describes this saved evidence, not a separate Foundry workflow name |
| Responses generated at run time | New answers from a model or agent target, then evaluated; [Foundry model and agent evaluation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-targets) (F29) |
| Reference / expected outcome | Independent evidence of the intended result |
| Rubric | Business-specific judge criteria; not an authorization mechanism |
| Gate | Declared release policy with required coverage, attribution, and limits |
| Continuous evaluation | Operational evaluation of sampled traffic, not simply a nightly batch |
| Simulation | Generated user-agent interaction, not proof of production representativeness |
| Golden dataset | Curated versioned regression evidence, not an infallible or universally required artifact |

For agent-evaluation methodology, use M01's definitions with attribution:

| M01 term | Meaning and boundary |
|---|---|
| Task / test case | A test with defined inputs and success criteria |
| Trial | One attempt at a task; repeat trials to study variable agent behavior |
| Grader | Logic scoring an aspect of performance; code-based, model-based, or human. Foundry documentation uses "evaluator" for its evaluator interfaces; a methodological grader is not automatically a registered Foundry evaluator or the catalog's Quality Grader |
| Transcript / trace / trajectory | The trial's complete interaction record. Preserve available outputs, tool calls, and results; this definition does not require exposing hidden model reasoning |
| Outcome | The final environment state, not just an agent's claim that an action succeeded |
| Evaluation harness | Infrastructure that runs tasks, records evidence, grades, and aggregates results |
| Agent harness / scaffold | The system that lets the model act as an agent; distinct from the evaluation harness |
| Evaluation suite | A collection of tasks measuring capabilities or behaviors |
| Capability / regression evals | Capability evals measure what an agent can do; regression evals check whether previously working behavior still works. Their different purposes do not prescribe a universal release threshold |

Use "Microsoft Foundry" for current guidance. Historical product names remain in
quoted source titles and preserved archives. CAF and WAF are different frameworks.

## SDK and feature-status register

| Surface | Grounding / boundary |
|---|---|
| Projects SDK | Current `azure-ai-projects` 2.x versioned agents, Responses and Evals. A stable package includes preview capabilities; use the sample's exact dependency pin and integration notes. |
| Companion's tested package set | Projects 2.2.0, Identity 1.25.1, OpenAI 2.29.0; import/type/mock-transport checks, not live Azure validation. See `samples/contoso-evaluation/sdk-status.json` for release-tag commits, complete pins, and installation constraints. |
| Standalone Agents SDK | `azure-ai-agents` threads/messages/runs. Approved legacy grounding, but no mixing into the current Projects sample. |
| Agent Framework | Independently versioned framework evaluation and Foundry integration APIs; verify the selected language and package set before reuse. The companion does not currently implement or validate this integration. |
| Evaluation CLI | `azure.ai.evaluations`, independently versioned from `microsoft.foundry` and agent/dataset extensions. The cited CLI article labels it preview. Recipe: `evals/azure.eval.yaml`. |
| Conversation workflow | `evaluation_level` defaults to turn. Check catalog compatibility; unsupported evaluators can be skipped. |
| Trace/simulation/optimizer workflows | Check each linked source's preview flags, target support, region, and limits at implementation time. No series-wide GA/preview inference. |
| Synthetic dataset generation | The cited current guide requires Projects SDK >=2.8.0. A dependency set for recorded-output Evals is not proof that this newer workflow is compatible. |

Pin reproducible code to a tested package set and source revision. Record imports
and local tests separately from live-cloud validation. Do not carry product
model lists, pricing, connector counts, or universal latency promises into prose.

## Known source discrepancies

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

### Methodology applicability and tensions

These are differences in scope and recommendations, not evidence that the
sources define one shared product contract:

- **Dataset size and quality (M01-M03).** M01 recommends starting with a small
  set of real failures; M02 describes larger sample floors for Anthropic's safety
  evaluations; M03 advises prioritizing volume over quality in its design
  principles. Attribute each recommendation to its context. This series does
  not adopt a fixed count or accept ambiguous tasks and unreliable labels in
  exchange for more rows. Choose coverage, repeated trials, and sample size
  around the decision, risk, detectable effect, and reported uncertainty.
- **Grader errors and release gates (M02).** M02 recommends flagging broken
  grading and excluding affected items from an evaluation. Preserve those
  errors and disclose any analytical exclusion and its denominator. Under this
  repository's sample release policy, a missing or errored required item blocks
  the gate; dropping it cannot manufacture complete coverage or a passing rate.
- **Outcome grading and process checks (M01).** M01 warns against requiring an
  unnecessarily rigid tool sequence and allows partial credit. The Contoso
  fixture intentionally checks an exact tool contract and uses all-pass release
  rules. Label these as illustrative sample policy, not a general agent-grading
  prescription. For other applications, justify process constraints by actual
  requirements, such as authorization and consent, while allowing valid
  alternative solutions.
- **Coding-agent grader combination (M01).** M01 presents unit tests for
  correctness plus an LLM rubric for overall code quality as a practical pattern
  for coding-agent evaluations, with additional graders and metrics as needed.
  Treat this as context-specific methodology, not a universal combination or a
  Foundry requirement. Choose graders for the task and verify any Foundry
  evaluator inputs, result contract, and score semantics separately.
- **Safety measures and environment (M02).** Risk-specific rubrics, harmless or
  appropriate response rates, and atomic binary criteria are methodological
  choices, not replacements for Foundry's documented score scales and thresholds.
  Refusal alone does not establish safety. Anthropic's discussion of disabling
  safeguards in controlled research does not authorize weakening safeguards,
  production routing, or data controls here; any adversarial execution requires
  an explicitly authorized, isolated environment.
- **Repeated-trial metrics (M01).** `pass@k` measures at least one successful
  attempt; `pass^k` measures success in every attempt. Neither is the sample's
  aggregate per-check pass rate. State the trial protocol and assumptions before
  using these metrics; they are not interchangeable with average evaluator
  scores or evidence of complete required coverage.

## Claim classes and maintenance

Label product behavior through a source, organizational advice as a recommendation,
and example thresholds as illustrative policy. Content-harm default threshold 3
means >3 fails; a stricter policy is not a Foundry default.

For methodology claims, cite sources by their linked article or section titles
where the recommendation appears, retain established terminology, and explain
applicability to the chosen evaluation unit and decision. Register source IDs in
the affected plan and catalog entry when adopting that guidance. A source's illustrative YAML or
numeric target is not an implemented sample feature, an SDK schema, or a safety
guarantee. Report grader calibration against human judgments, relevant
configuration and lineage, and uncertainty appropriate to the claim.

Before a release, review every registered source for changed meaning, not just
HTTP success. Update impacted plans/articles/slides together. Move unresolved
affected articles to `review` and record the refresh reason in their plans; do
not mark them `ready` until the required reviews are complete. Keep review notes,
SDK tests, output provenance, and publication URLs; a release is not a claim of
legal compliance or zero risk.
