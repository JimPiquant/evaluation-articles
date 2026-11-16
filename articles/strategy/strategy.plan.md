# E00 plan: establish an evaluation practice

## Purpose
Make evaluation a decision-making capability rather than a one-time score report.
Outcome: leaders can assign owners, fund evidence collection, and approve a release policy.

## Audience
IT leaders, product owners, and architects. No code in article or slides.

## Outline
1. Decide which customer outcomes matter.
2. Allocate product, engineering, safety, and platform ownership.
3. Separate quality, safety, reliability, and operational evidence.
4. Combine automated evaluations with production monitoring, user feedback,
   manual transcript review, and systematic human evaluation as appropriate.
5. Distinguish capability evaluations from regression evaluations and assign
   owners for suite maintenance.
6. Establish calibrated acceptance, escalation, and budget policies.
7. Adopt an evaluation-driven learning loop with trace feedback and held-out
   validation.
8. Use a launch-readiness checklist.

## Prerequisites and boundaries
No deployed agent required. Contoso Support is illustrative, not a production design.
Avoid compliance guarantees, universal sample sizes, and assumed evaluator defaults.
Use M01 for evaluation methodology, not Foundry service behavior. No single
evaluation method provides a complete picture; no fixed task count guarantees
confidence. Capability and regression evaluations have different purposes and
do not imply universal pass thresholds.

## References
F01: [workflow model](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview).
F11: [human review](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation).
F15: [permissions](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions).
M01: [agent-evaluation methodology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

## Acceptance
Concrete owner/decision table, multi-method learning loop, separate capability
and regression purposes, explicit suite ownership, separate recommendation
versus product fact, no code, source-backed claims, and a leadership slide
narrative. Editorial state: draft.
