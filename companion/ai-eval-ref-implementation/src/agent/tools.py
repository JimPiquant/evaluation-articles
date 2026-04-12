"""
Contoso Support Agent — Tool Definitions

Defines the tools available to the customer support agent.
These are used both for agent creation and for evaluation
(tool_definitions field in evaluation datasets).
"""

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search the Contoso knowledge base for product information, policies, FAQs, and troubleshooting guides.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant knowledge base articles.",
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter (e.g., 'returns', 'billing', 'products', 'account').",
                        "enum": ["returns", "billing", "products", "account", "shipping", "general"],
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_order",
            "description": "Look up an order by order number or search for recent orders by customer identifier. Returns order status, items, shipping details, and payment information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_number": {
                        "type": "string",
                        "description": "The order number to look up (e.g., '#12345').",
                    },
                    "customer_email": {
                        "type": "string",
                        "description": "Customer email to search for recent orders. Used when order number is not available.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create a customer support ticket for issues that require human follow-up, such as returns, refunds, escalations, or complex account issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "Brief subject line for the support ticket.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue.",
                    },
                    "priority": {
                        "type": "string",
                        "description": "Ticket priority level.",
                        "enum": ["low", "medium", "high", "urgent"],
                    },
                    "category": {
                        "type": "string",
                        "description": "Ticket category.",
                        "enum": ["return", "refund", "billing", "escalation", "technical", "general"],
                    },
                },
                "required": ["subject", "description", "priority", "category"],
            },
        },
    },
]
