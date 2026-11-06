import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from uuid import UUID

SCRIPTS = Path(__file__).resolve().parents[1] / 'plugins/lej-pp-search/scripts'
spec = importlib.util.spec_from_file_location('writer', SCRIPTS / 'write-research.py')
writer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(writer)


class ResearchSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / 'project'
        self.project.mkdir()
        self.outside = self.root / 'outside'
        self.outside.mkdir()
        self.research = self.project / '.perplexity-research'
        self.previous = Path.cwd()
        os.chdir(self.project)
        self.addCleanup(os.chdir, self.previous)

    def hook(self, command=None, content='Synthetic answer [1]'):
        event = {
            'tool_input': {'command': command or '''curl https://api.perplexity.ai/chat/completions -d '{"messages":[{"role":"user","content":"audit"}]}' '''},
            'tool_response': json.dumps({
                'choices': [{'message': {'content': content}}],
                'citations': ['https://example.com/source'],
                'search_results': [{'title': 'Source', 'url': 'https://example.com/source', 'snippet': 'Evidence'}],
            }),
        }
        return subprocess.run(['bash', str(SCRIPTS / 'save-perplexity-result.sh')],
                              input=json.dumps(event), text=True, cwd=self.project,
                              capture_output=True, umask=0o022, timeout=10)

    def test_ordinary_hook_preserves_research_and_private_mode(self):
        result = self.hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        files = list(self.research.glob('*.md'))
        self.assertEqual(len(files), 1)
        self.assertEqual(stat.S_IMODE(files[0].stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(self.research.stat().st_mode), 0o700)
        text = files[0].read_text()
        for expected in ('# audit', 'Synthetic answer [1]', 'https://example.com/source', '**Snippet:** Evidence'):
            self.assertIn(expected, text)

    def test_hook_rejects_directory_symlink(self):
        self.research.symlink_to(self.outside, target_is_directory=True)
        result = self.hook()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.outside.iterdir()), [])
        self.assertNotIn('Research saved to', result.stderr)

    def test_hook_rejects_dangling_directory_symlink(self):
        self.research.symlink_to(self.outside / 'absent', target_is_directory=True)
        self.assertNotEqual(self.hook().returncode, 0)
        self.assertFalse((self.outside / 'absent').exists())

    def test_hook_rejects_regular_file_as_directory(self):
        self.research.write_text('keep me')
        self.assertNotEqual(self.hook().returncode, 0)
        self.assertEqual(self.research.read_text(), 'keep me')

    def test_existing_public_directory_still_gets_private_files(self):
        self.research.mkdir(mode=0o755)
        result = self.hook()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(stat.S_IMODE(next(self.research.glob('*.md')).stat().st_mode), 0o600)

    def test_concurrent_same_query_keeps_all_answers(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.hook(), range(4)))
        self.assertTrue(all(result.returncode == 0 for result in results))
        self.assertEqual(len(list(self.research.glob('*.md'))), 4)

    def test_response_is_data_and_not_executed(self):
        content = '$(touch injected) `touch injected` ${HOME}\nUnicode: café'
        self.assertEqual(self.hook(content=content).returncode, 0)
        self.assertFalse((self.project / 'injected').exists())
        self.assertIn(content, next(self.research.glob('*.md')).read_text())

    def test_unrelated_commands_do_not_create_directory(self):
        self.assertEqual(self.hook(command='printf hello').returncode, 0)
        self.assertFalse(self.research.exists())

    def test_writer_rejects_paths_before_creating_directory(self):
        for prefix in ('../escape', '/absolute', 'path/name', ''):
            with self.assertRaises(ValueError):
                writer.save_research(prefix, 'data')
        self.assertFalse(self.research.exists())

    def test_writer_refuses_existing_file_symlink_hardlink_and_fifo(self):
        self.research.mkdir()
        victim = self.outside / 'victim'
        victim.write_text('keep me')
        fixed_id = UUID(int=1)
        target = self.research / f'audit-{fixed_id.hex}.md'
        for kind in ('regular', 'symlink', 'hardlink', 'fifo'):
            with self.subTest(kind=kind):
                if kind == 'regular':
                    target.write_text('keep me')
                elif kind == 'symlink':
                    target.symlink_to(victim)
                elif kind == 'hardlink':
                    os.link(victim, target)
                else:
                    os.mkfifo(target)
                with patch.object(writer.uuid, 'uuid4', return_value=fixed_id):
                    with self.assertRaises(FileExistsError):
                        writer.save_research('audit', 'overwrite')
                self.assertEqual(victim.read_text(), 'keep me')
                if kind == 'regular':
                    self.assertEqual(target.read_text(), 'keep me')
                target.unlink()

    def test_directory_replacement_cannot_redirect_open(self):
        self.research.mkdir()
        pinned = self.project / 'original-research'
        original_open = os.open

        def replace_before_file_open(path, flags, mode=0o777, *, dir_fd=None):
            if dir_fd is not None:
                self.research.rename(pinned)
                self.research.symlink_to(self.outside, target_is_directory=True)
            return original_open(path, flags, mode, dir_fd=dir_fd)

        with patch.object(writer.os, 'open', side_effect=replace_before_file_open):
            writer.save_research('audit', 'confined')
        self.assertEqual(list(self.outside.iterdir()), [])
        self.assertEqual(next(pinned.glob('*.md')).read_text(), 'confined')

    def test_documented_key_removal_preserves_other_settings_privately(self):
        root = SCRIPTS.parents[2]
        for document in (root / 'README.md', SCRIPTS.parent / 'skills/lej-pp-search/SKILL.md'):
            with self.subTest(document=document.name):
                text = document.read_text()
                command = re.search(r'```bash\n(\(\n  set -e\n  settings_tmp=.*?)```', text, re.S)[1]
                settings_dir = self.root / 'home' / '.claude'
                settings_dir.mkdir(parents=True, exist_ok=True)
                settings = settings_dir / 'settings.json'
                data = {'env': {'PERPLEXITY_API_KEY': 'synthetic', 'OTHER_KEY': 'preserve'},
                        'environmentVariables': {'PERPLEXITY_API_KEY': 'synthetic-legacy'},
                        'permissions': {'allow': ['Read']}}
                settings.write_text(json.dumps(data))
                result = subprocess.run(['bash', '-c', command], capture_output=True, text=True,
                                        env={**os.environ, 'HOME': str(settings_dir.parent)},
                                        umask=0o022, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(settings.read_text()), {
                    'env': {'OTHER_KEY': 'preserve'}, 'environmentVariables': {},
                    'permissions': {'allow': ['Read']}})
                self.assertEqual(stat.S_IMODE(settings.stat().st_mode), 0o600)
                self.assertEqual(list(settings_dir.glob('settings.json.*')), [])

                settings.write_text('invalid JSON')
                result = subprocess.run(['bash', '-c', command], capture_output=True, text=True,
                                        env={**os.environ, 'HOME': str(settings_dir.parent)}, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(settings.read_text(), 'invalid JSON')
                self.assertEqual(list(settings_dir.glob('settings.json.*')), [])


if __name__ == '__main__':
    unittest.main()
