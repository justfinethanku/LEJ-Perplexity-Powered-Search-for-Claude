---
name: lej-pp-search
description: Perplexity-powered search for discovering current information. Use instead of built-in web search when you need up-to-date docs, recent changes, or information that may contradict training data.
allowed-tools: Read, Edit, Write, mcp__perplexity__perplexity_search, mcp__perplexity__perplexity_ask, mcp__perplexity__perplexity_research, mcp__perplexity__perplexity_reason
user-invocable: true
---

# LEJ PP Search

**Perplexity-Powered Search for Claude Code**

Use Perplexity tools for web research instead of built-in WebSearch. Perplexity searches to **discover** new information, not to confirm existing knowledge.

---

## Overview

**LEJ PP Search** (Perplexity-Powered Search for Claude Code) by [Limited Edition Jonathan](https://substack.com/@limitededitionjonathan).

**What this plugin does:**
- WebSearch is automatically redirected to Perplexity, which searches to *discover* new information rather than confirm what I already think I know

**Four tools at your disposal:**
- `perplexity_search` — Fast URL/link retrieval
- `perplexity_ask` — Quick Q&A with citations
- `perplexity_research` — Deep dives and comprehensive analysis
- `perplexity_reason` — Step-by-step logical breakdowns

**Options:**
- Don't want auto-redirect? Just say "don't automatically use Perplexity" and I'll turn it off
- To uninstall completely (including your API key), say "uninstall lej-pp-search completely"

---

## Why Perplexity?

LLMs (including Claude) have confirmation bias when searching—looking for evidence to support existing beliefs from training data. Perplexity is architecturally different: it searches first, then synthesizes, making it better for:

- Up-to-date documentation
- Recent changes to APIs, frameworks, tools
- Information that contradicts outdated training data
- Current best practices

## Tool Selection

```
Need raw URLs/links?      → perplexity_search (fast, cheap)
Quick question?           → perplexity_ask (sonar-pro)
Deep research/reports?    → perplexity_research (slow, expensive, 2× citations)
Logical problem/analysis? → perplexity_reason (shows thinking process)
```

### Quick Reference

| Tool | Speed | Cost | Best For |
|------|-------|------|----------|
| `perplexity_search` | Fast | Low | Raw URLs, titles, snippets |
| `perplexity_ask` | Moderate | Moderate | Synthesized answers + citations |
| `perplexity_research` | Slow (30s-5min) | High | Deep analysis, comprehensive reports |
| `perplexity_reason` | Moderate | Moderate | Step-by-step logical analysis |

## Prompting Philosophy

Frame queries to **discover**, not **confirm**:

✅ "What is the current state of X?"
✅ "What has changed in X since [date]?"
✅ "What are the latest best practices for X?"

❌ "Is X still true?"
❌ "Confirm X works this way"
❌ "Verify that X is correct"

## Tool Details

For detailed usage of each tool:
- [search.md](search.md) - perplexity_search
- [ask.md](ask.md) - perplexity_ask
- [research.md](research.md) - perplexity_research
- [reason.md](reason.md) - perplexity_reason

## Message Format

All tools use the same parameter schema:

```json
{
  "messages": [
    {"role": "system", "content": "Context or instructions"},
    {"role": "user", "content": "Your query"}
  ]
}
```

## Response Format

All tools return:

```json
{
  "id": "response-id",
  "model": "model-name",
  "choices": [{
    "message": {"role": "assistant", "content": "Response with inline citations"}
  }],
  "usage": {"prompt_tokens": 25, "completion_tokens": 347, "total_tokens": 372},
  "citations": ["url1", "url2", "..."]
}
```

---

## Auto-Redirect Control

By default, WebSearch calls are automatically blocked and redirected to Perplexity. Users can toggle this behavior.

### Disabling Auto-Redirect

When the user asks to "stop auto-redirecting", "let WebSearch through", "disable auto-redirect", "don't automatically use Perplexity", or similar:

1. Read the file `~/.claude/settings.json`
2. Parse the JSON content
3. Set `environmentVariables.LEJ_AUTO_REDIRECT` to `"false"`
4. Write the updated JSON back to the file
5. Confirm: "Auto-redirect disabled. WebSearch works normally now. You can still use Perplexity tools explicitly anytime."

### Re-enabling Auto-Redirect

When the user asks to "turn auto-redirect back on", "block WebSearch again", "re-enable Perplexity redirect", "use Perplexity automatically", or similar:

1. Read the file `~/.claude/settings.json`
2. Parse the JSON content
3. Remove `LEJ_AUTO_REDIRECT` from environmentVariables (or set to `"true"`)
4. Write the updated JSON back to the file
5. Confirm: "Auto-redirect re-enabled. WebSearch calls will be redirected to Perplexity."

### Important Safety Rules

- Preserve all other keys in the JSON structure
- If settings.json doesn't exist, create it with just the environmentVariables section
- If environmentVariables doesn't exist, create it

---

## Uninstall Instructions

When the user asks to "uninstall completely", "fully remove", or "clean uninstall" this plugin:

### Step 1: Remove API Key

1. Read the file `~/.claude/settings.json`
2. Parse the JSON content
3. If `environmentVariables.PERPLEXITY_API_KEY` exists, remove ONLY that key
4. Do NOT remove any other keys in environmentVariables
5. Write the updated JSON back to the file
6. Confirm: "Removed PERPLEXITY_API_KEY from settings"

### Step 2: Uninstall Plugin

Run the command: `/plugin uninstall lej-pp-search`

### Step 3: Confirm

Tell the user: "LEJ PP Search has been fully removed, including your API key. To reinstall later, run `/plugin install lej-pp-search` (the marketplace is already configured)."

### Important Safety Rules

- ONLY remove `PERPLEXITY_API_KEY` - never touch other environment variables
- If the key doesn't exist, skip step 1 and proceed to uninstall
- If settings.json doesn't exist, skip step 1 and proceed to uninstall
- Always preserve the rest of the JSON structure
