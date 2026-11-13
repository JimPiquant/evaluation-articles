---
title: "Secure evaluation identities and networks"
description: "Separate caller, project, and runtime permissions by workflow."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Secure evaluation identities and networks

Evaluation can involve several identities and resources. "Give the developer
Contributor" is not an adequate permission design. Start with the actual
workflow and use the [evaluation permission matrix](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions).

## Separate identities

| Identity | Purpose | Scope to verify |
|---|---|---|
| Human/application caller | Submit and review runs | Foundry resource/project; account scope for model inference where required |
| Project managed identity | Service access to traces/storage and rules | Connected resources and rule requirements |
| Agent runtime identity | Access application knowledge/tools | Business-service permissions, distinct from evaluator access |
| Role-assignment administrator | Grant approved access | Target scope with role-assignment permission |

Current names include Foundry User, Owner, Account Owner, and Project Manager;
older Azure AI names can still appear during rollout. IDs/core permissions are
unchanged by renaming.

The source explicitly states that model inference may require Foundry account
scope: a project-only role does not authorize that operation. Trace access and
bring-your-own storage have additional identity-specific requirements.

Contributor does not by itself grant `Microsoft.Authorization/roleAssignments/write`.
Use appropriately authorized administration and least privilege; do not grant
every listed role to every identity.

## Record a workflow-specific access decision

This illustrative artifact is not an Azure role-assignment request:

```json
{
  "workflow": "recorded-output-evaluation",
  "caller": "evaluation-workload-identity",
  "project_identity": "service-managed-identity",
  "resources": ["approved-project", "judge-account"],
  "trace_access": "not-required-for-this-workflow",
  "approval": "platform-owner"
}
```

Add trace permissions only when using traces. The current matrix distinguishes
Application Insights Reader, protected-content access, workspace modes, and
caller versus project identity. Copy the relevant source rows into the access
request rather than inventing a one-role-fits-all shortcut.

## Match federation to execution context

Use workload identity rather than long-lived secrets for cloud CI where supported.
The trusted subject must match the actual branch, PR, or environment context.
A subject restricted to `main` does not automatically cover a PR job.

Protect privileged cloud acceptance from untrusted PR code. Offline fixture tests
need no cloud identity and should remain runnable without secrets. If a protected
environment approves evaluation, include its data access and budget policy.

## Verify networking independently

Follow [evaluation VNet guidance](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-virtual-network)
for the exact data source and execution path. Evaluation-only templates and
requirements are not the same as full agent application infrastructure.

Verify where the client/runner executes, approved route, DNS, endpoint access,
connected storage, and telemetry connectivity. A successful role assignment does
not establish network reachability. A timeout is not automatically an
authentication failure.

Separate 401/403 identity/scope checks from private-endpoint/DNS/route checks.
Use approved access rather than weakening production network policy to complete
a test.

## Protect data and retire access

Review trace and tool-result sensitivity before granting reviewer or export access.
Redaction must precede reusable dataset publication. Do not include keys or
personal records in this repository; `.env` and generated evidence remain ignored.

Assign owners for access review, connection retirement, rule disabling, and
artifact retention. When a workflow ends, remove unused grants and credentials
without destroying evidence required by approved policy.

Continue with the [operations runbook](../../articles/operations/operations.md).
