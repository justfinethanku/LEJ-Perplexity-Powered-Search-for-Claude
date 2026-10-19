#!/bin/bash
# save-perplexity-result.sh
# PostToolUse hook that automatically saves Perplexity API responses
# Receives JSON via stdin with tool_input.command and tool_response

set -e

# Read stdin (hook input JSON)
INPUT=$(cat)

# Extract the command that was run
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

# Only process Perplexity API calls
if [[ "$COMMAND" != *"api.perplexity.ai"* ]]; then
  exit 0
fi

# Extract the tool response (curl output). Bash tool responses are objects with stdout.
TOOL_RESPONSE=$(echo "$INPUT" | jq -r '.tool_response | if type == "object" then .stdout else . end // empty' 2>/dev/null)

# Validate we got a response
if [[ -z "$TOOL_RESPONSE" ]] || [[ "$TOOL_RESPONSE" == "null" ]]; then
  exit 0
fi

# Try to parse as JSON to validate it's a Perplexity Agent API response
if ! echo "$TOOL_RESPONSE" | jq -e '.output[] | select(.type == "message")' >/dev/null 2>&1; then
  exit 0
fi

# Extract query from the curl command's -d parameter
# Use sed for macOS compatibility (no grep -P)
QUERY=$(echo "$COMMAND" | sed -n 's/.*"input"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | tail -1 2>/dev/null || echo "")

# If we couldn't extract from command, try from response
if [[ -z "$QUERY" ]]; then
  QUERY="perplexity-search"
fi

# Extract response fields
ANSWER=$(echo "$TOOL_RESPONSE" | jq -r '[.output[] | select(.type == "message") | .content[] | select(.type == "output_text") | .text] | join("\n\n") | if . == "" then "No content" else . end')
PRESET=$(echo "$COMMAND" | sed -n 's/.*"preset"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | tail -1 2>/dev/null || echo "")
MODEL=$(echo "$TOOL_RESPONSE" | jq -r '.model // "unknown"')
if [[ -n "$PRESET" ]]; then
  MODEL="${PRESET} preset (${MODEL})"
fi
COST=$(echo "$TOOL_RESPONSE" | jq -r '.usage.cost.total_cost // "unknown"' 2>/dev/null)

# Generate filename
TIMESTAMP=$(date +%Y-%m-%d-%H-%M-%S)
# Create slug from query (lowercase, spaces to dashes, remove special chars, limit length)
SLUG=$(echo "$QUERY" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-' | cut -c1-50)
FILENAME=".perplexity-research/${TIMESTAMP}-${SLUG}.md"

# Ensure directory exists
mkdir -p .perplexity-research

# Collect sources from every search_results item; each id matches an [n] marker in the answer
RESULTS=$(echo "$TOOL_RESPONSE" | jq -c '[.output[] | select(.type == "search_results") | .results[]]' 2>/dev/null || echo "[]")

# Build citations section using printf for proper newlines
CITATIONS_MD=""
CITATIONS=$(echo "$RESULTS" | jq -r '.[] | "\(.id // "-")\t\(.url // empty)"' 2>/dev/null || echo "")
if [[ -n "$CITATIONS" ]]; then
  while IFS=$'\t' read -r id url; do
    if [[ -n "$url" ]]; then
      CITATIONS_MD="${CITATIONS_MD}${id}. <${url}>"$'\n'
    fi
  done <<< "$CITATIONS"
fi

# Build search results section
SEARCH_RESULTS_MD=""
if [[ "$RESULTS" != "[]" ]] && [[ -n "$RESULTS" ]]; then
  while IFS= read -r result; do
    TITLE=$(echo "$result" | jq -r '.title // "Untitled"')
    URL=$(echo "$result" | jq -r '.url // "N/A"')
    SNIPPET=$(echo "$result" | jq -r '.snippet // "N/A"')
    SEARCH_RESULTS_MD="${SEARCH_RESULTS_MD}### ${TITLE}"$'\n'"**URL:** ${URL}"$'\n'"**Snippet:** ${SNIPPET}"$'\n\n'
  done <<< "$(echo "$RESULTS" | jq -c '.[]' 2>/dev/null)"
fi

# Write markdown file
cat > "$FILENAME" << MARKDOWN
# ${QUERY}

**Query:** ${QUERY}
**Model:** ${MODEL}
**Date:** $(date '+%Y-%m-%d %H:%M:%S')
**Cost:** \$${COST}

---

## Answer

${ANSWER}

---

## Citations

${CITATIONS_MD:-"No citations available."}

---

## Search Results

${SEARCH_RESULTS_MD:-"No search results available."}

---

*Saved automatically by LEJ PP Search*
MARKDOWN

# Output confirmation (will be shown in hook output)
echo "Research saved to ${FILENAME}" >&2

exit 0
