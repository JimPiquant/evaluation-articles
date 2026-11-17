---
title: "Deploy a trustworthy evaluation target"
description: "Choose a target and isolate it without confusing deployment with evaluation."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Deploy a trustworthy evaluation target

Deployment is supporting work, not the starting point of every evaluation.
If you already have approved recorded responses or completed conversations,
score that evidence directly. The [Foundry overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)
provides separate recorded-output, target, simulation, and trace workflows.

Deploy a target when you need fresh responses or interactions from a specific
candidate. Make the target's identity and effects measurable before evaluating
its quality.

## Choose the target and API generation

A prompt agent uses managed model-based configuration. A hosted agent runs
application code with its own configuration and dependencies. Both can participate
in evaluation, but setup, invocation, tracing, and optimization support differ.
Do not assume every harness or target exposes the same features.

The [current Projects SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python)
documents versioned agents and Responses/Evals integration. The
[standalone Agents SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python)
documents a different thread/message/run surface. Select one generation per
executable recipe and record package versions; do not blend their creation and
evaluation methods.

A stable package does not imply every operation is generally available. Verify
capability-specific preview requirements and limits.

## Isolate evaluation effects

Use a separate target/configuration or a documented supported version selector.
Point order/ticket tools at synthetic or sandbox services. Ensure generated
interactions cannot mutate real customer records or unexpectedly charge external
services.

Treat each trial as a reproducible experiment: reset fixture state or provision a
fresh isolated state where practical, and record environment/tool/policy versions
that can affect outcomes. Environment fidelity should match the question; a
sandbox can validate behavior but is not automatically representative of
production. Do not confuse isolation guidance with a Foundry deployment
requirement. This follows the trial guidance in
[“Demystifying evals for AI agents”](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

Mixed canary traffic is useful for operational rollout, but not automatically
clean candidate-comparison data. Preserve actual served version. Missing version
metadata is an evidence problem, not permission to substitute the desired version.
Do not temporarily reroute production solely to run synthetic tests.

## Verify the target before judging

Check health/invocation, expected tool contract, actual runtime version/configuration,
independent side effects, emitted traces where required, and authorization behavior.
Only then submit paid evaluation work.

Follow [cloud prerequisites](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation)
for project, models, and evaluation setup. Application dependencies such as
knowledge indexes or business services are separate from evaluator/judge resources.

Hosted configurations may require optimizer-ready integration. The
[Agent Optimizer overview](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-optimizer-overview)
explains that hosted candidates are applied locally, reviewed, and redeployed.
Prompt-agent tool-description optimization does not evaluate client-side tool
execution. Do not assume optimization bypasses target-readiness work.

## Avoid absolute platform promises

Do not promise universal sub-second startup, zero idle cost, built-in durability,
or a fixed connector/model count. Those depend on the actual service, deployment,
configuration, and date. Durable business workflows need explicitly designed
state, retries, idempotency, and compensation where appropriate.

The earlier hosted-agent deck and meeting notes are archived historical material,
not current evidence for these claims.

## Target-readiness checklist

- Fresh target invocation is necessary for the intended decision.
- The chosen generation, dependencies, and capability status are documented.
- Observed target/model/tool/configuration attribution is available.
- Tools are safe for repeated evaluation and independently observable.
- Identity/network prerequisites match the actual environment.
- Failure/retry behavior does not duplicate uncontrolled side effects.
- Deployment and live-cloud validation status are recorded honestly.

The [Contoso sample](../../samples/contoso-evaluation/README.md) is a teaching
fixture, not this production target. Continue with
[identity/networking](../identity/identity.md) and
[conversation evaluation](../../articles/agent-conversations/agent-conversations.md).
