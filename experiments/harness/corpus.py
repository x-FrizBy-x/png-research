"""Corpus management.

  python -m harness.corpus synth     # (re)generate corpus/synthetic/ smoke-test images
  python -m harness.corpus manifest  # rebuild corpus/manifest.csv from corpus/<category>/**.png
  python -m harness.corpus check     # verify files still match the manifest's sha256

Category = first folder under corpus/. The manifest is versioned and the images are not.
Once an experiment has used a manifest, add files instead of editing existing ones.
"""
from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

import numpy as np
import png

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "corpus"
MANIFEST = CORPUS / "manifest.csv"
FIELDS = ["path", "category", "width", "height", "colour_type", "bitdepth", "bytes", "sha256"]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build_manifest() -> int:
    rows = []
    for p in sorted(CORPUS.glob("*/**/*.png")):
        r = png.Reader(filename=str(p))
        r.preamble()
        rel = p.relative_to(CORPUS)
        rows.append(dict(path=rel.as_posix(), category=rel.parts[0], width=r.width, height=r.height,
                         colour_type=r.color_type, bitdepth=r.bitdepth, bytes=p.stat().st_size,
                         sha256=sha256(p)))
    with MANIFEST.open("w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} files -> {MANIFEST}")
    return 0


def load_manifest(path: Path = MANIFEST) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def check(path: Path = MANIFEST) -> list[str]:
    """Return a list of problems (missing / changed files)."""
    problems = []
    for row in load_manifest(path):
        p = CORPUS / row["path"]
        if not p.exists():
            problems.append(f"missing: {row['path']}")
        elif sha256(p) != row["sha256"]:
            problems.append(f"changed: {row['path']}")
    return problems


def synth() -> int:
    """Small deterministic images covering every colour type and bit depth. For checking
    the harness works, not for drawing compression conclusions."""
    rng = np.random.default_rng(20261126)
    out = CORPUS / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    W = H = 256
    yy, xx = np.mgrid[0:H, 0:W]

    def write(name, arr, **kw):
        h = arr.shape[0]
        w_ = kw.pop("width")
        with (out / f"{name}.png").open("wb") as f:
            png.Writer(w_, h, **kw).write(f, arr.reshape(h, -1).tolist())

    grad = ((xx + yy) / 2).astype(np.uint8)
    write("grey8_gradient", grad, width=W, greyscale=True, bitdepth=8)
    write("grey1_checker", ((xx // 8 + yy // 8) % 2).astype(np.uint8), width=W, greyscale=True, bitdepth=1)
    write("grey4_bands", (yy // 16).astype(np.uint8), width=W, greyscale=True, bitdepth=4)
    write("grey16_gradient", (xx * 256 + yy).astype(np.uint16), width=W, greyscale=True, bitdepth=16)
    write("greya8_vignette", np.dstack([grad, (255 - np.hypot(xx - 128, yy - 128)).clip(0, 255).astype(np.uint8)]),
          width=W, greyscale=True, alpha=True, bitdepth=8)

    # "photo-like": smooth fields + mild noise
    base = np.dstack([np.sin(xx / 23) * 60 + 128, np.cos(yy / 17) * 60 + 128, (xx + yy) / 4 + 30])
    photo = (base + rng.normal(0, 6, base.shape)).clip(0, 255).astype(np.uint8)
    write("rgb8_photolike", photo, width=W, greyscale=False, bitdepth=8)
    write("rgb8_noise", rng.integers(0, 256, (H, W, 3), dtype=np.uint8), width=W, greyscale=False, bitdepth=8)

    # "screenshot-like": flat background, flat rectangles, thin 'text' lines
    sw, sh = 640, 400
    shot = np.full((sh, sw, 3), 245, np.uint8)
    for _ in range(40):
        x0, y0 = rng.integers(0, sw - 60), rng.integers(0, sh - 30)
        shot[y0:y0 + rng.integers(8, 30), x0:x0 + rng.integers(20, 60)] = rng.integers(0, 256, 3)
    for y in range(20, sh, 14):
        mask = rng.random(sw) < 0.35
        shot[y:y + 2, mask] = 30
    write("rgb8_screenshot", shot, width=sw, greyscale=False, bitdepth=8)

    # RGBA sprite with junk colour under alpha=0 (tests alpha-equivalent detection)
    alpha = (np.hypot(xx - 128, yy - 128) < 90).astype(np.uint8) * 255
    sprite = np.dstack([photo, alpha])
    sprite[alpha == 0, :3] = rng.integers(0, 256, (int((alpha == 0).sum()), 3), dtype=np.uint8)
    write("rgba8_sprite", sprite, width=W, greyscale=False, alpha=True, bitdepth=8)

    write("rgb16_gradient", np.dstack([xx * 257, yy * 257, (xx ^ yy) * 257]).astype(np.uint16),
          width=W, greyscale=False, bitdepth=16)

    # Palette pixel art: 16 colours, 8x8 blocks, with partial transparency in palette
    pal = [tuple(int(c) for c in rng.integers(0, 256, 3)) + (255 if i else 0,) for i in range(16)]
    blocks = rng.integers(0, 16, (H // 8, W // 8)).repeat(8, 0).repeat(8, 1).astype(np.uint8)
    write("pal8_pixelart", blocks, width=W, palette=pal, bitdepth=8)
    write("pal4_pixelart", blocks, width=W, palette=pal, bitdepth=4)

    print(f"synthetic images -> {out}")
    return 0


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else ""
    if cmd == "synth":
        return synth()
    if cmd == "manifest":
        return build_manifest()
    if cmd == "check":
        problems = check()
        print("\n".join(problems) or "corpus OK")
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
