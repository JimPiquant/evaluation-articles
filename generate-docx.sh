#!/usr/bin/env bash
#
# generate-docx.sh — Convert Markdown articles to Word (.docx) files.
#
# Usage:
#   ./generate-docx.sh           # Convert all articles
#   ./generate-docx.sh 01 02     # Convert only matching folders (by prefix)
#
# Requires: pandoc, mmdc (@mermaid-js/mermaid-cli)
# Output:   docx/<article-name>.docx  (with Mermaid diagrams rendered as PNG)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTDIR="$SCRIPT_DIR/docx"
LUA_FILTER="$SCRIPT_DIR/mermaid.lua"

# Articles to convert: space-separated "folder:markdown" pairs
ARTICLES=(
  "00-strategy-guide-caf:ai-eval-strategy-guide.md"
  "01-pipeline-overview:ai-eval-pipeline-overview.md"
  "02-ref-architecture:ai-eval-ref-architecture.md"
  "07-deploy-foundry-agents:foundry-agents-deployment.md"
  "07-deploy-foundry-agents:hosted-agents-developer-guide.md"
)

# Check dependencies
for cmd in pandoc mmdc; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "Error: $cmd is required but not installed." >&2
    exit 1
  fi
done

mkdir -p "$OUTDIR"

# Filter entries if arguments provided
if [[ $# -gt 0 ]]; then
  filtered=()
  for entry in "${ARTICLES[@]}"; do
    folder="${entry%%:*}"
    for prefix in "$@"; do
      if [[ "$folder" == "$prefix"* ]]; then
        filtered+=("$entry")
        break
      fi
    done
  done
  ARTICLES=("${filtered[@]}")
fi

converted=0
failed=0

for entry in "${ARTICLES[@]}"; do
  folder="${entry%%:*}"
  mdfile="${entry#*:}"
  src="$SCRIPT_DIR/$folder/$mdfile"
  docxname="${mdfile%.md}.docx"
  dest="$OUTDIR/$docxname"
  imgdir="$OUTDIR/img"

  if [[ ! -f "$src" ]]; then
    echo "⚠  Skipping $folder — $mdfile not found"
    continue
  fi

  echo -n "📄 $folder/$mdfile → docx/$docxname ... "

  # Run pandoc from the output directory so the Lua filter writes images there
  if (cd "$OUTDIR" && pandoc "$src" \
      --from=markdown \
      --to=docx \
      --lua-filter="$LUA_FILTER" \
      --resource-path="$SCRIPT_DIR/$folder" \
      --standalone \
      -o "$docxname" 2>&1); then
    echo "✅"
    ((converted++))
  else
    echo "❌"
    ((failed++))
  fi
done

echo ""
echo "Done: $converted converted, $failed failed"
echo "Output: $OUTDIR/"
