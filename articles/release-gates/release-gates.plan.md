# E08 plan: automated release decisions

## Purpose
Enforce measurable evidence-based policy with reliable CI failure semantics.
Outcome: required evidence blocks a deliberately degraded or incomplete candidate.

## Audience
Developers and CI/CD engineers.

## Outline
1. Separate successful evaluation execution from candidate acceptance.
2. Centralize policy and verify normalized result shape.
3. Demonstrate offline good/bad gates.
4. Map the workflow to Foundry SDK, Actions, or preview CLI.
5. Secure identity and preserve evidence.
6. Release, rollback, and exception handling.

## Prerequisites and boundaries
Local root workflow requires no cloud identity. Actual cloud gates need exact
schema adapters and tested credentials; no policy inferred from an action name.

## References
F06: [skip semantics](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations).
F09: [results](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results).
F12: [Actions](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluation-github-action).
F13: [CLI](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/azure-developer-cli-evaluation).
F15: [permissions](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions).
F24: [Azure DevOps extension](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluation-azure-devops).

## Acceptance
Runnable CLI gate, explicit negative test, missing evidence fails, persisted results.
