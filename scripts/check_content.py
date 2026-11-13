#!/usr/bin/env python3
"""Validate maintained Markdown and the publication catalog without network access."""

import argparse
import sys
from pathlib import Path

from content import ContentError, validate


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="Repository root (also useful for isolated test fixtures)")
    args = parser.parse_args(argv)
    try:
        catalog, _, errors = validate(args.root)
    except ContentError as exc:
        errors = [str(exc)]
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Content checks passed: {len(catalog['articles'])} catalog entries; "
          "local paths/anchors and external URL syntax checked (no network requests).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
