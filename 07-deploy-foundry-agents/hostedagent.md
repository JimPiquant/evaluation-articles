# 🔎 1. Platform Overview & Value

**Q: What is the goal of Hosted Agents in Foundry?**

*   Provide a **managed agent hosting platform (PaaS-like)** so customers don’t need to build infrastructure themselves.
*   Focus areas:
    *   Integration with enterprise systems (via Toolbox, Logic Apps)
    *   Governance and identity (Entra-based agent identity)
    *   Observability (Application Insights + OpenTelemetry)

**Key takeaway:**  
👉 Hosted Agents = “agent platform abstraction” (compute + governance + integration out of the box).

# ⚙️ 2. Architecture & Runtime

## Core runtime model

**Q: How does Hosted Agents runtime actually work?**

*   Developer provides **container image**
*   Foundry:
    *   Pulls image
    *   Creates **micro-VM snapshot**
    *   Spins session in **<1 second startup**
*   Each request is routed into the agent endpoint (`/responses` or `/invocations`)

**Q: Is this SaaS, PaaS, or IaaS?**

*   It behaves **like PaaS**
    *   Compute fully managed by Microsoft
    *   No direct control of underlying infrastructure

## Isolation & execution

**Q: How isolated are agents?**

*   Each conversation/session:
    *   Runs in its **own micro-VM**
    *   Fully isolated compute (no sharing)

**Q: Can I run code interpreter or other compute?**

*   Code interpreter runs **separately (managed environment)**
*   OR you can run code inside the **same micro-VM session**

## Persistence model

**Q: Is state preserved?**

*   Yes:
    *   Each session has:
        *   **Persistent storage (“$HOME”)**
        *   File store (`/files`)
    *   Compute can shut down, but state persists

# 🔐 3. Identity, Governance & Security

**Q: How is identity handled?**

*   Every agent gets an **automatic Entra agent identity**
*   Enables:
    *   RBAC
    *   Auditing
    *   Policy enforcement across M365

**Q: How is governance applied?**

*   Integrated across:
    *   Foundry
    *   M365
    *   Defender / Purview ecosystem

**Q: Is it a “black box”?**

*   Partially:
    *   Compute is abstracted
    *   BUT:
        *   Logs, telemetry, and evaluation are **fully visible and controllable**

# 🌐 4. Networking & Enterprise Constraints

## Private networking

**Q: Does Hosted Agents support private networking / VNet?**

*   Yes:
    *   Same approach as prompt agents:
        *   Managed network OR BYO VNet
*   Uses **same VNet/subnet model as existing Foundry setups**

**Known gaps**

*   Documentation clarity still evolving
*   Details like:
    *   subnet sizing
    *   IP consumption
    *   detailed architecture diagrams  
        ➡️ Not fully answered in meeting

## ACR & private connectivity

**Q: Private ACR support?**

*   Not fully available at time of meeting
*   Expected **within \~1–2 weeks**
*   Also exploring:
    *   Upload code directly (no ACR dependency)

## CI/CD in private networks

**Q: How to deploy in locked-down environments?**

*   Similar to other PaaS:
    *   Use **self-hosted runners inside VNet**
    *   Then deploy via SDK/API

# ⚡ 5. Scaling, Performance & Cost Model

**Q: How does scaling work?**

*   Managed automatically by platform
*   Key model:
    *   **1 session = 1 isolated runtime**
    *   Scale based on concurrent sessions

**Q: Do I pay when idle?**

*   No:
    *   After \~15 mins idle → compute stops
    *   Storage persists

**Q: Can customers control scaling?**

*   Limited:
    *   No direct scaling knobs like App Service autoscale
    *   You define compute size per session
*   Actual concurrency handled by platform

**Q: SLA / HA / DR?**

*   Not clearly defined in preview
*   Acknowledged gap in meeting (needs follow-up)

# 🧠 6. Agent Capabilities & Framework Flexibility

## Framework flexibility

**Q: Do I have to use Agent Framework?**

*   No:
    *   Supported:
        *   Agent Framework ✅ (recommended)
        *   LangGraph ✅
        *   CrewAI ✅
        *   Custom code ✅

## Tools & integrations

**Q: How do agents call enterprise systems?**

*   Via:
    *   Toolbox
    *   Logic Apps connectors
    *   Custom code

## Continuous evaluation

**Q: Is evaluation built in?**

*   Yes:
    *   Integrated with input/output capture
    *   Connected to evaluation pipelines

## Autonomous agents

**Q: Are long-running or event-driven agents supported?**

*   Yes:
    *   Timers and triggers being introduced
    *   Persistent sessions enable long-running workflows

# 🔁 7. Prompt Agents vs Hosted Agents

**Q: When should I use Hosted vs Prompt Agents?**

*   Guidance emerging:
    *   **Prompt Agents**
        *   Simpler, low-code
    *   **Hosted Agents**
        *   Pro-code
        *   Full flexibility
*   Direction:
    *   Hosted Agents likely **strategic long-term platform**

# 🧩 8. State, Conversations & Publishing

**Q: Are conversations stateful?**

*   Yes:
    *   Foundry stores conversation history
*   Added:
    *   **isolation key (per user/session)**
*   Prevents data leakage across users

**Q: What happens after publishing?**

*   Should retain stateful behaviour
*   Docs temporarily inconsistent → acknowledged

# 🛠️ 9. Dev Experience & Tooling

## Local development

**Q: Can I develop locally?**

*   Yes:
    *   Full local runtime with:
        *   VS Code
        *   Foundry extension
        *   Debugging via HTTP endpoint

## Deployment

**Q: How do I deploy agents?**

*   Options:
    *   AZD (Azure Developer CLI)
    *   VS Code extension
*   Infra auto-generated:
    *   Bicep
    *   App Insights
    *   CI/CD scaffolding

# 🔄 10. Advanced Scenarios

## Durable orchestration

**Q: Can I build durable multi-agent workflows?**

*   Not native out-of-the-box
*   Approach:
    *   Use **Agent Framework + Durable Functions**
    *   Bring your own state store

## Custom metadata in conversations

**Q: Can I add metadata (e.g., user ID, product)?**

*   Possibly:
    *   Needs custom implementation
    *   Platform is flexible enough
*   Suggested: follow up with product team

# ⚠️ 11. Key Gaps / Open Questions from the Session

These came up repeatedly with no definitive answer:

*   Subnet sizing & IP consumption
*   SLA / availability / failover
*   Scaling limits (max sessions, concurrency)
*   Enterprise networking UX visibility
*   Clear architecture diagrams
*   Terraform / IaC-first workflows
*   Private networking documentation maturity

# ✅ TL;DR (Field-ready positioning)

**When to pitch Hosted Agents:**

*   Customers want:
    *   Fast time to production
    *   Built-in governance & identity
    *   Enterprise integration (M365, Logic Apps)
    *   Managed scaling

**When NOT ideal (yet):**

*   Strict control over:
    *   Networking topology
    *   Compute / infra
    *   HA/DR guarantees
*   Deep AKS/IaaS governance requirements


