# Getting started

Run all commands below from the **repository root**, not this docs folder. Offline commands use Python 3.9+ and the standard library.

## 1. Produce actual application evidence

```bash
python3 -m unittest discover -s samples/contoso-evaluation/tests
python3 samples/contoso-evaluation/run.py --candidate baseline --output build/evaluation/baseline.json
python3 samples/contoso-evaluation/run.py --candidate regressed --output build/evaluation/regressed.json
```

Both runs should say `completed`. The intentionally failing candidate still completed evaluation: some checks scored zero. An evaluator/tool error is different; it makes the run `error` and the runner exit 2. Invalid input replaces stale output with explicit error evidence instead of leaving a prior success file behind.

Explore alternative splits with `--split development` or `--split holdout`. The release gate expects the complete regression split specified in `policy.json`, so it will reject those experiment reports.

### `run.py` parameter reference

`run.py` executes the local fixture-backed candidate, or evaluates supplied
recordings, and writes a JSON report. Display its built-in help with:

```bash
python3 samples/contoso-evaluation/run.py --help
```

| Parameter | Meaning |
|---|---|
| `--candidate` | **Required.** Candidate name registered in `policy.json`, such as `baseline` or `regressed`. |
| `--output` | **Required.** File path for the JSON evaluation report. |
| `--split` | Optional: `development`, `regression`, or `holdout`. Defaults to the release split in `policy.json`, currently `regression`. |
| `--records` | Optional path to a JSON array of externally collected fixture-scenario records. Evaluates those records instead of executing the local candidate. Must be a different file from `--output`. See [the application/collector boundary](#4-understand-the-applicationcollector-boundary) for the record format and an example. |

Exit code **0** means evaluation completed, even if checks failed. Exit code
**2** indicates an execution, input, or argument error. Use `gate.py` separately
to apply the release policy; a completed evaluation is not a release pass.

## 2. Inspect the failure before using an average

```bash
python3 - <<'PY'
import json
from pathlib import Path
report = json.loads(Path("build/evaluation/regressed.json").read_text())
print(json.dumps(report["summary"], indent=2))
item = next(item for item in report["items"] if item["item_id"] == "reg-ticket")
print(json.dumps(item, indent=2))
PY
```

For `reg-ticket`, compare:

- `expected.tools`: lookup followed by ticket creation;
- `record.trace`: only lookup actually ran;
- `record.response`/`record.outcome`: claimed ticket `TKT-FAKE`;
- `record.state.tickets`: empty;
- `evaluations.ticket_state`: completed, score 0, `passed: false`.

The local functions have no real external side effects. This example demonstrates why an assistant's success claim is not evidence of a committed transaction.

The output shape includes these fields (this fragment is **not** a complete gate input):

```json
{
  "schema_version": "contoso.offline-evaluation/1",
  "kind": "offline-deterministic",
  "status": "completed",
  "expected_item_count": 8,
  "evaluated_item_count": 8,
  "summary": {
    "ticket_state": {
      "expected": 8,
      "evaluated": 8,
      "passed": 7,
      "failed": 1,
      "skipped": 0,
      "errors": 0,
      "pass_rate": 0.875
    }
  }
}
```

Every real report includes **all five** required evaluator aggregates and detailed results for every registered case. `policy.json` defines the gate rates; do not recreate a second threshold table in CI.

## 3. Enforce the release decision

```bash
python3 samples/contoso-evaluation/gate.py build/evaluation/baseline.json
```

Expected stdout:

```json
{"decision": "pass", "failures": []}
```

The command below should exit 1 and identify failed case IDs:

```bash
python3 samples/contoso-evaluation/gate.py build/evaluation/regressed.json
echo $?
```

`echo $?` displays the gate's numeric exit code. Check it immediately after the
gate; `$?` holds only the most recent command's exit code. **0** means the gate
passed, **1** means it rejected the candidate or its evidence (expected for
`regressed`), and **2** indicates an input, argument, or execution error.

The gate prints JSON explaining the rejection. To inspect the underlying
evaluation report as formatted JSON:

```bash
python3 -m json.tool build/evaluation/regressed.json
```

To test that contract safely in a shell script:

```bash
if python3 samples/contoso-evaluation/gate.py build/evaluation/regressed.json; then
  echo "ERROR: a deliberately bad candidate passed"
  exit 1
else
  status=$?
  test "$status" -eq 1  # A measured rejection, not malformed JSON or a missing file.
fi
```

In a real pipeline, also bind to the intended candidate:

```bash
python3 samples/contoso-evaluation/gate.py build/evaluation/baseline.json --expected-candidate baseline
```

Wrong/missing versions are errors, not substitutions or harmless exclusions. The gate verifies current fixture, code, data and policy fingerprints and recomputes detailed checks. Keep the originating report and gate decision together.

## 4. Understand the application/collector boundary

`contoso/app.py` is an executable fixture-backed target. It does not interpret free-form language: `datasets/support.jsonl` supplies a structured `request` alongside `query`. It never reads `expected` when answering. The evaluator owns that separate oracle.

To integrate another target:

1. Keep the fixture scenario and expected cases independent of the target. Replace target invocation/collection, not the reference answers.
2. Collect exactly one record for every regression case, with `item_id`, **observed** `actual_version`, `response`, `context`, `trace`, `outcome` and `state.tickets`.
3. Trace actual client-side tool execution. Include each tool's `arguments`, `result` and `status: "completed"`; derive context from retrieved/tool outputs, never from the answer or reference.
4. Capture actual side-effect state through a trusted collector. Local replay is a fixture check, not verification of a production database.
5. Register the candidate name and expected immutable version in `policy.json`. The CLI accepts registered candidates with `--records`. A custom live adapter must obtain actual version metadata from the application; **do not default it from policy**.
6. Protect the evidence channel. This format is not signed attestation, and a collector that fabricates both traces and state defeats its purpose.

A record is a JSON object with this shape:

```json
{
  "item_id": "reg-order",
  "actual_version": "contoso-support/1.0.0",
  "response": "Order ORD-1001 is shipped. Tracking: TRACK-1001.",
  "context": [
    {
      "source": "lookup_order",
      "id": "tool-result-1",
      "content": {"code": "found", "order_id": "ORD-1001", "status": "shipped", "tracking": "TRACK-1001"}
    }
  ],
  "trace": [
    {
      "tool": "lookup_order",
      "arguments": {"order_id": "ORD-1001", "customer_id": "C-001"},
      "result": {"code": "found", "order_id": "ORD-1001", "status": "shipped", "tracking": "TRACK-1001"},
      "status": "completed"
    }
  ],
  "outcome": {"action": "order_status", "code": "found", "order_id": "ORD-1001", "status": "shipped", "tracking": "TRACK-1001"},
  "state": {"tickets": []}
}
```

The recording file is a **JSON array** of records (distinct from the input case dataset's JSONL format). A round trip using the baseline is useful to check the collector contract:

```bash
python3 - <<'PY'
import json
from pathlib import Path
report = json.loads(Path("build/evaluation/baseline.json").read_text())
records = [item["record"] for item in report["items"]]
Path("build/evaluation/recordings.json").write_text(json.dumps(records, indent=2, allow_nan=False) + "\n")
PY
python3 samples/contoso-evaluation/run.py --candidate baseline --records build/evaluation/recordings.json --output build/evaluation/recorded-baseline.json
python3 samples/contoso-evaluation/gate.py build/evaluation/recorded-baseline.json
```

Every record must cover the selected manifest exactly once. Missing attribution, failed tool execution, duplicate IDs and missing records cannot silently reduce the denominator.

## 5. Optionally check the Foundry SDK without Azure access

Use Python **3.11** for the tested pinned cloud environment. Install only if taking this optional path:

```bash
python3.11 -m venv samples/contoso-evaluation/.venv
samples/contoso-evaluation/.venv/bin/python -m pip install -r samples/contoso-evaluation/requirements-cloud.txt
samples/contoso-evaluation/.venv/bin/python -m pip check
samples/contoso-evaluation/.venv/bin/python samples/contoso-evaluation/cloud.py --check-sdk
```

If a relocated uv-managed interpreter cannot bootstrap `venv`, an alternative is:

```bash
uv venv --python 3.11 samples/contoso-evaluation/.venv
uv pip install --python samples/contoso-evaluation/.venv/bin/python -r samples/contoso-evaluation/requirements-cloud.txt
uv pip check --python samples/contoso-evaluation/.venv/bin/python
samples/contoso-evaluation/.venv/bin/python samples/contoso-evaluation/cloud.py --check-sdk
```

The smoke imports official types, checks exact API signatures, serializes evaluator/JSONL requests, and exercises two result pages through an **in-process mock HTTP transport**. It does not instantiate Azure credentials or call Azure. Expected output includes `status: "passed"` and `mock_transport: {"requests": 5, "output_items": 2, "pages": 2}`.

The complete stdlib tests also exercise asynchronous completion/failure/cancellation, deadline expiry, partial page failures, resume without resubmission, and strict result/count/version checks using fake clients. A passing mock is **not** a live integration result. Refer to [SDK status and versioned sources](../sdk-status.json) before upgrading the pins.

## 6. Optionally submit recorded outputs to an existing project

**Do not run this section until data handling and evaluation costs are approved.** Nothing here provisions resources. Follow Microsoft's [evaluation-only prerequisites](https://learn.microsoft.com/azure/foundry/observability/how-to/cloud-evaluation) for an existing project, authorized identity and supported judge deployment.

Set `AZURE_AI_PROJECT_ENDPOINT` to your HTTPS project endpoint and `AZURE_AI_MODEL_DEPLOYMENT_NAME` to your authorized judge deployment. Configure `DefaultAzureCredential` using your approved identity flow; do not store credentials in this repository.

```bash
samples/contoso-evaluation/.venv/bin/python samples/contoso-evaluation/cloud.py \
  --input build/evaluation/regressed.json \
  --output build/evaluation/cloud-regressed.json \
  --allow-upload \
  --timeout 600 \
  --poll-interval 5
```

The adapter sends the recorded response, not a reference answer. For the regressed return case, the response says 90 days while the retrieved context says 30. The cloud service judges those fields with `builtin.groundedness`; it does not invoke the support tools or regenerate a candidate response.

The adapter:

- persists `eval_id` immediately after evaluation creation and `run_id` after submission;
- records the input fingerprint, candidate/version, judge request, project endpoint, package pins and raw SDK outputs;
- stops polling on `completed`, `failed`, `canceled`/`cancelled`, unknown status or deadline;
- disables SDK request retries and caps individual requests at 30 seconds;
- retrieves **every result page**, preserves partial evidence on errors, and validates every required per-item evaluator result against submitted IDs/versions and run/criterion counts;
- retains remote evaluations/runs: **no automatic deletion or cancellation**.

The polling deadline bounds local waiting; a request/page already in flight can add up to its 30-second request timeout. The remote run may continue after local timeout. IDs known before an exception are retained; if the server accepted creation but the response was lost, the client cannot know that ID. Inspect the project before starting another submission.

A complete cloud evidence file uses `schema_version: "contoso.cloud-evaluation/1"` and `kind: "cloud-recorded-output-advisory"`, with `raw_run`, `raw_output_items`, `pages_retrieved`, `all_results_retrieved` and a per-evaluator `summary`. A paginated download can be complete while coverage/schema validation still fails; inspect `status` and `error`, not just `all_results_retrieved`.

Cloud exit 0 means **a complete, schema-validated job**, even when groundedness labels fail. It is not a release pass. Exit 2 means an execution/validation error. `gate.py` rejects cloud evidence; the toy release policy is based on deterministic fixture checks. Adding a cloud release gate requires a separately calibrated policy and a live-verified adapter contract.

To continue retrieval after a timeout or partial-page failure:

```bash
samples/contoso-evaluation/.venv/bin/python samples/contoso-evaluation/cloud.py \
  --input build/evaluation/regressed.json \
  --output build/evaluation/cloud-regressed.json \
  --allow-upload \
  --resume
```

Resume requires both known IDs plus the same input, judge request and endpoint. It preserves earlier attempt evidence and does not submit another run. If only an evaluation ID is known, retain it for investigation; do not fabricate a run ID. Cancellation and eventual cleanup follow your explicit retention/budget policy and Microsoft's [results guidance](https://learn.microsoft.com/azure/foundry/observability/how-to/cloud-evaluation-results).

**Remaining limits:** this adapter has not authenticated to Azure or run against a live service. Judge-region support, permission propagation, service output shape, privacy controls, score calibration and actual costs remain unverified. The sample deliberately fails closed if the pinned expected output shape is not returned.
