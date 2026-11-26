# Session 001 — 2026-11-26

**Goal:** review the scaffold, write CLAUDE.md, set up the workflow (Phase 0).

## Done
- Reviewed the structure: all knowledge files were empty placeholders and there was
  nowhere for experiments.
- Wrote `/CLAUDE.md` (scope, IDs, claim statuses, experiment rules, session protocol).
- Phase 0: `git init`, `.gitignore`, `.venv`, created `experiments/`:
  - `harness/pngio.py`: canonical decode + lossless compare; raw scanline loader for every colour type and bit depth
  - `encoders/pyref.py`: reference encoder (vectorised 5-filter pass, minsum or fixed filter, zlib)
  - `harness/encoders.py`: registry (pyref-*, pillow-*, oxipng via pyoxipng; zopflipng/ect/optipng when on PATH)
  - `harness/corpus.py`: synthetic corpus, sha256 manifest, integrity check
  - `harness/bench.py`: runner → results.csv / env.json / summary.md
- E000_smoke: 12 synthetic images × 6 in-process encoders × 5 runs. 0 mismatches.
  The verifier was also tested by hand: a flipped visible pixel gives MISMATCH, a change
  under alpha=0 gives alpha-equiv, and 16→8-bit truncation gives MISMATCH.
- `cargo install oxipng` was blocked (system-wide install) → switched to the `pyoxipng`
  bindings in .venv (D006). E001_smoke-oxipng: oxipng-o2/max, 0 mismatches.
- Removed `structure.txt`, added git remote `origin`, first commit and push.

## Observations (not evidence: synthetic data)
- Python's zlib is zlib-ng 1.3.1 (→ Q003).
- pyref-minsum-z9 was 2.5% larger than z6 (→ Q002).

## New IDs
Q001–Q003, D001–D006, E000, E001.

## Next
See CURRENT_STATE.
