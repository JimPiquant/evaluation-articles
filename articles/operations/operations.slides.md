---
title: "Operate and govern evaluations"
subtitle: "E09 | Operational runbook | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Evaluation is an operated service

- Execution owner
- Data/evidence owner
- Product/safety decision owner
- Platform and budget owner

# Two operating loops

- Scheduled fixed regression set
- Sampled live traffic
- Different coverage and detection needs
- Missing evidence is not a green interval

# Dependencies must exist

- Emitted traces
- Connected Application Insights
- Caller and project identity access
- Network route and retention

# Operate asynchronous runs

- Persist run IDs before polling
- Bound waits and retries
- Inspect before resubmitting billed work
- Reject failed/canceled/partial evidence

# Triage the correct failure

- Auth: identity and scope
- Network: route and DNS
- Coverage: level and mappings
- Candidate: actual failing outcome

# Govern artifact lifecycle

- Version data, evaluators, judge, policy
- Separate raw sensitive traces
- Curate approved regression cases
- Retain and retire under explicit policy

# Close the learning loop

- Review drift by slice
- Assign targeted fixes
- Replenish held-out evidence
- Track full cost and stop conditions

# Grounding and next path

[Monitoring](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard)

[Permissions](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions)

[Traces to dataset](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/traces-to-dataset)

[Regions and limits](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-regions-limits-virtual-network)

Next: E10 optimization.
