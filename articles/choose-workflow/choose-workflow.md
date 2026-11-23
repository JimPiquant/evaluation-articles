---
title: "Choose your Foundry evaluation workflow"
description: "Choose what to evaluate, select evaluators, run the evaluation, and use the results to improve."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

✅ TODO: Need to discuss where evaluations run, locally, in foundry or in code with or 
without foundry.

# Choose your Foundry evaluation workflow

Microsoft Foundry provides evaluation workflows for assessing the quality and
safety of models and agents. You can use evaluation results throughout the 
software development lifecycle and as a release gate.

You can run one or more evaluators against a single response, 
a single turn of a conversation or an entire conversation. You can generate new responses 
from a model or agent each time, or analyze a curated set of completed conversations 
or evaluate production traces.

This article follows the four steps in Microsoft Learn's
[Build an evaluation workflow](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview#build-an-evaluation-workflow).
It helps you choose what to evaluate, select evaluators, run an evaluation, and
review the results to guide improvements.

## 1. Choose what to evaluate

### Define the task and evaluation purpose

A **task** (or test case) is one test with defined inputs and success criteria.
Each attempt at a task is a **trial**; repeat trials when you need to understand
variation in agent behavior. This terminology follows
[Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

At a high level consider the purpose of the evaluations you require. **Capability evaluations** 
ask what an agent can do and help identify areas to improve.
**Regression evaluations** check whether behavior that worked before still works
after a change. The same task may contribute to either purpose at different
stages, but the result has meaning only relative to the intended decision.

### Choose the evaluation levels

Evaluators support different levels.  A turn-level evaluation asks whether an 
individual response is useful, relevant, supported, or safe in its context. 
A conversation-level evaluation asks whether
the whole interaction achieved the task and respected the intended process.

For a text-based conversation evaluation, use complete `messages` data and an
explicit compatible evaluation level. [Choose an evaluation level](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations#choose-an-evaluation-level)
states that omitted `evaluation_level` defaults to turn and that Foundry skips
evaluators that don't support conversation-level scoring on conversation-level
runs. The structure of the dataset alone does not determine the evaluation level.

Refer to this guidance on [combining evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators#combining-evaluators)
for different types of applications.

### Choose where data comes from

| Source | Good starting use | Note |
|---|---|---|
| Precomputed responses | Diagnose or compare answers already produced and saved | The reference answer is not the response |
| Responses generated at run time | Evaluate responses produced by invoking a model or agent on test inputs | Verify the actual target/version and isolate effects |
| Completed conversation | Assess a known interaction | Preserve tool messages, definitions, and results |
| Simulation seeds | Explore multi-turn behavior before release | Generated users may not represent real users |
| Production responses/traces | Investigate actual failures and operational trends | Requires authorized access, tracing, retention, and redaction |
| Synthetic test data | Broaden scenario coverage | Validate its labels, realism, and duplication |

For saved answers, see [Evaluate datasets with the Microsoft Foundry SDK](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-datasets).
To generate new answers, see [Evaluate models and agents with the Microsoft Foundry SDK](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-targets).
Either approach can support capability or regression evaluations.

[Evaluation datasets in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets) explains that reusable datasets are not always required; existing responses or traces can be evaluated directly. Use an immutable regression dataset when repeatable
candidate comparison matters, not as a mandatory ritual for every diagnosis.

## 2. Select evaluators

Choose grading methods for the task: deterministic checks when possible,
Foundry evaluators from the catalog, and human review where interpretation or
calibration needs it. In agent-evaluation methodology, a **grader** is logic
that scores an aspect of performance and may be code-based, model-based, or
human. 

Construct a rubric evaluator for domain-specific outcomes and appropriate built-in 
quality and safety evaluators. Check the 
[Built-in Evaluators Reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)
for supported levels and inputs. 

## 3. Run the evaluation

Choose when to run and how to launch the evaluation. Run it on demand during
development, as part of CI/CD for promotion decisions, or on a recurring basis
to monitor production traffic. Use the portal to explore a run with reviewers,
or the SDK for repeatable result retrieval and application integration.
A scheduled regression job on fixed test cases is not the same as evaluating
sampled live traffic.

The [first evaluation lab](../first-evaluation/first-evaluation.md) demonstrates
the evidence-to-decision loop locally. For more specific workflows, see
[RAG evaluation](../rag-responses/rag-responses.md),
[conversation evaluation](../agent-conversations/agent-conversations.md), or
[release automation](../release-gates/release-gates.md).

## 4. Review and improve

Before interpreting scores, confirm that the results belong to the intended
candidate and that required checks returned valid results. Start with aggregate
metrics, then inspect individual results for recurring failures.

Fix any recurring problems, then rerun the same cases with the same scoring
configuration to compare versions. See
[Interpret results and compare versions](../results/results.md) for comparison
and failure analysis.
