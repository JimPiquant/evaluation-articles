# E04 plan: evaluators

## Purpose
Measure domain outcomes with calibrated rubric, built-ins, and deterministic checks.
Outcome: a small compatible evaluator set and an agreed human calibration procedure.

## Audience
Developers and subject-matter reviewers.

## Outline
1. Map outcomes to evidence and evaluators.
2. Choose code-based, model-based, and human grading methods for the questions.
3. Distinguish methodology categories from Foundry evaluator interfaces and
   custom-evaluator implementation types.
4. For coding-agent tasks, illustrate unit tests for correctness plus an
   optional model-based rubric for overall code quality.
5. Author a weighted support rubric.
6. Test grader validity with known-good, known-bad, and ambiguous cases;
   distinguish task, grader, and application failures.
7. Calibrate model graders against independent human judgments and inspect bias
   and drift across meaningful slices.
8. Pair business quality with safety and independent outcome checks.
9. Check level, fields, applicability, scale, and thresholds.
10. Version judge/rubric and track discrepancies.

## Prerequisites and boundaries
Rubric example follows documented fields but needs registration/validation for
the selected surface. M01's code-based/model-based/human grader categories
describe evaluation methodology, not Foundry API types. Foundry evaluators and
custom evaluator implementation types have separate documented contracts.
Choose deterministic graders where appropriate, model graders when interpretation
is needed, and human review for calibration and disputes. No Quality Grader
recommendation pending source conflict. Attribute the coding-agent grader
combination to M01; it is a contextual example, not a Foundry requirement or
prescription for every task.

## References
F02: [catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators).
F07: [rubrics](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators).
F08: [safety](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators).
F11: [human evaluation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation).
F25: [custom evaluator contracts](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/custom-evaluators).
M01: [grader methodology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
M02: [safety-evaluation methodology](https://www.anthropic.com/research/building-strong-safety-evaluations).

## Acceptance
Define code-based, model-based, and human graders with examples, strengths, and
limitations; distinguish these methodology categories from Foundry evaluator
interfaces and custom-evaluator types. Include M01's coding-agent example of
unit tests for correctness with an optional model-based rubric for overall code
quality, clearly attributed and scoped. Include a business rubric, error/skip
coverage policy, correct scales, human calibration, and evidence that can
distinguish application failures from task/grader failures. Exercise grader
validity on known-good, known-bad, and ambiguous cases; record slice-level
disagreement and review judge changes as measurement changes.

## TODO
- [ ] Add or review AI evaluation rubrics: confirm coverage of Contoso Support
  outcomes, clear scoring criteria and examples, explicit scales and thresholds,
  and calibration against human judgments. Distinguish documented evaluator
  behavior from illustrative customer policy.
