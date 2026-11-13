#!/usr/bin/env bash
# Compatibility entry point: the catalog is the only list of publication inputs.
# Usage: ./generate-docx.sh [--article E02] [--output build]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/scripts/publish.py" "$@" --format docx
