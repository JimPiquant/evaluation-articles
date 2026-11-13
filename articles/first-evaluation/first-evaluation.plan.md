# E02 plan: first evaluation

## Purpose
Complete a small, honest evidence-to-decision loop before adding cloud complexity.
Outcome: baseline report passes, a regressed candidate fails, and the reader
understands what was and was not evaluated.

## Audience
Developers; workshop facilitators can use the exercises.

## Outline
1. Define the support outcome and fixture boundary.
2. Run baseline and inspect item evidence.
3. Run a regressed candidate and enforce the gate.
4. Map recorded outputs into the optional Foundry cloud path.
5. Diagnose setup failures and preserve evidence.
6. Workshop tasks and completion checklist.

## Prerequisites and boundaries
Python 3 for offline path. Optional cloud requires compatible pinned SDK, roles,
project, judge deployment, and cost approval. No live-cloud validation claim.

## References
F01: [overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview).
F03: [SDK setup](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation).
F09: [results](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results).
S01: [SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python).
S03: [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations).
F26: [portal workflow](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluate-generative-ai-app).
S04: [release-pinned groundedness example](https://github.com/Azure/azure-sdk-for-python/blob/azure-ai-projects_2.2.0/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_groundedness.py).

## Acceptance
Executable repository-root commands, linked companion, honest output semantics,
expected nonzero failure, and slides suitable for a short lab.
