#!/bin/bash
# PostToolUse hook: ignore unrelated Bash calls before loading the renderer.
set -eo pipefail
INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
if [[ "$COMMAND" != *"api.perplexity.ai"* ]]; then
  exit 0
fi
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
printf '%s' "$INPUT" | python3 "$SCRIPT_DIR/research-receipt.py"
