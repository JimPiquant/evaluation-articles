---
title: "Run adversarial testing responsibly"
description: "Scope authorized tests, isolate effects, and turn findings into safer regressions."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Run adversarial testing responsibly

Adversarial testing asks whether intentional probing reveals failures that
ordinary cases miss. It is a scoped risk-management activity, not a claim that
every possible attack has been exhausted.

The [Foundry AI Red Teaming Agent](https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent)
combines scanning, risk evaluation, and reporting, using capabilities from
Microsoft's [PyRIT](https://github.com/microsoft/PyRIT). Start with the maintained
Foundry workflow; direct PyRIT work is an advanced extension with its own
maintainer APIs and validation requirements.

## Write an authorized test charter

Specify the target/version, environment, approved risk categories, tool/data
boundaries, budget, rate limits, stop conditions, reviewer access, and finding
owner. Obtain authorization before any run.

This non-executable scope example is an editorial artifact, not a service API:

```json
{
  "environment": "isolated-support-test",
  "target_version": "observed-and-verified",
  "data": "synthetic-customer-fixtures",
  "tools": "sandbox-only",
  "stop_on": ["unexpected-external-effect", "budget-limit"],
  "finding_owner": "authorized-safety-reviewer",
  "promotion": "human-reviewed-release-policy"
}
```

Contoso tests should not access production CRM records or create real customer
tickets. Use synthetic identities and mocked/sandbox tools.

## Confirm support and limits

Read the current source's target, modality, language, region, and risk-category
restrictions. Model-only and agentic risks are not identical workflows. The
documentation describes cloud-only agent categories and category-specific
limitations; do not imply that every risk supports every language, target, or
conversation length.

Do not freeze a large attack-strategy or region catalog into this article.
Recheck the documented support before execution and record the exact versions.
This repository supplies no attack payloads or live red-teaming execution.

The concept page and general
[region/limit reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-regions-limits-virtual-network)
currently list different red-teaming region sets. The
[discrepancy register](../../references/grounding.md) records that conflict;
confirm exact target/risk availability rather than combining both lists.

## Separate the evidence activities

| Activity | Question |
|---|---|
| Ordinary safety evaluation | How does the candidate behave on chosen known scenarios? |
| User simulation | How does the interaction evolve under generated user behavior? |
| Adversarial probing | Can intentional pressure reveal a policy/risk failure? |
| Control tests | Does the application actually prevent prohibited effects? |

Use the [evaluation overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)
to select ordinary workflows and the
[risk/safety reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators)
to interpret risk results. An attack-success metric has a sampling and probing
context; it is not a universal production incident probability.

Design scenarios around a stated risk hypothesis and the behavior that would
count as evidence. Include realistic multi-turn context where the risk depends
on the interaction, plus benign or ambiguous controls that should not trigger
the same finding. Record expected behavior, test conditions, and important
limitations before interpreting a result. This follows
[“Building strong safety evaluations”](https://www.anthropic.com/research/building-strong-safety-evaluations);
it does not replace Foundry's documented supported risk categories, authorization,
or execution limits.

## Execute in a protected environment

Verify target attribution and tool routing before generated probes. Isolate
data and side effects, bound workload, and monitor for unexpected calls. Stop
if the environment violates the charter. Do not assume service-side redaction
or transient runs protect an external tool's logs or business effects.

Restrict reviewer exposure and artifact access. Retain required result IDs,
tool observations, risk settings, model/judge configuration, and finding history
under approved handling policy.

## Triage and close the loop

Confirm each finding against actual behavior and independent evidence. Distinguish
judge disagreement, unsupported evaluator behavior, a weak model response, and
an actual forbidden tool effect. Assign the mitigation layer and owner.

Re-test the finding, then related benign and risk cases to detect overcorrection.
Curate safe, approved representations into regression data. Keep sensitive
original evidence separately controlled; do not place it in this repository.

Record residual risk and release authority. Successful scanning does not mean
safe deployment; absence of findings means none were observed under that charter.
Combine adversarial evidence with [safety evaluation](../safety/safety.md),
runtime controls, and the [release policy](../release-gates/release-gates.md).
