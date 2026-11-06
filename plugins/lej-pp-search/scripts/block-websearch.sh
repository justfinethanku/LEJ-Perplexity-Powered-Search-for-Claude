#!/bin/bash
# block-websearch.sh
# Intercepts WebSearch calls and redirects Claude to use Perplexity via curl.
# Disable by setting LEJ_AUTO_REDIRECT=false in the environment or in
# ~/.claude/settings.json (env, then legacy environmentVariables).
#
# A key counts as configured when PERPLEXITY_API_KEY is nonempty in the
# environment, or in settings under env or legacy environmentVariables.
# The key value is never written to stdout or stderr. Redirect text is a
# quoted heredoc so $API_KEY / $PERPLEXITY_API_KEY cannot expand here.
# PreToolUse exit 2 feeds stderr back to Claude.

SETTINGS_FILE="$HOME/.claude/settings.json"

# Check if auto-redirect is disabled. Prefer the process environment
# (subagents), then settings env, then legacy environmentVariables.
AUTO_REDIRECT="${LEJ_AUTO_REDIRECT:-}"
if [[ -z "$AUTO_REDIRECT" ]]; then
  AUTO_REDIRECT=$(jq -r '.env.LEJ_AUTO_REDIRECT // .environmentVariables.LEJ_AUTO_REDIRECT // "true"' "$SETTINGS_FILE" 2>/dev/null) || AUTO_REDIRECT="true"
fi

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

# Presence only. jq prints "yes" or "no" so the secret never lands in a variable.
key_configured=no
if [[ -n "${PERPLEXITY_API_KEY:-}" ]]; then
  key_configured=yes
else
  key_configured=$(jq -r 'if ((.env.PERPLEXITY_API_KEY // "") | length) > 0 then "yes" elif ((.environmentVariables.PERPLEXITY_API_KEY // "") | length) > 0 then "yes" else "no" end' "$SETTINGS_FILE" 2>/dev/null) || key_configured=no
fi

if [[ "$key_configured" != "yes" ]]; then
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

# API key exists - block WebSearch and tell Claude to use curl.
# Keep this heredoc quoted. An unquoted delimiter would expand the key into stderr.
cat << 'EOF' >&2
WebSearch is blocked. Use Perplexity via curl instead.

**How to search:**

Do not print the API key. The command below reads PERPLEXITY_API_KEY from the environment when it is set, otherwise from ~/.claude/settings.json (`env`, then legacy `environmentVariables`).

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY:-$(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY // empty' ~/.claude/settings.json)}" \
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
