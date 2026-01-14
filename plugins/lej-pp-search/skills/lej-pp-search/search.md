# sonar (Search)

**Fast, cheap search for quick lookups. Use when you need basic facts fast.**

## When to Use

- Simple factual lookups
- Cost-conscious searches
- When you'll synthesize the results yourself
- Quick URL retrieval
- High-volume search tasks

## Characteristics

| Attribute | Value |
|-----------|-------|
| Model | `sonar` |
| Speed | Fast |
| Cost | ~$0.005 |
| Output | Answer with citations |

## How to Call

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar", "messages": [{"role": "user", "content": "YOUR_QUERY_HERE"}]}'
```

## Response

Returns JSON with:
- `choices[0].message.content` — The answer
- `citations` — Array of source URLs
- `search_results` — Array with titles, URLs, snippets

## Best For

- Quick fact checks
- Simple lookups
- Link collection
- Resource gathering
- Bulk searches where cost matters
