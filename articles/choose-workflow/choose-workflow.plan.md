# E01 plan: choose a workflow

## Purpose
Help customers apply the four-step Foundry workflow to a concrete decision.
Outcome: a written evaluation contract and an appropriate next how-to.

## Audience
Developers new to evaluations; architects can use the decision tables.

## Outline
1. Choose what to evaluate: name the decision, task, and purpose; consult the
   evaluator catalog; choose a turn or conversation and an evidence source.
2. Select evaluators: define observable Contoso success criteria, choose
   compatible graders, and capture the choices in an illustrative contract.
3. Run the evaluation: choose the cadence and execution surface separately.
4. Review and improve: verify coverage and candidate attribution, inspect
   aggregate and individual results, and use recurring failures to guide changes.

## Prerequisites and boundaries
No deployment prerequisite for recorded-output workflows. Contract example is
editorial JSON, not an SDK request schema. CLI and SDK generations are separate.
Introduce M01 task, trial, and grader as agent-evaluation methodology terms;
distinguish Anthropic's grader categories from Foundry evaluator interfaces.
Capability and regression purposes are distinct and do not prescribe Foundry
thresholds. Do not equate turn/conversation unit, evidence source, evaluation
purpose, or execution surface.

## References
F01: [Build an evaluation workflow](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview#build-an-evaluation-workflow)
(four-step structure verified 2026-11-19).
F02: [catalog](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators)
(listing reviewed 2026-11-19).
F04: [datasets](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-datasets).
F06: [levels](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations).
F07: [rubric evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators).
F13: [CLI](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/azure-developer-cli-evaluation).
F28: [precomputed responses](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-datasets).
F29: [responses generated at run time](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-targets).
M01: [agent-evaluation methodology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
M03: [success criteria and tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests).

## Acceptance
The article and slides follow the four Foundry steps. Keep the decision,
evaluation unit, purpose, evidence source, grading approach, and execution
surface distinct. Explain capability
versus regression evaluations and task/trial/grader at first use, attributing
methodology terms and linking sources. Concrete contract; no
pipeline-as-universal-workflow claim.
Include a Contoso example with an observable, task-specific success criterion;
do not import illustrative numeric targets as Foundry requirements.
