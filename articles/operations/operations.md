---
title: "Operate and govern evaluations"
description: "Manage sampling, run failures, identities, retention, budgets, and drift."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Operate and govern evaluations

Evaluation becomes operational work when customers depend on its decisions.
Assign owners for execution, evidence quality, dataset lifecycle, cost, and
incident response. Treat a missing evaluation as a service failure, not a quiet
green interval.

## Separate regression jobs from live sampling

A scheduled regression evaluates a fixed versioned dataset. Continuous evaluation
samples actual traffic and reveals failures not anticipated by the dataset.
The [monitoring guidance](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard)
describes the operational path; a nightly CI job is not a substitute.

Choose cadence and sampling according to risk, traffic, cost, and detection needs.
Document excluded populations and trace loss. A sample skewed toward one language
or successful short interaction may conceal a critical regression elsewhere.

## Make the dependencies real

Trace workflows require connected Application Insights, emitted trace content,
retention, and appropriate [caller/project access](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions).
A Log Analytics workspace alone does not establish that setup. Verify the
resource connections and identities independently.

Use the [evaluation networking requirements](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-virtual-network)
for the selected workflow. Do not require a complete production agent platform
to score recorded outputs. Conversely, do not assume a client with public access
can reach a privately isolated endpoint.

Verify [regions and rate limits](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-regions-limits-virtual-network)
for the exact capability. Playground, batch, risk, and generation availability
can differ. Honor service `retry-after` guidance and bound concurrency/backoff;
do not apply one static region list or maximum to every workflow.

## Operate the run state machine

Persist submission/run identifiers before polling. Bound waits, use appropriate
retry/backoff for transient errors, and stop on terminal failed/canceled state.
Do not resubmit a potentially billed run merely because the polling client
timed out; inspect the recorded run first.

Retrieve all result pages and enforce [required coverage](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results).
Incomplete retrieval is a blocked decision. Distinguish service failure,
invalid schema, incompatible evaluator, denied access, and actual candidate failure.

### Incident runbook

| Symptom | First action | Evidence / owner |
|---|---|---|
| 401/403 | Check caller identity, scope, and project managed identity | Role assignments; platform owner |
| Timeout/private endpoint failure | Verify approved connectivity and DNS | Network path; platform owner |
| Run stuck or failed | Inspect recorded run before retry/resubmit | Run status and diagnostics; execution owner |
| Missing/skipped criterion | Verify level, input mapping, required fields | Counts/item errors; evaluation owner |
| Quality drift | Inspect failure slices and target/data/judge changes | Paired evidence; product owner |
| Sensitive content in results | Restrict access and follow incident/data policy | Access records; data/safety owner |
| Unexpected cost | Stop optional jobs and inspect workload multiplication | Target/judge/simulation usage; budget owner |

## Govern artifacts through retirement

Keep dataset/evaluator versions, target/model/tool/policy versions, judge settings,
run IDs, normalized results, human decisions, and gate policy. Define retention
and exports according to organizational needs; there is no universal retention
duration.

Store raw sensitive traces separately from curated reusable cases. Restrict both
access and content. The
[trace-to-dataset workflow](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/traces-to-dataset)
does not eliminate approval, redaction, or purpose limitations.

When a policy changes, create a new dataset version and preserve the meaning of
old decisions. The [dataset guidance](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets)
supports versioned evidence; avoid mutable "latest" aliases in audit records.

When retiring the application, disable schedules/rules, revoke unused identities,
remove stale connections, archive required evidence, and apply approved deletion
policy. Do not auto-delete evaluation objects from normal execution code.

## Close the feedback loop

Review operational failure slices with domain experts. Promote approved cases
into development/calibration data; periodically replenish held-out acceptance
without contaminating it with routine tuning.

Own the suite as well as the run: assign maintainers for tasks, rubrics, judges,
and acceptance data. Recheck grader calibration when prompts, judge deployments,
or policy change, and investigate drift in human-versus-judge disagreements.
When a capability suite becomes easy for the candidate, keep useful tasks as
regression checks and add reviewed cases that expose new capability gaps. Do not
let acceptance data become routine tuning data; replenish it through an approved,
versioned process. These are suite-maintenance practices from
[M01](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) and
[M02](https://www.anthropic.com/research/building-strong-safety-evaluations),
not prescribed Foundry schedules or dataset sizes.

Budget the complete loop: application calls, tool effects, judge calls, simulation,
generation, telemetry, storage, and human review. Expose absent cost fields as
unknown, not zero. Use risk-based suites and cadence to reduce cost without
silently abandoning required coverage.

Continue with [optimization](../optimization/optimization.md).
