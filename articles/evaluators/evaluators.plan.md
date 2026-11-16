# E04 plan: evaluators

## Purpose
Measure domain outcomes with calibrated rubric, built-ins, and deterministic checks.
Outcome: a small compatible evaluator set and an agreed human calibration procedure.

## Audience
Developers and subject-matter reviewers.

## Outline
1. Map outcomes to evidence and evaluators.
2. Author a weighted support rubric.
3. Calibrate blinded cases against human judgments.
4. Pair business quality with safety and independent outcome checks.
5. Check level, fields, applicability, scale, and thresholds.
6. Version judge/rubric and track discrepancies.

## Prerequisites and boundaries
Rubric example follows documented fields but needs registration/validation for
the selected surface. No Quality Grader recommendation pending source conflict.

## References
F02: [catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators).
F07: [rubrics](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators).
F08: [safety](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators).
F11: [human evaluation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation).
F25: [custom evaluator contracts](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/custom-evaluators).

## Acceptance
Business rubric example, error/skip coverage policy, correct scales, calibration,
and clear distinction between deterministic checks and model judgment.

## TODO
- [ ] Add or review AI evaluation rubrics: confirm coverage of Contoso Support
  outcomes, clear scoring criteria and examples, explicit scales and thresholds,
  and calibration against human judgments. Distinguish documented evaluator
  behavior from illustrative customer policy.
