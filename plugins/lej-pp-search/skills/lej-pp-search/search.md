# fast preset (Search)

**Fast, cheap search for quick lookups. Default choice for most searches.**

## When to Use

- Simple factual lookups
- Current information lookup
- Documentation queries
- Cost-conscious searches
- High-volume search tasks

## Characteristics

| Attribute | Value |
|-----------|-------|
| Preset | `fast` (replaces `sonar` and `sonar-pro`) |
| Speed | Fast (~5s) |
| Cost | ~$0.002 |
| Output | Answer with `[n]` inline citations |

## How to Call

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer $(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"preset": "fast", "input": "YOUR_QUERY_HERE"}'
```

## Response

Returns JSON with an `output` array:
- `message` item — `content[].text` is the answer with `[n]` citation markers
- `search_results` item — `results[]` with `id`, `title`, `url`, `snippet`; each `id` matches a marker

## Best For

- Quick fact checks
- "How do I..." and "What is the current..." questions
- Link collection
- Bulk searches where cost matters
