---
title: "Automate evaluations and release decisions"
description: "Fail closed on incomplete evidence and prove that a degraded candidate is blocked."
author: "Evaluation articles contributors"
date: "2026-11-13"
---

# Automate evaluations and release decisions

Automation should enforce an agreed policy, not merely run an evaluator. Separate
"the evaluation completed" from "the candidate passed." Both success and failure
must preserve reviewable evidence.

## Define the contract first

Centralize the required criteria, scored coverage, allowed errors/skips, target
attribution, threshold direction, critical-slice constraints, and exception
process. Distinguish blocking criteria from advisory information.

The [sample policy](../../samples/contoso-evaluation/README.md) is the authority
for its fixture gate. Articles do not duplicate its thresholds as universal
Foundry defaults. Cloud results require an adapter for the actual
[service result schema](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-results).

Item-level diagnostic scores or partial credit can help explain progress, but
they do not override the release contract. If a required criterion is missing,
skipped, errored, or below its blocking threshold, preserve that detail and block
acceptance. An explicitly approved analytical exclusion may be useful for
diagnosis, with its denominator disclosed; it cannot turn incomplete required
evidence into a passing release. M01 discusses partial credit as an evaluation
methodology option:
[Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents).

Missing metrics, nonfinite scores, zero scored rows, inconsistent counts, unknown
candidate version, and truncated output must block. The
[conversation guide](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/cloud-evaluation-conversations)
explicitly warns that unsupported evaluators can be skipped; check required
coverage rather than trusting terminal success.

## Prove the gate locally

From the repository root:

```bash
python3 samples/contoso-evaluation/run.py \
  --candidate baseline --output build/evaluation/baseline.json
python3 samples/contoso-evaluation/gate.py build/evaluation/baseline.json
python3 samples/contoso-evaluation/run.py \
  --candidate regressed --output build/evaluation/regressed.json
if python3 samples/contoso-evaluation/gate.py build/evaluation/regressed.json; then
  echo "ERROR: regressed candidate was accepted" >&2
  exit 1
else
  status=$?
  test "$status" -eq 1
fi
```

The workflow should retain both reports. Unit tests also prove missing/invalid
evidence fails; an expected nonzero candidate gate must not hide a crashed
evaluation command. Run generation first and separately require its success.

The active root evaluation workflow exercises this offline path. It does not
claim live Foundry PR evaluation or need cloud credentials. Archived nested
workflows are not the maintained CI implementation.

## Choose the cloud execution surface

Use SDK code when you need custom evidence retrieval and policy normalization.
The [Foundry GitHub integration](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluation-github-action)
provides an Actions path; inspect the exact action version and outputs before
depending on its gating behavior.

[Agent Framework](https://learn.microsoft.com/en-us/agent-framework/agents/evaluation)
also provides evaluation orchestration and Foundry integration that can be used
from an application's development workflow. Treat that as a separate,
language- and package-version-specific implementation: verify how its
`EvalResults` and provider outputs map to your release contract before gating.
This series does not implement that CI integration, and framework behavior does
not replace Foundry service contracts or the repository's offline fixture gate.

The [preview evaluation CLI](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/azure-developer-cli-evaluation)
uses a recipe in `evals/azure.eval.yaml` and supports `--fail-on`. Scaffolding
does not generate rows, deploy targets, or establish evaluator compatibility.
Keep extension versions and recipe semantics separate from older local
`eval.yaml` optimizer intent.

For [Azure DevOps](https://learn.microsoft.com/en-us/azure/foundry/how-to/evaluation-azure-devops),
the extension has its own task inputs, data-file format, and service-connection
requirements. Verify its selected version and outputs; do not assume it consumes
the SDK JSONL or the CLI recipe unchanged. Apply the same evidence contract: successful run submission,
terminal status, complete retrieval, compatible criterion coverage, explicit
policy decision, and evidence artifact. Do not translate a YAML task name into
an acceptance guarantee.

## Secure and isolate the pipeline

Use workload federation for cloud CI where supported and configure the subject
for the actual workflow context: branch, PR, or protected environment. A
credential trusting `main` does not necessarily authorize a pull-request run.
Assign [workflow-specific permissions](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluation-permissions)
to the caller and project identity, including account scope for model inference
where required.

Untrusted PR code must not receive production credentials or sensitive acceptance
data. Keep fixture evaluation available without secrets. Run costly or privileged
cloud acceptance from an explicitly protected context.

## Promotion and rollback

Require a verified candidate version and tool configuration. Do not infer the
served version from an environment variable or use mixed canary output as if it
all came from the candidate. Prefer a separate evaluation target.

Persist decision, policy version, data/evaluator/judge lineage, and results before
promotion. Define who can grant a documented exception, its expiration, and
rollback triggers. Improving an average is not sufficient if a blocking outcome
or critical safety slice worsens.

Continue with [operations](../operations/operations.md).
