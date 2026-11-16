# E01 plan: choose a workflow

## Purpose
Help customers choose unit, evidence source, criteria, and execution surface.
Outcome: a written evaluation contract and an appropriate next how-to.

## Audience
Developers new to evaluations; architects can use the decision tables.

## Outline
1. Start with the decision.
2. Name the task and choose turn or conversation as the evaluation unit.
3. Distinguish capability evaluations (what an agent can do) from regression
   evaluations (whether previously working behavior still works).
4. Choose evidence: precomputed responses, responses generated at run time,
   traces, synthetic data, or simulation.
5. Select compatible evaluators/grading methods and portal/SDK/CLI execution.
6. Write an evaluation contract and verify coverage, attribution, and missing
   or skipped results.
7. Walk through a measurable Contoso success criterion and distinguish
   interpretation from an observable result.
8. Route to first evaluation and specialist articles.

## Prerequisites and boundaries
No deployment prerequisite for recorded-output workflows. Contract example is
editorial JSON, not an SDK request schema. CLI and SDK generations are separate.
Introduce M01 task, trial, and grader as agent-evaluation methodology terms;
distinguish Anthropic's grader categories from Foundry evaluator interfaces.
Capability and regression purposes are distinct and do not prescribe Foundry
thresholds. Do not equate turn/conversation unit, evidence source, evaluation
purpose, or execution surface.

## References
F01: [overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview).
F02: [catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators).
F04: [datasets](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets).
F06: [levels](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations).
F13: [CLI](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/azure-developer-cli-evaluation).
F28: [precomputed responses](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-datasets).
F29: [responses generated at run time](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-targets).
M01: [agent-evaluation methodology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
M03: [success criteria and tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests).

## Acceptance
Decision table defines the decision, evaluation unit, purpose, evidence source,
grading approach, and execution surface as separate choices. Explain capability
versus regression evaluations and task/trial/grader at first use, attributing
methodology terms and linking sources. Concrete contract; no
pipeline-as-universal-workflow claim.
Include a Contoso example with an observable, task-specific success criterion;
do not import illustrative numeric targets as Foundry requirements.
