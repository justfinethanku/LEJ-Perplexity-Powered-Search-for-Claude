"""Opt-in tests of the README's recovery commands against a real local CLI.

No model runs: only plugin-manager subcommands and an installed hook with
synthetic input. HOME, configuration, marketplace and project are disposable.
"""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ID = 'lej-pp-search@lej-marketplace'
OTHER_ID = 'recovery-control@lej-marketplace'
CLI = shutil.which('claude')


@unittest.skipUnless(os.environ.get('LEJ_TEST_NATIVE_CLI') == '1',
                     'set LEJ_TEST_NATIVE_CLI=1 to test the installed Claude CLI')
@unittest.skipUnless(CLI, 'Claude Code CLI is required')
@unittest.skipUnless(os.name == 'posix' and getattr(os, 'getuid', lambda: 0)() != 0,
                     'permission faults require a non-root POSIX user')
class PluginRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='lej-recovery-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / 'home'
        self.config = self.home / 'active profile'
        self.project = self.root / 'project'
        (self.project / '.claude').mkdir(parents=True)
        self.config.mkdir(parents=True)
        # A real user's default profile must not be the fallback write target.
        self.inactive = self.home / '.claude/settings.json'
        self.inactive.parent.mkdir()
        self.inactive.write_text('{"env":{"INACTIVE_PROFILE":"preserve"}}')
        self.inactive_bytes = self.inactive.read_bytes()
        self.settings = {
            'user': self.config / 'settings.json',
            'project': self.project / '.claude/settings.json',
            'local': self.project / '.claude/settings.local.json',
        }
        for scope, path in self.settings.items():
            path.write_text(json.dumps({'env': {'KEEP': scope},
                                        'permissions': {'allow': ['Read']}}))
        self.research = self.project / '.perplexity-research/retained.md'
        self.research.parent.mkdir()
        self.research.write_text('User research survives plugin recovery.\n')
        self.source = self.root / 'local marketplace [recovery]'
        plugin = self.source / 'plugins/lej-pp-search'
        shutil.copytree(ROOT / 'plugins/lej-pp-search', plugin)
        self.manifest = plugin / '.claude-plugin/plugin.json'
        self.version = json.loads(self.manifest.read_text())['version']
        other = self.source / 'plugins/recovery-control/.claude-plugin'
        other.mkdir(parents=True)
        (other / 'plugin.json').write_text(json.dumps({
            'name': 'recovery-control', 'version': '1.0.0',
            'description': 'Unrelated plugin used only in recovery tests',
        }))
        marketplace = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
        marketplace['plugins'].append({'name': 'recovery-control',
                                      'source': './plugins/recovery-control',
                                      'description': 'Unrelated recovery control'})
        (self.source / '.claude-plugin').mkdir()
        (self.source / '.claude-plugin/marketplace.json').write_text(json.dumps(marketplace))
        # Deliberately do not inherit auth, provider keys, or a user's config.
        self.env = {
            'PATH': os.environ['PATH'], 'HOME': str(self.home),
            'CLAUDE_CONFIG_DIR': str(self.config), 'LANG': 'C.UTF-8',
            'GIT_TERMINAL_PROMPT': '0', 'PYTHONDONTWRITEBYTECODE': '1',
            'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC': '1',
            'DISABLE_AUTOUPDATER': '1', 'DISABLE_TELEMETRY': '1',
            'DISABLE_ERROR_REPORTING': '1',
        }
        self.cli('plugin', 'marketplace', 'add', str(self.source))
        for scope in self.settings:
            self.cli('plugin', 'install', PLUGIN_ID, '--scope', scope)
        for scope in ('user', 'project'):
            self.cli('plugin', 'install', OTHER_ID, '--scope', scope)

    def cli(self, *args, succeeds=True):
        result = subprocess.run([CLI, *args], cwd=self.project, env=self.env,
                                text=True, capture_output=True, timeout=60)
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def documented(self, section, prefix, succeeds=True):
        """Run the maintained command, so a wrong-scope docs edit is observable."""
        text = (ROOT / 'README.md').read_text().split(section, 1)[1]
        text = text.split('\n## ', 1)[0]
        commands = [line for block in re.findall(r'```bash\n(.*?)```', text, re.S)
                    for line in block.splitlines() if line.startswith(prefix)]
        self.assertEqual(len(commands), 1, commands)
        return self.cli(*shlex.split(commands[0])[1:], succeeds=succeeds)

    def records(self):
        rows = json.loads(self.cli('plugin', 'list', '--json').stdout)
        for row in rows:
            self.assertFalse(row.get('errors'), row)
        # projectEnabled/folderVersion describe live source/enablement, not
        # the registry's installed version; don't confuse these during retry.
        return {(row['id'], row['scope']): {
            key: row.get(key) for key in ('id', 'scope', 'version', 'installPath', 'projectPath')
        } for row in rows}

    def settings_state(self):
        return {scope: json.loads(path.read_text()) for scope, path in self.settings.items()}

    def add_newer_edits(self):
        for scope, path in self.settings.items():
            data = json.loads(path.read_text())
            data['env']['ADDED_AFTER_FAILURE'] = scope
            path.write_text(json.dumps(data))

    def assert_retained(self):
        self.assertEqual(self.inactive.read_bytes(), self.inactive_bytes)
        self.assertEqual(self.research.read_text(), 'User research survives plugin recovery.\n')
        marketplaces = json.loads(self.cli('plugin', 'marketplace', 'list', '--json').stdout)
        self.assertIn('lej-marketplace', [entry['name'] for entry in marketplaces])

    def assert_cached_hook_works(self, record):
        plugin = Path(record['installPath'])
        hooks = json.loads((plugin / 'hooks/hooks.json').read_text())['hooks']
        result = subprocess.run(
            ['bash', '-c', hooks['PreToolUse'][0]['hooks'][0]['command']],
            input='{}', text=True, capture_output=True, cwd=self.project, timeout=10,
            env={**self.env, 'CLAUDE_PLUGIN_ROOT': str(plugin), 'LEJ_AUTO_REDIRECT': 'false'},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['hookSpecificOutput']['permissionDecision'], 'allow')

    @contextmanager
    def unwritable(self, *paths):
        modes = [(path, path.stat().st_mode & 0o777) for path in paths]
        try:
            for path, mode in modes:
                path.chmod(mode & ~0o222)
            yield
        finally:
            for path, mode in modes:
                path.chmod(mode)

    def stage_release(self):
        data = json.loads(self.manifest.read_text())
        data['version'] = '99.0.0'  # A fixture version, not a published release.
        self.manifest.write_text(json.dumps(data))
        (self.manifest.parent.parent / 'recovery-marker.txt').write_text('complete fixture release')

    def update(self, succeeds=True):
        return self.documented('**Installed code has not changed after a fix merged:**',
                               'claude plugin update ', succeeds)

    def uninstall(self, succeeds=True):
        return self.documented('## Uninstall', 'claude plugin uninstall ', succeeds)

    def test_successful_update_then_uninstall_preserves_other_installations(self):
        initial = self.records()
        settings = self.settings_state()
        self.stage_release()
        self.update()
        updated = self.records()
        self.assertEqual(updated[(PLUGIN_ID, 'user')]['version'], '99.0.0')
        for key in initial.keys() - {(PLUGIN_ID, 'user')}:
            self.assertEqual(updated[key], initial[key])
        self.assertEqual(self.settings_state(), settings)
        self.assert_cached_hook_works(updated[(PLUGIN_ID, 'user')])
        self.uninstall()
        self.assertEqual(self.records(), {key: value for key, value in updated.items()
                                          if key != (PLUGIN_ID, 'user')})
        expected = settings
        expected['user']['enabledPlugins'].pop(PLUGIN_ID)
        self.assertEqual(self.settings_state(), expected)
        self.assert_retained()

    def test_failed_update_retries_existing_cache_without_replaying_settings(self):
        initial = self.records()
        settings = self.settings_state()
        self.stage_release()
        with self.unwritable(self.config / 'plugins'):
            self.update(succeeds=False)
        cache = self.config / 'plugins/cache/lej-marketplace/lej-pp-search/99.0.0'
        self.assertTrue(cache.is_dir(), 'fault must occur after cache staging')
        self.assertEqual(self.records(), initial)
        self.assertEqual(self.settings_state(), settings)
        self.add_newer_edits()
        latest = self.settings_state()
        self.update()
        updated = self.records()
        self.assertEqual(updated[(PLUGIN_ID, 'user')]['version'], '99.0.0')
        self.assertEqual((Path(updated[(PLUGIN_ID, 'user')]['installPath']) /
                          'recovery-marker.txt').read_text(), 'complete fixture release')
        for key in initial.keys() - {(PLUGIN_ID, 'user')}:
            self.assertEqual(updated[key], initial[key])
        self.update()  # Repeating recovery must preserve the successful state.
        self.assertEqual(self.records(), updated)
        self.assertEqual(self.settings_state(), latest)
        self.assert_cached_hook_works(updated[(PLUGIN_ID, 'user')])
        self.assert_retained()

    def test_failed_uninstall_retry_then_out_of_order_update_and_reinstall(self):
        initial = self.records()
        settings = self.settings_state()
        # File permissions alone don't stop the CLI's atomic replacement.
        with self.unwritable(self.settings['user'], self.config):
            self.uninstall(succeeds=False)
        self.assertEqual(self.records(), initial)
        self.assertEqual(self.settings_state(), settings)
        self.add_newer_edits()
        latest = self.settings_state()
        self.uninstall()
        remaining = {key: value for key, value in initial.items() if key != (PLUGIN_ID, 'user')}
        self.assertEqual(self.records(), remaining)
        latest['user']['enabledPlugins'].pop(PLUGIN_ID)
        self.assertEqual(self.settings_state(), latest)
        # Delayed operations against the removed scope must not fall back to
        # project/local installations or recreate the removed user entry.
        self.uninstall(succeeds=False)
        self.update(succeeds=False)
        self.assertEqual(self.records(), remaining)
        self.assertEqual(self.settings_state(), latest)
        for scope in ('project', 'local'):
            self.assert_cached_hook_works(remaining[(PLUGIN_ID, scope)])
        self.cli('plugin', 'install', PLUGIN_ID, '--scope', 'user')
        self.assertEqual(self.records(), initial)
        latest['user']['enabledPlugins'][PLUGIN_ID] = True
        self.assertEqual(self.settings_state(), latest)
        self.assert_retained()


if __name__ == '__main__':
    unittest.main()
