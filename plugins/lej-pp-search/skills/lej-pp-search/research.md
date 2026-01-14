# perplexity_research

**Deep research with comprehensive analysis. Uses sonar-deep-research model.**

## When to Use

- Complex topics requiring thorough investigation
- Generating reports or documentation
- Comparing multiple approaches/solutions
- Topics where you need high confidence
- When 2× citations matter

## Characteristics

| Attribute | Value |
|-----------|-------|
| Model | sonar-deep-research |
| Speed | Slow (30 seconds to 5 minutes) |
| Cost | High |
| Output | Deep analysis with comprehensive citations |
| Citations | 2× more than other tools |

## Example Usage

```json
{
  "messages": [
    {"role": "system", "content": "Provide comprehensive analysis with multiple perspectives and extensive citations"},
    {"role": "user", "content": "Compare authentication strategies for Next.js applications: NextAuth.js vs Clerk vs Auth0. Include security considerations, pricing, and developer experience."}
  ]
}
```

## Response

Returns comprehensive analysis that:
- Explores topic from multiple angles
- Provides extensive citations (2× normal)
- Takes time to gather and synthesize
- Suitable for documentation/reports

## Best For

- Technical comparisons
- Architecture decisions
- Security analysis
- Comprehensive documentation
- Topics requiring high confidence

## Important Notes

- **Be patient**: Can take 30 seconds to 5 minutes
- **Use sparingly**: High cost per query
- **Worth the wait**: When you need thorough, well-cited analysis
- **Not for quick lookups**: Use `perplexity_ask` instead

## Prompting Tips

- Request specific comparisons or analyses
- Ask for multiple perspectives
- Specify what aspects matter most
- Frame as discovery, not confirmation
