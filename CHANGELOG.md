# Changelog

All notable changes to LEJ PP Search will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
