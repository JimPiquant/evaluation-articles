# Project scope: Foundry evaluation learning series

## Purpose

Help customers create, manage, use, and optimize evaluations for AI applications
in Microsoft Foundry. Teach decisions and repeatable workflows, not a duplicate
of the evaluator reference catalog. The customer journey is choose -> create ->
run -> interpret -> manage -> optimize.

The authoritative inventory is [series.json](series.json). The customer entry
point and reader paths are in [README.md](README.md). All current articles are
fresh drafts with adjacent plans and curated slide narratives; drafting and local
checks do not establish external publication or live-cloud validation.

## Grounding

The [Foundry Evaluation overview](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-overview)
and linked Evaluation section are the primary authority. Official Foundry
Agents/Projects SDK references and versioned samples additionally ground
implementation. The [source policy](references/grounding.md) defines how to
resolve API generations, feature status, and conflicting documentation.

CAF, the Azure Well-Architected Framework (WAF), and Azure Architecture Center
are potential publication destinations and architectural context, not claimed
publication venues. Publication URLs remain empty until confirmed.

## Content boundaries

E00-E10 form the core lifecycle. E11 covers safety; E12 covers adversarial
testing; E13 integrates the architecture. P01-P03 cover agent deployment,
identity/networking, and tool delivery only insofar as they support evaluation.

The Contoso Support scenario joins knowledge retrieval, customer-authorized
order lookup, and confirmed ticket creation. The executable companion is an
offline fixture harness plus an optional cloud integration, not a production
support application. It must not claim that fixture checks establish model
quality, groundedness, safety, or Azure deployment readiness.

Dev/test/prod are cross-cutting operating contexts, not primary navigation.
Recorded outputs do not require deploying an agent. Full agent platforms and
landing zones are optional application architecture, not dataset-evaluation
prerequisites.

## Deliverables and acceptance

Maintain article Markdown, reviewed plan, and curated slide Markdown together.
Generate Word and PowerPoint using the catalog and shared templates. Releases
include source/tool provenance and checksums; failures block publishing.
Generated binaries and their provenance are versioned snapshots under `build/`,
not independently maintained content masters. Preserve exact artifacts because
byte-identical rebuilds are not guaranteed. Refresh related metadata,
distributable archives, and previews when intentionally replacing an output.

An authored bundle remains `draft` until domain review, appropriate sample
execution, and visual Office review. Cloud recipes require live validation in an
authorized environment before claiming that validation. Publication status is
separate from editorial readiness.

## Preserved material

The previous numbered series, deployment guides, research, original images,
companion, and Office documents are in [archive/](archive/README.md). They are
superseded references, excluded from the current catalog and checks. The
[migration map](references/migration.md) records replacement locations.

## Out of scope

Production support-agent implementation, automatic Azure provisioning, legal
compliance certification, guaranteed safety, a CMS, and model/evaluator SDK
development. Foundry IQ and unrelated platform expansions are not in this
evaluation curriculum.


