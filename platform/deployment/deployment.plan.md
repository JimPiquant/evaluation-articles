# P01 plan: evaluation targets

## Purpose
Select and isolate an application target that can produce attributable evidence.
Outcome: an evaluation-target deployment checklist, not a full platform build.

## Audience
Architects and application owners. No code.

## Outline
1. Recognize when no target deployment is necessary.
2. Compare prompt and hosted targets and label API generations.
3. Preserve actual version/model/tool provenance.
4. Isolate fixture effects and production routing; reset state and preserve
   repeatable, representative evaluation conditions for each trial.
5. Review optimizer/trace requirements.
6. Validate before live evaluation.

## Prerequisites and boundaries
No universal durability/cold-start/idle-cost claims; no untested IaC.

## References
F01/F03: [overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview),
[setup](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation).
F18: [optimizer](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview).
S01/S02: [Projects SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python),
[Agents SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python).
M01: [agent-evaluation methodology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

## Acceptance
Generation and target distinctions, isolation checklist, actual provenance required.
Explain clean trial setup and environment fidelity as reproducibility practices,
not universal service requirements.
