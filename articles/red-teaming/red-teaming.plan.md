# E12 plan: adversarial testing

## Purpose
Plan authorized adversarial evaluation as a distinct evidence activity.
Outcome: scoped test charter, protected environment, finding triage, and regression loop.

## Audience
Developers and authorized safety reviewers.

## Outline
1. Define authorized targets, risks, and stop conditions; design realistic
   multi-turn scenarios around explicit risk hypotheses and benign controls.
2. Use current Foundry workflow and supported limits.
3. Separate simulation, ordinary safety evaluation, and adversarial search.
4. Execute only in an isolated sandbox and preserve lineage.
5. Triage and re-test fixes; convert safe findings into regression evidence.
6. Manage residual risk.

## Prerequisites and boundaries
No exploit payloads or live attacks. CLI/PyRIT mechanics link maintainer docs
rather than invent unvalidated APIs. Scope artifact example is non-executable policy.

## References
F01: [overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview).
F08: [safety](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/risk-safety-evaluators).
F21: [Foundry red teaming](https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent).
F27: [region/limit reference](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-regions-limits-virtual-network).
M02: [safety-evaluation methodology](https://www.anthropic.com/research/building-strong-safety-evaluations).

## Acceptance
Permission, target/version attribution, sandbox side effects, stop/triage checklist.
Scenario rationale, expected behavior, benign controls, evidence, and limitations
are recorded; no claim that adversarial probing exhausts risk.
