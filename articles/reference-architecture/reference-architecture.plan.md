# E13 plan: reference architecture

## Purpose
Integrate evidence, evaluation, gates, and operational feedback without requiring
a full production agent platform.
Outcome: an architecture decision record with implemented versus conceptual boundaries.

## Audience
Architects and application/platform owners. No code in article or slides.

## Outline
1. Choose minimum architecture for the evidence source.
2. Trace immutable lineage through datasets, execution, and decisions.
3. Separate the agent harness, evaluation harness, app runtime/tool effects,
   judging, and policy; show where clean trial state and effect verification sit.
4. Secure identities, networks, and production traces.
5. Present offline sample versus cloud integration versus conceptual operations.
6. Review failure modes and deployment-readiness criteria.

## Prerequisites and boundaries
Diagram is conceptual; only the documented sample is implemented.
No Cosmos/Search/landing-zone prerequisite for recorded-output evaluation.

## References
F01: [overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview).
F09/F14: [results](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results),
[monitoring](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard).
F15/F16: [permissions](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions),
[networking](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-virtual-network).
S01: [SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python).
M01: [agent-evaluation methodology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
A01: [Agent Framework evaluation](https://learn.microsoft.com/en-us/agent-framework/agents/evaluation).

## Acceptance
Conceptual diagram, truthful implementation table, no deployment/compliance guarantees.
Diagram makes harness boundaries and isolation visible without requiring a
deployed target for recorded-output evaluation. Agent Framework is an optional,
version-specific integration, not part of the current companion.
