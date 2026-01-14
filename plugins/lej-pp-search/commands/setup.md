---
description: "Set up Perplexity API key for LEJ PP Search"
allowed-tools: ["Read", "Edit", "Write", "AskUserQuestion", "Bash"]
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

## Step 3: Verify API Key

Before saving, verify the key works by making a test API call:

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer THE_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar", "messages": [{"role": "user", "content": "Say hi"}], "max_tokens": 5}'
```

**Check the response:**
- If response contains `"choices"` and `"id"` → Key is valid, proceed to Step 4
- If response contains `401` or `Unauthorized` → Key is invalid, inform user and ask if they want to try again
- If response contains other errors → Show error to user and ask if they want to try again

**On invalid key:**
Tell the user: "That API key didn't work (got authentication error). Please check that you copied the full key. Would you like to try again?"

Use AskUserQuestion with options:
- "Try again" - Go back to Step 2
- "Cancel setup" - Exit setup

## Step 4: Save API Key

Only save after verification succeeds:

1. Read `~/.claude/settings.json` (create if doesn't exist)
2. Parse the JSON
3. Ensure `environmentVariables` object exists
4. Set `environmentVariables.PERPLEXITY_API_KEY` to the verified key
5. Write the updated JSON back (preserve all other keys)

## Step 5: Confirm

Tell the user:

"✓ API key verified and saved! LEJ PP Search is ready to use.

The plugin will automatically redirect WebSearch to Perplexity. Just search normally and you'll get Perplexity-powered results.

**Note:** You may need to start a new session for the MCP server to pick up the new key.

Run `/lej-pp-search:help` for more info on available tools and commands."

## Important Safety Rules

- Never log or display the API key after receiving it
- Preserve all other keys in settings.json
- If settings.json doesn't exist, create it with proper structure
- The verification call uses minimal tokens (max_tokens: 5) to minimize cost
