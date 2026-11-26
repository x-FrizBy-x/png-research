# Current State
_Updated: 2026-11-26 (S001)_

**Phase:** 0 (setup) done → next is Phase 1 (baseline) and Phase 2 (literature).

**Have:** git repo; Python harness (`experiments/harness`) with lossless verification;
reference encoder `pyref`; synthetic smoke corpus (12 images, every colour type and bit
depth); smoke runs E000 (pyref/Pillow) and E001 (+ oxipng via pyoxipng 9.1.1); all outputs verified exact. Git remote: github.com/x-FrizBy-x/png-research.

**Best known result:** none yet (E000 is a harness check, not evidence).

**Blockers / needs the user:**
- Q001: choose the optimisation target (charter A/B/C).
- External CLI baselines are not installed (zopflipng, ECT, optipng); oxipng is available via pyoxipng.
- A real corpus is needed (see `experiments/corpus/README.md`).

**Next 3 actions:**
1. Decide Q001 and finish PROJECT_CHARTER success metrics.
2. Build the real corpus, run `E002_baseline` with all baselines.
3. Register the first sources: PNG spec, RFC 1950/1951, zopfli design notes.
