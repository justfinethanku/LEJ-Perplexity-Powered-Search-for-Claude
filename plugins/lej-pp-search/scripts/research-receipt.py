#!/usr/bin/env python3
"""Render a Perplexity Agent API receipt without starting a process per source.

The Bash entrypoint keeps the inexpensive unrelated-command filter. Claude Code
passes Bash output as an object with `stdout`; a plain string is also accepted.
The answer is `output_text`, or the `output_text` parts of `message` items, and
sources come from every `search_results` item in the typed `output` array.
"""

from datetime import datetime
from importlib import import_module
import json
import re
import sys


def field(record, key, default):
    value = record.get(key)
    return default if value is None or value is False else value


def receipt(event):
    command = event.get('tool_input', {}).get('command', '')
    response = event.get('tool_response')
    if not isinstance(command, str) or 'api.perplexity.ai' not in command:
        return None
    if isinstance(response, dict):
        response = response.get('stdout')
    if not isinstance(response, str):
        return None
    try:
        response = json.loads(response)
    except ValueError:
        return None
    if not isinstance(response, dict) or not isinstance(response.get('output'), list):
        return None
    items = [item for item in response['output'] if isinstance(item, dict)]
    answer = response.get('output_text')
    if not isinstance(answer, str) or not answer:
        answer = '\n\n'.join(
            part['text']
            for item in items if item.get('type') == 'message'
            for part in item.get('content') or []
            if isinstance(part, dict) and part.get('type') == 'output_text'
            and isinstance(part.get('text'), str)
        )
    if not answer:
        return None
    sources = [
        result
        for item in items if item.get('type') == 'search_results'
        for result in item.get('results') or [] if isinstance(result, dict)
    ]

    query = import_module('research-query').research_query(command)
    model = field(response, 'model', 'unknown')
    effort = field(response, 'effort', 'unknown')
    usage = response.get('usage') or {}
    cost = field(usage.get('cost') or {}, 'total_cost', 'unknown')
    now = datetime.now()
    # Keep the existing portable ASCII filename alphabet and 50-character slug.
    slug = re.sub(r'[^a-z0-9-]', '', query.lower().replace(' ', '-'))[:50]
    prefix = now.strftime('%Y-%m-%d-%H-%M-%S-') + slug

    # Agent API result ids match the [n] / [web:n] markers in the answer.
    citations = '\n'.join(
        f"{field(result, 'id', i)}. <{result['url']}>"
        for i, result in enumerate((r for r in sources if r.get('url')), 1)
    )
    results = '\n\n'.join(
        f"### {field(result, 'title', 'Untitled')}\n"
        f"**URL:** {field(result, 'url', 'N/A')}\n"
        f"**Snippet:** {field(result, 'snippet', 'N/A')}"
        for result in sources
    )
    # Match the section spacing of existing saved receipts.
    citations = citations + '\n' if citations else 'No citations available.'
    results = results + '\n\n' if results else 'No search results available.'
    markdown = (
        f'# {query}\n\n**Query:** {query}\n**Model:** {model}\n**Effort:** {effort}\n'
        f"**Date:** {now.strftime('%Y-%m-%d %H:%M:%S')}\n**Cost:** ${cost}\n\n"
        f'---\n\n## Answer\n\n{answer}\n\n---\n\n## Citations\n\n'
        f'{citations}\n\n---\n\n## Search Results\n\n{results}\n\n---\n\n'
        '*Saved automatically by LEJ PP Search*\n'
    )
    return prefix, markdown


def main():
    result = receipt(json.load(sys.stdin))
    if result is None:
        return 0
    try:
        filename = import_module('write-research').save_research(*result)
    except (OSError, ValueError):
        print('Research not saved: unsafe or inaccessible research path.', file=sys.stderr)
        return 1
    print(f'Research saved to {filename}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
