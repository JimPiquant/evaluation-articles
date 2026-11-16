# E05 plan: model and RAG responses

## Purpose
Separate retrieval defects from generation defects in support answers.
Outcome: a reproducible failed-answer diagnosis and a targeted fix.

## Audience
Developers building question-answering or RAG applications.

## Outline
1. Preserve actual response and independent retrieved context.
2. Score retrieval, answer support, relevance, correctness, source quality, and
   answer coverage separately where each has independent evidence.
3. Analyze missing, irrelevant, outdated, and contradictory evidence.
4. Add exact fixture assertions without pretending they prove groundedness.
5. Compare retrieval and generation changes with fixed lineage.

## Prerequisites and boundaries
Contoso knowledge-base subscenario; Python assertions are deterministic checks,
not implementations of Foundry evaluators.

## References
F02: [catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators).
F04: [datasets](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets).
F05: [schemas](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-dataset-schema).
F09: [results](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results).
M03: [success criteria and tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests).

## Acceptance
Independent evidence example, failure taxonomy, slices, and no self-grounding.
Where source authority or answer completeness matters, define explicit
task-specific checks rather than assuming groundedness/relevance measures them.
