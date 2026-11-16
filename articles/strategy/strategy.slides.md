---
title: "Establish an AI evaluation practice"
subtitle: "E00 | Leadership briefing | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Start with the decision

- What customer outcome matters?
- What failure is unacceptable?
- Who can approve, stop, or roll back a release?

::: notes
Ask the audience to name a decision, not a metric. Foundry's workflow begins with
what to evaluate: https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview
:::

# Contoso Support outcomes

- Current, useful policy answer
- Customer-authorized order lookup
- Confirmed ticket, not a success claim
- Safe and sustainable operation

# Assign accountable owners

- Product: useful outcome and rubric
- Engineering: correct effects and access
- Safety: residual risk and escalation
- Data/platform: evidence lifecycle and budget

::: notes
Responsibility allocation is a recommendation, not a Foundry role definition.
:::

# Evidence is a portfolio

- Exact tests for contracts and effects
- Model judges for open-ended qualities
- Human review to inspect and calibrate
- Monitoring, user feedback, and trace review

::: notes
Automated evaluations complement production monitoring, user feedback, manual
transcript review, and systematic human evaluation. Each provides a different
signal; none is a complete substitute for the others.
Methodology: https://www.anthropic.com/research/demystifying-evals-for-ai-agents
:::

# Fund two evaluation purposes

- Capability: what can the agent do?
- Regression: does prior behavior still work?
- Assign owners to maintain tasks and graders
- No universal pass threshold

# Set acceptance before tuning

- Required coverage and target attribution
- Blocking versus advisory criteria
- Held-out acceptance data
- Uncertainty, not a magic sample size

# Fund the complete loop

- Application and judge inference
- Simulation and artifact generation
- Telemetry, storage, human review
- Access, retention, and incident ownership

# Launch-readiness discussion

- Can we explain one pass and one failure?
- Can we distinguish agent failure from test/grader failure?
- Does missing evidence block release?
- Are exceptions and rollback owned?
- Can we reconstruct the decision later?

# Grounding and next path

[Foundry workflow](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)

[Human review](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation)

[Evaluation permissions](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions)

Next: E01 workflow selection; E13 architecture.
