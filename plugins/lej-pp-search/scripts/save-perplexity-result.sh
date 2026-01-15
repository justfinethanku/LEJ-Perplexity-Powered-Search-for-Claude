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

# Extract the tool response (curl output)
TOOL_RESPONSE=$(echo "$INPUT" | jq -r '.tool_response // empty' 2>/dev/null)

# Validate we got a response
if [[ -z "$TOOL_RESPONSE" ]] || [[ "$TOOL_RESPONSE" == "null" ]]; then
  exit 0
fi

# Try to parse as JSON to validate it's a Perplexity response
if ! echo "$TOOL_RESPONSE" | jq -e '.choices[0].message.content' >/dev/null 2>&1; then
  exit 0
fi

# Extract query from the curl command's -d parameter
# Use sed for macOS compatibility (no grep -P)
QUERY=$(echo "$COMMAND" | sed -n 's/.*"content"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | tail -1 2>/dev/null || echo "")

# If we couldn't extract from command, try from response
if [[ -z "$QUERY" ]]; then
  QUERY="perplexity-search"
fi

# Extract response fields
ANSWER=$(echo "$TOOL_RESPONSE" | jq -r '.choices[0].message.content // "No content"')
MODEL=$(echo "$TOOL_RESPONSE" | jq -r '.model // "unknown"')
COST=$(echo "$TOOL_RESPONSE" | jq -r '.usage.cost.total_cost // "unknown"' 2>/dev/null)

# Generate filename
TIMESTAMP=$(date +%Y-%m-%d-%H-%M-%S)
# Create slug from query (lowercase, spaces to dashes, remove special chars, limit length)
SLUG=$(echo "$QUERY" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-' | cut -c1-50)
FILENAME=".perplexity-research/${TIMESTAMP}-${SLUG}.md"

# Ensure directory exists
mkdir -p .perplexity-research

# Build citations section using printf for proper newlines
CITATIONS_MD=""
CITATIONS=$(echo "$TOOL_RESPONSE" | jq -r '.citations // [] | .[]' 2>/dev/null || echo "")
if [[ -n "$CITATIONS" ]]; then
  COUNTER=1
  while IFS= read -r url; do
    if [[ -n "$url" ]]; then
      CITATIONS_MD="${CITATIONS_MD}${COUNTER}. <${url}>"$'\n'
      ((COUNTER++))
    fi
  done <<< "$CITATIONS"
fi

# Build search results section
SEARCH_RESULTS_MD=""
SEARCH_RESULTS=$(echo "$TOOL_RESPONSE" | jq -r '.search_results // []' 2>/dev/null)
if [[ "$SEARCH_RESULTS" != "[]" ]] && [[ "$SEARCH_RESULTS" != "null" ]] && [[ -n "$SEARCH_RESULTS" ]]; then
  while IFS= read -r result; do
    TITLE=$(echo "$result" | jq -r '.title // "Untitled"')
    URL=$(echo "$result" | jq -r '.url // "N/A"')
    SNIPPET=$(echo "$result" | jq -r '.snippet // "N/A"')
    SEARCH_RESULTS_MD="${SEARCH_RESULTS_MD}### ${TITLE}"$'\n'"**URL:** ${URL}"$'\n'"**Snippet:** ${SNIPPET}"$'\n\n'
  done <<< "$(echo "$SEARCH_RESULTS" | jq -c '.[]' 2>/dev/null)"
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
