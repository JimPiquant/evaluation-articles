---
title: "Create and manage evaluation datasets"
description: "Build representative, reproducible, protected evidence and maintain its lifecycle."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Create and manage evaluation datasets

A dataset is an evidence asset. Its value comes from coverage, trustworthy labels,
and reproducibility, not from being called "golden." The
[Foundry dataset overview](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets)
also describes workflows that evaluate existing responses or traces without first
registering a reusable dataset.

Create a versioned dataset when you need regression testing, controlled comparison,
or stable review evidence. For a one-off production failure, direct response/trace
evaluation may be a better start.

## Separate what happened from what should happen

Keep the actual application response, its independent retrieved context, and the
expected answer or outcome distinct. This recorded-turn example is illustrative;
check the [schema reference](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-dataset-schema)
and evaluator mapping for your chosen surface:

```json
{
  "case_id": "return-policy-01",
  "query": "How long do I have to return an unopened item?",
  "response": "You can return it within 30 days.",
  "context": "Contoso policy v1: unopened items may be returned within 30 days.",
  "ground_truth": "30 days under policy v1",
  "slice": "policy-answer"
}
```

The context must be what the application retrieved, not a copy of its answer.
The reference must be independently approved. Add observed target/version metadata
and tool evidence outside or inside the row according to the supported schema.

Complete-conversation rows use `messages`, with tool calls/results and definitions
when relevant. Simulation rows are scenario seeds, not completed transcripts.
Do not treat these schemas as interchangeable.

## Build coverage intentionally

Start with the outcomes in your product policy. For Contoso, include ordinary
policy questions, no-answer cases, outdated or contradictory documents, authorized
order lookup, denied access, successful escalation, tool failure, and ambiguous
requests.

Cover languages, customer populations, task difficulty, and important operating
conditions. Oversample rare critical failures for diagnosis, but record that
sampling design: an enriched test-set rate is not a production prevalence estimate.

[Synthetic generation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-dataset-synthetic)
can broaden coverage from agent instructions or an inline prompt with optional
reference-file grounding. Simple Q&A and multi-turn simulation seeds are distinct
outputs. Review labels and realism.
Duplicated or near-duplicated examples can inflate confidence. Simulation adds
interaction coverage but also introduces another model's assumptions about users.

## Create development, calibration, and acceptance splits

Use development examples to tune the application. Use calibration cases to align
judges and humans. Keep acceptance cases held out from prompt/rubric optimization.
Split by conversation or related case family, not individual turns, to avoid
near-identical information appearing in both tuning and acceptance data.

Generation APIs can have different minimum SDK versions from recorded-output
evaluation. The current synthetic-generation guide specifies Projects SDK 2.8.0
or later; the companion's dependency set covers its own evaluation path, not
every newer generation workflow. Recheck capability-specific requirements rather
than upgrading or reusing a pin blindly.

Record stable case IDs, provenance, licensing/consent, slice labels, schema
version, source policy version, and content hash. Register immutable versions;
do not overwrite a dataset behind an unchanged name. Retain enough history to
reconstruct release decisions.

The [shared sample](../../samples/contoso-evaluation/README.md) supplies a small
fixture dataset and metadata. It is deliberately not advertised as a 100-row
production acceptance set.

## Validate before paying for a run

This small local check catches malformed JSONL and missing recorded-turn fields:

```python
import json
from pathlib import Path

rows = []
for number, line in enumerate(Path("recorded-turns.jsonl").read_text().splitlines(), 1):
    row = json.loads(line)
    if not isinstance(row, dict):
        raise ValueError(f"line {number}: expected an object")
    for field in ("query", "response", "context"):
        if not isinstance(row.get(field), str) or not row[field].strip():
            raise ValueError(f"line {number}: missing {field}")
    rows.append(row)
if not rows:
    raise ValueError("dataset is empty")
```

This is a shape check, not evaluator/schema compatibility validation. Validate
the selected evaluator's full required fields and level before a cloud run.

## Govern trace-derived data

[Creating datasets from production traces](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/traces-to-dataset)
can make tests more realistic, but requires tracing, appropriate access, and data
handling controls. Raw traces can contain personal data, secrets, or confidential
tool outputs.

Approve the purpose and retention, redact before reuse, restrict reviewer access,
and preserve lineage without copying sensitive values unnecessarily. Human-review
the curated cases and avoid promoting one anomalous failure into a universal label.

Retire datasets when policy or application behavior changes, not simply when the
score becomes inconvenient. Preserve the old version's decision record and
document what the new set measures differently.

Continue with [evaluator calibration](../evaluators/evaluators.md).
