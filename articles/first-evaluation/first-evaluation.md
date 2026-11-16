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

This walkthrough uses the [Contoso sample](../../samples/contoso-evaluation/README.md).
It is a fixture-backed support workflow with real local tool implementations,
not a deployed or generative support agent. Its checks demonstrate deterministic
outcomes and release policy. They do **not** measure Foundry groundedness, natural
language quality, or safety.

Complete the local demo first: prepare Python, run the baseline, and explain the
deliberate regression. Then, optionally, use Foundry to evaluate the saved
responses. Cloud setup is grouped with that optional procedure; it is not a
prerequisite for the local demo.

## Define the outcome

Contoso answers knowledge-base questions, retrieves an authorized customer's
order, and creates a ticket when the workflow permits it. Evaluation needs the
actual response, independent context, tool evidence, expected outcome, and
observed candidate attribution.

The evaluation unit is an individual turn: each case contains one request and
its response and tool evidence, not a complete multi-turn conversation. Choosing
the unit and evidence before the execution tool follows the
[Foundry Evaluation overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview).

The baseline and deliberately regressed candidate make the key distinction:
an evaluation can execute successfully and still show an unacceptable candidate.

## Prepare your environment

Run all commands from the **repository root**. The baseline and regression demo
run locally with **Python 3.9+ and the standard library**. No environment
variables, credentials, Azure resources, or language model are needed.

```bash
python3 --version
```

Confirm that the version is 3.9 or newer, then continue to **Run the baseline**.
The [Contoso getting-started guide](../../samples/contoso-evaluation/docs/getting-started.md)
walks through the demo, result interpretation, and optional cloud integration.

## Run the baseline

From the repository root, with Python 3.9+, run:

```bash
python3 -m unittest discover -s samples/contoso-evaluation/tests
python3 samples/contoso-evaluation/run.py \
  --candidate baseline --output build/evaluation/baseline.json
python3 samples/contoso-evaluation/gate.py build/evaluation/baseline.json
echo $?
```

`unittest discover` finds and runs the local tests. `run.py` then executes the
baseline candidate against the regression cases and saves its responses, tool
activity, five deterministic check results, and provenance in `baseline.json`.
`gate.py` applies the sample's release policy to that report. A completed
evaluation is not itself a release pass.

`echo $?` displays the gate's numeric exit code. Run it immediately after the
gate, because `$?` holds only the most recent command's exit code. Expect **0**
and a printed JSON decision of `pass` for the baseline.

After generating `baseline.json`, paste this entire block into your terminal from the repository
root. It runs Python to read and print the saved report; it does not rerun the
evaluation:

```bash
python3 - <<'PY'
import json
from pathlib import Path

report = json.loads(Path("build/evaluation/baseline.json").read_text())
print(json.dumps(report, indent=2))
PY
```

The `<<'PY'` and closing `PY` delimit the Python input passed by Bash to
`python3 -`. Keep the closing `PY` on its own line with no indentation.

Follow the sample's documented result contract. Identify which case produced
which observation, whether the intended checks scored every required case, and
which policy made the decision. Do not infer an SDK-compatible result format
merely because a local report is JSON.

