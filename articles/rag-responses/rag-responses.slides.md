---
title: "Evaluate model and RAG responses"
subtitle: "E05 | Diagnose the right layer | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# One wrong answer, several causes

- Missing relevant document
- Irrelevant retrieval
- Obsolete policy
- Generation ignores good evidence

# Preserve the case

- Query and actual response
- Retrieved context and document versions
- Independent expected outcome
- Target/retrieval/model configuration

# Grounded is not always correct

- Faithful answer to obsolete context
- Useful phrasing with incorrect fact
- Similar wording with wrong meaning
- Judge explanation is not independent proof

# Separate measurements

- Retrieval relevance/coverage
- Answer support
- Query relevance
- Business correctness and usability

# Add exact checks

- Authorized customer attribution
- Correct order/status
- Persisted ticket effect
- Denied access and error behavior

::: notes
Exact fixture assertions are not Foundry groundedness or safety evaluators.
:::

# Change one layer deliberately

- Retrieval versus generation
- Fixed dataset and judge
- Paired baseline/candidate cases
- Critical slices, not only averages

# Decide the intervention

- Missing evidence: retrieval/index
- Stale policy: governance/freshness
- Contradiction: instructions/context
- Unsupported assertion: abstention/escalation

# Grounding and next path

[Catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)

[Schema](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-dataset-schema)

[Results](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results)

Next: E07 results; E10 optimization.
