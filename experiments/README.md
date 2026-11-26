# experiments/

Reproducible benchmarks for PNG encoder research. Rules are in `../CLAUDE.md` (Experiment rules).

```
harness/    pngio.py (canonical decode, verification, raw loading), encoders.py (registry),
            corpus.py (synth / manifest / check), bench.py (runner)
encoders/   our own encoder prototypes; pyref.py = reference encoder (numpy filters + zlib)
corpus/     test images by category: corpus/<category>/**.png (images git-ignored,
            manifest.csv versioned)
results/    one folder per experiment: E001_<name>/{results.csv, env.json, summary.md}
```

## Setup (from repo root)
```
python -m venv .venv
.venv/Scripts/python -m pip install -r experiments/requirements.txt
```
oxipng is included through the `pyoxipng` package (in-process, nothing system-wide).
Optional external CLI baselines, used automatically when on PATH: `zopflipng`, `ect`,
`optipng` (prebuilt Windows binaries).

## Use (from `experiments/`)
```
../.venv/Scripts/python -m harness.corpus synth       # smoke-test images
../.venv/Scripts/python -m harness.corpus manifest    # after adding images
../.venv/Scripts/python -m harness.bench E001_baseline --runs 5
../.venv/Scripts/python -m harness.bench E002_x --encoders pyref-minsum-z9,oxipng-o2 --category photo
```
Encoder names: `pyref-<none|sub|up|avg|paeth|minsum>-z<0-9>`, `pillow-z<0-9>`,
`oxipng-o<0-6>` / `oxipng-max`, plus the CLI tools
listed in `harness/encoders.py`.

## Adding an experimental encoder
1. Put the code in `encoders/` and reuse `pyref` stages where you can (`filter_all`,
   `choose_filters`, `deflate`), changing only the stage you're testing.
2. Register it in `harness/encoders.py` as an `InProc` (or `Cli` for an external binary).
3. Run it next to the baseline it claims to beat, on the full corpus.

## Notes and limits
- Verification decodes with pypng's raw sample values: `exact`, `alpha-equiv` (differs only
  in colour where alpha=0, which is lossless visually but not bit-exact), or `MISMATCH`.
- Python's `zlib` on this machine is **zlib-ng 1.3.1** (recorded in env.json), not
  Mark Adler's zlib. Level-for-level results may differ from libpng+zlib.
- Time scopes: `encode` excludes decoding; `recode` (oxipng) includes decoding the input;
  `process` (CLI tools) includes process start.
- pypng is pure Python, so loading large images is slow. Loading isn't timed, but expect
  slow runs on large corpora.
- `synthetic/` images only check that the harness works. Don't draw conclusions from them.
