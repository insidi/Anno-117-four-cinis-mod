"""Build the obsidian update from an existing 0.3.x mod, without rebuilding its maps.

Only uses the Python standard library. Does not modify the input mod or savegames.
Usage: python scripts/build_obsidian_fix.py --source <installed-or-unpacked-0.3.x-folder>
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def file_hashes(folder):
    return {p.relative_to(folder).as_posix(): sha256(p)
            for p in sorted(folder.rglob('*')) if p.is_file()}


def apply_obsidian_ops(existing, fragment):
    if existing.tag != 'ModOps' or fragment.tag != 'ModOps':
        raise ValueError('Expected ModOps roots')
    # Replace our exact operations on repeated builds rather than accumulating duplicates.
    for op in fragment:
        for previous in list(existing):
            if (previous.get('GUID'), previous.get('Replace')) == (op.get('GUID'), op.get('Replace')):
                existing.remove(previous)
        existing.append(copy.deepcopy(op))
    return existing


def build(source):
    source = Path(source).resolve()
    target = ROOT / 'dist/cinis-four-directions'
    if source == target.resolve() or source in target.resolve().parents or target.resolve() in source.parents:
        raise ValueError('Source and destination must be separate, non-nested directories')
    info = json.loads((source / 'modinfo.json').read_text(encoding='utf-8-sig'))
    if info.get('ModID') != 'cinis-four-directions-phil' or info.get('Version') not in ('0.3.0', '0.3.1', '0.3.2'):
        raise ValueError('Expected the four-Cinis mod version 0.3.0, 0.3.1 or 0.3.2')
    for layout in ('cinis_four', 'cinis_four_v2'):
        for variant in ('easy', 'medium', 'hard'):
            for suffix in ('.a7t', '.a7te', '.a7tinfo'):
                required = source / f'data/phil/{layout}/{variant}/{layout}_{variant}{suffix}'
                if not required.is_file():
                    raise ValueError(f'Missing map component: {required}')
    source_before = file_hashes(source)
    before = file_hashes(source / 'data')
    fragment = ET.parse(ROOT / 'config/obsidian-modops.xml').getroot()
    metadata = json.loads((ROOT / 'config/modinfo.json').read_text(encoding='utf-8-sig'))
    if target.exists():
        # Never silently include stale files from another working build.
        allowed = {'modinfo.json', 'README.md', 'OBSIDIAN-FIX.md'} | {'data/' + p for p in before}
        extras = set(file_hashes(target)) - allowed
        if extras:
            raise ValueError(f'Destination contains unexpected files: {sorted(extras)}')
    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source / 'data', target / 'data', dirs_exist_ok=True)
    assets = target / 'data/base/config/export/assets.xml'
    patched = apply_obsidian_ops(ET.parse(assets).getroot(), fragment)
    ET.indent(patched, space='  ')
    assets.write_text(ET.tostring(patched, encoding='unicode') + '\n', encoding='utf-8')
    (target / 'modinfo.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    shutil.copyfile(ROOT / 'docs/TESTANLEITUNG.md', target / 'README.md')
    shutil.copyfile(ROOT / 'docs/OBSIDIAN-FIX.md', target / 'OBSIDIAN-FIX.md')
    after = file_hashes(target / 'data')
    changed = [p for p in before if before[p] != after.get(p)]
    if set(before) != set(after) or set(changed) - {'base/config/export/assets.xml'}:
        raise AssertionError(f'Unexpected gameplay file changes: {changed}')
    if file_hashes(source) != source_before:
        raise AssertionError('Source mod changed during packaging')
    archive = ROOT / f'dist/cinis-four-directions-v{metadata["Version"]}.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(target.rglob('*')):
            if path.is_file():
                z.write(path, 'cinis-four-directions/' + path.relative_to(target).as_posix())
    # Verify every archived file against the folder that all peers will install.
    with zipfile.ZipFile(archive) as z:
        for name, digest in file_hashes(target).items():
            if hashlib.sha256(z.read('cinis-four-directions/' + name)).hexdigest() != digest:
                raise AssertionError('ZIP verification failed: ' + name)
    archive.with_suffix('.zip.sha256').write_text(sha256(archive) + '  ' + archive.name + '\n', encoding='ascii')
    report = {
        'version': metadata['Version'], 'source_version': info['Version'],
        'changed_data_files': changed, 'unchanged_data_files': len(before) - len(changed),
        'source_files_unchanged': True,
        'zip_sha256': sha256(archive), 'zip_files_verified': True,
        'runtime_test': 'NOT RUN: check stock on all four Cinis at the next eruption',
    }
    (ROOT / 'research').mkdir(exist_ok=True)
    (ROOT / 'research/obsidian-package-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    print(archive)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    build(parser.parse_args().source)
