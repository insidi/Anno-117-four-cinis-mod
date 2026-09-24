"""Writer for single-block RDA 2.2 archives.

The game only opened .a7t archives whose zlib streams use compression level 1
(stream header 0x78 0x01); higher levels failed with "Failed opening file".
"""
import struct
import zlib

ZLIB_LEVEL = 1


def write_rda(path, files, timestamp=0):
    """files: list of (name, bytes). Writes one zlib-compressed block."""
    out = bytearray(b'Resource File V2.2')
    out.extend(bytes(0x310 - len(out)))
    out.extend(struct.pack('<Q', 0))  # first block offset, patched below
    placed = []
    for name, data in files:
        packed = zlib.compress(data, ZLIB_LEVEL)
        placed.append((name, len(out), len(packed), len(data)))
        out.extend(packed)
    directory = bytearray()
    for name, offset, csize, size in placed:
        encoded = name.encode('utf-16le')
        directory.extend(encoded + bytes(520 - len(encoded)))
        directory.extend(struct.pack('<5Q', offset, csize, size, timestamp, 0))
    packed_dir = zlib.compress(bytes(directory), ZLIB_LEVEL)
    out.extend(packed_dir)
    block = len(out)
    out.extend(struct.pack('<IIQQQ', 1, len(placed), len(packed_dir), len(directory), block + 32))
    struct.pack_into('<Q', out, 0x310, block)
    with open(path, 'wb') as f:
        f.write(out)
