# perplexity_search

**Fast, lightweight search returning raw URLs and snippets.**

## When to Use

- You need actual URLs to reference or share
- Quick lookup of multiple sources
- Building a list of resources
- Cost-conscious searches
- When you'll synthesize the results yourself

## Characteristics

| Attribute | Value |
|-----------|-------|
| Speed | Fast |
| Cost | Low |
| Output | Raw URLs, titles, snippets |
| Citations | URLs in results |

## Example Usage

```json
{
  "messages": [
    {"role": "system", "content": "Return recent, authoritative sources"},
    {"role": "user", "content": "Claude Code plugin development documentation 2024-2025"}
  ]
}
```

## Response

Returns search results with:
- Page titles
- URLs
- Snippet previews
- No synthesis (raw results)

## Best For

- Link collection
- Source gathering
- Quick fact-checking URLs
- Resource lists for users
