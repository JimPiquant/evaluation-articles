from .common import ROOT, digest, nonempty, number, parse_json, read_json


CHECK_NAMES = {
    "tool_contract", "fixture_context", "expected_outcome",
    "response_assertions", "ticket_state",
}


def load_inputs(split=None):
    policy_path = ROOT / "policy.json"
    metadata_path = ROOT / "datasets/metadata.json"
    dataset_path = ROOT / "datasets/support.jsonl"
    fixture_path = ROOT / "fixtures/support.json"
    policy = read_json(policy_path)
    metadata = read_json(metadata_path)
    fixtures = read_json(fixture_path)
    if policy.get("schema_version") != "contoso.policy/1":
        raise ValueError("Unsupported policy")
    if set(policy.get("evaluators", {})) != CHECK_NAMES:
        raise ValueError("Policy must require every implemented evaluator")
    if not policy.get("candidates") or any(
        not nonempty(name) or not nonempty(version)
        for name, version in policy["candidates"].items()
    ):
        raise ValueError("Policy candidate versions must be explicit")
    if not number(policy.get("required_coverage")) or policy["required_coverage"] != 1.0:
        raise ValueError("This contract requires complete coverage")
    for criterion in policy["evaluators"].values():
        rate = criterion.get("min_pass_rate")
        if not number(rate) or not 0 <= rate <= 1:
            raise ValueError("Policy pass rates must be finite numbers in [0,1]")
    if metadata.get("schema_version") != "contoso.dataset/1":
        raise ValueError("Unsupported dataset metadata")
    for document in (policy, metadata):
        if not nonempty(document.get("id")) or not nonempty(document.get("version")):
            raise ValueError("Policy and dataset identity/version are required")
    splits = metadata.get("splits", {})
    if split is None:
        split = policy.get("release_split")
    if split not in splits or policy.get("release_split") not in splits:
        raise ValueError("Unknown split")
    all_ids = []
    for ids in splits.values():
        if not isinstance(ids, list) or not ids or any(not nonempty(i) for i in ids):
            raise ValueError("Every split must contain case IDs")
        all_ids.extend(ids)
    if len(all_ids) != len(set(all_ids)):
        raise ValueError("Dataset split IDs overlap or are duplicated")
    rows = []
    for line_number, line in enumerate(dataset_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            raise ValueError("Blank JSONL row at line " + str(line_number))
        row = parse_json(line)
        validate_case(row)
        if row["split"] not in splits or row["id"] not in splits[row["split"]]:
            raise ValueError("Case is not registered in its metadata split")
        rows.append(row)
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(all_ids):
        raise ValueError("Dataset IDs do not exactly match the manifest")
    by_id = {row["id"]: row for row in rows}
    selected = [by_id[item_id] for item_id in splits[split]]
    provenance = {
        "dataset": {
            "id": metadata["id"], "version": metadata["version"],
            "sha256": digest(dataset_path), "metadata_sha256": digest(metadata_path),
            "split": split, "item_ids": splits[split],
        },
        "fixtures": {"id": fixtures["id"], "sha256": digest(fixture_path)},
        "policy": {
            "id": policy["id"], "version": policy["version"], "sha256": digest(policy_path),
        },
    }
    return policy, selected, fixtures, provenance


def validate_case(row):
    if not isinstance(row, dict) or any(
        not nonempty(row.get(key)) for key in ("id", "split", "query")
    ):
        raise ValueError("Case requires id, split and query")
    if not isinstance(row.get("tags"), list) or not row["tags"]:
        raise ValueError("Case requires coverage tags")
    request = row.get("request", {})
    operation = request.get("operation")
    parameters = request.get("parameters")
    keys = {
        "knowledge": {"query"},
        "order": {"order_id", "customer_id"},
        "ticket": {"order_id", "customer_id", "issue", "consent"},
    }
    if operation not in keys or not isinstance(parameters, dict) or set(parameters) != keys[operation]:
        raise ValueError("Invalid structured request")
    for key, value in parameters.items():
        if (key == "consent" and type(value) is not bool) or (key != "consent" and not nonempty(value)):
            raise ValueError("Invalid request parameter: " + key)
    expected = row.get("expected", {})
    if not isinstance(expected.get("outcome"), dict) or not expected["outcome"]:
        raise ValueError("Case requires an independent expected outcome")
    if not isinstance(expected.get("tools"), list) or not expected["tools"]:
        raise ValueError("Case requires expected tool calls")
    for tool in expected["tools"]:
        if not nonempty(tool.get("tool")) or not isinstance(tool.get("arguments"), dict):
            raise ValueError("Invalid expected tool call")
    for key in ("document_ids", "response_contains", "response_excludes"):
        if not isinstance(expected.get(key), list) or any(not nonempty(v) for v in expected[key]):
            raise ValueError("Invalid case assertions: " + key)
    if not expected["response_contains"] or type(expected.get("ticket_count")) is not int or expected["ticket_count"] < 0:
        raise ValueError("Case requires response assertions and a ticket count")
