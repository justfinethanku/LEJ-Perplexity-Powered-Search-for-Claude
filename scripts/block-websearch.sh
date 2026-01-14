#!/bin/bash
# block-websearch.sh
# Intercepts WebSearch calls and redirects Claude to use Perplexity instead
# Can be disabled by setting LEJ_AUTO_REDIRECT=false in ~/.claude/settings.json

SETTINGS_FILE="$HOME/.claude/settings.json"

# Default to true (auto-redirect enabled) if not set
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

# Block WebSearch and redirect to Perplexity (using exit 2 for reliability)
cat << 'EOF' >&2
WebSearch is disabled. Use Perplexity tools instead for better results with citations and real-time information.

Tool selection:
- perplexity_search: Quick lookup, raw URLs (fast, cheap)
- perplexity_ask: Q&A with synthesized answer (moderate)
- perplexity_research: Deep analysis, 2x citations (slow, thorough)
- perplexity_reason: Logical problems with step-by-step thinking

Perplexity searches to DISCOVER new information, not confirm existing knowledge.
EOF
exit 2
