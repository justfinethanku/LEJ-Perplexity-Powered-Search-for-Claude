# low effort (Ask)

**Light multi-step research with synthesized answers and citations. Use when one quick search won't cover the question.**

## When to Use

- Questions that need a few searches to answer well
- Current information spread across several sources
- Documentation questions where `fast` came back thin
- Everyday research questions

## Characteristics

| Attribute | Value |
|-----------|-------|
| Effort | `low` (replaces `sonar-reasoning-pro`) |
| Speed | ~1 minute |
| Cost | ~$0.01 |
| Output | Synthesized answer with `[web:n]` inline citations |

## How to Call

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY:-$(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY // empty' ~/.claude/settings.json)}" \
  -H "Content-Type: application/json" \
  -d '{"effort": "low", "input": "YOUR_QUESTION_HERE"}' \
  --max-time 300
```

## Response

Returns JSON with an `output` array:
- `message` item — `content[].text` is the synthesized answer with `[web:n]` citation markers
- `search_results` items (may be several) — `results[]` with `id`, `title`, `url`, `snippet`; `[web:n]` matches the result whose `id` is `n`
- `fetch_url_results` items — pages the agent read in full

## Best For

- "How do I..." questions with several moving parts
- API/framework questions spanning versions
- General research questions

## Prompting Tips

- Be specific about versions/dates when relevant
- Ask for "current" or "latest" to emphasize recency
- Frame as discovery: "What is..." not "Is it true that..."
