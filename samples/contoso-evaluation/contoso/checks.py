from .app import FixtureTools, context_from_trace
from .common import nonempty


def validate_record(record, item_id):
    if not isinstance(record, dict) or record.get("item_id") != item_id:
        raise ValueError("Missing or wrong recording item ID")
    if not nonempty(record.get("actual_version")):
        raise ValueError("Missing observed actual_version; expected version is never a fallback")
    if not nonempty(record.get("response")):
        raise ValueError("Missing response")
    for field in ("trace", "context"):
        if not isinstance(record.get(field), list) or not record[field]:
            raise ValueError("Missing " + field)
    if not isinstance(record.get("outcome"), dict) or not record["outcome"]:
        raise ValueError("Missing structured outcome")
    if not isinstance(record.get("state"), dict) or not isinstance(record["state"].get("tickets"), list):
        raise ValueError("Missing observed ticket state")
    for call in record["trace"]:
        if (
            not isinstance(call, dict) or not nonempty(call.get("tool"))
            or not isinstance(call.get("arguments"), dict)
            or not isinstance(call.get("result"), dict)
            or call.get("status") != "completed" or call.get("error")
        ):
            raise ValueError("Tool traces must include completed calls and their results")


def evaluate_record(record, case, fixtures):
    validate_record(record, case["id"])
    expected = case["expected"]
    replay = FixtureTools(fixtures)
    tool_errors = []
    for call in record["trace"]:
        try:
            result = replay.execute(call["tool"], call["arguments"])
            if result != call["result"]:
                tool_errors.append("Tool result differs from authoritative fixture execution")
        except (ValueError, TypeError, KeyError) as exc:
            tool_errors.append(str(exc))
    plan = [{"tool": call["tool"], "arguments": call["arguments"]} for call in record["trace"]]
    if plan != expected["tools"]:
        tool_errors.append("Tool sequence or arguments differ from the expected contract")
    document_ids = [
        doc["id"] for call in record["trace"] if call["tool"] == "search_knowledge"
        for doc in call["result"].get("documents", [])
    ]
    context_ok = (
        not tool_errors
        and record["context"] == context_from_trace(record["trace"])
        and document_ids == expected["document_ids"]
    )
    response = record["response"].casefold()
    missing = [text for text in expected["response_contains"] if text.casefold() not in response]
    forbidden = [text for text in expected["response_excludes"] if text.casefold() in response]
    tickets = record["state"]["tickets"]
    ticket_ok = tickets == replay.tickets and len(tickets) == expected["ticket_count"]
    if expected["outcome"].get("code") == "created":
        ticket_ok = ticket_ok and any(
            ticket.get("ticket_id") == record["outcome"].get("ticket_id") for ticket in tickets
        )
    decisions = {
        "tool_contract": (not tool_errors, "; ".join(tool_errors) or "Executed tools match fixtures and expected calls"),
        "fixture_context": (context_ok, "Retrieved/tool context must match fixture outputs and expected document IDs"),
        "expected_outcome": (record["outcome"] == expected["outcome"], "Structured outcome must equal the independent expected outcome"),
        "response_assertions": (not missing and not forbidden, "Missing phrases: " + repr(missing) + "; forbidden phrases: " + repr(forbidden)),
        "ticket_state": (ticket_ok, "Observed tickets must match executed side effects, expected count and claimed ticket ID"),
    }
    return {
        name: {
            "status": "completed", "score": 1.0 if passed else 0.0,
            "passed": bool(passed), "reason": reason,
        }
        for name, (passed, reason) in decisions.items()
    }
