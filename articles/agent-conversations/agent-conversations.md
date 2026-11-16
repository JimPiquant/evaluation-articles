---
title: "Evaluate agents and complete conversations"
description: "Measure interaction outcomes and tool behavior with complete, attributable evidence."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Evaluate agents and complete conversations

A support conversation can fail even when each individual answer is polite and
plausible. The agent might repeat an ineffective step, fail to create a ticket,
or retrieve the wrong customer's order. Evaluate the whole outcome when the task
depends on multiple steps.

The [conversation workflow](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations)
distinguishes turn and conversation scoring. Complete `messages` are required;
omitted `evaluation_level` defaults to turn. Specify the intended level explicitly.

## Preserve process evidence

Capture user/assistant messages, tool definitions, tool calls and arguments,
tool results, final response, actual target version, and independently verified
outcome. Tool-call intent and tool execution are different facts.

The **agent harness** is the runtime and tools that let the model act. The
**evaluation harness** sets up tasks and trials, records the transcript and
outcome, applies graders, and aggregates evidence. Keep their responsibilities
separate so an agent's own success claim is not its grader. For repeatable trials,
start from a known environment state where practical, reset fixture data, and
record relevant tool, policy, and environment versions. Match the environment to
the decision being studied; isolation improves reproducibility but does not by
itself make results representative. This distinction follows
[M01's agent-evaluation methodology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents),
not a Foundry service requirement.

For Contoso, "your ticket has been created" is a communication claim. A returned
ticket identifier and persisted fixture/service record establish the effect.
A denied order lookup should not become a success because the assistant
invented a plausible status.

Use non-production tool endpoints or fixtures for generated interactions.
Multiple simulated users can create repeated side effects; resetting the sandbox
is part of reproducibility, not an optional cleanup detail.

## Select compatible criteria

The current [catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)
and conversation guide identify Output Quality and Tool Use Quality as composites.
Customer Satisfaction and Task Completion cover interaction outcomes. A
[business rubric](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators)
expresses domain-specific quality; exact authorization/effect checks cover
boundaries a judge cannot enforce.

This current Projects SDK construction illustrates a criterion, **not a full
submitted run**. Follow the companion's dependency pins and current SDK setup:

```python
from azure.ai.projects.models import TestingCriterionAzureAIEvaluator

criterion = TestingCriterionAzureAIEvaluator(
    type="azure_ai_evaluator",
    name="customer_satisfaction",
    evaluator_name="builtin.customer_satisfaction",
    initialization_parameters={"model": "your-judge-deployment"},
    data_mapping={"messages": "{{item.messages}}"},
)
```

The run also needs the documented conversation schema and
`evaluation_level="conversation"`. Tool-related criteria need the required tool
definition mapping. The [Projects SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python)
and current guide are the implementation authority; do not mix this with older
thread/run agent code.

Unsupported turn-only evaluators can be skipped rather than fail the run. Check
each required criterion's scored count, applicability, skipped/error cases, and
input mapping. A completed run with no Task Completion scores is not completion
evidence.

## Choose a conversation source

| Workflow | What happens | What to control |
|---|---|---|
| Completed dataset | Scores recorded messages | Transcript completeness and provenance |
| Production conversations | Reads deployed traces | Permissions, sampling, privacy, trace completeness |
| Simulated interaction | A generated user interacts with a target | Seeds, simulator settings, stop conditions, tool effects |
| Synthetic completed conversation | Generates evidence without the same live target interaction | Realism, labels, and separation from target-performance claims |

The [simulation workflow](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-simulate-conversations)
helps explore interactions before deployment. Its generated behavior is useful
evidence, not a representative census of customers. Include ambiguity, correction,
frustration, denied access, and tool failure without assuming the simulator
exhausts the risk space.

## Diagnose the failed journey

Inspect where the task diverged. Did the agent misunderstand intent, omit a required
confirmation, call the wrong tool, pass incorrect arguments, ignore a tool error,
or communicate an unverified result? Those are different fixes.

Track candidate/model/tool/policy versions. If actual attribution is missing,
reject or explicitly exclude the case under a declared policy. Never replace
missing observed version with the requested version, especially with mixed
canary traffic.

The [offline companion](../../samples/contoso-evaluation/README.md) demonstrates
working fixture effects and fail-closed evidence, not generative conversation
quality. Use cloud-compatible captured messages and current target integration
when adding judge/simulation evaluation.

## Agent Framework as a separate integration path

[Microsoft Agent Framework evaluation](https://learn.microsoft.com/en-us/agent-framework/agents/evaluation)
adds framework APIs for local checks, custom evaluators, orchestration, and
Microsoft Foundry evaluators. Treat it as an optional implementation path beside
the Foundry workflows above, not as the companion's current implementation.
Choose the language-specific package and version, then verify its API and result
contract before adapting examples; framework defaults do not redefine Foundry
service behavior. The series' fixture does not implement or validate this
integration.

Continue with [results](../results/results.md) and
[tool delivery](../../platform/tools/tools.md).
