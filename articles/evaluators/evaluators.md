---
title: "Define and calibrate evaluators"
description: "Combine business rubrics, built-in checks, and observable outcomes."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Define and calibrate evaluators

An evaluator should answer a question that affects a customer decision. Start
with outcomes and evidence, then consult the
[built-in catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators).
Do not turn on every available metric and hope the averages explain quality.

## Map criteria to evidence

| Question | Useful evidence |
|---|---|
| Did the customer get a correct policy answer? | Approved business rubric, independent context/reference |
| Did the agent use the right tool correctly? | Tool definitions, calls, inputs, results, and observable effects |
| Was escalation completed? | Ticket record plus conversation, not assistant self-report |
| Was the interaction safe? | Appropriate supported safety checks and human review |
| Was the experience useful across turns? | Conversation-level quality, completion, and satisfaction |

Use deterministic checks for exact values and effects. Use model judgment for
open-ended qualities. Retain human review for calibration and disputed decisions.

## Express quality with a business rubric

The [rubric guidance](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators)
recommends a rubric as the primary agent-quality measure, paired with relevant
built-ins. Its dimensions have stable IDs, descriptions, weights, and optional
`always_applicable`. Dimensions score 1-5; the weighted total is normalized to
0-1. Do not compare that total directly with a different evaluator's raw scale.

This starting rubric illustrates documented fields; register and validate it
through the selected supported workflow:

```json
[
  {
    "id": "correct_resolution",
    "description": "Resolves the support request using the current policy and observed tool results; never claims an unconfirmed action.",
    "weight": 9
  },
  {
    "id": "appropriate_escalation",
    "description": "Obtains required information and confirmation, then escalates unresolved issues without repeated ineffective actions.",
    "weight": 5
  },
  {
    "id": "clear_communication",
    "description": "States the outcome and next step accurately and concisely, including limitations.",
    "weight": 3,
    "always_applicable": true
  }
]
```

These weights are editorial examples, not Foundry defaults. Describe score
anchors in the domain instructions so "acceptable" means the same thing to
reviewers. Do not treat a high rubric score as permission to access another
customer's data: authorization needs enforcement and exact checks.

## Calibrate before gating

Select blinded acceptable, unacceptable, and ambiguous cases from calibration
data. Ask reviewers to rate independently and explain reasons. Run the judge
with the same inputs, then inspect disagreements rather than optimizing only
an aggregate agreement number.

Refine vague criteria and incorrect references. Preserve genuine disagreements:
they may expose policy ambiguity rather than judge failure. Recheck alignment
by language, task type, and difficult slice. The
[human evaluation workflow](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation)
provides a managed review path.

Version the rubric, judge deployment/settings, and mapping. A judge change is a
measurement change, not automatically an application improvement.

## Add a custom evaluator when the contract needs it

The [custom evaluator reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/custom-evaluators)
distinguishes three implementations:

| Type | Useful for | Contract boundary |
|---|---|---|
| Code-based | Exact format/domain rules | `grade(sample, item)` returns a float 0-1; sandbox has no network |
| Prompt-based | Semantic domain judgment | Declared score type and JSON `result`/`reason` |
| Endpoint-based | Proprietary/networked scoring | Operated endpoint with documented request/result schema |

For recorded datasets, code grades fields on `item`; generated-target access is
a different documented pattern and is explicitly subject to API change. Register
the evaluator and initialization parameters through the selected current workflow;
a local Python function is not automatically a registered service evaluator.

Treat a legitimate bad outcome as a score failure, and infrastructure/malformed
input as invalid evidence. The service can record a code exception or timeout as
score 0 **with an error state**. Preserve that state and block required evidence
errors rather than treating all zeros as successfully graded cases. This series
does not recommend silent success-shaped fallback scores.

Endpoint evaluation adds authentication, privacy, network, operational latency,
and failure responsibilities. It is not a shortcut around evidence governance.
Custom capabilities and sandbox restrictions must be checked per surface/version.

## Verify compatibility and coverage

For every criterion record supported turn/conversation level, required fields,
initialization parameters, score direction, threshold, applicability, and error
policy. Missing tool traces cannot become proof of accurate tool use. Unsupported
evaluators may skip; required skips block the decision.

Output Quality and Tool Use Quality are composites. Customer Satisfaction and
Task Completion address broader outcomes. Select them according to current level
support and your domain rubric rather than assuming an evaluator name proves
compatibility.

The catalog's Quality Grader listing conflicts with the conversation guide's
deprecation statement. This series avoids recommending it for new workflows;
see [the discrepancy register](../../references/grounding.md).

## Keep safety semantics separate

Pair the rubric with appropriate [risk/safety evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators).
For the documented content-harm threshold 3, scores <=3 pass and >3 fail.
A stricter organization policy must be named explicitly. Never assume every
safety evaluator has the same scale or result fields.

Acceptance should include required coverage, outcome constraints, safety limits,
and human exceptions, not merely one weighted average. Continue with
[RAG responses](../rag-responses/rag-responses.md) or
[complete conversations](../agent-conversations/agent-conversations.md).
