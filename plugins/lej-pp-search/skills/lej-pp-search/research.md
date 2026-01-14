# sonar-deep-research (Research)

**Deep research with comprehensive analysis. Use only when explicitly asked for thorough/comprehensive research.**

## When to Use

- Complex topics requiring thorough investigation
- Generating reports or documentation
- Comparing multiple approaches/solutions
- Topics where you need high confidence
- When user explicitly asks for "deep" or "comprehensive" research

## Characteristics

| Attribute | Value |
|-----------|-------|
| Model | `sonar-deep-research` |
| Speed | Slow (30 seconds to 5 minutes) |
| Cost | ~$1+ per query |
| Output | Deep analysis with extensive citations |

## How to Call

```bash
curl -s -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $(jq -r '.environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar-deep-research", "messages": [{"role": "user", "content": "YOUR_RESEARCH_TOPIC_HERE"}]}' \
  --max-time 300
```

**Important:** Use `--max-time 300` to allow for the longer response time.

## Response

Returns JSON with:
- `choices[0].message.content` — Comprehensive analysis with extensive citations
- `citations` — Large array of source URLs (2× more than other models)
- `search_results` — Detailed search results
- `usage.reasoning_tokens` — Shows depth of analysis performed

## Best For

- Technical comparisons
- Architecture decisions
- Security analysis
- Comprehensive documentation
- Topics requiring high confidence

## Important Notes

- **Be patient**: Can take 30 seconds to 5 minutes
- **Use sparingly**: High cost (~$1+ per query)
- **Worth the wait**: When you need thorough, well-cited analysis
- **Not for quick lookups**: Use `sonar-pro` instead

## Prompting Tips

- Request specific comparisons or analyses
- Ask for multiple perspectives
- Specify what aspects matter most
- Frame as discovery, not confirmation
