# E09 plan: operations

## Purpose
Make evaluation a reliable governed service and feedback loop.
Outcome: operators have an incident/runbook checklist and clear lifecycle owners.

## Audience
Platform engineers, application operators, and data stewards.

## Outline
1. Distinguish scheduled regression runs from live-traffic sampling.
2. Configure identities, tracing, networking, and budgets.
3. Operate asynchronous runs and incomplete evidence.
4. Govern dataset/evaluator/run retention and exports.
5. Respond to drift and refresh trace-derived datasets.
6. Decommission and audit.

## Prerequisites and boundaries
No universal sampling percentage or retention period. Application Insights and
access must actually exist for trace workflows. This is not provisioned infrastructure.

## References
F04/F20: [datasets](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets),
[trace curation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/traces-to-dataset).
F09: [results](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results).
F14: [monitoring](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard).
F15/F16: [permissions](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions),
[networking](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-virtual-network).
F27: [regions and rate limits](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-regions-limits-virtual-network).

## Acceptance
Actionable runbook, privacy/budget controls, cancellation/retry policy, retention ownership.
