# Project Charter — PNG Encoding Research

_Status: DRAFT (2026-11-26). Optimisation target decided: any Pareto improvement (D007)._

## Goal
Find, measure and build ways to make **lossless PNG encoding** produce smaller files
and/or encode faster, while every output stays a standard-conforming PNG that decodes to
bit-exact pixels.

## Scope
In: colour type / bit depth / palette reductions, scanline filter selection, DEFLATE
encoding (matching, parsing, block splitting, Huffman), IDAT layout, metadata stripping.
Out (unless a decision says otherwise): lossy techniques (quantisation, dithering), APNG,
decoder optimisation, non-PNG formats (comparison only).

## Optimisation target — any Pareto improvement (D007, closes Q001)
All three regimes are in scope. A result counts if it improves on the best existing tool in any of them:
- **A. Max compression**: smallest bytes, time secondary (zopfli / ECT territory).
- **B. Size/time Pareto**: beat existing tools at the same time budget (oxipng -o2..-o4 territory).
- **C. Fast encode**: near zlib-6 size at a fraction of the time (fpng / libdeflate territory).

## Success metrics
- A **win** = a new point on the size-vs-encode-time Pareto front: smaller output than
  every baseline at equal or lower time, or faster at equal or smaller size. It counts on
  the full corpus or on a single category (name the category).
- Results are reported as a Pareto chart plus a table, never as size alone.
- Hard requirement: 0 `MISMATCH` in verification.
- Report regimes separately (A max compression, B balanced, C fast) so a win in one isn't
  hidden by the others.

## Deliverables
- Knowledge base (`01_KNOWLEDGE`) with sourced claims.
- Experiment results (`experiments/results/`) and comparison tables.
- Final report in `06_OUTPUT/FINAL/`; prototype encoder code in `experiments/encoders/`.
