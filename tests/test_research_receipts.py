"""Exercise saved receipt contents through the installed PostToolUse command.

All requests and responses are synthetic. The curl command is hook input data;
it is never run, and HOME points at an empty temporary directory.
"""

import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest


PLUGIN = Path(__file__).resolve().parents[1] / 'plugins/lej-pp-search'


def message(text):
    return {'type': 'message', 'role': 'assistant', 'status': 'completed',
            'content': [{'type': 'output_text', 'text': text, 'annotations': []}]}


class ResearchReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.home = self.project / 'home'
        self.home.mkdir()
        hooks = json.loads((PLUGIN / 'hooks/hooks.json').read_text())['hooks']
        self.command = hooks['PostToolUse'][0]['hooks'][0]['command']

    def curl(self, query, option='-d', *, items=None, pretty=False):
        body = json.dumps({'effort': 'fast', 'input': items if items is not None else query},
                          indent=2 if pretty else None)
        argument = (option + shlex.quote(body) if option.endswith('=')
                    else option + ' ' + shlex.quote(body))
        return 'curl -s https://api.perplexity.ai/v1/agent ' + argument

    def save(self, command, *, response=None, as_string=False):
        if response is None:
            response = {
                'model': 'synthetic-model',
                'effort': 'fast@synthetic',
                'status': 'completed',
                'output': [
                    {'type': 'search_results', 'queries': ['q'], 'results': [
                        {'id': 1, 'title': 'First source', 'url': 'https://example.com/one',
                         'snippet': 'Evidence one'},
                        {'id': 2, 'title': 'Second source', 'url': 'https://example.com/two',
                         'snippet': 'Evidence two'},
                    ]},
                    message('First line [1]\n\nSecond line [2].'),
                ],
                'usage': {'cost': {'total_cost': 0}},
            }
        stdout = json.dumps(response)
        # Claude Code sends Bash output as an object; a bare string is also accepted.
        event = {'tool_name': 'Bash', 'tool_input': {'command': command},
                 'tool_response': stdout if as_string else
                 {'stdout': stdout, 'stderr': '', 'interrupted': False}}
        result = subprocess.run(
            ['bash', '-c', self.command], input=json.dumps(event),
            text=True, capture_output=True, cwd=self.project, timeout=10,
            env={**os.environ, 'HOME': str(self.home),
                 'CLAUDE_PLUGIN_ROOT': str(PLUGIN)},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        files = list((self.project / '.perplexity-research').glob('*.md'))
        self.assertEqual(len(files), 1, result.stderr)
        self.assertIn(str(files[0].relative_to(self.project)), result.stderr)
        return files[0].read_text()

    def assert_query(self, markdown, query):
        self.assertTrue(markdown.startswith('# ' + query + '\n\n'), markdown)
        self.assertIn('**Query:** ' + query + '\n**Model:**', markdown)

    def test_quoted_unicode_and_backslash_query_is_decoded_exactly(self):
        query = 'Compare "café" and 日本語 at C:\\tools'
        self.assert_query(self.save(self.curl(query)), query)

    def test_apostrophe_and_shell_metacharacters_remain_literal(self):
        query = "What's $(touch injected) `touch injected` ${HOME}?"
        self.assert_query(self.save(self.curl(query)), query)
        self.assertFalse((self.project / 'injected').exists())

    def test_escaped_newline_is_real_query_text(self):
        query = 'First question\nSecond question'
        self.assert_query(self.save(self.curl(query)), query)

    def test_last_user_message_is_used_instead_of_later_system_content(self):
        items = [
            {'type': 'message', 'role': 'system', 'content': 'Initial instructions'},
            {'type': 'message', 'role': 'user', 'content': 'Earlier question'},
            {'type': 'message', 'role': 'assistant', 'content': 'Earlier answer'},
            {'type': 'message', 'role': 'user', 'content': 'Actual research question'},
            {'type': 'message', 'role': 'system', 'content': 'Formatting instructions'},
        ]
        self.assert_query(self.save(self.curl('', items=items)),
                          'Actual research question')

    def test_input_text_parts_form_the_query(self):
        items = [{'type': 'message', 'role': 'user', 'content': [
            {'type': 'input_text', 'text': 'Part one'},
            {'type': 'input_image', 'image_url': 'https://example.com/x.png'},
            {'type': 'input_text', 'text': 'Part two'},
        ]}]
        self.assert_query(self.save(self.curl('', items=items)), 'Part one\nPart two')

    def test_header_content_does_not_replace_request_query(self):
        command = self.curl('Actual question') + ' -H ' + shlex.quote('X-Audit: "content":"header"')
        self.assert_query(self.save(command), 'Actual question')

    def test_pretty_printed_request_json_is_supported(self):
        self.assert_query(self.save(self.curl('Pretty "question"', pretty=True)),
                          'Pretty "question"')

    def test_literal_curl_data_options_are_supported(self):
        # Clear the prior subcase even when its assertion failed.
        for option in ('-d', '--data', '--data-raw', '--data-binary', '--json', '--data='):
            with self.subTest(option=option):
                for file in (self.project / '.perplexity-research').glob('*.md'):
                    file.unlink()
                self.assert_query(self.save(self.curl('An "exact" query', option)),
                                  'An "exact" query')

    def test_file_request_is_not_read_or_invented_from_other_command_text(self):
        request = self.project / 'request.json'
        request.write_text(json.dumps({'effort': 'fast', 'input': 'private query'}))
        command = ('curl https://api.perplexity.ai/v1/agent -d @request.json'
                   ' -H ' + shlex.quote('X-Audit: "content":"unrelated header"'))
        self.assert_query(self.save(command), 'perplexity-search')

    def test_unparseable_command_keeps_response_with_fallback_query(self):
        command = "curl https://api.perplexity.ai/v1/agent -d 'unterminated"
        self.assert_query(self.save(command), 'perplexity-search')

    def test_generated_request_is_not_executed_to_recover_metadata(self):
        command = 'curl https://api.perplexity.ai/v1/agent -d "$(touch injected)"'
        self.assert_query(self.save(command), 'perplexity-search')
        self.assertFalse((self.project / 'injected').exists())

    def test_non_message_json_and_multiple_bodies_keep_generic_receipt(self):
        for arguments in ("-d '[]'", "-d '{\"input\":null}'", "-d '{\"input\":\"  \"}'", "-d '{}' -d '{}'",
                          "-d '{\"input\":[{\"role\":\"system\",\"content\":\"not a query\"}]}'"):
            with self.subTest(arguments=arguments):
                for file in (self.project / '.perplexity-research').glob('*.md'):
                    file.unlink()
                self.assert_query(self.save('curl https://api.perplexity.ai/v1/agent ' + arguments),
                                  'perplexity-search')

    def test_response_receipt_preserves_answer_source_order_model_and_zero_cost(self):
        markdown = self.save(self.curl('Receipt question'))
        for value in ('**Model:** synthetic-model', '**Effort:** fast@synthetic', '**Cost:** $0',
                      'First line [1]\n\nSecond line [2].',
                      '- [1] <https://example.com/one>\n- [2] <https://example.com/two>',
                      '### First source\n**URL:** https://example.com/one\n**Snippet:** Evidence one',
                      '### Second source\n**URL:** https://example.com/two\n**Snippet:** Evidence two'):
            self.assertIn(value, markdown)

    def test_large_receipt_keeps_every_source_in_order_and_literal(self):
        sources = [
            {'title': f'Source {i}', 'url': f'https://example.com/{i}',
             'snippet': f'Evidence {i}: café "quoted"\nnext line $(touch injected)'}
            for i in range(100)
        ]
        for i, source in enumerate(sources, 1):
            source['id'] = i
        # Split across two search_results items, as multi-step efforts return them.
        markdown = self.save(self.curl('Many sources'), response={'output': [
            {'type': 'search_results', 'results': sources[:50]},
            {'type': 'fetch_url_results', 'contents': []},
            {'type': 'search_results', 'results': sources[50:]},
            message('Large answer ' * 1000),
        ]})
        previous = -1
        for i, source in enumerate(sources):
            self.assertIn(f"- [{i + 1}] <{source['url']}>", markdown)
            expected = (f"### {source['title']}\n**URL:** {source['url']}\n"
                        f"**Snippet:** {source['snippet']}")
            position = markdown.index(expected)
            self.assertGreater(position, previous)
            previous = position
        self.assertEqual(markdown.count('### Source '), 100)
        self.assertIn('Large answer ' * 1000, markdown)
        self.assertFalse((self.project / 'injected').exists())

    def test_missing_optional_metadata_still_saves_answer(self):
        markdown = self.save(self.curl('Minimal question'),
                             response={'output': [message('Minimal answer')]})
        for value in ('Minimal answer', '**Model:** unknown', '**Effort:** unknown', '**Cost:** $unknown',
                      'No citations available.', 'No search results available.'):
            self.assertIn(value, markdown)

    def test_legacy_string_tool_response_is_still_saved(self):
        markdown = self.save(self.curl('String response'), as_string=True)
        self.assertIn('First line [1]', markdown)

    def test_top_level_output_text_is_preferred(self):
        markdown = self.save(self.curl('Output text'), response={
            'output_text': 'Top-level answer [web:3]',
            'output': [message('Part answer'),
                       {'type': 'search_results', 'results': [
                           {'id': 3, 'url': 'https://example.com/three', 'title': 'T', 'snippet': 'S'}]}],
        })
        self.assertIn('Top-level answer [web:3]', markdown)
        self.assertNotIn('Part answer', markdown)
        self.assertIn('- [3] <https://example.com/three>', markdown)

    def test_multiple_message_parts_are_joined(self):
        markdown = self.save(self.curl('Parts'), response={'output': [
            {'type': 'message', 'content': [
                {'type': 'output_text', 'text': 'Alpha'}, {'type': 'output_text', 'text': 'Beta'}]},
        ]})
        self.assertIn('Alpha\n\nBeta', markdown)

    def assert_not_saved(self, tool_response):
        event = {'tool_name': 'Bash', 'tool_input': {'command': self.curl('ignored')},
                 'tool_response': tool_response}
        result = subprocess.run(
            ['bash', '-c', self.command], input=json.dumps(event),
            text=True, capture_output=True, cwd=self.project, timeout=10,
            env={**os.environ, 'HOME': str(self.home), 'CLAUDE_PLUGIN_ROOT': str(PLUGIN)},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.project / '.perplexity-research').exists())

    def test_error_legacy_and_empty_responses_are_not_saved(self):
        for response in (
            {'stdout': json.dumps({'error': {'code': 'agent_api_migration_required',
                                             'message': 'Sonar retired'}})},
            {'stdout': json.dumps({'choices': [{'message': {'content': 'old Sonar'}}]})},
            {'stdout': json.dumps({'status': 'failed', 'output': []})},
            {'stdout': json.dumps({'output': [{'type': 'search_results', 'results': []}]})},
            {'stdout': json.dumps({'output': [{'type': 'message', 'content': 5},
                                              {'type': 'search_results', 'results': 7}]})},
            {'stdout': 'not json'},
            {'stdout': None},
            {'stderr': 'curl failed'},
            None,
        ):
            with self.subTest(response=response):
                self.assert_not_saved(response)


if __name__ == '__main__':
    unittest.main()
