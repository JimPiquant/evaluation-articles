---
title: "Define and calibrate evaluators"
subtitle: "E04 | Measure useful outcomes | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Select questions, not a catalog

- Was the policy answer useful and correct?
- Was the right tool used appropriately?
- Did the action actually complete?
- Was the outcome acceptably safe?

# Choose a grading method

- Code-based: explicit, repeatable checks
- Model-based: judge nuanced responses with criteria
- Human: expert review and calibration
- Combine only when each adds distinct evidence

::: notes
These are Anthropic's agent-evaluation methodology categories. Code graders are
fast and reproducible but can be brittle; model graders handle nuance but need
calibration; human graders provide expert review but require time. Foundry
evaluator interfaces and custom-evaluator types have separate contracts.
https://www.anthropic.com/research/demystifying-evals-for-ai-agents
https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators

For coding-agent evaluations, Anthropic describes unit tests for correctness
plus an LLM rubric for overall code quality, adding other graders only as
needed. This is a context-specific methodology example, not a Foundry
requirement.
:::

# Start with a business rubric

- Stable dimension IDs
- Specific descriptions and weights
- Domain score anchors
- Applicable versus always applicable

::: notes
Dimensions score 1-5; weighted total is normalized to 0-1:
https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators
:::

# Contoso quality dimensions

- Correct resolution from evidence
- Appropriate escalation
- Accurate concise communication
- No unconfirmed success claim

# Pair rubric with independent checks

- Built-in safety and support
- Exact authorization/effect checks
- Tool/process evidence
- Human disagreement review

::: notes
Custom implementations can be code-based, prompt-based, or endpoint-based, with
different output contracts. Code exceptions/timeouts carry an error state even
if the score is zero; preserve that distinction:
https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/custom-evaluators
:::

# Calibrate before release gates

- Blinded acceptable/failed/ambiguous cases
- Known-good and known-bad grader checks
- Independent reviewer judgments
- Inspect task/grader disagreements by slice
- Version rubric and judge settings

::: notes
Check that graders measure the intended construct; task, grader, and environment
defects can look like candidate failures. Recheck bias and calibration when the
judge, rubric, or mapping changes. M02 methodology:
https://www.anthropic.com/research/building-strong-safety-evaluations
:::

# Compatibility is part of quality

- Supported evaluation level
- Required fields and tool mappings
- Score scale and threshold direction
- Scored, skipped, and errored counts

# Avoid false certainty

- Composite score is not authorization
- Required skips block
- No uniform scale across evaluators
- Quality Grader source conflict remains tracked

# Grounding and next path

[Catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)

[Rubrics](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators)

[Human evaluation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation)

[Custom evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/custom-evaluators)

Next: E05 RAG or E06 conversations.
