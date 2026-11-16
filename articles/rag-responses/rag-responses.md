---
title: "Evaluate model and RAG responses"
description: "Separate retrieval, answer support, relevance, and correctness."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Evaluate model and RAG responses

An incorrect RAG answer can result from missing evidence, irrelevant retrieval,
outdated policy, or generation that ignores good evidence. A single average
groundedness score does not tell you which layer to fix.

Use the Contoso knowledge-base scenario as part of the same support journey, not
a disconnected benchmark. Preserve what the application actually retrieved and
answered, then compare it with independent approved evidence.

## Capture a reproducible case

Record query, actual response, retrieved context/document IDs, expected outcome,
target version, retrieval configuration, model/settings, and policy version.
The [dataset schema](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-dataset-schema)
and selected evaluator determine the service mapping.

For example, a customer asks about unopened-item returns. The application retrieves
policy v1 with a 30-day window but answers 60 days. That is a generation/support
failure. If it retrieves an obsolete 60-day policy and accurately quotes it, the
answer can be grounded yet operationally incorrect.

Never substitute the reference answer for the actual response, or pass the
response as its own context. Those shortcuts produce reassuring numbers without
application evidence.

## Measure different layers

Use the [catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)
to select supported checks. Document Retrieval evaluates retrieval against
appropriate relevance labels; answer-level checks address support and usefulness.
Similarity can compare with a reference, but legitimate paraphrases and incorrect
near-matches require interpretation.

| Failure | Evidence to inspect | Likely intervention |
|---|---|---|
| Relevant document absent | Retrieval results and approved labels | Indexing, query transformation, filters, recall |
| Irrelevant content dominates | Rank/order and labels | Ranking, chunking, precision, reranking |
| Obsolete policy retrieved | Document version and effective date | Governance, indexing freshness, metadata filters |
| Answer contradicts good context | Response plus retrieved passages | Instructions, model choice, context packaging |
| No answer but confident assertion | Unanswerable slice and response | Abstention/escalation policy |
| Correct answer, poor usability | Rubric reasons and human review | Communication and task framing |

Groundedness measures support from supplied context, not independent factual
truth. Relevance measures responsiveness, not guaranteed correctness. Use a
business rubric and outcome checks to cover what each built-in leaves out.
When policy authority or answer completeness matters, define those as separate
task-specific criteria: for example, require the effective approved policy
version and check that every material sub-question is addressed. A relevance or
groundedness score alone does not establish source authority or coverage.
See [M03's success-criteria guidance](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
for methodology; this is not a Foundry evaluator contract.

## Add exact checks where they help

For fixture-backed order lookup, assert an authorized result rather than asking
a language model to judge whether a number appears plausible:

```python
def verify_order(observation, expected):
    if observation["customer_id"] != expected["customer_id"]:
        raise ValueError("customer attribution mismatch")
    if observation["order_id"] != expected["order_id"]:
        raise ValueError("wrong order")
    if observation["status"] != expected["status"]:
        raise ValueError("incorrect status")
```

This demonstrates a deterministic outcome assertion. It is not an implementation
of Foundry groundedness and does not establish access-control enforcement by
itself; separately test denied access and real tool authorization.

## Compare controlled candidates

Change retrieval or generation deliberately. Keep dataset version, evaluator
mapping, judge settings, and relevant target settings fixed. If both retrieval
and prompt change, describe a combined intervention rather than attributing the
gain to one setting.

Report per-case and slice differences: no-answer cases, contradictory sources,
policy versions, languages, and complex requests. Better average performance
can conceal worse abstention or higher-risk failures.

Use [result retrieval](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results)
to preserve reasons and evidence. Review disagreement with domain experts before
expanding the acceptance set. A fixed [dataset](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets)
supports repeatability; trace-derived cases broaden realism after approval.

Continue with [result analysis](../results/results.md) and
[controlled optimization](../optimization/optimization.md).
