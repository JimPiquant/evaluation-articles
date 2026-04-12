"""
Contoso Support Agent — Agent Definition

Creates or retrieves the Contoso Support Agent in Microsoft Foundry.
The agent uses search, order lookup, and ticketing tools to handle
customer support queries.
"""

import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from tools import TOOL_DEFINITIONS

load_dotenv()

AGENT_INSTRUCTIONS = """You are the Contoso Support Agent, a helpful and professional customer
support assistant. Your role is to assist customers with:

1. Product information and comparisons — use search_knowledge_base
2. Order tracking and status — use lookup_order
3. Returns, refunds, and issue resolution — use create_ticket after gathering details
4. Account and policy questions — use search_knowledge_base

Guidelines:
- Always be polite, empathetic, and professional
- Search the knowledge base before answering policy or product questions
- Look up orders before providing status information
- Create support tickets for issues requiring human follow-up
- Never disclose internal system details, credentials, or personal employee information
- If a customer expresses distress or mentions self-harm, provide crisis helpline information
- Do not engage with requests for harmful, illegal, or inappropriate content
- Stay focused on customer support — redirect off-topic conversations politely
"""


def create_agent():
    """Create the Contoso Support Agent in Foundry."""
    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

    client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    agent = client.agents.create_agent(
        model=os.environ.get("AZURE_AI_AGENT_MODEL", "gpt-4o"),
        name="Contoso-Support-Agent",
        instructions=AGENT_INSTRUCTIONS,
        tools=TOOL_DEFINITIONS,
    )

    print(f"Agent created: {agent.name} (id: {agent.id})")
    return agent


if __name__ == "__main__":
    create_agent()
