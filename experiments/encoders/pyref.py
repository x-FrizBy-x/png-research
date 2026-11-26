"""pyref: transparent reference PNG encoder (numpy filtering + zlib).

This is the baseline that our experiments modify. Each stage is a plain function so a
hypothesis can swap one stage (filter choice, DEFLATE backend, ...) and leave the rest
unchanged.

Stages: RawImage -> filter_all (5 candidates per row) -> choose_filters -> deflate -> chunks.
It keeps the source colour type and bit depth (no reductions) and writes no metadata.
"""
from __future__ import annotations

import struct
import zlib

import numpy as np

from harness.pngio import RawImage

SIGNATURE = b"\x89PNG\r\n\x1a\n"
FILTERS = ("none", "sub", "up", "avg", "paeth")  # index == PNG filter type byte


def filter_all(scan: np.ndarray, bpp: int) -> np.ndarray:
    """Apply all five PNG filters to every row. Returns (5, H, stride) uint8.

    Encode-side filtering reads only *unfiltered* neighbours, so the whole image can be
    filtered in one vectorised pass (unlike decoding, where each row depends on the last).
    """
    x = scan.astype(np.int16)
    left = np.zeros_like(x); left[:, bpp:] = x[:, :-bpp]
    up = np.zeros_like(x); up[1:] = x[:-1]
    ul = np.zeros_like(x); ul[1:, bpp:] = x[:-1, :-bpp]
    p = left + up - ul
    pa, pb, pc = np.abs(p - left), np.abs(p - up), np.abs(p - ul)
    paeth = np.where((pa <= pb) & (pa <= pc), left, np.where(pb <= pc, up, ul))
    out = np.stack([x, x - left, x - up, x - ((left + up) >> 1), x - paeth])
    return (out & 0xFF).astype(np.uint8)


def choose_filters(filtered: np.ndarray, strategy: str) -> np.ndarray:
    """Per-row filter type, shape (H,). Strategies: a fixed filter name, or 'minsum'
    (libpng's heuristic: minimise the sum of |byte as int8|)."""
    h = filtered.shape[1]
    if strategy in FILTERS:
        return np.full(h, FILTERS.index(strategy), dtype=np.intp)
    if strategy == "minsum":
        cost = np.abs(filtered.view(np.int8).astype(np.int32)).sum(axis=2)  # (5, H)
        return cost.argmin(axis=0)
    raise ValueError(f"unknown filter strategy {strategy!r}")


def deflate(data: bytes, level: int = 9, mem_level: int = 9,
            strategy: int = zlib.Z_DEFAULT_STRATEGY) -> bytes:
    c = zlib.compressobj(level, zlib.DEFLATED, 15, mem_level, strategy)
    return c.compress(data) + c.flush()


def _chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def encode(img: RawImage, filter_strategy: str = "minsum", level: int = 9) -> bytes:
    filtered = filter_all(img.scanlines, img.bpp)
    types = choose_filters(filtered, filter_strategy)
    rows = filtered[types, np.arange(img.height)]
    stream = np.concatenate([types.astype(np.uint8)[:, None], rows], axis=1).tobytes()

    ihdr = struct.pack(">IIBBBBB", img.width, img.height, img.bitdepth, img.colour_type, 0, 0, 0)
    parts = [SIGNATURE, _chunk(b"IHDR", ihdr)]
    if img.plte:
        parts.append(_chunk(b"PLTE", img.plte))
    if img.trns:
        parts.append(_chunk(b"tRNS", img.trns))
    parts += [_chunk(b"IDAT", deflate(stream, level)), _chunk(b"IEND", b"")]
    return b"".join(parts)
