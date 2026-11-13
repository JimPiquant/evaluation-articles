# P03 plan: tool delivery

## Purpose
Evaluate actual candidate tool contracts and effects, not an unused endpoint.
Outcome: staged tool promotion with deterministic and conversation-level evidence.

## Audience
Developers and CI/CD engineers.

## Outline
1. Separate function, OpenAPI, and MCP tool contracts.
2. Exercise real implementations in an isolated fixture environment.
3. Verify authorization, inputs, effects, and output semantics.
4. Add tool/process quality and business-rubric conversation evaluation.
5. Attribute tool versions and wire the gate to deployment.
6. Roll back incompatible contracts.

## Prerequisites and boundaries
Sample fixture tools are not live CRM services. Current SDK connection APIs must
be checked before implementation; no illustrative create_or_update deployment.

## References
F02/F06: [catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators),
[tool conversations](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations).
F12: [CI integration](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluation-github-action).
S01: [Projects SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python).

## Acceptance
Concrete fixture command, consistent evidence/policy, no simulated endpoint validation.
