#!/usr/bin/env python3
import argparse
import json

from contoso.common import read_json
from contoso.gating import validate_report


def main():
    parser = argparse.ArgumentParser(description="Fail-closed release gate for offline Contoso evidence.")
    parser.add_argument("report")
    parser.add_argument("--expected-candidate", help="Optionally bind the gate to the intended registered candidate.")
    args = parser.parse_args()
    try:
        failures = validate_report(read_json(args.report), args.expected_candidate)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"decision": "fail", "failures": [str(exc)]}))
        return 2
    print(json.dumps({"decision": "fail" if failures else "pass", "failures": failures}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
