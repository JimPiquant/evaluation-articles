---
title: "Run adversarial testing responsibly"
subtitle: "E12 | Authorized risk discovery | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Search for missed failures

- Intentional probing differs from ordinary tests
- Findings support mitigation
- No scan exhausts possible failures
- Authorization comes first

# Write the charter

- Approved target and observed version
- Risks, limits, budget
- Synthetic data and sandbox tools
- Stop conditions and finding owner

# Start with maintained Foundry guidance

- Scanning, scoring, reporting
- Target/risk restrictions
- Category-specific limitations
- PyRIT as an advanced extension

::: notes
The concept page and general region reference currently disagree; verify exact
service support before a run rather than merging their lists:
https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-regions-limits-virtual-network
:::

# Separate evidence activities

- Ordinary safety cases
- User simulation
- Adversarial discovery
- Exact control/effect tests

# Design interpretable scenarios

- State the risk hypothesis and expected behavior
- Use realistic multi-turn context where relevant
- Include benign/ambiguous controls
- Record limits before interpreting results

::: notes
Scenario realism and construct validity are M02 methodology; retain Foundry's
documented support and authorization limits:
https://www.anthropic.com/research/building-strong-safety-evaluations
:::

# Protect the environment

- No real customer mutations
- Verify tool routing
- Bound workloads and side effects
- Stop on charter violation

::: notes
Service redaction does not automatically protect external business-service logs.
No live attacks or payloads are supplied in this repository.
:::

# Triage actual behavior

- Judge disagreement or confirmed failure?
- Response versus tool effect
- Correct mitigation layer
- Restricted reviewer evidence

# Close the loop

- Re-test finding and benign cases
- Curate safe regressions
- Preserve residual-risk decision
- Apply release policy

# Grounding and next path

[Foundry red teaming](https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent)

[Safety evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators)

[PyRIT](https://github.com/microsoft/PyRIT)

Next: E08 release policy.
