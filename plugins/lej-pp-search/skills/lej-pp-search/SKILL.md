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

All Perplexity calls use the Agent API endpoint (`/v1/agent`). Sonar Chat Completions (`/chat/completions` with `sonar-*` models) was retired on September 27, 2026 and now returns `403 agent_api_migration_required`.

The API key is `PERPLEXITY_API_KEY` in the environment, or in `~/.claude/settings.json` under `env` (then legacy `environmentVariables`). Do not print the key.

### Basic Call

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY:-$(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY // empty' ~/.claude/settings.json)}" \
  -H "Content-Type: application/json" \
  -d '{"effort": "fast", "input": "YOUR_QUERY"}'
```

### Full Call with Parameters

Search controls live on the `web_search` tool. Adding the tool keeps the effort level's other settings.

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY:-$(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY // empty' ~/.claude/settings.json)}" \
  -H "Content-Type: application/json" \
  -d '{
    "effort": "EFFORT",
    "input": "YOUR_QUERY",
    "tools": [{
      "type": "web_search",
      "max_results": 10,
      "filters": {"search_recency_filter": "month", "search_domain_filter": ["docs.example.com"]}
    }]
  }'
```

---

## Effort Selection

| Effort | Use Case | Cost (measured) | Speed (measured) |
|--------|----------|-----------------|------------------|
| `fast` | Quick lookups, everyday questions (DEFAULT) | ~$0.002 | ~5s |
| `low` | Light multi-step research, current info needing a few searches | ~$0.01 | ~1 min |
| `medium` | Multi-hop research across many sources, comparisons, tradeoffs | ~$0.02 | ~1 min |
| `high` | Exhaustive, expert-level deep research | Higher | Several minutes |
| `xhigh` | Open-ended agentic work (code sandbox, long tool loops) | Highest | Slowest |

**Default to `fast`** for most searches. Step up to `low` or `medium` when one search won't cover the question. Only use `high` or `xhigh` when explicitly asked for deep/comprehensive research.

Effort levels map from the old Sonar models: `sonar` and `sonar-pro` → `fast`, `sonar-reasoning-pro` → `low`, `sonar-deep-research` → `high`.

---

## Search Parameters

### search_recency_filter (in web_search filters)

Filters search results by time. Use when freshness matters.

| Value | When to Use |
|-------|-------------|
| `"day"` | Breaking news, today's events, live data |
| `"week"` | Recent updates, this week's news |
| `"month"` | Recent releases, monthly trends |
| `"year"` | Annual summaries, recent but not urgent |
| (omit) | All time - when recency doesn't matter |

**Usage:**
```json
{"tools": [{"type": "web_search", "filters": {"search_recency_filter": "week"}}]}
```

**Guidance:**
- Use `"day"` or `"week"` for news, current events, stock prices
- Use `"month"` for recent software releases, API changes
- Omit for stable topics (tutorials, concepts, documentation)

### search_domain_filter (in web_search filters)

Include or exclude up to 20 domains. Prefix with `-` to exclude. Use allowlist or denylist mode, not both.

```json
{"tools": [{"type": "web_search", "filters": {"search_domain_filter": ["-reddit.com", "-pinterest.com"]}}]}
```

### max_results and token budgets (on web_search)

Replace Sonar's `search_context_size`. `max_results` (1-50) caps the total results; `max_tokens` and `max_tokens_per_page` cap how much page content is pulled in.

| Goal | Setting |
|------|---------|
| Quick facts, cost-conscious | `"max_results": 5` |
| Balanced (default) | omit |
| Thorough coverage | `"max_results": 20` |

### Images (image_search tool)

Replaces Sonar's `return_images`. Add the `image_search` tool when visual content is relevant:

```json
{"tools": [{"type": "image_search", "max_results": 5}]}
```

Results come back as an `image_search_results` item in `output`, each with `image_url`, `origin_url`, and optional `title`.

**Presenting images to users:** Use the image title as the link label and the returned `image_url` as its target:

```markdown
**Images:**
- [Golden Gate Bridge at sunset](https://media.istockphoto.com/...)
- [Aerial view of the bridge](https://media.istockphoto.com/...)
```

### Long-running effort levels

`high` and `xhigh` can take several minutes. Add `--max-time 600` to curl and set the Bash tool `timeout` to `600000`; the Bash tool's own default limit is 2 minutes.

---

## Example Calls

### Quick lookup

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY:-$(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY // empty' ~/.claude/settings.json)}" \
  -H "Content-Type: application/json" \
  -d '{"effort": "fast", "input": "What is the latest version of Node.js?", "tools": [{"type": "web_search", "max_results": 5}]}'
```

### Recent news (recency filter)

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY:-$(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY // empty' ~/.claude/settings.json)}" \
  -H "Content-Type: application/json" \
  -d '{"effort": "fast", "input": "Latest AI news", "tools": [{"type": "web_search", "filters": {"search_recency_filter": "day"}}]}'
```

### Thorough comparison

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY:-$(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY // empty' ~/.claude/settings.json)}" \
  -H "Content-Type: application/json" \
  -d '{"effort": "medium", "input": "Compare PostgreSQL vs MySQL for a new project"}' --max-time 300
```

### Deep research (comprehensive)

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY:-$(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY // empty' ~/.claude/settings.json)}" \
  -H "Content-Type: application/json" \
  -d '{"effort": "high", "input": "Comprehensive analysis of WebAssembly adoption"}' --max-time 600
```

---

## Response Format

Responses contain a typed `output` array, one item per step the agent took:

```json
{
  "status": "completed",
  "model": "openai/...",
  "output": [
    {"type": "search_results", "results": [{"id": 1, "title": "...", "url": "...", "snippet": "...", "date": "..."}]},
    {"type": "fetch_url_results", "...": "..."},
    {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "The answer with [1] inline citations"}]}
  ],
  "usage": {"cost": {"total_cost": 0.002}}
}
```

- **Answer:** `content[].text` of the `message` item
- **Sources:** `results[]` of every `search_results` item (there can be several). Each result's `id` matches a citation marker: `[n]` from `fast`, `[web:n]` from `low` and above
- **Cost:** `usage.cost.total_cost`
- Check `status` is `"completed"` and `error` is null

To pull pieces out of a response you already have, run jq in a **separate** command on saved JSON, never piped from the curl call (the hook would not see the response):

```bash
jq -r '.output[] | select(.type == "message") | .content[] | select(.type == "output_text") | .text'
jq -r '.output[] | select(.type == "search_results") | .results[] | "[\(.id)] \(.title) - \(.url)"'
```

**Always include citations in your response to the user.** Format them as markdown links.

---

## Persisting Research Results

The `PostToolUse` hook saves recognized Perplexity responses automatically. Let
that hook own persistence rather than creating a second Markdown copy manually.
Its writer creates `.perplexity-research/` on the first saved result, gives each
file a unique name, and keeps new files private to your user.

Run curl so it prints the raw JSON; piping it through `jq` in the same command
hides the response from the hook. Reference the saved file when reusing research. Check that it exists before
telling the user where it was saved. If the hook did not save the response, the
API answer is still available in the tool output. For manual recovery, format
the query, answer, and sources as Markdown and pass it on stdin to the plugin's
[`scripts/write-research.py`](../../scripts/write-research.py) with a filename
prefix as its only argument (1–100 letters, digits, or dashes). Run it from the
project directory. The writer reports the saved path on stderr; report a failure
if it cannot save the file.

---

## Parameter Selection Guide

**For simple questions:**
- Effort: `fast`
- `max_results`: 5
- No recency filter

**For general research:**
- Effort: `fast`, or `low` if it needs several searches
- Recency: based on topic freshness

**For comparisons/analysis:**
- Effort: `medium`
- Add `--max-time 300`

**For comprehensive reports:**
- Effort: `high`
- Add `--max-time 600`

**For breaking news:**
- Effort: `fast`
- Recency: `day` or `week`

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
2. Set `env.LEJ_AUTO_REDIRECT` and `environmentVariables.LEJ_AUTO_REDIRECT` to `"false"`
3. Write the updated JSON back
4. Confirm: "Auto-redirect disabled. WebSearch works normally now."

### Re-enabling Auto-Redirect

When the user asks to "turn auto-redirect back on" or similar:

1. Read `~/.claude/settings.json`
2. Remove `LEJ_AUTO_REDIRECT` from both `env` and `environmentVariables`, or set each to `"true"`
3. Write the updated JSON back
4. Confirm: "Auto-redirect re-enabled."

---

## Uninstall Instructions

Follow the [README uninstall procedure](../../../../README.md#uninstall). Use
Claude Code's plugin manager for the installed scope and verify the resulting
plugin list. Do not edit registry JSON or remove cache directories by hand.
The README also covers optional marketplace removal and private API-key cleanup.
Project research files remain in place; uninstalling does not revoke a remote key.
