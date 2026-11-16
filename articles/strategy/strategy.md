---
title: "Establish an AI evaluation practice"
description: "Assign outcomes, ownership, and evidence requirements before choosing metrics."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Establish an AI evaluation practice

An evaluation practice should help a team decide what to change, what to release,
and when to intervene. A dashboard full of scores is useful only when someone
owns those decisions.

Microsoft Foundry's [evaluation workflow](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)
starts with what to evaluate, then evaluator selection, execution, and improvement.
Use that sequence to organize your practice. Pipelines are one way to operate it,
not its purpose.

## Start with a customer outcome

For Contoso Support, "the agent sounds helpful" is not enough. Customers need an
accurate answer from current policy, access only to their own order, and a real
ticket when escalation is requested and confirmed. An answer claiming a ticket
was created is not evidence that it exists.

Translate each outcome into independent evidence and an accountable owner:

| Outcome | Evidence | Accountable decision |
|---|---|---|
| Useful answer | Business rubric, relevant context, human review | Product owner approves quality criteria |
| Correct order access | Identity/authorization checks and tool results | Engineering owner approves access boundary |
| Completed escalation | Confirmed tool effect and ticket record | Application owner approves task behavior |
| Acceptable risk | Safety evaluation, adversarial findings, control tests | Safety owner accepts residual risk |
| Sustainable service | Operational failures, latency, full cost | Platform owner approves operating limits |

These are recommendations for a support scenario, not product defaults.

## Treat evidence as a portfolio

Conventional tests remain necessary: validate schemas, authorization, arithmetic,
and tool side effects. Model-judged evaluation helps with open-ended relevance,
support, and domain quality. Human review helps calibrate both the criteria and
the interpretation. Production telemetry shows how the application behaves with
real users and operating conditions.

None replaces the others. Groundedness can show that an answer follows its
context, but cannot establish that the context is current or legally appropriate.
Safety scores do not enforce authorization or guarantee regulatory compliance.

Use [human evaluation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation)
to inspect disagreement and edge cases rather than treating the judge as the final
authority. Budget expert time as part of the evaluation service.

Automated evaluations are one part of a broader way to understand agent
performance. Combine them, as appropriate, with production monitoring, user
feedback, manual transcript review, and systematic human evaluation. Each gives
a different signal; none is a complete substitute for the others. This
multi-method approach follows [agent-evaluation methodology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents),
not a Foundry service requirement.

Plan for two distinct evaluation purposes. **Capability evaluations** ask what
the agent can do and help identify where it needs to improve. **Regression
evaluations** check whether behavior that worked before still works after a
change. A capability evaluation can become useful regression evidence as the
agent improves, but that does not make the purposes or acceptance thresholds
interchangeable. Assign an owner to review tasks, graders, and results so the
suite remains meaningful as the product changes.

## Establish a release policy before tuning

Agree what is blocking, what is advisory, and what evidence is mandatory. A
blocking criterion without enough scored cases is not a passing criterion. A
missing evaluator, unknown candidate version, or failed run should stop the
decision, not silently improve the average.

Set thresholds with domain review and representative cases. There is no universal
"100 rows is enough" rule. Common task quality, rare safety failures, and small
candidate improvements have different evidence needs. Report uncertainty and
coverage alongside scores; no observed defects does not establish zero risk.

Freeze a held-out acceptance set. Use separate data to develop prompts and
rubrics. Repeated tuning on release examples turns the gate into a memorization
exercise and weakens its ability to predict new failures.

## Fund management, not just evaluation runs

Plan for target inference, judge inference, optional simulation, telemetry,
storage, and human review. A cheap individual judge call does not imply a cheap
complete evaluation loop. Set budget alerts and experiment limits, then reduce
unnecessary work through risk-based cadence and targeted suites.

Assign data ownership: who approves production-trace reuse, removes sensitive
content, versions the dataset, reviews retention, and handles deletion requests?
Assign platform ownership for the separate caller and project identities required
by [evaluation workflows](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions).

## Adopt a controlled learning loop

Practice eval-driven development: define intended behavior with tasks, run
evaluations during development, and improve the application against observed
failures. Start with a useful baseline, a few understood failures, and a
transparent result report. Expand coverage as real failure patterns appear.
Read failed transcripts
or traces to distinguish an application failure from an ambiguous task, a
misconfigured grader, or an environment problem. For each improvement,
record what changed in the application, data, evaluator, and judge. If several
change together, do not attribute the gain to one of them.

After release, compare operational slices to the tested population. Curate
approved failures into development evidence and periodically refresh acceptance
data. Preserve the previous dataset so historical decisions remain interpretable.

### Leadership launch checklist

- A product owner can state the customer outcome and unacceptable failures.
- Engineering, safety, data, and platform owners have explicit responsibilities.
- Required evidence, thresholds, exceptions, and rollback authority are documented.
- Dataset coverage, uncertainty, and human calibration are visible.
- Run lineage, retention, access, and total budget have owners.
- The team can explain a failed case and a justified improvement, not only a score.

Continue with [workflow selection](../choose-workflow/choose-workflow.md) or the
[architecture capstone](../reference-architecture/reference-architecture.md).
