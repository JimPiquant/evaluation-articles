---
title: "Automate evaluations and release decisions"
subtitle: "E08 | Policy that really blocks | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Two different successes

- Evaluation execution completed
- Candidate met acceptance policy
- Retain evidence for both outcomes

# Centralize the contract

- Required criteria and coverage
- Actual candidate version
- Threshold direction and scale
- Critical slices and exception owner

# Fail closed

- Missing/invalid metrics
- Zero or inconsistent counts
- Required skips/errors
- Unknown version or incomplete pages

# Diagnose partial credit; gate required evidence

- Partial scores explain progress
- Required missing/error/skip still blocks
- Disclose approved analytical exclusions
- Never turn incomplete coverage into a pass

::: notes
The distinction between diagnostic partial credit and the local release policy
is grounded in “Demystifying evals for AI agents”:
https://www.anthropic.com/research/demystifying-evals-for-ai-agents
:::

# Prove the negative case

- Baseline generation succeeds
- Baseline gate passes
- Regressed generation succeeds
- Regressed gate returns nonzero

::: notes
An expected candidate rejection must not hide a crashed evaluation command.
The root evaluation CI workflow exercises the offline fixture path.
:::

# Choose cloud execution deliberately

- SDK with explicit result adapter
- Agent Framework orchestration: verify result-to-policy mapping
- Foundry evaluation Action
- Preview CLI recipe and fail-on policy
- Equivalent evidence contract in Azure DevOps

::: notes
Agent Framework is a separate, language/package-specific integration and is not
implemented by the local fixture:
https://learn.microsoft.com/en-us/agent-framework/agents/evaluation
:::

# Protect the pipeline

- Workload federation for actual subject
- No privileged secrets for untrusted PRs
- Isolated target and tools
- Protected acceptance data and budget

# Promotion is a decision

- Persist lineage and results
- Apply independent safety/outcome constraints
- Human-owned exceptions with expiry
- Application/tool rollback plan

# Grounding and next path

[GitHub integration](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluation-github-action)

[Evaluation CLI](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/azure-developer-cli-evaluation)

[Permissions](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions)

[Azure DevOps](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluation-azure-devops)

Next: E09 operations.
