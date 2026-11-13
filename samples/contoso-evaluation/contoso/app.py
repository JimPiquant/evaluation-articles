import copy
import re

from .common import nonempty


CANDIDATE_VERSIONS = {
    "baseline": "contoso-support/1.0.0",
    "regressed": "contoso-support/1.1.0-regressed",
}


class FixtureTools:
    """Local function execution; state is isolated to one evaluation case."""

    def __init__(self, fixtures):
        self.fixtures = copy.deepcopy(fixtures)
        self.tickets = []

    def search_knowledge(self, query):
        if not nonempty(query):
            raise ValueError("query must be a nonempty string")
        tokens = set(re.findall(r"\w+", query.lower()))
        documents = [
            {key: doc[key] for key in ("id", "title", "text")}
            for doc in self.fixtures["knowledge"]
            if tokens.intersection(doc["keywords"])
        ]
        return {"code": "found" if documents else "not_found", "documents": documents}

    def lookup_order(self, order_id, customer_id):
        if not nonempty(order_id) or not nonempty(customer_id):
            raise ValueError("Order and authenticated customer IDs are required")
        order = self.fixtures["orders"].get(order_id)
        if order is None:
            return {"code": "not_found"}
        if order["customer_id"] != customer_id:
            return {"code": "access_denied"}
        return {
            "code": "found", "order_id": order_id,
            "status": order["status"], "tracking": order["tracking"],
        }

    def create_ticket(self, order_id, customer_id, issue, consent):
        if not nonempty(issue) or type(consent) is not bool:
            raise ValueError("A nonempty issue and explicit boolean consent are required")
        order = self.lookup_order(order_id, customer_id)
        if order["code"] != "found":
            return {"code": order["code"]}
        if not consent:
            return {"code": "consent_required"}
        ticket = {
            "ticket_id": "TKT-" + str(len(self.tickets) + 1).zfill(4),
            "order_id": order_id, "customer_id": customer_id,
            "issue": issue, "status": "open",
        }
        self.tickets.append(ticket)
        return {"code": "created", "ticket": copy.deepcopy(ticket)}

    def execute(self, name, arguments):
        functions = {
            "search_knowledge": self.search_knowledge,
            "lookup_order": self.lookup_order,
            "create_ticket": self.create_ticket,
        }
        if name not in functions:
            raise ValueError("Unknown tool: " + str(name))
        return functions[name](**arguments)


def context_from_trace(trace):
    context = []
    for index, call in enumerate(trace):
        if call["tool"] == "search_knowledge" and call["result"].get("documents"):
            context.extend(
                {"source": "knowledge", "id": doc["id"], "content": copy.deepcopy(doc)}
                for doc in call["result"]["documents"]
            )
        else:
            context.append({
                "source": call["tool"], "id": "tool-result-" + str(index + 1),
                "content": copy.deepcopy(call["result"]),
            })
    return context


def run_candidate(name, request, item_id, fixtures):
    version = CANDIDATE_VERSIONS[name]
    tools = FixtureTools(fixtures)
    trace = []

    def call(tool, arguments):
        result = tools.execute(tool, arguments)
        trace.append({
            "tool": tool, "arguments": copy.deepcopy(arguments),
            "result": copy.deepcopy(result), "status": "completed",
        })
        return result

    operation = request["operation"]
    parameters = request["parameters"]
    if operation == "knowledge":
        result = call("search_knowledge", parameters)
        if result["documents"]:
            document = result["documents"][0]
            response = document["text"] + " [" + document["id"] + "]"
            if name == "regressed":
                response = response.replace("30 days", "90 days")
            outcome = {"action": "knowledge", "code": "answered", "document_id": document["id"]}
        else:
            response = "I could not find a matching policy. Please contact support."
            outcome = {"action": "knowledge", "code": "not_found"}
    else:
        order_arguments = {key: parameters[key] for key in ("order_id", "customer_id")}
        order = call("lookup_order", order_arguments)
        action = "ticket" if operation == "ticket" else "order_status"
        if order["code"] != "found":
            outcome = {"action": action, "code": order["code"]}
            response = (
                "I cannot access that order for this customer."
                if order["code"] == "access_denied" else "That order was not found."
            )
        elif operation == "order":
            outcome = {"action": action, **order}
            if name == "regressed":
                outcome["status"] = "delivered"
            tracking = outcome["tracking"] or "not available"
            response = (
                "Order " + order["order_id"] + " is " + outcome["status"]
                + ". Tracking: " + tracking + "."
            )
        elif name == "regressed" and parameters["consent"]:
            # Deliberate bug: claim a side effect without executing the tool.
            outcome = {"action": "ticket", "code": "created", "ticket_id": "TKT-FAKE"}
            response = "I created ticket TKT-FAKE."
        else:
            ticket = call("create_ticket", parameters)
            outcome = {"action": "ticket", "code": ticket["code"]}
            if ticket["code"] == "created":
                outcome["ticket_id"] = ticket["ticket"]["ticket_id"]
                response = "I created ticket " + outcome["ticket_id"] + "."
            else:
                response = "I need your consent; no ticket was created."
    return {
        "item_id": item_id,
        "actual_version": version,
        "response": response,
        "context": context_from_trace(trace),
        "trace": trace,
        "outcome": outcome,
        "state": {"tickets": copy.deepcopy(tools.tickets)},
    }
