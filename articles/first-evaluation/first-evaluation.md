---
title: "Run and understand your first evaluation"
description: "Complete a small evidence-to-decision loop and distinguish fixtures from model evaluation."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Run and understand your first evaluation

Your first evaluation should have a result you can explain and a failure you can
reproduce. Start small enough to inspect every case. Then add model judgment and
cloud execution without losing evidence or gate semantics.

This lab uses the [Contoso companion](../../samples/contoso-evaluation/README.md).
It is a fixture-backed support workflow with real local tool implementations,
not a deployed or generative support agent. Its checks demonstrate deterministic
outcomes and release policy. They do **not** measure Foundry groundedness, natural
language quality, or safety.

## Define the outcome

Contoso answers knowledge-base questions, retrieves an authorized customer's
order, and creates a ticket when the workflow permits it. Evaluation needs the
actual response, independent context, tool evidence, expected outcome, and
observed candidate attribution.

The baseline and deliberately regressed candidate make the key distinction:
an evaluation can execute successfully and still show an unacceptable candidate.

## Run the baseline

From the repository root, with Python 3:

```bash
python3 -m unittest discover -s samples/contoso-evaluation/tests
python3 samples/contoso-evaluation/run.py \
  --candidate baseline --output build/evaluation/baseline.json
python3 samples/contoso-evaluation/gate.py build/evaluation/baseline.json
```

Inspect the report rather than stopping at the exit code:

```python
import json
from pathlib import Path

report = json.loads(Path("build/evaluation/baseline.json").read_text())
print(json.dumps(report, indent=2))
```

Follow the companion's documented result contract. Identify which case produced
which observation, whether the intended checks scored every required case, and
which policy made the decision. Do not infer an SDK-compatible result format
merely because a local report is JSON.

## Prove that failure is visible

```bash
python3 samples/contoso-evaluation/run.py \
  --candidate regressed --output build/evaluation/regressed.json
python3 samples/contoso-evaluation/gate.py build/evaluation/regressed.json
```

The last command must return nonzero. Compare its evidence with the baseline.
Look for the actual failed effect or response, not just the candidate label.
Tests also cover incomplete or invalid evidence: absence must not become a zero
defect rate.

This is a demonstration dataset, not a statistical certification. Passing all
fixture cases says the candidate met those checks on those cases.

## Add Foundry evaluation deliberately

For open-ended response quality, use the companion's optional cloud integration
and the [current cloud evaluation setup](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation).
It requires an authorized project, appropriate caller/project permissions,
compatible pinned dependencies, and a supported judge deployment. Expect charges
for judging and any generated target responses or simulations.

Recorded-output evaluation scores the captured application response. It should
not replace that response with the reference answer or use the response as its
own grounding context. A target-generated workflow creates fresh responses;
it does not simply re-score the stored answer.

The [Projects SDK reference](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python)
and [official evaluation samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations)
ground the implementation. Use the companion's pinned integration instructions,
not a blend of older standalone Agents APIs and current Evals code.

Cloud runs are asynchronous. Preserve evaluation/run identifiers, inspect terminal
status, retrieve all item pages, and validate required coverage before applying
a gate. [Result retrieval guidance](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results)
describes the service result surface; adapt it explicitly rather than assuming
it equals the fixture report.

The companion's tested cloud package set is Projects 2.2.0, Identity 1.25.1,
and OpenAI 2.29.0, with additional dependencies pinned in its requirements file.
It follows a [release-pinned groundedness example](https://github.com/Azure/azure-sdk-for-python/blob/azure-ai-projects_2.2.0/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_groundedness.py).
These are tested integration pins, not a "latest" recommendation or a minimum
for every Foundry capability.

After following the companion's optional environment setup, check imports and
mocked API behavior without Azure access:

```bash
samples/contoso-evaluation/.venv/bin/python \
  samples/contoso-evaluation/cloud.py --check-sdk
```

For an existing authorized project and approved data/budget, the
[companion guide](../../samples/contoso-evaluation/docs/getting-started.md) gives
the upload, timeout, and resume commands. That path produces advisory groundedness
evidence; its completion is not a calibrated cloud release pass. The offline
gate intentionally rejects the separate cloud report contract.

### Portal alternative

For a reviewer-led first run, use the
[portal workflow](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluate-generative-ai-app).
Choose **Dataset** to score preexisting outputs without rerunning the agent;
choose a model/agent target when fresh generation is intended. Supply the
compatible data, select criteria and judge where required, review the configured
target/mappings, and submit. Inspect item results and coverage after completion.
Do not choose target generation merely because your recorded rows contain a
model response: that changes what evidence is being measured.

## Workshop exercises

1. Explain one case using independent expected evidence and observed tool output.
2. Find a regression and state why it violates the declared policy.
3. Remove required evidence from a copy of the report and confirm rejection.
4. Propose a business rubric that tests a useful outcome the fixture cannot judge.

Do not upload real customer traces for the exercise. Use synthetic or approved,
redacted material.

You are ready to expand when you can explain a pass, a failure, missing evidence,
and the boundary between deterministic checks and model judgment. Continue with
[datasets](../datasets/datasets.md) and [results](../results/results.md).
