# E10 plan: optimization

## Purpose
Improve the application and measurement process without acceptance-set leakage.
Outcome: a controlled experiment with quality, risk, latency, and cost tradeoffs.

## Audience
Developers and application owners.

## Outline
1. Fix the dominant failure rather than blindly optimize scores.
2. Separate application changes, measurement changes, and evaluation cost;
   keep a controlled comparison fixed except for the declared intervention.
3. Explain Prompt Optimizer versus Agent Optimizer.
4. Freeze baseline/data/judge and preserve held-out acceptance.
5. Compare candidates and require human review/redeployment.
6. Stop, rollback, or broaden evidence when tradeoffs are unacceptable.

## Prerequisites and boundaries
Optimizer support and preview restrictions are target-specific. Offline commands
compare fixture candidates only, not a claimed optimization service.

## References
F07: [rubric](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators).
F09: [results](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results).
F17: [Prompt Optimizer](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/prompt-optimizer).
F18: [Agent Optimizer](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview).
M01: [agent-evaluation methodology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
M03: [success criteria and tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests).

## Acceptance
Held-out evidence, safety constraints, no auto-promotion, and complete cost boundary.
Do not treat rubric/judge/task/environment changes as application improvement;
declare them as measurement or evaluation-design experiments and re-establish
held-out acceptance when its evidence has informed tuning.
