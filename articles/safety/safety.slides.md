---
title: "Evaluate safety without false assurance"
subtitle: "E11 | Risk-specific evidence | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Measurement is not prevention

- Safety evaluation measures chosen cases
- Runtime controls constrain behavior
- Authorization enforces access
- None guarantees legal compliance

# Map the support risks

- Inappropriate content
- Confidential order disclosure
- Unsupported personal inference
- Unauthorized or unconfirmed action

# Select supported checks

- Target and evaluation level
- Language and modality
- Required evidence
- Actual result scale and limitations

# Be precise at the boundary

- Content-harm default threshold: 3
- Score <=3 passes
- Score >3 fails
- Stricter policy must be labeled

::: notes
These semantics are specific to the cited content-harm scores, not all risk metrics:
https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators
:::

# Coverage is part of acceptance

- Required skips/errors block
- Critical slices need evidence
- Enriched test rates are not prevalence
- Zero observed defects is not zero risk

# Measure the intended safety construct

- State the behavior or harm being measured
- Pair risk cases with benign and ambiguous controls
- Refusal alone is not safety
- Inspect tool effects and grader disagreement

::: notes
Construct validity and realistic controls are M02 methodology. They do not
change Foundry score semantics:
https://www.anthropic.com/research/building-strong-safety-evaluations
:::

# Review safely

- Controlled access to sensitive results
- Independent evidence and human judgment
- Version and policy attribution
- Approved retention

# Mitigate at the right layer

- Data/privacy controls
- Authorization and tool behavior
- Runtime restrictions
- Instructions/model, then retest

# Grounding and next path

[Risk/safety reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators)

[Human review](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation)

Next: E12 adversarial testing.
