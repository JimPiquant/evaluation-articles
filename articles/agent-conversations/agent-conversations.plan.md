# E06 plan: agents and conversations

## Purpose
Assess whole-interaction outcomes and observable tool behavior.
Outcome: customers can select conversation-compatible evaluators and verify
task completion against real effects.

## Audience
Agent developers with familiarity from E01-E04.

## Outline
1. Explain why successful turns can still form a failed conversation.
2. Preserve messages, tool definitions/results, and target provenance.
3. Select Output Quality, Tool Use Quality, satisfaction, completion, and rubric.
4. Separate recorded conversations from target simulation and production traces.
5. Verify evaluator coverage and side effects.
6. Diagnose frustration, repeated tool use, false success, and missing permission.

## Prerequisites and boundaries
SDK snippet constructs a current criterion, not a complete submitted run.
Offline companion is a fixture process, not a generative multi-turn agent.

## References
F02: [catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators).
F06: [conversations](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations).
F07: [rubrics](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators).
F19: [simulation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-simulate-conversations).
S01: [Projects SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python).

## Acceptance
Explicit conversation level and skip policy; no success by self-report or version fallback.
