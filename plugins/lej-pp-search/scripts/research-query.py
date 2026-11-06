#!/usr/bin/env python3
"""Recover query metadata from literal curl JSON without executing shell input.

Only literal JSON is supported; variables and shell expressions are not
expanded. File references and ambiguous data arguments use a generic title.
"""

import json
import shlex
import sys


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
        if not isinstance(body, dict) or not isinstance(body.get('messages'), list):
            return fallback
        for message in reversed(body['messages']):
            if isinstance(message, dict) and message.get('role') == 'user':
                query = message.get('content')
                return query if isinstance(query, str) and query.strip() else fallback
    except (ValueError, StopIteration):
        pass
    return fallback


if __name__ == '__main__':
    print(research_query(sys.stdin.read()))
