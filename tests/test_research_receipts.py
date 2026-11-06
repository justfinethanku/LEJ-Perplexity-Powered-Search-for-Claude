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


class ResearchReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.home = self.project / 'home'
        self.home.mkdir()
        hooks = json.loads((PLUGIN / 'hooks/hooks.json').read_text())['hooks']
        self.command = hooks['PostToolUse'][0]['hooks'][0]['command']

    def curl(self, query, option='-d', *, messages=None, pretty=False):
        body = json.dumps({'messages': messages or [{'role': 'user', 'content': query}]},
                          indent=2 if pretty else None)
        argument = (option + shlex.quote(body) if option.endswith('=')
                    else option + ' ' + shlex.quote(body))
        return 'curl -s https://api.perplexity.ai/chat/completions ' + argument

    def save(self, command, *, response=None):
        if response is None:
            response = {
                'model': 'synthetic-model',
                'choices': [{'message': {'content': 'First line [1]\n\nSecond line [2].'}}],
                'citations': ['https://example.com/one', 'https://example.com/two'],
                'search_results': [
                    {'title': 'First source', 'url': 'https://example.com/one',
                     'snippet': 'Evidence one'},
                    {'title': 'Second source', 'url': 'https://example.com/two',
                     'snippet': 'Evidence two'},
                ],
                'usage': {'cost': {'total_cost': 0}},
            }
        event = {'tool_name': 'Bash', 'tool_input': {'command': command},
                 # PR #3 owns the modern Bash stdout and Agent response shapes.
                 'tool_response': json.dumps(response)}
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
        messages = [
            {'role': 'system', 'content': 'Initial instructions'},
            {'role': 'user', 'content': 'Earlier question'},
            {'role': 'assistant', 'content': 'Earlier answer'},
            {'role': 'user', 'content': 'Actual research question'},
            {'role': 'system', 'content': 'Formatting instructions'},
        ]
        self.assert_query(self.save(self.curl('', messages=messages)),
                          'Actual research question')

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
        request.write_text(json.dumps({'messages': [{'role': 'user', 'content': 'private query'}]}))
        command = ('curl https://api.perplexity.ai/chat/completions -d @request.json'
                   ' -H ' + shlex.quote('X-Audit: "content":"unrelated header"'))
        self.assert_query(self.save(command), 'perplexity-search')

    def test_unparseable_command_keeps_response_with_fallback_query(self):
        command = "curl https://api.perplexity.ai/chat/completions -d 'unterminated"
        self.assert_query(self.save(command), 'perplexity-search')

    def test_generated_request_is_not_executed_to_recover_metadata(self):
        command = 'curl https://api.perplexity.ai/chat/completions -d "$(touch injected)"'
        self.assert_query(self.save(command), 'perplexity-search')
        self.assertFalse((self.project / 'injected').exists())

    def test_non_message_json_and_multiple_bodies_keep_generic_receipt(self):
        for arguments in ("-d '[]'", "-d '{\"messages\":null}'", "-d '{}' -d '{}'",
                          "-d '{\"messages\":[{\"role\":\"system\",\"content\":\"not a query\"}]}'"):
            with self.subTest(arguments=arguments):
                for file in (self.project / '.perplexity-research').glob('*.md'):
                    file.unlink()
                self.assert_query(self.save('curl https://api.perplexity.ai/chat/completions ' + arguments),
                                  'perplexity-search')

    def test_response_receipt_preserves_answer_source_order_model_and_zero_cost(self):
        markdown = self.save(self.curl('Receipt question'))
        for value in ('**Model:** synthetic-model', '**Cost:** $0',
                      'First line [1]\n\nSecond line [2].',
                      '1. <https://example.com/one>\n2. <https://example.com/two>',
                      '### First source\n**URL:** https://example.com/one\n**Snippet:** Evidence one',
                      '### Second source\n**URL:** https://example.com/two\n**Snippet:** Evidence two'):
            self.assertIn(value, markdown)

    def test_missing_optional_metadata_still_saves_answer(self):
        markdown = self.save(self.curl('Minimal question'), response={
            'choices': [{'message': {'content': 'Minimal answer'}}],
        })
        for value in ('Minimal answer', '**Model:** unknown', '**Cost:** $unknown',
                      'No citations available.', 'No search results available.'):
            self.assertIn(value, markdown)


if __name__ == '__main__':
    unittest.main()
