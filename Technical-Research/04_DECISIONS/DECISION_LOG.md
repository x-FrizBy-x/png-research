# Decision Log

| ID | date | decision | rationale | alternatives |
|---|---|---|---|---|
| D001 | 2026-11-26 | Experiment harness in Python (numpy + pypng + Pillow); performance prototypes later in Rust | quick to iterate; numpy filters whole images at once; Rust toolchain already available for speed work | C (no compiler installed), Rust only (slower to iterate) |
| D002 | 2026-11-26 | Verify losslessness by decoding with pypng raw samples into uint16 RGBA; classify exact / alpha-equiv / MISMATCH | pypng keeps 16-bit and sub-byte depths exact and doesn't apply sBIT or gamma; alpha-equiv kept separate because "clean transparent pixels" is a known optimisation that is not bit-exact | Pillow decode |
| D003 | 2026-11-26 | Corpus images are not in git; a sha256 manifest is versioned and checked before every run | size and licensing; the manifest still guarantees reproducibility | git-lfs |
| D004 | 2026-11-26 | Experiment result folders are immutable; re-runs get new E-IDs | traceable evidence for claims | overwrite in place |
| D005 | 2026-11-26 | Reference encoder `pyref` keeps the source colour type and bit depth and writes no metadata | changes one variable at a time; reductions get their own experiments later | reduce by default |
| D006 | 2026-11-26 | Run oxipng through the `pyoxipng` PyPI bindings (in-process, timing scope `recode`) instead of the cargo-installed CLI | installs into .venv via requirements.txt, no system-wide install, no process-start overhead in timings | `cargo install oxipng` (global, built from source) |
