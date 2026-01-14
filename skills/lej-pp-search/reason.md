# perplexity_reason

**Logical analysis with visible thinking process. Uses sonar-reasoning-pro model.**

## When to Use

- Problems requiring step-by-step reasoning
- Debugging complex issues
- Architecture decisions with tradeoffs
- When you need to see the reasoning process
- Analytical questions

## Characteristics

| Attribute | Value |
|-----------|-------|
| Model | sonar-reasoning-pro |
| Speed | Moderate |
| Cost | Moderate |
| Output | `<think>` block + synthesized answer |
| Citations | Standard citation array |

## Example Usage

```json
{
  "messages": [
    {"role": "system", "content": "Analyze this problem step by step, showing your reasoning"},
    {"role": "user", "content": "Given these constraints: 1) Must support 10k concurrent users, 2) Budget under $500/month, 3) Team knows Python but not Go - should we use FastAPI with PostgreSQL or Django with PostgreSQL for our API?"}
  ]
}
```

## Response Format

Returns response with visible reasoning:

```
<think>
Step 1: Analyzing concurrent user requirement...
Step 2: Evaluating cost constraints...
Step 3: Considering team expertise...
...
</think>

Based on the analysis, FastAPI with PostgreSQL is recommended because...
[citations]
```

## Best For

- Tradeoff analysis
- Debugging strategies
- Architecture decisions
- "Should I use X or Y?" questions
- Problems with multiple constraints

## Prompting Tips

- Clearly state constraints and requirements
- Ask for comparison when relevant
- Request explicit tradeoff analysis
- Frame as problem-solving, not confirmation