The [getting-started guide](../../samples/contoso-evaluation/docs/getting-started.md#runpy-parameter-reference)
documents `run.py` parameters. The sample's
[`policy.json`](../../samples/contoso-evaluation/policy.json) selects the release
split, expected candidate versions, required checks, coverage, and pass rates.
These are illustrative Contoso rules, not Foundry defaults.

## What failure looks like

```bash
python3 samples/contoso-evaluation/run.py \
  --candidate regressed --output build/evaluation/regressed.json
python3 samples/contoso-evaluation/gate.py build/evaluation/regressed.json
echo $?
```

`echo $?` displays the gate's numeric exit code. Expect **1**
for the deliberately regressed candidate. **0** means the gate passed;
**1** means the gate rejected the candidate or its evidence; **2** indicates an
input, argument, or execution error.

The gate also prints JSON explaining the rejection. To view the underlying
evaluation report as formatted JSON, run:

```bash
python3 -m json.tool build/evaluation/regressed.json
```

Compare a failed case's expected outcome with its recorded response, tool calls,
and resulting state. For example, `reg-ticket` claims ticket `TKT-FAKE`, but its
trace has no ticket-creation call and its recorded ticket list is empty. That
mismatch explains the failure; the candidate's name alone does not.
Tests also cover incomplete or invalid evidence: absence must not become a zero
defect rate.

This is a demonstration dataset, not a statistical certification. Passing all
fixture cases says the candidate met those checks on those cases.

## Optional: evaluate precomputed responses in Foundry

Microsoft's [Evaluate datasets guide](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-datasets)
describes evaluating **precomputed responses**: answers the application has
already produced and saved. The evaluation uses those saved answers; it does
not ask the application to generate new ones. This is the workflow used by the
sample's optional Foundry integration.

Use it to assess **groundedness**: whether the saved response is supported by
its retrieved or tool-provided context. It adds a model-judged check alongside
the local deterministic checks, not a general assessment of response quality,
safety, or successful tool execution.

`run.py` has already saved the Contoso response and its retrieved or tool-provided
context in a JSON report. `cloud.py` sends that saved response and context to
Foundry, where the groundedness evaluator judges whether the context supports
the answer. For example, a saved response claiming a 90-day return window
conflicts with retrieved policy text stating 30 days. Evaluate the actual saved
response, not the reference answer (the expected correct answer), and use
independent retrieved or tool-provided evidence as context, not the response
itself. The optional cloud integration does not rerun Contoso or correct its
saved answer.

### Prepare the cloud environment

**Skip the rest of this section if you only want the local demo.** The cloud path
requires Python 3.11, an existing authorized Foundry project, appropriate
caller/project permissions, and a supported judge deployment. See Microsoft's
[cloud evaluation setup guide](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation)
for project prerequisites. Before any upload, approve data handling and evaluation
costs. Use only synthetic or approved, redacted data: saved context can contain
customer, order, and ticket fields. Nothing in this procedure provisions resources.

The sample's tested cloud package set is Projects 2.2.0, Identity 1.25.1,
and OpenAI 2.29.0, with additional dependencies pinned in its requirements file.
It follows a [release-pinned groundedness example](https://github.com/Azure/azure-sdk-for-python/blob/azure-ai-projects_2.2.0/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_groundedness.py).
These are tested integration pins, not a "latest" recommendation or a minimum
for every Foundry capability. The [Projects SDK reference](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python)
and [official evaluation samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations)
provide additional implementation guidance; do not combine older standalone
Agents APIs with this Projects/Evals example.

From the repository root, create the cloud environment and check SDK imports
and mocked API behavior without calling Azure:

```bash
python3.11 -m venv samples/contoso-evaluation/.venv
samples/contoso-evaluation/.venv/bin/python -m pip install \
  -r samples/contoso-evaluation/requirements-cloud.txt
samples/contoso-evaluation/.venv/bin/python -m pip check
samples/contoso-evaluation/.venv/bin/python \
  samples/contoso-evaluation/cloud.py --check-sdk
```

The SDK check uses a mock transport, not live Azure validation. The sample's
live cloud integration remains unvalidated. For setup alternatives, see
[getting started: SDK checks](../../samples/contoso-evaluation/docs/getting-started.md#5-optionally-check-the-foundry-sdk-without-azure-access).

Before submission, set your project's HTTPS endpoint and the **deployment name**
of your authorized judge model. Use the **entire project endpoint URL**,
including `/api/projects/<project-name>`, not just the resource hostname.
A fictional example is
`https://contoso-eval.services.ai.azure.com/api/projects/contoso-support`.
Copy your actual endpoint from Foundry; the [SDK setup documentation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation#set-up-the-sdk-client)
describes this URL format.

```bash
export AZURE_AI_PROJECT_ENDPOINT="https://<account-name>.services.ai.azure.com/api/projects/<project-name>"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="<your-judge-deployment-name>"
```

Alternatively, put these assignments in a Bash-compatible `.env` file at the
repository root, using your real values:

```bash
AZURE_AI_PROJECT_ENDPOINT="https://<account-name>.services.ai.azure.com/api/projects/<project-name>"
AZURE_AI_MODEL_DEPLOYMENT_NAME="<your-judge-deployment-name>"
```

The sample does **not** load `.env` automatically. Load it in the same Bash
session where you will run the cloud sample:

```bash
set -a       # Automatically export subsequent variable assignments
source .env  # Load the file into the current shell
set +a       # Turn off automatic export for future assignments
```

The loaded variables remain exported after `set +a`, so Python can read them.
Only source trusted files: `source` executes shell commands, not just variable
assignments. Keep `.env` out of version control and never commit credentials.

These settings are read by `cloud.py`; they do not authenticate you. Configure
`DefaultAzureCredential` using your organization's approved identity flow.
You can alternatively pass `--endpoint` and `--judge-deployment` to `cloud.py`.

### Submit the saved responses

After confirming identity, data handling, and budget, submit the
`build/evaluation/regressed.json` report generated in the local demo:

```bash
samples/contoso-evaluation/.venv/bin/python samples/contoso-evaluation/cloud.py \
  --input build/evaluation/regressed.json \
  --output build/evaluation/cloud-regressed.json \
  --allow-upload \
  --timeout 600 \
  --poll-interval 5
echo $?
```

`--allow-upload` explicitly authorizes this command to send saved data for
evaluation and incur evaluation costs. The adapter requests only
`builtin.groundedness` at turn level and saves cloud results separately from the
local report. It does not rerun the support workflow.

### Inspect the cloud results

```bash
python3 -m json.tool build/evaluation/cloud-regressed.json
```

Inspect `status`, any `error`, the per-evaluator `summary`, and the saved
`raw_output_items`. The adapter retrieves every result page and validates the
required items, counts, and candidate/version attribution. Downloading all pages
alone does not establish valid coverage. Microsoft's
[result retrieval guide](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results)
explains cloud results; the sample's
[getting-started guide](../../samples/contoso-evaluation/docs/getting-started.md#6-optionally-submit-recorded-outputs-to-an-existing-project)
documents its report fields and operational limits.

Cloud exit **0** means the job completed and its results passed the adapter's
schema and coverage checks, even if groundedness labels fail. Exit **2** indicates
an execution or validation error. These are **advisory groundedness results**,
not a calibrated release decision. Do not pass this report to `gate.py`: that
gate accepts only the local deterministic report.

### Preserve evidence and resume retrieval

Keep the cloud report and its `eval_id` and `run_id`. A timeout stops local
waiting, not the remote job or billing. The sample does not automatically cancel
or delete cloud evaluations or runs.

If retrieval timed out or failed after both IDs were saved, resume with the same
input, endpoint, judge deployment, and output file rather than submitting again:

```bash
samples/contoso-evaluation/.venv/bin/python samples/contoso-evaluation/cloud.py \
  --input build/evaluation/regressed.json \
  --output build/evaluation/cloud-regressed.json \
  --allow-upload \
  --resume
```

If both IDs are not available, inspect the project before another submission;
do not invent missing IDs or assume the remote job did not start. Cancellation
and deletion are separate decisions under your retention and budget policy.

## Try it yourself

1. Explain one case using independent expected evidence and observed tool output.
2. Find a regression and state why it violates the declared policy.
3. Remove required evidence from a copy of the report and confirm rejection.
4. Propose a business rubric that tests a useful outcome the fixture cannot judge.

Do not upload real customer traces for the exercise. Use synthetic or approved,
redacted material.

You are ready to expand when you can explain a pass, a failure, missing evidence,
and the boundary between deterministic checks and model judgment.

## Next steps

Continue with [datasets](../datasets/datasets.md) and [results](../results/results.md).
For a different workflow, Microsoft's
[Evaluate models and agents guide](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-targets)
explains evaluating **responses generated at run time**: the evaluation sends
test inputs to a deployed model or agent, collects new answers, and evaluates
those answers instead of saved ones. This sample does not implement that
workflow.

For a portal-led alternative, see Microsoft's
[portal evaluation guide](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluate-generative-ai-app).
Choose a workflow deliberately: evaluating existing answers and generating new
ones measure different application executions.
