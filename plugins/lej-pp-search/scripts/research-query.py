#!/usr/bin/env python3
"""Recover query metadata from literal curl JSON without executing shell input.

The query is the Agent API `input` field: a string, or the last user message
in an input-item array. Only literal JSON is supported; variables and shell
expressions are not expanded. File references and ambiguous data arguments use a generic title.
"""

import json
import shlex
import sys


def message_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [part.get('text') for part in content
                 if isinstance(part, dict) and part.get('type') == 'input_text'
                 and isinstance(part.get('text'), str)]
        return '\n'.join(parts) if parts else None
    return None


def agent_input_query(value):
    """Agent API input: a string, or items whose last user message is the query."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        for item in reversed(value):
            if (isinstance(item, dict) and item.get('role') == 'user'
                    and item.get('type', 'message') == 'message'):
                return message_text(item.get('content'))
    return None


def research_query(command):
    fallback = 'perplexity-search'
    try:
        arguments = iter(shlex.split(command))
        bodies = []
        options = ('--data', '--data-raw', '--data-binary', '--json')
        for argument in arguments:
            if argument in ('-d', *options):
                bodies.append(next(arguments))
            elif argument.startswith('-d') and len(argument) > 2:
                bodies.append(argument[2:])
            else:
                for option in options:
                    if argument.startswith(option + '='):
                        bodies.append(argument[len(option) + 1:])
                        break
        if len(bodies) != 1:
            return fallback
        body = json.loads(bodies[0])
        if not isinstance(body, dict):
            return fallback
        query = agent_input_query(body.get('input'))
        return query if query and query.strip() else fallback
    except (ValueError, StopIteration):
        pass
    return fallback


if __name__ == '__main__':
    print(research_query(sys.stdin.read()))
