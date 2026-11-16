# E02 plan: first evaluation

## Purpose
Complete a small, honest evidence-to-decision loop before adding cloud complexity.
Outcome: baseline report passes, a regressed candidate fails, and the reader
understands what was and was not evaluated.

## Audience
Developers following a self-guided first evaluation; facilitators can reuse the
practice tasks.

## Outline
1. Define the support outcome, turn-level unit, and local fixture boundary.
2. Prepare the local environment, run baseline, and inspect item evidence.
3. Run a regressed candidate, explain the mismatch, and interpret the gate.
4. Optionally evaluate precomputed responses in Foundry: explain groundedness,
   then keep cloud prerequisites, Bash setup, submission, and interpretation
   together. Put environment instructions before the commands that need them.
5. Preserve cloud evidence and resume retrieval without resubmitting.
6. Practice locally and use next-step links for generating responses at run time,
   portal evaluation, datasets, and result analysis.

## Prerequisites and boundaries
Python 3.9+ for offline path; no environment variables or credentials required.
Optional cloud uses Python 3.11 and requires compatible pinned SDK, roles,
project, judge deployment, and cost approval. No live-cloud validation claim.
The optional adapter evaluates precomputed responses only; it requests turn-level
groundedness as an advisory signal, not a cloud release gate. Use the concepts
and terminology in the grounding documentation, not invented workflow names.
Keep local execution, SDK/mock checks, and live-cloud validation distinct.

## References
F01: [overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview).
F03: [SDK setup](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation).
F09: [results](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results).
S01: [SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python).
S03: [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations).
F26: [portal workflow](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluate-generative-ai-app).
F28: [evaluate precomputed responses in datasets](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-datasets).
F29: [evaluate responses generated at run time](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-targets).
S04: [release-pinned groundedness example](https://github.com/Azure/azure-sdk-for-python/blob/azure-ai-projects_2.2.0/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_groundedness.py).

## Acceptance
Executable repository-root commands and linked getting-started instructions.
Complete the local demo before introducing optional cloud setup; explain the
baseline pass, regression rejection, and limits of fixture evidence.
Cloud setup retains endpoint and `.env` examples, pinned dependencies, identity,
upload approval, and budget boundaries. Submission, result inspection, exit-code
semantics, and resume instructions form a complete optional procedure.
Terminology and direct links match the documented workflows; alternatives appear
only as next steps. No generated Office snapshots are refreshed by this edit.
