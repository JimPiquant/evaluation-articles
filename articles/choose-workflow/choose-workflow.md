---
title: "Choose your Foundry evaluation workflow"
description: "Choose the unit, source of evidence, criteria, and execution surface."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Choose your Foundry evaluation workflow

Before choosing an SDK or evaluator, write down the decision: diagnose an answer,
compare two candidates, approve a release, or detect an operational regression.
That decision determines the evidence you need.

The [Foundry overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)
separates what you evaluate from how you run the evaluation. Keep those choices
independent.

## Choose the evaluation unit

A turn-level evaluation asks whether an individual response is useful, relevant,
supported, or safe in its context. A conversation-level evaluation asks whether
the whole interaction achieved the task and respected the intended process.

For Contoso Support, a clear order-status answer is a turn. Repeatedly asking
for the same information, obtaining consent, invoking a ticket tool, and confirming
the result form a conversation. Each response might be polite while the customer
still leaves without a resolution.

Use complete `messages` data for a conversation and an explicit compatible
evaluation level. The [conversation guide](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations)
states that omitted `evaluation_level` defaults to turn and incompatible
conversation evaluators can be skipped. Dataset shape alone does not select the
right semantics.

## Choose where evidence comes from

| Evidence | Good starting use | Important boundary |
|---|---|---|
| Recorded query/response/context | Diagnose known output or compare recorded candidates | Reference answer is not the response |
| Target-generated response | Compare a model/agent against fixed inputs | Verify the actual served candidate and isolate effects |
| Completed conversation | Assess a known interaction | Preserve tool messages, definitions, and results |
| Simulation seeds | Explore multi-turn behavior before release | Generated users may not represent real users |
| Production responses/traces | Investigate actual failures and operational trends | Requires authorized access, tracing, retention, and redaction |
| Synthetic test data | Broaden scenario coverage | Validate its labels, realism, and duplication |

The [dataset overview](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets)
explains that reusable datasets are not always required; existing responses or
traces can be evaluated directly. Use an immutable regression dataset when repeatable
candidate comparison matters, not as a mandatory ritual for every diagnosis.

## Select criteria before execution tooling

Choose a business rubric for domain-specific outcomes, appropriate built-in
quality and safety checks, and deterministic assertions for exact effects.
Check [supported evaluator levels and inputs](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators).
Do not enable the entire catalog by default: incompatible or irrelevant scoring
adds cost and can hide what matters.

For example, a ticket conversation needs verified ticket creation, tool/process
quality, and a rubric covering correct escalation and communication. A RAG answer
needs independent retrieved evidence. Coherence alone answers neither question.

## Write the evaluation contract

This local JSON illustrates a decision artifact, **not a Foundry request schema**:

```json
{
  "decision": "approve-support-candidate",
  "unit": "conversation",
  "source": "completed-messages",
  "candidate": "verified-deployment-version",
  "required_evidence": ["business-rubric", "tool-effects", "safety"],
  "on_missing_or_skipped": "block",
  "acceptance_data": "held-out-support-v1"
}
```

Agree this contract before tuning. The actual SDK schema, registered evaluator
names, and result mapping depend on the chosen surface and version.

## Choose how to run

Use the portal to explore a run with reviewers. Use SDK code for controlled
datasets, repeatable result retrieval, and application integration. Use CI/CD
when the decision is promotion. Use operational monitoring for sampled live
traffic. A scheduled regression job is not the same as continuous evaluation.

The [evaluation CLI](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/azure-developer-cli-evaluation)
is a separately versioned preview extension, `azure.ai.evaluations`. Its recipe
is `evals/azure.eval.yaml`; scaffolding does not deploy an agent or generate rows.
Agent CLI installation alone does not supply evaluation commands.

The [first evaluation lab](../first-evaluation/first-evaluation.md) demonstrates
the evidence-to-decision loop locally. Then choose [RAG](../rag-responses/rag-responses.md),
[conversations](../agent-conversations/agent-conversations.md), or
[release automation](../release-gates/release-gates.md).
