from __future__ import annotations

import shutil
from pathlib import Path
import tempfile
import unittest

from check_sources import load_sources

DATA = Path(__file__).with_name('data')


class ExchangeTests(unittest.TestCase):
    def test_example_is_readable(self):
        tables = load_sources(DATA)
        self.assertTrue(all(tables.values()))
        self.assertTrue(all(0 <= float(r['score']) <= 1 and int(r['event_at']) <= int(r['seen_at']) for r in tables['signals']))
        self.assertTrue(any(r['decision'] == 'pending' for r in tables['episodes']))
        self.assertTrue({r['use'] for r in tables['shifts']} >= {'tune', 'holdout'})

    def test_duplicate_identity_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            duplicate = Path(directory) / 'copies'
            shutil.copytree(DATA, duplicate)
            path = duplicate / 'shifts.csv'
            rows = path.read_text(encoding='utf-8').splitlines()
            path.write_text('\n'.join(rows + [rows[1]]) + '\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, '标识为空或重复'):
                load_sources(duplicate)
