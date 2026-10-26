"""Retained Witch's House sources survive Git without newline conversion."""

import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'data/quest/evidence/witchs_house'


class WitchsHouseEvidenceTest(unittest.TestCase):
    def test_source_index_preserves_body_hashes_and_sizes(self):
        records = json.loads((EVIDENCE / 'source-index.json').read_text())
        self.assertTrue(records)
        for record in records:
            with self.subTest(source=record['local']):
                raw = (EVIDENCE / record['local']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), record['sha256'])
                self.assertEqual(len(raw), record['saved_bytes'])

    def test_all_packet_sources_match_original_build_manifest(self):
        decisions = json.loads((EVIDENCE / 'build-decisions.json').read_text())
        manifest = decisions['uncommitted_build_evidence']['file_sha256']
        prefix = 'data/quest/evidence/witchs_house/sources/'
        expected = {path: digest for path, digest in manifest.items()
                    if path.startswith(prefix)}
        actual = {path.relative_to(ROOT).as_posix()
                  for path in (EVIDENCE / 'sources').rglob('*') if path.is_file()}
        self.assertEqual(actual, set(expected))
        for path, digest in expected.items():
            with self.subTest(source=path):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_git_preserves_mixed_line_endings_in_retained_html(self):
        path = EVIDENCE / 'sources/tipit-20120825005349.html'
        raw = path.read_bytes()
        with io.TextIOWrapper(io.BytesIO(raw), encoding='latin-1', newline='') as stream:
            self.assertEqual(stream.read().encode('latin-1'), raw)
            self.assertEqual(stream.newlines, ('\n', '\r\n'))
        checkout = Path(self.enterContext(tempfile.TemporaryDirectory()))
        subprocess.run(['git', 'init', '-q', str(checkout)], check=True)
        relative = path.relative_to(ROOT).as_posix()
        retained = checkout / relative
        retained.parent.mkdir(parents=True)
        retained.write_bytes(raw)
        (retained.parent.parent / '.gitattributes').write_bytes(
            (EVIDENCE / '.gitattributes').read_bytes(),
        )
        attribute = subprocess.check_output(
            ['git', 'check-attr', '-z', 'text', '--', relative], cwd=checkout,
        )
        self.assertEqual(attribute.split(b'\0')[2], b'unset')
        stored = subprocess.check_output(
            ['git', 'hash-object', '--stdin', '--path', relative], input=raw, cwd=checkout,
        )
        original = subprocess.check_output(
            ['git', 'hash-object', '--stdin', '--no-filters'], input=raw, cwd=checkout,
        )
        self.assertEqual(stored, original)
