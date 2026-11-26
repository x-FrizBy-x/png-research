"""Benchmark runner.

  python -m harness.bench E001_baseline [--encoders a,b] [--runs 5] [--baseline pyref-minsum-z6]
                                        [--category photo] [--keep-outputs] [--force]

For every corpus file x encoder: encode `runs` times (median time), decode the output and
compare pixels with the source, and record the size. Writes results/<exp>/:
  results.csv  one row per (file, encoder)
  env.json     machine, versions, command, git state
  summary.md   totals per encoder and per category, deltas vs baseline
An experiment directory isn't overwritten unless --force is given.
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import re
import statistics
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import datetime
from importlib.metadata import version as pkg_version
from pathlib import Path

from harness import corpus, encoders
from harness.pngio import compare, decode_canonical

ROOT = corpus.ROOT
FIELDS = ["file", "category", "encoder", "scope", "src_bytes", "out_bytes", "ratio_vs_src",
          "time_median_s", "time_min_s", "runs", "verify"]


def git_state() -> dict:
    def git(*a):
        r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    return {"commit": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain"))}


def summarise(rows: list[dict], names: list[str], baseline: str) -> str:
    ok = {(r["file"], r["encoder"]): r for r in rows if r["out_bytes"]}
    files = sorted({r["file"] for r in rows})
    cats = sorted({r["category"] for r in rows})
    cat_of = {r["file"]: r["category"] for r in rows}

    def total(enc, fs):
        return sum(int(ok[(f, enc)]["out_bytes"]) for f in fs)

    def delta(enc, fs):
        common = [f for f in fs if (f, enc) in ok and (f, baseline) in ok]
        if not common or enc == baseline:
            return "—"
        return f"{100 * (total(enc, common) / total(baseline, common) - 1):+.2f}%"

    src_total = sum(int(r["src_bytes"]) for r in {r["file"]: r for r in rows}.values())
    lines = [f"Files: {len(files)} · source bytes: {src_total:,} · baseline: `{baseline}`", "",
             "| encoder | scope | files ok | total bytes | Δ vs baseline | Σ median time (s) | mismatch | alpha-equiv | errors |",
             "|---|---|---|---|---|---|---|---|---|"]
    for enc in names:
        rs = [r for r in rows if r["encoder"] == enc]
        good = [r for r in rs if r["out_bytes"]]
        lines.append(
            f"| {enc} | {rs[0]['scope'] if rs else ''} | {len(good)}/{len(rs)} | {total(enc, [r['file'] for r in good]):,} "
            f"| {delta(enc, files)} | {sum(float(r['time_median_s']) for r in good):.3f} "
            f"| {sum(r['verify'] == 'MISMATCH' for r in rs)} | {sum(r['verify'] == 'alpha-equiv' for r in rs)} "
            f"| {sum(r['verify'].startswith('ERROR') for r in rs)} |")
    lines += ["", "### Δ vs baseline by category", "",
              "| encoder | " + " | ".join(cats) + " |", "|---|" + "---|" * len(cats)]
    for enc in names:
        lines.append(f"| {enc} | " + " | ".join(delta(enc, [f for f in files if cat_of[f] == c]) for c in cats) + " |")
    lines += ["", "Δ is computed only over files where both encoders succeeded. Time scopes: `encode` = pixels already decoded; "
              "`recode` = PNG bytes in, includes decoding; `process` = CLI tool, includes process startup. "
              "Don't compare times across scopes without saying so."]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("exp", help="experiment id, e.g. E001_baseline")
    ap.add_argument("--manifest", type=Path, default=corpus.MANIFEST)
    ap.add_argument("--encoders", help="comma-separated; default: all available")
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--baseline", default="pyref-minsum-z6")
    ap.add_argument("--category", action="append", help="restrict to category (repeatable)")
    ap.add_argument("--keep-outputs", action="store_true")
    ap.add_argument("--force", action="store_true", help="overwrite existing results dir")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to a legacy codepage

    if not re.fullmatch(r"E\d{3}(_[\w-]+)?", a.exp):
        ap.error("exp must look like E001 or E001_short-name")
    outdir = ROOT / "results" / a.exp
    if outdir.exists() and not a.force:
        ap.error(f"{outdir} exists; experiments are immutable (use --force to overwrite)")

    if problems := corpus.check(a.manifest):
        print("Corpus does not match manifest:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    files = [r for r in corpus.load_manifest(a.manifest) if not a.category or r["category"] in a.category]

    requested = a.encoders.split(",") if a.encoders else encoders.DEFAULT
    encs, skipped = [], []
    for n in requested:
        e = encoders.get(n)
        (encs if e.available() else skipped).append(e)
    if skipped:
        print("skipping unavailable: " + ", ".join(e.name for e in skipped))
    names = [e.name for e in encs]
    if a.baseline not in names:
        ap.error(f"baseline {a.baseline!r} is not among the encoders being run")

    outdir.mkdir(parents=True, exist_ok=True)
    work = outdir / "out" if a.keep_outputs else Path(tempfile.mkdtemp(prefix="pngbench-"))
    work.mkdir(exist_ok=True)

    rows = []
    for i, fr in enumerate(files, 1):
        src = corpus.CORPUS / fr["path"]
        ref = decode_canonical(src)
        for e in encs:
            out = work / f"{Path(fr['path']).stem}.{e.name}.png"
            row = dict(file=fr["path"], category=fr["category"], encoder=e.name, scope=e.scope,
                       src_bytes=fr["bytes"], out_bytes="", ratio_vs_src="", time_median_s="",
                       time_min_s="", runs=a.runs)
            try:
                prepared = e.prepare(src)
                times = [e.run(prepared, src, out) for _ in range(a.runs)]
                size = out.stat().st_size
                row.update(out_bytes=size, ratio_vs_src=f"{size / int(fr['bytes']):.4f}",
                           time_median_s=f"{statistics.median(times):.6f}", time_min_s=f"{min(times):.6f}",
                           verify=compare(ref, decode_canonical(out)))
            except Exception as ex:  # record and continue; failures are results too
                row["verify"] = f"ERROR: {type(ex).__name__}: {str(ex)[:120]}"
            rows.append(row)
            print(f"[{i}/{len(files)}] {fr['path']:40} {e.name:18} {row['out_bytes']!s:>10} {row['verify']}")

    with (outdir / "results.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)

    env = {
        "date": datetime.now().isoformat(timespec="seconds"),
        "command": " ".join(sys.argv),
        "platform": platform.platform(), "processor": platform.processor(),
        "python": platform.python_version(),
        "packages": {p: pkg_version(p) for p in ("numpy", "pillow", "pypng", "pyoxipng")},
        "zlib": __import__("zlib").ZLIB_RUNTIME_VERSION,
        "encoders": {e.name: e.version() for e in encs},
        "skipped": [e.name for e in skipped],
        "manifest": a.manifest.relative_to(ROOT).as_posix(), "files": len(files), "runs": a.runs,
        "git": git_state(),
    }
    (outdir / "env.json").write_text(json.dumps(env, indent=2))
    summary = f"# {a.exp}\n\n{summarise(rows, names, a.baseline)}"
    (outdir / "summary.md").write_text(summary, encoding="utf-8")
    print("\n" + summary)
    bad = sum(r["verify"] == "MISMATCH" for r in rows)
    if bad:
        print(f"WARNING: {bad} lossless-verification mismatches", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
