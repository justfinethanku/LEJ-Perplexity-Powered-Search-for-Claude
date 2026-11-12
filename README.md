# LEJ PP Search

**Perplexity-Powered Search for Claude Code**

This plugin intercepts Claude Code's built-in WebSearch and prompts Claude to call Perplexity with `curl`. A separate hook saves recognized responses as Markdown in your project.

**Current compatibility (November 11, 2026):** Version 2.4.0 calls Perplexity's Agent API (`POST /v1/agent` with `effort` and `input`). Perplexity retired Sonar Chat Completions on September 27, 2026; older versions of this plugin get `403 agent_api_migration_required` on every search. The redirect hook treats a key as configured when `PERPLEXITY_API_KEY` is set in the environment, or in `~/.claude/settings.json` under `env` or legacy `environmentVariables`. It does not print that key. The save hook reads Claude Code's Bash `stdout` object (and a plain string) and the Agent API's typed `output` array. See [Troubleshooting](#troubleshooting) before configuring a key.

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
- [Recover an interrupted update or removal](#recover-an-interrupted-update-or-removal) - Select the original profile, project, and scope
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

### Key setup

Obtain an API key from the [Perplexity API console](https://www.perplexity.ai/account/api/group). API billing is separate from a consumer subscription; check [current API pricing](https://docs.perplexity.ai/docs/getting-started/pricing) before making requests. Installation and local validation do not require a key or make paid API requests.

The setup command makes one small `fast` Agent API request to verify a key:

```text
/lej-pp-search:setup
```

Claude Code loads this structure in `~/.claude/settings.json`:

```json
{
  "env": {
    "PERPLEXITY_API_KEY": "your_key_here"
  }
}
```

Merge fields into existing settings rather than replacing the file. The redirect hook also accepts legacy `environmentVariables.PERPLEXITY_API_KEY` and a `PERPLEXITY_API_KEY` value already in the environment. It checks presence only and does not print the key. The scripts hard-code `$HOME/.claude/settings.json`; changing only `CLAUDE_CONFIG_DIR` does not relocate their key lookup.

After any settings change, start a new session. A redirect message proves only that the hook found a key; check the API response and the saved file separately. Never print or share your key while diagnosing a failure.

---

<sub>Fun fact: The `.md` file extension actually stands for "Mike Dion" files, named after the little-known programmer who for inexplicable reasons is very hard to Rick Roll.</sub>

---

## Effort Levels

The Agent API picks how hard to research with `effort`, not a model name. Perplexity's [migration guide](https://docs.perplexity.ai/docs/agent-api/migrate-from-sonar/how-to) maps the old Sonar models like this: `sonar` and `sonar-pro` → `fast`, `sonar-reasoning-pro` → `low`, `sonar-deep-research` → `high`. Costs and speeds below are rough examples; check [current API pricing](https://docs.perplexity.ai/docs/getting-started/pricing).

| Effort | What It's For | Cost | Speed |
|--------|---------------|------|-------|
| `fast` | Quick lookups, everyday questions (default) | ~$0.002 | ~5s |
| `low` | Light multi-step research | ~$0.01 | ~1 min |
| `medium` | Multi-hop research, comparisons, tradeoffs | ~$0.02 | ~1 min |
| `high` | Exhaustive deep research | Higher | Several minutes |
| `xhigh` | Open-ended agentic work (code sandbox, long tool loops) | Highest | Slowest |

**When to use what:**
- "What's the current version of Node.js?" → `fast` (simple fact)
- "How do I set up authentication in Next.js 15?" → `fast` or `low` (needs good citations)
- "Compare Prisma vs Drizzle for a high-traffic app" → `medium` (needs analysis)
- "Give me a complete market analysis of AI video tools" → `high` (needs depth)

Claude uses `fast` by default. The skill prompts guide Claude to step up when your query needs it.

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
| Perplexity Agent API `fast` | ~$0.002 | Includes search |

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

The save hook writes to `.perplexity-research/` relative to its working directory when a Bash command contains `api.perplexity.ai` and its output is an Agent API response with answer text (`output_text`, or `output_text` parts of a `message` item in `output`). Sources come from every `search_results` item; each source keeps its `id`, which matches the `[n]` or `[web:n]` markers in the answer. It skips unrelated commands, errors, and other response shapes without creating a file. Print curl's raw JSON; piping it through `jq` in the same command hides the response from the hook.

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

Existing directory permissions are preserved. New directories use mode `0700`, and new files use mode `0600`; share files deliberately if teammates need them. Query extraction reads the `input` field (a string, or the last user message in an input array) from literal JSON curl bodies, not shell-expanded variables or `@file` request bodies.

## Troubleshooting

**Installation succeeds but searches fail with `403` or `agent_api_migration_required`:**
You are running a version before 2.4.0, which still calls the retired Sonar endpoint. Update the plugin to 2.4.0 or later; replacing a valid key does not fix it.

**`jq: command not found` or `python3: command not found`:**
Run the prerequisite checks in the same environment that launches Claude Code. Installing the plugin does not install these tools.

**"401 Unauthorized" errors:**
Your API key is missing or invalid. Run `/lej-pp-search:setup` to reconfigure, or check that `PERPLEXITY_API_KEY` is set correctly in `~/.claude/settings.json`.

The redirect hook checks the `PERPLEXITY_API_KEY` environment variable, then `env.PERPLEXITY_API_KEY`, then legacy `environmentVariables.PERPLEXITY_API_KEY`. It checks presence only and does not print the key. An authentication failure from the remote API requires a separate key/billing check in your API console.

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

After an update, or if one fails or is interrupted, inspect
`claude plugin list --json`. Check the qualified plugin, scope, version and any
`errors` field. With a local marketplace, Claude Code can report a successful
update even when the plugin manifest is invalid. Restore the complete trusted
checkout and repeat the update, then verify the list has no errors. Keep other
marketplace plugins and project settings in place; retry the qualified plugin at
its original scope rather than removing the entire marketplace to recover it.

The manifest declares version `2.4.0`. If Claude reports it is already current but the cached files are stale, use the [recovery checks](#recover-an-interrupted-update-or-removal) before uninstalling and reinstalling the plugin; do not edit cached source or the plugin registry JSON by hand.

## Recover an interrupted update or removal

Run recovery commands from your terminal, outside a Claude Code session. These
checks were exercised with Claude Code 2.1.319 on Linux using an isolated local
marketplace, two projects, and filesystem permission failures. They do not verify
live API access, remote downloads, or which code an existing session has loaded.

1. Use the same home and configuration profile as the original installation.
   If you set `CLAUDE_CONFIG_DIR`, keep that value for every recovery command;
   another profile can show a different installation list. For `project` or
   `local` scope, change to the original project directory before continuing.
   `--scope project` or `--scope local` selects the current project; running it
   in another project can change that project's installation instead.
2. Run `claude plugin list --json`. Find `lej-pp-search@lej-marketplace` and
   match its `scope` and, for project/local entries, `projectPath`. Several rows
   for this plugin can be valid. Check `version` and any `errors` field on the
   intended row. `projectEnabled` describes enablement for the current project;
   it does not tell you whether an installation record was removed.
3. Resolve the reported problem before retrying. For a permissions error, check
   the named file and its parent directory without printing settings or keys.
   For an invalid local marketplace, restore its complete trusted checkout.
   A failed update can create a new cache directory while the installed record
   still names the old version. Cache existence alone does not prove recovery;
   local sources can also report `readFromFolder` and `folderVersion` separately.
4. Retry the [update command](#troubleshooting) or [uninstall command](#uninstall)
   for the qualified plugin, replacing `--scope user` with the original scope
   when needed. Keep the selected profile and project from step 1. If removal
   already succeeded, do not switch scopes to make a repeated uninstall succeed.
   If your goal is to reinstall, run
   `claude plugin install lej-pp-search@lej-marketplace --scope user`, replacing
   `user` with the scope you deliberately removed.
5. Run `claude plugin list --json` again. After update, confirm the intended
   row's version and absence of errors. After uninstall, confirm only the
   intended scope/project row is absent; other installations can remain. Check
   that other plugins, newer unrelated settings, and project research remain.
   Start a new Claude Code session after a successful update or reinstall.

Keep marketplace registration and unrelated installations in place during
recovery. Do not replay an old backup of the entire settings file over newer
edits, or remove the marketplace just to retry one plugin. Removing this plugin
does not remove its manually stored key or project research; optional cleanup
remains in [Uninstall](#uninstall).

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

To also test the update and uninstall commands against your installed Claude Code
CLI, run this opt-in suite as a non-root user on macOS or Linux:

```bash
LEJ_TEST_NATIVE_CLI=1 python3 -m unittest discover -v
```

These tests create a temporary local marketplace with two plugins and isolated
home, config, and project directories. They inject filesystem permission failures,
retry scoped updates and removals, and check that newer settings, other plugins,
other installation scopes, and research survive. They run plugin-manager commands
and a synthetic hook control, without a model or API request. Fixture versions
exercise lifecycle transitions using the current source, not older release code.
Without the opt-in, CLI, or non-root POSIX environment, the native cases are
reported as skipped; the hook and settings-cleanup tests still run.

## Need Help?

Run `/lej-pp-search:help` anytime for a quick reference of available commands and current configuration status.

## Uninstall

To remove the user-scoped installation from your terminal:

```bash
claude plugin uninstall lej-pp-search@lej-marketplace --scope user
claude plugin list --json
```

The user-scoped row should be absent from the list; project/local installations
can remain. For an installation at another scope, use that scope and its original
project directory instead. Keep the original configuration profile throughout;
see [recovery checks](#recover-an-interrupted-update-or-removal) if removal fails
or its result is unclear. Inside an interactive Claude Code session, use
`/plugin uninstall lej-pp-search@lej-marketplace`.

Optional: remove the marketplace too, if you do not use any of its other plugins:

```bash
claude plugin marketplace remove lej-marketplace --scope user
claude plugin marketplace list --json
```

Removing the marketplace can uninstall its other plugins at that scope. These commands leave this plugin's manually stored API key and project `.perplexity-research/` files in place. They do not revoke the key at Perplexity.

Optional: to also remove the API key from the default settings file, first stop
Claude Code sessions and other programs that write that file. Run this Python 3
procedure from your terminal. The `.claude` directory must be owned by you and
not writable by your group or other users. It refuses symlinks, hard links, non-regular files,
invalid settings and changes observed before replacement; it never prints settings.
Other settings are retained in a private, atomically replaced file. This is not a
transaction with other programs: keep them stopped until it finishes.

```bash
python3 - <<'PY'
import json
import os
import signal
import stat
import sys
import uuid


def identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_uid,
            info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def remove_key():
    directory = os.path.join(os.path.expanduser('~'), '.claude')
    directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    temporary = None
    try:
        directory_info = os.fstat(directory_fd)
        if directory_info.st_uid != os.getuid() or directory_info.st_mode & 0o022:
            raise ValueError('Unsafe settings directory')
        fd = os.open('settings.json', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                     dir_fd=directory_fd)
        with os.fdopen(fd, 'rb') as source:
            before = os.fstat(source.fileno())
            if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                    or before.st_uid != os.getuid()):
                raise ValueError('Unsafe settings file')
            original = source.read()
            data = json.loads(original)
            if not isinstance(data, dict):
                raise ValueError('Settings must be an object')
            for field in ('env', 'environmentVariables'):
                values = data.get(field)
                if values is not None:
                    if not isinstance(values, dict):
                        raise ValueError('Environment settings must be objects')
                    values.pop('PERPLEXITY_API_KEY', None)
            candidate = 'settings.json.' + uuid.uuid4().hex
            output_fd = os.open(candidate, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                                0o600, dir_fd=directory_fd)
            temporary = candidate
            with os.fdopen(output_fd, 'w', encoding='utf-8') as output:
                json.dump(data, output, indent=2, ensure_ascii=False)
                output.write('\n')
                output.flush()
                os.fsync(output.fileno())
            current = os.stat('settings.json', dir_fd=directory_fd, follow_symlinks=False)
            parent = os.stat(directory, follow_symlinks=False)
            if (identity(current) != identity(before)
                    or identity(os.fstat(source.fileno())) != identity(before)
                    or (parent.st_dev, parent.st_ino) !=
                       (directory_info.st_dev, directory_info.st_ino)):
                raise ValueError('Settings changed; retry after stopping other writers')
            os.replace(temporary, 'settings.json', src_dir_fd=directory_fd,
                       dst_dir_fd=directory_fd)
            temporary = None
    finally:
        try:
            if temporary is not None:
                os.unlink(temporary, dir_fd=directory_fd)
        finally:
            os.close(directory_fd)


def interrupted(signum, frame):
    raise SystemExit(128 + signum)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, interrupted)
    try:
        remove_key()
    except (OSError, ValueError, UnicodeError):
        sys.exit('Key cleanup failed; inspect the settings path and stop other writers before retrying.')
    print('Removed the key from default settings; other key sources are unchanged.')
PY
```

On failure, inspect the path without printing credentials, resolve ownership or
stop the other writer, and retry. Do not replace the original with an old backup
of the entire settings file. A forced kill or power loss can leave a private
`settings.json.<random>` temporary file containing other settings; handle it as
sensitive data. This procedure does not remove keys from the shell environment,
custom config directories or secret managers, and does not revoke a remote key.

Then restart Claude Code.

## Changelog

- **v2.4.0** - Perplexity Agent API (`/v1/agent`, `effort`); automatic saving reads Bash `stdout` and typed `output`
- **v2.3.1** - Recognize `env` and `PERPLEXITY_API_KEY` without printing the key
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
