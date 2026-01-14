#!/bin/bash
# block-websearch.sh
# Intercepts WebSearch calls and redirects Claude to use Perplexity via curl
# Can be disabled by setting LEJ_AUTO_REDIRECT=false in ~/.claude/settings.json

SETTINGS_FILE="$HOME/.claude/settings.json"

# Check if auto-redirect is disabled
AUTO_REDIRECT=$(jq -r '.environmentVariables.LEJ_AUTO_REDIRECT // "true"' "$SETTINGS_FILE" 2>/dev/null)

if [[ "$AUTO_REDIRECT" == "false" ]]; then
  # Allow WebSearch to proceed normally
  cat << 'EOF'
{
  "hookSpecificOutput": {
    "permissionDecision": "allow",
    "permissionDecisionReason": "Auto-redirect disabled, using built-in WebSearch"
  }
}
EOF
  exit 0
fi

# Check if Perplexity API key is configured
API_KEY=$(jq -r '.environmentVariables.PERPLEXITY_API_KEY // empty' "$SETTINGS_FILE" 2>/dev/null)

if [[ -z "$API_KEY" ]]; then
  # No API key - block and ask user what they want to do
  cat << 'EOF' >&2
⚠️ Perplexity API key is not configured.

You MUST use AskUserQuestion to ask the user how they want to proceed. Present these options:

**Question:** "Perplexity API key not configured. How would you like to proceed?"
**Header:** "Search"

**Options:**
1. "Use WebSearch instead" - Description: "Fall back to standard web search for this session"
2. "Set up Perplexity API" - Description: "Configure your API key now (run /lej-pp-search:setup)"
3. "Get manual search prompt" - Description: "I'll format a query you can paste into perplexity.ai"

**Based on user choice:**
- If "Use WebSearch instead": Run /lej-pp-search:disable-redirect, then retry the original search using WebSearch
- If "Set up Perplexity API": Run /lej-pp-search:setup
- If "Get manual search prompt": Format the original search query nicely and tell the user to paste it at https://perplexity.ai, then paste the results back here
EOF
  exit 2
fi

# API key exists - block WebSearch and tell Claude to use curl
cat << 'EOF' >&2
WebSearch is blocked. Use Perplexity via curl instead.

**How to search:**

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar-pro", "messages": [{"role": "user", "content": "YOUR_QUERY_HERE"}]}'
```

**Model selection:**
- `sonar` — Fast, cheap (~$0.005)
- `sonar-pro` — Better quality, default choice (~$0.008)
- `sonar-reasoning-pro` — Complex analysis (~$0.01)
- `sonar-deep-research` — Comprehensive reports (~$1+, slow)

**Response format:** Extract `choices[0].message.content` for the answer and `citations` array for sources.

Perplexity searches to DISCOVER new information, not confirm existing knowledge.
EOF
exit 2
