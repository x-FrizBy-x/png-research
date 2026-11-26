"""Encoder registry. Each encoder: prepare(src) once (untimed), then run(prepared, src, out)
returning elapsed seconds.

Timing scope differs by kind and is recorded in results:
- 'encode'  in-process: filtering + compression of already-decoded pixels only.
- 'recode'  in-process PNG bytes -> PNG bytes (includes decoding the input, no process start).
- 'process' CLI tools: whole process wall time (startup + decode + optimise + write).
Don't compare raw times across scopes without saying so.
"""
from __future__ import annotations

import io
import re
import shutil
import subprocess
import time
from pathlib import Path

import oxipng
from PIL import Image

from encoders import pyref
from harness.pngio import load_raw


class InProc:
    scope = "encode"

    def __init__(self, name: str, prepare, encode, scope: str = "encode", version: str = "in-process"):
        self.name, self._prepare, self._encode = name, prepare, encode
        self.scope, self._version = scope, version

    def available(self) -> bool:
        return True

    def version(self) -> str:
        return self._version

    def prepare(self, src: Path):
        return self._prepare(src)

    def run(self, prepared, src: Path, out: Path) -> float:
        t0 = time.perf_counter()
        data = self._encode(prepared)
        dt = time.perf_counter() - t0
        out.write_bytes(data)
        return dt


class Cli:
    """argv uses {in}/{out} placeholders. inplace=True: src is copied to out (untimed)
    and the tool rewrites out. The copy is redone on every run so runs stay independent."""
    scope = "process"

    def __init__(self, name: str, argv: list[str], inplace: bool = False, version_args=("--version",)):
        self.name, self.argv, self.inplace, self.version_args = name, argv, inplace, version_args

    def available(self) -> bool:
        return shutil.which(self.argv[0]) is not None

    def version(self) -> str:
        try:
            r = subprocess.run([self.argv[0], *self.version_args], capture_output=True, text=True, timeout=10)
            lines = (r.stdout or r.stderr).strip().splitlines()
            return lines[0] if lines else "unknown"
        except Exception:
            return "unknown"

    def prepare(self, src: Path):
        return None

    def run(self, prepared, src: Path, out: Path) -> float:
        out.unlink(missing_ok=True)
        if self.inplace:
            shutil.copyfile(src, out)
        argv = [a.replace("{in}", str(src)).replace("{out}", str(out)) for a in self.argv]
        t0 = time.perf_counter()
        subprocess.run(argv, check=True, capture_output=True)
        return time.perf_counter() - t0


def _pillow(level: int) -> InProc:
    def prepare(src):
        im = Image.open(src)
        im.load()
        return im

    def encode(im):
        buf = io.BytesIO()
        im.save(buf, "PNG", compress_level=level)
        return buf.getvalue()

    return InProc(f"pillow-z{level}", prepare, encode)


def _pyref(name: str) -> InProc | None:
    m = re.fullmatch(r"pyref-(\w+)-z(\d)", name)
    if not m:
        return None
    strat, level = m.group(1), int(m.group(2))
    return InProc(name, load_raw, lambda img: pyref.encode(img, strat, level))


def _oxipng(level: int, name: str) -> InProc:
    """oxipng via pyoxipng bindings. force=True writes the result even if larger than the
    input, so we measure the encoder itself. level 6 == CLI '-o max'."""
    from importlib.metadata import version
    return InProc(name, lambda src: src.read_bytes(),
                  lambda data: oxipng.optimize_from_memory(
                      data, level=level, force=True, strip=oxipng.StripChunks.safe()),
                  scope="recode", version=f"pyoxipng {version('pyoxipng')}")


# Default set, in report order. Any pyref-<filter|minsum>-z<0-9> / pillow-z<0-9> /
# oxipng-o<0-6> name also works.
CLI = [
    Cli("zopflipng", ["zopflipng", "-y", "{in}", "{out}"], version_args=("-h",)),
    Cli("ect-9", ["ect", "-9", "-strip", "{out}"], inplace=True, version_args=()),
    Cli("optipng-o7", ["optipng", "-o7", "-quiet", "-out", "{out}", "{in}"], version_args=("-v",)),
]
DEFAULT = ["pyref-none-z9", "pyref-paeth-z9", "pyref-minsum-z6", "pyref-minsum-z9",
           "pillow-z6", "pillow-z9", "oxipng-o2", "oxipng-max"] + [c.name for c in CLI]


def get(name: str):
    for c in CLI:
        if c.name == name:
            return c
    if name == "oxipng-max":
        return _oxipng(6, name)
    if m := re.fullmatch(r"oxipng-o([0-6])", name):
        return _oxipng(int(m.group(1)), name)
    if m := re.fullmatch(r"pillow-z(\d)", name):
        return _pillow(int(m.group(1)))
    if enc := _pyref(name):
        return enc
    raise KeyError(f"unknown encoder {name!r}")
