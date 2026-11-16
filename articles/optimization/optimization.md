---
title: "Optimize using evaluation evidence"
description: "Improve application quality and evaluation efficiency without leaking acceptance data."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Optimize using evaluation evidence

Optimize the dominant failure, not an abstract leaderboard score. A RAG answer
using outdated policy needs retrieval/governance work. A missing ticket needs a
tool/process fix. Prompt rewriting may solve neither.

Separate three activities: improving the application, improving measurement,
and reducing evaluation cost.

## Define the experiment

Record baseline target/configuration, dataset split/version, evaluator/rubric
version, judge settings, candidate change, success criteria, safety constraints,
and latency/cost boundaries. Keep the acceptance set held out from tuning.

State the hypothesis and intended application change before running. Keep the
task set, rubric, judge, environment, and other relevant settings fixed when you
want to attribute a difference to that change. If the task, grader, or environment
also changes, label it as a measurement/design change or a combined experiment;
do not claim the score movement proves application improvement. If acceptance
failures inform later tuning, that evidence is no longer held out; create a
reviewed replacement acceptance version. Success criteria should be specific to
the task, as described in
[M03](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests).
The task/trial distinction and controlled evidence lineage follow
[M01's agent-evaluation methodology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

The [rubric](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators)
should express the actual outcome. A changed rubric can raise scores without
improving the application; treat that as a separate measurement experiment.

The local fixture commands demonstrate comparing candidates, not running a
Foundry optimization job:

```bash
python3 samples/contoso-evaluation/run.py \
  --candidate baseline --output build/evaluation/baseline.json
python3 samples/contoso-evaluation/run.py \
  --candidate regressed --output build/evaluation/regressed.json
```

Use the resulting failures to explain what an acceptable change must fix. A
fixture baseline is not an optimized prompt or model.

## Choose the appropriate optimizer

[Prompt Optimizer](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/prompt-optimizer)
rewrites text instructions in the portal with paragraph-level reasoning. It
does not by itself establish a measured quality improvement or optimize knowledge
sources/tool implementation. Review and preserve changes, then evaluate them.

[Agent Optimizer](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview)
uses evaluation-driven candidate generation and comparison. Setup and supported
targets differ:

| Target | Workflow boundary |
|---|---|
| Prompt agent | Portal workflow for supported agents; review a selected candidate and create a new version |
| Hosted agent | Optimizer-ready runtime configuration/integration; apply candidate locally, review, redeploy |
| Function-tool descriptions | Descriptions can improve model choices; prompt-agent client-side execution is not evaluated by tool-description optimization |
| Skill learning | Separate recorded-conversation workflow, with its own preview status |

Do not conflate the optimizer's local `eval.yaml` intent with the evaluation CLI's
`evals/azure.eval.yaml` recipe. Confirm target support, version, models, regions,
and costs in the current workflow before starting.

Hosted optimization can invoke actual tools for every task/candidate. Use test
endpoints or mocks to avoid repeated charges, state mutations, and rate-limit
effects. Never toggle production routing merely to run synthetic experiments.

## Validate improvements independently

Inspect [item results](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results),
critical slices, safety outcomes, and human disagreements. Compare candidates
on shared evidence and fixed measurement settings. Preserve uncertainty and
repeated-run variation.

A composite winner can still regress on denied-access or no-answer behavior.
Apply hard outcome/safety constraints separately from a ranking score. Review
generated instructions for removed restrictions or newly unsupported promises.

Only after development/calibration gains are credible should you run held-out
acceptance and authorize promotion. If you repeatedly tune after seeing acceptance
failures, replenish truly held-out evidence rather than claiming it remains untouched.

## Reduce evaluation cost responsibly

Use deterministic checks for exact effects. Run small targeted suites while
debugging, and broader required acceptance before release. Consider appropriate
composite evaluators and sampling, but verify applicability and judge alignment.
Lower cost is not an improvement if required coverage disappears.

Track full workflow cost, latency distribution, and quality separately. Missing
optional cost fields are unknown. Set maximum candidate/run budgets and stop
conditions before experimentation.

Preserve the chosen candidate, rejected alternatives, evidence, and rationale.
Optimization proposes; the release policy decides.
