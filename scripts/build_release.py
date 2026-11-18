"""Build a complete release from the SHA256-pinned public 0.3.2 package.

No installed game, numpy or private build inputs are required. Game compatibility
is audited separately on an installed copy; see audit_cinis.py and the patch report.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

from build_obsidian_fix import apply_obsidian_ops
from cinis_v2 import filedb, rda, rdawrite

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ('easy', 'medium', 'hard')
LAYOUTS = ('cinis_four', 'cinis_four_v2')
MAP_FILES = tuple(f'data/phil/{layout}/{variant}/{layout}_{variant}{ext}'
                  for layout in LAYOUTS for variant in VARIANTS
                  for ext in ('.a7t', '.a7te', '.a7tinfo'))
ASSETS = 'data/base/config/export/assets.xml'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def config():
    return json.loads((ROOT / 'config/release.json').read_text(encoding='utf-8'))


def update_playable(data, tag, previous, target):
    roots, tags, attrs = filedb.parse(data)
    node = filedb.find_tag(roots, tag)
    field = filedb.attr(node, 'PlayableArea') if node else None
    if field is None or struct.unpack('<4i', field['data']) != tuple(previous):
        raise ValueError('Unexpected source PlayableArea in ' + tag)
    field['data'] = struct.pack('<4i', *target)
    encoded = filedb.serialize(roots, tags, attrs)
    decoded, new_tags, new_attrs = filedb.parse(encoded)
    if decoded != roots or new_tags != tags or new_attrs != attrs:
        raise AssertionError('FileDB serialization changed unrelated fields')
    # Restoring the one scalar must recover the complete original node tree.
    filedb.attr(filedb.find_tag(decoded, tag), 'PlayableArea')['data'] = struct.pack('<4i', *previous)
    if decoded != filedb.parse(data)[0]:
        raise AssertionError('Unexpected changes outside PlayableArea')
    return encoded


def download_base(destination):
    settings = config()
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(settings['base_url'], headers={'User-Agent': 'Four-Cinis-build'})
    with urllib.request.urlopen(request, timeout=60) as response:
        destination.write_bytes(response.read())
    if digest(destination.read_bytes()) != settings['base_sha256']:
        raise ValueError('Downloaded base ZIP does not match the pinned SHA256')
    return destination


def build(base_zip, output=None, tag=None):
    settings = config()
    metadata = json.loads((ROOT / 'config/modinfo.json').read_text(encoding='utf-8'))
    version = metadata['Version']
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('Expected a numeric major.minor.patch version')
    if tag is not None and tag != 'v' + version:
        raise ValueError('Tag and modinfo version differ')
    if metadata['ModID'] != 'cinis-four-directions-phil' or metadata['GameSetup']['Multiplayer'] is not True:
        raise ValueError('Mod identity or multiplayer metadata changed unexpectedly')
    raw_zip = Path(base_zip).read_bytes()
    if digest(raw_zip) != settings['base_sha256']:
        raise ValueError('Base ZIP does not match the pinned SHA256')
    output = Path(output or ROOT / 'dist').resolve()
    target = output / ('v' + version) / 'cinis-four-directions'
    docs = {'docs/TESTANLEITUNG.md': 'README.md', 'docs/OBSIDIAN-FIX.md': 'OBSIDIAN-FIX.md',
            'docs/PATCH-KOMPATIBILITAET.md': 'PATCH-KOMPATIBILITAET.md', 'CHANGELOG.md': 'CHANGELOG.md'}
    allowed = set(MAP_FILES) | {ASSETS, 'modinfo.json'} | set(docs.values())
    if target.exists():
        extras = {p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()} - allowed
        if extras:
            raise ValueError('Unexpected files in release folder: ' + repr(sorted(extras)))
    original = {}
    with zipfile.ZipFile(base_zip) as source:
        for name in MAP_FILES + (ASSETS,):
            payload = source.read('cinis-four-directions/' + name)
            original[name] = digest(payload)
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
    for variant in VARIANTS:
        template = target / f'data/phil/cinis_four_v2/{variant}/cinis_four_v2_{variant}.a7tinfo'
        template.write_bytes(update_playable(template.read_bytes(), 'MapTemplate',
                                            settings['previous_playable_area'], settings['playable_area']))
    # Only Easy stores this v2 playable rectangle in its world file. The flat
    # Medium/Hard worlds retain their original session settings and terrain.
    world = target / 'data/phil/cinis_four_v2/easy/cinis_four_v2_easy.a7t'
    source_entries = rda.entries(str(world))
    if len(source_entries) != 1 or source_entries[0].name != 'gamedata.data':
        raise ValueError('Unexpected world archive members')
    payload = update_playable(rda.read_single(str(world)), 'SessionSettings',
                              settings['previous_playable_area'], settings['playable_area'])
    rdawrite.write_rda(str(world), [('gamedata.data', payload)], timestamp=0)
    if rda.read_single(str(world)) != payload:
        raise AssertionError('Repacked world payload differs')
    assets_path = target / ASSETS
    assets = apply_obsidian_ops(ET.parse(assets_path).getroot(),
                               ET.parse(ROOT / 'config/obsidian-modops.xml').getroot())
    ET.indent(assets, space='  ')
    assets_path.write_bytes((ET.tostring(assets, encoding='unicode') + '\n').encode('utf-8'))
    (target / 'modinfo.json').write_bytes((json.dumps(metadata, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))
    for source, name in docs.items():
        (target / name).write_bytes((ROOT / source).read_text(encoding='utf-8').encode('utf-8'))
    map_changes = [name for name in MAP_FILES if digest((target / name).read_bytes()) != original[name]]
    expected = [f'data/phil/cinis_four_v2/{v}/cinis_four_v2_{v}.a7tinfo' for v in VARIANTS]
    expected.append('data/phil/cinis_four_v2/easy/cinis_four_v2_easy.a7t')
    if set(map_changes) != set(expected):
        raise AssertionError('Unexpected map changes: ' + repr(map_changes))
    files = {name: digest((target / name).read_bytes()) for name in sorted(allowed)}
    archive = output / f'cinis-four-directions-v{version}.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipped:
        for name in files:
            info = zipfile.ZipInfo('cinis-four-directions/' + name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            zipped.writestr(info, (target / name).read_bytes(), compresslevel=6)
    with zipfile.ZipFile(archive) as zipped:
        if len(zipped.namelist()) != len(files):
            raise AssertionError('Unexpected ZIP members')
        for name, sha in files.items():
            if digest(zipped.read('cinis-four-directions/' + name)) != sha:
                raise AssertionError('ZIP payload differs: ' + name)
    checksum = digest(archive.read_bytes())
    archive.with_suffix('.zip.sha256').write_bytes((checksum + '  ' + archive.name + '\n').encode('ascii'))
    report = {'version': version, 'base_version': settings['base_version'], 'base_sha256': settings['base_sha256'],
              'zip_sha256': checksum, 'map_changes': map_changes, 'unchanged_map_files': len(MAP_FILES) - len(map_changes),
              'playable_area': settings['playable_area'], 'only_playable_area_changed_in_map_data': True,
              'file_hashes': files, 'runtime_test': 'NOT RUN'}
    (output / f'build-v{version}.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'version': version, 'folder': str(target), 'zip': str(archive), 'sha256': checksum,
                      'changed_map_files': len(map_changes), 'unchanged_map_files': len(MAP_FILES) - len(map_changes)}, indent=2))
    return target, archive, report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-zip', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--tag')
    args = parser.parse_args()
    source = args.base_zip or download_base(ROOT / 'dist/base/cinis-four-directions-v0.3.2.zip')
    build(source, args.output, args.tag)
