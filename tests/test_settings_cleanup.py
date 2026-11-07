"""Execute the maintained uninstall example with isolated settings and fault injection."""
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
import unittest

README = Path(__file__).resolve().parents[1] / 'README.md'


class SettingsCleanupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / 'home'
        self.directory = self.home / '.claude'
        self.directory.mkdir(parents=True, mode=0o700)
        self.settings = self.directory / 'settings.json'
        self.data = {'env': {'PERPLEXITY_API_KEY': 'synthetic-not-real', 'OTHER': 'old'},
                     'environmentVariables': {'PERPLEXITY_API_KEY': 'synthetic-legacy'},
                     'permissions': {'allow': ['Read']}, 'enabledPlugins': {'other@market': True}}
        self.settings.write_text(json.dumps(self.data))
        self.original = self.settings.read_bytes()
        self.command = re.search(r'```bash\n(.*?)```', README.read_text().split(
            'Optional: to also remove the API key', 1)[1], re.S)[1]

    def run_cleanup(self, fault=''):
        env = {'PATH': os.environ['PATH'], 'HOME': str(self.home), 'LANG': 'C.UTF-8',
               'PYTHONDONTWRITEBYTECODE': '1'}
        if fault:
            binary = self.root / 'bin'
            binary.mkdir(exist_ok=True)
            # Run faults after the temporary output is flushed, before publication.
            actions = {
                'concurrent': "p.write_text(json.dumps({**json.loads(p.read_text()), 'permissions': {'allow': ['Read', 'Write']}}))",
                'inplace': "p.write_text(json.dumps({**json.loads(p.read_text()), 'permissions': {'allow': ['Read', 'Write']}}))",
                'directory': "p.rename(p.with_name('original.json')); p.mkdir()",
                'symlink': "p.rename(p.with_name('original.json')); p.symlink_to(victim)",
                'parent': "p.parent.rename(p.parent.with_name('retained')); p.parent.mkdir(); (p.parent / 'settings.json').write_text('replacement')",
                'replace-failure': "raise OSError('synthetic replace failure')",
                'term': 'os.kill(os.getpid(), signal.SIGTERM)',
                'kill': 'os.kill(os.getpid(), signal.SIGKILL)',
                'collision': 'pass',
            }
            action = actions[fault]
            if fault == 'concurrent':
                action = "replacement = p.with_name('new.json'); replacement.write_text(json.dumps({**json.loads(p.read_text()), 'permissions': {'allow': ['Read', 'Write']}})); replacement.replace(p)"
            runner = self.root / 'runner.py'
            runner.write_text('''import json, os, pathlib, signal, sys
from unittest.mock import patch
p = pathlib.Path.home() / '.claude/settings.json'
victim = p.parent.parent.parent / 'victim.json'
real_fsync = os.fsync
fired = False
def fault(fd):
    global fired
    real_fsync(fd)
    if not fired:
        fired = True
        ACTION
code = sys.stdin.read()
with patch.object(os, 'fsync', fault):
    exec(compile(code, '<documented-cleanup>', 'exec'), {'__name__': '__main__'})
'''.replace('ACTION', action).replace('code = sys.stdin.read()',
    'import uuid\nuuid.uuid4 = lambda: type(\"Id\", (), {\"hex\": \"fixed\"})()\ncode = sys.stdin.read()'
    if fault == 'collision' else 'code = sys.stdin.read()'))
            (binary / 'python3').write_text('#!/bin/sh\nexec ' + shutil.which('python3') + ' ' + str(runner) + '\n')
            (binary / 'python3').chmod(0o755)
            # The baseline uses jq; reproduce equivalent publication-time races there.
            jq = shutil.which('jq')
            jq_actions = {
                'concurrent': '''"$REAL_JQ" '.permissions.allow += ["Write"]' "$HOME/.claude/settings.json" > "$HOME/.claude/new.json"; mv "$HOME/.claude/new.json" "$HOME/.claude/settings.json"''',
                'inplace': '''"$REAL_JQ" '.permissions.allow += ["Write"]' "$HOME/.claude/settings.json" > "$HOME/.claude/new.json"; cat "$HOME/.claude/new.json" > "$HOME/.claude/settings.json"; rm "$HOME/.claude/new.json"''',
                'directory': '''mv "$HOME/.claude/settings.json" "$HOME/.claude/original.json"; mkdir "$HOME/.claude/settings.json"''',
                'symlink': '''mv "$HOME/.claude/settings.json" "$HOME/.claude/original.json"; ln -s "$HOME/../victim.json" "$HOME/.claude/settings.json"''',
                'term': 'kill -TERM "$PPID"; exit 143',
            }
            (binary / 'jq').write_text('#!/bin/bash\n"$REAL_JQ" "$@"\n' + jq_actions.get(fault, '') + '\n')
            (binary / 'jq').chmod(0o755)
            env.update(PATH=str(binary) + ':' + env['PATH'], REAL_JQ=jq)
        result = subprocess.run(['bash', '-c', self.command], env=env, cwd=self.root,
                                capture_output=True, text=True, umask=0o022, timeout=10)
        self.assertNotIn('synthetic-not-real', result.stdout + result.stderr)
        self.assertNotIn('synthetic-legacy', result.stdout + result.stderr)
        return result

    def assert_no_temporary(self, directory=None):
        self.assertEqual(list((directory or self.directory).glob('settings.json.*')), [])

    def test_success_retains_unrelated_settings_and_retry_is_idempotent(self):
        for _ in range(2):
            result = self.run_cleanup()
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = json.loads(self.original)
            for field in ('env', 'environmentVariables'):
                expected[field].pop('PERPLEXITY_API_KEY')
            self.assertEqual(json.loads(self.settings.read_text()), expected)
            self.assertEqual(stat.S_IMODE(self.settings.stat().st_mode), 0o600)
            self.assert_no_temporary()

    def test_existing_symlink_and_hardlink_are_preserved_and_refused(self):
        target = self.root / 'victim.json'
        target.write_bytes(self.original)
        self.settings.unlink()
        for kind in ('symlink', 'hardlink'):
            with self.subTest(kind=kind):
                if kind == 'symlink':
                    self.settings.symlink_to(target)
                else:
                    os.link(target, self.settings)
                inode = self.settings.lstat().st_ino
                try:
                    self.assertNotEqual(self.run_cleanup().returncode, 0)
                    self.assertEqual(self.settings.lstat().st_ino, inode)
                    self.assertEqual(target.read_bytes(), self.original)
                    self.assert_no_temporary()
                finally:
                    self.settings.unlink()

    def test_fifo_and_directory_are_refused_without_blocking(self):
        self.settings.unlink()
        for kind in ('fifo', 'directory'):
            with self.subTest(kind=kind):
                if kind == 'fifo':
                    os.mkfifo(self.settings)
                else:
                    self.settings.mkdir()
                self.assertNotEqual(self.run_cleanup().returncode, 0)
                self.assert_no_temporary()
                if kind == 'directory':
                    self.settings.rmdir()
                else:
                    self.settings.unlink()

    def test_invalid_json_stream_and_settings_shapes_are_preserved(self):
        for text in ('invalid JSON', '{}\n{}', 'null', '[]', '{"env": []}'):
            with self.subTest(shape=text):
                self.settings.write_text(text)
                self.assertNotEqual(self.run_cleanup().returncode, 0)
                self.assertEqual(self.settings.read_text(), text)
                self.assert_no_temporary()

    def test_replaced_or_inplace_settings_edit_is_preserved(self):
        for fault in ('concurrent', 'inplace'):
            with self.subTest(fault=fault):
                self.settings.write_bytes(self.original)
                self.assertNotEqual(self.run_cleanup(fault).returncode, 0)
                expected = json.loads(self.original)
                expected['permissions']['allow'].append('Write')
                self.assertEqual(json.loads(self.settings.read_text()), expected)
                self.assert_no_temporary()
                shutil.rmtree(self.root / 'bin')

    def test_replacement_directory_is_not_a_publication_destination(self):
        self.assertNotEqual(self.run_cleanup('directory').returncode, 0)
        self.assertEqual(list(self.settings.iterdir()), [])
        self.assertEqual((self.directory / 'original.json').read_bytes(), self.original)
        self.assert_no_temporary()

    def test_late_symlink_is_not_replaced_or_followed(self):
        victim = self.root / 'victim.json'
        victim.write_text('untouched victim')
        self.assertNotEqual(self.run_cleanup('symlink').returncode, 0)
        self.assertTrue(self.settings.is_symlink())
        self.assertEqual(victim.read_text(), 'untouched victim')
        self.assertEqual((self.directory / 'original.json').read_bytes(), self.original)
        self.assert_no_temporary()

    def test_replaced_parent_directory_is_preserved(self):
        self.assertNotEqual(self.run_cleanup('parent').returncode, 0)
        self.assertEqual(self.settings.read_text(), 'replacement')
        retained = self.home / 'retained'
        self.assertEqual((retained / 'settings.json').read_bytes(), self.original)
        self.assert_no_temporary(retained)

    def test_exclusive_creation_collision_never_removes_an_existing_file(self):
        occupied = self.directory / 'settings.json.fixed'
        occupied.write_text('preserve existing temporary')
        self.assertNotEqual(self.run_cleanup('collision').returncode, 0)
        self.assertEqual(occupied.read_text(), 'preserve existing temporary')
        self.assertEqual(self.settings.read_bytes(), self.original)

    def test_symlinked_or_shared_settings_directory_is_refused(self):
        retained = self.home / 'retained'
        self.directory.rename(retained)
        self.directory.symlink_to(retained, target_is_directory=True)
        self.assertNotEqual(self.run_cleanup().returncode, 0)
        self.assertTrue(self.directory.is_symlink())
        self.assertEqual((retained / 'settings.json').read_bytes(), self.original)
        self.directory.unlink()
        retained.rename(self.directory)
        self.directory.chmod(0o777)
        self.assertNotEqual(self.run_cleanup().returncode, 0)
        self.assertEqual(self.settings.read_bytes(), self.original)
        self.assert_no_temporary()

    def test_write_failure_preserves_original_and_cleans_temporary(self):
        self.assertNotEqual(self.run_cleanup('replace-failure').returncode, 0)
        self.assertEqual(self.settings.read_bytes(), self.original)
        self.assert_no_temporary()

    def test_sigterm_preserves_original_and_cleans_temporary(self):
        self.assertNotEqual(self.run_cleanup('term').returncode, 0)
        self.assertEqual(self.settings.read_bytes(), self.original)
        self.assert_no_temporary()

    def test_forced_kill_preserves_original_and_leaves_only_private_temporary(self):
        self.assertNotEqual(self.run_cleanup('kill').returncode, 0)
        self.assertEqual(self.settings.read_bytes(), self.original)
        files = list(self.directory.glob('settings.json.*'))
        self.assertEqual(len(files), 1)
        self.assertEqual(stat.S_IMODE(files[0].stat().st_mode), 0o600)
        self.assertNotIn('PERPLEXITY_API_KEY', json.loads(files[0].read_text())['env'])

    def test_interrupted_cleanup_retries_latest_settings_instead_of_old_output(self):
        for fault in ('term', 'kill', 'replace-failure'):
            with self.subTest(fault=fault):
                self.settings.write_bytes(self.original)
                self.assertNotEqual(self.run_cleanup(fault).returncode, 0)
                self.assertEqual(self.settings.read_bytes(), self.original)
                leftovers = {path: path.read_bytes()
                             for path in self.directory.glob('settings.json.*')}
                latest = json.loads(self.settings.read_text())
                latest['env']['OTHER'] = 'edited after interruption'
                latest['permissions']['allow'].append('Write')
                latest['enabledPlugins']['new-plugin@market'] = True
                self.settings.write_text(json.dumps(latest))
                for field in ('env', 'environmentVariables'):
                    latest[field].pop('PERPLEXITY_API_KEY')
                for _ in range(2):
                    result = self.run_cleanup()
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(self.settings.read_text()), latest)
                    self.assertEqual(stat.S_IMODE(self.settings.stat().st_mode), 0o600)
                # SIGKILL output is private but stale: retry must neither use it
                # as a backup nor delete an arbitrary pre-existing sibling.
                self.assertEqual({path: path.read_bytes() for path in
                                  self.directory.glob('settings.json.*')}, leftovers)
                for path in leftovers:
                    self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
                    path.unlink()

    def test_retry_after_concurrent_edit_keeps_new_marketplace_enablement(self):
        self.assertNotEqual(self.run_cleanup('concurrent').returncode, 0)
        latest = json.loads(self.settings.read_text())
        latest['enabledPlugins']['installed-after-failure@market'] = True
        self.settings.write_text(json.dumps(latest))
        result = self.run_cleanup()
        self.assertEqual(result.returncode, 0, result.stderr)
        for field in ('env', 'environmentVariables'):
            latest[field].pop('PERPLEXITY_API_KEY')
        self.assertEqual(json.loads(self.settings.read_text()), latest)
        self.assert_no_temporary()


if __name__ == '__main__':
    unittest.main()
