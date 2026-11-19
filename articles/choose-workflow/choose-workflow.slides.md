---
title: "Choose your Foundry evaluation workflow"
subtitle: "E01 | Decision workshop | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Decide what the evidence is for

- Diagnose
- Compare candidates
- Approve release
- Detect operational drift

::: notes
The workshop follows Microsoft Learn's [Build an evaluation workflow](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview#build-an-evaluation-workflow):
choose what to evaluate, select evaluators, run the evaluation, then review and
improve.
:::

# 1. Choose what to evaluate: task and purpose

- Task: test inputs and success criteria
- Trial: one attempt at a task
- Capability: what can the agent do?
- Regression: does prior behavior still work?

::: notes
Task and trial are agent-evaluation methodology terms. Capability and regression
describe different evaluation purposes, not evaluation units or execution tools.
See [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
:::

# 1. Choose what to evaluate: unit

- Turn: one response in context
- Conversation: complete interaction outcome
- Polite turns can still form a failed journey

::: notes
Messages alone do not select conversation-level scoring. Specify the level:
https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations
:::

# 1. Choose what to evaluate: evidence

- Precomputed responses
- Responses generated at run time
- Completed conversation data
- Production response/trace
- Synthetic data or simulated user

::: notes
Foundry documents evaluating precomputed responses and evaluating responses
generated at run time as distinct workflows:
https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-datasets
https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-targets
:::

# 2. Select evaluators

- Business rubric
- Compatible Foundry evaluators
- Deterministic checks and human review
- Exact tool-effect assertions

::: notes
Anthropic uses grader for scoring logic that may be code-based, model-based, or
human. Foundry's evaluator is a product interface. These terms are related but
not interchangeable API names.
Methodology: https://www.anthropic.com/research/demystifying-evals-for-ai-agents
:::

# Write the evaluation contract

- Decision, unit, source
- Observable criterion: confirmed ticket has the right customer and issue
- Observed candidate identity
- Required evidence
- Missing/skipped results block
- Held-out data and policy owner

::: notes
Make success concrete: a ticket is created only after confirmation, belongs to
the right customer and issue, and is not claimed without an observed record.
“Define success criteria and build evaluations” recommends task-specific
criteria; its examples are not Foundry request requirements:
https://platform.claude.com/docs/en/test-and-evaluate/develop-tests
:::

# 3. Run the evaluation

- On demand during development
- In CI/CD for promotion decisions
- On a recurring basis for production monitoring
- Choose the portal, SDK, or CLI as appropriate

::: notes
Cadence and execution tooling are separate choices. See
[Run agent evaluations with the azd CLI (preview)](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/azure-developer-cli-evaluation)
for the independently versioned evaluation extension.
:::

# 4. Review and improve

- Verify candidate identity and required results
- Inspect individual failures behind the metrics
- Fix recurring issues
- Rerun comparable cases to check for improvement

::: notes
A strong communication score does not offset a missing ticket record. Inspect
the evidence to distinguish an agent failure from a gap in the evaluation.
:::

# Avoid the false shortcuts

- Dataset registration is not always required
- Reference answer is not actual response
- Scaffolding does not produce evidence
- Completed run is not passing coverage

# Grounding and next path

[Build an evaluation workflow](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview#build-an-evaluation-workflow)

[Datasets](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets)

[Catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)

Next: E02 first evaluation.
