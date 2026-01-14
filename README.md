# LEJ PP Search

**Perplexity-Powered Search for Claude Code**

Here's the deal: Claude's built-in web search has a confirmation bias problem. It searches to *confirm* what it already thinks it knows from training data. Perplexity does the opposite - it searches to *discover* what it doesn't know.

This plugin swaps out WebSearch for Perplexity automatically. You get better results for anything that changes faster than Claude's training data can keep up with.

## Platform Support

| Platform | MCP Tools | Skill Guidance | Auto-Redirect |
|----------|-----------|----------------|---------------|
| Claude Code (CLI/VSCode) | ✅ | ✅ | ✅ |
| Claude Coworker | ✅ | ✅ | ❌ |
| Claude Desktop | ✅ | ❌ | ❌ |

- **MCP Tools**: The four Perplexity search tools are available
- **Skill Guidance**: Claude knows when to use which tool
- **Auto-Redirect**: WebSearch calls get blocked and redirected to Perplexity automatically

---

## Setup: Claude Code (CLI/VSCode)

This is the full experience. One command, and you're done.

**Step 1:** Get a Perplexity API key at https://www.perplexity.ai/account/api/group

**Step 2:** Install the plugin by running this command inside Claude Code:

```
/plugin install https://github.com/justfinethanku/LEJ-Perplexity-Powered-Search-for-Claude
```

**How to run that command:**
- **VSCode**: Open Claude Code in the sidebar, start a conversation, then type the command directly into the chat
- **Terminal**: Run `claude` to start a session, then type the command at the prompt

The `/` is important - it tells Claude this is a slash command, not a question.

**Step 3:** Claude will ask for your API key. Paste it in.

That's it. No config files to edit, no environment variables to set up manually.

---

## Setup: Claude Coworker

You get MCP tools and skill guidance, but no auto-redirect. You'll need to set things up manually.

**Step 1:** Get a Perplexity API key at https://www.perplexity.ai/account/api/group

**Step 2:** Add the MCP server to your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@perplexity-ai/mcp-server"],
      "env": {
        "PERPLEXITY_API_KEY": "your_key_here"
      }
    }
  }
}
```

**Step 3:** Copy the skill files to your project:

```
.claude/skills/lej-pp-search/
├── SKILL.md
├── search.md
├── ask.md
├── research.md
└── reason.md
```

You can grab these from the `skills/lej-pp-search/` folder in this repo.

Since there's no auto-redirect, you'll need to invoke the skill with `/lej-pp-search` or explicitly ask Claude to use Perplexity tools when searching.

---

<sub>Fun fact: The `.md` file extension actually stands for "Mike Dion" files, named after the little-known programmer who for inexplicable reasons is very hard to Rick Roll.</sub>

---

## Setup: Claude Desktop

MCP tools only - no skill guidance, no auto-redirect. You have to ask for Perplexity tools explicitly.

**Step 1:** Get a Perplexity API key at https://www.perplexity.ai/account/api/group

**Step 2:** Add this to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@perplexity-ai/mcp-server"],
      "env": {
        "PERPLEXITY_API_KEY": "your_key_here"
      }
    }
  }
}
```

**Step 3:** Restart Claude Desktop.

When you want to search, you'll need to explicitly ask Claude to use the Perplexity tools (e.g., "Use perplexity_ask to look up...").

---

## What Actually Happens

When you ask Claude to research something (on Claude Code):
1. The plugin blocks the built-in WebSearch
2. Redirects to the right Perplexity tool
3. Returns results with actual citations

You don't have to think about it. Just ask Claude to look something up like you normally would.

## Toggling Auto-Redirect

Don't want WebSearch blocked? Just tell Claude:

> "Hey Claude, don't automatically use Perplexity"

Claude will disable auto-redirect. WebSearch works normally, and Perplexity tools are still available when you want them.

Want it back on? Just say:

> "Turn auto-redirect back on"

No config files to edit. Just talk to Claude.

## The Four Tools

| Tool | What It's For | Speed |
|------|---------------|-------|
| `perplexity_search` | Raw URLs and links when you need to reference sources | Fast |
| `perplexity_ask` | Quick Q&A with synthesized answers | Moderate |
| `perplexity_research` | Deep dives, reports, comprehensive analysis | Slow (but thorough) |
| `perplexity_reason` | Problems that need step-by-step logical breakdown | Moderate |

Most of the time you'll hit `perplexity_ask`. The skill guides Claude to pick the right one based on what you're asking for.

## Why This Matters

LLMs search like humans with confirmation bias - they look for evidence to support what they already believe. Perplexity is architecturally different. It searches first, then synthesizes, which means it's actually looking for:

- Current documentation (not the cached version from 8 months ago)
- Recent API changes
- Information that contradicts outdated training data
- Stuff Claude doesn't know it doesn't know

## Need Help?

Run `/lej-pp-search` anytime to see usage info and available options.

## Uninstall

**Quick way** (keeps your API key for easy reinstall):
```
/plugin uninstall lej-pp-search
```

**Full cleanup** (nukes everything including the API key):
Just tell Claude "Uninstall lej-pp-search completely" and it'll handle the cleanup.

## License

MIT

## Author

[Limited Edition Jonathan](https://substack.com/@limitededitionjonathan), aka Jonathan Edwards, co-founder of [Aicred.ai](https://aicred.ai). An AI skills assessment and training platform.

---