# perplexity_ask

**Quick Q&A with synthesized answers and citations. Uses sonar-pro model.**

## When to Use

- Direct questions needing authoritative answers
- Current information lookup
- Quick fact verification
- Documentation queries
- Default choice for most searches

## Characteristics

| Attribute | Value |
|-----------|-------|
| Model | sonar-pro |
| Speed | Moderate |
| Cost | Moderate |
| Output | Synthesized answer with inline citations |
| Citations | Array of source URLs |

## Example Usage

```json
{
  "messages": [
    {"role": "system", "content": "Provide current, accurate information with citations"},
    {"role": "user", "content": "What are the current best practices for React Server Components in Next.js 15?"}
  ]
}
```

## Response

Returns a synthesized answer that:
- Combines information from multiple sources
- Includes inline citation markers
- Provides source URLs in citations array
- Balances depth with conciseness

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
