"""Second build stage for version 0.3.0 (runs after MapBuild, see Build-Cinis.ps1).

maps:   * data/phil/cinis_four/easy/*.a7t   is rebuilt so the baked continental terrain matches the
          four Cinis positions stored in existing 0.2.0 savegames (rotation 0).
        * data/phil/cinis_four_v2/<variant>/ is created for new games: Cinis flush in the four corners,
          Rotation90 0/3/2/1, terrain and area IDs rotated accordingly, PlayableArea 268..3828.
assets: writes data/base/config/export/assets.xml (template path, generator settings, horizon islands).

Usage:
  python build_v2.py maps   <mod folder> <vanilla expanded easy gamedata.data>
  python build_v2.py assets <vanilla assets.xml> <mod folder>
"""
import json
import os
import re
import shutil
import struct
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import filedb  # noqa: E402
import rda  # noqa: E402
import rdawrite  # noqa: E402

VARIANTS = (('easy', 3377), ('medium', 44421), ('hard', 44422))
MAP = 4096                # enlarged map size in tiles
BOX = 768                 # Cinis island box (roman_dlc01_island_continental_01)
SAMPLES = 2 * BOX + 1     # height samples per island box (heightmap has 2 samples per tile)
OCEAN = -2559             # height of open sea in the vanilla easy world
VANILLA_SIZE = 2688       # vanilla expanded DLC01 map
VANILLA_CORNER = 1920     # vanilla Cinis position (1920,1920), flush in the corner
SHIFT = 1024              # MapBuild shifts the vanilla world by +1024/+1024

# Positions as stored in 0.2.0 savegames (the save freezes positions and rotations).
OLD_LAYOUT = {'north': ((3200, 3200), 0), 'east': ((3200, 128), 0),
              'south': ((128, 128), 0), 'west': ((128, 3200), 0)}
# New layout: flush in the corners; Rotation90 turns the open coast of each copy towards the map centre.
NEW_LAYOUT = {'north': ((3328, 3328), 0), 'east': ((3328, 0), 3),
              'south': ((0, 0), 2), 'west': ((0, 3328), 1)}
LABELS = {'north': 'roman_dlc01_island_continental_01', 'east': 'cinis_east',
          'south': 'cinis_south', 'west': 'cinis_west'}
# Keeps 248 tiles of every Cinis box outside the playable area, like vanilla (2440 of 2688).
NEW_PLAYABLE = (268, 268, 3828, 3828)


def rotate(grid, k):
    """Rotate a square grid stored as [x][y] by Rotation90=k.
    k=1 maps local (u,v) to (b-v, u) with b = size-1 (measured in a savegame)."""
    return np.rot90(grid, k)


def _check_rotation():
    n = 5
    a = np.arange(n * n).reshape(n, n)
    b = n - 1
    for u in range(n):
        for v in range(n):
            assert rotate(a, 1)[b - v][u] == a[u][v]
            assert rotate(a, 2)[b - u][b - v] == a[u][v]
            assert rotate(a, 3)[v][b - u] == a[u][v]


def heightmap(root):
    node = filedb.find_tag(filedb.find_tag(root, 'TerrainManager')['children'], 'HeightMap')
    width = struct.unpack('<i', filedb.attr(node, 'Width')['data'])[0]
    data = filedb.attr(node, 'HeightMap')['data']
    return np.frombuffer(data, dtype='<i2', count=width * width).reshape(width, width).copy(), node


def area_ids(root, size):
    """Decode the sparse AreaIDs grid (16x16 blocks, stored [x][y])."""
    node = filedb.find_tag(root, 'AreaIDs')
    blocks = [c for c in node['children'] if c.get('tag') == 'block']
    grid = np.zeros((size, size), dtype=np.uint16)
    present = set()
    for block in blocks[1:-1]:
        values = {c['attr']: c['data'] for c in block['children'] if 'attr' in c}
        x = struct.unpack('<H', values['x'])[0] if 'x' in values else 0
        y = struct.unpack('<H', values['y'])[0] if 'y' in values else 0
        if 'values' in values:
            grid[x:x + 16, y:y + 16] = np.frombuffer(values['values'], dtype='<u2').reshape(16, 16)
        elif 'default' in values:
            grid[x:x + 16, y:y + 16] = struct.unpack('<H', values['default'])[0]
        present.add((x, y))
    return grid, node, blocks, present


