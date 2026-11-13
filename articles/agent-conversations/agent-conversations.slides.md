---
title: "Evaluate agents and complete conversations"
subtitle: "E06 | Outcomes across turns | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Polite turns can fail a journey

- Repeated ineffective action
- Missing consent
- Wrong customer's order
- Ticket claimed but never created

# Choose conversation semantics

- Complete messages
- Explicit conversation level
- Compatible evaluators
- Required coverage verification

::: notes
The default level is turn; unsupported conversation evaluators may skip:
https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations
:::

# Preserve tool evidence

- Definitions and arguments
- Calls and returned results
- Independently observed effects
- Actual target/tool versions

# Measure broader outcomes

- Output Quality
- Tool Use Quality
- Task Completion and satisfaction
- Business rubric and exact controls

# Choose the source

- Completed transcripts
- Deployed trace conversations
- Simulated interaction with target
- Synthetic evidence with realism review

# Isolate effects

- Sandbox tools and synthetic customers
- Reset fixture state
- Bound generated interactions
- No production-routing toggles for tests

# Inspect the failed process

- Intent or information gathering?
- Wrong tool or invalid parameters?
- Ignored error or false confirmation?
- Missing observed candidate attribution?

# Grounding and next path

[Conversation workflow](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations)

[Simulation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-simulate-conversations)

[Rubrics](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators)

Next: E07 results; P03 tool delivery.
