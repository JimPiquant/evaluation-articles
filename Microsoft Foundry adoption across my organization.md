# Microsoft Foundry adoption across my organization

Written by Alex Ruiz, Ayan Banerjee, Chris Tava

This guide presents options for planning
adoption of Microsoft Foundry across your organization. It is important to
think through how your organization plans to use Foundry and work backwards
from that desired outcome.

The focus of this article is to assist
customers in adopting Foundry for development purposes for the first time;
there is a separate article targeted at production rollouts for agents and
models created inside of Foundry.

## Prerequisites

Before you begin adoption planning, confirm
that you have:

- A target Azure
  subscription(s) and resource group(s) strategy for development and testing
  environments. This article does not cover production, which is tackled in its own
  separate article.
- Microsoft Entra ID groups
  (or equivalent identity groups) should be defined for administrators, project
  managers, and project users to ensure role-based access governance.
- Reviewed your data
  residency constraints and identified an initial region plan based on model and
  feature availability. Certain industries, such as healthcare or financial
  services, have strict compliance requirements for where data must reside and/or
  be processed. For details, see [feature
  availability across cloud regions](https://learn.microsoft.com/en-us/azure/foundry/reference/region-support), our [model
  deployment guide](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/deployment-types), and our [data
  processing & privacy article](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy?tabs=azure-portal).
- Reviewed your
  organization’s security requirements for private networking, encryption, cloud
  access, and data isolation. It is recommended that your security teams are a
  part of Foundry adoption planning efforts.
- Familiarized yourself with
  the concepts of the [agent
  development lifecycle](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/development-lifecycle) for Microsoft Foundry.

## How are customers adopting Foundry? What are they using it for?

Across our customers, when it comes to
artificial intelligence, we see two main adoptions across enterprises:
Generative AI software-as-a-service tools (i.e. CoPilot Studio) and
customizable, enterprise-wide, cloud-based AI platforms (i.e. Microsoft
Foundry).

Some customers want their users to create
and consume agents in an easy-to-use tool, and CoPilot Studio squarely fits
this need. Other customers lean more to the pro-code developer approach or have
compliance or security restrictions that require more control and
configurability over agentic development, and so they lean more on Microsoft
Foundry.

These camps tend to co-exist because
customers want to enable the full breadth of their employee talents and want to
make AI ubiquitous across their enterprise (we’ll double-click into the enterprise-wide
AI platform later in this article).

In development scenarios, we are seeing
Foundry primarily tackle 3 use cases:

1. **Development playground experiences:** first-time developers leverage the
   Playgrounds experience in Foundry to try out different models, prompts, and
   evaluations in the ideation phase of development.
2. **Model API Hosting:** seasoned developers feel more at home in their IDE of choice, and
   so platform administrators may provide policy-compliant model endpoints for
   developers to consume as they please.
3. **End-to-end AI pipelines:** developers may choose to build complete solutions with Foundry that
   take advantage of models, agents, evaluations tools, and content safety
   features.

The content of this article is geared
toward (1) & (2), with a more robust article around complete production
rollouts available elsewhere.

> **TIP:** We highly recommend familiarizing yourself with the [agent development lifecycle in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/development-lifecycle) *before* proceeding with the remainder of the article. Concepts from the lifecycle will be touched on towards the end of the article when we cover observability, governance, and monitoring.

## Microsoft Foundry adoption checklist

Many customers find it useful to have an
adoption checklist handy that outlines the important components of adopting a
new technology platform. We’ve provided an adoption checklist below for you to
use as a starting point:

| Done | Adoption item |
| --- | --- |
| ✓ | Define your environment boundaries across development, testing, and production. |
| ✓ | Identify or assign ownership for each Foundry resource and project scope. Leverage the approaches to organizing Foundry section of this article to determine how your organization will adopt Foundry. |
| ✓ | Identify any resource connection requirements for your Foundry projects. |
| ✓ | Define your network configuration for Foundry based on the three recommended patterns presented in this article. Leverage infrastructure-as-code templates wherever possible. |
| ✓ | Determine whether customer-managed keys are required by policy. This is an important consideration for highly regulated industries such as healthcare. |
| ✓ | Define a model deployment strategy to ensure model capacity and that your organization remains compliant with any data residency or processing requirements. |
| ✓ | Identify environment-wide policies that are required to apply to model and agent deployments – i.e. token-limit policies via APIM, Azure Policies restricting certain model usage, etc. |
| ✓ | Define role-based access control assignments for platform administrators, project managers, and project users. Root your assignments in the Microsoft best practice of least-privilege. |
| ✓ | Determine your cost management strategy for tracking costs associated with Foundry, such as model, agent, and tool calling, or associate resources. |
| ✓ | Enable monitoring capabilities to capture information related to your Foundry environment and the agents created there. |

