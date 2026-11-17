---
title: "Establish an AI evaluation practice"
subtitle: "E00 | A leadership roadmap from real tasks to reliable decisions | Draft"
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Start before the complaints

- Name the customer decision
- Define what success and failure look like
- Build evidence before relying on intuition

::: notes
Foundry's workflow starts by deciding what to evaluate:
https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview
The roadmap adapts the “Going from zero to one” section of
[“Demystifying evals for AI agents”](https://www.anthropic.com/research/demystifying-evals-for-ai-agents);
it is not a
Foundry-required process:
:::

# Anchor on an outcome

- Current, useful policy answer
- Customer-authorized order lookup
- Confirmed ticket, not a success claim
- Safe and sustainable operation

::: notes
For each outcome, name the evidence and the person accountable for deciding
whether it is acceptable. These are illustrative Contoso Support examples.
:::

# Step 0–1: Start small, use real work

- Define intended behavior early
- Reuse manual checks and common user tasks
- Add support issues and observed failures
- Prioritize by customer impact, not row count

::: notes
“Demystifying evals for AI agents” recommends starting early and building from
manual checks and real failures. Its example task volumes are context-specific,
not a universal minimum:
https://www.anthropic.com/research/demystifying-evals-for-ai-agents
:::

# Step 2–3: Make cases clear and balanced

- Reviewers agree on what success means
- A reference solution checks task solvability
- Test when behavior should and should not occur
- Label important slices and edge cases

::: notes
For Contoso, test both confirmed escalation and no ticket without confirmation.
A failed valid solution may indicate an ambiguous task or grader, not an agent
defect. Balance avoids rewarding overuse or underuse of a capability.
:::

# Step 4: Stabilize trials and verify outcomes

- Start each trial from known state
- Keep the evaluation environment representative
- Record transcripts, tools, versions, and conditions
- Verify effects independently

::: notes
The agent harness lets the model act; the evaluation harness sets up trials,
records and grades evidence. Shared state can distort results. A claimed ticket
is not proof of a persisted ticket. The isolation and harness distinction are
from “Demystifying evals for AI agents”:
https://www.anthropic.com/research/demystifying-evals-for-ai-agents
:::

# Step 5: Match graders to the question

- Code-based: exact checks and observed effects
- Model-based: open-ended quality against a rubric
- Human: expert review and calibration
- Verify real outcomes, not easy-to-game proxies

::: notes
A grader is scoring logic; Foundry uses evaluator for its product interfaces.
Use deterministic checks where possible, model graders where interpretation
helps, and human review judiciously. Calibrate model judgments against people.
:::

# Use scores to learn, policy to release

- Partial credit can show progress
- Combine grader results by declared policy
- Keep required evidence and blocking criteria explicit
- Missing or invalid results cannot pass the gate

::: notes
Partial credit can help diagnose multi-part tasks, but it does not waive required
release criteria. A grading rule should verify the intended outcome, not only a
superficial proxy. See “Demystifying evals for AI agents” and the repository's fail-closed
policy:
https://www.anthropic.com/research/demystifying-evals-for-ai-agents
:::

# Step 6: Read transcripts and grades

- Is the failure genuine?
- Was the task ambiguous or impossible?
- Did the grader reject a valid solution?
- Did the harness or environment constrain success?

::: notes
Review successful and failed trials. A fair failure has a clear reason and
supports a specific improvement; do not take a summary score at face value.
:::

# Step 7: Watch for saturation

- Easy capability suite? It may stop showing progress
- Keep useful tasks as regression checks
- Add reviewed cases that expose new gaps
- Don't infer a universal pass threshold

::: notes
Capability evaluations measure what the agent can do; regression evaluations
check whether prior behavior still works. A saturated capability suite may remain
valuable for regression.
:::

# Step 8: Make maintenance routine

- Assign owners for tasks, graders, and infrastructure
- Invite product and domain experts to contribute cases
- Use evaluations during development
- Refresh acceptance evidence without tuning on it

::: notes
Treat the evaluation suite as a living product asset. Preserve versions so
historical release decisions remain interpretable.
:::

# Combine signals; no one method is enough

- Automated evaluations before release
- Production monitoring and user feedback
- Manual transcript review and human evaluation
- A/B tests when the decision requires live comparison

::: notes
These methods answer different questions. Select the combination according to
decision and risk. “Demystifying evals for AI agents” discusses this broader
view of agent performance:
https://www.anthropic.com/research/demystifying-evals-for-ai-agents
Foundry human evaluation: https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation
:::

# Fund the whole decision loop

- Target and judge inference
- Simulation, telemetry, and storage
- Human review, access, and retention
- Budget, exceptions, and rollback ownership

# Launch-readiness check

- Can we explain a pass and a failure?
- Can we separate agent, task, grader, and environment issues?
- Does missing required evidence block release?
- Can we reconstruct the decision later?

# Grounding and next path

[Foundry workflow](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)

[“Going from zero to one” roadmap](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)

[Human evaluation](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/human-evaluation)

Next: E01 workflow selection; E13 architecture.
