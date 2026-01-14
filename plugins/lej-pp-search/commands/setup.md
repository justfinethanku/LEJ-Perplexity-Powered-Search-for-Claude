---
description: "Set up Perplexity API key for LEJ PP Search"
allowed-tools: ["Read", "Edit", "Write", "AskUserQuestion"]
---

# Setup LEJ PP Search

Help the user configure their Perplexity API key.

## Step 1: Check Current Status

First, read `~/.claude/settings.json` to check if `PERPLEXITY_API_KEY` is already set in `environmentVariables`.

If already set, ask the user if they want to update it.

## Step 2: Get API Key

Use AskUserQuestion to ask:

**Question:** "Enter your Perplexity API key"

**Header:** "API Key"

**Options:**
- "I need to get one first" (description: "Opens https://www.perplexity.ai/account/api/group")
- "I have my key ready" (description: "You'll paste it in the next step")

If they select "I need to get one first", tell them to visit https://www.perplexity.ai/account/api/group and run `/lej-pp-search:setup` again when ready.

If they select "I have my key ready" or provide a custom response with their key:
- If they typed their key directly, use that
- Otherwise, ask them to paste the key

## Step 3: Save API Key

1. Read `~/.claude/settings.json` (create if doesn't exist)
2. Parse the JSON
3. Ensure `environmentVariables` object exists
4. Set `environmentVariables.PERPLEXITY_API_KEY` to the provided key
5. Write the updated JSON back (preserve all other keys)

## Step 4: Confirm

Tell the user:

"API key saved! LEJ PP Search is ready to use.

The plugin will automatically redirect WebSearch to Perplexity. Just search normally and you'll get Perplexity-powered results.

Run `/lej-pp-search:help` for more info on available tools and commands."

## Important Safety Rules

- Never log or display the API key after receiving it
- Preserve all other keys in settings.json
- If settings.json doesn't exist, create it with proper structure
- Validate the key looks like an API key (starts with "pplx-" typically) but don't reject if it doesn't - just proceed
