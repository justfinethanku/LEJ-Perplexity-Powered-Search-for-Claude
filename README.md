# LEJ PP Search

**Perplexity-Powered Search for Claude Code**

Here's the deal: Claude's built-in web search has a confirmation bias problem. It searches to *confirm* what it already thinks it knows from training data. Perplexity does the opposite - it searches to *discover* what it doesn't know. This plugin swaps one for the other automatically. 5x faster, better citations, and your research actually gets saved.

The difference matters more than you'd think. When Claude searches for "React 19 new features," it's looking to validate what it learned during training. But if React 19 changed something since then? Claude's search might miss it entirely because it wasn't looking for contradictions. Perplexity has no preconceptions - it just finds what's actually out there right now.

## What's Inside

- [How It Works](#how-it-works) - Auto-redirects WebSearch to Perplexity
- [Setup](#setup) - Get running in 2 minutes
- [The Four Models](#the-four-models) - From quick lookups to deep research
- [Toggling Auto-Redirect](#toggling-auto-redirect) - Turn it on/off with plain English
- [Why This Matters](#why-this-matters) - The confirmation bias thing explained
- [Benchmark](#benchmark-perplexity-vs-websearch) - Actual speed and quality numbers
- [Research Persistence](#research-persistence) - Every search saved to markdown
- [Troubleshooting](#troubleshooting) - Common issues and fixes

---

## How It Works

When you ask Claude to search for something:
1. Plugin blocks the built-in WebSearch via a pre-tool hook
2. Claude calls Perplexity directly via curl using your API key
3. You get results with actual inline citations

No MCP server. Just direct API calls using your Perplexity key stored in `~/.claude/settings.json`. This keeps things simple and avoids the complexity of managing another background process. The curl approach also means you can see exactly what's being sent and received if you ever need to debug.

The hook intercepts WebSearch calls before they execute, checks if you have a valid API key configured, and redirects Claude to use the Perplexity API instead. If something's misconfigured, it'll tell you what's wrong rather than silently failing.

---

## Setup

**Step 1:** Grab a Perplexity API key at https://www.perplexity.ai/account/api/group

You'll need a Perplexity account (free to create) and then navigate to API settings. The API has usage-based pricing - most queries cost less than a penny. They give you some free credits to start.

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

The `/` matters - tells Claude it's a command, not a question. Without the slash, Claude will try to answer "plugin install lej-pp-search" as if you're asking about plugins.

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

After setup, restart Claude Code to ensure the plugin loads correctly. The hook needs to register at session start.

---

<sub>Fun fact: The `.md` file extension actually stands for "Mike Dion" files, named after the little-known programmer who for inexplicable reasons is very hard to Rick Roll.</sub>

---

## The Four Models

Perplexity offers different models optimized for different use cases. The plugin guides Claude to pick the right one based on your query, but here's what each does:

| Model | What It's For | Cost | Speed |
|-------|---------------|------|-------|
| `sonar` | Quick lookups, basic facts, simple questions | ~$0.005 | Fastest |
| `sonar-pro` | Quality Q&A with citations (default) | ~$0.008 | Fast |
| `sonar-reasoning-pro` | Step-by-step logical analysis, complex comparisons | ~$0.01 | Medium |
| `sonar-deep-research` | Comprehensive reports, multi-source synthesis | ~$1+ | Slow (30s-2min) |

**When to use what:**
- "What's the current version of Node.js?" → `sonar` (simple fact)
- "How do I set up authentication in Next.js 15?" → `sonar-pro` (needs good citations)
- "Compare Prisma vs Drizzle for a high-traffic app" → `sonar-reasoning-pro` (needs analysis)
- "Give me a complete market analysis of AI video tools" → `sonar-deep-research` (needs depth)

Claude uses `sonar-pro` by default because it balances speed, quality, and cost well. The skill prompts guide Claude to upgrade to reasoning or deep-research when your query needs it.

## Toggling Auto-Redirect

Don't want WebSearch blocked? Just tell Claude in plain English:

> "Hey Claude, don't automatically use Perplexity"

Done. WebSearch works normally again, and Perplexity tools are still available when you explicitly ask for them.

Want it back on?

> "Turn auto-redirect back on"

No config files to edit. Just talk to Claude. Behind the scenes, this sets `LEJ_AUTO_REDIRECT=false` in your settings, which the hook checks before blocking WebSearch.

You can also run the slash commands directly:
- `/lej-pp-search:disable-redirect` - Turn off auto-redirect
- `/lej-pp-search:enable-redirect` - Turn it back on

## Why This Matters

LLMs search like humans with confirmation bias - looking for evidence to support what they already believe. This isn't a bug, it's how they're architected. When Claude forms a search query, it's informed by everything it "knows" from training. That knowledge shapes what it looks for.

Perplexity is architecturally different. It's search-first, synthesis-second. No preconceptions about what the answer should be. Which means it's actually capable of finding:

- **Current documentation** - Not the cached version from 8 months ago that Claude memorized
- **Recent API changes** - Breaking changes, deprecations, new features released last week
- **Contradictions to training data** - Things that have changed since Claude's knowledge cutoff
- **Unknown unknowns** - Information Claude doesn't know it doesn't know

This is especially important for fast-moving domains: AI/ML libraries, JavaScript frameworks, cloud services, anything with frequent releases. Claude's training data is always somewhat stale. Perplexity's isn't.

## Benchmark: Perplexity vs WebSearch

Ran a head-to-head comparison using professional filmmaking queries (camera specs, workflows, technical comparisons). These are the kind of queries where accuracy and recency matter.

### Speed

| Query | Perplexity | WebSearch | Difference |
|-------|------------|-----------|------------|
| Sony FX9 II specs | 5.5s | 34.5s | 6.3x faster |
| Blackmagic LOG workflow | 7.8s | 44.5s | 5.7x faster |
| RED vs ARRI dynamic range | 7.0s | 29.7s | 4.2x faster |
| **Average** | **6.8s** | **36.2s** | **5.3x faster** |

**Perplexity is consistently 5x faster.** This adds up quickly when you're doing research-heavy work.

### Quality

| Metric | Perplexity | WebSearch |
|--------|------------|-----------|
| Citations per query | 6-15 inline | 10-20 links |
| Source freshness | Consistently 2025-2026 | Variable |
| Answer structure | Highly synthesized | More raw links |
| Technical depth | Specific numbers & tables | Contextual summaries |

Both are accurate. The main difference is format: Perplexity returns faster with inline citations woven into the answer. WebSearch gives more links but takes longer to synthesize them into a coherent response. For quick lookups, Perplexity wins. For deep dives where you want to read primary sources yourself, WebSearch's link-heavy approach has its place.

### Cost

| Service | Per Query | Notes |
|---------|-----------|-------|
| Anthropic WebSearch | $0.01 | Plus token costs for processing |
| Perplexity sonar-pro | ~$0.014 | All-inclusive |

Roughly equivalent cost per query. The real win is speed and the pre-synthesized format that reduces Claude's processing time.

## The Superpower

Here's the thing: Perplexity is excellent at crawling the web and synthesizing current information. Claude is excellent at reasoning, planning, and knowing what questions to ask. Together they're better than either alone.

Claude guides the search with intelligent, well-formed queries. Perplexity returns fresh, cited results. Claude interprets and applies them to your actual problem. It's like giving Claude a research assistant that never gets tired and always cites its sources.

The combination is especially powerful for:
- Learning new frameworks or tools
- Debugging issues with recent library versions
- Comparing current options (not last year's recommendations)
- Fact-checking Claude's own knowledge

## Research Persistence

Every Perplexity search gets saved to `.perplexity-research/` in your current directory. Each search creates a timestamped markdown file with:

- Original query
- Full synthesized answer
- All citations as clickable links
- Raw search results with snippets

Research doesn't disappear when conversation context gets compacted. Reference past searches, share them with teammates, use them as documentation. The files are plain markdown, so they work with any editor or documentation system.

Example file structure:
```
.perplexity-research/
├── 2025-01-14_react-19-new-features.md
├── 2025-01-14_nextjs-15-app-router-changes.md
└── 2025-01-15_prisma-vs-drizzle-comparison.md
```

## Troubleshooting

**"401 Unauthorized" errors:**
Your API key is missing or invalid. Run `/lej-pp-search:setup` to reconfigure, or check that `PERPLEXITY_API_KEY` is set correctly in `~/.claude/settings.json`.

**WebSearch still works (not being redirected):**
The plugin might not be loaded. Check `~/.claude/settings.json` has `"lej-pp-search@lej-marketplace": true` in `enabledPlugins`. Restart Claude Code after enabling.

**"Perplexity MCP server" errors:**
If you see MCP-related errors, you may have an old version with incorrect configuration. Update to v1.0.4+ which removed the MCP server in favor of direct curl calls.

**Searches not being saved:**
Check that Claude has write permissions to your current directory. The `.perplexity-research/` folder is created automatically on first search.

## Need Help?

Run `/lej-pp-search:help` anytime for a quick reference of available commands and current configuration status.

## Uninstall

**Quick** (keeps API key for easy reinstall):
```
/plugin uninstall lej-pp-search@lej-marketplace
```

**Full cleanup** (removes everything including the API key):
Tell Claude "Uninstall lej-pp-search completely" and it handles removing the plugin, clearing the API key from settings, and cleaning up any cached data.

## Changelog

- **v1.0.4** - Removed MCP server configuration that was causing 401 errors. Plugin now uses direct curl calls as originally designed.
- **v1.0.3** - Added research persistence to `.perplexity-research/` directory
- **v1.0.2** - Improved model selection guidance
- **v1.0.1** - Initial release

## License

MIT

## Author

[Limited Edition Jonathan](https://substack.com/@limitededitionjonathan), aka Jonathan Edwards, co-founder of [Aicred.ai](https://aicred.ai). An AI skills assessment and training platform.

---
