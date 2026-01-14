---
name: lej-pp-search
description: Perplexity-powered search for discovering current information. Use instead of built-in web search when you need up-to-date docs, recent changes, or information that may contradict training data.
allowed-tools: Read, Edit, Write, Bash
user-invocable: true
---

# LEJ PP Search

**Perplexity-Powered Search for Claude Code**

Use Perplexity for web research instead of built-in WebSearch. Perplexity searches to **discover** new information, not to confirm existing knowledge.

---

## How to Call Perplexity

All Perplexity calls use the same API endpoint with different models. The API key is stored in `~/.claude/settings.json` under `environmentVariables.PERPLEXITY_API_KEY`.

### Get the API Key

```bash
jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json
```

### Make the API Call

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "MODEL_NAME", "messages": [{"role": "user", "content": "YOUR_QUERY"}]}'
```

Replace `MODEL_NAME` with one of:
- `sonar` — Fast, cheap basic search
- `sonar-pro` — Better quality Q&A with citations
- `sonar-reasoning-pro` — Step-by-step logical analysis
- `sonar-deep-research` — Comprehensive research (slow, expensive)

---

## Model Selection

| Model | Use Case | Cost | Speed |
|-------|----------|------|-------|
| `sonar` | Quick lookups, basic facts | ~$0.005 | Fast |
| `sonar-pro` | Quality Q&A with citations | ~$0.008 | Fast |
| `sonar-reasoning-pro` | Complex analysis, comparisons | ~$0.01 | Moderate |
| `sonar-deep-research` | Comprehensive reports | ~$1+ | Slow (30s-5min) |

**Default to `sonar-pro`** for most searches. Only use `sonar-deep-research` when explicitly asked for deep/comprehensive research.

---

## Response Format

All responses include:

```json
{
  "choices": [{"message": {"content": "The answer with [1] inline citations"}}],
  "citations": ["https://source1.com", "https://source2.com"],
  "search_results": [{"title": "...", "url": "...", "snippet": "..."}]
}
```

**Always include citations in your response to the user.** Format them as markdown links.

---

## Example Calls

### Quick Q&A (sonar-pro)

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar-pro", "messages": [{"role": "user", "content": "What is the latest version of React?"}]}' | jq .
```

### Reasoning/Analysis (sonar-reasoning-pro)

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar-reasoning-pro", "messages": [{"role": "user", "content": "Compare Next.js and Remix for a new project"}]}' | jq .
```

### Deep Research (sonar-deep-research)

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar-deep-research", "messages": [{"role": "user", "content": "Comprehensive overview of WebAssembly adoption in 2025"}]}' --max-time 300 | jq .
```

**Note:** `sonar-deep-research` can take 30 seconds to 5 minutes. Use `--max-time 300` to allow for longer responses.

---

## Prompting Philosophy

Frame queries to **discover**, not **confirm**:

✅ "What is the current state of X?"
✅ "What has changed in X since [date]?"
✅ "What are the latest best practices for X?"

❌ "Is X still true?"
❌ "Confirm X works this way"
❌ "Verify that X is correct"

---

## Auto-Redirect Control

By default, WebSearch calls are automatically blocked and redirected to Perplexity.

### Disabling Auto-Redirect

When the user asks to "stop auto-redirecting", "let WebSearch through", "disable auto-redirect", or similar:

1. Read `~/.claude/settings.json`
2. Set `environmentVariables.LEJ_AUTO_REDIRECT` to `"false"`
3. Write the updated JSON back
4. Confirm: "Auto-redirect disabled. WebSearch works normally now."

### Re-enabling Auto-Redirect

When the user asks to "turn auto-redirect back on" or similar:

1. Read `~/.claude/settings.json`
2. Remove `LEJ_AUTO_REDIRECT` or set to `"true"`
3. Write the updated JSON back
4. Confirm: "Auto-redirect re-enabled."

---

## Uninstall Instructions

When the user asks to "uninstall completely":

1. Read `~/.claude/settings.json`
2. Remove `PERPLEXITY_API_KEY` from environmentVariables (preserve everything else)
3. Write the updated JSON back
4. Run `/plugin uninstall lej-pp-search`
5. Confirm: "LEJ PP Search fully removed."
