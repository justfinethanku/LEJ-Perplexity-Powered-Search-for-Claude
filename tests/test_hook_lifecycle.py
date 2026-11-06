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
        (self.home / '.claude/settings.json').write_text(json.dumps({
            'environmentVariables': {
                'LEJ_AUTO_REDIRECT': redirect,
                'PERPLEXITY_API_KEY': 'synthetic-lifecycle-key',
            },
        }))

    def run_hook(self, event, payload=None):
        command = self.hooks[event][0]['hooks'][0]['command']
        return subprocess.run(
            ['bash', '-c', command], input=json.dumps(payload or {}),
            text=True, capture_output=True, cwd=self.project, timeout=10,
            env={**os.environ, 'HOME': str(self.home),
                 'CLAUDE_PLUGIN_ROOT': str(self.plugin)}, umask=0o022,
        )

    def response(self, answer='Lifecycle answer [1]'):
        return {
            'tool_name': 'Bash',
            'tool_input': {'command': '''curl https://api.perplexity.ai/chat/completions -d '{"messages":[{"role":"user","content":"lifecycle"}]}' '''},
            # The current parser accepts a legacy string. PR #3 separately
            # owns the Bash stdout object and Agent API migration.
            'tool_response': json.dumps({
                'choices': [{'message': {'content': answer}}],
                'citations': ['https://example.com/lifecycle'],
            }),
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
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('WebSearch is blocked', result.stderr)
        self.assertNotIn('synthetic-lifecycle-key', result.stderr + result.stdout)

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
