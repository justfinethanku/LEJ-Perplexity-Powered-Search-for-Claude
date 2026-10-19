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

The API key is stored in `~/.claude/settings.json` under `env.PERPLEXITY_API_KEY` (older installs used `environmentVariables.PERPLEXITY_API_KEY`; the commands below read either).

### Basic Call

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer $(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"preset": "fast", "input": "YOUR_QUERY"}'
```

### Full Call with Parameters

Search controls live on the `web_search` tool. Adding the tool keeps the preset's other settings.

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer $(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{
    "preset": "PRESET_NAME",
    "input": "YOUR_QUERY",
    "tools": [{
      "type": "web_search",
      "max_results": 10,
      "filters": {"search_recency_filter": "month", "search_domain_filter": ["docs.example.com"]}
    }]
  }'
```

---

## Preset Selection

| Preset | Use Case | Cost (measured) | Speed (measured) |
|--------|----------|-----------------|------------------|
| `fast` | Quick lookups, everyday questions (DEFAULT) | ~$0.002 | ~5s |
| `low` | Light multi-step research, current info needing a few searches | ~$0.01 | ~1 min |
| `medium` | Multi-hop research across many sources, comparisons, tradeoffs | ~$0.02 | ~1 min |
| `high` | Exhaustive, expert-level deep research | Higher | Several minutes |
| `xhigh` | Open-ended agentic work (code sandbox, long tool loops) | Highest | Slowest |

**Default to `fast`** for most searches. Step up to `low` or `medium` when one search won't cover the question. Only use `high` or `xhigh` when explicitly asked for deep/comprehensive research.

Presets map from the old Sonar models: `sonar` and `sonar-pro` → `fast`, `sonar-reasoning-pro` → `low`, `sonar-deep-research` → `high`.

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

Replace Sonar's `search_context_size`. `max_results` (1-50) caps results per search call; `max_tokens` and `max_tokens_per_page` cap how much page content is pulled in.

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

**Presenting images to users:** Format as clickable markdown links, `[title](image_url)`:

```markdown
**Images:**
- [Golden Gate Bridge at sunset](https://media.istockphoto.com/...)
- [Aerial view of the bridge](https://media.istockphoto.com/...)
```

### Long-running presets

`high` and `xhigh` can take several minutes. Add `--max-time 600` to curl.

---

## Example Calls

### Quick lookup

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer $(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"preset": "fast", "input": "What is the latest version of Node.js?", "tools": [{"type": "web_search", "max_results": 5}]}'
```

### Recent news (recency filter)

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer $(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"preset": "fast", "input": "Latest AI news", "tools": [{"type": "web_search", "filters": {"search_recency_filter": "day"}}]}'
```

### Thorough comparison

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer $(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"preset": "medium", "input": "Compare PostgreSQL vs MySQL for a new project"}' --max-time 300
```

### Deep research (comprehensive)

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer $(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"preset": "high", "input": "Comprehensive analysis of WebAssembly adoption"}' --max-time 600
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

Useful jq filters:

```bash
jq -r '.output[] | select(.type == "message") | .content[] | select(.type == "output_text") | .text'
jq -r '.output[] | select(.type == "search_results") | .results[] | "[\(.id)] \(.title) - \(.url)"'
```

**Always include citations in your response to the user.** Format them as markdown links.

---

## Persisting Research Results

A PostToolUse hook automatically saves every Perplexity response to `.perplexity-research/` in the current working directory. For the hook to see the response, run curl so it prints the raw JSON (don't pipe it through jq in the same command). Read the saved file or re-run jq on it if you need the answer text.

After the hook saves, tell the user: "Research saved to `.perplexity-research/[filename].md`"

If the hook didn't fire, save it yourself in this format:

```markdown
# [Query Title]

**Query:** [The exact query sent to Perplexity]
**Model:** [preset and model from response]
**Date:** [YYYY-MM-DD HH:MM]
**Cost:** $[usage.cost.total_cost]

---

## Answer

[The message item's text]

---

## Citations

1. [Title or URL](url)
...

---

## Search Results

### [Result 1 Title]
**URL:** [url]
**Snippet:** [snippet text]
...
```

---

## Parameter Selection Guide

**For simple questions:**
- Preset: `fast`
- `max_results`: 5
- No recency filter

**For general research:**
- Preset: `fast`, or `low` if it needs several searches
- Recency: based on topic freshness

**For comparisons/analysis:**
- Preset: `medium`
- Add `--max-time 300`

**For comprehensive reports:**
- Preset: `high`
- Add `--max-time 600`

**For breaking news:**
- Preset: `fast`
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
2. Set `env.LEJ_AUTO_REDIRECT` to `"false"`
3. Write the updated JSON back
4. Confirm: "Auto-redirect disabled. WebSearch works normally now."

### Re-enabling Auto-Redirect

When the user asks to "turn auto-redirect back on" or similar:

1. Read `~/.claude/settings.json`
2. Remove `LEJ_AUTO_REDIRECT` from both `env` and `environmentVariables` (or set to `"true"`)
3. Write the updated JSON back
4. Confirm: "Auto-redirect re-enabled."

---

## Uninstall Instructions

When the user asks to "uninstall completely", run this bash script:

```bash
# Full uninstall of lej-pp-search
rm -rf ~/.claude/plugins/cache/lej-marketplace/lej-pp-search
rm -rf ~/.claude/plugins/marketplaces/lej-marketplace
jq 'del(."lej-marketplace")' ~/.claude/plugins/known_marketplaces.json > /tmp/known_marketplaces.json && mv /tmp/known_marketplaces.json ~/.claude/plugins/known_marketplaces.json
jq 'del(.plugins["lej-pp-search@lej-marketplace"])' ~/.claude/plugins/installed_plugins.json > /tmp/installed_plugins.json && mv /tmp/installed_plugins.json ~/.claude/plugins/installed_plugins.json
echo "LEJ PP Search fully removed."
```

Optionally also remove the API key from settings:
```bash
jq 'del(.env.PERPLEXITY_API_KEY, .environmentVariables.PERPLEXITY_API_KEY)' ~/.claude/settings.json > /tmp/settings.json && mv /tmp/settings.json ~/.claude/settings.json
```

Confirm: "LEJ PP Search fully removed. Restart Claude Code to complete."
