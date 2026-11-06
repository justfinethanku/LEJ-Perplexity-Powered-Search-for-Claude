#!/usr/bin/env python3
"""Render a legacy Perplexity receipt without starting a process per source.

The Bash entrypoint keeps the inexpensive unrelated-command filter. API schema
migration is separate: this renderer accepts the existing string response.
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
    if not isinstance(response, str):
        return None
    try:
        response = json.loads(response)
        answer = response['choices'][0]['message']['content']
    except (ValueError, KeyError, IndexError, TypeError):
        return None
    if not isinstance(answer, str):
        return None

    query = import_module('research-query').research_query(command)
    model = field(response, 'model', 'unknown')
    usage = response.get('usage') or {}
    cost = field(usage.get('cost') or {}, 'total_cost', 'unknown')
    now = datetime.now()
    # Keep the existing portable ASCII filename alphabet and 50-character slug.
    slug = re.sub(r'[^a-z0-9-]', '', query.lower().replace(' ', '-'))[:50]
    prefix = now.strftime('%Y-%m-%d-%H-%M-%S-') + slug

    citations = '\n'.join(
        f'{i}. <{url}>'
        for i, url in enumerate((url for url in response.get('citations') or [] if url), 1)
    )
    results = '\n\n'.join(
        f"### {field(result, 'title', 'Untitled')}\n"
        f"**URL:** {field(result, 'url', 'N/A')}\n"
        f"**Snippet:** {field(result, 'snippet', 'N/A')}"
        for result in response.get('search_results') or []
    )
    # Match the section spacing of existing saved receipts.
    citations = citations + '\n' if citations else 'No citations available.'
    results = results + '\n\n' if results else 'No search results available.'
    markdown = (
        f'# {query}\n\n**Query:** {query}\n**Model:** {model}\n'
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
