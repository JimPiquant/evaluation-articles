---
title: "Integrate an evaluation reference architecture"
subtitle: "E13 | Architecture decision briefing | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Choose the minimum architecture

- Recorded evidence does not need a full agent platform
- Target invocation adds runtime dependencies
- Traces add telemetry/access
- Continuous rules add operational ownership

# Evidence-to-decision loop

```mermaid
flowchart LR
    A[Evidence] --> B[Evaluation]
    B --> C[Coverage and results]
    C --> D[Review and policy]
    D --> E[Release]
    E --> F[Telemetry feedback]
    F --> A
```

::: notes
Conceptual flow only; no claim that Azure resources are provisioned.
:::

# Separate responsibilities

- Runtime produces responses/effects
- Evaluators measure observations
- Gate applies acceptance policy
- Humans own exceptions and risk

# Carry lineage through every step

- Data and policy versions
- Actual target/model/tool versions
- Evaluator/rubric/judge settings
- Run IDs and retained evidence

# Secure the actual workflow

- Caller, project, runtime identities
- Required model/resource scopes
- Approved trace access
- Correct network route

# Know what is implemented

- Local fixture tools and gate
- Optional recorded-output cloud path
- Publishing and local CI
- Production agent/infrastructure: not supplied

# Architecture review questions

- Can missing evidence ever pass?
- Are tool effects isolated and verified?
- Can the decision be reconstructed?
- Is live validation status explicit?

# Grounding and next path

[Overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)

[Permissions](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions)

[Networking](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-virtual-network)

Next: P01 targets and E09 operations.
