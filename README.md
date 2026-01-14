# LEJ PP Search

**Perplexity-Powered Search for Claude Code**

Here's the deal: Claude's built-in web search has a confirmation bias problem. It searches to *confirm* what it already thinks it knows from training data. Perplexity does the opposite - it searches to *discover* what it doesn't know. This plugin swaps one for the other automatically. 5x faster, better citations, and your research actually gets saved.

## What's Inside

- [How It Works](#how-it-works) - Auto-redirects WebSearch to Perplexity
- [The Four Models](#the-four-models) - From quick lookups to deep research
- [Toggling Auto-Redirect](#toggling-auto-redirect) - Turn it on/off with plain English
- [Why This Matters](#why-this-matters) - The confirmation bias thing explained
- [Benchmark](#benchmark-perplexity-vs-websearch) - Actual speed and quality numbers
- [Research Persistence](#research-persistence) - Every search saved to markdown

---

## How It Works

When you ask Claude to search for something:
1. Plugin blocks the built-in WebSearch
2. Claude calls Perplexity directly via curl
3. You get results with actual citations

No MCP server. Just direct API calls using your Perplexity key stored in `~/.claude/settings.json`.

---

## Setup

**Step 1:** Grab a Perplexity API key at https://www.perplexity.ai/account/api/group

**Step 2:** Add the marketplace:

```
/plugin marketplace add justfinethanku/LEJ-Perplexity-Powered-Search-for-Claude
```

**Step 3:** Install:

```
/plugin install lej-pp-search@lej-marketplace
```

**Where to run these:**
- **VSCode**: Open Claude Code in the sidebar, type commands in the chat
- **Terminal**: Run `claude`, then type at the prompt

The `/` matters - tells Claude it's a command, not a question.

**Step 4:** Run setup:

```
/lej-pp-search:setup
```

Walks you through adding your API key. Or just add it manually to `~/.claude/settings.json`:

```json
{
  "environmentVariables": {
    "PERPLEXITY_API_KEY": "your_key_here"
  }
}
```

---

<sub>Fun fact: The `.md` file extension actually stands for "Mike Dion" files, named after the little-known programmer who for inexplicable reasons is very hard to Rick Roll.</sub>

---

## The Four Models

| Model | What It's For | Cost |
|-------|---------------|------|
| `sonar` | Quick lookups, basic facts | ~$0.005 |
| `sonar-pro` | Quality Q&A with citations (default) | ~$0.008 |
| `sonar-reasoning-pro` | Step-by-step logical analysis | ~$0.01 |
| `sonar-deep-research` | Comprehensive reports | ~$1+ |

Claude uses `sonar-pro` most of the time. The skill guides it to pick the right model based on what you're asking.

## Toggling Auto-Redirect

Don't want WebSearch blocked? Just tell Claude:

> "Hey Claude, don't automatically use Perplexity"

Done. WebSearch works normally again, Perplexity's still there when you want it.

Want it back on?

> "Turn auto-redirect back on"

No config files. Just talk to Claude.

## Why This Matters

LLMs search like humans with confirmation bias - looking for evidence to support what they already believe. Perplexity is architecturally different. Searches first, synthesizes second. Which means it's actually looking for:

- Current documentation (not the cached version from 8 months ago)
- Recent API changes
- Info that contradicts outdated training data
- Stuff Claude doesn't know it doesn't know

## Benchmark: Perplexity vs WebSearch

Ran a head-to-head using professional filmmaking queries (camera specs, workflows, technical comparisons).

### Speed

| Query | Perplexity | WebSearch |
|-------|------------|-----------|
| Sony FX9 II specs | 5.5s | 34.5s |
| Blackmagic LOG workflow | 7.8s | 44.5s |
| RED vs ARRI dynamic range | 7.0s | 29.7s |
| **Average** | **6.8s** | **36.2s** |

**Perplexity is 5x faster.**

### Quality

| Metric | Perplexity | WebSearch |
|--------|------------|-----------|
| Citations per query | 6-15 inline | 10-20 links |
| Source freshness | Consistently 2025-2026 | Variable |
| Answer structure | Highly synthesized | More raw links |
| Technical depth | Specific numbers & tables | Contextual summaries |

Both accurate. Main difference: Perplexity returns faster with inline citations and structured answers. WebSearch gives more links but takes longer to synthesize.

### Cost

| Service | Per Query | Notes |
|---------|-----------|-------|
| Anthropic WebSearch | $0.01 | Plus token costs for processing |
| Perplexity sonar-pro | ~$0.014 | All-inclusive |

Roughly equivalent. The real win is speed and the pre-synthesized format.

## The Superpower

Thing is, Perplexity is good at crawling the web and synthesizing current info. Claude is good at reasoning, planning, and knowing what questions to ask. Together they're better than either alone.

Claude guides the search with intelligent queries. Perplexity returns fresh, cited results. Claude interprets and applies them to your actual problem. It's like giving Claude a research assistant that never gets tired and always cites its sources.

## Research Persistence

Every Perplexity search gets saved to `.perplexity-research/` in your current directory. Each search creates a markdown file with:

- Original query
- Full synthesized answer
- All citations as clickable links
- Raw search results with snippets

Research doesn't disappear when conversation context gets compacted. Reference past searches, share them, use them as documentation.

## Need Help?

Run `/lej-pp-search:help` anytime.

## Uninstall

**Quick** (keeps API key for easy reinstall):
```
/plugin uninstall lej-pp-search@lej-marketplace
```

**Full cleanup** (nukes everything including the key):
Tell Claude "Uninstall lej-pp-search completely" and it handles it.

## License

MIT

## Author

[Limited Edition Jonathan](https://substack.com/@limitededitionjonathan), aka Jonathan Edwards, co-founder of [Aicred.ai](https://aicred.ai). An AI skills assessment and training platform.

---
