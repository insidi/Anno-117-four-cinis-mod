"""Check the finished package against its pinned predecessor; no game needed."""
import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import struct
import unittest
import uuid
import xml.etree.ElementTree as ET
import zipfile

import build_release as release
from cinis_v2 import filedb, rda

ROOT = Path(__file__).resolve().parents[1]
VERSION = json.loads((ROOT / 'config/modinfo.json').read_text(encoding='utf-8'))['Version']
BASE = ROOT / 'dist/base/cinis-four-directions-v0.3.2.zip'
MOD = ROOT / f'dist/v{VERSION}/cinis-four-directions'
ZIP = ROOT / f'dist/cinis-four-directions-v{VERSION}.zip'


@contextmanager
def scratch_directory():
    # Use ordinary inherited workspace permissions. Windows' private temporary
    # directory ACLs can exclude a restricted token even in its own test run.
    parent = (ROOT / 'dist').resolve()
    directory = parent / ('release-test-' + uuid.uuid4().hex)
    directory.mkdir()
    try:
        yield directory
    finally:
        if directory.resolve().parent != parent:
            raise ValueError('Unexpected scratch directory')
        for child in directory.iterdir():
            child.unlink()
        directory.rmdir()


def signature(node):
    return node.tag, sorted(node.attrib.items()), (node.text or '').strip(), [signature(c) for c in node]


class ReleaseChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = release.config()
        cls.source = zipfile.ZipFile(BASE)
        cls.addClassCleanup(cls.source.close)
        if release.digest(BASE.read_bytes()) != cls.settings['base_sha256']:
            raise ValueError('Tests require the verified predecessor ZIP')

    def previous(self, name):
        return self.source.read('cinis-four-directions/' + name)

    def test_identity_save_and_multiplayer_metadata_are_preserved(self):
        old = json.loads(self.previous('modinfo.json'))
        new = json.loads((MOD / 'modinfo.json').read_text(encoding='utf-8'))
        self.assertEqual(new, json.loads((ROOT / 'config/modinfo.json').read_text(encoding='utf-8')))
        self.assertEqual(new['Version'], VERSION)
        self.assertTrue(new['GameSetup']['Multiplayer'])
        for value in (old, new):
            value.pop('Version')
            value.pop('Description')
        self.assertEqual(new, old)

    def test_zip_is_complete_clean_and_matches_folder(self):
        # Independent allowlist: only runtime resources and user instructions.
        expected = {'modinfo.json', 'README.md', 'OBSIDIAN-FIX.md', 'PATCH-KOMPATIBILITAET.md',
                    'CHANGELOG.md', 'data/base/config/export/assets.xml'}
        for layout in ('cinis_four', 'cinis_four_v2'):
            for variant in ('easy', 'medium', 'hard'):
                expected.update(f'data/phil/{layout}/{variant}/{layout}_{variant}{ext}'
                                for ext in ('.a7t', '.a7tinfo', '.a7te'))
        self.assertEqual(len(expected), 24)
        self.assertEqual({p.relative_to(MOD).as_posix() for p in MOD.rglob('*') if p.is_file()}, expected)
        with zipfile.ZipFile(ZIP) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(len(archive.namelist()), 24)
            self.assertEqual(set(archive.namelist()), {'cinis-four-directions/' + n for n in expected})
            for name in expected:
                self.assertEqual(archive.read('cinis-four-directions/' + name), (MOD / name).read_bytes(), name)
        self.assertIn(VERSION, (MOD / 'README.md').read_text(encoding='utf-8'))

    def test_only_four_playable_fields_change_and_legacy_stays_identical(self):
        changed = 0
        for name in release.MAP_FILES:
            with self.subTest(file=name):
                old, new = self.previous(name), (MOD / name).read_bytes()
                expected_change = '/cinis_four_v2/' in name and (
                    name.endswith('.a7tinfo') or name.endswith('/cinis_four_v2_easy.a7t'))
                if not expected_change:
                    self.assertEqual(new, old)
                    continue
                changed += 1
                self.assertNotEqual(new, old)
                tag = 'MapTemplate'
                if name.endswith('.a7t'):
                    tag = 'SessionSettings'
                    with scratch_directory() as directory:
                        base_world = Path(directory) / 'base.a7t'
                        base_world.write_bytes(old)
                        old = rda.read_single(str(base_world))
                    entries = rda.entries(str(MOD / name))
                    self.assertEqual([entry.name for entry in entries], ['gamedata.data'])
                    # The game requires the level-1 zlib stream, not ZIP's level.
                    self.assertEqual(new[entries[0].offset:entries[0].offset + 2], b'\x78\x01')
                    new = rda.read_single(str(MOD / name))
                old_roots, old_tags, old_attrs = filedb.parse(old)
                roots, tags, attrs = filedb.parse(new)
                self.assertEqual((tags, attrs), (old_tags, old_attrs))
                field = filedb.attr(filedb.find_tag(roots, tag), 'PlayableArea')
                # Verified native map: 2688 wide, upper playable edge 2440.
                margin = 2688 - 2440
                self.assertEqual(struct.unpack('<4i', field['data']), (margin, margin, 4096-margin, 4096-margin))
                field['data'] = filedb.attr(filedb.find_tag(old_roots, tag), 'PlayableArea')['data']
                self.assertEqual(roots, old_roots, 'Unrelated FileDB fields changed')
        self.assertEqual(changed, 4)

    def test_every_template_has_four_unique_current_island_references(self):
        original_name = 'roman_dlc01_island_continental_01'
        expected_path = f'data/dlc01/provinces/roman/islands/pool/{original_name}/{original_name}.a7m'
        expected_positions = {
            'cinis_four': {(3200, 3200): 0, (3200, 128): 0, (128, 128): 0, (128, 3200): 0},
            'cinis_four_v2': {(3328, 3328): 0, (3328, 0): 3, (0, 0): 2, (0, 3328): 1},
        }
        for layout, positions in expected_positions.items():
            for variant in ('easy', 'medium', 'hard'):
                prefix = MOD / f'data/phil/{layout}/{variant}/{layout}_{variant}'
                roots, *_ = filedb.parse(prefix.with_suffix('.a7tinfo').read_bytes())
                template = filedb.find_tag(roots, 'MapTemplate')
                labels, found = [], {}
                for wrapper in template['children']:
                    if wrapper.get('tag') != 'TemplateElement':
                        continue
                    element = filedb.find_tag(wrapper['children'], 'Element')
                    path = filedb.attr(element, 'MapFilePath')
                    if path and path['data'].decode('utf-16le') == expected_path:
                        labels.append(filedb.attr(element, 'IslandLabel')['data'].decode('ascii'))
                        found[struct.unpack('<2i', filedb.attr(element, 'Position')['data'])] = filedb.attr(element, 'Rotation90')['data'][0]
                self.assertEqual(len(labels), 4)
                self.assertEqual(set(labels), {original_name, 'cinis_east', 'cinis_south', 'cinis_west'})
                self.assertEqual(found, positions)
                editor = ET.parse(prefix.with_suffix('.a7te')).getroot()
                self.assertEqual(editor.findtext('Dimensions/X'), '4096')
                self.assertEqual(len(editor.findall('.//Chunk')), 4096)

    def test_map_and_volcano_modops_are_unchanged_without_new_guids(self):
        old = ET.fromstring(self.previous(release.ASSETS))
        new = ET.parse(MOD / release.ASSETS).getroot()
        self.assertEqual(signature(new), signature(old))
        self.assertEqual(new.tag, 'ModOps')
        self.assertEqual(len(new), 12)
        self.assertIsNone(new.find('.//Asset'))
        self.assertEqual({op.get('GUID') for op in new}, {'3377', '44421', '44422', '144830', '144837'})
        keys = [(op.get('GUID'), op.get('Merge'), op.get('Replace')) for op in new]
        self.assertEqual(len(keys), len(set(keys)))

    def test_bad_base_tag_and_unexpected_source_boundary_are_rejected(self):
        with scratch_directory() as directory:
            corrupt = Path(directory) / 'wrong.zip'
            corrupt.write_bytes(b'not the verified release')
            output = Path(directory) / 'must-not-exist'
            with self.assertRaisesRegex(ValueError, 'pinned SHA256'):
                release.build(corrupt, output)
            with self.assertRaisesRegex(ValueError, 'Tag and modinfo'):
                release.build(BASE, output, 'v0.0.0')
            self.assertFalse(output.exists())
        template = self.previous('data/phil/cinis_four_v2/easy/cinis_four_v2_easy.a7tinfo')
        with self.assertRaisesRegex(ValueError, 'Unexpected source PlayableArea'):
            release.update_playable(template, 'MapTemplate', (0, 0, 4096, 4096), self.settings['playable_area'])

    def test_checksum_and_report_match_actual_package(self):
        checksum = hashlib.sha256(ZIP.read_bytes()).hexdigest()
        self.assertEqual(ZIP.with_suffix('.zip.sha256').read_text().strip(), checksum + '  ' + ZIP.name)
        report = json.loads((ZIP.parent / f'build-v{VERSION}.json').read_text(encoding='utf-8'))
        self.assertEqual(report['version'], VERSION)
        self.assertEqual(report['zip_sha256'], checksum)
        self.assertEqual(report['unchanged_map_files'], 14)
        for name, expected in report['file_hashes'].items():
            self.assertEqual(release.digest((MOD / name).read_bytes()), expected)
        self.assertEqual(report['runtime_test'], 'NOT RUN')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-zip', type=Path, default=BASE)
    parser.add_argument('--mod', type=Path, default=MOD)
    parser.add_argument('--zip', type=Path, default=ZIP)
    args = parser.parse_args()
    BASE, MOD, ZIP = args.base_zip, args.mod, args.zip
    outcome = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReleaseChecks))
    report = {'result': 'PASS' if outcome.wasSuccessful() else 'FAIL', 'version': VERSION,
              'tests': outcome.testsRun, 'zip_sha256': release.digest(ZIP.read_bytes()), 'runtime_test': 'NOT RUN'}
    (ZIP.parent / f'tests-v{VERSION}.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    raise SystemExit(0 if outcome.wasSuccessful() else 1)
