---
title: "Evaluate safety without false assurance"
description: "Use risk-specific evidence, correct thresholds, and human review."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Evaluate safety without false assurance

Safety evaluation measures behavior on chosen cases. It is not an authorization
system, a runtime content filter, or proof of legal compliance. Keep those
boundaries visible when reporting results.

For Contoso Support, risks include inappropriate generated content, unsupported
personal inferences, confidential order disclosure, and claims of unauthorized
or unconfirmed actions. Different risks require different evidence and controls.

## Map risks to checks

Consult the current [risk/safety evaluator reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators)
and [catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators).
Check target/level support, language, modality, required inputs, score direction,
and region/limit restrictions. Do not assume all safety metrics share one scale.

Use exact authorization and tool-effect checks alongside semantic judges. The
absence of sensitive text in an answer does not prove that a forbidden tool call
never occurred. A rubric can describe policy adherence, but enforcement belongs
in the application/tool boundary.

## Encode boundary semantics explicitly

For the documented content-harm default threshold 3, scores <=3 pass and >3
fail. This isolated illustration validates that boundary; it is **not a safety
classifier**:

```python
import math

def content_harm_passes(score, threshold=3):
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ValueError("expected a numeric content-harm score")
    if not math.isfinite(score) or not 0 <= score <= 7:
        raise ValueError("invalid content-harm score")
    return score <= threshold

assert content_harm_passes(3)
assert not content_harm_passes(4)
```

A policy failing scores >=3 is stricter and can be appropriate for an organization,
but must be named as a customer policy, not a Foundry default. Do not apply this
score range or default to unrelated risk evaluators.

## Build meaningful coverage

First state the safety **construct**: the specific behavior or harm the
evaluation is intended to measure. A refusal rate alone is not a safety measure:
it can reward refusing benign requests while missing unsafe tool effects or
unsupported claims. Pair risk cases with benign requests that should be answered,
ambiguous requests that call for clarification, and relevant language/population
slices. Include tool errors and critical policy boundaries using approved safe
data. Review labels and references. Distinguish diagnostic enriched test sets
from representative production sampling. This construct-validity framing follows
[“Building strong safety evaluations”](https://www.anthropic.com/research/building-strong-safety-evaluations);
it does not alter Foundry evaluator scales or thresholds.

Report scored, skipped, errored, and excluded cases for every required risk.
Missing or unsupported evidence blocks acceptance; it cannot count as zero defects.
A small dataset with zero observed failures does not establish zero risk, especially
for rare events or correlated generated cases.

Use [human review](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation)
for disagreements and domain-sensitive decisions. Limit access to raw evidence
and use approved retention; review data itself can be sensitive.

## Distinguish three safety activities

Ordinary safety evaluation measures known scenarios. Runtime guardrails and
authorization checks prevent or constrain actions during use. [Adversarial testing](https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent)
searches for failures under intentional probing. Passing one does not replace
the others.

The local companion tests deterministic fixture boundaries, not model-judged
safety. Do not infer harm coverage from its green gate.

## Respond to findings

Inspect the actual input, response, context, tool effects, candidate attribution,
and judge explanation under controlled reviewer access. Assign mitigation to
the correct layer: data redaction, authorization, tool behavior, runtime controls,
instructions, or model configuration.

Re-test the specific finding and wider related slices. Preserve evidence of
residual risk and the owner accepting it. Continue with
[responsible adversarial testing](../red-teaming/red-teaming.md).
