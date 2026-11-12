"""Execute registered commands in a temporary project, without API calls."""

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest


PLUGIN = Path(__file__).resolve().parents[1] / 'plugins/lej-pp-search'
SYNTHETIC_KEY = 'synthetic-fleet-641-DoNotPrint-9f3c2a7b'


class HookLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'project'
        self.project.mkdir()
        self.home = self.root / 'home'
        (self.home / '.claude').mkdir(parents=True)
        # Copy the installed layout, including executable bits, rather than
        # bypassing hooks.json by invoking a script with bash explicitly.
        self.plugin = self.root / 'plugin cache [audit]'
        shutil.copytree(PLUGIN, self.plugin)
        self.hooks = json.loads((self.plugin / 'hooks/hooks.json').read_text())['hooks']
        self.research = self.project / '.perplexity-research'
        self.configure(redirect='true')

    def configure(self, redirect):
        self.write_settings({
            'environmentVariables': {
                'LEJ_AUTO_REDIRECT': redirect,
                'PERPLEXITY_API_KEY': 'synthetic-lifecycle-key',
            },
        })

    def write_settings(self, payload):
        (self.home / '.claude/settings.json').write_text(json.dumps(payload))

    def run_hook(self, event, payload=None, extra_env=None):
        command = self.hooks[event][0]['hooks'][0]['command']
        env = os.environ.copy()
        env['HOME'] = str(self.home)
        env['CLAUDE_PLUGIN_ROOT'] = str(self.plugin)
        # Never inherit a real credential into the hook under test.
        env.pop('PERPLEXITY_API_KEY', None)
        env.pop('LEJ_AUTO_REDIRECT', None)
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            ['bash', '-c', command], input=json.dumps(payload or {}),
            text=True, capture_output=True, cwd=self.project, timeout=10,
            env=env, umask=0o022,
        )

    def assert_secret_absent(self, result, secret):
        self.assertNotIn(secret, result.stdout)
        self.assertNotIn(secret, result.stderr)

    def assert_redirect_instructions(self, result, secret):
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('WebSearch is blocked', result.stderr)
        self.assertIn('https://api.perplexity.ai/v1/agent', result.stderr)
        self.assertIn('"effort": "fast"', result.stderr)
        self.assertIn('YOUR_QUERY_HERE', result.stderr)
        self.assertIn('${PERPLEXITY_API_KEY:-', result.stderr)
        self.assertIn('Do not print the API key', result.stderr)
        self.assertEqual(result.stdout, '')
        self.assert_secret_absent(result, secret)

    def response(self, answer='Lifecycle answer [1]'):
        return {
            'tool_name': 'Bash',
            'tool_input': {'command': '''curl https://api.perplexity.ai/v1/agent -d '{"effort":"fast","input":"lifecycle"}' '''},
            # Claude Code delivers Bash output as an object with stdout.
            'tool_response': {'stdout': json.dumps({
                'output': [
                    {'type': 'search_results', 'results': [
                        {'id': 1, 'url': 'https://example.com/lifecycle', 'title': 'L', 'snippet': 'S'}]},
                    {'type': 'message', 'content': [{'type': 'output_text', 'text': answer}]},
                ],
            }), 'stderr': '', 'interrupted': False},
        }

    def test_session_context_does_not_allocate_research_storage(self):
        result = self.run_hook('SessionStart')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Perplexity', result.stdout)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_session_context_survives_unusable_research_path(self):
        self.research.write_text('existing user file')
        result = self.run_hook('SessionStart')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Perplexity', result.stdout)
        self.assertEqual(self.research.read_text(), 'existing user file')

    def test_registered_redirect_honors_disabled_setting_in_spaced_install(self):
        self.configure(redirect='false')
        result = self.run_hook('PreToolUse')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['hookSpecificOutput']['permissionDecision'], 'allow')

    def test_registered_redirect_blocks_in_spaced_install(self):
        result = self.run_hook('PreToolUse')
        self.assert_redirect_instructions(result, 'synthetic-lifecycle-key')

    def test_synthetic_key_stays_out_of_hook_output(self):
        """FLEET-641: an expanding heredoc must not echo a configured key."""
        cases = (
            ('settings env', {'env': {'PERPLEXITY_API_KEY': SYNTHETIC_KEY}}, {}),
            ('legacy settings', {'environmentVariables': {'PERPLEXITY_API_KEY': SYNTHETIC_KEY}}, {}),
            ('process environment', {}, {'PERPLEXITY_API_KEY': SYNTHETIC_KEY}),
            ('all sources', {
                'env': {'PERPLEXITY_API_KEY': SYNTHETIC_KEY},
                'environmentVariables': {'PERPLEXITY_API_KEY': SYNTHETIC_KEY},
            }, {'PERPLEXITY_API_KEY': SYNTHETIC_KEY}),
        )
        for name, settings, extra in cases:
            with self.subTest(name=name):
                self.write_settings(settings)
                result = self.run_hook('PreToolUse', extra_env=extra)
                self.assert_redirect_instructions(result, SYNTHETIC_KEY)

    def test_redirect_disable_does_not_print_synthetic_key(self):
        self.write_settings({
            'env': {
                'LEJ_AUTO_REDIRECT': 'false',
                'PERPLEXITY_API_KEY': SYNTHETIC_KEY,
            },
        })
        result = self.run_hook('PreToolUse', extra_env={'PERPLEXITY_API_KEY': SYNTHETIC_KEY})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['hookSpecificOutput']['permissionDecision'], 'allow')
        self.assert_secret_absent(result, SYNTHETIC_KEY)

        self.write_settings({'environmentVariables': {'PERPLEXITY_API_KEY': SYNTHETIC_KEY}})
        result = self.run_hook('PreToolUse', extra_env={'LEJ_AUTO_REDIRECT': 'false'})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['hookSpecificOutput']['permissionDecision'], 'allow')
        self.assert_secret_absent(result, SYNTHETIC_KEY)

    def test_full_lifecycle_saves_once_with_private_directory(self):
        self.assert_private_lifecycle()

    def test_full_lifecycle_private_directory_without_install_path_spaces(self):
        plain_path = self.root / 'plugin'
        self.plugin.rename(plain_path)
        self.plugin = plain_path
        self.assert_private_lifecycle()

    def assert_private_lifecycle(self):
        self.assertEqual(self.run_hook('SessionStart').returncode, 0)
        result = self.run_hook('PostToolUse', self.response())
        self.assertEqual(result.returncode, 0, result.stderr)
        files = list(self.research.glob('*.md'))
        self.assertEqual(len(files), 1)
        self.assertIn('Lifecycle answer [1]', files[0].read_text())
        self.assertIn('https://example.com/lifecycle', files[0].read_text())
        self.assertEqual(stat.S_IMODE(self.research.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(files[0].stat().st_mode), 0o600)
        self.assertIn(str(files[0].relative_to(self.project)), result.stderr)

    def test_unsuccessful_search_leaves_no_research_directory(self):
        self.assertEqual(self.run_hook('SessionStart').returncode, 0)
        event = self.response()
        event['tool_response'] = '{"error":"synthetic failure"}'
        result = self.run_hook('PostToolUse', event)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.research.exists())
        self.assertNotIn('Research saved', result.stderr)

    def test_manual_recovery_uses_private_writer_in_spaced_install(self):
        self.assertEqual(self.run_hook('SessionStart').returncode, 0)
        content = '# Recovered query\n\nAnswer [1]\n\n1. <https://example.com/source>\n'
        result = subprocess.run(
            ['python3', str(self.plugin / 'scripts/write-research.py'), 'recovered-query'],
            input=content, text=True, capture_output=True, cwd=self.project,
            timeout=10, umask=0o022,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        files = list(self.research.glob('*.md'))
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].read_text(), content)
        self.assertEqual(stat.S_IMODE(self.research.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(files[0].stat().st_mode), 0o600)


if __name__ == '__main__':
    unittest.main()
