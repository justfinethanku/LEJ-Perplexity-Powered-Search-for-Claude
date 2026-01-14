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

All Perplexity calls use the same API endpoint. The API key is stored in `~/.claude/settings.json` under `environmentVariables.PERPLEXITY_API_KEY`.

### Basic Call

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar-pro", "messages": [{"role": "user", "content": "YOUR_QUERY"}]}'
```

### Full Call with Parameters

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "MODEL_NAME",
    "messages": [{"role": "user", "content": "YOUR_QUERY"}],
    "web_search_options": {"search_context_size": "medium"},
    "search_recency_filter": "month"
  }'
```

---

## Model Selection

| Model | Use Case | Cost | Speed |
|-------|----------|------|-------|
| `sonar` | Quick lookups, basic facts | ~$0.005 | Fast |
| `sonar-pro` | Quality Q&A with citations (DEFAULT) | ~$0.008 | Fast |
| `sonar-reasoning-pro` | Complex analysis, comparisons | ~$0.01 | Moderate |
| `sonar-deep-research` | Comprehensive reports | ~$1+ | Slow (30s-5min) |

**Default to `sonar-pro`** for most searches. Only use `sonar-deep-research` when explicitly asked for deep/comprehensive research.

---

## Search Parameters

### search_context_size (via web_search_options)

Controls how many search results are included in the context. **Higher = more thorough but more expensive.**

| Value | Cost Impact | When to Use |
|-------|-------------|-------------|
| `"low"` | ~$0.006 | Quick facts, simple lookups, cost-conscious queries |
| `"medium"` | ~$0.010 | DEFAULT - balanced depth for most questions |
| `"high"` | ~$0.014 | Complex topics, comparisons, when thoroughness matters |

**Usage:**
```json
{"web_search_options": {"search_context_size": "high"}}
```

**Guidance:**
- Use `"low"` for simple factual queries ("What version is X?")
- Use `"medium"` (default) for general questions
- Use `"high"` for comparisons, analysis, or when user asks for "thorough" or "comprehensive" info

### search_recency_filter

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
{"search_recency_filter": "week"}
```

**Guidance:**
- Use `"day"` or `"week"` for news, current events, stock prices
- Use `"month"` for recent software releases, API changes
- Omit for stable topics (tutorials, concepts, documentation)

### return_images

Include images in the response. Use when visual content is relevant.

**Usage:**
```json
{"return_images": true}
```

**Guidance:**
- Use for queries about visual topics (UI, design, places, products)
- Skip for code, documentation, or text-focused queries

**Presenting images to users:**

When images are returned, present them as clickable markdown links:

```markdown
**Images:**
- [Golden Gate Bridge at sunset](https://media.istockphoto.com/...)
- [Aerial view of the bridge](https://media.istockphoto.com/...)
```

The response includes:
- `image_url` — Direct link to the image
- `origin_url` — Source page
- `title` — Description (use this as the link text)

Format: `[title](image_url)` — Makes them clickable in VSCode

### reasoning_effort (for sonar-reasoning-pro)

Controls reasoning depth. Only works with `sonar-reasoning-pro` model.

| Value | When to Use |
|-------|-------------|
| `"low"` | Simple comparisons, quick analysis |
| `"medium"` | DEFAULT - balanced reasoning |
| `"high"` | Complex multi-factor decisions, deep analysis |

**Usage:**
```json
{"model": "sonar-reasoning-pro", "reasoning_effort": "high"}
```

---

## Example Calls

### Quick lookup (low context)

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar-pro", "messages": [{"role": "user", "content": "What is the latest version of Node.js?"}], "web_search_options": {"search_context_size": "low"}}'
```

### Recent news (recency filter)

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar-pro", "messages": [{"role": "user", "content": "Latest AI news"}], "search_recency_filter": "day"}'
```

### Thorough comparison (high context + reasoning)

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar-reasoning-pro", "messages": [{"role": "user", "content": "Compare PostgreSQL vs MySQL for a new project"}], "web_search_options": {"search_context_size": "high"}, "reasoning_effort": "high"}'
```

### Deep research (comprehensive)

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar-deep-research", "messages": [{"role": "user", "content": "Comprehensive analysis of WebAssembly adoption"}]}' --max-time 300
```

---

## Response Format

All responses include:

```json
{
  "choices": [{"message": {"content": "The answer with [1] inline citations"}}],
  "citations": ["https://source1.com", "https://source2.com"],
  "search_results": [{"title": "...", "url": "...", "snippet": "..."}],
  "images": ["url1", "url2"],  // if return_images: true
  "usage": {"search_context_size": "medium", "cost": {"total_cost": 0.02}}
}
```

**Always include citations in your response to the user.** Format them as markdown links.

---

## Persisting Research Results

After every Perplexity search, save the results to a markdown file for future reference. This prevents research from being lost when conversation context is compacted.

### How to Save

1. Create `.perplexity-research/` in the current working directory if it doesn't exist
2. Generate filename: `YYYY-MM-DD-HH-MM-query-slug.md` (e.g., `2025-01-14-15-30-node-js-version.md`)
3. Write the markdown file with the format below

### Markdown Format

```markdown
# [Query Title]

**Query:** [The exact query sent to Perplexity]
**Model:** [sonar-pro | sonar-reasoning-pro | etc.]
**Date:** [YYYY-MM-DD HH:MM]
**Cost:** $[total_cost from response]

---

## Answer

[The full content from choices[0].message.content]

---

## Citations

1. [Title or URL](url)
2. [Title or URL](url)
...

---

## Search Results

### [Result 1 Title]
**URL:** [url]
**Snippet:** [snippet text]

### [Result 2 Title]
...
```

### Example Workflow

```bash
# 1. Run the search
RESULT=$(curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar-pro", "messages": [{"role": "user", "content": "What is the latest Node.js version?"}]}')

# 2. Create directory if needed
mkdir -p .perplexity-research

# 3. Save to file (Claude formats and writes the markdown)
```

After saving, tell the user: "Research saved to `.perplexity-research/[filename].md`"

---

## Parameter Selection Guide

**For simple questions:**
- Model: `sonar-pro`
- Context: `low`
- No recency filter

**For general research:**
- Model: `sonar-pro`
- Context: `medium` (default)
- Recency: based on topic freshness

**For comparisons/analysis:**
- Model: `sonar-reasoning-pro`
- Context: `high`
- Reasoning: `medium` or `high`

**For comprehensive reports:**
- Model: `sonar-deep-research`
- Context: (handled by model)
- Add `--max-time 300`

**For breaking news:**
- Model: `sonar-pro`
- Context: `medium`
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
