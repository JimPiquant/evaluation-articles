# E06 plan: agents and conversations

## Purpose
Assess whole-interaction outcomes and observable tool behavior.
Outcome: customers can select conversation-compatible evaluators and verify
task completion against real effects.

## Audience
Agent developers with familiarity from E01-E04.

## Outline
1. Explain why successful turns can still form a failed conversation.
2. Distinguish the agent harness from the evaluation harness; preserve complete
   messages, tool definitions/results, and target provenance.
3. Run repeatable trials in a clean, isolated environment and independently
   verify tool effects.
4. Select Output Quality, Tool Use Quality, satisfaction, completion, and rubric.
5. Separate recorded conversations from target simulation and production traces.
6. Verify evaluator coverage and side effects.
7. Diagnose frustration, repeated tool use, false success, task/grader/environment
   failures, and missing permission.
8. Introduce Agent Framework's evaluation integration as a separate optional
   implementation path, with language/package-version boundaries.

## Prerequisites and boundaries
SDK snippet constructs a current criterion, not a complete submitted run.
Offline companion is a fixture process, not a generative multi-turn agent.

## References
F02: [catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators).
F06: [conversations](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations).
F07: [rubrics](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators).
F19: [simulation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-simulate-conversations).
S01: [Projects SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python).
M01: [agent-evaluation methodology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
A01: [Agent Framework evaluation](https://learn.microsoft.com/en-us/agent-framework/agents/evaluation).

## Acceptance
Explicit conversation level and skip policy; no success by self-report or version fallback.
Explain harness roles and trial isolation without implying that Foundry requires a
particular harness design. Separate Agent Framework APIs from Foundry service
contracts and label the companion as a deterministic fixture, not a generative
agent or framework integration.
