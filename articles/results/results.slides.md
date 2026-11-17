---
title: "Interpret results and compare versions"
subtitle: "E07 | Evidence before averages | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# First: is the evidence usable?

- Successful terminal run
- Verified target attribution
- Complete result pages
- Required criterion coverage

# Read the item, not only the mean

- Actual query/messages and response
- Independent context/expected effect
- Score, label, threshold, reason
- Tool results and observed outcome

# Inspect important slices

- Task and language
- Policy/document freshness
- Denied access and no-answer cases
- Tool and operating failures
- Task, grader, or environment defect?

# Compare like with like

- Same cases and measurement setup
- Paired baseline/candidate evidence
- Record target/data/evaluator/judge changes
- Repeat when nondeterminism matters

# Repeated trials answer different questions

- `pass@k`: at least one success in k attempts
- `pass^k`: success in every attempt
- State trial conditions and aggregation
- Neither is an ordinary pass rate or coverage proof

::: notes
These metrics from “Demystifying evals for AI agents” describe repeated-trial
consistency, not a Foundry result contract:
https://www.anthropic.com/research/demystifying-evals-for-ai-agents
:::

# Make uncertainty visible

- No magic dataset size
- Zero observed defects is not zero risk
- Correlated cases weaken simple estimates
- General benchmarks need application validation

# Review patterns with people

- Blind disputed comparisons where practical
- Treat clusters as hypotheses
- Preserve unresolved policy ambiguity
- Export cluster analysis before leaving

::: notes
Cluster results are not automatically persisted:
https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cluster-analysis
:::

# Write the decision report

- Coverage and invalid evidence
- Quality/safety and critical slices
- Latency, full cost, uncertainty
- Action, owner, retained lineage

# Grounding and next path

[Results](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results)

[Cluster analysis](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cluster-analysis)

[Human review](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation)

[Benchmarks](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/benchmark-evaluations)

Next: E08 release decisions.
