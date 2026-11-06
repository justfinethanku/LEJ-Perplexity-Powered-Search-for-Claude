# LEJ PP Search

**Perplexity-Powered Search for Claude Code**

This plugin intercepts Claude Code's built-in WebSearch and prompts Claude to call Perplexity with `curl`. A separate hook saves recognized responses as Markdown in your project.

**Current compatibility (verified November 6, 2026):** `main` still uses the legacy Sonar `/chat/completions` API and `environmentVariables` settings. Its save hook accepts a JSON **string** in `tool_response`; current Claude Code Bash events use an object with `stdout`, which this version silently skips. [PR #3](https://github.com/justfinethanku/LEJ-Perplexity-Powered-Search-for-Claude/pull/3) tracks the API, settings, and response migration and is not yet merged. Installation succeeds on Claude Code 2.1.318, but that does not establish working live searches or automatic saving. See [Troubleshooting](#troubleshooting) before configuring a key.

The difference matters more than you'd think. When Claude searches for "React 19 new features," it's looking to validate what it learned during training. But if React 19 changed something since then? Claude's search might miss it entirely because it wasn't looking for contradictions. Perplexity has no preconceptions - it just finds what's actually out there right now.

## What's Inside

- [How It Works](#how-it-works) - Auto-redirects WebSearch to Perplexity
- [Setup](#setup) - Prerequisites, installation, and verification
- [The Four Models](#the-four-models) - From quick lookups to deep research
- [Toggling Auto-Redirect](#toggling-auto-redirect) - Turn it on/off with plain English
- [Why This Matters](#why-this-matters) - The confirmation bias thing explained
- [Benchmark](#benchmark-perplexity-vs-websearch) - Historical speed and quality observations
- [Research Persistence](#research-persistence) - Supported responses and saved files
- [Troubleshooting](#troubleshooting) - Common issues and fixes
- [Local validation](#local-validation) - Check a checkout without an API key

---

## How It Works

When you ask Claude to search for something:
1. Plugin blocks the built-in WebSearch via a pre-tool hook
2. Claude calls Perplexity directly via curl using your API key
3. You get results with actual inline citations

No MCP server. Just direct API calls using your Perplexity key stored in `~/.claude/settings.json`. This keeps things simple and avoids the complexity of managing another background process. The curl approach also means you can see exactly what's being sent and received if you ever need to debug.

The hook intercepts WebSearch calls before they execute and checks for a nonempty configured key. It does not validate that key or make the search itself: it blocks WebSearch with instructions for Claude to run `curl`. A later API failure is separate from the redirect hook.

---

## Setup

### Prerequisites

Use macOS or Linux with Claude Code, Git, Bash, `curl`, `jq`, and Python 3 available on the PATH inherited by Claude Code. The Python helpers use the standard library; there is no package install or MCP server to start. Check your terminal:

```bash
claude --version
git --version
bash --version
curl --version
jq --version
python3 --version
```

Install any missing prerequisite with your platform's package manager, then restart Claude Code so its hooks inherit the updated PATH.

### Install and verify

Run these commands in your terminal, outside a Claude Code session:

```bash
claude plugin marketplace add justfinethanku/LEJ-Perplexity-Powered-Search-for-Claude
claude plugin install lej-pp-search@lej-marketplace --scope user
claude plugin list --json
```

The list should contain `lej-pp-search@lej-marketplace`, `"scope": "user"`, and `"enabled": true`. This confirms installation only; it does not test the API or saving. See the [Claude Code plugin command reference](https://code.claude.com/docs/en/plugins/cli-reference) for other installation scopes.

Inside an interactive Claude Code session, the equivalent commands are:

```text
/plugin marketplace add justfinethanku/LEJ-Perplexity-Powered-Search-for-Claude
/plugin install lej-pp-search@lej-marketplace
```

Start a new Claude Code session after installation. Run `/lej-pp-search:help` to confirm the plugin's commands are available.

### Legacy key setup

Obtain an API key from the [Perplexity API console](https://www.perplexity.ai/account/api/group). API billing is separate from a consumer subscription; check [current API pricing](https://docs.perplexity.ai/docs/getting-started/pricing) before making requests. Installation and local validation do not require a key or make paid API requests.

The current setup command attempts a legacy Sonar request to verify a key:

```text
/lej-pp-search:setup
```

It can fail at that request even with a valid key. The current hook reads this **legacy** structure in `~/.claude/settings.json`:

```json
{
  "environmentVariables": {
    "PERPLEXITY_API_KEY": "your_key_here"
  }
}
```

Merge fields into existing settings rather than replacing the file. This is the legacy hook's input, not Claude Code's supported environment setting: Claude Code uses `env`. Setting only `env.PERPLEXITY_API_KEY` does not satisfy the current hook, and exporting the variable alone does not satisfy it either. PR #3 owns that compatibility fix. The scripts also hard-code `$HOME/.claude/settings.json`; changing only `CLAUDE_CONFIG_DIR` does not relocate their key lookup.

After any settings change, start a new session. A redirect message proves only that the hook found a key; check the API response and the saved file separately. Never print or share your key while diagnosing a failure.

---

<sub>Fun fact: The `.md` file extension actually stands for "Mike Dion" files, named after the little-known programmer who for inexplicable reasons is very hard to Rick Roll.</sub>

---

## The Four Models

These are the legacy model names used by the current plugin, not a current Perplexity model catalog. The following costs and speeds are historical examples. For current API choices and migration guidance, use the [Perplexity quickstart](https://docs.perplexity.ai/docs/getting-started/quickstart) and PR #3.

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

The original README reported this comparison using professional filmmaking queries. The repository does not include a runnable benchmark or raw timing logs for it, and the November 2026 local documentation audit did not reproduce these API timings. Treat the numbers and prices in this section as historical observations, not current guarantees.

### Speed

| Query | Perplexity | WebSearch | Difference |
|-------|------------|-----------|------------|
| Sony FX9 II specs | 5.5s | 34.5s | 6.3x faster |
| Blackmagic LOG workflow | 7.8s | 44.5s | 5.7x faster |
| RED vs ARRI dynamic range | 7.0s | 29.7s | 4.2x faster |
| **Average** | **6.8s** | **36.2s** | **5.3x faster** |

The reported average in this sample was 5.3x faster. Actual latency depends on the API, query, and service conditions.

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

Automatic saving requires Bash, `jq`, and Python 3 on macOS or Linux. New research
files are readable and writable only by your user. The writer creates the research
directory on the first recognized result; starting a session does not create it.
The save hook rejects a `.perplexity-research` symlink and gives each result a unique filename, so repeated
searches in the same second do not overwrite earlier results.

The save hook writes to `.perplexity-research/` relative to its working directory when a Bash command contains `api.perplexity.ai` and its string response contains `choices[0].message.content`. It skips unrelated commands and unsupported/error response shapes without creating a file. It does not currently handle object-shaped Bash responses or Agent API output (see PR #3).

Each recognized response creates a timestamped Markdown file with:

- Original query
- Full synthesized answer
- All citations as clickable links
- Raw search results with snippets

Research doesn't disappear when conversation context gets compacted. Reference past searches, share them with teammates, use them as documentation. The files are plain markdown, so they work with any editor or documentation system.

Filenames contain local date and time, a sanitized query prefix (up to 50 characters), and a unique UUID suffix. For example:

```text
.perplexity-research/
└── 2026-11-06-10-30-00-react-features-0123456789abcdef0123456789abcdef.md
```

Existing directory permissions are preserved. New directories use mode `0700`, and new files use mode `0600`; share files deliberately if teammates need them. Query extraction supports literal JSON curl bodies, not shell-expanded variables or `@file` request bodies.

## Troubleshooting

**Installation succeeds but searches fail with `403` or `agent_api_migration_required`:**
The installed legacy endpoint is incompatible with the API. Follow PR #3; reinstalling the same version or replacing a valid key does not migrate it.

**`jq: command not found` or `python3: command not found`:**
Run the prerequisite checks in the same environment that launches Claude Code. Installing the plugin does not install these tools.

**"401 Unauthorized" errors:**
Your API key is missing or invalid. Run `/lej-pp-search:setup` to reconfigure, or check that `PERPLEXITY_API_KEY` is set correctly in `~/.claude/settings.json`.

The legacy hook reads `environmentVariables.PERPLEXITY_API_KEY`, not `env` or the shell environment. It checks presence only. An authentication failure from the remote API requires a separate key/billing check in your API console.

**WebSearch still works (not being redirected):**
The plugin might not be loaded. Check `~/.claude/settings.json` has `"lej-pp-search@lej-marketplace": true` in `enabledPlugins`. Restart Claude Code after enabling.

**"Perplexity MCP server" errors:**
If you see MCP-related errors, you may have an old version with incorrect configuration. Update to v1.0.4+ which removed the MCP server in favor of direct curl calls.

**Searches not being saved:**
First check the compatibility note: an object-shaped Bash response or Agent API response is silently skipped by this version. Check that the Markdown file exists. The hook also writes `Research saved to ...` to stderr, which successful hooks do not surface in the normal conversation; use [Claude Code hook debug logging](https://code.claude.com/docs/en/hooks#exit-code-0) to inspect it. An API answer alone does not confirm a save.

If the hook reports `Research not saved: unsafe or inaccessible research path.`, check that its working directory is writable and `.perplexity-research` is a real directory, not a symlink or regular file. Session start does not create the directory. Preserve any existing file or research before resolving a path conflict. For manual recovery of an answer, use the [private writer procedure](plugins/lej-pp-search/skills/lej-pp-search/SKILL.md#persisting-research-results) instead of rerunning a paid search.

**Installed code has not changed after a fix merged:**
Refresh the marketplace, update the installed plugin, and start a new session:

```bash
claude plugin marketplace update lej-marketplace
claude plugin update lej-pp-search@lej-marketplace --scope user
claude plugin list --json
```

The manifest still declares version `2.3.0`. If Claude reports it is already current but the cached files are stale, uninstall and reinstall the plugin using the commands below; do not edit cached source or the plugin registry JSON by hand.

## Local validation

To validate a source checkout without a key or API request, run:

```bash
git clone https://github.com/justfinethanku/LEJ-Perplexity-Powered-Search-for-Claude.git
cd LEJ-Perplexity-Powered-Search-for-Claude
claude plugin validate .
claude plugin validate plugins/lej-pp-search
python3 -m unittest discover -v
```

The tests use temporary projects and synthetic responses to exercise hook behavior and private file writes. They do not verify live API access or an interactive Claude session. The marketplace validator can report a missing-icon advisory; validation still succeeds.

## Need Help?

Run `/lej-pp-search:help` anytime for a quick reference of available commands and current configuration status.

## Uninstall

To remove the user-scoped installation from your terminal:

```bash
claude plugin uninstall lej-pp-search@lej-marketplace --scope user
claude plugin list --json
```

The plugin should be absent from the list. For an installation at another scope, use that scope instead. Inside an interactive Claude Code session, use `/plugin uninstall lej-pp-search@lej-marketplace`.

Optional: remove the marketplace too, if you do not use any of its other plugins:

```bash
claude plugin marketplace remove lej-marketplace --scope user
claude plugin marketplace list --json
```

Removing the marketplace can uninstall its other plugins at that scope. These commands leave this plugin's manually stored API key and project `.perplexity-research/` files in place. They do not revoke the key at Perplexity.

Optional: to also remove the API key from the default settings file, use a private temporary file beside your settings.
This preserves other settings and makes the updated file readable only by your user:

```bash
(
  set -e
  settings_tmp=$(mktemp "$HOME/.claude/settings.json.XXXXXX")
  trap 'rm -f "$settings_tmp"' EXIT
  jq 'del(.env.PERPLEXITY_API_KEY, .environmentVariables.PERPLEXITY_API_KEY)' \
    "$HOME/.claude/settings.json" > "$settings_tmp"
  mv "$settings_tmp" "$HOME/.claude/settings.json"
)
```

Then restart Claude Code.

## Changelog

- **v2.3.0** - Automatic research saving via PostToolUse hook (enforced, not optional)
- **v2.2.1** - Auto-create `.perplexity-research/` folder on session start
- **v2.2.0** - Research persistence to `.perplexity-research/` directory
- **v1.0.4** - Removed MCP server causing 401 errors

See [CHANGELOG.md](CHANGELOG.md) for full history.

## License

MIT

## Author

[Limited Edition Jonathan](https://substack.com/@limitededitionjonathan), aka Jonathan Edwards, co-founder of [Aicred.ai](https://aicred.ai). An AI skills assessment and training platform.

---
