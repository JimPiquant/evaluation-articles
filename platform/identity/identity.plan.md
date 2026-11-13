# P02 plan: identities and networking

## Purpose
Prevent permission/network assumptions from undermining evaluation.
Outcome: least-privilege identity matrix and workflow-specific connectivity checks.

## Audience
Operators and identity/platform engineers.

## Outline
1. Separate caller, project managed identity, and application runtime.
2. Choose resource/project/model/storage/telemetry scopes.
3. Match CI federation to the actual subject.
4. Select evaluation-only network requirements.
5. Diagnose auth versus network failures.
6. Control trace privacy, access, cost, and retirement.

## Prerequisites and boundaries
No one-role-fits-all claim. Contributor does not itself grant role assignment.
Identity example is a decision artifact, not deployable Azure RBAC JSON.

## References
F15: [evaluation permissions](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions).
F16: [evaluation networking](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-virtual-network).

## Acceptance
Concrete identity mapping, correct federation distinction, no invented deployment API.
