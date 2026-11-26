# Project Charter — PNG Encoding Research

_Status: DRAFT (2026-11-26). The optimisation target is still open, see Q001._

## Goal
Find, measure and build ways to make **lossless PNG encoding** produce smaller files
and/or encode faster, while every output stays a standard-conforming PNG that decodes to
bit-exact pixels.

## Scope
In: colour type / bit depth / palette reductions, scanline filter selection, DEFLATE
encoding (matching, parsing, block splitting, Huffman), IDAT layout, metadata stripping.
Out (unless a decision says otherwise): lossy techniques (quantisation, dithering), APNG,
decoder optimisation, non-PNG formats (comparison only).

## Optimisation target — OPEN (Q001)
Pick one primary target. It decides corpus, baselines and what counts as a win:
- **A. Max compression**: smallest bytes, time secondary (zopfli / ECT territory).
- **B. Size/time Pareto**: beat existing tools at the same time budget (oxipng -o2..-o4 territory).
- **C. Fast encode**: near zlib-6 size at a fraction of the time (fpng / libdeflate territory).

## Success metrics (fill in once Q001 is decided)
- Primary: total bytes on the frozen corpus vs `<baseline>`, by category: target `<x>%`.
- Constraint: encode time ≤ `<budget>` relative to `<baseline>`.
- Hard requirement: 0 `MISMATCH` in verification.

## Deliverables
- Knowledge base (`01_KNOWLEDGE`) with sourced claims.
- Experiment results (`experiments/results/`) and comparison tables.
- Final report in `06_OUTPUT/FINAL/`; prototype encoder code in `experiments/encoders/`.
