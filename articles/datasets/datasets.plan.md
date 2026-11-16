# E03 plan: datasets

## Purpose
Create reproducible, representative, protected evidence.
Outcome: customers can version a dataset, separate splits, and refresh it safely.

## Audience
Developers and data owners.

## Outline
1. Define tasks from product outcomes, manual checks, and observed failures.
2. Write unambiguous inputs and success criteria; confirm tasks are solvable and
   graders accept a reference solution.
3. Demonstrate turning a vague support goal into a specific, observable criterion.
4. Balance examples where behaviors should and should not occur; add realistic
   slices and edge cases without treating enriched rates as production rates.
5. Decide whether a reusable dataset is necessary and separate actual responses,
   independent context, and references.
6. Choose turn, conversation, or simulation-seed schema.
7. Create development, grader-calibration, and held-out acceptance evidence.
8. Version, split, register, retain, and retire; prevent leakage and duplicates.
9. Validate JSONL and required evaluator fields.

## Prerequisites and boundaries
Schema snippet is a recorded-turn illustration, not a universal schema.
Dataset size and thresholds are use-case decisions, not confidence guarantees.
M01 task-design recommendations are methodology, not Foundry requirements or
fixed dataset-size prescriptions. Reference solutions help verify task
solvability and grader configuration; they are not actual application responses.
Capability and regression suites serve distinct purposes: capability evaluations
measure what an agent can do, while regression evaluations check whether prior
behavior still works. M01's example pass-rate expectations are not universal
acceptance thresholds.

## References
F04: [dataset selection](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets).
F05: [schema](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-dataset-schema).
F20: [traces to dataset](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/traces-to-dataset).
F23: [synthetic generation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-dataset-synthetic).
M01: [agent-evaluation methodology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
M03: [success criteria and tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests).

## Acceptance
Concrete task and row, reference solution, balanced coverage, distinct
capability/regression purposes, version/split lifecycle, privacy checklist,
and failure on malformed data. No fixed row-count guarantee or universal pass
threshold.
Criteria must describe observable task outcomes and meaningful edge cases;
M03's examples and numeric targets are illustrative, not Foundry contracts.
