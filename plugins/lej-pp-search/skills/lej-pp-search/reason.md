# medium effort (Reason)

**Multi-hop research that chains evidence across many sources. Use for complex comparisons and tradeoff analysis.**

## When to Use

- Problems requiring step-by-step reasoning
- Debugging complex issues
- Architecture decisions with tradeoffs
- "Should I use X or Y?" questions
- Questions that need wide aggregation across many sources

## Characteristics

| Attribute | Value |
|-----------|-------|
| Effort | `medium` |
| Speed | ~1 minute |
| Cost | ~$0.02 |
| Output | Structured analysis with `[web:n]` inline citations, often 100+ sources |

## How to Call

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer ${PERPLEXITY_API_KEY:-$(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY // empty' ~/.claude/settings.json)}" \
  -H "Content-Type: application/json" \
  -d '{"effort": "medium", "input": "YOUR_ANALYSIS_QUESTION_HERE"}' \
  --max-time 300
```

## Response

Returns JSON with an `output` array:
- `message` item — `content[].text` is the analysis with `[web:n]` citation markers
- `search_results` items (several) — supporting sources; `[web:n]` matches the result whose `id` is `n`
- `fetch_url_results` items — pages the agent read in full

## Best For

- Tradeoff analysis
- Debugging strategies
- Architecture decisions
- Comparison questions
- Problems with multiple constraints

## Prompting Tips

- Clearly state constraints and requirements
- Ask for comparison when relevant
- Request explicit tradeoff analysis
- Frame as problem-solving, not confirmation
