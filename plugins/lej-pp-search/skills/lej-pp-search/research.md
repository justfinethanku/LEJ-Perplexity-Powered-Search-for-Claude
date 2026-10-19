# high preset (Research)

**Deep research with exhaustive source coverage. Use only when explicitly asked for thorough/comprehensive research.**

## When to Use

- Complex topics requiring thorough investigation
- Generating reports or documentation
- Comparing multiple approaches/solutions
- Topics where you need high confidence
- When user explicitly asks for "deep" or "comprehensive" research

## Characteristics

| Attribute | Value |
|-----------|-------|
| Preset | `high` (replaces `sonar-deep-research`) |
| Speed | Slow (several minutes) |
| Cost | Highest of the research presets |
| Output | Deep analysis with extensive `[web:n]` citations |

For open-ended agentic work (running code in a sandbox, long tool-use loops), use `xhigh` instead. It is the most capable and most expensive preset.

## How to Call

```bash
curl -s "https://api.perplexity.ai/v1/agent" \
  -H "Authorization: Bearer $(jq -r '.env.PERPLEXITY_API_KEY // .environmentVariables.PERPLEXITY_API_KEY' ~/.claude/settings.json)" \
  -H "Content-Type: application/json" \
  -d '{"preset": "high", "input": "YOUR_RESEARCH_TOPIC_HERE"}' \
  --max-time 600
```

**Important:** Use `--max-time 600` to allow for the longer response time.

## Response

Returns JSON with an `output` array:
- `message` item — `content[].text` is the comprehensive analysis with `[web:n]` citation markers
- `search_results` items — large set of sources; `[web:n]` matches the result whose `id` is `n`
- `usage.output_tokens_details.reasoning_tokens` — shows depth of analysis performed
- `usage.cost.total_cost` — what the run cost

## Best For

- Technical comparisons
- Architecture decisions
- Security analysis
- Comprehensive documentation
- Topics requiring high confidence

## Important Notes

- **Be patient**: Can take several minutes
- **Use sparingly**: Highest cost of the research presets
- **Worth the wait**: When you need thorough, well-cited analysis
- **Not for quick lookups**: Use `fast` instead

## Prompting Tips

- Request specific comparisons or analyses
- Ask for multiple perspectives
- Specify what aspects matter most
- Frame as discovery, not confirmation
