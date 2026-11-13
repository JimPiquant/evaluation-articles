#!/usr/bin/env python3
import argparse
from pathlib import Path

from contoso.common import REPORT_SCHEMA, read_json, write_json
from contoso.results import build_report


def main():
    parser = argparse.ArgumentParser(description="Run fixture-backed deterministic Contoso evaluations.")
    parser.add_argument("--candidate", required=True, help="Candidate name registered in policy.json.")
    parser.add_argument("--split", choices=("development", "regression", "holdout"), help="Defaults to the release split in policy.json.")
    parser.add_argument("--records", type=Path, help="Optional JSON array of externally collected fixture-scenario records.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.records and args.records.resolve() == args.output.resolve():
        parser.error("--records and --output must be different files")
    try:
        recordings = read_json(args.records) if args.records else None
        report = build_report(args.candidate, args.split, recordings)
        write_json(args.output, report)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        write_json(args.output, {"schema_version": REPORT_SCHEMA, "status": "error", "error": str(exc)})
        print("Evaluation error: " + str(exc))
        return 2
    print(str(args.output) + ": " + report["status"] + "; inspect items and summary")
    # A completed evaluation can contain failed checks. gate.py makes the release decision.
    return 0 if report["status"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
