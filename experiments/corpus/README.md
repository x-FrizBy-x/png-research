# Corpus

Images are **not** in git; `manifest.csv` (path, category, dimensions, colour type,
bit depth, bytes, sha256) is. `bench` refuses to run if files don't match the manifest.

Layout: `corpus/<category>/...png`. The category is the first folder name.

| category | status | notes |
|---|---|---|
| synthetic | present | from `harness.corpus synth`; covers every colour type and bit depth; smoke test only |
| photo | TODO | natural photos saved as PNG |
| screenshot | TODO | desktop/web screenshots, text-heavy |
| ui | TODO | icons, UI assets, flat colour with alpha |
| pixelart | TODO | game sprites, palette images |
| alpha | TODO | images with large transparent regions |
| conformance | TODO | PngSuite (odd colour types and bit depths); for correctness, not size |

Rules: record each image's source and licence in `SOURCES.md` here (also not versioned
if private). Don't edit or remove files once an experiment has used them. Add files and
rebuild the manifest instead, and note the change in the session log.
