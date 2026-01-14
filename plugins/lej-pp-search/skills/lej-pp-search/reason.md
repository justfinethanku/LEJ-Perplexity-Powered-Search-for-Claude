# sonar-reasoning-pro (Reason)

**Logical analysis with step-by-step reasoning. Use for complex comparisons and tradeoff analysis.**

## When to Use

- Problems requiring step-by-step reasoning
- Debugging complex issues
- Architecture decisions with tradeoffs
- When you need to see the reasoning process
- "Should I use X or Y?" questions

## Characteristics

| Attribute | Value |
|-----------|-------|
| Model | `sonar-reasoning-pro` |
| Speed | Moderate |
| Cost | ~$0.01 |
| Output | Structured reasoning + synthesized answer |

## How to Call

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar-reasoning-pro", "messages": [{"role": "user", "content": "YOUR_ANALYSIS_QUESTION_HERE"}]}'
```

## Response

Returns JSON with:
- `choices[0].message.content` — Structured analysis with reasoning steps
- `citations` — Array of source URLs
- `search_results` — Supporting search results

The response often includes visible reasoning structure with analysis of different factors and tradeoffs.

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
