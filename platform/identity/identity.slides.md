---
title: "Secure evaluation identities and networks"
subtitle: "P02 | Platform access review | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Begin with the workflow

- Recorded outputs
- Model/agent invocation
- Trace evaluation
- Scheduled/continuous rules

# Separate identities

- Human/application caller
- Project managed identity
- Application runtime
- Role-assignment administrator

# Match scopes to operations

- Project evaluation access
- Account scope for model inference
- Trace/storage-specific access
- No one-role-fits-all shortcut

::: notes
Contributor alone does not grant roleAssignments/write. Use the source's
workflow matrix, not a blanket role recommendation.
:::

# Names changed, core IDs did not

- Foundry User
- Foundry Owner
- Foundry Account Owner
- Foundry Project Manager

# Match federation to context

- Branch, PR, or environment subject
- No cloud secrets for untrusted PRs
- Protected acceptance data and budget
- Offline tests remain credential-free

# Verify network separately

- Runner location and approved route
- Private endpoint DNS
- Storage and telemetry connectivity
- Auth failure is not a network diagnosis

# Govern and retire

- Redact traces before reuse
- Restrict evidence access
- Review unused grants/connections
- Retain required decision history

# Grounding and next path

[Permissions](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions)

[Evaluation networks](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-virtual-network)

Next: E09 operations.
