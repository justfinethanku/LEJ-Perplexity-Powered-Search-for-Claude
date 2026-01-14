# Changelog

All notable changes to LEJ PP Search will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
