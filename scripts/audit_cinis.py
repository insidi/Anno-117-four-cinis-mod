"""Read-only audit of installed Cinis patches and every packaged island instance.

Needs numpy (the map build dependency). Extracted game data stays under research/.
Never writes to the game installation, installed mods or savegames.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'tools/python-libs'), str(ROOT / 'scripts/cinis_v2')]
import numpy as np
import build_v2 as maps
import filedb
import rda

ASSETS = 'data/base/config/export/assets.xml'
CINIS = ('data/dlc01/provinces/roman/islands/pool/roman_dlc01_island_continental_01/'
         'roman_dlc01_island_continental_01.a7m')
VARIANTS = {'easy': '3377', 'medium': '44421', 'hard': '44422'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def playable(nodes):
    template = filedb.find_tag(nodes, 'MapTemplate')
    return struct.unpack('<4i', filedb.attr(template, 'PlayableArea')['data'])


def cinis_elements(nodes):
    template = filedb.find_tag(nodes, 'MapTemplate')
    result = []
    for wrapper in template['children']:
        if wrapper.get('tag') != 'TemplateElement':
            continue
        island = filedb.find_tag(wrapper['children'], 'Element')
        path = filedb.attr(island, 'MapFilePath')
        if path and path['data'].decode('utf-16le') == CINIS:
            result.append(island)
    return result


def visible_areas(grid, position, rotation, rectangle):
    rotated = np.rot90(grid, rotation)
    x, y = position
    x0, y0, x1, y1 = rectangle
    visible = np.zeros_like(rotated)
    sx = slice(max(0, x0 - x), min(768, x1 - x))
    sy = slice(max(0, y0 - y), min(768, y1 - y))
    visible[sx, sy] = rotated[sx, sy]
    # Normalize each rotated copy back to original local coordinates. Restrict
    # comparison to land/coast; ocean margins differ by design on the larger map.
    visible = np.rot90(visible, -rotation)
    return np.where((visible == 8193) | (visible == 16385), visible, 0)


def audit(game, mod, destination):
    game, mod, destination = Path(game), Path(mod), Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    settings = json.loads((ROOT / 'config/release.json').read_text(encoding='utf-8'))
    manifest = (game.parents[1] / 'appmanifest_3274580.acf').read_text(encoding='utf-8')
    build = re.search(r'"buildid"\s+"(\d+)"', manifest).group(1)
    with (game / 'Bin/Win64/Anno117.exe').open('rb') as stream:
        exe_sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    if build != settings['checked_steam_build'] or exe_sha != settings['checked_executable_sha256']:
        raise ValueError('Game build changed: verify patch version/native semantics and update release.json first')
    maindata = game / 'maindata'
    winners, history, inventory = {}, [], []
    # Scan every RDA directory, with numbered patch archives taking precedence.
    archives = sorted(maindata.glob('*.rda'), key=lambda p: (p.name.startswith('zz_patchfiles_'), p.name))
    for archive in archives:
        entries = rda.entries(str(archive))
        inventory.append({'archive': archive.name, 'entries': len(entries)})
        for entry in entries:
            name = entry.name
            relevant = name in (CINIS, CINIS + 'info', ASSETS) or (
                'roman_province_default_01_' in name and 'dlc01expanded' in name
                and name.endswith(('.a7t', '.a7tinfo')))
            if not relevant:
                continue
            winners[name] = (archive, entry)
            if name == CINIS:
                data = rda.read_entry(str(archive), entry)
                target = destination / (archive.stem + '-cinis.a7m')
                target.write_bytes(data)
                roots, *_ = filedb.parse(rda.read_single(str(target)))
                grid, *_ = maps.area_ids(roots, 768)
                height, _ = maps.heightmap(roots)
                history.append({'archive': archive.name, 'sha256': sha(data),
                                'land_tiles': int(np.count_nonzero(grid == 8193)),
                                'coast_tiles': int(np.count_nonzero(grid == 16385)),
                                'height_sha256': sha(height.tobytes()), 'area_grid_sha256': sha(grid.tobytes())})
    required = (ASSETS, CINIS, CINIS + 'info')
    for name in required:
        if name not in winners:
            raise ValueError('Missing current resource: ' + name)

    def current(name):
        archive, entry = winners[name]
        return rda.read_entry(str(archive), entry)

    assets_bytes = current(ASSETS)
    (destination / 'current-assets.xml').write_bytes(assets_bytes)
    assets = ET.fromstring(assets_bytes)
    asset_ids = {}
    for asset in assets.iter('Asset'):
        guid = asset.findtext('Values/Standard/GUID')
        if guid:
            if guid in asset_ids:
                raise ValueError('Duplicate game GUID: ' + guid)
            asset_ids[guid] = asset
    if asset_ids['145426'].findtext('Values/Island/NameOfIsland') != 'roman_dlc01_island_continental_01':
        raise ValueError('Original Cinis identity changed')
    ops = ET.parse(mod / ASSETS).getroot()
    if len(ops) != 12 or ops.find('.//Asset') is not None:
        raise ValueError('Unexpected asset creation or operation count')
    for op in ops:
        if op.get('GUID') not in asset_ids:
            raise ValueError('Invalid ModOp target GUID')
    if {op.get('GUID') for op in ops} != {'3377', '44421', '44422', '144830', '144837'}:
        raise ValueError('Unexpected changed GUIDs')
    if list(mod.rglob('*.a7m')) or list(mod.rglob('*.a7minfo')):
        raise ValueError('Mod must use the patched original island instead of freezing a copy')
    island_path = destination / 'current-cinis.a7m'
    island_path.write_bytes(current(CINIS))
    island, *_ = filedb.parse(rda.read_single(str(island_path)))
    grid, *_ = maps.area_ids(island, 768)
    results = []
    for variant, guid in VARIANTS.items():
        world_name = asset_ids[guid].findtext('Values/MapTemplate/EnlargedTemplateFilename')
        info_name = world_name + 'info'
        native_info, *_ = filedb.parse(current(info_name))
        native_cinis = cinis_elements(native_info)
        if len(native_cinis) != 1:
            raise ValueError('Expected one original Cinis in vanilla template')
        native_position = struct.unpack('<2i', filedb.attr(native_cinis[0], 'Position')['data'])
        native_rect = playable(native_info)
        native_visible = visible_areas(grid, native_position, 0, native_rect)
        margin = maps.VANILLA_SIZE - native_rect[2]
        expected_rect = (margin, margin, maps.MAP - margin, maps.MAP - margin)
        world_path = destination / Path(world_name).name
        world_path.write_bytes(current(world_name))
        native_world, *_ = filedb.parse(rda.read_single(str(world_path)))
        native_height, _ = maps.heightmap(native_world)
        native_grid, *_ = maps.area_ids(native_world, maps.VANILLA_SIZE)
        for layout, positions in (('cinis_four', maps.OLD_LAYOUT), ('cinis_four_v2', maps.NEW_LAYOUT)):
            prefix = mod / f'data/phil/{layout}/{variant}/{layout}_{variant}'
            template, *_ = filedb.parse(prefix.with_suffix('.a7tinfo').read_bytes())
            instances = cinis_elements(template)
            if len(instances) != 4:
                raise ValueError('Expected four Cinis in ' + str(prefix))
            rectangle = playable(template)
            if layout == 'cinis_four_v2' and rectangle != expected_rect:
                raise ValueError(f'{variant}: playable area {rectangle} differs from native margin {expected_rect}')
            labels = [filedb.attr(i, 'IslandLabel')['data'].decode('ascii') for i in instances]
            if len(set(labels)) != 4 or set(labels) != set(maps.LABELS.values()):
                raise ValueError('Missing/duplicate island labels')
            world, *_ = filedb.parse(rda.read_single(str(prefix.with_suffix('.a7t'))))
            height, _ = maps.heightmap(world)
            world_grid = maps.area_ids(world, maps.MAP)[0] if variant == 'easy' else None
            for direction, (position, rotation) in positions.items():
                instance = instances[labels.index(maps.LABELS[direction])]
                if struct.unpack('<2i', filedb.attr(instance, 'Position')['data']) != position:
                    raise ValueError('Island position changed')
                if filedb.attr(instance, 'Rotation90')['data'] != bytes([rotation]):
                    raise ValueError('Island rotation changed')
                invariant = lambda node: [c for c in node['children'] if c.get('attr') not in ('Position', 'Rotation90', 'IslandLabel')]
                if invariant(instance) != invariant(native_cinis[0]):
                    raise ValueError('Island instance overrides the current original definition')
                visible = visible_areas(grid, position, rotation, rectangle)
                if layout == 'cinis_four_v2' and not np.array_equal(visible, native_visible):
                    raise ValueError('Buildable/coast mask differs from original: ' + direction)
                x, y = position
                if variant == 'easy':
                    corner = native_height[3840:5377, 3840:5377]
                    expected_height = np.rot90(corner, rotation).copy()
                    for samples, real_border in ((expected_height[0, :], x == 0),
                                                 (expected_height[-1, :], x + 768 == 4096),
                                                 (expected_height[:, 0], y == 0),
                                                 (expected_height[:, -1], y + 768 == 4096)):
                        if not real_border:
                            samples[samples == 0] = maps.OCEAN
                    if not np.array_equal(height[2*x:2*x+1537, 2*y:2*y+1537], expected_height):
                        raise ValueError('Baked terrain differs from current vanilla world')
                    if not np.array_equal(world_grid[x:x+768, y:y+768],
                                          np.rot90(native_grid[1920:2688, 1920:2688], rotation)):
                        raise ValueError('Baked area markers differ from current vanilla world')
                elif np.any(height) or np.any(native_height):
                    raise ValueError('Medium/Hard flat-world assumption no longer holds')
                results.append({'layout': layout, 'variant': variant, 'direction': direction,
                                'position': position, 'rotation90': rotation, 'playable_area': rectangle,
                                'land_tiles_in_playable_area': int(np.count_nonzero(visible == 8193)),
                                'coast_tiles_in_playable_area': int(np.count_nonzero(visible == 16385)),
                                'uses_current_original_island': True, 'terrain_verified': True})
    report = {'result': 'PASS', 'game_version': settings['checked_game_version'], 'steam_build': build,
              'executable_sha256': exe_sha,
              'assets_sha256': sha(assets_bytes), 'cinis_source': winners[CINIS][0].name,
              'cinis_sha256': sha(current(CINIS)), 'cinis_info_sha256': sha(current(CINIS + 'info')),
              'archives_scanned': inventory, 'island_history': history, 'instances': results,
              'runtime_test': 'NOT RUN; multiplayer, eruptions and loading existing saves require in-game tests'}
    (destination / 'audit.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'result': 'PASS', 'archives': len(inventory), 'instances_checked': len(results),
                      'current_cinis_source': report['cinis_source'], 'report': str(destination / 'audit.json')}, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', required=True, type=Path)
    parser.add_argument('--mod', required=True, type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'research/compatibility-audit')
    args = parser.parse_args()
    audit(args.game, args.mod, args.output)
