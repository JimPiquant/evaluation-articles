# E00 plan: establish an evaluation practice

## Purpose
Make evaluation a decision-making capability rather than a one-time score report.
Outcome: leaders can assign owners, fund evidence collection, and approve a release policy.

## Audience
IT leaders, product owners, and architects. No code in article or slides.

## Outline
1. Explain why evaluation should begin early and how it prevents reactive,
   production-only learning.
2. Build an initial task set from manual checks, user feedback, and observed
   failures; prioritize by customer impact.
3. Make tasks unambiguous and solvable; use reference solutions to check task
   and grader configuration.
4. Balance tasks for behaviors that should and should not occur.
5. Provide a stable, isolated environment and independently verified outcomes.
6. Select graders deliberately; use partial credit for diagnosis without
   weakening required release policy, and calibrate model judgments with people.
7. Review transcripts and grades to identify agent, task, grader, and harness
   failures.
8. Watch capability suites for saturation while retaining useful regression
   coverage.
9. Establish suite ownership, eval-driven development, holistic evidence,
   operating budget, and a leadership launch checklist.

## Prerequisites and boundaries
No deployed agent required. Contoso Support is illustrative, not a production design.
Avoid compliance guarantees, universal sample sizes, and assumed evaluator defaults.
Adapt M01's zero-to-one roadmap for a leadership audience; do not copy its
illustrative task counts or imply the sequence is a Foundry requirement. Use M01
for evaluation methodology, not Foundry service behavior. No single evaluation
method provides a complete picture; no fixed task count guarantees confidence.
Capability and regression evaluations have different purposes and do not imply
universal pass thresholds.

## References
F01: [workflow model](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview).
F07: [rubric evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators);
recommendation and scoring options checked in documentation on 2026-11-18.
F11: [human review](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation).
F15: [permissions](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions).
M01: [agent-evaluation methodology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

## Acceptance
The article follows M01's steps in order, distinguishes methodology from
Foundry-supported workflows, includes customer outcomes and accountable owners,
balanced tasks, harness/grader/transcript review, suite saturation and ownership,
complementary evidence methods, and a leadership checklist. No code, fixed task
count, universal threshold, or conflation of partial credit with gate acceptance.
The slide narrative accurately summarizes the roadmap. Editorial state: draft.
