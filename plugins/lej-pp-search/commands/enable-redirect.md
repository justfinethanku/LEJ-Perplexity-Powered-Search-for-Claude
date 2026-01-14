---
description: "Enable automatic WebSearch to Perplexity redirect"
allowed-tools: ["Read", "Edit", "Write"]
---

# Enable Auto-Redirect

Re-enable the automatic interception of WebSearch calls. After this, WebSearch calls will be blocked and redirected to Perplexity tools.

## Instructions

1. Read the file `~/.claude/settings.json`
2. Parse the JSON content
3. If `environmentVariables.LEJ_AUTO_REDIRECT` exists, remove it (or set to `"true"`)
4. Write the updated JSON back to the file (preserve all other keys)
5. Confirm to the user: "Auto-redirect enabled. WebSearch calls will now be redirected to Perplexity. Run `/lej-pp-search:disable-redirect` to turn it off."

## Important

- If settings.json doesn't exist, no action needed (auto-redirect is enabled by default)
- Preserve all other keys in the JSON structure
- Removing the key entirely is preferred over setting to "true" (cleaner config)
