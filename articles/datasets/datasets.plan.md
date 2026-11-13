# E03 plan: datasets

## Purpose
Create reproducible, representative, protected evidence.
Outcome: customers can version a dataset, separate splits, and refresh it safely.

## Audience
Developers and data owners.

## Outline
1. Decide whether a reusable dataset is necessary.
2. Separate actual outputs, independent context, and references.
3. Choose turn, conversation, or simulation-seed schema.
4. Curate representative slices and protect trace-derived data.
5. Version, split, register, retain, and retire.
6. Validate JSONL and prevent acceptance-set leakage.

## Prerequisites and boundaries
Schema snippet is a recorded-turn illustration, not a universal schema.
Dataset size and thresholds are use-case decisions, not confidence guarantees.

## References
F04: [dataset selection](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets).
F05: [schema](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-dataset-schema).
F20: [traces to dataset](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/traces-to-dataset).
F23: [synthetic generation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-dataset-synthetic).

## Acceptance
Concrete row, version/split lifecycle, privacy checklist, and failure on malformed data.
