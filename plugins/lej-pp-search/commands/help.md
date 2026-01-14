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

## Available Tools

### perplexity_search
**Fast URL/link retrieval**

```
Speed: Fast | Cost: Low
Best for: Raw URLs, titles, snippets
```

Use when you just need links and basic info.

---

### perplexity_ask
**Quick Q&A with citations**

```
Speed: Moderate | Cost: Moderate
Model: sonar-pro
```

Use for synthesized answers with source citations.

---

### perplexity_research
**Deep dives and comprehensive analysis**

```
Speed: Slow (30s-5min) | Cost: High
Best for: Deep analysis, comprehensive reports, 2x citations
```

Use for thorough research and detailed reports.

---

### perplexity_reason
**Step-by-step logical breakdowns**

```
Speed: Moderate | Cost: Moderate
Best for: Logical analysis, shows thinking process
```

Use when you need to work through a problem systematically.

---

## Quick Tool Selection

```
Need raw URLs/links?      -> perplexity_search
Quick question?           -> perplexity_ask
Deep research/reports?    -> perplexity_research
Logical problem/analysis? -> perplexity_reason
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