We’ll start with the considerations to keep
in mind for organizing projects inside Microsoft Foundry.

## Project setup considerations for adopting Foundry

### What are Foundry Projects?

Microsoft Foundry uses a resource and
project distinction for resource organization – like a parent / child
relationship. Foundry projects are designed to represent specific use cases for
developers to work on. They’re containers to organize components such as agents
or files for an application. While they inherit security settings from their
parent resource, they can also implement their own access controls, resource
connections, and other governance controls.

You can have many Foundry projects within a
Foundry resource, as seen below:

![](microsoft-foundry-adoption-across-my-organization-assets/image001.png)

### Approaches to organizing Foundry

There are two perspectives to consider when
approaching Foundry adoption: the enterprise-wide perspective and the
department-level perspective.

#### The “Enterprise-Wide” Perspective

Many organizations gravitate towards
viewing Foundry as their next generation AI platform, and leaders will
naturally want to build a single, enterprise-wide AI platform around Foundry.

> **TIP:** It is crucial to view Foundry as a *development* platform, not a *consumption* platform. It is acceptable and, in some cases, encouraged to pursue an enterprise-wide AI platform, where many users can log on and consume models and agents from one secure application.

When tasked with an enterprise-wide
adoption of Foundry, you will want to urge decision makers towards segmenting
Foundry deployments across logical boundaries such as data domains or business
units to ensure developer autonomy. See an example below:

![](microsoft-foundry-adoption-across-my-organization-assets/image002.png)

To fulfill this “enterprise-wide” vision,
you will have:

- **Department-level development environments:** Many Foundry resources,
  each for your different departments to use for development purposes,
- **Source Control & DevOps:** a process by which to check-in and promote
  your agentic code, or deploy your created agents across your development, test,
  and production environments,
- **API Governance:** a governance layer using Azure API Management, where rate limiting
  and token limit policies are applied to your models and agents APIs to control
  usage and costs.
- **Consumption Platform:** an application layer where users can consume your agents or models
  – such as CoPilot Studio, or your own custom application where you expose
  deployed models and agents.

#### The “Department-level” Perspective

Let’s double click into the
department-level approach to organizing Foundry. We’ve seen that organizations
want to enable their departments or business groups to take advantage of
emerging AI technologies such as agents to deliver impact by solving real business
problems.

These developers need an environment where
they can test models, build agents, and implement evaluations – either
programmatically, or through a GUI – with a certain level of autonomy.
Developer teams may need to access sensitive, department-level data or track
costs specific to their budget; it is for this reason that we recommend
segmenting your Foundry resources across these department-level boundaries, as
seen below:

![](microsoft-foundry-adoption-across-my-organization-assets/image003.png)

In this approach, you’ll give developers or
developer teams their own projects inside of their respective Foundry resource
and leverage shared connected resources – like storage and search indexes –
across all those projects. This way, you’re keeping development scoped at the
department-level, while still consolidating costs and maintaining a degree of
collaboration.

> **TIP:** You may be asking, “How many model deployments should I have inside each Foundry resource?”, “Is it recommended that users share model deployments?”, or “Should I give each user their own model deployment?” The answer here is it depends on your cost management/tracking requirements.

#### Department-level Enclaves

We recognize that in some more restricted
industries, such as healthcare or financial services, there are stricter
requirements over the sensitivity and handling of data; these industries
require more segmentation and more granular control over Foundry, and so we
introduce the concept of the “department-level enclave”:

![](microsoft-foundry-adoption-across-my-organization-assets/image004.png)

Here, each project receives their own
respective resources, and users are *strictly* given role-based access to
only their project and its supporting resources.

