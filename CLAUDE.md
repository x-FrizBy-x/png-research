# CLAUDE.md — PNG Encoding Research

## Purpose
Research and optimize **lossless PNG encoding**: smaller files and/or faster encoding
with **bit-exact decoded pixels**. The work has two halves:
1. **Literature/knowledge**: papers, specs, existing encoders, captured in `Technical-Research/`.
2. **Experiments**: reproducible benchmarks of encoder strategies against fixed baselines.

Every claim about compression ratio or speed must trace to a source (paper/spec/code)
or to an experiment logged in this repo.

## Domain scope (what "PNG encoding" covers here)
Pipeline stages, each a possible optimization target:
- **Pre-processing**: colour type / bit depth reduction, palette generation and ordering,
  alpha cleanup (RGB of fully transparent pixels), interlacing (usually off).
- **Filtering**: per-scanline filter choice (None/Sub/Up/Average/Paeth), heuristics
  (MSAD, entropy, brute force, genetic search).
- **DEFLATE**: match finding, lazy/optimal parsing, Huffman block splitting, window size
  (zlib, libdeflate, zlib-ng, zopfli, 7-zip/ECT style).
- **Container**: IDAT chunking, metadata stripping, fdAT/APNG (out of scope unless noted).

Reference baselines: libpng+zlib (levels 1/6/9), oxipng, optipng, pngcrush, zopflipng, ECT,
fpng, libdeflate. Non-PNG formats (QOI, WebP-lossless, JPEG XL lossless) only as
comparison points, never as the goal.

## Repository layout
```
Technical-Research/
  00_PROJECT/      PROJECT_CHARTER (goals, scope, success metrics), RESEARCH_PROTOCOL
                   (rules below, in detail), CURRENT_STATE (read first every session), GLOSSARY
  01_KNOWLEDGE/    MASTER_KNOWLEDGE (synthesised understanding), CLAIM_REGISTER (atomic,
                   sourced claims), TECHNICAL_CONCEPTS, OPEN_QUESTIONS
  02_PAPERS/       PAPER_REGISTER (index), PAPER_NOTES/Pxxx.md, ORIGINAL_PDFS/
  03_ANALYSIS/     TECHNICAL_ANALYSIS, COMPARISON_TABLES, CONTRADICTIONS
  04_DECISIONS/    DECISION_LOG
  05_SESSIONS/     SESSION_xxx.md, one per working session
  06_OUTPUT/       DRAFTS/, FINAL/
  07_AUDIT/        CHANGELOG, VERIFICATION_LOG
experiments/
  harness/         pngio (canonical decode + verify), encoders (registry), corpus, bench
  encoders/        our encoder prototypes; pyref.py = reference encoder (numpy filters + zlib)
  corpus/          <category>/**.png (git-ignored) + manifest.csv (versioned, sha256)
  results/         E0NN_<name>/ results.csv, env.json, summary.md (immutable)
```
See `experiments/README.md` for commands. Run them from `experiments/` with
`../.venv/Scripts/python -m harness.<bench|corpus> ...`.

## ID conventions
| Prefix | Thing | Lives in |
|---|---|---|
| `P001` | Paper / spec / source | PAPER_REGISTER + `PAPER_NOTES/P001.md` (PDF: `ORIGINAL_PDFS/P001_<short-name>.pdf`) |
| `C001` | Claim | CLAIM_REGISTER |
| `Q001` | Open question | OPEN_QUESTIONS |
| `D001` | Decision | DECISION_LOG |
| `X001` | Contradiction | CONTRADICTIONS |
| `E001` | Experiment | experiments area (see below) |
| `S001` | Session | `05_SESSIONS/SESSION_001.md` |

IDs are never reused or renumbered. Cross-reference by ID (e.g. "C014 supported by P003, E002").

## Claim rules
Each claim in CLAIM_REGISTER has: ID, one-sentence statement, sources (P/E IDs with page
or section), status, date. Status values:
- `UNVERIFIED`: stated by a source, not yet checked
- `VERIFIED-SOURCE`: checked against the primary source text or code
- `VERIFIED-EXPERIMENT`: reproduced by our own experiment
- `DISPUTED`: conflicting evidence; link the `X` entry
- `REFUTED`: shown false; keep the entry, don't delete it

Rules:
- Don't invent numbers or citations. If a figure is from memory, mark it `UNVERIFIED`
  and say so.
- MASTER_KNOWLEDGE may only state things that point to claims.
- Each status change goes in VERIFICATION_LOG.

## Experiment rules
- **Losslessness first**: each encoder output is decoded and compared pixel-for-pixel
  with the source (RGBA 16-bit-normalised). A size win with a mismatch counts as a failure.
- Fixed, versioned **test corpus** with a manifest (file, dims, colour type, category:
  photo / screenshot / UI / pixel-art / palette / alpha-heavy). Never cherry-pick per result.
- Report **bytes** (total and per category), **% vs baseline**, **encode time**
  (median of ≥5 runs, wall clock, single thread unless stated), and decode time if
  relevant. Record CPU, OS, tool versions and exact command lines.
- Results go in machine-readable files (CSV/JSON) and are summarised in COMPARISON_TABLES
  with the E-ID.
- Compare on the Pareto front (size vs time), not on size alone.

## Session protocol
**Start**: read `00_PROJECT/CURRENT_STATE.md`, then the latest `SESSION_xxx.md`, then
OPEN_QUESTIONS. Don't re-read the whole tree unless asked.
**During**: write findings into the knowledge files as you go, not only into the session log.
**End**:
1. Write/finish `SESSION_xxx.md`: goal, what was done, new IDs created, next steps.
2. Update `CURRENT_STATE.md` (short: current focus, best-known result, top 3 next actions).
3. Add a line to `07_AUDIT/CHANGELOG.md`.

## Tooling
- Python deps live in `.venv` (`experiments/requirements.txt`). Python's `zlib` here is
  zlib-ng 1.3.1, not stock zlib. Keep that in mind when citing "zlib level N" numbers.
- Windows 11; shells: PowerShell and Git Bash. Python 3.14 and Rust/cargo available;
  no C compiler on PATH (install MSVC Build Tools or use WSL if C encoders need building).
- Prefer Python (numpy, Pillow, `zlib`) for analysis and harnesses. Use Rust for
  performance-critical encoder prototypes (`png`, `flate2`, `oxipng` crates are a good
  starting point).
- Don't commit large corpora or PDFs to git without asking. Keep them in ignored folders
  and keep only manifests and checksums under version control.

## Style
- Markdown, concise, tables where they help. Dates as YYYY-MM-DD.
- Separate **what a source says** from **our interpretation** (label the latter "Analysis:").
