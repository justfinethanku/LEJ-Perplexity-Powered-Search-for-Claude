---
description: "Disable automatic WebSearch to Perplexity redirect"
allowed-tools: ["Read", "Edit", "Write"]
---

# Disable Auto-Redirect

Disable the automatic interception of WebSearch calls. After this, WebSearch will work normally and Perplexity tools remain available for explicit use.

## Instructions

1. Read the file `~/.claude/settings.json`
2. Parse the JSON content
3. Ensure `environmentVariables` object exists (create if needed)
4. Set `environmentVariables.LEJ_AUTO_REDIRECT` to `"false"`
5. Write the updated JSON back to the file (preserve all other keys)
6. Confirm to the user: "Auto-redirect disabled. WebSearch now works normally. You can still use Perplexity tools explicitly anytime. Run `/lej-pp-search:enable-redirect` to turn it back on."

## Important

- If settings.json doesn't exist, create it with just the environmentVariables section
- Preserve all other keys in the JSON structure
- The value must be the string `"false"`, not a boolean
