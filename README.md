# LEJ PP Search

**Perplexity-Powered Search for Claude Code**

Here's the deal: Claude's built-in web search has a confirmation bias problem. It searches to *confirm* what it already thinks it knows from training data. Perplexity does the opposite - it searches to *discover* what it doesn't know.

This plugin swaps out WebSearch for Perplexity automatically. You get better results for anything that changes faster than Claude's training data can keep up with.

## How It Works

When you ask Claude to search for something:
1. The plugin blocks the built-in WebSearch
2. Claude calls the Perplexity API directly via curl
3. Returns results with actual citations

No MCP server needed. Just direct API calls using your Perplexity API key stored in `~/.claude/settings.json`.

---

## Setup

**Step 1:** Get a Perplexity API key at https://www.perplexity.ai/account/api/group

**Step 2:** Add the marketplace:

```
/plugin marketplace add justfinethanku/LEJ-Perplexity-Powered-Search-for-Claude
```

**Step 3:** Install the plugin:

```
/plugin install lej-pp-search@lej-marketplace
```

**How to run these commands:**
- **VSCode**: Open Claude Code in the sidebar, start a conversation, then type the commands directly into the chat
- **Terminal**: Run `claude` to start a session, then type the commands at the prompt

The `/` is important - it tells Claude this is a slash command, not a question.

**Step 4:** Run the setup command:

```
/lej-pp-search:setup
```

This will walk you through adding your API key safely.

Or manually add it to `~/.claude/settings.json`:

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

Most of the time Claude will use `sonar-pro`. The skill guides Claude to pick the right model based on what you're asking for.

## Toggling Auto-Redirect

Don't want WebSearch blocked? Just tell Claude:

> "Hey Claude, don't automatically use Perplexity"

Claude will disable auto-redirect. WebSearch works normally, and Perplexity is still available when you want it.

Want it back on? Just say:

> "Turn auto-redirect back on"

No config files to edit. Just talk to Claude.

## Why This Matters

LLMs search like humans with confirmation bias - they look for evidence to support what they already believe. Perplexity is architecturally different. It searches first, then synthesizes, which means it's actually looking for:

- Current documentation (not the cached version from 8 months ago)
- Recent API changes
- Information that contradicts outdated training data
- Stuff Claude doesn't know it doesn't know

## Benchmark: Perplexity vs WebSearch

We ran a head-to-head comparison using professional filmmaking queries (camera specs, workflows, technical comparisons).

### Speed

| Query | Perplexity | WebSearch |
|-------|------------|-----------|
| Sony FX9 II specs | 5.5s | 34.5s |
| Blackmagic LOG workflow | 7.8s | 44.5s |
| RED vs ARRI dynamic range | 7.0s | 29.7s |
| **Average** | **6.8s** | **36.2s** |

**Perplexity is 5x faster** on average.

### Quality

| Metric | Perplexity | WebSearch |
|--------|------------|-----------|
| Citations per query | 6-15 inline | 10-20 links |
| Source freshness | Consistently 2025-2026 | Variable |
| Answer structure | Highly synthesized | More raw links |
| Technical depth | Specific numbers & tables | Contextual summaries |

Both tools provided accurate information for these queries. The main differences: Perplexity returns faster with inline citations and structured answers. WebSearch returns more links but takes longer to synthesize.

## Need Help?

Run `/lej-pp-search:help` anytime to see usage info and available options.

## Uninstall

**Quick way** (keeps your API key for easy reinstall):
```
/plugin uninstall lej-pp-search@lej-marketplace
```

**Full cleanup** (nukes everything including the API key):
Just tell Claude "Uninstall lej-pp-search completely" and it'll handle the cleanup.

## License

MIT

## Author

[Limited Edition Jonathan](https://substack.com/@limitededitionjonathan), aka Jonathan Edwards, co-founder of [Aicred.ai](https://aicred.ai). An AI skills assessment and training platform.

---
