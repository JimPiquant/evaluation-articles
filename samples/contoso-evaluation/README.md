# Contoso evaluation companion

A small, **offline-validated** support application and evaluation harness. Start here without Azure, credentials, dependencies, or a language model. The optional Foundry adapter judges **recorded outputs**; its imports, API types and mocked HTTP lifecycle are validated, but **the live cloud service has not been validated**.

## Run from the repository root

Python 3.9+ for the standard-library path; tested on Python 3.9.6 and 3.11.14.

```bash
python3 -m unittest discover -s samples/contoso-evaluation/tests
python3 samples/contoso-evaluation/run.py --candidate baseline --output build/evaluation/baseline.json
python3 samples/contoso-evaluation/run.py --candidate regressed --output build/evaluation/regressed.json
python3 samples/contoso-evaluation/gate.py build/evaluation/baseline.json
python3 samples/contoso-evaluation/gate.py build/evaluation/regressed.json
```

The baseline gate exits **0**. The regressed gate exits **1**, with failed evaluator names and case IDs. `run.py` exits 0 when evaluation completes, even if checks fail; it is **not** the gate. Missing files or malformed JSON make `gate.py` exit 2. Incomplete/errored runs never pass.

See [getting started](docs/getting-started.md) for interpretation, integration and optional cloud commands.

## What actually runs

`contoso/app.py` executes real local functions over [fictional fixtures](fixtures/support.json):

- `search_knowledge`: keyword retrieval of independent policy documents.
- `lookup_order`: status/tracking lookup, with an ownership check.
- `create_ticket`: ownership and explicit consent checks, followed by an in-memory ticket write.

Each case gets isolated state. Records contain the actual response, retrieved/tool context, executed tool arguments/results, structured outcome and observed ticket state. Expectations come from [JSONL cases](datasets/support.jsonl), **not** from the candidate. The baseline respects fixture outcomes. The regressed candidate invents a 90-day return window, changes an order status, and claims a ticket without executing its creation.

**Integration boundary:** this sample takes a structured request next to a human-readable query. It does not implement natural-language routing, an LLM agent loop, a hosted tool service or a deployed application. These are single requests with tool traces, not complete multi-turn conversations. Client-side function execution belongs to the application/collector; a cloud evaluator does not execute these local functions.

## Evaluators and release policy

[policy.json](policy.json) is the single policy source. Every required evaluator must run on every case in its release split. The gate verifies the exact case manifest, candidate/version attribution, dataset/fixture/policy/implementation fingerprints, per-item results and recomputed counts. It rechecks recorded evidence rather than trusting a supplied average.

| Deterministic check | What it measures |
|---|---|
| `tool_contract` | Expected tool sequence/arguments and outputs matching fixture execution |
| `fixture_context` | Context matching those tool outputs and expected retrieved document IDs |
| `expected_outcome` | Structured outcome matching the independently authored expectation |
| `response_assertions` | Required phrases present and explicitly forbidden phrases absent |
| `ticket_state` | Observed ticket state matching executed side effects, expected count and claimed ID |

These are **not** LLM quality, groundedness, safety, or red-team scores. Phrase assertions cannot detect every unsupported claim. Authorization and consent cases test those specific fixture contracts, not general security. Context consistency is not proof of factual correctness beyond the fixture. Ticket replay verifies this local scenario, not a production database transaction.

The small demonstration policy requires complete coverage and all checks to pass. It is not a universal Foundry threshold. No missing, skipped, errored, nonnumeric, NaN/Infinity, wrong-version, zero-coverage or inconsistent required result is treated as a pass. A valid business denial (`access_denied`, for example) can pass when denial is the expected outcome.

## Data, identity and evidence

[Dataset metadata](datasets/metadata.json) registers 14 public synthetic cases: 3 development, 8 regression and 3 holdout. `run.py --split development` or `--split holdout` supports experimentation; those smaller splits cannot satisfy the release gate. Shared fixtures and public holdout cases do not constitute independent or hidden test data. These counts demonstrate mechanics, **not** production coverage or statistical confidence.

Each application recording must supply `actual_version`. Expected versions are configured separately in policy. There is no default that substitutes the intended version for missing observations. For an external collector, use `run.py --records` and capture immutable version identity at invocation time; see the integration instructions.

The offline contract is `contoso.offline-evaluation/1`. A report contains:

- `provenance`: selected candidate, expected/actual versions and SHA-256 fingerprints;
- `items`: query/tags, independent expectations, application record and every evaluator result;
- `summary`: per-evaluator expected/evaluated/passed/failed/skipped/error counts and pass rate;
- run identity, timestamps, status and exact required evaluator names.

Changing evaluated inputs, code or policy invalidates old evidence. Re-run rather than relabeling it. Fingerprints provide lineage, **not** cryptographic attestation that a deployed candidate executed. Do not let an untrusted application supply its own expected outcomes or fabricate its collector evidence.

## Optional Foundry recorded-output evaluation

The adapter uses `AIProjectClient.get_openai_client()` and `client.evals.create`, `evals.runs.create/retrieve`, and `evals.runs.output_items.list`. There is no legacy `create_agent`, target generation, resource provisioning, or automatic remote deletion/cancellation.

The selected package set is pinned in [requirements-cloud.txt](requirements-cloud.txt), including transitive dependencies:

- `azure-ai-projects==2.2.0`
- `azure-identity==1.25.1`
- `openai==2.29.0`

This is the current **Projects 2.x/OpenAI Evals generation**, not a claim that the pins are the newest releases. Newer package metadata was reviewed but that package set could not be installed here. The exact official release-tag references, discrepancy notes and capability-level limitations are in [sdk-status.json](sdk-status.json). The adapter's schema acceptance is deliberately strict; a changed service shape fails instead of manufacturing a passing score.

Only `builtin.groundedness` is requested, at turn level, over the recorded response and independently retrieved/tool context. This is an **advisory judge signal**; it does not verify ticket execution, independent truth, safety or conversational task completion. Cloud reports have a separate contract and are rejected by the offline gate. Do not call successful job completion a successful release decision.

## Privacy, cost and operations

Offline evaluation has no network calls; tickets exist only in memory. Cloud execution requires explicit `--allow-upload` and existing authorized project/judge configuration. It sends case IDs, queries, actual responses, derived context and actual version identity. **Context can contain order/ticket/customer fields.** The supplied fixtures are fictional; scrub, minimize and approve real data before reusing this workflow.

Cloud judge calls can incur charges and store data in the configured project. Check region, permissions, retention, data handling and budget before submission. There is no fixed-cost or “free tier” promise. A timeout stops local waiting, **not** the remote job or billing. Retain the evidence and remote IDs; resume retrieval rather than resubmitting. Cancellation and deletion are separate, explicit operational decisions.

For existing-project setup, follow the official [evaluation-only prerequisites](https://learn.microsoft.com/azure/foundry/observability/how-to/cloud-evaluation), [evaluation permissions](https://learn.microsoft.com/azure/foundry/observability/how-to/evaluation-permissions) and [results/cancellation guidance](https://learn.microsoft.com/azure/foundry/observability/how-to/cloud-evaluation-results). This companion does not promise a Bicep deployment or provision an agent.

## Repository CI

The active workflow is [`.github/workflows/evaluate.yml`](../../.github/workflows/evaluate.yml). It runs local unittest, requires the baseline to pass, explicitly requires the regressed gate to return 1, and uploads per-item evidence and gate decisions with a 14-day demonstration retention. It needs `contents: read`, not Azure secrets or OIDC. Cloud evaluation is never triggered automatically.
