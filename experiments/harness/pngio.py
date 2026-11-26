"""PNG I/O helpers shared by the harness and in-process encoders.

- decode_canonical(): any PNG -> uint16 RGBA array, used for lossless verification.
- load_raw(): any PNG -> RawImage (unfiltered scanline bytes in the source's own
  colour type / bit depth), the input format for in-process encoders.

Both use pypng's read(), which returns raw samples (no sBIT rescaling and no gamma), so
two files count as equal when their stored sample values are equal.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import png


def _read(path: Path):
    w, h, rows, info = png.Reader(filename=str(path)).read()
    a = np.asarray(list(rows), dtype=np.uint32)  # (h, w*planes), unpacked samples
    return w, h, a, info


def decode_canonical(path: Path) -> np.ndarray:
    """Decode to (H, W, 4) uint16 RGBA, every bit depth scaled exactly to 0..65535.

    Palette and tRNS are applied, so a palette image and an equivalent truecolour image
    compare equal. Exact for bit depths 1/2/4/8/16 (65535 is divisible by 2^bd - 1).
    """
    w, h, a, info = _read(path)
    planes = info["planes"]
    a = a.reshape(h, w, planes)
    if "palette" in info:
        pal = np.array([tuple(p) + (255,) * (4 - len(p)) for p in info["palette"]], dtype=np.uint32)
        return (pal[a[..., 0]] * 257).astype(np.uint16)
    maxv = (1 << info["bitdepth"]) - 1
    colour = np.repeat(a[..., :1], 3, axis=2) if info["greyscale"] else a[..., :3]
    if info["alpha"]:
        alpha = a[..., -1:]
    else:
        alpha = np.full((h, w, 1), maxv, dtype=np.uint32)
        key = info.get("transparent")
        if key is not None:
            alpha[np.all(a == np.atleast_1d(key), axis=2)] = 0
    return (np.concatenate([colour, alpha], axis=2) * (65535 // maxv)).astype(np.uint16)


def compare(src: np.ndarray, out: np.ndarray) -> str:
    """'exact' | 'alpha-equiv' (differs only in colour under alpha=0) | 'MISMATCH'."""
    if src.shape != out.shape:
        return "MISMATCH"
    if np.array_equal(src, out):
        return "exact"
    visible = (src[..., 3] != 0) | (out[..., 3] != 0)
    return "alpha-equiv" if np.array_equal(src[visible], out[visible]) else "MISMATCH"


@dataclass
class RawImage:
    width: int
    height: int
    bitdepth: int
    colour_type: int          # PNG colour type: 0 grey, 2 RGB, 3 palette, 4 grey+A, 6 RGBA
    bpp: int                  # bytes per complete pixel, min 1 (the filter "bpp")
    scanlines: np.ndarray     # (H, stride) uint8, unfiltered, packed as stored in PNG
    plte: bytes | None = None
    trns: bytes | None = None


def load_raw(path: Path) -> RawImage:
    w, h, a, info = _read(path)
    bd, planes = info["bitdepth"], info["planes"]
    if bd == 16:
        scan = a.astype(">u2").view(np.uint8).reshape(h, -1)
    elif bd == 8:
        scan = a.astype(np.uint8)
    else:  # pack 1/2/4-bit samples, MSB first, rows padded to a byte boundary
        per = 8 // bd
        v = np.pad(a, ((0, 0), (0, (-a.shape[1]) % per))).astype(np.uint8).reshape(h, -1, per)
        shifts = (bd * np.arange(per - 1, -1, -1)).astype(np.uint8)
        scan = (v << shifts).sum(axis=2).astype(np.uint8)

    plte = trns = None
    if "palette" in info:
        ct = 3
        pal = info["palette"]
        plte = bytes(c for p in pal for c in p[:3])
        alphas = [p[3] if len(p) == 4 else 255 for p in pal]
        while alphas and alphas[-1] == 255:
            alphas.pop()
        trns = bytes(alphas) or None
    else:
        ct = (0 if info["greyscale"] else 2) | (4 if info["alpha"] else 0)
        if info.get("transparent") is not None:
            trns = np.atleast_1d(info["transparent"]).astype(">u2").tobytes()

    return RawImage(w, h, bd, ct, max(1, planes * bd // 8), np.ascontiguousarray(scan), plte, trns)
