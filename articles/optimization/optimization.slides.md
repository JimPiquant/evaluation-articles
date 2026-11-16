---
title: "Optimize using evaluation evidence"
subtitle: "E10 | Controlled improvement | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Fix the dominant failure

- Stale policy is not a tone problem
- Missing ticket is not just bad prose
- Quality gain must preserve safety
- Measure before and after

# Three optimization activities

- Application behavior
- Measurement alignment
- Evaluation cost and cadence

# Freeze the experiment

- Baseline and candidate change
- Data/evaluator/judge versions
- Keep task, grader, and environment fixed for attribution
- Label measurement/design changes separately
- Success and safety constraints
- Held-out acceptance data

::: notes
If task, judge, or environment changes, do not attribute score movement solely
to the application. Acceptance data used for tuning is no longer held out.
Task-specific success criteria: https://platform.claude.com/docs/en/test-and-evaluate/develop-tests
:::

# Prompt Optimizer

- Rewrites text instructions
- Explains paragraph-level changes
- Review and preserve proposed text
- Evaluate before accepting

# Agent Optimizer

- Evaluation-driven candidate comparison
- Prompt and hosted setups differ
- Hosted integration then local apply/redeploy
- Tool effects need isolation

::: notes
Prompt-agent tool-description optimization does not evaluate client-side execution:
https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview
:::

# Validate independently

- Paired item and slice evidence
- Human review of changed restrictions
- Critical outcome constraints
- No tuning on final acceptance set

# Reduce cost responsibly

- Exact checks for exact effects
- Targeted debugging suites
- Required broad acceptance
- Full cost, budget, and stop conditions

# Grounding and next path

[Prompt Optimizer](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/prompt-optimizer)

[Agent Optimizer](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview)

[Results](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results)

Next: release under E08 policy.
