---
title: "Create and manage evaluation datasets"
subtitle: "E03 | Evidence lifecycle | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Data is an evidence asset

- Representative coverage
- Independent references
- Reproducible versions
- Approved handling

# Design a task that measures success

- Start with a product outcome or observed failure
- Specify inputs and unambiguous success criteria
- Ticket exists only after consent; correct customer and issue
- Confirm a reference solution passes its graders
- Test when behavior should and should not occur

::: notes
These are task-design recommendations, not Foundry schema requirements or a
fixed dataset-size rule.
Source: https://www.anthropic.com/research/demystifying-evals-for-ai-agents
Task-specific measurable criteria are also described in:
https://platform.claude.com/docs/en/test-and-evaluate/develop-tests
:::

# Choose the right row

- Query/response/context for recorded turns
- Complete messages for conversations
- Scenario seeds for simulation
- Do not interchange schemas

# Separate observation from expectation

- Actual output: what happened
- Context: what was retrieved
- Reference: what should happen
- Version: who actually produced it

# Cover the support journey

- Ordinary policy questions
- No answer or outdated evidence
- Allowed and denied order lookup
- Confirmed ticket and failed tool

# Keep splits honest

- Development for tuning
- Calibration for judge/human alignment
- Acceptance held out
- Split related conversations as a group

# Support capability and regression evaluations

- Capability: identify what the agent can do and improve
- Regression: check behavior that worked before still works
- A capability task may later join the regression set
- Set thresholds for the decision; no universal rates

::: notes
Anthropic describes capability evaluations as having room to improve and
regression evaluations as checking for backsliding. Its example pass-rate
expectations are not Foundry defaults or universal acceptance thresholds.
Source: https://www.anthropic.com/research/demystifying-evals-for-ai-agents
:::

::: notes
Avoid near-duplicate leakage across splits and record the sampling design.
:::

# Govern trace reuse

- Approve purpose and access
- Redact before publication
- Review labels and realism
- Preserve lineage and retention ownership

# Manage versions

- Stable case IDs and content hashes
- Schema/policy version
- Immutable registrations
- Retirement with historical decisions retained

# Grounding and next path

[Dataset choices](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets)

[Schema](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-dataset-schema)

[Traces to dataset](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/traces-to-dataset)

[Synthetic generation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-dataset-synthetic)

Next: E04 evaluators.
