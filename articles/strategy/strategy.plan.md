# E00 plan: establish an evaluation practice

## Purpose
Explain why teams invest in evaluations and how to build and maintain a useful
evaluation practice, rather than treating evaluation as a one-time score report.

Customer outcome: leaders can connect Contoso Support outcomes to evidence and
accountable decisions, assign owners, fund the work, and approve a release policy.

## Audience
IT leaders, product owners, and architects. No code in article or slides.

## Outline
1. Introduce evaluation and the reasons to invest: baselines, regression
   detection, clearer requirements, scalable testing, model adoption, and
   evaluation-driven development. Situate evaluation alongside other signals
   and account for variable outcomes.
2. Use Contoso Support to connect customer outcomes to evidence and accountable
   product, engineering, application, safety, and platform decisions.
3. Define task, trial, grader, transcript, outcome, evaluation harness, agent
   harness, and evaluation suite.
4. Introduce the different ways to classify evaluations: Foundry evaluator
   categories, grading methods, evaluation purpose, application architecture,
   and turn or conversation level. Explain why complementary evaluators may
   be useful.
5. Introduce the M01 roadmap and collect initial tasks: start early, turn
   existing checks and failures into tasks, make tasks clear and solvable, and
   balance when behavior should and should not occur (steps 0-3).
6. Design the evaluation harness and graders: stabilize and isolate trials,
   verify outcomes independently, select code-based, model-based, and human
   grading, and calibrate judgments (steps 4-5). Explain reference answers,
   rubric evaluators, partial credit, and necessary process constraints.
7. Maintain and use the suite: review transcripts and grades, watch capability
   suites for saturation, retain useful regression coverage, assign owners, and
   refresh evidence through a versioned process (steps 6-8).
8. Combine evaluation with monitoring, user feedback, A/B tests, and human
   review. Set evidence and release policy, fund the full operating loop, and
   close with the leadership launch checklist and next steps.

## Prerequisites and boundaries
No deployed agent required; teams can evaluate existing outputs. Contoso Support
is illustrative, not a production design. The article requires no code and does
not establish live-cloud validation.

Adapt M01's zero-to-one roadmap for a leadership audience; do not copy its
illustrative task counts or imply the sequence is a Foundry requirement. Use M01
for methodology and Foundry documentation for service behavior. Distinguish
evaluator categories, grading methods, evaluation purposes, application
architectures, and evaluation levels; do not imply they map one-to-one.
Capability and regression evaluations have different purposes and do not imply
universal pass thresholds.

Avoid compliance guarantees, universal sample sizes, assumed evaluator defaults,
and guaranteed cost or productivity benefits. No single method provides a complete
picture. Partial credit can inform diagnosis without waiving required release
evidence; missing or invalid required results must not pass a release gate.

## References
F01: [workflow model](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview).
F07: [rubric evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rubric-evaluators);
recommendation and scoring options checked in documentation on 2026-11-18.
F11: [human review](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation).
F15: [permissions](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions).
M01: [agent-evaluation methodology](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).
F02: [built-in evaluators reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/built-in-evaluators).
Candidate grounding for the article's category list and evaluation levels;
add to the E00 catalog sources when the article is revised to cite it.

F01, F02, F07, and M01 were inspected for this plan on 2026-11-23. This is not
a complete source refresh or a live-service validation.

## Acceptance
- Introduce the value of evaluations, Contoso outcomes and owners, key terms,
  and evaluation dimensions before the M01 roadmap.
- Follow the roadmap's steps in order; cover balanced, solvable tasks, isolated
  trials, grading and calibration, transcript review, suite saturation, and
  ownership.
- Distinguish source recommendations and methodological terms from Foundry
  capabilities, support classification with citations, and qualify benefits
  and tradeoffs.
- Explain complementary evidence methods, required release evidence, operating
  costs, and ownership in a leadership checklist. Do not prescribe code, a
  fixed task count, a universal threshold, or partial credit as gate acceptance.
- The slide narrative is a curated adaptation of the article's main points.
  Editorial state: draft; acceptance and customer validation remain pending.

## Current draft review notes
- **Evaluation test types:** cite the source for Foundry categories and
  distinguish its evaluator catalog from grading methods, evaluation purpose,
  application architecture, and evaluation level. M01 describes capability
  and regression as purposes; it does not establish "workflow" as a third
  purpose. Check category completeness against F02, including audio and Azure
  OpenAI graders, rather than presenting a partial list as exhaustive.
- **Why invest / choose graders:** qualify claims that evaluations remove
  guesswork, always speed model adoption, or that cost and effort increase in a
  fixed order across grader types. Costs and benefits depend on the task,
  implementation, and operating context.
- **Definitions / grader support:** attribute the methodological definitions to
  M01 near their use. Clarify Foundry's evaluator interfaces and human-review
  workflow without implying that every grading method is the same kind of
  registered evaluator.
- **Slides:** the current deck covers the roadmap and outcomes but does not
  explicitly introduce the article's definitions or evaluation dimensions;
  review whether its audience needs those concepts in the curated narrative.
