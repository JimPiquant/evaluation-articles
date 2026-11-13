---
title: "Deliver and evaluate agent tools"
description: "Test candidate contracts and effects before conversation-level promotion."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Deliver and evaluate agent tools

A tool definition tells a model what it may call. It does not implement the tool,
enforce authorization, or prove a business effect. Tool delivery should test
contracts and actual behavior before judging the surrounding conversation.

## Identify the integration contract

Function calling, OpenAPI-backed tools, and MCP servers have different execution
and authentication contracts. A schema or connection-update snippet for one is
not a universal deployment API for all three.

Use the [current Projects SDK reference](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python)
for actual signatures and selected generation. Verify the exact connection/tool
API before implementing. This article intentionally does not present an untested
`connections.create_or_update` recipe.

For client-side function calling, the application must dispatch, validate, execute,
and return tool results. A managed evaluation target cannot be assumed to implement
your missing client-side tool loop.

## Test the candidate implementation

The [Contoso companion](../../samples/contoso-evaluation/README.md) implements
fixture-backed knowledge lookup, order lookup, and ticket creation. From the
repository root:

```bash
python3 -m unittest discover -s samples/contoso-evaluation/tests
python3 samples/contoso-evaluation/run.py \
  --candidate baseline --output build/evaluation/tools-baseline.json
python3 samples/contoso-evaluation/gate.py build/evaluation/tools-baseline.json
```

This exercises actual local fixture functions, not a live CRM endpoint. For a
real candidate service, verify the invocation reaches that service/version,
not an unused `TOOL_ENDPOINT_URL` variable or a model deployment.

Check input validation, customer authorization, output schema, effect correctness,
idempotency where applicable, timeouts, error handling, and compatibility. Test
denied or invalid operations without creating unintended external effects.

## Add process and interaction evaluation

Once tool behavior is independently observable, capture tool definitions, calls,
arguments, results, and complete messages. The
[conversation guide](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations)
describes mapping tool definitions for process-related scoring.

Use [Tool Use Quality and relevant supported evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)
plus a business rubric. Distinguish choosing a tool, passing correct inputs,
receiving a result, achieving the task, and accurately telling the customer.
These are not interchangeable measures.

Configure every criterion required by the policy. A utilization threshold with
no utilization evaluator produces missing evidence, not a pass. Do not compare
raw score scales with pass-rate percentages without explicit normalization.

## Promote a coherent application/tool pair

Record application version, tool implementation/configuration version, schema,
data/policy version, and evaluator/judge lineage. A backward-incompatible tool
change can invalidate an otherwise unchanged agent prompt.

Run deterministic contract tests, isolated candidate invocation, compatible
conversation evaluation, and the centralized release gate. The
[Foundry Actions guidance](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluation-github-action)
is an execution option, not proof that your custom policy is wired.

Preserve evidence before deployment. Use protected promotion with a rollback
plan for both application and tool contract. Avoid testing against real production
mutations or changing routing just to run synthetic scenarios.

Continue with [release gates](../../articles/release-gates/release-gates.md).