There are trade-offs between compliance and
complexity with this approach. Yes, you are gaining segmentation of resources
and can govern sensitive use cases with the appropriate care; however, you are
increasing the complexity of your environment and costs. There are also
limitations with certain connections to resources, so be sure to review that [here](https://learn.microsoft.com/en-us/azure/foundry/how-to/connections-add?tabs=foundry-portal).

> **TIP:** When it comes to setting up an enclave, carefully consider each use case before you create a new project. Ask questions such as:
>
> - What kind of data will this project require?
> - Will de-identified data suffice? If not, does the data need to be stored separately?
> - Will indexed data need to be treated similarly?
> - Does this use case require robust logging and security of conversation threads?
>
> If yes, then you may benefit from the enclave scenario. You may find that some resources can be shared, while others may not.

A key piece of the department-level
approach is defining your organization’s model strategy. Certain models are
only available in certain regions and in certain deployment configurations,
which can impact where data is processed. It is important to understand model
availability as well as model deployment configurations and plan accordingly.
We will cover that later in this article.

## Securing your Foundry environment

There are 3 primary ways to configure
network security for your Foundry environment: *public*, *private*,
and *hybrid*. Below walks through each of these configurations and
provides rationale, as well as infrastructure-as-code templates you can use to
get started with your deployment.

> **NOTE:** All of these configurations are variations of the [Standard Agent Setup](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/standard-agent-setup). If you are looking for a quick, easy-to-deploy Foundry configuration where all underlying components are managed by Microsoft, please see the basic agent setup.

#### Deployment 1 – Standard Agent Setup (Public)

The public standard agent setup is the
recommended configuration for customers looking for a complete Foundry
deployment that includes all its ancillary Azure services but aren’t restricted
by a requirement to deploy an environment with private networking.

![](microsoft-foundry-adoption-across-my-organization-assets/image005.png)

With this deployment configuration, you’ll
get the following resources deployed into your resource group:

- **Microsoft Foundry account & project:** parent resource and one
  project in which to work in by default.
- **[Foundry project capability host](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/capability-hosts):**
  this sub-resource allows you to bring your own Azure resources and specifies
  resources for storing agent states such as conversation history, file uploads,
  and vector stores.
- **Azure Cosmos DB:** stores conversation history and threads.
- **Azure Storage:** stores data or files produced by your Agents, models, or Speech and
  Language services.
- **Azure AI Search:** stores embeddings and vector data.
- **Azure Key Vault:** stores encrypted keys that are used to connect across resources or
  APIs.

You can find an infrastructure-as-code
template for this deployment configuration here: [*foundry-samples/infrastructure/infrastructure-setup-bicep/41-standard-agent-setup
at main · microsoft-foundry/foundry-samples*](https://github.com/microsoft-foundry/foundry-samples/tree/main/infrastructure/infrastructure-setup-bicep/41-standard-agent-setup)

> **NOTE:** You have the option to point the template to existing resources or have the template create new ones. In either case, these dependencies are customer-managed resources, not Microsoft-managed resources (as is the case in the basic agent setup).

#### Deployment 2 – Standard Agent Setup (Private)

The private standard agent setup includes
everything that the public standard agent setup includes, however all the
resources are deployed in your own virtual network alongside private endpoints
for each of the respective Azure resources. For customers in regulated
industries such as healthcare or financial services, this is generally the
recommended approach for deploying Foundry. There’s a more detailed article
around setting up this environment found [here](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/virtual-networks).

> **NOTE:** There is also support for a variation of this deployment but with a Microsoft-managed VNET, you can read more about that [here](https://learn.microsoft.com/en-us/azure/foundry/how-to/managed-virtual-network).

![Diagram of the recommended network isolation for Foundry.](microsoft-foundry-adoption-across-my-organization-assets/image006.png)

An important callout for this private setup
is the introduction of the Agents subnet – also called the delegated subnet –
where your agents are deployed into. Although you may bring your own Azure
resources, deployed agents (also called prompt agents) always get deployed into
this subnet onto Microsoft-managed container applications where the agent
runtimes are hosted. Two key points:

- Those container
  applications exist inside of the delegated subnet and are not seen or managed
  by customers.
- Customers are not charged
  for those container applications but are charged for the calls made to agents
  that run on those containers.

You can find a deployment template for this
configuration here: [*foundry-samples/infrastructure/infrastructure-setup-bicep/15-private-network-standard-agent-setup
at main · microsoft-foundry/foundry-samples*](https://github.com/microsoft-foundry/foundry-samples/tree/main/infrastructure/infrastructure-setup-bicep/15-private-network-standard-agent-setup)

There is also a modified version of this
template that supports customer-managed keys.

> **NOTE:** As agentic platform capabilities continue to mature, we are seeing customers move towards including Azure API Management as a core component of their Foundry deployments to manage model and agent APIs via policies. While there is a [deployment template of this private standard agent setup that includes APIM](https://github.com/microsoft-foundry/foundry-samples/tree/main/infrastructure/infrastructure-setup-bicep/16-private-network-standard-agent-apim-setup-preview), there are efforts underway to integrate APIM and Foundry via the [AI Gateway feature](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/ai-gateway) (currently in public preview).

#### Deployment 3 – Standard Agent Setup (Hybrid)

Lastly, there is one more deployment
configuration for Foundry that is not often seen, but deserves mention: the
hybrid configuration. The key differentiator with this configuration is the
ability to switch between public and private Foundry access. Organizations will
want to use this deployment configuration when they want:

- **Private backend resources:** Keep Azure AI Search, Cosmos DB, and
  Azure Storage behind private endpoints.
- **MCP Server integration:** Deploy MCP servers on the VNET that agents can access via a data
  proxy.
- **Private Foundry:** Full network isolation with secure access via VPN, ExpressRoute, or
  Bastion.
- **Optional public Foundry access:** Switch to public access for portal-based
  development if allowed by your organization’s security policy.

Organizations will want to avoid this
configuration and defer to Deployment 2 – Standard Agent Setup (private) when
they need:

- **Fully managed private networking:** Including managed VNET with
  Microsoft-managed private endpoints.
- **Compliance requirements:** Regulations that require a different private networking topology.

Below is a table that compares private
deployment and hybrid deployments:

| Feature | Deployment 2 (Private) | Deployment 3 (Hybrid – “Private”) | Deployment 3 (Hybrid – “Public”) |
| --- | --- | --- | --- |
| AI Services public access | Disabled | Disabled | Enabled |
| Foundry Portal access | Via VPN, ExpressRoute, or Bastion | Via VPN, ExpressRoute, or Bastion | Works directly |
| Backend resources | Private | Private | Private |
| Data Proxy | Configured | Configured | Configured |
| Secure connection required | Yes | Yes | No |

You can find a deployment template for this
configuration here: [*foundry-samples/infrastructure/infrastructure-setup-bicep/19-hybrid-private-resources-agent-setup
at main · microsoft-foundry/foundry-samples*](https://github.com/microsoft-foundry/foundry-samples/tree/main/infrastructure/infrastructure-setup-bicep/19-hybrid-private-resources-agent-setup)

## Define your model strategy

In a constantly evolving space like AI, it
is important for an organization to define its model strategy. Model lifecycle
stages or regional capacity constraints can affect the models you choose to
integrate into your applications. A viable model strategy should address three
key areas:

1. **Model lifecycle:** models are continuously refreshed with newer, more capable models.
   As a part of this process, model providers may deprecate and retire older
   models, requiring application updates to use newer model SKUs. It is important
   to understand the model lifecycle stages, and how [Foundry
   models](https://learn.microsoft.com/en-us/azure/foundry/concepts/model-lifecycle-retirement) and [Azure
   Open AI models](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-retirements?tabs=text) are deprecated and retired.
2. **Deployment types:** There are different [deployment
   offerings](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/deployment-types), which impact where your prompt inputs are processed
   geographically. For customers in regulated industries, there may be a
   requirement for [data
   processing](https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy?tabs=azure-portal) to occur within a geographical region.
3. **Region availability:** Along the same lines as deployment types, it is important when
   selecting a model to verify which regions are supported for the model your team
   may be evaluating. Regional support can vary depending on available capacity,
   and not all models get rolled out to all regions.

## Planning your user access strategy for Foundry

_To be completed._

## Adopting a cost management strategy in Foundry

_To be completed._

## Governance & monitoring strategy in Foundry

While the scope of this guide is limited to
development workloads (and not production), we recognize the need for platform
governance and monitoring strategies in development environments. Platform
administrators may want to:

- Govern API endpoints for
  models or agents in development,
- Control access to certain
  models available in the Foundry catalog,
- Monitor usage or operations
  of agents deployed for testing in dev / test / UAT environments,
- Verify that logging
  configurations satisfy organizational requirements.

The list above may not be exhaustive but is
a well-rounded set of asks that we commonly see customers looking for guidance
around. We’ve gathered information around these four areas, which you can find
below.

#### Model & Agentic API Governance via an AI Gateway

_To be completed._

#### Control model access with Azure Policy

Certain organizations in more restricted
industries may seek to govern or restrict the deployment of specific models in
the Microsoft Foundry model catalog. Microsoft provides built-in Azure policies
for governing both [model
deployments](https://learn.microsoft.com/en-us/azure/foundry/how-to/model-deployment-policy?tabs=cli) as well as [Foundry
tools](https://learn.microsoft.com/en-us/azure/ai-services/policy-reference?context=/azure/foundry/context/context) to give customers control over which models and tools developers can
use.

> **NOTE:** These Azure Policies *do not* make any UI changes inside of the Microsoft Foundry portal; users will still be able to see model and tool cards in the catalog but will not be able to deploy them. Be sure to communicate to your users that you’ve put policies in place that restrict usage of certain models or tools!

#### Monitoring your deployed agents with Foundry’s observability suite

A large part of the agent development cycle
focuses on developing agent observability. Observability refers to the ability
to monitor, understand, and troubleshoot AI agents throughout their lifecycle.
There are three core capabilities that make up the Foundry observability suite:

1. **Evaluations:** [Evaluators](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent)
   measure the quality, safety, and reliability of agentic responses throughout
   development and into production. Different agents may use different evaluators
   depending on their specific purpose; however, some organizations may require a
   set of baseline evaluators across all agents – be sure to check with your AI
   platform or security administrator.
2. **Monitoring:** Microsoft Foundry provides [real-time
   dashboards](https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard?tabs=python) for tracking operational metrics, token consumption, latency,
   error rates, and quality scores. You can set up alerts when outputs fail
   quality thresholds or produce harmful content. We also provide a [fleet
   monitoring guide](https://learn.microsoft.com/en-us/azure/foundry/control-plane/monitoring-across-fleet) for platform administrators who are looking to monitor
   agents across many Foundry resources, as well as a guide for [performing
   lifecycle operations at scale](https://learn.microsoft.com/en-us/azure/foundry/control-plane/how-to-manage-agents).
3. **Tracing:** [Tracing](https://learn.microsoft.com/en-us/azure/foundry/observability/concepts/trace-agent-concept)
   offers insight into the execution flow of agentic systems, particularly into
   API calls, tool invocations, agentic decisions, and inter-service dependencies.
   It’s a key piece of troubleshooting or debugging your developers may need to do
   as they refine their agentic system.

Alongside enablement of these features
across all agent development efforts, it is important for developer teams to
understand and implement red teaming as a pre-requisite to shipping any agentic
system live into production. AI Red Teaming focuses on simulations or testing
by both human users and AI Red Teaming agents to uncover security
vulnerabilities or probe for novel risks in an agentic system.

> **TIP:** Microsoft has released a guide for developer teams to familiarize themselves not only with red teaming as a concept, but also how to implement red teaming using Microsoft Foundry’s [AI Red Teaming agent](https://learn.microsoft.com/en-us/azure/foundry/concepts/ai-red-teaming-agent).

#### AI Platform resource usage tracking with Azure Monitor & Log Analytics

Administrators want visibility into the
health and usage of Microsoft Foundry and other platform-level resources. You’ll
want to [configure
Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/fundamentals/data-sources) as the common monitoring data platform to monitor Azure
resources like Microsoft Foundry, log data from Microsoft Entra ID, and application
data – while routing [diagnostic
logs](https://learn.microsoft.com/en-us/azure/ai-services/diagnostic-logging?context=/azure/foundry/context/context) to be queried or consumed in Azure Log Analytics.
