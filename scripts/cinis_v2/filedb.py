"""FileDB version 3 reader/writer (.a7tinfo and gamedata.data).

Node stream: [i32 size][i32 id]; id < 0x8000 opens a tag (size 0), 0/0 closes it,
id >= 0x8000 is an attribute whose payload is padded to 8 bytes.
Footer (20 bytes): node count + 1, tag dictionary offset, attribute dictionary offset, 8, -3.
Nodes are dicts: {'tag': name, 'children': [...]} or {'attr': name, 'data': bytes}.
"""
import struct

NONE_TAG = 1        # list item tag "None"
COUNT_ATTR = 32768  # implicit attribute "count"


def _read_dict(b, off):
    count = struct.unpack_from('<I', b, off)[0]
    p = off + 4
    ids = struct.unpack_from('<%dH' % count, b, p)
    p += 2 * count
    names = {}
    for i in ids:
        end = b.index(b'\0', p)
        names[i] = b[p:end].decode('utf-8', 'replace')
        p = end + 1
    return names


def parse(b):
    """Return (root nodes, tag dict, attribute dict)."""
    _, tag_off, attr_off, _, version = struct.unpack_from('<iiiii', b, len(b) - 20)
    if version != -3:
        raise ValueError('not a FileDB version 3 document')
    tags = _read_dict(b, tag_off)
    attrs = _read_dict(b, attr_off)
    # Some documents declare "None"/"count" explicitly and still use the implicit ids.
    none_name = '#None' if 'None' in tags.values() else 'None'
    count_name = '#count' if 'count' in attrs.values() else 'count'
    root = []
    stack = [root]
    p = 0
    while p < tag_off:
        size, ident = struct.unpack_from('<ii', b, p)
        p += 8
        if size == 0 and ident == 0:
            stack.pop()
            if not stack:
                break
            continue
        if size == 0 and ident < 0x8000:
            name = tags.get(ident, none_name if ident == NONE_TAG else 'TAG%d' % ident)
            node = {'tag': name, 'children': []}
            stack[-1].append(node)
            stack.append(node['children'])
        else:
            name = attrs.get(ident, count_name if ident == COUNT_ATTR else 'ATTR%d' % ident)
            stack[-1].append({'attr': name, 'data': b[p:p + size]})
            p += size
            if p % 8:
                p += 8 - p % 8
    return root, tags, attrs


def _align8(n):
    return (n + 7) // 8 * 8


def _dict_bytes(d):
    out = bytearray(struct.pack('<I', len(d)))
    for k in d:
        out.extend(struct.pack('<H', k))
    for k in d:
        out.extend(d[k].encode('utf-8'))
        out.append(0)
    return out


def serialize(root, tags, attrs):
    tag_id = {v: k for k, v in tags.items()}
    attr_id = {v: k for k, v in attrs.items()}
    tag_id.setdefault('None', NONE_TAG)
    tag_id['#None'] = NONE_TAG
    attr_id.setdefault('count', COUNT_ATTR)
    attr_id['#count'] = COUNT_ATTR
    out = bytearray()
    count = 0

    def emit(nodes):
        nonlocal count
        for node in nodes:
            count += 1
            if 'tag' in node:
                out.extend(struct.pack('<ii', 0, tag_id[node['tag']]))
                emit(node['children'])
                out.extend(struct.pack('<ii', 0, 0))
            else:
                data = node['data']
                out.extend(struct.pack('<ii', len(data), attr_id[node['attr']]))
                out.extend(data)
                if len(data) % 8:
                    out.extend(bytes(8 - len(data) % 8))

    emit(root)
    out.extend(struct.pack('<ii', 0, 0))
    tag_off = len(out)
    out.extend(_dict_bytes(tags))
    out.extend(bytes(_align8(len(out)) - len(out)))
    attr_off = len(out)
    out.extend(_dict_bytes(attrs))
    footer = _align8(len(out)) + 4
    out.extend(bytes(footer - len(out)))
    out.extend(struct.pack('<iiiii', count + 1, tag_off, attr_off, 8, -3))
    return bytes(out)


def find_tag(nodes, name):
    """Depth-first search for the first tag with the given name."""
    for node in nodes:
        if 'tag' in node:
            if node['tag'] == name:
                return node
            found = find_tag(node['children'], name)
            if found:
                return found
    return None


def attr(node, name):
    for child in node['children']:
        if child.get('attr') == name:
            return child
    return None