def write_area_ids(node, blocks, grid, present):
    """Rebuild the block list like vanilla: header block; every previously present block plus every
    non-zero block, ordered y-major; uniform non-zero blocks as mode=2/default, others with values;
    terminator block."""
    header, trailer = blocks[0], blocks[-1]
    coords = set(present)
    nonzero = np.argwhere(grid.reshape(grid.shape[0] // 16, 16, grid.shape[1] // 16, 16).max(axis=(1, 3)) != 0)
    for bx, by in nonzero:
        coords.add((int(bx) * 16, int(by) * 16))
    rebuilt = [header]
    for x, y in sorted(coords, key=lambda c: (c[1], c[0])):
        block = grid[x:x + 16, y:y + 16]
        uniform = block.min() == block.max() and block.max() != 0
        children = []
        if uniform:
            children.append({'attr': 'mode', 'data': bytes([2])})
        if x:
            children.append({'attr': 'x', 'data': struct.pack('<H', x)})
        if y:
            children.append({'attr': 'y', 'data': struct.pack('<H', y)})
        if uniform:
            children.append({'attr': 'default', 'data': struct.pack('<H', int(block.max()))})
        else:
            children.append({'attr': 'values', 'data': block.astype('<u2').tobytes()})
        rebuilt.append({'tag': 'block', 'children': children})
    rebuilt.append(trailer)
    node['children'] = [c for c in node['children'] if 'tag' not in c] + rebuilt


def build_world(base_bytes, vanilla_root, layout, target, playable=None):
    """Move the baked Cinis terrain of the shifted vanilla world to the given layout."""
    root, tags, attrs = filedb.parse(base_bytes)
    height, height_node = heightmap(root)
    vanilla_height, _ = heightmap(vanilla_root)
    assert height.shape == (2 * MAP + 1,) * 2 and vanilla_height.shape == (2 * VANILLA_SIZE + 1,) * 2
    # 1) Remove the shifted vanilla Cinis terrain and the copied vanilla map border (height 0 line).
    s0 = 2 * (VANILLA_CORNER + SHIFT)
    height[s0:s0 + SAMPLES, s0:s0 + SAMPLES] = OCEAN
    edge = 2 * SHIFT + 2 * VANILLA_SIZE
    height[edge, 2 * SHIFT:edge + 1] = OCEAN
    height[2 * SHIFT:edge + 1, edge] = OCEAN
    # 2) Stamp the vanilla corner block at every Cinis position, rotated.
    corner = vanilla_height[2 * VANILLA_CORNER:2 * VANILLA_CORNER + SAMPLES,
                            2 * VANILLA_CORNER:2 * VANILLA_CORNER + SAMPLES]
    for (x, y), k in layout.values():
        block = rotate(corner, k).copy()
        # The vanilla block carries the map border (height 0) on its high-x/high-y edge. Keep border
        # samples only where the rotated edge coincides with the real map border.
        edges = {'x0': block[0, :], 'x1': block[-1, :], 'y0': block[:, 0], 'y1': block[:, -1]}
        real = {'x0': x == 0, 'x1': x + BOX == MAP, 'y0': y == 0, 'y1': y + BOX == MAP}
        for name, samples in edges.items():
            if not real[name]:
                samples[samples == 0] = OCEAN
        height[2 * x:2 * x + SAMPLES, 2 * y:2 * y + SAMPLES] = block
    filedb.attr(height_node, 'HeightMap')['data'] = height.astype('<i2').tobytes()
    # 3) Area IDs (island area markers) get the same treatment.
    grid, node, blocks, present = area_ids(root, MAP)
    vanilla_grid, *_ = area_ids(vanilla_root, VANILLA_SIZE)
    o = VANILLA_CORNER + SHIFT
    grid[o:o + BOX, o:o + BOX] = 0
    marker = vanilla_grid[VANILLA_CORNER:VANILLA_CORNER + BOX, VANILLA_CORNER:VANILLA_CORNER + BOX]
    for (x, y), k in layout.values():
        grid[x:x + BOX, y:y + BOX] = rotate(marker, k)
    write_area_ids(node, blocks, grid, present)
    # 4) PlayableArea in SessionSettings.
    if playable:
        filedb.attr(filedb.find_tag(root, 'SessionSettings'), 'PlayableArea')['data'] = struct.pack('<4i', *playable)
    for name in ('mode', 'x', 'y', 'default', 'values'):
        if name not in attrs.values():
            attrs[max(attrs) + 1] = name
    rdawrite.write_rda(target, [('gamedata.data', filedb.serialize(root, tags, attrs))], timestamp=0)


def require_flat(a7t):
    """Medium/Hard: the vanilla expanded worlds carry no baked terrain (flat height 0)."""
    root, *_ = filedb.parse(rda.read_single(a7t))
    height, _ = heightmap(root)
    if height.min() != 0 or height.max() != 0:
        raise SystemExit(a7t + ': unexpected baked terrain; the Medium/Hard assumption must be re-checked')


def build_template(source, target):
    root, tags, attrs = filedb.parse(open(source, 'rb').read())
    template = filedb.find_tag(root, 'MapTemplate')
    filedb.attr(template, 'PlayableArea')['data'] = struct.pack('<4i', *NEW_PLAYABLE)
    by_label = {LABELS[name]: value for name, value in NEW_LAYOUT.items()}
    changed = 0
    for element in [c for c in template['children'] if c.get('tag') == 'TemplateElement']:
        island = filedb.find_tag(element['children'], 'Element')
        label = filedb.attr(island, 'IslandLabel')
        if label:
            (x, y), k = by_label[label['data'].decode('ascii')]
            filedb.attr(island, 'Position')['data'] = struct.pack('<2i', x, y)
            filedb.attr(island, 'Rotation90')['data'] = bytes([k])
            changed += 1
    if changed != 4:
        raise SystemExit(source + ': expected four labelled Cinis elements, found %d' % changed)
    check_layout(source, layout_json(root))
    with open(target, 'wb') as f:
        f.write(filedb.serialize(root, tags, attrs))
    return root


def check_layout(source, slots):
    """Conservative boxes (max island size per size code, as in MapBuild): every other slot must lie
    inside the new playable area and must not overlap any Cinis box."""
    x0, y0, x1, y1 = NEW_PLAYABLE
    cinis = [s for s in slots if s['kind'] == 'Cinis']
    for s in slots:
        if s['kind'] == 'Cinis':
            continue
        if not (x0 <= s['x'] and y0 <= s['y'] and s['x'] + s['size'] <= x1 and s['y'] + s['size'] <= y1):
            raise SystemExit('%s: slot outside the new playable area: %r' % (source, s))
        for c in cinis:
            if s['x'] < c['x'] + BOX and s['x'] + s['size'] > c['x'] and s['y'] < c['y'] + BOX and s['y'] + s['size'] > c['y']:
                raise SystemExit('%s: slot overlaps %s: %r' % (source, c['label'], s))


def layout_json(root):
    """Same format as MapBuild's .layout.json, plus rotation90 for the Cinis."""
    out = []
    template = filedb.find_tag(root, 'MapTemplate')
    for element in [c for c in template['children'] if c.get('tag') == 'TemplateElement']:
        island = filedb.find_tag(element['children'], 'Element')
        kind_attr = filedb.attr(element, 'ElementType')
        element_type = struct.unpack('<i', kind_attr['data'])[0] if kind_attr else 0
        x, y = struct.unpack('<2i', filedb.attr(island, 'Position')['data'])
        label = filedb.attr(island, 'IslandLabel')
        size_attr = filedb.attr(island, 'Size')
        size_code = struct.unpack('<H', size_attr['data'])[0] if size_attr else 0
        if label:
            kind, size = 'Cinis', BOX
        elif element_type == 2:
            kind, size = 'Start', 0
        else:
            kind, size = 'Random', {0: 256, 1: 320, 2: 512, 3: 512}.get(size_code, 256)
        entry = {'x': x, 'y': y, 'size': size, 'kind': kind, 'sizeCode': size_code,
                 'label': label['data'].decode('ascii') if label else ''}
        if label:
            entry['rotation90'] = filedb.attr(island, 'Rotation90')['data'][0]
        out.append(entry)
    return out


def build_maps(mod, vanilla_easy):
    _check_rotation()
    vanilla_root, *_ = filedb.parse(open(vanilla_easy, 'rb').read())
    for name, _ in VARIANTS:
        old = '%s/data/phil/cinis_four/%s/cinis_four_%s' % (mod, name, name)
        new_dir = '%s/data/phil/cinis_four_v2/%s' % (mod, name)
        new = '%s/cinis_four_v2_%s' % (new_dir, name)
        os.makedirs(new_dir, exist_ok=True)
        if name == 'easy':
            base = rda.read_single(old + '.a7t')   # MapBuild output: shifted vanilla world
            build_world(base, vanilla_root, NEW_LAYOUT, new + '.a7t', playable=NEW_PLAYABLE)
            build_world(base, vanilla_root, OLD_LAYOUT, old + '.a7t')
        else:
            require_flat(old + '.a7t')
            shutil.copyfile(old + '.a7t', new + '.a7t')
        shutil.copyfile(old + '.a7te', new + '.a7te')
        root = build_template(old + '.a7tinfo', new + '.a7tinfo')
        with open(new + '.a7tinfo.layout.json', 'w', encoding='utf-8', newline='\r\n') as f:
            json.dump(layout_json(root), f, indent=2)
        print('PASS: %s old world fixed, v2 template and world written' % name if name == 'easy'
              else 'PASS: %s v2 template written, flat world reused' % name, flush=True)


def build_assets(source, mod):
    text = open(source, encoding='utf-8').read()
    asset = re.search(r'<Asset>(?:(?!<Asset>).)*?<GUID>3377</GUID>.*?</Asset>', text, re.S).group(0)
    horizon = re.search(r'<EnlargedHorizonIslands>(.*?)</EnlargedHorizonIslands>', asset, re.S).group(1)
    scale = MAP / VANILLA_SIZE

    def scaled(c):
        return int(round(c * scale / 4.0)) * 4 if c >= 0 else c

    def rotated(x, z, k):
        # Same Rotation90 convention as the islands, around the map centre.
        u, v = x - MAP // 2, z - MAP // 2
        for _ in range(k % 4):
            u, v = -v, u
        return MAP // 2 + u, MAP // 2 + v

    items, volcanoes = [], []
    for item in re.findall(r'<Item>(.*?)</Item>', horizon, re.S):
        path = re.search(r'<HorizonIslandFile>(.*?)</HorizonIslandFile>', item).group(1)
        x, y, z = (int(re.search(r'<%s>(-?\d+)</%s>' % (t, t), item).group(1)) for t in 'XYZ')
        size = int(re.search(r'<Scale>(\d+)</Scale>', item).group(1))
        rotation = re.search(r'<Rotation>(\d+)</Rotation>', item)
        rotation = int(rotation.group(1)) if rotation else 0
        if 'volcano_mesh' in path:
            volcanoes.append((path, x, y, z, size, rotation))
        else:
            items.append((path, scaled(x), y, scaled(z), size, rotation))
    # The vanilla volcano meshes stand behind the single Cinis corner; repeat them for all four corners.
    for path, x, y, z, size, rotation in volcanoes:
        for k in (0, 3, 2, 1):
            rx, rz = rotated(scaled(x), scaled(z), k)
            items.append((path, int(rx), y, int(rz), size, (rotation + 90 * k) % 360))

    def item_xml(path, x, y, z, size, rotation):
        return ('      <Item>\n        <HorizonIslandFile>%s</HorizonIslandFile>\n        <Position>\n'
                '          <X>%d</X>\n          <Y>%d</Y>\n          <Z>%d</Z>\n        </Position>\n'
                '        <Scale>%d</Scale>\n' % (path, x, y, z, size)
                + ('        <Rotation>%d</Rotation>\n' % rotation if rotation else '') + '      </Item>\n')

    horizon_xml = ''.join(item_xml(*i) for i in items)
    ops = []
    for name, guid in VARIANTS:
        ops.append('''  <!-- %(n)s: new template for new games (old path data/phil/cinis_four/%(n)s stays for running saves) -->
  <ModOp GUID="%(g)d" Merge="MapTemplate">
    <MapTemplate>
      <EnlargedTemplateFilename>data/phil/cinis_four_v2/%(n)s/cinis_four_v2_%(n)s.a7t</EnlargedTemplateFilename>
      <Attraction>
        <WiggleIterationCount>0</WiggleIterationCount>
        <ShrinkWorld>0</ShrinkWorld>
      </Attraction>
    </MapTemplate>
  </ModOp>
  <ModOp GUID="%(g)d" Replace="MapTemplate/EnlargedHorizonIslands">
    <EnlargedHorizonIslands>
%(h)s    </EnlargedHorizonIslands>
  </ModOp>
''' % {'n': name, 'g': guid, 'h': horizon_xml})
    target = mod + '/data/base/config/export'
    os.makedirs(target, exist_ok=True)
    with open(target + '/assets.xml', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('<ModOps>\n' + ''.join(ops) + '</ModOps>\n')
    print('PASS: assets.xml written, %d horizon items per template' % len(items))


if __name__ == '__main__':
    if len(sys.argv) != 4 or sys.argv[1] not in ('maps', 'assets'):
        raise SystemExit(__doc__)
    if sys.argv[1] == 'maps':
        build_maps(sys.argv[2], sys.argv[3])
    else:
        build_assets(sys.argv[2], sys.argv[3])
