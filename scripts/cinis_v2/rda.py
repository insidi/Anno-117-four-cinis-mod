"""Minimal reader for RDA "Resource File V2.2" archives (.a7t map worlds)."""
import os
import struct
import zlib

HEADER_OFFSET = 0x310   # u64 offset of the first block header
DIR_ENTRY_SIZE = 560    # 520 bytes UTF-16 file name + 5 x u64


class Entry:
    __slots__ = ('name', 'offset', 'csize', 'size', 'timestamp', 'flags')


def entries(path):
    """Return all directory entries of an RDA 2.2 archive."""
    out = []
    size = os.path.getsize(path)
    with open(path, 'rb') as f:
        if f.read(18) != b'Resource File V2.2':
            raise ValueError(path + ': not an RDA 2.2 archive')
        f.seek(HEADER_OFFSET)
        offset = struct.unpack('<Q', f.read(8))[0]
        while offset and offset < size:
            f.seek(offset)
            flags, count, dir_size, _dec_size, next_block = struct.unpack('<IIQQQ', f.read(32))
            if flags & 6:
                raise ValueError(path + ': encrypted or memory-resident blocks are not supported')
            f.seek(offset - dir_size)
            directory = f.read(dir_size)
            if flags & 1:
                directory = zlib.decompress(directory)
            for i in range(count):
                raw = directory[i * DIR_ENTRY_SIZE:(i + 1) * DIR_ENTRY_SIZE]
                e = Entry()
                e.name = raw[:520].decode('utf-16le').split('\0')[0]
                e.offset, e.csize, e.size, e.timestamp, _ = struct.unpack('<5Q', raw[520:560])
                e.flags = flags
                out.append(e)
            if next_block == offset or next_block >= size:
                break
            offset = next_block
    return out


def read_entry(path, entry):
    with open(path, 'rb') as f:
        f.seek(entry.offset)
        data = f.read(entry.csize)
    return zlib.decompress(data) if entry.flags & 1 else data


def read_single(path, name='gamedata.data'):
    """Return the payload of the named file inside the archive."""
    for e in entries(path):
        if e.name == name:
            return read_entry(path, e)
    raise KeyError(name)
