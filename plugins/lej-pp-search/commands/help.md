---
description: "Explain LEJ PP Search plugin and available tools"
---

# LEJ PP Search Help

Please explain the following to the user:

## What is LEJ PP Search?

**LEJ PP Search** (Perplexity-Powered Search for Claude Code) by [Limited Edition Jonathan](https://substack.com/@limitededitionjonathan).

This plugin redirects web searches to Perplexity, which searches to **discover** new information rather than confirm existing knowledge. LLMs have confirmation bias when searching - they look for evidence to support beliefs from training data. Perplexity is architecturally different: it searches first, then synthesizes.

**Best for:**
- Up-to-date documentation
- Recent changes to APIs, frameworks, tools
- Information that contradicts outdated training data
- Current best practices

---

## Search Effort Levels

The plugin calls Perplexity's Agent API (`/v1/agent`) with an `effort` level that sets how deep it researches. Costs and times below were measured on real queries.

### fast (default)
**Quick lookups and everyday questions**

```
Speed: ~5s | Cost: ~$0.002
Best for: Facts, definitions, current versions, quick summaries
```

---

### low
**Light multi-step research**

```
Speed: ~1 min | Cost: ~$0.01
Best for: Questions that need a few searches
```

---

### medium
**Multi-hop research and comparisons**

```
Speed: ~1 min | Cost: ~$0.02
Best for: Tradeoffs, X vs Y, chaining evidence across many sources
```

---

### high / xhigh
**Deep research**

```
Speed: Several minutes | Cost: Highest
Best for: Comprehensive reports; xhigh for open-ended agentic work
```

---

## Quick Effort Selection

```
Quick question?           -> fast
Needs a few searches?     -> low
Comparison / analysis?    -> medium
Deep research/reports?    -> high
```

---

## Auto-Redirect Feature

By default, WebSearch calls are automatically redirected to Perplexity.

**Commands:**
- `/lej-pp-search:disable-redirect` - Turn off auto-redirect
- `/lej-pp-search:enable-redirect` - Turn it back on

Or just say "don't automatically use Perplexity" / "turn auto-redirect back on"

---

## Prompting Tips

Frame queries to **discover**, not **confirm**:

**Good:**
- "What is the current state of X?"
- "What has changed in X since [date]?"
- "What are the latest best practices for X?"

**Avoid:**
- "Is X still true?"
- "Confirm X works this way"
- "Verify that X is correct"

---

## Available Commands

- `/lej-pp-search:help` - Show this help
- `/lej-pp-search:setup` - Configure your Perplexity API key
- `/lej-pp-search:disable-redirect` - Disable auto-redirect
- `/lej-pp-search:enable-redirect` - Enable auto-redirect

---

## Uninstall

To fully remove (including API key): Say "uninstall lej-pp-search completely"

To reinstall later: `/plugin install lej-pp-search@lej-marketplace`
