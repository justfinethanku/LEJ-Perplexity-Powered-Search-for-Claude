# Changelog

All notable changes to LEJ PP Search will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.4.0] - 2026-10-18

### Changed

- **Migrated to Perplexity's Agent API**: All calls now go to `/v1/agent` with presets (`fast`, `low`, `medium`, `high`, `xhigh`). Sonar Chat Completions (`/chat/completions`) was retired on September 27, 2026 and returns `403 agent_api_migration_required`
- Default is now the `fast` preset (replaces `sonar-pro`). Mapping: `sonar`/`sonar-pro` → `fast`, `sonar-reasoning-pro` → `low`, `sonar-deep-research` → `high`
- Search options moved onto the `web_search` tool: recency and domain filters go in `filters`, `search_context_size` is replaced by `max_results` and token budgets, `return_images` by the `image_search` tool
- API key and `LEJ_AUTO_REDIRECT` are now stored under `env` in settings.json, which Claude Code actually loads. Scripts still read the legacy `environmentVariables` location
- Help command describes presets instead of the old `perplexity_*` MCP tools

### Fixed

- Auto-save hook never saved anything: it read `tool_response` as a string, but Bash tool responses are objects with a `stdout` field
- Auto-save hook parses the Agent API response shape (`output[]` message and `search_results` items) and records the preset used

## [2.3.0] - 2025-01-14

### Added

- **Automatic Research Saving**: PostToolUse hook now automatically saves every Perplexity API response to `.perplexity-research/`
- New `save-perplexity-result.sh` script parses Bash command output and saves results as formatted markdown
- Research is saved with timestamp, query, model, cost, answer, citations, and search results
- No longer relies on Claude remembering to save - it's enforced by hook

### Changed

- Research persistence is now guaranteed, not optional
- Hook receives tool response via stdin JSON and filters for Perplexity API calls only

## [2.2.1] - 2025-01-14

### Fixed

- Research folder `.perplexity-research/` is now auto-created on session start via SessionStart hook
- Previously required Claude to manually create the folder during searches

## [2.2.0] - 2025-01-14

### Added

- **Research Persistence**: Every Perplexity search is now saved to `.perplexity-research/` as a markdown file
- Saved files include: query, model, date, cost, full answer, citations, and search results
- Research survives context compaction and can be referenced later without re-searching

## [2.1.0] - 2025-01-14

### Added

- Full parameter documentation for Perplexity API
- `web_search_options.search_context_size` support (low/medium/high)
- `search_recency_filter` support (day/week/month/year)
- `return_images` support for visual queries
- `reasoning_effort` support for sonar-reasoning-pro model
- Parameter Selection Guide for different query types
- Example calls for each use case
- Benchmark comparison: Perplexity vs WebSearch (5x faster, better source freshness)

### Changed

- Updated SKILL.md with comprehensive parameter guidance
- Added cost breakdowns for each context size level
- Updated README with benchmark results

## [2.0.0] - 2025-01-14

### Changed

- **Breaking**: Removed MCP server dependency - now uses direct Perplexity API calls via curl
- Simplified architecture: no more `${PERPLEXITY_API_KEY}` interpolation issues
- API key read directly from `~/.claude/settings.json` using `jq`
- Updated all skill documentation with exact curl commands
- Hook now provides curl command template when blocking WebSearch

### Removed

- `.mcp.json` - No longer needed since we're not using an MCP server
- MCP tool references from `allowed-tools` in SKILL.md

### Fixed

- API key not being passed to MCP server (env var interpolation didn't work for plugin MCP servers)
- Tool naming mismatch (`mcp__perplexity__*` vs `mcp__plugin_lej-pp-search_perplexity__*`)

## [1.0.0] - 2025-01-14

### Added

- Initial release
- Perplexity MCP server integration with 4 tools:
  - `perplexity_search` - Fast URL/link retrieval
  - `perplexity_ask` - Quick Q&A with sonar-pro
  - `perplexity_research` - Deep analysis with sonar-deep-research
  - `perplexity_reason` - Logical analysis with sonar-reasoning-pro
- WebSearch blocking hook with Perplexity redirect
- Configurable auto-redirect (tell Claude to enable/disable)
- SessionStart hook for automatic context injection
- Skill with tool selection guidance
- Post-installation welcome message
- `/lej-pp-search` command for usage info
- Full uninstall support with API key cleanup
- Documentation for all tools
