# sonar-pro (Ask)

**Quick Q&A with synthesized answers and citations. Default choice for most searches.**

## When to Use

- Direct questions needing authoritative answers
- Current information lookup
- Quick fact verification
- Documentation queries
- Default choice for most searches

## Characteristics

| Attribute | Value |
|-----------|-------|
| Model | `sonar-pro` |
| Speed | Fast |
| Cost | ~$0.008 |
| Output | Synthesized answer with inline citations |

## How to Call

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar-pro", "messages": [{"role": "user", "content": "YOUR_QUESTION_HERE"}]}'
```

## Response

Returns JSON with:
- `choices[0].message.content` — The synthesized answer with [1] inline citation markers
- `citations` — Array of source URLs
- `search_results` — Array of search results with titles, URLs, snippets

## Best For

- "How do I..." questions
- "What is the current..." queries
- Documentation lookups
- API/framework questions
- General research questions

## Prompting Tips

- Be specific about versions/dates when relevant
- Ask for "current" or "latest" to emphasize recency
- Frame as discovery: "What is..." not "Is it true that..."
