---
title: "Choose your Foundry evaluation workflow"
description: "Choose what to evaluate, select evaluators, run the evaluation, and use the results to improve."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Choose your Foundry evaluation workflow

Microsoft Foundry provides evaluation workflows for assessing the quality and
safety of models and agents. You can evaluate saved responses, generate new
responses from a model or agent, or analyze completed conversations and
production traces.

Before choosing an SDK or evaluator, identify your objective: diagnose an
answer, compare two candidates, approve a release, or detect an operational
regression. That decision determines the evaluators you select and evidence you 
need to run the evaluators.

This article follows the four steps in Microsoft Learn's
[Build an evaluation workflow](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview#build-an-evaluation-workflow).
It helps you choose what to evaluate, select evaluators, run an evaluation, and
review the results to guide improvements.

## 1. Choose what to evaluate

### Define the task and evaluation purpose

A **task** (or test case) is one test with defined inputs and success criteria.
Each attempt at a task is a **trial**; repeat trials when you need to understand
variation in agent behavior. This terminology follows
[Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents);
it is not a Foundry request schema.

Choose the purpose separately from the evaluation unit. **Capability
evaluations** ask what an agent can do and help identify areas to improve.
**Regression evaluations** check whether behavior that worked before still works
after a change. The same task may contribute to either purpose at different
stages, but the result has meaning only relative to the intended decision.
These purposes do not prescribe a universal pass threshold.

### Choose the evaluation unit

A turn-level evaluation asks whether an individual response is useful, relevant,
supported, or safe in its context. A conversation-level evaluation asks whether
the whole interaction achieved the task and respected the intended process.

For Contoso Support, a clear order-status answer is a turn. Repeatedly asking
for the same information, obtaining consent, invoking a ticket tool, and confirming
the result form a conversation. Each response might be polite while the customer
still leaves without a resolution.

Use complete `messages` data for a conversation and an explicit compatible
evaluation level. [Choose an evaluation level](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations#choose-an-evaluation-level)
states that omitted `evaluation_level` defaults to turn and that Foundry skips
evaluators that don't support conversation-level scoring on conversation-level
runs. Dataset shape alone does not determine the scoring level.

### Choose where evidence comes from

| Evidence | Good starting use | Important boundary |
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

[Evaluation datasets in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets)
explains that reusable datasets are not always required; existing responses or
traces can be evaluated directly. Use an immutable regression dataset when repeatable
candidate comparison matters, not as a mandatory ritual for every diagnosis.

## 2. Select evaluators

Choose grading methods for the task: deterministic checks for exact effects,
compatible Foundry evaluators, and human review where interpretation or
calibration needs it. In agent-evaluation methodology, a **grader** is logic
that scores an aspect of performance and may be code-based, model-based, or
human. Foundry uses **evaluator** for its supported interfaces; the terms are
related, not interchangeable API names. Choose a business rubric for
domain-specific outcomes and appropriate built-in quality and safety evaluators.
Check the [Built-in Evaluators Reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)
for supported levels and inputs. Irrelevant scores can obscure the results that
matter, model-based checks can add inference cost, and incompatible checks can
be skipped.

For example, a ticket conversation needs verified ticket creation, tool/process
quality, and a rubric covering correct escalation and communication. A RAG answer
needs independent retrieved evidence. Coherence alone answers neither question.

### Write the evaluation contract

Make success observable rather than aspirational. For a Contoso ticket task,
"help the customer" is too vague; a testable criterion is: *after the customer
confirms escalation, the ticket record exists for that customer and issue, and
the final response does not claim creation without the returned record*. This
captures both a required effect and truthful communication. [“Define success
criteria and build evaluations”](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
recommends specific, task-relevant criteria;
its examples are methodology, not Foundry request requirements.

This local JSON illustrates a decision artifact, **not a Foundry request schema**:

```json
{
  "decision": "approve-support-candidate",
  "unit": "conversation",
  "source": "completed-messages",
  "candidate": "verified-deployment-version",
  "required_evidence": ["business-rubric", "tool-effects", "safety"],
  "on_missing_or_skipped": "block",
  "acceptance_data": "held-out-support-v1"
}
```

Agree this contract before tuning. The actual SDK schema, registered evaluator
names, and result mapping depend on the chosen surface and version.
See [task design](../datasets/datasets.md) for turning a goal into a test case.

## 3. Run the evaluation

Choose when to run and how to launch the evaluation. Run it on demand during
development, as part of CI/CD for promotion decisions, or on a recurring basis
to monitor production traffic. Use the portal to explore a run with reviewers,
or the SDK for repeatable result retrieval and application integration.
A scheduled regression job on fixed test cases is not the same as evaluating
sampled live traffic.

To [Run agent evaluations with the azd CLI (preview)](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/azure-developer-cli-evaluation),
use the separately versioned `azure.ai.evaluations` extension. Its recipe
is `evals/azure.eval.yaml`; scaffolding does not deploy an agent or generate rows.
Agent CLI installation alone does not supply evaluation commands.

The [first evaluation lab](../first-evaluation/first-evaluation.md) demonstrates
the evidence-to-decision loop locally. For more specific workflows, see
[RAG evaluation](../rag-responses/rag-responses.md),
[conversation evaluation](../agent-conversations/agent-conversations.md), or
[release automation](../release-gates/release-gates.md).

## 4. Review and improve

Before interpreting scores, confirm that the results belong to the intended
candidate and that required checks returned valid results. Start with aggregate
metrics, then inspect individual results for recurring failures. For Contoso
Support, a strong communication score doesn't offset a missing ticket record.
Inspect the ticket evidence and transcript to determine whether the agent
failed to create the ticket or the evaluation failed to capture the outcome.

Fix the recurring problem, then rerun the same cases with the same scoring
configuration to compare versions. See
[Interpret results and compare versions](../results/results.md) for comparison
and failure analysis.
