---
title: "Interpret results and compare versions"
description: "Validate coverage, inspect failure slices, and make uncertainty visible."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Interpret results and compare versions

Start by asking whether the result is usable evidence. Then ask what the candidate
did well or badly. A completed run, a high mean, or a green dashboard is not
sufficient for a release decision.

The [cloud results guidance](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results)
describes aggregate and per-item results. Preserve both.

## Validate the evidence envelope

Check terminal run status, evaluation/run IDs, actual target attribution,
dataset version, evaluator mappings, judge settings, and complete pagination.
Reject failed/canceled runs for acceptance. Bound polling and retries; do not
wait indefinitely or silently accept partial output.

For each required evaluator, inspect total, scored, skipped, errored, and applicable
counts according to the service's actual result contract. Unsupported conversation
evaluators can skip. A missing safety metric must not default to zero defects.

The local sample uses its own explicit normalized report. Inspect it:

```python
import json
from pathlib import Path

report = json.loads(Path("build/evaluation/baseline.json").read_text())
for name, value in report.items():
    print(name, json.dumps(value, indent=2))
```

Use the companion gate to validate that contract. Do not pass arbitrary cloud
JSON directly into the fixture gate or infer field names from a local example.

## Read the item behind the average

A useful case view joins query/messages, response, context, tool observations,
reference/outcome, score or label, threshold, reason, and evaluator details. Judge
reasons are aids for review, not independent proof.

For Contoso, investigate a "ticket complete" score alongside the actual ticket
record. Inspect incorrect-policy answers against the policy version and retrieved
passages. Include the evidence for denied access and no-answer behavior.

Group failures by task, language, document freshness, authorization boundary,
tool, latency band, and operating condition. Distinguish an improvement on common
cases from a regression on critical rare cases.

When a result surprises you, check three sources before attributing it to the
candidate: Was the task solvable and its success criterion valid? Did the grader
agree with independent review on known-good, known-bad, and ambiguous cases? Did
the trial run in the intended environment with the expected tools and state?
Preserve these as distinct failure hypotheses; a broken grader or fixture is not
an application regression.

## Compare like with like

Pair baseline and candidate on the same cases and measurement configuration.
Report both absolute criteria and paired differences. Record what changed:
target, retrieval, tool contract, policy, dataset, evaluator, or judge.

If the judge changes, the metric can move without an application improvement.
If the dataset changes, do not describe the difference as a controlled A/B
comparison. Re-run a shared baseline or clearly label incomparable evidence.

Repeated runs help characterize nondeterminism. Size the dataset according to
the failure coverage and effect you need to detect, not an arbitrary row count.
For a simple independent binary-event model, zero failures in a small sample still
leaves meaningful uncertainty; correlated synthetic or repeated cases weaken
that model further. Do not promise zero risk from zero observed defects.

For repeated attempts on the same task, [“Demystifying evals for AI agents”](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)
distinguishes `pass@k`—at least one
success among *k* attempts—from `pass^k`—success on every attempt. The first asks
whether the agent can succeed within the allowed attempts; the second asks
whether it succeeds consistently across them. State the task, trial conditions,
and aggregation protocol. These statistics answer different questions and are
not the ordinary per-item pass rate, an evaluator average, or proof of coverage.
They are methodology from [“Demystifying evals for AI agents”](https://www.anthropic.com/research/demystifying-evals-for-ai-agents),
not a Foundry result contract. Safety reports should also explain the measured
construct and uncertainty, consistent with
[“Building strong safety evaluations”](https://www.anthropic.com/research/building-strong-safety-evaluations).

For [model-selection benchmarking](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/benchmark-evaluations),
the portal provides predefined dataset/evaluation packages and separates target
from judge. Select the target, benchmark data, and judge where required, then
review and submit. Preserve run configuration, item results, and example counts.
Check that benchmark tasks, language, scoring,
and deployment settings match the application decision. A general benchmark
leader is not automatically the best support agent. Use application-specific
held-out validation before selecting a model for release.

## Use human review and clustering

[Human evaluation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation)
helps inspect disputed cases and calibrate business criteria. Blind reviewers to
candidate labels when practical; document policy ambiguity instead of forcing
agreement.

[Cluster analysis](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cluster-analysis)
can suggest common failure themes. Treat clusters as hypotheses requiring case
inspection. Its results are not automatically persisted: download them before
leaving the page.

## Write the decision report

Record coverage/invalid evidence, baseline and candidate results, critical slices,
human disagreements, uncertainty, safety constraints, latency/cost, and the
recommended action. Assign a fix owner and link the next experiment.

Optional model-target cost or latency fields may be absent or incomplete. They
are not the total bill for judge, agent, tools, simulation, storage, and monitoring.
State what was measured.

Retain evaluation/run IDs and item evidence for audit and reproducibility; avoid
automatic run deletion after printing a summary. Continue with
[release decisions](../release-gates/release-gates.md).
