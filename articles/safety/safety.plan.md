# E11 plan: safety

## Purpose
Measure scenario-specific risk without claiming zero risk or runtime prevention.
Outcome: a safety evidence matrix, correct threshold semantics, and response policy.

## Audience
Developers and safety/security reviewers.

## Outline
1. Model support-agent harms and authorization boundaries.
2. Distinguish offline safety, runtime controls, and adversarial testing.
3. Select appropriate supported risk evaluators.
4. Encode correct score-boundary behavior.
5. Inspect coverage, language/slice failures, and human disagreements.
6. Act, retain, and retest.

## Prerequisites and boundaries
No harmful payload examples. Code demonstrates score boundaries only, not a
safety classifier. No legal compliance or confidence guarantee.

## References
F02: [catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators).
F08: [risk/safety](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators).
F11: [human review](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation).
F21: [red teaming](https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent).

## Acceptance
<=3/>3 boundary correct, missing results fail, stricter policy labeled, safe examples.
