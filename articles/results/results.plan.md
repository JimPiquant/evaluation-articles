# E07 plan: results

## Purpose
Turn scores into actionable failure diagnosis and defensible version comparisons.
Outcome: a comparison report with coverage, slices, uncertainty, and next action.

## Audience
Developers and application owners.

## Outline
1. Validate run completion, attribution, pagination, and coverage.
2. Read scores, labels, reasons, thresholds, and item evidence.
3. Slice failures and review disagreements with humans.
4. Compare paired candidate/baseline observations.
5. Explain uncertainty and cost/latency boundaries.
6. Export and preserve decision artifacts.

## Prerequisites and boundaries
Local report inspection is executable. Statistical example is illustrative, not a
universal policy. Cluster analysis needs explicit export before leaving.

## References
F09: [results API](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results).
F10: [cluster analysis](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cluster-analysis).
F11: [human review](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation).
F22: [benchmark packages](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/benchmark-evaluations).

## Acceptance
No score-only decisions, no uniform result schema assumption, and uncertainty explanation.
