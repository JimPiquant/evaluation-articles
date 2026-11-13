---
title: "Choose your Foundry evaluation workflow"
subtitle: "E01 | Decision workshop | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Decide what the evidence is for

- Diagnose
- Compare candidates
- Approve release
- Detect operational drift

# Choose the unit

- Turn: one response in context
- Conversation: complete interaction outcome
- Polite turns can still form a failed journey

::: notes
Messages alone do not select conversation-level scoring. Specify the level:
https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations
:::

# Choose the source

- Recorded output or completed messages
- Newly invoked target
- Production response/trace
- Synthetic data or simulated user

# Match criteria to outcomes

- Business rubric
- Compatible quality/process checks
- Safety evidence
- Exact tool-effect assertions

# Choose the execution surface

- Portal for exploration/review
- SDK for controlled integration
- CLI or CI/CD for repeatability
- Monitoring for live sampling

::: notes
Evaluation CLI is an independently versioned preview extension:
https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/azure-developer-cli-evaluation
:::

# Write the evaluation contract

- Decision, unit, source
- Observed candidate identity
- Required evidence
- Missing/skipped results block
- Held-out data and policy owner

# Avoid the false shortcuts

- Dataset registration is not always required
- Reference answer is not actual response
- Scaffolding does not produce evidence
- Completed run is not passing coverage

# Grounding and next path

[Overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)

[Datasets](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets)

[Catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)

Next: E02 first evaluation.
